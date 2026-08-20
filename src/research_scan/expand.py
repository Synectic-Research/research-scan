# SPDX-License-Identifier: Apache-2.0
"""Citation-graph expansion (spec §8.5): the stage that finds what the queries could not.

The research this tool is built on is unanimous that multi-query search alone is the recall
ceiling and graph traversal is what breaks it (§2, findings 1 and 3). Three moves per run:

* **references** of each seed — where the seed's own argument came from, so this is where the
  foundational papers live. Their dates are *tagged* `outside_window`, never dropped.
* **citations** of each seed, newest first and inside the window — who has answered it since.
* **recommendations** for the whole seed set in one call — S2's "papers like these".

Seeds are only ever papers the screening agent scored ≥ 2. That is the ScholarQuest guard against
off-target exploration (§2, finding 2): expansion follows what was judged relevant, never the
whole candidate pool.

Not in spec §5's module list as a standalone stage owner; §5 does list `expand.py`.
"""

from __future__ import annotations

import logging
import time
from collections.abc import Callable
from dataclasses import dataclass, field
from datetime import date
from pathlib import Path

from research_scan import run as run_module
from research_scan.config import Settings
from research_scan.dedup import deduplicate, with_cid
from research_scan.http import auth_mode
from research_scan.retrieve import apply_filters, write_batches
from research_scan.schema import (
    Candidate,
    CandidatesFile,
    Expanded,
    ExpansionDropped,
    ExpansionStats,
    QueryPlan,
    Relation,
    RunInfo,
    ScreenFile,
)  # Relation used for the anchor check
from research_scan.sources.base import SourceQueryError

log = logging.getLogger(__name__)

DEFAULT_SEEDS = 15
DEFAULT_MAX_NEW = 100
DEFAULT_MAX_OUTSIDE_WINDOW = 20
REFERENCES_PER_SEED = 30
CITATIONS_PER_SEED = 30
RECOMMENDATIONS_LIMIT = 40

#: Screening score at which a candidate is trusted enough to expand from (§8.5).
SEED_SCORE_THRESHOLD = 2

#: The gap round expands from a handful of what its new queries found, not from the pool again.
GAP_SEEDS = 5


@dataclass
class ExpandOptions:
    seeds: int = DEFAULT_SEEDS
    max_new: int = DEFAULT_MAX_NEW
    max_outside_window: int = DEFAULT_MAX_OUTSIDE_WINDOW
    cache: bool | None = None
    round: int = 1


@dataclass
class ExpandResult:
    expanded: Expanded
    stats: ExpansionStats
    total_candidates: int
    seed_titles: list[str] = field(default_factory=list)


class NoSeeds(RuntimeError):
    """Nothing scored ≥ 2, so there is nothing to expand from. Exit 1 with an explanation (§6)."""


def outside_window_spent(run_dir: Path, round_: int) -> int:
    """Out-of-window admissions an *earlier* round already made (v0.2.1).

    The profile's `max_outside_window` is a total for the run, so the gap round gets what round 1
    left rather than a second full allowance. Round 1 counts nothing — re-running it replaces its
    own admissions rather than adding to them, and a stage that is not idempotent cannot be
    re-run, which §14.8 requires.
    """
    if round_ < 2:
        return 0
    path = Path(run_dir) / "expanded.json"
    if not path.exists():
        return 0
    try:
        return len(run_module.read_model(path, Expanded).added_outside_window)
    except run_module.StageInputError:
        return 0


def is_anchored(candidate: Candidate) -> bool:
    return any(origin.relation is Relation.anchor for origin in candidate.origins)


def select_seeds(
    candidates: list[Candidate], scores: dict[str, int], limit: int
) -> list[Candidate]:
    """Anchors always, then score ≥ 2 ordered by score and origin count, capped at `limit` (§8.5).

    Anchors seed regardless of screen score, window tag, and the cap — the user pinned them, and
    "expand from what the brief already names" is the whole point of pinning (S4.5). They also ride
    into the recommendations call as positivePaperIds via the ordinary seeds path.
    """
    anchored = [candidate for candidate in candidates if is_anchored(candidate)]
    anchored_cids = {candidate.cid for candidate in anchored}
    eligible = [
        candidate
        for candidate in candidates
        if candidate.cid not in anchored_cids
        and scores.get(candidate.cid, 0) >= SEED_SCORE_THRESHOLD
        and not candidate.outside_window
    ]
    eligible.sort(key=lambda c: (scores.get(c.cid, 0), len(c.origins)), reverse=True)
    return anchored + eligible[:limit]


def select_gap_seeds(
    candidates: list[Candidate],
    scores: dict[str, int],
    gap_query_ids: set[str],
    new_cids: set[str],
    limit: int = GAP_SEEDS,
) -> list[Candidate]:
    """The gap round seeds only from papers the gap round itself *added*.

    Two filters, and both matter. A gap-round query re-finds plenty of round-1 papers — they gain a
    `round2` origin without being new — and those papers have the higher origin counts, so without
    the `new_cids` filter they win the seed competition and the round walks bibliographies the pool
    already reflects. What has never been read is the gap round's own additions.

    Every `round2` query counts, not only the `gap`-typed ones: a topic where no criterion came
    back thin still writes reformulations, and the papers *those* find are exactly as unexplored.
    """
    eligible = [
        candidate
        for candidate in candidates
        if candidate.cid in new_cids
        and scores.get(candidate.cid, 0) >= SEED_SCORE_THRESHOLD
        and not candidate.outside_window
        and any(origin.query_id in gap_query_ids for origin in candidate.origins)
    ]
    eligible.sort(key=lambda c: (scores.get(c.cid, 0), len(c.origins)), reverse=True)
    return eligible[:limit]


def collect(
    seeds: list[Candidate],
    s2_source: object,
    openalex_source: object,
    window: tuple[date, date],
    *,
    cache: bool | None = None,
    on_event: Callable[..., None] | None = None,
) -> tuple[list[Candidate], dict[str, int]]:
    """Walk the graph around every seed. A seed that fails is logged and skipped, never fatal."""
    found: list[Candidate] = []
    failures: dict[str, int] = {}

    for seed in seeds:
        for relation, call in (
            (
                Relation.references,
                lambda s=seed: s2_source.references(
                    s, limit=REFERENCES_PER_SEED, window=window, cache=cache
                ),
            ),
            (
                Relation.citations,
                lambda s=seed: s2_source.citations(
                    s, limit=CITATIONS_PER_SEED, window=window, cache=cache
                ),
            ),
        ):
            hits = _try(call, relation.value, seed, failures, on_event)
            # S2 not knowing the paper is exactly when OpenAlex earns its keep (§8.5).
            if not hits and seed.ids.openalex:
                hits = _try(
                    lambda s=seed, r=relation: _openalex_graph(
                        openalex_source, s, r, window, cache=cache
                    ),
                    f"{relation.value}:openalex",
                    seed,
                    failures,
                    on_event,
                )
            found.extend(hits)
            _emit(on_event, "seed_graph", seed=seed.cid, relation=relation.value, hits=len(hits))

    recommended = _try(
        lambda: s2_source.recommendations(seeds, limit=RECOMMENDATIONS_LIMIT, cache=cache),
        "recommendations",
        None,
        failures,
        on_event,
    )
    found.extend(recommended)
    _emit(on_event, "recommendations", hits=len(recommended))
    return found, failures


def _openalex_graph(
    openalex_source: object,
    seed: Candidate,
    relation: Relation,
    window: tuple[date, date],
    *,
    cache: bool | None,
) -> list[Candidate]:
    if relation is Relation.references:
        return openalex_source.references(seed, limit=REFERENCES_PER_SEED, cache=cache)
    return openalex_source.citations(seed, limit=CITATIONS_PER_SEED, window=window, cache=cache)


def _try(
    call: Callable[[], list[Candidate]],
    label: str,
    seed: Candidate | None,
    failures: dict[str, int],
    on_event: Callable[..., None] | None,
) -> list[Candidate]:
    try:
        return call()
    except (SourceQueryError, NotImplementedError) as exc:
        failures[label] = failures.get(label, 0) + 1
        log.warning("expansion %s failed for %s: %s", label, seed.cid if seed else "seed set", exc)
        _emit(
            on_event,
            "graph_call_failed",
            call=label,
            seed=seed.cid if seed else None,
            error=str(exc),
        )
        return []


def _emit(on_event: Callable[..., None] | None, event: str, **fields: object) -> None:
    if on_event is not None:
        on_event(event, **fields)


def rank_additions(candidates: list[Candidate], anchor_year: int) -> list[Candidate]:
    """Order by how many seeds pointed at it, then by citations per year (§8.5).

    Seed-link count first because a paper three seeds all cite is structurally central to this
    literature; citations-per-age second so a 2024 paper with 40 citations outranks a 2015 paper
    with 60.

    v0.2.1 tried restricting the first term to in-window seeds and compressing the second with
    `log1p`, and measured both as no-ops: every seed is in-window unless an anchor is not, and a
    monotone transform of a sort key reorders nothing. Reverted — see `docs/measurements.md`.
    """

    def key(candidate: Candidate) -> tuple[int, float]:
        seeds = {origin.seed_id for origin in candidate.origins if origin.seed_id}
        age = max(1, anchor_year - (candidate.year or anchor_year) + 1)
        return len(seeds), candidate.citation_count / age

    return sorted(candidates, key=key, reverse=True)


def run_expand(
    run_dir: Path,
    info: RunInfo,
    plan: QueryPlan,
    existing: list[Candidate],
    screen: ScreenFile,
    s2_source: object,
    openalex_source: object,
    *,
    settings: Settings,
    window: tuple[date, date],
    options: ExpandOptions,
    anchor: date | None = None,
    on_event: Callable[..., None] | None = None,
    new_cids: set[str] | None = None,
) -> ExpandResult:
    """Seeds → graph → filters → caps → new batches, appended to `candidates.json`."""
    started = time.monotonic()
    anchor = anchor or run_module.today()
    scores = {entry.cid: entry.score for entry in screen.scores}
    gap_round = options.round == 2
    prefix = "xr" if gap_round else "x"

    if gap_round:
        gap_ids = {query.id for query in plan.round2}
        seeds = select_gap_seeds(existing, scores, gap_ids, new_cids or set())
        if not seeds:
            raise NoSeeds(
                "no new candidate from a gap query scored ≥ "
                f"{SEED_SCORE_THRESHOLD} — the gap round has nothing to grow from"
            )
    else:
        seeds = select_seeds(existing, scores, options.seeds)
        if not seeds:
            raise NoSeeds(
                f"no candidate scored ≥ {SEED_SCORE_THRESHOLD} in screen.json — "
                "expansion has nothing to grow from; re-screen or widen the window"
            )
    _emit(on_event, "seeds", count=len(seeds), cids=[seed.cid for seed in seeds])

    # The graph walk uses S2 first and falls back to OpenAlex, so both hosts' auth modes decide
    # this stage's rate-limit ceiling. Recorded before the walk, so a stage that dies mid-way still
    # says which credentials it was running under.
    auth = {source: auth_mode(settings, source) for source in ("s2", "openalex")}
    _emit(on_event, "auth", **auth)

    raw, failures = collect(
        seeds, s2_source, openalex_source, window, cache=options.cache, on_event=on_event
    )

    # Dedup against what retrieval already had: an "addition" that is already in the pool is not
    # new, it is another origin on a paper we know — and origin count is a ranking signal.
    known_cids = {candidate.cid for candidate in existing}
    merged, _ = deduplicate(list(existing) + [with_cid(candidate) for candidate in raw])
    additions = [candidate for candidate in merged if candidate.cid not in known_cids]
    updated_existing = [candidate for candidate in merged if candidate.cid in known_cids]

    kept, dropped_counts = apply_filters(
        additions,
        plan,
        window,
        include_preprints=True,
        tag_outside_window=True,  # §8.5: references before the window are tagged, not dropped
    )
    dropped = ExpansionDropped(
        retracted=dropped_counts.retracted,
        must_not=dropped_counts.must_not,
        type=dropped_counts.type,
    )

    in_window = rank_additions([c for c in kept if not c.outside_window], anchor.year)
    outside = rank_additions([c for c in kept if c.outside_window], anchor.year)
    capped_in = in_window[: options.max_new]
    capped_out = outside[: options.max_outside_window]
    dropped.cap = (len(in_window) - len(capped_in)) + (len(outside) - len(capped_out))
    _emit(
        on_event,
        "expansion_cap",
        in_window=len(capped_in),
        outside_window=len(capped_out),
        dropped=dropped.cap,
    )

    added = capped_in + capped_out
    all_candidates = updated_existing + added
    run_module.write_model(
        Path(run_dir) / "candidates.json", CandidatesFile(run=info, candidates=all_candidates)
    )
    batches = write_batches(run_dir, added, plan, prefix=prefix)

    expanded = Expanded(
        seeds=[seed.cid for seed in seeds],
        added=[candidate.cid for candidate in capped_in],
        added_outside_window=[candidate.cid for candidate in capped_out],
        dropped=dropped,
        batches=batches,
    )
    name = "expanded-round2.json" if gap_round else "expanded.json"
    run_module.write_model(Path(run_dir) / name, expanded)

    stats = ExpansionStats(
        seeds=len(seeds),
        added=len(capped_in),
        added_outside_window=len(capped_out),
        dropped=dropped,
        auth=auth,
        duration_s=round(time.monotonic() - started, 3),
    )
    if failures:
        log.warning("expansion graph calls failed: %s", failures)

    return ExpandResult(
        expanded=expanded,
        stats=stats,
        total_candidates=len(all_candidates),
        seed_titles=[seed.title for seed in seeds],
    )
