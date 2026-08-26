"""Contract tests for the reconciling screening driver, against the recorded x02 responses.

Fixtures come from the Phase-1.1 run, not from imagination:

* `fixtures/x02-batch.json`      — `runs/p11-t2/screen-batches/x02.json`, the 25-item batch.
* `fixtures/x02-response-salvage.json` — the salvage call's 27 rows: the 25 recorded judgements
  (`screen-batches/p11-t2/x02.json`) plus the two rows `stages/salvage-llm-lit-search-x02.json`
  records as dropped. Byte-recoverable.
* `fixtures/x02-attempts-recorded.json` — the six frozen-policy attempts, each rebuilt to its
  *recorded error signature* (`missing=[] extra=['<mangled cid>']`) over the same 25 rows. The
  signature is recorded; the six raw bodies were not kept, and this file says so per attempt.

The mutation cases (conflicting duplicate, missing cid, bad field) are derived from the same
recorded rows so that every test exercises real judgements.
"""

from __future__ import annotations

import copy
import json
from pathlib import Path

import pytest

import contract

FX = Path(__file__).parent / "fixtures"
BATCH = json.loads((FX / "x02-batch.json").read_text())
SALVAGE = json.loads((FX / "x02-response-salvage.json").read_text())
RECORDED = json.loads((FX / "x02-attempts-recorded.json").read_text())
WANT = [item["cid"] for item in BATCH["items"]]


def events(rec_or_outcome, name):
    return [e for e in rec_or_outcome.provenance if e["event"] == name]


# --------------------------------------------------------------- the recorded failure itself

def test_clean_response_is_unchanged():
    """A response with exactly the 25 wanted rows reconciles to those 25 rows, in batch order."""
    clean = {"scores": SALVAGE["scores"][:25]}
    rec = contract.reconcile(BATCH, clean)
    assert rec.verdict == contract.COMPLETE
    assert [r["cid"] for r in rec.scores] == WANT
    assert rec.provenance == []


@pytest.mark.parametrize("attempt", RECORDED, ids=[f"attempt{a['attempt']}" for a in RECORDED])
def test_every_recorded_x02_attempt_now_lands(attempt):
    """All six calls the frozen policy threw away carried 25 correct rows. Each now survives."""
    rec = contract.reconcile(BATCH, attempt["payload"])
    assert rec.verdict == contract.COMPLETE
    assert [r["cid"] for r in rec.scores] == WANT
    dropped = events(rec, "unknown_cid_discarded")
    assert len(dropped) == 1
    assert dropped[0]["cid"] == attempt["recorded_error"].split("'")[1]
    assert dropped[0]["well_formed"] is False


def test_salvage_response_needs_no_salvage_script():
    """The 27-row salvage body: 25 kept, 2 unknown rows discarded and named, no retry."""
    rec = contract.reconcile(BATCH, SALVAGE)
    assert rec.verdict == contract.COMPLETE
    assert len(rec.scores) == 25
    assert sorted(e["cid"] for e in events(rec, "unknown_cid_discarded")) == [
        "2ad9d99f0b79b", "4a1808a68e2a2"
    ]


def test_matches_the_recorded_salvage_output_exactly():
    """Reconciliation reproduces what `salvage.py` wrote, so nothing measured in 1.1 moves."""
    recorded = json.loads(
        (Path(__file__).parents[1] / "phase11-golden/screen-batches/p11-t2/x02.json").read_text()
    )["scores"]
    assert contract.reconcile(BATCH, SALVAGE).scores == recorded


# --------------------------------------------------------------- the four contract cases

def test_unknown_cid_is_discarded_and_logged_never_retried():
    payload = {"scores": SALVAGE["scores"][:25] + [
        {"cid": "ffffffffffff", "score": 3, "reason": "invented", "criteria_hit": ["C1"]}]}
    calls = []
    out = contract.screen_batch(BATCH, lambda b: (calls.append(b), payload)[1])
    assert out.ok and len(out.scores) == 25
    assert len(calls) == 1, "an unknown row must not buy another call"
    assert events(out, "unknown_cid_discarded")[0]["cid"] == "ffffffffffff"


def test_repeated_unknown_cid_is_discarded_the_same_way():
    ghost = {"cid": "2ad9d99f0b79dup", "score": 0, "reason": "duplicate placeholder",
             "criteria_hit": []}
    payload = {"scores": SALVAGE["scores"][:25] + [ghost, dict(ghost), dict(ghost, score=2)]}
    rec = contract.reconcile(BATCH, payload)
    assert rec.verdict == contract.COMPLETE
    assert len(rec.scores) == 25
    assert len(events(rec, "unknown_cid_discarded")) == 3
    assert events(rec, "duplicate_conflicting") == [], "unknown cids never make a batch invalid"


def test_duplicate_expected_cid_identical_score_keeps_one():
    row = next(r for r in SALVAGE["scores"][:25] if r["cid"] == "2ad9d99f0b79")
    payload = {"scores": SALVAGE["scores"][:25] + [copy.deepcopy(row)]}
    rec = contract.reconcile(BATCH, payload)
    assert rec.verdict == contract.COMPLETE
    assert [r["cid"] for r in rec.scores] == WANT
    collapsed = events(rec, "duplicate_identical_collapsed")
    assert collapsed[0]["cid"] == "2ad9d99f0b79" and collapsed[0]["copies"] == 2


def test_duplicate_expected_cid_conflicting_score_invalidates_the_batch():
    row = next(r for r in SALVAGE["scores"][:25] if r["cid"] == "2ad9d99f0b79")
    payload = {"scores": SALVAGE["scores"][:25] + [dict(row, score=0, criteria_hit=[])]}
    rec = contract.reconcile(BATCH, payload)
    assert rec.verdict == contract.INVALID
    assert rec.scores == []
    assert events(rec, "duplicate_conflicting")[0]["cid"] == "2ad9d99f0b79"


def test_conflicting_duplicate_retries_then_lands():
    bad_row = next(r for r in SALVAGE["scores"][:25] if r["cid"] == "2ad9d99f0b79")
    bad = {"scores": SALVAGE["scores"][:25] + [dict(bad_row, score=0, criteria_hit=[])]}
    seq = [bad, SALVAGE]
    out = contract.screen_batch(BATCH, lambda b: seq.pop(0))
    assert out.ok and out.attempts == 2 and len(out.scores) == 25


def test_conflicting_duplicate_forever_fails_after_two_retries():
    bad_row = next(r for r in SALVAGE["scores"][:25] if r["cid"] == "2ad9d99f0b79")
    bad = {"scores": SALVAGE["scores"][:25] + [dict(bad_row, score=0, criteria_hit=[])]}
    calls = []
    out = contract.screen_batch(BATCH, lambda b: (calls.append(b), bad)[1])
    assert len(calls) == 3, "one call plus at most two retries — never a loop"
    assert out.ok is False and out.attempts == 3
    assert "conflicting duplicate scores" in out.reason
    assert out.missing == WANT


def test_missing_cids_are_retried_as_a_sub_batch():
    partial = {"scores": SALVAGE["scores"][:23]}
    asked = []

    def call(b):
        asked.append([i["cid"] for i in b["items"]])
        return partial if len(asked) == 1 else {"scores": SALVAGE["scores"][23:25]}

    out = contract.screen_batch(BATCH, call)
    assert out.ok and out.attempts == 2
    assert asked[1] == WANT[23:25], "only the owed records are re-asked"
    assert [r["cid"] for r in out.scores] == WANT


def test_missing_cids_retry_the_whole_batch_when_sub_batch_is_unsupported():
    asked = []

    def call(b):
        asked.append(len(b["items"]))
        return {"scores": SALVAGE["scores"][:23]} if len(asked) == 1 else SALVAGE

    out = contract.screen_batch(BATCH, call, supports_sub_batch=False)
    assert out.ok and asked == [25, 25]


def test_persistently_missing_cids_fail_the_batch_but_keep_the_good_rows():
    partial = {"scores": SALVAGE["scores"][:23]}
    calls = []
    out = contract.screen_batch(BATCH, lambda b: (calls.append(b), partial)[1])
    assert len(calls) == 3
    assert out.ok is False
    assert len(out.scores) == 23, "25 correct rows are never destroyed by 2 absent ones"
    assert out.missing == WANT[23:]
    assert events(out, "batch_failed")[0]["kept"] == 23


# --------------------------------------------------------------- field contract, per row

@pytest.mark.parametrize("mutate,why", [
    ({"score": 7}, "out of range"),
    ({"score": "3"}, "not an integer"),
    ({"reason": ""}, "missing reason"),
    ({"criteria_hit": ["C9"]}, "unknown criteria ids"),
])
def test_a_bad_row_costs_its_own_cid_not_the_batch(mutate, why):
    rows = copy.deepcopy(SALVAGE["scores"][:25])
    rows[6].update(mutate)
    rec = contract.reconcile(BATCH, {"scores": rows})
    assert rec.verdict == contract.INCOMPLETE
    assert rec.missing == [WANT[6]]
    assert len(rec.scores) == 24
    assert why in events(rec, "row_rejected")[0]["why"]


def test_score_two_with_empty_criteria_hit_is_still_rejected():
    rows = copy.deepcopy(SALVAGE["scores"][:25])
    rows[6]["criteria_hit"] = []
    rec = contract.reconcile(BATCH, {"scores": rows})
    assert rec.missing == [WANT[6]]


def test_no_scores_array_is_a_retryable_invalid_batch():
    rec = contract.reconcile(BATCH, {"error": "overloaded"})
    assert rec.verdict == contract.INVALID
    assert rec.missing == WANT


def test_call_exception_counts_as_an_attempt_and_cannot_loop():
    calls = []

    def call(b):
        calls.append(b)
        raise RuntimeError("connection reset")

    out = contract.screen_batch(BATCH, call)
    assert len(calls) == 3 and out.ok is False
    assert "connection reset" in out.reason
