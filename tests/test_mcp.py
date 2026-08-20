"""The MCP adapter: authentication, pre-mutation validation, the stage bridge, and the lock.

Adapter only. The pipeline is exercised through the real CLI exactly once (test D), on the one
stage that touches no network — everything else stubs the subprocess, because what is under test
here is the bridging, not the engine.
"""

from __future__ import annotations

import asyncio
import json
import os
from datetime import date
from importlib.metadata import version as distribution_version
from pathlib import Path

import httpx
import pytest
from fastmcp import Client
from fastmcp.client.transports import StreamableHttpTransport
from fastmcp.server.dependencies import get_http_request

from conftest import make_candidate, make_plan, plan_payload
from research_scan import mcp_server, run
from research_scan.dedup import with_cid
from research_scan.schema import Manifest, Profile, RunInfo, SummaryPaper

TOKEN = "test-token-abcdef123456"
SCAN_ID = "11111111-2222-4333-8444-555555555555"
OTHER_SCAN = "99999999-2222-4333-8444-555555555555"


@pytest.fixture
def mcp_home(fake_settings, tmp_path, monkeypatch) -> Path:
    """`fake_settings` clears KNOWN_VARS, so the adapter's own two vars are set here."""
    root = tmp_path / "mcp-runs"
    monkeypatch.setenv("RESEARCH_SCAN_MCP_TOKEN", TOKEN)
    monkeypatch.setenv("RESEARCH_SCAN_MCP_DATA", str(root))
    return root


def candidate(seed: str) -> dict:
    return with_cid(
        make_candidate(
            title=f"Paper {seed}",
            doi=f"10.1000/{seed}",
            year=2024,
            publication_date="2024-01-01",
            abstract=f"An abstract about {seed}.",
            authors=(f"Ada Author{seed}",),
        )
    ).model_dump(mode="json")


def batch_payload(name: str, candidates: list[dict]) -> dict:
    return {
        "batch": name,
        "sub_criteria": plan_payload()["sub_criteria"],
        "items": [
            {"cid": item["cid"], "title": item["title"], "abstract_600": item["abstract"]}
            for item in candidates
        ],
    }


def scaffold(run_dir: Path) -> dict:
    """What `init` leaves behind: the batch directory, brief, manifest and the model's plan."""
    (run_dir / "screen-batches").mkdir(parents=True, exist_ok=True)
    info = RunInfo.model_validate(
        {
            "run_dir": str(run_dir),
            "slug": "t",
            "date": "2026-08-19",
            "brief_path": str(run_dir / "brief.md"),
            "defaults": {"domain": "behavioral", "top": 10, "foundational": 2},
        }
    )
    (run_dir / "brief.md").write_text("# brief\n")
    run.write_manifest(
        run_dir,
        Manifest.model_validate(
            {
                "run": info.model_dump(mode="json"),
                "defaults": info.defaults.model_dump(mode="json"),
                "tool_version": "0.2.4",
            }
        ),
    )
    (run_dir / "queries.json").write_text(json.dumps(plan_payload()))
    return info.model_dump(mode="json")


def make_scan(
    mcp_home: Path, batches: dict[str, list[dict]], *, scan_id: str = SCAN_ID, **files
) -> Path:
    """A scan directory as `scan_start` would have left it: run dir, plan, pool, batches."""
    root = mcp_home / scan_id
    run_dir = root / "research" / "scans" / "2026-08-19-t"
    info = RunInfo.model_validate(scaffold(run_dir))

    pool = [item for items in batches.values() for item in items]
    (run_dir / "candidates.json").write_text(
        json.dumps({"run": info.model_dump(mode="json"), "candidates": pool})
    )
    for name, items in batches.items():
        (run_dir / "screen-batches" / f"{name}.json").write_text(
            json.dumps(batch_payload(name, items))
        )
    for name, payload in files.items():
        (run_dir / f"{name}.json").write_text(json.dumps(payload))
    return root


def scores_for(
    items: list[dict], *, score: int = 3, criteria: list[str] | None = None
) -> list[dict]:
    return [
        {
            "cid": item["cid"],
            "score": score,
            "reason": "relevant",
            "criteria_hit": ["C1"] if criteria is None else criteria,
        }
        for item in items
    ]


def snapshot(root: Path) -> dict[str, bytes]:
    return {str(path): path.read_bytes() for path in sorted(root.rglob("*")) if path.is_file()}


# --- A. authentication -------------------------------------------------------


@pytest.mark.parametrize(
    ("path", "header", "expected"),
    [
        ("/mcp", f"Bearer {TOKEN}", True),
        ("/mcp", f"bearer {TOKEN}", True),
        ("/mcp", "Bearer wrong", False),
        ("/mcp", None, False),
        (f"/{TOKEN}/mcp", None, True),
        ("/not-the-token/mcp", None, False),
        (f"/{TOKEN}", None, True),
        ("/", f"Bearer {TOKEN}", True),
    ],
)
def test_authorize_accepts_either_mechanism(path, header, expected):
    assert mcp_server.authorize(path, header, TOKEN) is expected


def test_authorize_without_a_configured_token_denies_everything():
    assert mcp_server.authorize(f"/{TOKEN}/mcp", f"Bearer {TOKEN}", None) is False


def probe(app, url: str, auth: str | None = None) -> str:
    """One MCP handshake over ASGI — no socket, so this stays inside the default test run."""

    def factory(**kwargs):
        kwargs.pop("transport", None)
        return httpx.AsyncClient(
            transport=httpx.ASGITransport(app=app), base_url="http://test", **kwargs
        )

    async def go() -> str:
        async with app.router.lifespan_context(app):
            transport = StreamableHttpTransport(url, auth=auth, httpx_client_factory=factory)
            try:
                async with Client(transport) as client:
                    return f"ok:{len(await client.list_tools())}"
            except Exception as exc:  # noqa: BLE001 - the rejection shape is not the assertion
                return f"rejected:{type(exc).__name__}"

    return asyncio.run(go())


def test_both_mounts_accept_a_good_token_and_reject_a_bad_one(mcp_home):
    app = mcp_server.build_app(TOKEN)
    assert probe(app, f"http://test/{TOKEN}/mcp") == "ok:4"
    assert probe(app, "http://test/mcp", auth=TOKEN) == "ok:4"
    assert probe(app, "http://test/mcp").startswith("rejected:")
    assert probe(app, "http://test/mcp", auth="wrong-token").startswith("rejected:")
    assert probe(app, "http://test/not-the-token/mcp").startswith("rejected:")


def test_without_a_token_the_server_starts_and_401s_instead_of_refusing_to_boot(
    mcp_home, monkeypatch
):
    """It used to raise on build. A dead port is un-probeable; a 401 says what is wrong.

    Same security posture either way — no request is ever served — but a health check now gets
    an answer, and the answer names the missing token.
    """
    monkeypatch.delenv("RESEARCH_SCAN_MCP_TOKEN")

    app = mcp_server.build_app()

    async def statuses() -> list[tuple[int, str]]:
        async with httpx.AsyncClient(
            transport=httpx.ASGITransport(app=app), base_url="http://test"
        ) as client:
            out = []
            for url in ("/mcp", "/", f"/{TOKEN}/mcp"):
                response = await client.post(
                    url, json={"jsonrpc": "2.0", "id": 1, "method": "initialize"}
                )
                out.append((response.status_code, response.json()["error"]))
            return out

    assert asyncio.run(statuses()) == [(401, "unauthorized")] * 3
    # One mount, not two: with no secret there is no path-secret route to create.
    assert len(app.routes) == 1
    assert TOKEN not in str(app.routes[0].path)


def test_the_handshake_states_our_version_not_the_libraries(mcp_home):
    """serverInfo.version reported fastmcp's version until it was passed explicitly."""
    import fastmcp

    from research_scan import __version__

    assert mcp_server.mcp._mcp_server.version == __version__
    assert mcp_server.mcp._mcp_server.version != fastmcp.__version__
    assert mcp_server.mcp._mcp_server.name == "research-scan"


def test_stdio_serves_the_same_four_tools_over_a_real_subprocess(mcp_home, tmp_path):
    """The one test that proves stdout carries MCP and nothing else.

    Any stray print, log line or banner on stdout corrupts the frame and the handshake fails,
    so this passing *is* the stdout-purity assertion. No network: initialize and tools/list only.
    """
    from fastmcp.client.transports import StdioTransport

    binary = mcp_server.cli_binary()
    transport = StdioTransport(command=binary, args=["mcp"], env=dict(os.environ))

    async def handshake() -> tuple[str, str, list[str]]:
        async with Client(transport) as client:
            info = client.initialize_result.serverInfo
            tools = sorted(tool.name for tool in await client.list_tools())
            return info.name, info.version, tools

    name, version, tools = asyncio.run(handshake())

    assert name == "research-scan"
    assert version == distribution_version("research-scan")
    assert tools == ["scan_continue", "scan_result", "scan_start", "scan_verify"]


def test_stdio_reads_no_token_at_all(mcp_home, monkeypatch):
    """Local stdio is trusted because the user launched the process; auth would be theatre."""
    monkeypatch.delenv("RESEARCH_SCAN_MCP_TOKEN")

    # The gate short-circuits when there is no HTTP request to authenticate against, which is
    # every stdio message. `authorize` is never reached, so an absent token cannot lock anyone out.
    assert mcp_server.authorize("/mcp", None, None) is False
    with pytest.raises(RuntimeError):
        get_http_request()


# --- B. bad artifact or wrong phase: structured error, zero mutation ----------


def continue_call(**kwargs) -> dict:
    return asyncio.run(mcp_server.scan_continue(**kwargs))


@pytest.mark.parametrize(
    ("mutate", "status"),
    [
        (lambda scores: [{**scores[0], "score": 7}], "invalid_artifact"),
        (lambda scores: [{**scores[0], "cid": "ffffffffffff"}], "invalid_artifact"),
        (lambda scores: [{**scores[0], "criteria_hit": ["C9"]}], "invalid_artifact"),
        (lambda scores: scores[:1], "invalid_artifact"),
    ],
    ids=["bad-score", "unknown-cid", "unknown-criterion", "partial-batch"],
)
def test_a_bad_submission_is_refused_whole_and_writes_nothing(mcp_home, mutate, status):
    items = [candidate("a"), candidate("b")]
    root = make_scan(mcp_home, {"01": items})
    before = snapshot(root)

    result = continue_call(scan_id=SCAN_ID, screen_scores=mutate(scores_for(items)))

    assert result["status"] == status
    assert result["next_action"] is None
    assert result["payload"]["error"]
    assert snapshot(root) == before


def test_an_unknown_cid_names_itself_rather_than_reading_as_an_unscored_item(mcp_home):
    items = [candidate("a"), candidate("b")]
    make_scan(mcp_home, {"01": items})
    scores = scores_for(items) + [
        {"cid": "ffffffffffff", "score": 2, "reason": "r", "criteria_hit": ["C1"]}
    ]

    result = continue_call(scan_id=SCAN_ID, screen_scores=scores)

    assert result["status"] == "invalid_artifact"
    assert "candidates.json" in result["payload"]["error"]
    assert any("ffffffffffff" in line for line in result["payload"]["errors"])


def test_an_artifact_for_another_phase_is_refused(mcp_home):
    items = [candidate("a")]
    root = make_scan(mcp_home, {"01": items})
    before = snapshot(root)

    result = continue_call(
        scan_id=SCAN_ID,
        ranked_entries=[
            {
                "cid": items[0]["cid"],
                "criteria": {"C1": 3},
                "overall": 3,
                "evidence_level": "rct",
                "key_finding": "a finding",
                "methodology": "abstract-only",
                "why_it_matters": "it matters",
                "limitations": ["small n"],
                "relevance_reason": "on point",
            }
        ],
    )

    assert result["status"] == "wrong_phase"
    assert "screen_candidates" in result["payload"]["error"]
    assert snapshot(root) == before


def test_two_artifacts_in_one_call_are_refused(mcp_home):
    items = [candidate("a")]
    root = make_scan(mcp_home, {"01": items})
    before = snapshot(root)

    result = continue_call(scan_id=SCAN_ID, screen_scores=scores_for(items), gap_queries=[])

    assert result["status"] == "invalid_artifact"
    assert snapshot(root) == before


def test_an_unknown_scan_id_is_a_structured_refusal(mcp_home):
    assert continue_call(scan_id="not-a-uuid")["status"] == "invalid_artifact"
    assert continue_call(scan_id=OTHER_SCAN)["status"] == "wrong_phase"


def test_scoring_one_batch_while_others_wait_is_accepted(mcp_home, monkeypatch):
    """The whole-pool coverage rule belongs to `shortlist`; it must not fire on a page write."""
    first, second = [candidate("a")], [candidate("b")]
    root = make_scan(mcp_home, {"01": first, "02": second})
    monkeypatch.setattr(mcp_server, "run_stage", stub_cli(root))

    result = continue_call(scan_id=SCAN_ID, screen_scores=scores_for(first))

    assert result["status"] == "ok"
    assert result["next_action"] == "screen_candidates"
    assert result["payload"]["screen_batch"]["batch"] == "02"
    assert result["progress"]["batches_scored"] == 1


# --- C. the stage bridge -----------------------------------------------------


def stub_cli(root: Path, *, gap_should_run: bool = False, calls: list | None = None):
    """Stand in for the CLI: writes what each stage writes, records the argv it was given."""
    run_dir = root / "research" / "scans" / "2026-08-19-t"

    def fake(cwd: Path, stage: str, *args: str) -> mcp_server.StageOutcome:
        if calls is not None:
            calls.append((stage, *args))
        if stage == "expand":
            grown = [candidate("x1"), candidate("x2")]
            pool = json.loads((run_dir / "candidates.json").read_text())
            pool["candidates"] += grown
            (run_dir / "candidates.json").write_text(json.dumps(pool))
            (run_dir / "screen-batches" / "x01.json").write_text(
                json.dumps(batch_payload("x01", grown))
            )
            (run_dir / "expanded.json").write_text(
                json.dumps({"seeds": [], "added": [], "batches": ["x01"]})
            )
        elif stage == "coverage":
            (run_dir / "coverage.json").write_text(
                json.dumps(
                    {
                        "run": json.loads((run_dir / "manifest.json").read_text())["run"],
                        "rounds": [{"round": 1, "screened": 4, "ge2": 4}],
                        "gap_round": {
                            "should_run": gap_should_run,
                            "profile": "quick",
                            "reasons": ["stub"],
                        },
                    }
                )
            )
        elif stage == "shortlist":
            pool = json.loads((run_dir / "candidates.json").read_text())["candidates"]
            (run_dir / "shortlist.json").write_text(
                json.dumps(
                    {"in_window": [{**item, "score": 3} for item in pool], "outside_window": []}
                )
            )
        return mcp_server.StageOutcome(stage=stage, code=0, payload={"ok": True}, stderr="")

    return fake


def test_the_last_screen_batch_bridges_through_expand_coverage_and_shortlist(mcp_home, monkeypatch):
    items = [candidate("a"), candidate("b")]
    root = make_scan(mcp_home, {"01": items})
    calls: list = []
    monkeypatch.setattr(mcp_server, "run_stage", stub_cli(root, calls=calls))

    # Screening the only retrieval batch runs `expand` and hands back its batch.
    after_screen = continue_call(scan_id=SCAN_ID, screen_scores=scores_for(items))
    assert [call[0] for call in calls] == ["expand"]
    assert after_screen["next_action"] == "screen_candidates"
    assert after_screen["payload"]["screen_batch"]["batch"] == "x01"

    # Screening the expansion batch runs `coverage`, then `shortlist`, and asks for the rerank.
    grown = json.loads((root / "research/scans/2026-08-19-t/screen-batches/x01.json").read_text())
    after_expansion = continue_call(
        scan_id=SCAN_ID,
        screen_scores=[
            {"cid": item["cid"], "score": 3, "reason": "relevant", "criteria_hit": ["C1"]}
            for item in grown["items"]
        ],
    )
    assert [call[0] for call in calls] == ["expand", "coverage", "shortlist"]
    assert after_expansion["phase"] == "rank"
    assert after_expansion["next_action"] == "rank_shortlist"
    assert after_expansion["progress"] == {
        **after_expansion["progress"],
        "page": 1,
        "of": 1,
        "shortlisted": 4,
        "ranked": 0,
    }
    records = after_expansion["payload"]["shortlist_records"]
    assert len(records) == 4
    assert "abstract" in records[0], "the rerank boundary gets the record the local skill reads"


def test_a_screen_batch_payload_is_the_batch_file_verbatim(mcp_home):
    items = [candidate("a")]
    root = make_scan(mcp_home, {"01": items})

    result = asyncio.run(mcp_server.scan_continue(scan_id=SCAN_ID))

    on_disk = json.loads((root / "research/scans/2026-08-19-t/screen-batches/01.json").read_text())
    assert result["payload"]["screen_batch"] == on_disk
    assert "citation_count" not in json.dumps(result["payload"]["screen_batch"])


def test_force_gap_round_reaches_coverage_and_never_init(mcp_home, monkeypatch):
    items = [candidate("a")]
    root = make_scan(mcp_home, {"01": items})
    mcp_server.write_options(root, {"force_gap_round": True, "max_candidates": 300})
    calls: list = []
    monkeypatch.setattr(mcp_server, "run_stage", stub_cli(root, calls=calls))

    continue_call(scan_id=SCAN_ID, screen_scores=scores_for(items))
    grown = json.loads((root / "research/scans/2026-08-19-t/screen-batches/x01.json").read_text())
    continue_call(
        scan_id=SCAN_ID,
        screen_scores=[
            {"cid": item["cid"], "score": 3, "reason": "relevant", "criteria_hit": ["C1"]}
            for item in grown["items"]
        ],
    )

    coverage_call = next(call for call in calls if call[0] == "coverage")
    assert "--gap-round" in coverage_call
    assert not any(call[0] == "init" for call in calls)
    retrieve_calls = [call for call in calls if call[0] == "retrieve"]
    assert all("--gap-round" not in call for call in retrieve_calls)


def test_the_gap_round_is_offered_once_and_only_when_coverage_says_so(mcp_home, monkeypatch):
    items = [candidate("a")]
    root = make_scan(mcp_home, {"01": items})
    monkeypatch.setattr(mcp_server, "run_stage", stub_cli(root, gap_should_run=True))

    continue_call(scan_id=SCAN_ID, screen_scores=scores_for(items))
    grown = json.loads((root / "research/scans/2026-08-19-t/screen-batches/x01.json").read_text())
    asked = continue_call(
        scan_id=SCAN_ID,
        screen_scores=[
            {"cid": item["cid"], "score": 3, "reason": "relevant", "criteria_hit": ["C1"]}
            for item in grown["items"]
        ],
    )
    assert asked["next_action"] == "write_gap_queries"
    assert asked["payload"]["gap_round"]["should_run"] is True

    # An empty gap round is a legitimate answer, and it does not loop back.
    skipped = continue_call(scan_id=SCAN_ID, gap_queries=[])
    assert skipped["next_action"] == "rank_shortlist"


# --- D. the real CLI ---------------------------------------------------------


def test_run_stage_drives_the_installed_cli_and_maps_its_exit_codes(mcp_home):
    """`shortlist` touches no network, so the whole subprocess seam runs in the default suite."""
    items = [candidate("a"), candidate("b")]
    root = make_scan(mcp_home, {"01": items})
    run_dir = root / "research" / "scans" / "2026-08-19-t"
    (run_dir / "screen.json").write_text(json.dumps({"scores": scores_for(items)}))

    outcome = mcp_server.run_stage(root, "shortlist", "--run", str(run_dir))

    assert outcome.ok, outcome.stderr
    assert outcome.payload["screened_ge2"] == 2
    assert (run_dir / "shortlist.json").exists()


def test_an_incomplete_screen_file_comes_back_as_the_engines_own_exit_2(mcp_home):
    items = [candidate("a"), candidate("b")]
    root = make_scan(mcp_home, {"01": items})
    run_dir = root / "research" / "scans" / "2026-08-19-t"
    (run_dir / "screen.json").write_text(json.dumps({"scores": scores_for(items[:1])}))

    outcome = mcp_server.run_stage(root, "shortlist", "--run", str(run_dir))
    assert outcome.code == 2

    with pytest.raises(mcp_server.ScanFailure) as raised:
        mcp_server.check(outcome)
    assert raised.value.status == "invalid_artifact"
    assert "screen.json does not cover candidates.json exactly once" in raised.value.message
    assert any("missing scores" in line for line in raised.value.lines)
    assert not (run_dir / "shortlist.json").exists()


def test_an_unstructured_failure_is_never_read_as_success():
    outcome = mcp_server.StageOutcome(stage="expand", code=1, payload={}, stderr="Traceback…")
    with pytest.raises(mcp_server.ScanFailure) as raised:
        mcp_server.check(outcome, tolerate_structured=True)
    assert raised.value.status == "failed"


def test_the_gap_rounds_empty_expansion_is_tolerated_but_round_one_is_not():
    empty = {"ok": False, "error": "the gap round has nothing to grow from"}
    tolerated = mcp_server.check(
        mcp_server.StageOutcome(stage="expand", code=1, payload=empty, stderr=""),
        tolerate_structured=True,
    )
    assert tolerated.code == 1

    with pytest.raises(mcp_server.ScanFailure) as raised:
        mcp_server.check(mcp_server.StageOutcome(stage="expand", code=1, payload=empty, stderr=""))
    assert raised.value.status == "failed"
    assert raised.value.message == empty["error"]


# --- E. the lock -------------------------------------------------------------


def test_a_busy_pipeline_answers_immediately_and_mutates_nothing(mcp_home):
    items = [candidate("a")]
    root = make_scan(mcp_home, {"01": items})
    before = snapshot(root)

    assert mcp_server.acquire(OTHER_SCAN) is None
    try:
        other = continue_call(scan_id=SCAN_ID, screen_scores=scores_for(items))
        assert other["status"] == "queued_behind_other_scan"

        mcp_server._HELD_BY = SCAN_ID
        same = continue_call(scan_id=SCAN_ID, screen_scores=scores_for(items))
        assert same["status"] == "in_progress"
        assert "do not resubmit" in same["payload"]["error"]
    finally:
        mcp_server.release()

    assert all(result["next_action"] is None for result in (other, same))
    assert snapshot(root) == before
    assert mcp_server.acquire(SCAN_ID) is None
    mcp_server.release()


# --- scan_result -------------------------------------------------------------


def test_scan_result_reads_an_unfinished_run_without_erroring(mcp_home):
    items = [candidate("a")]
    make_scan(mcp_home, {"01": items})

    result = asyncio.run(mcp_server.scan_result(SCAN_ID))

    assert result["status"] == "ok"
    assert result["phase"] == "screen"
    assert "top" not in result["payload"]
    assert result["payload"]["unverified"] == []


def test_scan_result_leaves_the_prose_to_the_model(mcp_home):
    items = [candidate("a")]
    root = make_scan(mcp_home, {"01": items})
    run_dir = root / "research" / "scans" / "2026-08-19-t"
    packet = {
        **items[0],
        "criteria": {"C1": 3},
        "overall": 3,
        "evidence_level": "rct",
        "key_finding": "a finding",
        "methodology": "abstract-only",
        "why_it_matters": "it matters",
        "limitations": ["small n"],
        "relevance_reason": "on point",
        "relation": "design-changing",
        "verification": {
            "verified": True,
            "verified_by": ["crossref"],
            "verified_on": "2026-08-19",
        },
        "rank": 1,
        "selection_reason": "score",
    }
    manifest = json.loads((run_dir / "manifest.json").read_text())
    (run_dir / "evidence.json").write_text(
        json.dumps({"run": manifest["run"], "packets": [packet], "alternates": []})
    )
    (run_dir / "evidence.md").write_text("# evidence\n")

    result = asyncio.run(mcp_server.scan_result(SCAN_ID))

    assert result["phase"] == "complete"
    assert result["payload"]["top"][0]["rank"] == 1
    assert result["payload"]["top"][0]["relation"] == "design-changing"
    assert "why" not in result["payload"]["top"][0]
    assert "coverage_risks" not in result["payload"]
    assert result["payload"]["evidence_md"] == "# evidence\n"


def test_the_data_root_and_token_come_from_config(mcp_home):
    from research_scan import config

    settings = config.load()
    assert settings.mcp_data_dir == mcp_home
    assert settings.mcp_token == TOKEN
    assert settings.redact(f"token={TOKEN}") == "token=***REDACTED***"


def test_the_run_directory_is_isolated_per_scan(mcp_home):
    make_scan(mcp_home, {"01": [candidate("a")]})
    make_scan(mcp_home, {"01": [candidate("b")]}, scan_id=OTHER_SCAN)
    from research_scan import config

    settings = config.load()
    first = mcp_server.find_run_dir(mcp_server.scan_root(settings, SCAN_ID))
    second = mcp_server.find_run_dir(mcp_server.scan_root(settings, OTHER_SCAN))
    assert first != second
    assert first.is_relative_to(mcp_home / SCAN_ID)


def test_a_scan_id_outside_the_uuid_shape_never_reaches_the_filesystem():
    with pytest.raises(mcp_server.ScanFailure):
        mcp_server.valid_scan_id("../../etc")


def test_batches_are_offered_in_pipeline_order():
    names = ["x02", "01", "xr01", "r01", "02", "x01"]
    ordered = sorted(
        (Path(f"{name}.json") for name in names),
        key=lambda path: (
            mcp_server.BATCH_FAMILIES.index(mcp_server.batch_family(path.stem)),
            path.stem,
        ),
    )
    assert [path.stem for path in ordered] == ["01", "02", "x01", "x02", "r01", "xr01"]


def test_today_is_not_needed_by_the_adapter():
    """A guard: the adapter derives phase from files, never from the clock."""
    assert date.today() is not None


# --- scan_start: the client owns the id, so a timed-out call is retryable ----

V1_UUID = "d9428888-122b-11e1-b85c-61cd3cbb3210"
MIXED_CASE_V4 = "a1b2c3d4-e5f6-4a7b-8c9d-0e1f2a3b4c5d"
UPPERCASE_V4 = MIXED_CASE_V4.upper()


def start_call(**kwargs) -> dict:
    kwargs.setdefault("scan_id", SCAN_ID)
    kwargs.setdefault("brief", "# brief\n\nHow do defaults shape enrolment?\n")
    kwargs.setdefault("queries", make_plan())
    return asyncio.run(mcp_server.scan_start(**kwargs))


def stub_start_cli(root: Path, calls: list, *, items: list[dict] | None = None):
    """`init` then `retrieve`, recording whether the start inputs were on disk when each ran."""
    run_dir = root / "research" / "scans" / "2026-08-19-t"
    pool = items if items is not None else [candidate("a"), candidate("b")]

    def fake(cwd: Path, stage: str, *args: str) -> mcp_server.StageOutcome:
        calls.append(
            {
                "stage": stage,
                "args": args,
                "inputs_persisted": mcp_server.options_path(root).exists(),
            }
        )
        if stage == "init":
            scaffold(run_dir)
        elif stage == "retrieve":
            info = json.loads((run_dir / "manifest.json").read_text())["run"]
            (run_dir / "candidates.json").write_text(
                json.dumps({"run": info, "candidates": pool})
            )
            (run_dir / "screen-batches" / "01.json").write_text(
                json.dumps(batch_payload("01", pool))
            )
        return mcp_server.StageOutcome(stage=stage, code=0, payload={"ok": True}, stderr="")

    return fake


@pytest.mark.parametrize(
    "bad",
    ["not-a-uuid", "", "  ", "{" + SCAN_ID + "}", "urn:uuid:" + SCAN_ID, SCAN_ID.replace("-", "")],
)
def test_a_malformed_scan_id_is_refused_and_touches_no_disk(mcp_home, bad):
    before = snapshot(mcp_home) if mcp_home.exists() else {}

    result = start_call(scan_id=bad)

    assert result["status"] == "invalid_artifact"
    assert result["payload"]["code"] == "invalid_scan_id"
    assert result["next_action"] is None
    assert (snapshot(mcp_home) if mcp_home.exists() else {}) == before


@pytest.mark.parametrize(("bad", "why"), [(V1_UUID, "v1"), (UPPERCASE_V4, "uppercase v4")])
def test_a_v1_or_uppercase_id_is_refused_exactly_like_a_malformed_one(mcp_home, bad, why):
    before = snapshot(mcp_home) if mcp_home.exists() else {}

    result = start_call(scan_id=bad)

    assert result["payload"]["code"] == "invalid_scan_id", why
    assert result["status"] == "invalid_artifact"
    assert (snapshot(mcp_home) if mcp_home.exists() else {}) == before


def test_the_start_inputs_are_on_disk_before_retrieve_runs(mcp_home, monkeypatch):
    root = mcp_home / SCAN_ID
    calls: list = []
    monkeypatch.setattr(mcp_server, "run_stage", stub_start_cli(root, calls))

    result = start_call()

    assert [call["stage"] for call in calls] == ["init", "retrieve"]
    assert all(call["inputs_persisted"] for call in calls), (
        "a scan_start that dies mid-retrieve must still leave the record a retry compares against"
    )
    assert result["next_action"] == "screen_candidates"
    assert result["scan_id"] == SCAN_ID

    persisted = json.loads(mcp_server.options_path(root).read_text())
    assert persisted["brief"].startswith("# brief")
    assert persisted["queries"]["domain"] == "behavioral"
    assert persisted["profile"] == "standard"


def test_an_identical_retry_resumes_instead_of_retrieving_again(mcp_home, monkeypatch):
    root = mcp_home / SCAN_ID
    calls: list = []
    monkeypatch.setattr(mcp_server, "run_stage", stub_start_cli(root, calls))

    first = start_call()
    assert [call["stage"] for call in calls] == ["init", "retrieve"]

    retry = start_call()

    assert [call["stage"] for call in calls] == ["init", "retrieve"], "no stage ran twice"
    assert retry["scan_id"] == first["scan_id"]
    assert retry["phase"] == first["phase"] == "screen"
    assert retry["next_action"] == "screen_candidates"
    assert retry["payload"]["screen_batch"] == first["payload"]["screen_batch"]

    # And the resumed envelope tracks the run as it moves, rather than replaying the first answer.
    items = retry["payload"]["screen_batch"]["items"]
    monkeypatch.setattr(mcp_server, "run_stage", stub_cli(root))
    continue_call(
        scan_id=SCAN_ID,
        screen_scores=[
            {"cid": item["cid"], "score": 3, "reason": "relevant", "criteria_hit": ["C1"]}
            for item in items
        ],
    )
    assert start_call()["progress"]["batches_scored"] == 1


def test_the_same_id_with_different_inputs_is_a_conflict_and_changes_nothing(mcp_home, monkeypatch):
    root = mcp_home / SCAN_ID
    calls: list = []
    monkeypatch.setattr(mcp_server, "run_stage", stub_start_cli(root, calls))
    start_call()
    before = snapshot(root)

    conflict = start_call(profile=Profile.quick)

    assert conflict["status"] == "invalid_artifact"
    assert conflict["payload"]["code"] == "scan_id_conflict"
    assert conflict["payload"]["errors"] == ["differs: profile"]
    assert [call["stage"] for call in calls] == ["init", "retrieve"], "the conflict ran no stage"
    assert snapshot(root) == before


def test_a_conflict_names_every_differing_key_and_no_values(mcp_home, monkeypatch):
    root = mcp_home / SCAN_ID
    monkeypatch.setattr(mcp_server, "run_stage", stub_start_cli(root, []))
    secret_brief = "# brief\n\nA different question entirely.\n"
    start_call()

    conflict = start_call(brief=secret_brief, top=3)

    assert conflict["payload"]["errors"] == ["differs: brief", "differs: top"]
    assert secret_brief not in json.dumps(conflict), "a conflict names keys, never their contents"


def test_an_identical_retry_while_the_first_call_runs_is_told_to_wait(mcp_home, monkeypatch):
    root = mcp_home / SCAN_ID
    monkeypatch.setattr(mcp_server, "run_stage", stub_start_cli(root, []))
    before = snapshot(mcp_home) if mcp_home.exists() else {}

    assert mcp_server.acquire(SCAN_ID) is None
    try:
        retry = start_call()
    finally:
        mcp_server.release()

    assert retry["status"] == "in_progress"
    assert retry["next_action"] is None
    assert "do not resubmit" in retry["payload"]["error"]
    assert (snapshot(mcp_home) if mcp_home.exists() else {}) == before


# --- scan_result carries the packet's url, it never derives one -------------

TRANSPORT_RUN = Path("research/scans/2026-08-20-agentic-lit-search-mcp-transport")


def test_the_summary_rows_copy_the_packet_url_verbatim(mcp_home):
    items = [candidate("a")]
    root = make_scan(mcp_home, {"01": items})
    run_dir = root / "research" / "scans" / "2026-08-19-t"
    packet = {
        **items[0],
        "criteria": {"C1": 3},
        "overall": 3,
        "evidence_level": "rct",
        "key_finding": "a finding",
        "methodology": "abstract-only",
        "why_it_matters": "it matters",
        "limitations": ["small n"],
        "relevance_reason": "on point",
        "verification": {
            "verified": True,
            "verified_by": ["crossref"],
            "verified_on": "2026-08-19",
        },
        "rank": 1,
        "selection_reason": "score",
        "url": "https://arxiv.org/abs/2501.10120",
    }
    manifest = json.loads((run_dir / "manifest.json").read_text())
    (run_dir / "evidence.json").write_text(
        json.dumps({"run": manifest["run"], "packets": [packet], "alternates": []})
    )

    row = asyncio.run(mcp_server.scan_result(SCAN_ID))["payload"]["top"][0]

    assert row["url"] == "https://arxiv.org/abs/2501.10120"
    assert row["doi"] == items[0]["ids"]["doi"]


def test_a_packet_without_a_url_still_summarises(mcp_home):
    items = [candidate("a")]
    root = make_scan(mcp_home, {"01": items})
    run_dir = root / "research" / "scans" / "2026-08-19-t"
    bare = {k: v for k, v in items[0].items() if k != "ids"}
    packet = {
        **bare,
        "ids": {},
        "criteria": {"C1": 3},
        "overall": 3,
        "evidence_level": "rct",
        "key_finding": "a finding",
        "methodology": "abstract-only",
        "why_it_matters": "it matters",
        "limitations": ["small n"],
        "relevance_reason": "on point",
        "verification": {"verified": True, "verified_by": [], "verified_on": "2026-08-19"},
        "rank": 1,
        "selection_reason": "score",
    }
    manifest = json.loads((run_dir / "manifest.json").read_text())
    (run_dir / "evidence.json").write_text(
        json.dumps({"run": manifest["run"], "packets": [packet], "alternates": []})
    )

    row = asyncio.run(mcp_server.scan_result(SCAN_ID))["payload"]["top"][0]

    assert row["url"] is None
    assert row["doi"] is None
    assert row["rank"] == 1


@pytest.mark.parametrize(
    ("title", "arxiv"),
    [("ScholarGym", "2601.21654"), ("Diagnosing Search Behavior", "2608.01913")],
)
def test_a_doi_less_preprint_keeps_its_arxiv_url_through_to_the_summary(title, arxiv):
    """Both papers are real, DOI-less, and in the committed v0.4.0 transport run."""
    evidence = json.loads((TRANSPORT_RUN / "evidence.json").read_text())
    packet = next(p for p in evidence["packets"] if p["title"].startswith(title))

    assert packet["ids"]["doi"] is None
    assert packet["url"] == f"https://arxiv.org/abs/{arxiv}"

    summary = SummaryPaper.model_validate(
        {
            "rank": packet["rank"],
            "title": packet["title"],
            "year": packet["year"],
            "doi": packet["ids"]["doi"],
            "url": packet["url"],
            "evidence_level": packet["evidence_level"],
            "verified": packet["verification"]["verified"],
            "why": "carried through verbatim",
        }
    )
    assert summary.url == packet["url"]
    assert summary.doi is None
