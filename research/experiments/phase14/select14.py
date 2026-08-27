"""Phase-1.4 — the selection ordering key each cell's emitted list is read from.

The slot rules are not re-implemented anywhere in this slice. `research_scan.select.select` is
called unchanged and only `select.order_key` is swapped, exactly as Phase-1.2C did — `select`,
`presentation_order` and `_lowest_displaceable` all reach the ordering through that one module-level
name, so swapping it is the whole of "the slot rules replayed unchanged, only the ordering varies".

Two keys:

  `shipped`   `research_scan.select.order_key`, imported not copied. Used by the C0 and C cells.
              Phase-1.2C validated that replaying it reproduces the CLI's own `evidence.json`
              top-10 cid-for-cid in 30/30 recorded runs; this slice re-validates it per run, since
              both non-S cells also run `emit` and the two must agree.

  `priority`  the S cells. `(overall, -priority_rank, <the shipped key's remaining tiers>)`.
              Above the top tier nothing changes: `overall` still leads. Inside `overall == 3` the
              model's own order leads. Below it, `-priority_rank` is 0 on every row and the shipped
              key applies unchanged, tier for tier.

MERGE RULE, pre-registered before any call was issued. `RERANK_CHUNK` is 13 and R40 is four chunks,
so each chunk returns its own 1..N over its own 3s and the four orders are not globally comparable.
They are merged by **interleaving on rank**: every chunk's rank-1 comes before every chunk's rank-2,
and rows sharing a rank fall through to the shipped key's own tiers. This introduces no number, no
weight and no composite — it is one recorded field inserted as one lexicographic tier, which is the
Phase-1.2B/1.2C doctrine. The alternative (concatenating the chunks) would make a rank mean
something different depending on which chunk a paper landed in, and chunk membership is an artefact
of the frozen cut, not a judgement.
"""

from __future__ import annotations

import contextlib

from research_scan import select
from research_scan.schema import Candidate, RankedEntry

Pair = tuple[Candidate, RankedEntry]

#: Bound once at import, so a swap of `select.order_key` cannot shadow the control with itself.
SHIPPED_ORDER_KEY = select.order_key

TOP_TIER = 3


@contextlib.contextmanager
def ordering_key(fn):
    original = select.order_key
    select.order_key = fn
    try:
        yield
    finally:
        select.order_key = original


def shipped_key(pair: Pair) -> tuple:
    return SHIPPED_ORDER_KEY(pair)


def make_priority_key(priority: dict[str, int]):
    """`priority` is cid -> rank, as `priority.json` records it. Missing or 0 means no rank."""

    def key(pair: Pair) -> tuple:
        _, entry = pair
        rank = priority.get(entry.cid, 0) if entry.overall == TOP_TIER else 0
        return (entry.overall, -rank) + tuple(SHIPPED_ORDER_KEY(pair)[1:])

    return key


def key_for(cell: str, priority: dict[str, int]):
    """The key this cell's reported result is selected under."""
    from variants import uses_priority_rank

    return make_priority_key(priority) if uses_priority_rank(cell) else shipped_key


def selection(pairs: list[Pair], key_fn, *, top: int, foundational: int) -> dict:
    """`select.select` under `key_fn`, reported as the fields the analysis reads."""
    with ordering_key(key_fn):
        result = select.select(
            pairs, top=top, foundational=foundational, contradicting=select.CONTRADICTING_SLOTS
        )
        ordered = sorted(pairs, key=key_fn, reverse=True)
    return {
        "emitted": [p.cid for p in result.packets],
        "reasons": [p.selection_reason.value for p in result.packets],
        "alternates": [p.cid for p in result.alternates],
        "merit_order": [e.cid for _, e in ordered],
        "in_window_merit": [e.cid for c, e in ordered if not c.outside_window],
    }
