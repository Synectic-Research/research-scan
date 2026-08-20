# SPDX-License-Identifier: Apache-2.0
"""Coverage validation and the ordered cut handed to the rerank step (spec §8.7, §9.6).

This stage exists to make one failure impossible: a paper that was retrieved, never screened, and
so quietly never considered. Every cid in `candidates.json` must carry exactly one score. Anything
else exits 2 with the list, because the agent can fix that and only the agent can.
"""

from __future__ import annotations

import logging
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


def order_key(scored: ScoredCandidate) -> tuple:
    """Score, then how many ways we found it, then recency (§8.7)."""
    return (scored.score, len(scored.origins), scored.publication_date or "0000-00-00")


def build(
    candidates: list[Candidate],
    screen: ScreenFile,
    *,
    max_in_window: int = DEFAULT_MAX_IN_WINDOW,
    max_outside_window: int = DEFAULT_MAX_OUTSIDE_WINDOW,
) -> Shortlist:
    """Attach scores, split by window, order, and cut (§8.7)."""
    scores = {entry.cid: entry.score for entry in screen.scores}
    scored = [
        ScoredCandidate(**candidate.model_dump(), score=scores[candidate.cid])
        for candidate in candidates
        if scores.get(candidate.cid, 0) >= SHORTLIST_SCORE_THRESHOLD
    ]

    in_window = sorted(
        (item for item in scored if not item.outside_window), key=order_key, reverse=True
    )
    outside_window = sorted(
        (item for item in scored if item.outside_window), key=order_key, reverse=True
    )

    return Shortlist(
        in_window=in_window[:max_in_window],
        outside_window=outside_window[:max_outside_window],
    )
