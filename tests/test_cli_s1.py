"""`init` and `retrieve` end to end: run directories, exit codes, manifest, batches (spec §6)."""

from __future__ import annotations

import json
from datetime import date
from pathlib import Path

import httpx
import pytest
import respx
from typer.testing import CliRunner

from conftest import FIXTURES, load_fixture, plan_payload
from research_scan import http, run
from research_scan.cli import app
from research_scan.schema import CandidatesFile, Manifest, RunInfo
from research_scan.sources import openalex as openalex_module
from research_scan.sources import s2 as s2_module

FROZEN_TODAY = date(2026, 8, 18)
runner = CliRunner()


@pytest.fixture(autouse=True)
def frozen_and_fast(monkeypatch):
    """A fixed clock for reproducible run names, and no real waiting on rate limits."""
    monkeypatch.setattr(run, "today", lambda: FROZEN_TODAY)
    monkeypatch.setattr(http.RateLimiter, "acquire", lambda self, host: 0.0)


@pytest.fixture
def workspace(fake_settings, tmp_path) -> Path:
    """`fake_settings` already chdir'd into tmp_path and isolated HOME."""
    return tmp_path


def write_brief(directory: Path) -> Path:
    brief = directory / "brief.example.md"
    brief.write_text("# Defaults\n\nWhat should we know before designing the enrolment flow?\n")
    return brief


def init_run(brief: str, *args: str):
    return runner.invoke(app, ["init", brief, "--json", *args])


# --- init -------------------------------------------------------------------


def test_init_from_a_brief_file(workspace):
    brief = write_brief(workspace)

    result = init_run(str(brief), "--slug", "s1-smoke")

    assert result.exit_code == 0
    info = RunInfo.model_validate(json.loads(result.stdout))
    assert info.run_dir == "research/scans/2026-08-18-s1-smoke"
    assert Path(info.brief_path).read_text().startswith("# Defaults")
    assert info.defaults.window.from_ == "2023-08"  # 36 months back
    assert info.defaults.window.to is None


def test_init_from_a_bare_question(workspace):
    result = init_run("What do defaults do to subscription churn?")

    assert result.exit_code == 0
    info = RunInfo.model_validate(json.loads(result.stdout))
    assert info.slug == "what-do-defaults-do-to-subscription"  # first six words, kebabbed
    assert "subscription churn" in Path(info.brief_path).read_text()


def test_init_writes_a_manifest_carrying_the_defaults(workspace):
    brief = write_brief(workspace)

    result = init_run(
        str(brief), "--slug", "m", "--top", "8", "--foundational", "1", "--domain", "cs"
    )

    info = RunInfo.model_validate(json.loads(result.stdout))
    manifest = Manifest.model_validate(
        json.loads((Path(info.run_dir) / "manifest.json").read_text())
    )
    assert manifest.defaults.top == 8
    assert manifest.defaults.foundational == 1
    assert manifest.defaults.domain.value == "cs"
    assert [source.value for source in manifest.defaults.sources] == ["openalex", "s2", "arxiv"]
    assert manifest.retrieval is None  # each command owns its own section


def test_init_honours_an_explicit_window(workspace):
    brief = write_brief(workspace)
    result = init_run(str(brief), "--slug", "w", "--from", "2020-01", "--to", "2024-12")
    info = RunInfo.model_validate(json.loads(result.stdout))
    assert (info.defaults.window.from_, info.defaults.window.to) == ("2020-01", "2024-12")


def test_init_rejects_a_malformed_window(workspace):
    brief = write_brief(workspace)
    result = init_run(str(brief), "--from", "2020")
    assert result.exit_code == 2


def test_init_without_json_prints_the_next_step(workspace):
    brief = write_brief(workspace)
    result = runner.invoke(app, ["init", str(brief), "--slug", "human"])
    assert result.exit_code == 0
    assert "queries.json" in result.stdout


# --- retrieve ---------------------------------------------------------------


def prepare_run(workspace: Path, *init_args: str, **plan_overrides) -> Path:
    brief = write_brief(workspace)
    result = init_run(str(brief), "--slug", "s1-smoke", "--domain", "behavioral", *init_args)
    assert result.exit_code == 0, result.stdout
    run_dir = Path(json.loads(result.stdout)["run_dir"])
    (run_dir / "queries.json").write_text(json.dumps(plan_payload(**plan_overrides)))
    return run_dir


def mock_both_sources(openalex_status: int = 200, s2_status: int = 200) -> None:
    openalex = load_fixture("openalex_defaults.json")
    s2 = load_fixture("s2_defaults.json")
    respx.get(openalex_module.WORKS_URL).mock(
        return_value=httpx.Response(
            openalex_status, json=openalex if openalex_status == 200 else {}
        )
    )
    respx.get(s2_module.SEARCH_URL).mock(
        return_value=httpx.Response(s2_status, json=s2 if s2_status == 200 else {})
    )


@respx.mock
def test_retrieve_writes_every_expected_file(workspace):
    run_dir = prepare_run(workspace)
    mock_both_sources()

    result = runner.invoke(app, ["retrieve", "--json", "--quiet"])

    assert result.exit_code == 0, result.stdout + result.stderr
    payload = json.loads(result.stdout)
    assert payload["ok"] is True
    assert (run_dir / "candidates.json").exists()
    assert (run_dir / "retrieval.log.jsonl").exists()
    assert sorted(path.name for path in (run_dir / "screen-batches").glob("*.json")) == ["01.json"]


@respx.mock
def test_retrieve_merges_the_same_paper_across_both_sources(workspace):
    """The AER paper is the top hit for both APIs in the recorded fixtures."""
    run_dir = prepare_run(workspace)
    mock_both_sources()

    runner.invoke(app, ["retrieve", "--json", "--quiet"])

    candidates = CandidatesFile.model_validate(
        json.loads((run_dir / "candidates.json").read_text())
    )
    aer = [c for c in candidates.candidates if c.ids.doi == "10.1257/aer.20210881"]
    assert len(aer) == 1
    sources = {origin.source.value for origin in aer[0].origins}
    assert sources == {"openalex", "s2"}
    assert aer[0].ids.openalex and aer[0].ids.s2  # both identifiers survived the merge


@respx.mock
def test_retrieve_records_its_manifest_section_and_counts(workspace):
    run_dir = prepare_run(workspace)
    mock_both_sources()

    runner.invoke(app, ["retrieve", "--json", "--quiet"])

    manifest = Manifest.model_validate(json.loads((run_dir / "manifest.json").read_text()))
    assert manifest.retrieval is not None
    assert manifest.retrieval.per_source["openalex"].queried == 6
    assert manifest.retrieval.per_source["s2"].queried == 6
    assert manifest.retrieval.deduped_remaining > 0
    assert manifest.retrieval.abstracts_present > 0
    assert manifest.counts.retrieved == 36  # 6 queries × 2 sources × 3 fixture hits
    assert manifest.defaults.domain.value == "behavioral"  # init's section is untouched


@respx.mock
def test_retrieve_logs_one_jsonl_line_per_stage(workspace):
    run_dir = prepare_run(workspace)
    mock_both_sources()

    runner.invoke(app, ["retrieve", "--json", "--quiet"])

    events = [
        json.loads(line)
        for line in (run_dir / "retrieval.log.jsonl").read_text().splitlines()
        if line
    ]
    names = [event["event"] for event in events]
    assert names[0] == "enter"
    assert names[-1] == "exit"
    for stage in ("plan", "fan_out", "dedup", "filter", "cap", "batches", "http"):
        assert stage in names


@respx.mock
def test_retrieve_applies_must_not_from_the_plan(workspace):
    run_dir = prepare_run(workspace, must_not=["retirement"])
    mock_both_sources()

    runner.invoke(app, ["retrieve", "--json", "--quiet"])

    manifest = Manifest.model_validate(json.loads((run_dir / "manifest.json").read_text()))
    assert manifest.retrieval.dropped.must_not > 0


@respx.mock
def test_retrieve_honours_the_sources_override(workspace):
    prepare_run(workspace)
    mock_both_sources()

    result = runner.invoke(app, ["retrieve", "--json", "--quiet", "--sources", "openalex"])

    payload = json.loads(result.stdout)
    assert set(payload["retrieval"]["per_source"]) == {"openalex"}


@respx.mock
def test_retrieve_records_an_unbuilt_source_instead_of_skipping_it_silently(workspace):
    # arXiv is built as of S10g, so PubMed (S6) is the unbuilt source biomed routes to.
    prepare_run(workspace, domain="biomed")
    mock_both_sources()

    result = runner.invoke(app, ["retrieve", "--json", "--quiet"])

    assert result.exit_code == 0
    per_source = json.loads(result.stdout)["retrieval"]["per_source"]
    assert per_source["pubmed"]["unavailable"] is True
    assert per_source["openalex"]["unavailable"] is False


@respx.mock
def test_retrieve_survives_one_source_failing(workspace):
    prepare_run(workspace)
    mock_both_sources(s2_status=403)

    result = runner.invoke(app, ["retrieve", "--json", "--quiet"])

    assert result.exit_code == 0
    per_source = json.loads(result.stdout)["retrieval"]["per_source"]
    assert per_source["s2"]["failed"] == 6
    assert per_source["openalex"]["hits"] == 18


@respx.mock
def test_retrieve_exits_one_when_every_source_fails(workspace):
    prepare_run(workspace)
    mock_both_sources(openalex_status=403, s2_status=403)

    result = runner.invoke(app, ["retrieve", "--json", "--quiet"])

    assert result.exit_code == 1
    assert "every routed source failed" in result.stderr


@respx.mock
def test_retrieve_exits_one_when_no_routed_source_is_built(workspace):
    prepare_run(workspace)
    result = runner.invoke(app, ["retrieve", "--json", "--quiet", "--sources", "pubmed"])
    assert result.exit_code == 1
    assert "no usable source" in result.stderr


def test_retrieve_exits_two_with_the_pydantic_error_list(workspace):
    run_dir = prepare_run(workspace)
    broken = plan_payload()
    broken["queries"] = broken["queries"][:4]
    broken["domain"] = "auto"
    (run_dir / "queries.json").write_text(json.dumps(broken))

    result = runner.invoke(app, ["retrieve", "--json", "--quiet"])

    assert result.exit_code == 2
    payload = json.loads(result.stderr)
    assert payload["ok"] is False
    assert any("domain" in line for line in payload["errors"])
    assert any("queries" in line for line in payload["errors"])


def test_retrieve_exits_two_on_malformed_json(workspace):
    run_dir = prepare_run(workspace)
    (run_dir / "queries.json").write_text("{not json")

    result = runner.invoke(app, ["retrieve", "--json", "--quiet"])

    assert result.exit_code == 2
    assert "not valid JSON" in result.stderr


def test_retrieve_exits_two_when_queries_json_is_missing(workspace):
    run_dir = prepare_run(workspace)
    (run_dir / "queries.json").unlink()

    result = runner.invoke(app, ["retrieve", "--quiet"])

    assert result.exit_code == 2
    assert "queries.json" in result.stderr


def test_retrieve_exits_two_with_no_run_directory(workspace):
    result = runner.invoke(app, ["retrieve", "--quiet"])
    assert result.exit_code == 2
    assert "init" in result.stderr


def test_retrieve_rejects_an_unknown_source(workspace):
    prepare_run(workspace)
    result = runner.invoke(app, ["retrieve", "--quiet", "--sources", "scopus"])
    assert result.exit_code == 2
    assert "scopus" in result.stderr


@respx.mock
def test_retrieve_uses_the_newest_run_by_default(workspace):
    prepare_run(workspace)
    brief = write_brief(workspace)
    later = init_run(str(brief), "--slug", "zz-later")
    newer_dir = Path(json.loads(later.stdout)["run_dir"])
    (newer_dir / "queries.json").write_text(json.dumps(plan_payload()))
    mock_both_sources()

    result = runner.invoke(app, ["retrieve", "--json", "--quiet"])

    assert json.loads(result.stdout)["run_dir"] == str(newer_dir)


@respx.mock
def test_explicit_run_flag_wins(workspace):
    run_dir = prepare_run(workspace)
    brief = write_brief(workspace)
    later = init_run(str(brief), "--slug", "zz-later")
    (Path(json.loads(later.stdout)["run_dir"]) / "queries.json").write_text(
        json.dumps(plan_payload())
    )
    mock_both_sources()

    result = runner.invoke(app, ["retrieve", "--json", "--quiet", "--run", str(run_dir)])

    assert json.loads(result.stdout)["run_dir"] == str(run_dir)


@respx.mock
def test_rerunning_retrieve_is_served_from_the_cache(workspace):
    """Acceptance §14.8: an unchanged re-run makes no network calls."""
    prepare_run(workspace)
    openalex = respx.get(openalex_module.WORKS_URL).mock(
        return_value=httpx.Response(200, json=load_fixture("openalex_defaults.json"))
    )
    respx.get(s2_module.SEARCH_URL).mock(
        return_value=httpx.Response(200, json=load_fixture("s2_defaults.json"))
    )

    runner.invoke(app, ["retrieve", "--json", "--quiet"])
    first_calls = openalex.call_count
    runner.invoke(app, ["retrieve", "--json", "--quiet"])

    assert openalex.call_count == first_calls


@respx.mock
def test_no_cache_forces_fresh_calls(workspace):
    prepare_run(workspace)
    openalex = respx.get(openalex_module.WORKS_URL).mock(
        return_value=httpx.Response(200, json=load_fixture("openalex_defaults.json"))
    )
    respx.get(s2_module.SEARCH_URL).mock(
        return_value=httpx.Response(200, json=load_fixture("s2_defaults.json"))
    )

    runner.invoke(app, ["retrieve", "--json", "--quiet", "--no-cache"])
    runner.invoke(app, ["retrieve", "--json", "--quiet", "--no-cache"])

    assert openalex.call_count == 12


@respx.mock
def test_cs_routing_derives_the_three_source_cap_on_the_deep_profile(workspace):
    """cs → openalex + s2 + arxiv, and `deep` scales the cap to 675 (S10g, profiled in v0.2.1)."""
    run_dir = prepare_run(workspace, "--profile", "deep", domain="cs")
    mock_both_sources()
    arxiv_feed = (FIXTURES / "arxiv-search.atom.xml").read_text(encoding="utf-8")
    respx.get(url__regex=r"https://export\.arxiv\.org/api/query.*").mock(
        return_value=httpx.Response(200, text=arxiv_feed)
    )

    result = runner.invoke(app, ["retrieve", "--json", "--quiet"])

    assert result.exit_code == 0, result.output
    per_source = json.loads(result.stdout)["retrieval"]["per_source"]
    assert per_source["arxiv"]["unavailable"] is False
    assert per_source["arxiv"]["hits"] > 0
    log_lines = [
        json.loads(line) for line in (run_dir / "retrieval.log.jsonl").read_text().splitlines()
    ]
    plan = next(entry for entry in log_lines if entry["event"] == "plan")
    assert plan["max_candidates"] == 675
    assert plan["profile"] == "deep"
    assert plan["sources"] == ["openalex", "s2", "arxiv"]


@respx.mock
def test_the_standard_profile_holds_the_cap_flat_even_for_three_sources(workspace):
    """`deep` buys the scaled cap; `standard` bounds cost at 450 whatever is routed (v0.2.1)."""
    run_dir = prepare_run(workspace, domain="cs")
    mock_both_sources()
    arxiv_feed = (FIXTURES / "arxiv-search.atom.xml").read_text(encoding="utf-8")
    respx.get(url__regex=r"https://export\.arxiv\.org/api/query.*").mock(
        return_value=httpx.Response(200, text=arxiv_feed)
    )

    runner.invoke(app, ["retrieve", "--json", "--quiet"])

    log_lines = [
        json.loads(line) for line in (run_dir / "retrieval.log.jsonl").read_text().splitlines()
    ]
    plan = next(entry for entry in log_lines if entry["event"] == "plan")
    assert (plan["profile"], plan["max_candidates"], plan["per_query"]) == ("standard", 450, 40)


@respx.mock
def test_the_quick_profile_shrinks_depth_and_cap_together(workspace):
    run_dir = prepare_run(workspace, "--profile", "quick")
    mock_both_sources()

    runner.invoke(app, ["retrieve", "--json", "--quiet"])

    log_lines = [
        json.loads(line) for line in (run_dir / "retrieval.log.jsonl").read_text().splitlines()
    ]
    plan = next(entry for entry in log_lines if entry["event"] == "plan")
    assert (plan["profile"], plan["max_candidates"], plan["per_query"]) == ("quick", 250, 20)


@respx.mock
def test_a_flag_still_beats_the_profile(workspace):
    prepare_run(workspace, "--profile", "quick")
    mock_both_sources()

    runner.invoke(app, ["retrieve", "--per-query", "5", "--max-candidates", "7", "--quiet"])

    run_dir = Path("research/scans/2026-08-18-s1-smoke")
    log_lines = [
        json.loads(line) for line in (run_dir / "retrieval.log.jsonl").read_text().splitlines()
    ]
    plan = next(entry for entry in log_lines if entry["event"] == "plan")
    assert (plan["per_query"], plan["max_candidates"]) == (5, 7)


def test_the_profile_is_recorded_in_the_manifest(workspace):
    run_dir = prepare_run(workspace, "--profile", "deep")
    manifest = Manifest.model_validate(json.loads((run_dir / "manifest.json").read_text()))
    assert manifest.defaults.profile.value == "deep"


# --- the root callback -------------------------------------------------------


def test_version_prints_and_exits_zero():
    """`--help` advertises `--version`, so it has to work — it exited 2 until S5."""
    from research_scan import __version__

    result = runner.invoke(app, ["--version"])

    assert result.exit_code == 0
    assert result.stdout.strip() == __version__


def test_no_arguments_still_shows_help_rather_than_running_anything():
    assert runner.invoke(app, []).exit_code == 2


def test_the_reported_version_is_the_one_written_in_pyproject():
    """The single-source guarantee, as a test.

    `__version__` resolves from the installed distribution, so a bump to `pyproject.toml`
    that never reached an install would silently keep reporting the old number. Four
    version strings already drifted apart once; this is the check that would have caught it.
    """
    import tomllib
    from importlib.metadata import version as distribution_version

    from research_scan import __version__

    pyproject = Path(__file__).parent.parent / "pyproject.toml"
    written = tomllib.loads(pyproject.read_text(encoding="utf-8"))["project"]["version"]

    assert __version__ == distribution_version("research-scan")
    assert __version__ == written, (
        f"pyproject.toml says {written}, the installed distribution says {__version__} —"
        " reinstall (`uv sync`) after a version bump"
    )
    assert runner.invoke(app, ["--version"]).stdout.strip() == written


def test_version_command_reports_the_runtime_it_is_running_on():
    result = runner.invoke(app, ["version", "--json"])

    assert result.exit_code == 0
    payload = json.loads(result.stdout)
    assert set(payload) == {"version", "python", "platform", "mcp"}
    assert payload["version"] == runner.invoke(app, ["--version"]).stdout.strip()
    assert payload["mcp"] in {"enabled", "disabled"}
    # No `commit` field: the package carries no git SHA and inventing one would be a lie.
    assert "commit" not in payload


# --- the gap round (V1.1) ---------------------------------------------------


GAP_QUERY = {
    "id": "G1",
    "type": "gap",
    "text": "forced active choice",
    "mode": "semantic",
    "target_criterion": "C2",
}


def gap_work() -> dict:
    """One OpenAlex work no round-1 query returned, so the gap round has something to add."""
    return {
        "meta": {"count": 1},
        "results": [
            {
                "id": "https://openalex.org/W9999999999",
                "doi": "https://doi.org/10.1234/active.choice",
                "title": "Active choice and enrolment",
                "publication_date": "2025-01-15",
                "publication_year": 2025,
                "type": "article",
                "authorships": [
                    {
                        "author_position": "first",
                        "author": {"id": "https://openalex.org/A1", "display_name": "Bo Chooser"},
                    }
                ],
                "cited_by_count": 3,
                "is_retracted": False,
                "abstract_inverted_index": {"Active": [0], "choice": [1]},
            }
        ],
    }


def mock_gap_round() -> None:
    """Round-1 queries get the recorded fixture; the gap query gets its own work."""
    openalex = load_fixture("openalex_defaults.json")
    s2 = load_fixture("s2_defaults.json")

    def route(request: httpx.Request) -> httpx.Response:
        search = request.url.params.get("search") or request.url.params.get("query") or ""
        return httpx.Response(200, json=gap_work() if "active choice" in search else openalex)

    respx.get(openalex_module.WORKS_URL).mock(side_effect=route)
    respx.get(s2_module.SEARCH_URL).mock(return_value=httpx.Response(200, json=s2))


@respx.mock
def test_the_gap_round_appends_and_never_evicts_round_one(workspace):
    run_dir = prepare_run(workspace, round2=[GAP_QUERY])
    mock_gap_round()

    assert runner.invoke(app, ["retrieve", "--json", "--quiet"]).exit_code == 0
    before = CandidatesFile.model_validate(json.loads((run_dir / "candidates.json").read_text()))

    result = runner.invoke(app, ["retrieve", "--round", "2", "--json", "--quiet"])

    assert result.exit_code == 0, result.stdout + result.stderr
    payload = json.loads(result.stdout)
    after = CandidatesFile.model_validate(json.loads((run_dir / "candidates.json").read_text()))
    kept = {c.cid for c in before.candidates}
    assert kept <= {c.cid for c in after.candidates}  # round 1 survives whole
    assert payload["added"] == len(after.candidates) - len(before.candidates)
    assert payload["added"] >= 1
    assert "10.1234/active.choice" in {c.ids.doi for c in after.candidates}


@respx.mock
def test_the_gap_round_batches_under_r_and_leaves_the_other_families_alone(workspace):
    run_dir = prepare_run(workspace, round2=[GAP_QUERY])
    mock_gap_round()
    runner.invoke(app, ["retrieve", "--json", "--quiet"])
    (run_dir / "screen-batches" / "x01.json").write_text("{}")  # a stand-in expansion batch

    runner.invoke(app, ["retrieve", "--round", "2", "--json", "--quiet"])

    names = sorted(path.name for path in (run_dir / "screen-batches").glob("*.json"))
    assert names == ["01.json", "r01.json", "x01.json"]


@respx.mock
def test_the_gap_round_records_its_own_manifest_section_and_log(workspace):
    run_dir = prepare_run(workspace, round2=[GAP_QUERY])
    mock_gap_round()
    runner.invoke(app, ["retrieve", "--json", "--quiet"])
    round_one = Manifest.model_validate(json.loads((run_dir / "manifest.json").read_text()))

    runner.invoke(app, ["retrieve", "--round", "2", "--json", "--quiet"])

    manifest = Manifest.model_validate(json.loads((run_dir / "manifest.json").read_text()))
    assert manifest.retrieval_round2 is not None
    assert manifest.retrieval == round_one.retrieval  # round 1's section is never replaced
    assert manifest.counts.retrieved > round_one.counts.retrieved
    assert "retrieve-r2.started_at" in manifest.timestamps
    assert (run_dir / "retrieval-r2.log.jsonl").exists()
    assert (run_dir / "retrieval.log.jsonl").read_text()  # round 1's log was not truncated


@respx.mock
def test_a_gap_round_without_round2_queries_exits_two(workspace):
    prepare_run(workspace)
    mock_both_sources()
    runner.invoke(app, ["retrieve", "--json", "--quiet"])

    result = runner.invoke(app, ["retrieve", "--round", "2", "--json", "--quiet"])

    assert result.exit_code == 2
    assert "round2" in result.stdout + result.stderr
