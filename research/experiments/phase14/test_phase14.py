"""Phase-1.4 — everything that can be checked without spending a token.

Three groups:

  variants        the four rubric texts are what they claim to be — C0 byte-identical to the
                  shipped file, each patch applied exactly once, the factors composing, and no
                  golden named.
  contract        the `priority_rank` rules fire on each of the four violations and stay quiet on
                  a clean chunk; reconciliation still behaves as Phase-1.2C measured it.
  selection       the priority key degenerates to the shipped key when nothing is ranked, and the
                  shipped-key replay reproduces the recorded `evidence.json` of all 30 Phase-1.2B
                  runs — the same control Phase-1.2C validated, re-run through this slice's code.
"""

from __future__ import annotations

import sys
from pathlib import Path

import pytest

HERE = Path(__file__).resolve().parent
sys.path.insert(0, str(HERE))
sys.path.insert(0, str(HERE.parent / "phase12-selection"))
sys.path.insert(0, str(HERE.parent / "phase12-selection" / "phase12c"))

import contract  # noqa: E402
import contract14  # noqa: E402
import schema14  # noqa: E402
import select14  # noqa: E402
import variants  # noqa: E402

from research_scan import select  # noqa: E402
from research_scan.schema import CandidatesFile, Ranked  # noqa: E402

CRITERIA = [{"id": "C1", "name": "n", "text": "t"}, {"id": "C2", "name": "n", "text": "t"}]


def entry(cid: str, overall: int, rank: int | None = None) -> dict:
    row = {
        "cid": cid,
        "criteria": {"C1": overall, "C2": 1},
        "overall": overall,
        "evidence_level": "experimental",
        "relation": "closely-related",
        "flags": {"review": False, "contradicts": False, "methods_paper": False},
        "key_finding": "k", "methodology": "abstract-only", "why_it_matters": "w",
        "limitations": ["l"], "relevance_reason": "r",
    }
    if rank is not None:
        row["priority_rank"] = rank
    return row


def batch(cids: list[str]) -> dict:
    return {"batch": "t/c1", "items": [{"cid": c} for c in cids], "sub_criteria": CRITERIA}


# --------------------------------------------------------------------- variants


def test_c0_is_the_shipped_rubric_byte_for_byte():
    assert variants.variant("C0") == variants.SHIPPED.read_text(encoding="utf-8")


def test_every_patch_applies_exactly_once():
    base = variants.shipped_text()
    for find in (variants.S1_FIND, variants.S2_FIND, variants.C2_FIND, variants.C1_ANCHOR):
        assert base.count(find) == 1


def test_s_removes_the_relation_quota_and_adds_the_anchors():
    s = variants.variant("S")
    assert variants.S2_FIND not in s
    assert "Any of the first four earns" not in s
    assert "absolute anchors" in s
    assert "priority_rank" in s
    # S must NOT touch the off-domain cap — that is C's site.
    assert variants.C2_FIND in s


def test_c_adds_the_value_section_and_extends_the_cap_exception_only():
    c = variants.variant("C")
    assert "What counts as decision-changing value" in c
    assert "The same exception is available" in c
    # C must NOT touch the overall scale or the relation quota — those are S's sites.
    assert variants.S1_FIND in c
    assert variants.S2_FIND in c


def test_factors_compose_without_overlapping():
    sc = variants.variant("SC")
    for marker in ("absolute anchors", "priority_rank", "What counts as decision-changing value",
                   "The same exception is available"):
        assert marker in sc
    assert variants.S1_FIND not in sc and variants.S2_FIND not in sc


def test_sc_is_exactly_s_then_c_and_c_then_s():
    base = variants.shipped_text()
    assert variants.apply_c(variants.apply_s(base)) == variants.variant("SC")


def test_no_golden_is_named_in_any_variant():
    assert variants.check_contamination() == {}


def test_the_contamination_check_has_teeth(monkeypatch):
    real = variants.variant
    monkeypatch.setattr(variants, "variant", lambda cell: real(cell) + "\nBerk et al is a 3.\n")
    assert "berk" in variants.check_contamination(("S",))["S"]


def test_only_s_cells_put_priority_rank_on_the_wire():
    assert [variants.uses_priority_rank(c) for c in variants.CELLS] == [False, True, False, True]


def test_wire_schema_gains_exactly_one_property_in_s_cells():
    off = schema14.entry_schema(["C1", "C2"], priority=False)
    on = schema14.entry_schema(["C1", "C2"], priority=True)
    assert set(on["properties"]) - set(off["properties"]) == {"priority_rank"}
    assert set(on["required"]) - set(off["required"]) == {"priority_rank"}
    assert off == schema14.frozen_rerank().entry_schema(["C1", "C2"])


# --------------------------------------------------------------------- contract


def test_clean_chunk_passes():
    rows = [entry("a" * 12, 3, 1), entry("b" * 12, 3, 2), entry("c" * 12, 2, 0)]
    contract14.check_batch("t/c1", rows)


def test_missing_rank_on_a_three_is_a_violation():
    rows = [entry("a" * 12, 3, 1), entry("b" * 12, 3, 0)]
    with pytest.raises(contract14.PriorityContractViolation) as exc:
        contract14.check_batch("t/c1", rows)
    assert "carry no rank" in str(exc.value)
    assert exc.value.EXIT_CODE == 2


def test_a_rank_below_the_top_tier_is_a_violation():
    rows = [entry("a" * 12, 3, 1), entry("b" * 12, 2, 2)]
    with pytest.raises(contract14.PriorityContractViolation, match="carry a rank"):
        contract14.check_batch("t/c1", rows)


def test_duplicate_ranks_are_a_violation():
    rows = [entry("a" * 12, 3, 1), entry("b" * 12, 3, 1)]
    with pytest.raises(contract14.PriorityContractViolation, match="not unique"):
        contract14.check_batch("t/c1", rows)


def test_a_gap_in_the_ranks_is_a_violation():
    rows = [entry("a" * 12, 3, 1), entry("b" * 12, 3, 3)]
    with pytest.raises(contract14.PriorityContractViolation, match="not contiguous"):
        contract14.check_batch("t/c1", rows)


def test_ranks_need_not_start_at_the_first_row():
    """Order in the array is not order in the ranking. Only the rank values are contracted."""
    contract14.check_batch("t/c1", [entry("a" * 12, 3, 2), entry("b" * 12, 3, 1)])


def test_a_chunk_with_no_threes_is_clean():
    contract14.check_batch("t/c1", [entry("a" * 12, 2, 0), entry("b" * 12, 1, 0)])


def test_a_non_integer_rank_costs_its_own_row_not_the_chunk():
    row = entry("a" * 12, 3)
    row["priority_rank"] = "1"
    clean, why = contract14.validate_entry_with_priority(row, {"C1", "C2"})
    assert clean is None and "not an integer" in why


def test_an_out_of_range_rank_costs_its_own_row():
    clean, why = contract14.validate_entry_with_priority(
        entry("a" * 12, 3, schema14.MAX_RANK + 1), {"C1", "C2"})
    assert clean is None and "out of range" in why


def test_reconciliation_still_discards_a_ghost_row_without_a_retry():
    """Phase-1.2C's measured defect, with `priority_rank` on the wire."""
    cids = ["a" * 12, "b" * 12]
    payload = {"ranked": [entry(cids[0], 3, 1), entry("dead" + "b" * 8, 3, 2),
                          entry(cids[1], 2, 0)]}
    rec = contract.reconcile(batch(cids), payload, rows_key="ranked", score_field="overall",
                             validate_row=contract14.validate_entry_with_priority)
    assert rec.verdict == contract.COMPLETE
    assert [r["cid"] for r in rec.scores] == cids
    assert any(p["event"] == "unknown_cid_discarded" for p in rec.provenance)


def test_strip_priority_leaves_a_shipped_schema_valid_entry():
    rows = [entry("a" * 12, 3, 1), entry("b" * 12, 2, 0)]
    entries, priority = contract14.strip_priority(rows)
    assert all("priority_rank" not in e for e in entries)
    assert priority == {"a" * 12: 1, "b" * 12: 0}   # the sidecar records the 0s too
    Ranked.model_validate(entries)      # extra="forbid" would raise if a rank leaked through


# -------------------------------------------------------------------- selection


def test_priority_key_degenerates_to_the_shipped_key_when_nothing_is_ranked():
    runs = _recorded_runs()
    pairs = _pairs(runs[0])
    key = select14.make_priority_key({})
    a = sorted(pairs, key=key, reverse=True)
    b = sorted(pairs, key=select14.shipped_key, reverse=True)
    assert [e.cid for _, e in a] == [e.cid for _, e in b]


def test_priority_key_leads_the_top_tier_and_leaves_the_rest_alone():
    pairs = _pairs(_recorded_runs()[0])
    threes = [e.cid for _, e in pairs if e.overall == 3]
    assert len(threes) >= 3, "fixture must contain a saturated top tier"
    # Rank the LAST three first; it must come out on top of the tier and nowhere else.
    priority = {cid: i + 1 for i, cid in enumerate(reversed(threes))}
    ordered = sorted(pairs, key=select14.make_priority_key(priority), reverse=True)
    top = [e.cid for _, e in ordered if e.overall == 3]
    assert top == list(reversed(threes))
    below = [e.cid for _, e in ordered if e.overall != 3]
    shipped_below = [e.cid for _, e in sorted(pairs, key=select14.shipped_key, reverse=True)
                     if e.overall != 3]
    assert below == shipped_below


def _recorded_runs():
    """The 28 Phase-1.2B rerank runs, as `common12c` joins them."""
    import types
    sys.modules.setdefault("anthropic", types.ModuleType("anthropic"))
    import common12c
    return common12c.runs()


def _pairs(run):
    ranked = Ranked.model_validate(run.load("ranked.json"))
    candidates = CandidatesFile.model_validate(run.load("candidates.json"))
    by_cid = {c.cid: c for c in candidates.candidates}
    return [(by_cid[e.cid], e) for e in ranked.root]


def test_shipped_key_replay_reproduces_every_recorded_emit():
    """The control validation, re-run through this slice's own selection code."""
    runs = _recorded_runs()
    assert len(runs) == 30, "the Phase-1.2B corpus is 30 recorded rerank runs"
    for run in runs:
        manifest = run.load("manifest.json")
        result = select14.selection(
            _pairs(run), select14.shipped_key,
            top=manifest["defaults"]["top"], foundational=manifest["defaults"]["foundational"])
        recorded = [p["cid"] for p in run.load("evidence.json")["packets"]]
        assert result["emitted"] == recorded, run.key


def test_swapping_the_key_is_restored_afterwards():
    before = select.order_key
    with select14.ordering_key(lambda pair: (0,)):
        assert select.order_key is not before
    assert select.order_key is before


# --------------------------------------------------------------- the deviation bound


def test_the_deviation_bound_needs_every_breach_lifted_to_clear_the_clause():
    """`no_stable_golden_lost` fails if ANY stable golden breaches, so the best case for the
    missing replicate clears it only when NO breach survives. The first draft of this aggregation
    asked whether *some* breach could be lifted, which would have reported S's verdict as
    deviation-sensitive when it is not."""
    import deviation14

    one_survives = {
        "non_inferiority": {"attainable": False},
        "materially_better": {"attainable": False},
        "no_stable_golden_lost": {
            "PaSa": {"breach_stands": True}, "LitSearch": {"breach_stands": False}},
        "substantially_less_saturated": {"already_failed_independently_of_this_topic": True},
    }
    assert deviation14._flippable(one_survives) == []

    none_survive = {
        **one_survives,
        "no_stable_golden_lost": {
            "PaSa": {"breach_stands": False}, "LitSearch": {"breach_stands": False}},
    }
    assert deviation14._flippable(none_survive) == ["no_stable_golden_lost"]


def test_the_recorded_deviation_cannot_flip_any_clause():
    """The ruling's robustness to the one protocol deviation, over the recorded numbers."""
    import json

    import deviation14

    out = json.loads((HERE / "results" / "deviation_s_r4.json").read_text())
    assert out["deviation"]["cell"] == "llm-lit-search/S"
    assert out["bound"]["non_inferiority"]["needs_missing_replicate_to_score"] > \
        out["bound"]["reachable_ceiling"]
    assert out["clauses_the_deviation_could_flip"] == []
    assert out["verdict_robust_to_deviation"] is True
    assert deviation14._flippable(out["bound"]) == []
