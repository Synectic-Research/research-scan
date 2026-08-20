"""`expand`, `shortlist`, `verify` and `emit` end to end: files and exit codes (spec §6)."""

from __future__ import annotations

import json
from datetime import date
from pathlib import Path

import httpx
import pytest
import respx
from typer.testing import CliRunner

from conftest import plan_payload, ranked_entry, verification_payload
from research_scan import expand, http, run
from research_scan.cli import app
from research_scan.dedup import with_cid
from research_scan.schema import (
    CandidatesFile,
    Evidence,
    Manifest,
    Ranked,
    RunInfo,
    Shortlist,
)
from research_scan.sources import crossref as crossref_module
from research_scan.sources import openalex as openalex_module
from research_scan.sources import s2 as s2_module

FROZEN_TODAY = date(2026, 8, 19)
runner = CliRunner()

CROSSREF_PATTERN = r"https://api\.crossref\.org/works/.*"
OPENALEX_PATTERN = r"https://api\.openalex\.org/works.*"


@pytest.fixture(autouse=True)
def frozen_and_fast(monkeypatch):
    """Fixed clock for reproducible names; no real waiting on rate limits or retry backoff."""
    monkeypatch.setattr(run, "today", lambda: FROZEN_TODAY)
    monkeypatch.setattr(http.RateLimiter, "acquire", lambda self, host: 0.0)
    monkeypatch.setattr(http.time, "sleep", lambda _seconds: None)


@pytest.fixture
def workspace(fake_settings, tmp_path) -> Path:
    return tmp_path


def candidate_payload(cid_seed: str, **overrides) -> dict:
    from conftest import make_candidate

    candidate = with_cid(
        make_candidate(
            title=overrides.pop("title", f"Paper {cid_seed}"),
            doi=overrides.pop("doi", f"10.1000/{cid_seed}"),
            year=overrides.pop("year", 2024),
            publication_date=overrides.pop("publication_date", "2024-01-01"),
            abstract=overrides.pop("abstract", "An abstract about enrolment defaults."),
            # Distinct first authors: identical ones would trip the §10.4 diversity cap.
            authors=overrides.pop("authors", (f"Ada Author{cid_seed}",)),
            **overrides,
        )
    )
    return candidate.model_dump(mode="json")


def make_run(workspace: Path, candidates: list[dict], **files) -> Path:
    """Build a run directory by hand — S2's stages only need files, not a live retrieve."""
    run_dir = workspace / "research" / "scans" / "2026-08-19-t"
    run_dir.mkdir(parents=True)
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
                "tool_version": "0.1.0",
            }
        ),
    )
    (run_dir / "queries.json").write_text(json.dumps(plan_payload()))
    (run_dir / "candidates.json").write_text(
        json.dumps({"run": info.model_dump(mode="json"), "candidates": candidates})
    )
    for name, payload in files.items():
        (run_dir / f"{name}.json").write_text(json.dumps(payload))
    return run_dir


def screen_payload(*pairs: tuple[str, int]) -> dict:
    return {"scores": [{"cid": cid, "score": score, "reason": "why"} for cid, score in pairs]}


# --- expand -----------------------------------------------------------------


@respx.mock
def test_expand_writes_expanded_json_and_x_batches(workspace):
    seed = candidate_payload("seed", openalex="W1")
    run_dir = make_run(workspace, [seed], screen=screen_payload((seed["cid"], 3)))

    respx.get(url__regex=r".*/references").mock(
        return_value=httpx.Response(
            200,
            json={
                "data": [
                    {
                        "citedPaper": {
                            "paperId": "old",
                            "title": "A 2004 classic",
                            "year": 2004,
                            "publicationDate": "2004-05-01",
                            "citationCount": 900,
                            "externalIds": {"DOI": "10.1000/classic"},
                        }
                    }
                ]
            },
        )
    )
    respx.get(url__regex=r".*/citations").mock(
        return_value=httpx.Response(
            200,
            json={
                "data": [
                    {
                        "citingPaper": {
                            "paperId": "new",
                            "title": "A 2025 answer",
                            "year": 2025,
                            "publicationDate": "2025-05-01",
                            "citationCount": 4,
                            "externalIds": {"DOI": "10.1000/answer"},
                        }
                    }
                ]
            },
        )
    )
    respx.post(s2_module.RECOMMENDATIONS_URL).mock(
        return_value=httpx.Response(200, json={"recommendedPapers": []})
    )

    result = runner.invoke(app, ["expand", "--json", "--quiet"])

    assert result.exit_code == 0, result.stdout + result.stderr
    payload = json.loads(result.stdout)
    assert payload["seeds"] == [seed["cid"]]
    assert len(payload["added"]) == 1
    assert len(payload["added_outside_window"]) == 1
    assert payload["batches"] == ["x01"]
    assert (run_dir / "expanded.json").exists()
    assert (run_dir / "screen-batches" / "x01.json").exists()
    assert (run_dir / "expansion.log.jsonl").exists()

    written = CandidatesFile.model_validate(json.loads((run_dir / "candidates.json").read_text()))
    classic = next(c for c in written.candidates if c.title == "A 2004 classic")
    assert classic.outside_window is True
    assert classic.origins[0].relation.value == "references"
    assert classic.origins[0].query_id is None


@respx.mock
def test_expand_records_its_manifest_section(workspace):
    seed = candidate_payload("seed")
    run_dir = make_run(workspace, [seed], screen=screen_payload((seed["cid"], 2)))
    respx.get(url__regex=r".*/(references|citations)").mock(
        return_value=httpx.Response(200, json={"data": []})
    )
    respx.post(s2_module.RECOMMENDATIONS_URL).mock(
        return_value=httpx.Response(200, json={"recommendedPapers": []})
    )

    runner.invoke(app, ["expand", "--json", "--quiet"])

    manifest = Manifest.model_validate(json.loads((run_dir / "manifest.json").read_text()))
    assert manifest.expansion is not None
    assert manifest.expansion.seeds == 1
    assert manifest.defaults.domain.value == "behavioral"  # init's section untouched


def test_expand_exits_one_when_nothing_was_screened_relevant(workspace):
    seed = candidate_payload("seed")
    make_run(workspace, [seed], screen=screen_payload((seed["cid"], 1)))

    result = runner.invoke(app, ["expand", "--json", "--quiet"])

    assert result.exit_code == 1
    assert "nothing to grow from" in result.stderr


def test_expand_exits_two_without_a_screen_file(workspace):
    make_run(workspace, [candidate_payload("seed")])
    result = runner.invoke(app, ["expand", "--quiet"])
    assert result.exit_code == 2
    assert "screen.json" in result.stderr


# --- shortlist --------------------------------------------------------------


def test_shortlist_orders_and_cuts(workspace):
    high = candidate_payload("a", title="Central paper")
    low = candidate_payload("b", title="Tangential paper")
    run_dir = make_run(
        workspace, [high, low], screen=screen_payload((high["cid"], 3), (low["cid"], 1))
    )

    result = runner.invoke(app, ["shortlist", "--json", "--quiet"])

    assert result.exit_code == 0, result.stderr
    payload = json.loads(result.stdout)
    assert payload["in_window"] == 1
    assert payload["screened_ge2"] == 1

    document = Shortlist.model_validate(json.loads((run_dir / "shortlist.json").read_text()))
    assert [row.title for row in document.in_window] == ["Central paper"]
    assert document.in_window[0].score == 3


def test_shortlist_exits_two_listing_the_missing_cids(workspace):
    """§8.7's whole point: a retrieved paper must never go unscreened and unnoticed."""
    scored = candidate_payload("a")
    unscored = candidate_payload("b", title="Never screened")
    make_run(workspace, [scored, unscored], screen=screen_payload((scored["cid"], 3)))

    result = runner.invoke(app, ["shortlist", "--json", "--quiet"])

    assert result.exit_code == 2
    payload = json.loads(result.stderr)
    assert payload["ok"] is False
    assert unscored["cid"] in " ".join(payload["errors"])
    assert "missing scores" in " ".join(payload["errors"])


def test_shortlist_exits_two_on_a_duplicate_score(workspace):
    candidate = candidate_payload("a")
    make_run(
        workspace,
        [candidate],
        screen=screen_payload((candidate["cid"], 3), (candidate["cid"], 2)),
    )

    result = runner.invoke(app, ["shortlist", "--quiet"])

    assert result.exit_code == 2
    assert "duplicate" in result.stderr


def test_shortlist_separates_the_two_windows(workspace):
    current = candidate_payload("a", title="Current")
    classic = candidate_payload("b", title="Classic") | {"outside_window": True}
    run_dir = make_run(
        workspace,
        [current, classic],
        screen=screen_payload((current["cid"], 3), (classic["cid"], 3)),
    )

    runner.invoke(app, ["shortlist", "--json", "--quiet"])

    document = Shortlist.model_validate(json.loads((run_dir / "shortlist.json").read_text()))
    assert [row.title for row in document.in_window] == ["Current"]
    assert [row.title for row in document.outside_window] == ["Classic"]


# --- verify -----------------------------------------------------------------


def mock_verification(
    *, crossref_title="Paper a", crossref_status=200, retracted=False, family="Authora"
):
    respx.get(url__regex=CROSSREF_PATTERN).mock(
        return_value=httpx.Response(
            crossref_status,
            json={
                "message": {
                    "DOI": "10.1000/a",
                    "title": [crossref_title],
                    "issued": {"date-parts": [[2024, 1, 1]]},
                    "author": [{"given": "Ada", "family": family, "sequence": "first"}],
                }
            },
        )
    )
    respx.get(url__regex=OPENALEX_PATTERN).mock(
        return_value=httpx.Response(
            200,
            json={
                "results": [
                    {
                        "id": "https://openalex.org/W1",
                        "title": "Paper a",
                        "publication_year": 2024,
                        "is_retracted": retracted,
                    }
                ]
            },
        )
    )


@respx.mock
def test_verify_stamps_ranked_json_and_the_manifest(workspace):
    candidate = candidate_payload("a", title="Paper a")
    run_dir = make_run(
        workspace,
        [candidate],
        screen=screen_payload((candidate["cid"], 3)),
        ranked=[ranked_entry(candidate["cid"], overall=3).model_dump(mode="json")],
    )
    mock_verification()

    result = runner.invoke(app, ["verify", "--json", "--quiet"])

    assert result.exit_code == 0, result.stderr
    payload = json.loads(result.stdout)
    assert payload["verification"]["verified"] == 1
    assert payload["unverified"] == []

    ranked = Ranked.model_validate(json.loads((run_dir / "ranked.json").read_text()))
    assert ranked.root[0].verification.verified is True
    assert [item.value for item in ranked.root[0].verification.verified_by] == [
        "crossref",
        "openalex",
    ]
    assert (run_dir / "verify.log.jsonl").exists()

    manifest = Manifest.model_validate(json.loads((run_dir / "manifest.json").read_text()))
    assert manifest.verification.verified == 1
    assert manifest.counts.verified == 1


@respx.mock
def test_verify_reports_a_title_mismatch_without_deleting_the_paper(workspace):
    candidate = candidate_payload("a", title="Paper a")
    run_dir = make_run(
        workspace,
        [candidate],
        screen=screen_payload((candidate["cid"], 3)),
        ranked=[ranked_entry(candidate["cid"]).model_dump(mode="json")],
    )
    mock_verification(crossref_title="An entirely different paper")

    result = runner.invoke(app, ["verify", "--json", "--quiet"])

    payload = json.loads(result.stdout)
    assert payload["verification"]["unverified"] == 1
    assert payload["unverified"][0]["mismatches"] == ["title"]
    ranked = Ranked.model_validate(json.loads((run_dir / "ranked.json").read_text()))
    assert ranked.root[0].verification.verified is False


@respx.mock
def test_verify_notes_crossref_shutting_us_out(workspace):
    candidate = candidate_payload("a", title="Paper a")
    run_dir = make_run(
        workspace,
        [candidate],
        screen=screen_payload((candidate["cid"], 3)),
        ranked=[ranked_entry(candidate["cid"]).model_dump(mode="json")],
    )
    respx.get(url__regex=CROSSREF_PATTERN).mock(return_value=httpx.Response(429))
    respx.get(url__regex=OPENALEX_PATTERN).mock(
        return_value=httpx.Response(
            200,
            json={"results": [{"id": "W1", "title": "Paper a", "publication_year": 2024}]},
        )
    )

    result = runner.invoke(app, ["verify", "--json", "--quiet"])

    assert result.exit_code == 0
    manifest = Manifest.model_validate(json.loads((run_dir / "manifest.json").read_text()))
    assert manifest.verification.crossref_skipped is True
    assert manifest.verification.verified == 1  # OpenAlex carried it


def test_verify_exits_two_on_a_ranked_cid_that_is_not_a_candidate(workspace):
    candidate = candidate_payload("a")
    make_run(
        workspace,
        [candidate],
        screen=screen_payload((candidate["cid"], 3)),
        ranked=[ranked_entry("deadbeef0000").model_dump(mode="json")],
    )

    result = runner.invoke(app, ["verify", "--quiet"])

    assert result.exit_code == 2
    assert "deadbeef0000" in result.stderr


# --- emit -------------------------------------------------------------------


def emit_run(workspace: Path, entries: list[dict], candidates: list[dict]) -> Path:
    return make_run(
        workspace,
        candidates,
        screen=screen_payload(*[(c["cid"], 3) for c in candidates]),
        ranked=entries,
    )


def test_emit_writes_all_three_deliverables(workspace):
    candidates = [candidate_payload(f"p{n}", title=f"Paper {n}") for n in range(3)]
    entries = [
        ranked_entry(c["cid"], overall=3, verification=verification_payload()).model_dump(
            mode="json"
        )
        for c in candidates
    ]
    run_dir = emit_run(workspace, entries, candidates)

    result = runner.invoke(app, ["emit", "--json", "--quiet"])

    assert result.exit_code == 0, result.stderr
    assert (run_dir / "evidence.json").exists()
    assert (run_dir / "evidence.md").exists()
    assert (run_dir / "evidence.bib").exists()

    evidence = Evidence.model_validate(json.loads((run_dir / "evidence.json").read_text()))
    assert len(evidence.packets) == 3
    assert [packet.rank for packet in evidence.packets] == [1, 2, 3]

    manifest = Manifest.model_validate(json.loads((run_dir / "manifest.json").read_text()))
    assert manifest.emit.emitted == 3
    assert manifest.counts.emitted == 3


def test_no_bib_skips_the_bibliography(workspace):
    candidates = [candidate_payload("a")]
    entries = [
        ranked_entry(candidates[0]["cid"], verification=verification_payload()).model_dump(
            mode="json"
        )
    ]
    run_dir = emit_run(workspace, entries, candidates)

    runner.invoke(app, ["emit", "--json", "--quiet", "--no-bib"])

    assert not (run_dir / "evidence.bib").exists()


def test_emit_exits_two_when_ranked_json_was_never_verified(workspace):
    """§14.3: emit refuses a ranked.json lacking verification."""
    candidates = [candidate_payload("a")]
    entries = [ranked_entry(candidates[0]["cid"]).model_dump(mode="json")]
    emit_run(workspace, entries, candidates)

    result = runner.invoke(app, ["emit", "--json", "--quiet"])

    assert result.exit_code == 2
    payload = json.loads(result.stderr)
    assert "research-scan verify" in " ".join(payload["errors"])


def test_emit_drops_a_paper_retracted_at_verify_and_counts_it(workspace):
    """§14.4: a retraction found only at verify never reaches evidence.json."""
    live = candidate_payload("a", title="A live paper")
    dead = candidate_payload("b", title="A retracted paper")
    entries = [
        ranked_entry(live["cid"], overall=3, verification=verification_payload()).model_dump(
            mode="json"
        ),
        ranked_entry(
            dead["cid"],
            overall=3,
            verification=verification_payload(False, ["retracted"]),
        ).model_dump(mode="json"),
    ]
    run_dir = emit_run(workspace, entries, [live, dead])

    result = runner.invoke(app, ["emit", "--json", "--quiet"])

    payload = json.loads(result.stdout)
    assert payload["emit"]["dropped_retracted"] == 1
    evidence = Evidence.model_validate(json.loads((run_dir / "evidence.json").read_text()))
    assert [p.title for p in evidence.packets] == ["A live paper"]
    assert "A retracted paper" not in (run_dir / "evidence.md").read_text()


def test_emit_marks_an_unverified_paper_in_the_markdown(workspace):
    candidates = [candidate_payload("a", title="A doubtful paper")]
    entries = [
        ranked_entry(
            candidates[0]["cid"],
            overall=3,
            verification=verification_payload(False, ["doi_unresolved"]),
        ).model_dump(mode="json")
    ]
    run_dir = emit_run(workspace, entries, candidates)

    runner.invoke(app, ["emit", "--json", "--quiet"])

    markdown = (run_dir / "evidence.md").read_text()
    assert "[UNVERIFIED — check manually]" in markdown
    assert "A doubtful paper" in markdown
    assert "doi_unresolved" in markdown


def test_emit_honours_top_and_foundational_flags(workspace):
    candidates = [candidate_payload(f"p{n}", title=f"Paper {n}") for n in range(8)]
    entries = [
        ranked_entry(c["cid"], overall=3, verification=verification_payload()).model_dump(
            mode="json"
        )
        for c in candidates
    ]
    emit_run(workspace, entries, candidates)

    result = runner.invoke(app, ["emit", "--json", "--quiet", "--top", "3", "--foundational", "0"])

    assert len(json.loads(result.stdout)["top"]) == 3


def test_emit_exits_two_on_a_ranked_cid_that_is_not_a_candidate(workspace):
    candidates = [candidate_payload("a")]
    entries = [
        ranked_entry("deadbeef0000", verification=verification_payload()).model_dump(mode="json")
    ]
    emit_run(workspace, entries, candidates)

    result = runner.invoke(app, ["emit", "--quiet"])

    assert result.exit_code == 2
    assert "deadbeef0000" in result.stderr


def test_the_module_urls_stay_where_the_tests_expect_them():
    assert "crossref.org" in crossref_module.WORKS_URL
    assert "openalex.org" in openalex_module.WORKS_URL


# --- coverage (V1.1) --------------------------------------------------------


def attributed(*rows: tuple[str, int, list[str]]) -> dict:
    return {
        "scores": [
            {"cid": cid, "score": score, "reason": "why", "criteria_hit": hits}
            for cid, score, hits in rows
        ]
    }


def test_coverage_counts_each_criterion_and_names_the_thin_ones(workspace):
    kept = candidate_payload("kept")
    other = candidate_payload("other")
    run_dir = make_run(
        workspace,
        [kept, other],
        screen=attributed((kept["cid"], 3, ["C1"]), (other["cid"], 2, ["C1"])),
    )

    result = runner.invoke(app, ["coverage", "--run", str(run_dir), "--json"])

    assert result.exit_code == 0, result.stdout + result.stderr
    payload = json.loads(result.stdout)
    assert payload["round"] == 1
    assert {c["id"]: c["hits"] for c in payload["criteria"]} == {"C1": 2, "C2": 0, "C3": 0}
    assert payload["thin"] == ["C1", "C2", "C3"]  # two hits is below the threshold of five
    assert (run_dir / "coverage.json").exists()


def test_coverage_exits_two_on_a_criterion_queries_json_does_not_define(workspace):
    kept = candidate_payload("kept")
    run_dir = make_run(workspace, [kept], screen=attributed((kept["cid"], 3, ["C9"])))

    result = runner.invoke(app, ["coverage", "--run", str(run_dir), "--json"])

    assert result.exit_code == 2
    assert "C9" in result.stdout + result.stderr


def test_coverage_keeps_the_earlier_round_when_the_gap_round_recounts(workspace):
    kept = candidate_payload("kept")
    run_dir = make_run(workspace, [kept], screen=attributed((kept["cid"], 3, ["C1"])))
    runner.invoke(app, ["coverage", "--run", str(run_dir), "--json"])

    plan = plan_payload(
        round2=[{"id": "G1", "type": "gap", "text": "thin area", "target_criterion": "C2"}]
    )
    (run_dir / "queries.json").write_text(json.dumps(plan))
    result = runner.invoke(app, ["coverage", "--run", str(run_dir), "--json"])

    assert json.loads(result.stdout)["round"] == 2
    saved = json.loads((run_dir / "coverage.json").read_text())
    assert [entry["round"] for entry in saved["rounds"]] == [1, 2]


def test_the_out_of_window_cap_is_a_total_for_the_run(workspace):
    """v0.2.1: the gap round inherits what round 1 left, not a second full allowance."""
    kept = candidate_payload("kept")
    run_dir = make_run(workspace, [kept], screen=screen_payload((kept["cid"], 3)))
    assert expand.outside_window_spent(run_dir, 1) == 0  # round 1 replaces its own admissions
    assert expand.outside_window_spent(run_dir, 2) == 0  # nothing expanded yet

    (run_dir / "expanded.json").write_text(
        json.dumps(
            {
                "seeds": [kept["cid"]],
                "added": [],
                "added_outside_window": ["a" * 12, "b" * 12, "c" * 12],
                "batches": [],
            }
        )
    )

    assert expand.outside_window_spent(run_dir, 2) == 3
    assert expand.outside_window_spent(run_dir, 1) == 0
