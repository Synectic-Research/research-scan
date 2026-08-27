# SPDX-License-Identifier: Apache-2.0
"""Coverage validation and the ordered cut handed to the rerank step (spec §8.7, §9.6).

This stage exists to make one failure impossible: a paper that was retrieved, never screened, and
so quietly never considered. Every cid in `candidates.json` must carry exactly one score. Anything
else exits 2 with the list, because the agent can fix that and only the agent can.
"""

from __future__ import annotations

import functools
import logging
from collections.abc import Collection, Iterable, Sequence
from dataclasses import dataclass, field

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

#: What an unknown publication date sorts as: last, under a DESC date tier.
NO_DATE = "0000-00-00"


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

    Unique, because a repeated id is one criterion; and restricted to `known` when the run's
    `queries.json` is at hand, so a typo cannot buy a place in the order. Empty on pre-v0.2
    `screen.json` files, where the tier no-ops and the remaining tiers decide.

    criteria_supported is a lexicographic tie-break feature, not a relevance score — never
    optimize it numerically.
    """
    if known is None:
        return len({criterion for criterion in criteria_hit if criterion})
    return len({criterion for criterion in criteria_hit if criterion in known})


def best_retrieval_rank(candidate: Candidate) -> int:
    """The best position any source gave this paper, over every origin it earned."""
    return min((origin.rank for origin in candidate.origins), default=NO_RETRIEVAL_RANK)


def order_key(scored: ScoredCandidate, supported: int = 0) -> tuple:
    """The shortlist's lexicographic total order — ascending, so `sorted(..., key=…)` is enough.

    score DESC, criteria_supported DESC, origin_count DESC, best_retrieval_rank ASC, date DESC,
    cid ASC (§8.7, Phase-1.2A). Date sat third until v0.6.0, where — inside the large equal-score,
    equal-origin bands a real pool actually produces — it was the only discriminator left, so the
    cut ran as a recency filter and dropped central papers for being older than their band
    (`552f09c:research/experiments/phase12-selection/results/report_tail.md` §4). The two tiers
    ahead of it are relevance evidence the screen and the retrieval already produced; `cid` last
    makes the order total, so a shortlist does not depend on `candidates.json` order.
    """
    return (
        -scored.score,
        -supported,
        -len(scored.origins),
        best_retrieval_rank(scored),
        _Descending(scored.publication_date or NO_DATE),
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
    """
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
