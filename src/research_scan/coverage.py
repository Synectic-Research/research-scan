# SPDX-License-Identifier: Apache-2.0
"""Coverage of the sub-criteria (V1.1) — deterministic, no judgement.

Screening says whether a paper is relevant; it never said *what* it was relevant to. Without that,
a scan cannot tell a criterion nobody wrote a good query for from a criterion the literature is
simply thin on, and both look like "we found 200 papers". `criteria_hit` on each screen entry
supplies the attribution; this module counts it.

The only threshold here is `THIN_CRITERION_HITS`, and it is a count, not an opinion: a criterion
with fewer than five kept papers is where the gap round aims. Which queries to write against it is
the agent's call under `plan-rubric.md` — the CLI never writes a query.
"""

from __future__ import annotations

import statistics
from collections import Counter
from dataclasses import dataclass, field

from research_scan.schema import (
    THIN_CRITERION_HITS,
    Candidate,
    CoverageFile,
    CoverageRound,
    CriterionCoverage,
    GapRoundAdvice,
    Profile,
    QueryPlan,
    QueryType,
    QueryYield,
    Relation,
    RunInfo,
    ScreenFile,
    SeedPrecision,
)

#: A paper only counts towards a criterion if screening kept it (§8.7's threshold, reused).
KEPT_SCORE = 2

#: The gap round's screening cost is real, so `standard` only pays it when one of these trips.
#:
#: Absolute floor first, for a pool too thin to argue about. The relative test is the one that
#: earns its keep: on both reference runs every criterion cleared the flat threshold while one sat
#: at a fifth of the median, which is the shape a missing query actually makes. The query test
#: catches the other cause — a query that returned almost nothing is a query aimed wrong.
GAP_MIN_HITS = 8
GAP_MEDIAN_SHARE = 0.5
GAP_MIN_QUERY_POOL = 20


@dataclass
class AttributionReport:
    """`criteria_hit` ids that no sub-criterion in `queries.json` defines."""

    unknown: list[tuple[str, str]] = field(default_factory=list)
    missing: list[str] = field(default_factory=list)

    @property
    def ok(self) -> bool:
        return not self.unknown

    def lines(self) -> list[str]:
        shown = [f"{cid}: unknown criterion {criterion!r}" for cid, criterion in self.unknown[:10]]
        if len(self.unknown) > 10:
            shown.append(f"… (+{len(self.unknown) - 10} more)")
        return shown


def validate_criteria_hit(plan: QueryPlan, screen: ScreenFile) -> AttributionReport:
    """Every `criteria_hit` id must name a sub-criterion. A typo is exit 2, not a silent zero."""
    known = {criterion.id for criterion in plan.sub_criteria}
    report = AttributionReport()
    for entry in screen.scores:
        for criterion in entry.criteria_hit:
            if criterion not in known:
                report.unknown.append((entry.cid, criterion))
        if entry.score >= KEPT_SCORE and not entry.criteria_hit:
            report.missing.append(entry.cid)
    return report


def current_round(plan: QueryPlan) -> int:
    """Derived from the plan, not from how often `coverage` has run — so re-runs are idempotent."""
    return 2 if plan.round2 else 1


def build(
    info: RunInfo,
    plan: QueryPlan,
    candidates: list[Candidate],
    screen: ScreenFile,
    *,
    previous: CoverageFile | None = None,
    profile: Profile = Profile.standard,
    forced: bool = False,
) -> CoverageFile:
    """One snapshot for the current round, keeping any snapshot from an earlier round."""
    snapshot = _snapshot(plan, candidates, screen)
    rounds = [
        entry for entry in (previous.rounds if previous else []) if entry.round != snapshot.round
    ]
    rounds.append(snapshot)
    rounds.sort(key=lambda entry: entry.round)
    advice = advise(snapshot, profile, forced=forced) if snapshot.round == 1 else None
    return CoverageFile(
        run=info, rounds=rounds, gap_round=advice or (previous.gap_round if previous else None)
    )


def _snapshot(plan: QueryPlan, candidates: list[Candidate], screen: ScreenFile) -> CoverageRound:
    scores = {entry.cid: entry.score for entry in screen.scores}
    hits = {entry.cid: entry.criteria_hit for entry in screen.scores}
    by_cid = {candidate.cid: candidate for candidate in candidates}
    query_types = {query.id: query.type for query in [*plan.queries, *plan.round2]}

    kept = [cid for cid, score in scores.items() if score >= KEPT_SCORE and cid in by_cid]

    criteria = []
    for criterion in plan.sub_criteria:
        matched = [cid for cid in kept if criterion.id in hits.get(cid, [])]
        # Counted per *paper*, not per origin: a paper three queries found is one paper covering
        # the criterion, and counting its origins would make the breakdown outrun `hits`.
        types: Counter[str] = Counter()
        sources: Counter[str] = Counter()
        for cid in matched:
            candidate = by_cid[cid]
            for source in {origin.source.value for origin in candidate.origins}:
                sources[source] += 1
            for kind in {
                _origin_type(origin.relation, origin.query_id, query_types)
                for origin in candidate.origins
            }:
                types[kind] += 1
        criteria.append(
            CriterionCoverage(
                id=criterion.id,
                name=criterion.name,
                hits=len(matched),
                by_query_type=dict(sorted(types.items())),
                by_source=dict(sorted(sources.items())),
                thin=len(matched) < THIN_CRITERION_HITS,
            )
        )

    yields = []
    for query in [*plan.queries, *plan.round2]:
        pool = [
            candidate.cid
            for candidate in candidates
            if any(origin.query_id == query.id for origin in candidate.origins)
        ]
        yields.append(
            QueryYield(
                query_id=query.id,
                type=query.type,
                pool=len(pool),
                ge2=sum(1 for cid in pool if scores.get(cid, 0) >= KEPT_SCORE),
            )
        )

    neighbours: dict[str, set[str]] = {}
    for candidate in candidates:
        for origin in candidate.origins:
            if origin.seed_id:
                neighbours.setdefault(origin.seed_id, set()).add(candidate.cid)

    seeds = []
    for seed_id in sorted(neighbours):
        found = sorted(neighbours[seed_id])
        good = sum(1 for cid in found if scores.get(cid, 0) >= KEPT_SCORE)
        seeds.append(
            SeedPrecision(
                seed_id=seed_id,
                neighbours=len(found),
                ge2=good,
                precision=round(good / len(found), 3) if found else 0.0,
            )
        )

    return CoverageRound(
        round=current_round(plan),
        screened=len(scores),
        ge2=len(kept),
        unattributed_ge2=sum(1 for cid in kept if not hits.get(cid)),
        criteria=criteria,
        queries=yields,
        seeds=seeds,
    )


def _origin_type(relation: Relation, query_id: str | None, types: dict[str, QueryType]) -> str:
    """A query origin reports its query's type; a graph origin reports its relation."""
    if relation is Relation.query and query_id:
        found = types.get(query_id)
        return found.value if found else "unknown"
    return relation.value


def advise(snapshot: CoverageRound, profile: Profile, *, forced: bool = False) -> GapRoundAdvice:
    """Whether the gap round is worth its cost. Deterministic; `--gap-round` overrides it."""
    hits = sorted(criterion.hits for criterion in snapshot.criteria)
    reasons: list[str] = []
    if hits:
        weakest = min(snapshot.criteria, key=lambda criterion: criterion.hits)
        middle = statistics.median(hits)
        if weakest.hits < GAP_MIN_HITS:
            reasons.append(
                f"{weakest.id} {weakest.name} has {weakest.hits} papers, under {GAP_MIN_HITS}"
            )
        if weakest.hits < GAP_MEDIAN_SHARE * middle:
            reasons.append(
                f"{weakest.id} {weakest.name} has {weakest.hits} papers against a median of"
                f" {middle:g} across the criteria"
            )
    starved = [q for q in snapshot.queries if q.pool < GAP_MIN_QUERY_POOL]
    if starved:
        named = ", ".join(f"{q.query_id} ({q.pool})" for q in starved[:3])
        reasons.append(
            f"{len(starved)} quer(ies) returned under {GAP_MIN_QUERY_POOL} papers: {named}"
        )

    if forced:
        return GapRoundAdvice(
            should_run=True, profile=profile, forced=True, reasons=["--gap-round was passed"]
        )
    if profile is Profile.deep:
        return GapRoundAdvice(
            should_run=True, profile=profile, reasons=["the deep profile always runs it", *reasons]
        )
    if profile is Profile.quick:
        return GapRoundAdvice(
            should_run=False, profile=profile, reasons=["the quick profile never runs it"]
        )
    if reasons:
        return GapRoundAdvice(should_run=True, profile=profile, reasons=reasons)
    return GapRoundAdvice(
        should_run=False,
        profile=profile,
        reasons=["coverage is even across the criteria and no query came back starved"],
    )


def thin_criteria(snapshot: CoverageRound) -> list[str]:
    return [criterion.id for criterion in snapshot.criteria if criterion.thin]


def render(coverage: CoverageFile) -> str:
    """The human table: one row per criterion, one column per round."""
    rounds = coverage.rounds
    if not rounds:
        return "no coverage recorded"
    header = ["| Criterion | " + " | ".join(f"round {r.round}" for r in rounds) + " | thin |"]
    header.append("|---" * (len(rounds) + 2) + "|")
    latest = rounds[-1]
    for index, criterion in enumerate(latest.criteria):
        cells = []
        for snapshot in rounds:
            match = snapshot.criteria[index] if index < len(snapshot.criteria) else None
            cells.append(str(match.hits) if match else "—")
        header.append(
            f"| {criterion.id} {criterion.name} | "
            + " | ".join(cells)
            + f" | {'yes' if criterion.thin else 'no'} |"
        )
    header.append("")
    header.append(
        f"screened {latest.screened} · kept ≥2 {latest.ge2}"
        f" · unattributed {latest.unattributed_ge2}"
    )
    if coverage.gap_round:
        verdict = "run the gap round" if coverage.gap_round.should_run else "skip the gap round"
        header.append(
            f"{verdict} ({coverage.gap_round.profile.value}): "
            + "; ".join(coverage.gap_round.reasons)
        )
    return "\n".join(header)
