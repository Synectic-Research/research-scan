"""The run-directory contract: what is re-bought, what is written, and what is refused."""

from __future__ import annotations

import json

import pytest
from stateless_driver import cli

from conftest import row

BRIEF = "Purpose: research\n\nHow defaults shape enrolment.\n"


def make_run(tmp_path, *, batches: dict[str, list[str]], scored: list[dict] | None = None):
    run = tmp_path / "run"
    (run / "screen-batches").mkdir(parents=True)
    (run / "brief.md").write_text(BRIEF)
    cids = []
    for bid, items in batches.items():
        cids.extend(items)
        (run / "screen-batches" / f"{bid}.json").write_text(
            json.dumps(
                {
                    "batch": bid,
                    "sub_criteria": [{"id": "C1", "name": "n", "text": "t"}],
                    "items": [{"cid": cid, "title": cid} for cid in items],
                }
            )
        )
    (run / "candidates.json").write_text(
        json.dumps({"candidates": [{"cid": cid} for cid in cids]})
    )
    if scored is not None:
        (run / "screen.json").write_text(json.dumps({"scores": scored}))
    return run


def test_a_batch_already_covered_by_screen_json_is_not_re_bought(tmp_path):
    run = make_run(
        tmp_path,
        batches={"01": ["aaaaaaaaaaaa"], "02": ["bbbbbbbbbbbb"]},
        scored=[row("aaaaaaaaaaaa")],
    )
    batches = cli.read_batches(run, "*.json")

    assert list(cli.outstanding(batches, {"aaaaaaaaaaaa"})) == ["02"]
    assert list(cli.outstanding(batches, set())) == ["01", "02"]


def test_the_merge_orders_by_candidates_json_and_keeps_earlier_scores(tmp_path):
    run = make_run(tmp_path, batches={"01": ["cccccccccccc", "aaaaaaaaaaaa", "bbbbbbbbbbbb"]})

    merged = cli.merge(run, [row("aaaaaaaaaaaa", score=2)], [row("bbbbbbbbbbbb")])

    assert [entry["cid"] for entry in merged] == ["aaaaaaaaaaaa", "bbbbbbbbbbbb"]
    assert merged[0]["score"] == 2


def test_a_score_for_a_cid_the_run_never_retrieved_is_refused(tmp_path):
    """Last guard before pipeline state: an engine cannot add a paper to a run."""
    run = make_run(tmp_path, batches={"01": ["aaaaaaaaaaaa"]})

    with pytest.raises(SystemExit, match="not in candidates.json"):
        cli.merge(run, [], [row("dddddddddddd")])


def test_a_dry_run_writes_provenance_and_makes_no_call(tmp_path, monkeypatch):
    run = make_run(tmp_path, batches={"01": ["aaaaaaaaaaaa"]})
    rubric = tmp_path / "screen-rubric.md"
    rubric.write_text("# rubric\n")
    monkeypatch.delenv("ANTHROPIC_API_KEY", raising=False)

    code = cli.main(["--run", str(run), "--rubric", str(rubric), "--dry-run"])

    assert code == 0
    written = sorted(path.name for path in (run / "engine").rglob("*.json"))
    assert written == ["plan.json", "provenance.json"]
    record = json.loads(next((run / "engine").rglob("provenance.json")).read_text())
    assert record["engine_id"] == "anthropic-stateless-reference"
    assert not (run / "screen.json").exists()


def test_a_brief_without_a_purpose_line_is_refused_before_any_call(tmp_path):
    run = make_run(tmp_path, batches={"01": ["aaaaaaaaaaaa"]})
    (run / "brief.md").write_text("How defaults shape enrolment.\n")
    rubric = tmp_path / "screen-rubric.md"
    rubric.write_text("# rubric\n")

    with pytest.raises(ValueError, match="Purpose:"):
        cli.main(["--run", str(run), "--rubric", str(rubric), "--dry-run"])
