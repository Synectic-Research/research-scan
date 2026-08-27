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


# --- the terminal path: what a run that cannot finish leaves behind ----------


def install_fake_anthropic(monkeypatch, responder):
    """`cli.main` imports `anthropic` at the point of first spend; hand it a fake there."""
    import sys
    import types

    from conftest import FakeClient

    module = types.ModuleType("anthropic")
    module.Anthropic = lambda **kwargs: FakeClient(responder)
    monkeypatch.setitem(sys.modules, "anthropic", module)
    monkeypatch.setenv("ANTHROPIC_API_KEY", "sk-ant-test-not-a-real-key")


def rubric_file(tmp_path):
    path = tmp_path / "screen-rubric.md"
    path.write_text("# rubric\nscore 0-3\n")
    return path


def engine_dir(run):
    return next((run / "engine").iterdir())


def test_exhaustion_exits_non_zero_and_never_presents_a_complete_screen(tmp_path, monkeypatch):
    """A batch that cannot be satisfied leaves a named shortfall, not a quietly complete file."""
    run = make_run(tmp_path, batches={"01": ["aaaaaaaaaaaa", "bbbbbbbbbbbb"]})
    # Every attempt answers for one cid only; the other is never satisfied.
    install_fake_anthropic(monkeypatch, lambda request, n: {"scores": [row("aaaaaaaaaaaa")]})

    code = cli.main(["--run", str(run), "--rubric", str(rubric_file(tmp_path))])

    assert code == 1, "a short run must not exit 0"
    summary = json.loads((engine_dir(run) / "summary.json").read_text())
    assert summary["unsatisfied_cids"] == ["bbbbbbbbbbbb"]
    assert summary["batches_failed"] == ["01"]

    record = json.loads((engine_dir(run) / "provenance.json").read_text())
    assert record["completion_status"] == "incomplete"
    assert record["unresolved_cids"] == ["bbbbbbbbbbbb"]
    assert record["attempt_count"] == 3, "one call plus two retries, then it stops"
    assert record["retry_summary"]["batches_failed"] == ["01"]
    assert record["input_record_count"] == 2
    assert record["accepted_record_count"] == 1

    assert not (run / "screen.json").exists(), "a short run may not write the finished-screen name"
    written = json.loads((run / cli.PARTIAL_NAME).read_text())["scores"]
    assert [entry["cid"] for entry in written] == ["aaaaaaaaaaaa"], "the shortfall is visible"


def test_a_complete_run_records_itself_complete_and_exits_zero(tmp_path, monkeypatch):
    run = make_run(tmp_path, batches={"01": ["aaaaaaaaaaaa", "bbbbbbbbbbbb"]})
    install_fake_anthropic(
        monkeypatch,
        lambda request, n: {"scores": [row("aaaaaaaaaaaa"), row("bbbbbbbbbbbb")]},
    )

    code = cli.main(["--run", str(run), "--rubric", str(rubric_file(tmp_path))])

    assert code == 0
    record = json.loads((engine_dir(run) / "provenance.json").read_text())
    assert record["completion_status"] == "complete"
    assert record["unresolved_cids"] == []
    assert record["attempt_count"] == 1
    assert record["batch_size"] == 2
    assert record["completed_at"] is not None
    assert record["usage"]["calls"] == 1


def test_only_rows_the_acceptance_chain_returned_can_reach_screen_json(tmp_path, monkeypatch):
    """`accept.attach` decides the artifact; nothing writes a row that did not come through it."""
    run = make_run(tmp_path, batches={"01": ["aaaaaaaaaaaa", "bbbbbbbbbbbb"]})
    install_fake_anthropic(
        monkeypatch,
        lambda request, n: {
            "scores": [
                row("aaaaaaaaaaaa"),
                # A cid the run never retrieved, and a row that fails the field contract.
                row("dddddddddddd"),
                dict(row("bbbbbbbbbbbb"), score=9),
            ]
        },
    )

    code = cli.main(["--run", str(run), "--rubric", str(rubric_file(tmp_path))])

    assert code == 1
    accepted = json.loads((engine_dir(run) / "accepted.json").read_text())
    written = json.loads((run / cli.PARTIAL_NAME).read_text())["scores"]

    assert [entry["cid"] for entry in accepted["scores"]] == ["aaaaaaaaaaaa"]
    assert [entry["cid"] for entry in written] == ["aaaaaaaaaaaa"]
    assert written == accepted["scores"], "the file carries the accepted rows and nothing else"
    assert "dddddddddddd" not in json.dumps(written), "an invented cid never reaches the pipeline"


# --- the partial/promote contract -------------------------------------------
#
# `research-scan shortlist` is the stage that refuses an incomplete screen (exit 2, every missing
# cid named). The two stages that read a screen *before* it — `expand` and `coverage` — validate
# only that the file names known sub-criteria, so a shortened `screen.json` passes both at exit 0
# and quietly seeds the citation walk from fewer papers. Hence: only a run that satisfied every
# batch is allowed to write that name.


def test_a_short_run_leaves_an_existing_screen_json_exactly_as_it_found_it(tmp_path, monkeypatch):
    """The screen a previous pass earned outlives a later pass that ends short."""
    run = make_run(
        tmp_path,
        batches={"01": ["aaaaaaaaaaaa"], "02": ["bbbbbbbbbbbb", "cccccccccccc"]},
        scored=[row("aaaaaaaaaaaa")],
    )
    before = (run / "screen.json").read_text()
    # Batch 01 is already covered and is not re-bought; batch 02 is never satisfied.
    install_fake_anthropic(monkeypatch, lambda request, n: {"scores": [row("bbbbbbbbbbbb")]})

    assert cli.main(["--run", str(run), "--rubric", str(rubric_file(tmp_path))]) == 1

    assert (run / "screen.json").read_text() == before, "pipeline state is not touched by a failure"
    partial = json.loads((run / cli.PARTIAL_NAME).read_text())["scores"]
    assert [entry["cid"] for entry in partial] == ["aaaaaaaaaaaa", "bbbbbbbbbbbb"]


def test_a_retry_reads_the_partial_back_and_does_not_re_buy_what_it_paid_for(tmp_path, monkeypatch):
    """The partial file is resume state. Losing it would mean paying twice for the same batch."""
    run = make_run(
        tmp_path, batches={"01": ["aaaaaaaaaaaa"], "02": ["bbbbbbbbbbbb", "cccccccccccc"]}
    )
    # Batch 01 is satisfiable; batch 02 never is. The run ends short, holding 01's row.
    install_fake_anthropic(
        monkeypatch,
        lambda request, n: {"scores": [row(cid) for cid in ("aaaaaaaaaaaa", "bbbbbbbbbbbb")]},
    )
    assert cli.main(["--run", str(run), "--rubric", str(rubric_file(tmp_path))]) == 1
    assert [e["cid"] for e in json.loads((run / cli.PARTIAL_NAME).read_text())["scores"]] == [
        "aaaaaaaaaaaa",
        "bbbbbbbbbbbb",
    ]

    asked: list[str] = []

    def responder(request, n):
        asked.append(request["messages"][0]["content"])
        return {"scores": [row(cid) for cid in ("bbbbbbbbbbbb", "cccccccccccc")]}

    install_fake_anthropic(monkeypatch, responder)
    assert cli.main(["--run", str(run), "--rubric", str(rubric_file(tmp_path))]) == 0

    assert len(asked) == 1, "only the outstanding batch is re-asked"
    assert "aaaaaaaaaaaa" not in asked[0], "a cid already paid for is not sent again"


def test_a_run_that_finishes_promotes_the_partial_and_removes_it(tmp_path, monkeypatch):
    run = make_run(tmp_path, batches={"01": ["aaaaaaaaaaaa", "bbbbbbbbbbbb"]})
    install_fake_anthropic(monkeypatch, lambda request, n: {"scores": [row("aaaaaaaaaaaa")]})
    assert cli.main(["--run", str(run), "--rubric", str(rubric_file(tmp_path))]) == 1
    assert (run / cli.PARTIAL_NAME).exists()

    install_fake_anthropic(
        monkeypatch,
        lambda request, n: {"scores": [row("aaaaaaaaaaaa"), row("bbbbbbbbbbbb")]},
    )
    assert cli.main(["--run", str(run), "--rubric", str(rubric_file(tmp_path))]) == 0

    assert not (run / cli.PARTIAL_NAME).exists(), "the partial name does not outlive its run"
    written = json.loads((run / "screen.json").read_text())["scores"]
    assert [entry["cid"] for entry in written] == ["aaaaaaaaaaaa", "bbbbbbbbbbbb"]
