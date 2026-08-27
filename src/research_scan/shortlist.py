# SPDX-License-Identifier: Apache-2.0
"""Coverage validation and the ordered cut handed to the rerank step (spec §8.7, §9.6).

This stage exists to make one failure impossible: a paper that was retrieved, never screened, and
so quietly never considered. Every cid in `candidates.json` must carry exactly one score. Anything
else exits 2 with the list, because the agent can fix that and only the agent can.
"""

from __future__ import annotations

import functools
import logging
import re
from collections.abc import Collection, Iterable, Sequence
from dataclasses import dataclass, field
from datetime import date

from research_scan.schema import Candidate, ScoredCandidate, ScreenFile, Shortlist

log = logging.getLogger(__name__)

DEFAULT_MAX_IN_WINDOW = 40

#: Raised from the spec's 5 in S4.5: on the ratified golden set, the 5-slot cap discarded
#: screened-3 classics (Save More Tomorrow, Chetty 2014) before the reranker ever saw them —
#: the single largest source of recall@25 misses. Sized for how much canon a mature literature
#: carries, not for emit's 2 foundational slots.
DEFAULT_MAX_OUTSIDE_WINDOW = 12

#: Below this, a candidate is tangential or off-topic and does not reach the reranker (§8.7).
SHORTLIST_SCORE_THRESHOLD = 2


@dataclass
class CoverageReport:
    """Which cids the screening pass missed, double-scored, or invented."""

    missing: list[str] = field(default_factory=list)
    duplicate: list[str] = field(default_factory=list)
    unknown: list[str] = field(default_factory=list)

    @property
    def ok(self) -> bool:
        return not (self.missing or self.duplicate or self.unknown)

    def lines(self) -> list[str]:
        report = []
        if self.missing:
            report.append(f"missing scores for {len(self.missing)} cid(s): {_sample(self.missing)}")
        if self.duplicate:
            report.append(
                f"duplicate scores for {len(self.duplicate)} cid(s): {_sample(self.duplicate)}"
            )
        if self.unknown:
            report.append(
                f"{len(self.unknown)} scored cid(s) not in candidates.json: {_sample(self.unknown)}"
            )
        return report


def _sample(cids: list[str], limit: int = 10) -> str:
    shown = ", ".join(cids[:limit])
    return shown + (f", … (+{len(cids) - limit} more)" if len(cids) > limit else "")


def validate_coverage(candidates: list[Candidate], screen: ScreenFile) -> CoverageReport:
    """Exactly one score per candidate, and no score for anything else (§8.7)."""
    counts: dict[str, int] = {}
    for entry in screen.scores:
        counts[entry.cid] = counts.get(entry.cid, 0) + 1

    candidate_cids = [candidate.cid for candidate in candidates]
    known = set(candidate_cids)

    return CoverageReport(
        missing=[cid for cid in candidate_cids if cid not in counts],
        duplicate=sorted(cid for cid, count in counts.items() if count > 1),
        unknown=sorted(cid for cid in counts if cid not in known),
    )


#: A candidate no source ranked (expansion-only, or an origin list a source left empty) sorts
#: behind every ranked one rather than ahead of it. Phase-1.2A's sweep used the same sentinel.
NO_RETRIEVAL_RANK = 10**6

#: What an unknown publication date sorts as: last, under a DESC date tier. Lower than every
#: real `YYYY-MM-DD`, so it needs no special case in the comparator.
NO_DATE = "0000-00-00"

_ISO_DATE = re.compile(r"^\d{4}-\d{2}-\d{2}$")


def order_date(publication_date: str | None) -> str:
    """The date tier's domain: a real `YYYY-MM-DD`, or `NO_DATE` for missing and malformed.

    `publication_date` is free text at the schema — sources report partial dates (`2024`,
    `2024-03`) and the field is metadata everywhere else, so tightening it there would reject
    records the pipeline is meant to keep. The ordering needs a total domain instead: anything
    that is not a real calendar date sorts with the unknowns, behind every dated row, rather
    than being compared as a raw string (where `"2024-13-01"` or `"n.d."` outranks `"2025-01-01"`).

    Resolved here, in the key, so the comparator itself stays plain tuple comparison.
    """
    if not publication_date or not _ISO_DATE.match(publication_date):
        return NO_DATE
    try:
        date.fromisoformat(publication_date)
    except ValueError:
        return NO_DATE
    return publication_date


@functools.total_ordering
class _Descending:
    """Reverses one field's order so a DESC tier can sit inside an ascending key.

    `publication_date` is a string, so it cannot be negated the way the numeric tiers are, and a
    whole-key `reverse=True` would flip `cid` too — which is exactly the tier that has to run ASC.
    """

    __slots__ = ("value",)

    def __init__(self, value: str) -> None:
        self.value = value

    def __eq__(self, other: object) -> bool:
        return isinstance(other, _Descending) and self.value == other.value

    def __lt__(self, other: _Descending) -> bool:
        return other.value < self.value

    def __repr__(self) -> str:  # pragma: no cover - diagnostics only
        return f"_Descending({self.value!r})"


def criteria_supported(criteria_hit: Sequence[str], known: Collection[str] | None = None) -> int:
    """How many distinct sub-criteria a paper was screened as satisfying.

    The domain is narrow on purpose. An id counts when it is a non-empty string that `known`
    declares; ids are compared in their canonical form — the schema strips surrounding
    whitespace, and matching is exact against `queries.json` — and de-duplicated after that
    normalisation, because a repeated id is one criterion. Empty, unknown and misspelled ids are
    ignored rather than counted, so a typo cannot buy a place in the order; booleans and other
    non-strings never reach here, being rejected at the schema. Without `known` (the caller has
    no `queries.json`) every distinct non-empty id counts.

    The no-op is artifact-level and is decided before sorting, in `build`, which resolves this
    count for every row up front: when no row in a `screen.json` carries a valid hit the tier is
    uniformly 0 across that artifact and the remaining tiers decide, which is what a pre-v0.2
    file gets. In a mixed artifact a row with no valid hits scores 0 and sorts behind its
    attributed peers — it is not exempted. This is never a pairwise "skip this tier" comparator:
    the tier is one resolved number per row, not a decision taken between two rows.

    criteria_supported is a lexicographic tie-break feature, not a relevance score — never
    optimize it numerically.
    """
    if known is None:
        return len({criterion for criterion in criteria_hit if criterion})
    return len({criterion for criterion in criteria_hit if criterion and criterion in known})


def best_retrieval_rank(candidate: Candidate) -> int:
    """The best position any source gave this paper, over every origin it earned.

    Every rank reaching here is already a valid one: `Origin.rank` is a strict, non-negative int
    at the schema, so booleans, floats, strings and negatives exit 2 long before the order runs.
    A candidate no source ranked — no origins at all — takes `NO_RETRIEVAL_RANK` and sorts behind
    every ranked row; an artifact where nothing is ranked gives every row the same sentinel, so
    the tier no-ops naturally. `origin_count` is a separate tier and is unaffected either way.
    """
    return min((origin.rank for origin in candidate.origins), default=NO_RETRIEVAL_RANK)


def order_key(scored: ScoredCandidate, supported: int = 0) -> tuple:
    """The shortlist's lexicographic total order — ascending, so `sorted(..., key=…)` is enough.

    score DESC, criteria_supported DESC, origin_count DESC, best_retrieval_rank ASC, date DESC,
    cid ASC (§8.7, Phase-1.2A). Date sat third until v0.6.0, where — inside the large equal-score,
    equal-origin bands a real pool actually produces — it was the only discriminator left, so the
    cut ran as a recency filter and dropped central papers for being older than their band
    (`552f09c462dce07a7c20fa3f30e85c3264f42346:research/experiments/phase12-selection/results/
    report_tail.md` §4). The two tiers ahead of it are relevance evidence the screen and the
    retrieval already produced; `cid` last makes the order total, so a shortlist does not depend
    on `candidates.json` order.

    Every tier resolves to a plain, totally ordered value here, and the result is a plain tuple
    that `sorted` computes once per row. Nothing fallible runs between two rows: there is no
    `cmp_to_key`, no parsing and no lookup in the comparison itself, so the order cannot depend
    on which pairs a particular sort implementation happens to compare. `cid ASC` is a fixed
    final tier, never a runtime option — a caller cannot turn it off, because an order that is
    total only sometimes is not a total order.
    """
    return (
        -scored.score,
        -supported,
        -len(scored.origins),
        best_retrieval_rank(scored),
        _Descending(order_date(scored.publication_date)),
        scored.cid,
    )


def build(
    candidates: list[Candidate],
    screen: ScreenFile,
    *,
    max_in_window: int = DEFAULT_MAX_IN_WINDOW,
    max_outside_window: int = DEFAULT_MAX_OUTSIDE_WINDOW,
    known_criteria: Collection[str] | None = None,
) -> Shortlist:
    """Attach scores, split by window, order, and cut (§8.7).

    `known_criteria` is `queries.json`'s sub-criterion ids when the caller has them; without it
    `criteria_supported` counts every distinct id the screen named.

    The order's last tier is `cid`, so a cid has to identify exactly one row. Both shipped call
    paths already refuse a duplicate before reaching here — `research-scan shortlist` exits 2 on
    `validate_coverage`, the MCP server raises `invalid_artifact` — and this repeats the check
    locally so the guarantee belongs to the ordering rather than to its callers: collapsing two
    rows onto one cid would silently drop a screened paper, which is the one failure this whole
    stage exists to prevent.
    """
    counts: dict[str, int] = {}
    for entry in screen.scores:
        counts[entry.cid] = counts.get(entry.cid, 0) + 1
    duplicates = sorted(cid for cid, count in counts.items() if count > 1)
    if duplicates:
        raise ValueError(
            f"screen.json scores {len(duplicates)} cid(s) more than once: {_sample(duplicates)}"
        )

    scores = {entry.cid: entry.score for entry in screen.scores}
    supported = {
        entry.cid: criteria_supported(entry.criteria_hit, known_criteria)
        for entry in screen.scores
    }
    scored = [
        ScoredCandidate(**candidate.model_dump(), score=scores[candidate.cid])
        for candidate in candidates
        if scores.get(candidate.cid, 0) >= SHORTLIST_SCORE_THRESHOLD
    ]

    def ordered(items: Iterable[ScoredCandidate]) -> list[ScoredCandidate]:
        return sorted(items, key=lambda item: order_key(item, supported.get(item.cid, 0)))

    return Shortlist(
        in_window=ordered(item for item in scored if not item.outside_window)[:max_in_window],
        outside_window=ordered(item for item in scored if item.outside_window)[:max_outside_window],
    )
