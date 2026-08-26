"""Phase-1.2C — the four tie-break ladders.

Every ladder is **lexicographic only**. No numeric composite is introduced and no weight is
invented: each tier is either a recorded grade, an order-free count of recorded grades, a
recorded joinable feature, or a boolean lifted verbatim from a predicate the shipped slot
rules already apply. Keys are consumed by `sorted(..., reverse=True)`, so an ASC tier is
expressed as a negated integer and every tuple position is type-consistent across rows.

  K0  control — `research_scan.select.order_key`, imported not copied. Its terminal tie-break
      is Python's stable sort over `ranked.json` order, i.e. the reranker's own emitted order.
      That is the shipped behaviour and K0 must reproduce every recorded top-10 cid-for-cid.

  K1  overall DESC, then the per-criterion grade histogram (count of 3s DESC, 2s DESC, 1s DESC)
      — order-free across criteria, and a strict refinement of the criteria *sum* K0 uses:
      (3,0,0,0,0) and (0,1,1,1,0) both sum to 3 and the histogram separates them.
      Terminates in T1 rank ASC.

  K2  K1 with screen score DESC and `criteria_supported` DESC inserted before T1 rank.
      Both are 1.1/1.2A recorded features; `criteria_supported` is a lexicographic tie-break
      feature and is never summed or weighted (Phase-1.2B doctrine).

  K3  K2 with relation-aware precedence inserted immediately after `overall` — the one place
      it can bite, since the instability lives inside the saturated `overall == 3` band. Both
      booleans are the shipped slot rules' own predicates, gated exactly as `_guarantee` gates
      them (`select.py:283-291`):
        * `flags.review and _earns_the_slot("review", entry)`  — the review floor, `select.py:326`
        * `flags.contradicts and _is_counter_evidence(entry)`  — the reserve, `select.py:240`
      Their relative order is `_apply_guarantees`'s own iteration order (review, then
      contradicting; `select.py:226-232`). No new slot, no new count, no new number.
"""
from __future__ import annotations

from research_scan import select
from research_scan.schema import Candidate, RankedEntry

Pair = tuple[Candidate, RankedEntry]


def _histogram(entry: RankedEntry) -> tuple[int, int, int]:
    """Counts of grade 3, 2, 1 among the per-criterion subscores. Order-free across criteria."""
    grades = list(entry.criteria.values())
    return (grades.count(3), grades.count(2), grades.count(1))


#: The shipped key, bound once at import so the replay's swap of `select.order_key` cannot
#: shadow the control with itself.
SHIPPED_ORDER_KEY = select.order_key


def make_keys(features: dict[str, dict], t1_rank: dict[str, int]):
    """Bind the joinable 1.1/1.2A features and return the four key functions."""

    def k0(pair: Pair) -> tuple:
        return SHIPPED_ORDER_KEY(pair)

    def k1(pair: Pair) -> tuple:
        _, entry = pair
        n3, n2, n1 = _histogram(entry)
        return (entry.overall, n3, n2, n1, -t1_rank[entry.cid])

    def k2(pair: Pair) -> tuple:
        _, entry = pair
        n3, n2, n1 = _histogram(entry)
        f = features[entry.cid]
        return (entry.overall, n3, n2, n1,
                f["screen_score"] or 0, f["criteria_supported"] or 0,
                -t1_rank[entry.cid])

    def k3(pair: Pair) -> tuple:
        _, entry = pair
        n3, n2, n1 = _histogram(entry)
        f = features[entry.cid]
        review = bool(entry.flags.review) and select._earns_the_slot("review", entry)
        counter = bool(entry.flags.contradicts) and select._is_counter_evidence(entry)
        return (entry.overall, int(review), int(counter), n3, n2, n1,
                f["screen_score"] or 0, f["criteria_supported"] or 0,
                -t1_rank[entry.cid])

    return {"K0": k0, "K1": k1, "K2": k2, "K3": k3}


#: Human-readable tier names, for the tie-depth table. The trailing entry is the terminal
#: tie-break; for K0 that is not a key component at all but the stable sort's input order.
TIERS = {
    "K0": ("overall", "criteria_sum", "origin_count", "date", "ranked.json order (stable sort)"),
    "K1": ("overall", "n3", "n2", "n1", "T1 rank"),
    "K2": ("overall", "n3", "n2", "n1", "screen", "criteria_supported", "T1 rank"),
    "K3": ("overall", "review_slot", "counter_slot", "n3", "n2", "n1",
           "screen", "criteria_supported", "T1 rank"),
}
