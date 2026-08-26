"""Phase-1.2C — the rerank sub-batch re-ask path, tested against the recorded 1.2B failure.

Run: `.venv/bin/python -m pytest research/experiments/phase12-selection/phase12c -q`
No model is called. The fixtures are reconstructed from committed artefacts (`fixtures12c`).
"""
from __future__ import annotations

import sys
import types
from pathlib import Path

import pytest

HERE = Path(__file__).resolve().parent
sys.path.insert(0, str(HERE))
sys.path.insert(0, str(HERE.parent))

# `phase11-golden/rerank.py` imports `anthropic` at module scope; this suite loads it for its
# pure functions and never calls the API. Same stub the Phase-1.2B offline scripts use.
sys.modules.setdefault("anthropic", types.ModuleType("anthropic"))

import contract  # noqa: E402
import fixtures12c as F  # noqa: E402
import rerank_contract as RC  # noqa: E402


# --------------------------------------------------------------------------------------
# The recorded failure
# --------------------------------------------------------------------------------------

def test_fixture_matches_the_recorded_chunk():
    cids = F.chunk_cids()
    assert len(cids) == F.RERANK_CHUNK
    assert set(F.RECORDED_MISSING) <= set(cids)
    # The ghost is a mangled variant of a real cid in the same chunk — the x02 signature.
    assert F.RECORDED_GHOST.split("_")[0] in cids
    assert F.RECORDED_GHOST not in cids


def test_x02_response_keeps_the_nine_and_owes_exactly_the_four():
    rec = RC.reconcile(F.batch(), F.x02_payload())
    assert rec.verdict == contract.INCOMPLETE
    assert [r["cid"] for r in rec.scores] == [
        c for c in F.chunk_cids() if c not in F.RECORDED_MISSING]
    assert rec.missing == [c for c in F.chunk_cids() if c in F.RECORDED_MISSING]
    assert len(rec.scores) == 9 and len(rec.missing) == 4


def test_the_ghost_is_discarded_and_logged_not_retried():
    rec = RC.reconcile(F.batch(), F.x02_payload())
    ghosts = [p for p in rec.provenance if p["event"] == "unknown_cid_discarded"]
    assert [g["cid"] for g in ghosts] == [F.RECORDED_GHOST]
    assert ghosts[0]["well_formed"] is False       # 12 hex chars + "_placeholder"
    assert F.RECORDED_GHOST not in rec.missing


def test_sub_batch_re_ask_recovers_the_four_in_one_extra_call():
    asks: list[list[str]] = []

    def call(batch):
        asks.append([i["cid"] for i in batch["items"]])
        if len(asks) == 1:
            return F.x02_payload()
        return F.clean_payload([i["cid"] for i in batch["items"]])

    out = RC.rerank_chunk(F.batch(), call)
    assert out.ok
    assert out.attempts == 2
    assert asks[0] == F.chunk_cids()
    # The second ask carries only what is owed — not the nine already banked.
    assert asks[1] == [c for c in F.chunk_cids() if c in F.RECORDED_MISSING]
    assert [r["cid"] for r in out.scores] == F.chunk_cids()
    assert [p["mode"] for p in out.provenance if p["event"] == "retry"] == ["sub_batch"]


def test_frozen_driver_would_have_re_asked_all_thirteen():
    """The counterfactual the record shows: `attempts: 2` over the whole chunk."""
    asks: list[list[str]] = []

    def call(batch):
        asks.append([i["cid"] for i in batch["items"]])
        return F.x02_payload() if len(asks) == 1 else F.clean_payload()

    out = RC.rerank_chunk(F.batch(), call, supports_sub_batch=False)
    assert out.ok and asks[1] == F.chunk_cids()
    assert len(asks[1]) == 13 and len(F.RECORDED_MISSING) == 4


# --------------------------------------------------------------------------------------
# The rerank field contract — `rerank.py`'s own checks, per row
# --------------------------------------------------------------------------------------

def test_clean_response_is_complete_and_ordered():
    rec = RC.reconcile(F.batch(), F.clean_payload())
    assert rec.verdict == contract.COMPLETE
    assert rec.missing == []
    assert [r["cid"] for r in rec.scores] == F.chunk_cids()


def test_response_order_does_not_matter():
    payload = F.clean_payload()
    payload["ranked"].reverse()
    rec = RC.reconcile(F.batch(), payload)
    assert rec.verdict == contract.COMPLETE
    assert [r["cid"] for r in rec.scores] == F.chunk_cids()


def test_empty_limitations_costs_its_own_cid_not_the_chunk():
    """`rerank.py:174-176` raised on this and threw away the other twelve rows."""
    payload = F.clean_payload()
    payload["ranked"][3]["limitations"] = []
    rec = RC.reconcile(F.batch(), payload)
    assert rec.verdict == contract.INCOMPLETE
    assert rec.missing == [F.chunk_cids()[3]]
    assert len(rec.scores) == 12
    assert any(p["event"] == "row_rejected" and p["why"] == "empty limitations"
               for p in rec.provenance)


@pytest.mark.parametrize("field,value,why", [
    ("overall", 4, "out of range"),
    ("overall", "3", "out of range"),
    ("evidence_level", "anecdote", "not in the enum"),
    ("relation", "related", "not in the enum"),
    ("key_finding", "", "missing key_finding"),
    ("methodology", None, "missing methodology"),
    ("why_it_matters", "", "missing why_it_matters"),
    ("relevance_reason", "", "missing relevance_reason"),
    ("limitations", ["ok", ""], "empty limitations"),
    ("flags", {"review": True}, "flags missing a boolean"),
])
def test_bad_field_rejects_one_row(field, value, why):
    payload = F.clean_payload()
    payload["ranked"][0][field] = value
    rec = RC.reconcile(F.batch(), payload)
    assert rec.missing == [F.chunk_cids()[0]]
    assert len(rec.scores) == 12
    assert any(why in p.get("why", "") for p in rec.provenance if p["event"] == "row_rejected")


def test_criteria_must_be_complete_and_in_range():
    ids = F.criteria_ids()
    payload = F.clean_payload()
    payload["ranked"][0]["criteria"].pop(ids[-1])
    payload["ranked"][1]["criteria"][ids[0]] = 5
    payload["ranked"][2]["criteria"]["C99"] = 2
    rec = RC.reconcile(F.batch(), payload)
    assert rec.missing == F.chunk_cids()[:3]
    whys = [p["why"] for p in rec.provenance if p["event"] == "row_rejected"]
    assert f"criteria missing ['{ids[-1]}']" in whys
    assert any("out of range" in w for w in whys)
    assert any("unknown criteria ids ['C99']" in w for w in whys)


# --------------------------------------------------------------------------------------
# Duplicates — `overall`, not `score`, is the rerank stage's discriminator
# --------------------------------------------------------------------------------------

def test_identical_duplicate_is_collapsed_not_retried():
    payload = F.clean_payload()
    payload["ranked"].append(dict(payload["ranked"][0]))
    rec = RC.reconcile(F.batch(), payload)
    assert rec.verdict == contract.COMPLETE
    assert [r["cid"] for r in rec.scores] == F.chunk_cids()
    assert any(p["event"] == "duplicate_identical_collapsed" for p in rec.provenance)


def test_duplicate_with_a_different_overall_invalidates_the_response():
    payload = F.clean_payload()
    dup = dict(payload["ranked"][0])
    dup["overall"] = 3
    payload["ranked"].append(dup)
    rec = RC.reconcile(F.batch(), payload)
    assert rec.verdict == contract.INVALID
    assert rec.missing == F.chunk_cids()
    assert any(p["event"] == "duplicate_conflicting" for p in rec.provenance)


# --------------------------------------------------------------------------------------
# Bounds — a rerank chunk can never loop, and a failure keeps what it earned
# --------------------------------------------------------------------------------------

def test_retries_are_bounded_and_partial_work_survives():
    calls = {"n": 0}

    def call(batch):
        calls["n"] += 1
        return F.x02_payload() if calls["n"] == 1 else {"ranked": []}

    out = RC.rerank_chunk(F.batch(), call)
    assert not out.ok
    assert calls["n"] == contract.MAX_RETRIES + 1
    assert len(out.scores) == 9
    # `missing` keeps the batch's own order, not sorted order.
    assert out.missing == [c for c in F.chunk_cids() if c in F.RECORDED_MISSING]
    assert any(p["event"] == "batch_failed" for p in out.provenance)


def test_a_transport_exception_is_recorded_and_bounded():
    calls = {"n": 0}

    def call(batch):
        calls["n"] += 1
        raise TimeoutError("stream timed out")

    out = RC.rerank_chunk(F.batch(), call)
    assert not out.ok and calls["n"] == contract.MAX_RETRIES + 1
    assert "TimeoutError" in out.reason
    assert out.scores == [] and out.missing == F.chunk_cids()


def test_a_non_object_payload_is_data_not_a_crash():
    rec = RC.reconcile(F.batch(), ["not", "an", "object"])
    assert rec.verdict == contract.INVALID
    assert rec.reason == "no ranked array"
    assert rec.missing == F.chunk_cids()


# --------------------------------------------------------------------------------------
# The driver wiring itself
# --------------------------------------------------------------------------------------

def test_driver_narrows_the_user_message_to_the_sub_batch():
    import rerank_driver as D

    items = [{"cid": c, "title": f"t{c}"} for c in F.chunk_cids()]
    whole = D.user_message(items)
    narrowed = D.user_message([i for i in items if i["cid"] in F.RECORDED_MISSING])
    assert "these 13 shortlisted records" in whole
    assert "these 4 shortlisted records" in narrowed
    for cid in F.RECORDED_MISSING:
        assert cid in narrowed
    assert F.chunk_cids()[0] not in narrowed


def test_driver_batch_carries_the_frozen_record_payload():
    import rerank_driver as D

    RR = D.frozen_rerank()
    rows = [{"cid": c, "title": f"t{c}", "score": 3, "outside_window": False}
            for c in F.chunk_cids()]
    batch = D.make_batch("tag", rows, F.sub_criteria())
    assert [i["cid"] for i in batch["items"]] == F.chunk_cids()
    assert batch["items"][0] == RR.record_payload(rows[0])
    assert contract.sub_batch(batch, F.RECORDED_MISSING)["items"] == [
        i for i in batch["items"] if i["cid"] in F.RECORDED_MISSING]


def test_screening_shape_is_untouched_by_the_generalisation():
    """The 1.2A default path must still be the 1.2A default path."""
    batch = {"batch": "b", "items": [{"cid": "a" * 12}, {"cid": "b" * 12}],
             "sub_criteria": [{"id": "C1"}]}
    payload = {"scores": [
        {"cid": "a" * 12, "score": 3, "reason": "r", "criteria_hit": ["C1"]},
        {"cid": "b" * 12, "score": 1, "reason": "r", "criteria_hit": []},
    ]}
    rec = contract.reconcile(batch, payload)
    assert rec.verdict == contract.COMPLETE and len(rec.scores) == 2
