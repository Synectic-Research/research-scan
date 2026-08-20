"""`eval` end to end, the arXiv-DOI verification fix, and stage timestamps (spec §13, §10.5)."""

from __future__ import annotations

import json
from datetime import date
from pathlib import Path

import httpx
import pytest
import respx
import yaml
from typer.testing import CliRunner

from conftest import make_candidate, plan_payload, ranked_entry, verification_payload
from research_scan import http, run
from research_scan import verify as verify_module
from research_scan.cli import app
from research_scan.dedup import with_cid
from research_scan.schema import (
    CandidatesFile,
    Defaults,
    EvidencePacket,
    Manifest,
    Mismatch,
    RunInfo,
    VerifiedBy,
)

FROZEN_TODAY = date(2026, 8, 19)
runner = CliRunner()

CROSSREF_PATTERN = r"https://api\.crossref\.org/works/.*"
OPENALEX_PATTERN = r"https://api\.openalex\.org/works.*"

# The real record from the s3-e2e run: OpenAlex resolves it, Crossref 404s on the DataCite DOI.
DARK_PATTERNS_DOI = "10.48550/arxiv.2310.00340"
DARK_PATTERNS_TITLE = "Regulating Dark Patterns"


@pytest.fixture(autouse=True)
def frozen_and_fast(monkeypatch):
    monkeypatch.setattr(run, "today", lambda: FROZEN_TODAY)
    monkeypatch.setattr(http.RateLimiter, "acquire", lambda self, host: 0.0)
    monkeypatch.setattr(http.time, "sleep", lambda _seconds: None)


@pytest.fixture
def workspace(fake_settings, tmp_path) -> Path:
    return tmp_path


# --- fix (b): arXiv DOIs verify without Crossref -----------------------------


def dark_patterns_candidate(*, arxiv: str | None):
    """The two variants that actually exist on disk: s1-smoke carried the id, s3-e2e did not."""
    return with_cid(
        make_candidate(
            title=DARK_PATTERNS_TITLE,
            doi=DARK_PATTERNS_DOI,
            arxiv=arxiv,
            openalex="W4387323449",
            year=2023,
            authors=("Martin Brenncke",),
        )
    )


class RecordingCrossref:
    def __init__(self):
        self.calls: list[str] = []

    def lookup(self, doi, *, cache=None):
        self.calls.append(doi)
        return None  # Crossref 404s on every 10.48550 DOI


class FakeOpenAlex:
    def __init__(self, record=None):
        self._record = record

    def lookup(self, *, doi=None, openalex_id=None, cache=None):
        return self._record


def verify_one(candidate, crossref, openalex):
    return verify_module.run_verify(
        [ranked_entry(candidate.cid)],
        {candidate.cid: candidate},
        crossref,
        openalex,
        options=verify_module.VerifyOptions(),
        today=FROZEN_TODAY,
    )


def openalex_record():
    return {
        "id": "https://openalex.org/W4387323449",
        "title": DARK_PATTERNS_TITLE,
        "publication_year": 2023,
        "is_retracted": False,
        "authorships": [{"author": {"display_name": "Martin Brenncke"}}],
    }


def test_crossref_is_never_asked_about_an_arxiv_doi():
    """It 404s on every one, and reading that as doi_unresolved marked good papers unverified."""
    crossref = RecordingCrossref()
    candidate = dark_patterns_candidate(arxiv="2310.00340")

    result = verify_one(candidate, crossref, FakeOpenAlex(openalex_record()))

    assert crossref.calls == []
    verification = result.entries[0].verification
    assert Mismatch.doi_unresolved not in verification.mismatches
    assert verification.verified is True


def test_an_independently_sourced_arxiv_id_corroborates():
    candidate = dark_patterns_candidate(arxiv="2310.00340")
    result = verify_one(candidate, RecordingCrossref(), FakeOpenAlex(openalex_record()))

    verification = result.entries[0].verification
    assert verification.verified_by == [VerifiedBy.openalex, VerifiedBy.arxiv]


def test_without_a_second_source_openalex_stands_alone():
    """The s3-e2e copy has no arXiv id: nothing to cross-check, so we claim nothing extra."""
    candidate = dark_patterns_candidate(arxiv=None)
    result = verify_one(candidate, RecordingCrossref(), FakeOpenAlex(openalex_record()))

    verification = result.entries[0].verification
    assert verification.verified is True
    assert verification.verified_by == [VerifiedBy.openalex]


def test_disagreeing_arxiv_ids_do_not_corroborate(caplog):
    """A mismatch between the record's id and the DOI's is the OpenAlex mis-merge signal."""
    candidate = dark_patterns_candidate(arxiv="2310.99999")
    with caplog.at_level("WARNING"):
        result = verify_one(candidate, RecordingCrossref(), FakeOpenAlex(openalex_record()))

    verification = result.entries[0].verification
    assert verification.verified_by == [VerifiedBy.openalex]
    assert "disagreement" in caplog.text


def test_a_normal_doi_still_goes_to_crossref():
    crossref = RecordingCrossref()
    candidate = with_cid(make_candidate(doi="10.1257/aer.20210881", year=2025))

    verify_one(candidate, crossref, FakeOpenAlex(None))

    assert crossref.calls == ["10.1257/aer.20210881"]


@respx.mock
def test_the_regression_through_the_verify_command(workspace):
    """End to end: Crossref would 404, and the paper still verifies."""
    candidate = dark_patterns_candidate(arxiv="2310.00340")
    run_dir = make_run(
        workspace,
        [candidate.model_dump(mode="json")],
        ranked=[ranked_entry(candidate.cid).model_dump(mode="json")],
    )
    crossref = respx.get(url__regex=CROSSREF_PATTERN).mock(return_value=httpx.Response(404))
    respx.get(url__regex=OPENALEX_PATTERN).mock(
        return_value=httpx.Response(200, json={"results": [openalex_record()]})
    )

    result = runner.invoke(app, ["verify", "--json", "--quiet", "--run", str(run_dir)])

    assert result.exit_code == 0
    payload = json.loads(result.stdout)
    assert payload["verification"]["verified"] == 1
    assert payload["unverified"] == []
    assert crossref.call_count == 0


# --- run scaffolding shared with the eval tests ------------------------------


def make_run(workspace: Path, candidates: list[dict], **files) -> Path:
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
                "timestamps": {"init.started_at": "2026-08-19T10:00:00+00:00"},
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


def evidence_for(run_dir: Path, candidates: list, entries: list) -> None:
    info = json.loads((run_dir / "candidates.json").read_text())["run"]
    packets = [
        EvidencePacket(
            **(candidate.model_dump() | entry.model_dump()),
            rank=rank,
            selection_reason="score",
        ).model_dump(mode="json")
        for rank, (candidate, entry) in enumerate(zip(candidates, entries, strict=True), start=1)
    ]
    (run_dir / "evidence.json").write_text(
        json.dumps({"run": info, "packets": packets, "alternates": []})
    )


# --- fix (a): timestamps through the commands --------------------------------


def test_emit_records_wall_clock_from_init(workspace, monkeypatch):
    candidate = with_cid(make_candidate(doi="10.1000/a"))
    entry = ranked_entry(candidate.cid, overall=3, verification=verification_payload())
    run_dir = make_run(
        workspace,
        [candidate.model_dump(mode="json")],
        ranked=[entry.model_dump(mode="json")],
    )

    result = runner.invoke(app, ["emit", "--json", "--quiet", "--run", str(run_dir)])

    assert result.exit_code == 0, result.stderr
    manifest = Manifest.model_validate(json.loads((run_dir / "manifest.json").read_text()))
    assert "emit.started_at" in manifest.timestamps
    assert "emit.finished_at" in manifest.timestamps
    assert manifest.timestamps["init.started_at"] == "2026-08-19T10:00:00+00:00"
    assert manifest.counts.wall_clock_s is not None
    assert json.loads(result.stdout)["counts"]["wall_clock_s"] == manifest.counts.wall_clock_s


# --- eval --------------------------------------------------------------------


def golden_dir(workspace: Path, **topics) -> Path:
    directory = workspace / "golden"
    directory.mkdir()
    for name, payload in topics.items():
        (directory / f"{name}.yaml").write_text(yaml.safe_dump(payload))
    return directory


def topic_file(*expected: dict) -> dict:
    return {
        "topic": "t",
        "status": "draft",
        "brief": "A brief.",
        "domain": "behavioral",
        "expected": list(expected),
    }


def run_with_evidence(workspace: Path, dois: list[str]) -> Path:
    candidates = [with_cid(make_candidate(title=f"P {d}", doi=d)) for d in dois]
    entries = [
        ranked_entry(c.cid, overall=3, verification=verification_payload()) for c in candidates
    ]
    run_dir = make_run(
        workspace,
        [c.model_dump(mode="json") for c in candidates],
        ranked=[e.model_dump(mode="json") for e in entries],
    )
    evidence_for(run_dir, candidates, entries)
    return run_dir


def test_eval_scores_a_run_and_writes_a_result(workspace):
    run_dir = run_with_evidence(workspace, ["10.1000/a"])
    golden = golden_dir(
        workspace,
        t=topic_file(
            {"doi": "10.1000/a", "why": "the central one"},
            {"doi": "10.1000/missing", "why": "should have been found"},
        ),
    )

    result = runner.invoke(
        app,
        [
            "eval",
            "--topic",
            "t",
            "--run",
            str(run_dir),
            "--golden",
            str(golden),
            "--json",
            "--quiet",
        ],
    )

    assert result.exit_code == 0, result.stderr
    payload = json.loads(result.stdout)
    assert payload["expected"] == 2
    assert payload["found_at_10"] == 1
    assert payload["recall_10"] == 0.5
    assert payload["misses"][0]["doi"] == "10.1000/missing"
    assert payload["golden_status"] == "draft"
    assert Path(payload["result_path"]).exists()


def test_eval_merges_a_judge_file(workspace):
    run_dir = run_with_evidence(workspace, ["10.1000/a"])
    golden = golden_dir(workspace, t=topic_file({"doi": "10.1000/a", "why": "central"}))
    judge = workspace / "judge.json"
    judge.write_text(
        json.dumps(
            {
                "judge_model": "claude-fable-5",
                "scores": [
                    {"rank": 1, "score": 3, "reason": "central"},
                    {"rank": 2, "score": 1, "reason": "tangential"},
                ],
            }
        )
    )

    result = runner.invoke(
        app,
        [
            "eval",
            "--topic",
            "t",
            "--run",
            str(run_dir),
            "--golden",
            str(golden),
            "--judge",
            str(judge),
            "--json",
            "--quiet",
        ],
    )

    payload = json.loads(result.stdout)
    assert payload["judged"]["precision_ge2"] == 0.5
    # No foundational slot in this run, so the two shares agree — but the field must be computed,
    # not left null: the CLI has the evidence and therefore owes the number.
    assert payload["judged"]["precision_ge2_in_window"] == 0.5
    assert payload["judged"]["foundational"] == []
    assert payload["judged"]["per_rank"][0]["reason"] == "central"


def test_eval_warns_that_a_draft_topic_is_provisional(workspace):
    run_dir = run_with_evidence(workspace, ["10.1000/a"])
    golden = golden_dir(workspace, t=topic_file({"doi": "10.1000/a", "why": "central"}))

    result = runner.invoke(
        app, ["eval", "--topic", "t", "--run", str(run_dir), "--golden", str(golden)]
    )

    assert "draft" in result.stderr
    assert "provisional" in result.stderr


def test_eval_exits_two_on_an_unknown_topic(workspace):
    run_dir = run_with_evidence(workspace, ["10.1000/a"])
    golden = golden_dir(workspace, t=topic_file({"doi": "10.1000/a", "why": "central"}))

    result = runner.invoke(
        app, ["eval", "--topic", "nope", "--run", str(run_dir), "--golden", str(golden), "--quiet"]
    )

    assert result.exit_code == 2
    assert "nope" in result.stderr


def test_eval_exits_two_on_a_malformed_golden_file(workspace):
    run_dir = run_with_evidence(workspace, ["10.1000/a"])
    golden = golden_dir(workspace, t={"topic": "t", "brief": "b", "expected": []})

    result = runner.invoke(
        app,
        [
            "eval",
            "--topic",
            "t",
            "--run",
            str(run_dir),
            "--golden",
            str(golden),
            "--json",
            "--quiet",
        ],
    )

    assert result.exit_code == 2
    assert json.loads(result.stderr)["ok"] is False


def test_eval_exits_two_without_an_emitted_run(workspace):
    candidate = with_cid(make_candidate(doi="10.1000/a"))
    run_dir = make_run(workspace, [candidate.model_dump(mode="json")])
    golden = golden_dir(workspace, t=topic_file({"doi": "10.1000/a", "why": "central"}))

    result = runner.invoke(
        app, ["eval", "--topic", "t", "--run", str(run_dir), "--golden", str(golden), "--quiet"]
    )

    assert result.exit_code == 2
    assert "evidence.json" in result.stderr


def test_eval_stage_candidates_scores_retrieval_without_the_agent_stages(tmp_path, monkeypatch):
    """`--stage candidates` must run on a run dir holding only candidates.json.

    That is the point of the stage: a retrieval change can be re-measured without paying for
    screening, reranking and emit again.
    """
    monkeypatch.chdir(tmp_path)
    run_dir = tmp_path / "run"
    run_dir.mkdir()
    candidate = with_cid(make_candidate(doi="10.1038/s41586-025-10072-4"))
    run.write_model(
        run_dir / "candidates.json",
        CandidatesFile(
            run=RunInfo(
                run_dir=str(run_dir),
                slug="s",
                date="2026-08-19",
                brief_path="b.md",
                defaults=Defaults(),
            ),
            candidates=[candidate],
        ),
    )
    golden = tmp_path / "golden"
    golden.mkdir()
    (golden / "t.yaml").write_text(
        "topic: t\n"
        "status: ratified\n"
        "brief: b\n"
        "expected:\n"
        "  - doi: 10.48550/arXiv.2411.14199\n"
        '    arxiv: "2411.14199"\n'
        "    aliases: [10.1038/s41586-025-10072-4]\n"
        "    why: the published version must count\n",
        encoding="utf-8",
    )

    result = runner.invoke(
        app,
        [
            "eval",
            "--topic",
            "t",
            "--run",
            str(run_dir),
            "--golden",
            str(golden),
            "--stage",
            "candidates",
            "--json",
            "--quiet",
        ],
    )

    assert result.exit_code == 0, result.output
    payload = json.loads(result.stdout)
    assert payload["stage"] == "candidates"
    assert payload["candidates"]["found"] == 1
    assert payload["candidates"]["papers"][0]["matched_by"] == "alias"
    assert payload["candidates"]["screened"] is False


def test_eval_rejects_an_unknown_stage(tmp_path, monkeypatch):
    monkeypatch.chdir(tmp_path)
    result = runner.invoke(app, ["eval", "--topic", "t", "--stage", "ranked", "--quiet"])
    assert result.exit_code == 2
    assert "--stage must be" in result.output + result.stderr
