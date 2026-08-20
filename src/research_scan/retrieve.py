# SPDX-License-Identifier: Apache-2.0
"""The retrieval pipeline (spec §8.1–§8.4): fan out, dedup, filter, cap, batch.

Every stage here is a pure function over lists of Candidates, so each one can be tested without a
network or a run directory. `run_retrieve` is the only part that touches disk.

Not in spec §5's module list; added deliberately (see AGENTS.md).
"""

from __future__ import annotations

import logging
import re
import time
from collections.abc import Callable, Sequence
from dataclasses import dataclass, field
from datetime import date
from pathlib import Path

from research_scan import run as run_module
from research_scan.config import Settings
from research_scan.dedup import deduplicate, title_similarity, with_cid
from research_scan.http import HttpClient, auth_mode
from research_scan.schema import (
    Anchor,
    Candidate,
    CandidatesFile,
    Counts,
    Domain,
    Origin,
    Query,
    QueryPlan,
    Relation,
    RetrievalDropped,
    RetrievalStats,
    RunInfo,
    ScreenBatch,
    ScreenBatchItem,
    SourceName,
    SourceStats,
    WorkType,
)
from research_scan.sources.arxiv import ArxivSource
from research_scan.sources.base import Source
from research_scan.sources.openalex import OpenAlexSource
from research_scan.sources.s2 import S2Source

log = logging.getLogger(__name__)

# 40/450, raised from 20/250 in S10f: at 20, four of six golden papers on the llm-lit-search
# topic sat between rank 20 and 40 of their best query (OpenAlex relevance mixes text match with
# a citation boost, so recent low-citation work ranks low); 40 recovered one more golden paper
# with no loss on defaults-savings, at unchanged OpenAlex cost.
DEFAULT_PER_QUERY = 40
DEFAULT_MAX_CANDIDATES = 450


def scaled_max_candidates(built_sources: int) -> int:
    """Default pool cap, scaled so per-source depth survives routed extras (S10g).

    450 was measured against the two mandatory sources; routing arXiv in without scaling made the
    round-robin cap displace a golden paper that sat 36 deep in an S2 query (LitLLM). The cap
    exists to stop one *query* dominating the pool, not to shrink per-source depth whenever a
    third source is routed. An explicit ``--max-candidates`` always wins.
    """
    return DEFAULT_MAX_CANDIDATES * max(1, built_sources) // 2


BATCH_SIZE = 25
ABSTRACT_PREVIEW_CHARS = 600

#: Routing map (spec §7). arXiv and PubMed are declared here but only built in S6.
ROUTING: dict[Domain, tuple[SourceName, ...]] = {
    Domain.behavioral: (SourceName.openalex, SourceName.s2),
    Domain.cs: (SourceName.openalex, SourceName.s2, SourceName.arxiv),
    Domain.biomed: (SourceName.openalex, SourceName.s2, SourceName.pubmed),
    Domain.general: (SourceName.openalex, SourceName.s2),
}

#: Sources with a working adapter today. The rest are recorded `unavailable`, never dropped quietly.
IMPLEMENTED_SOURCES: frozenset[SourceName] = frozenset(
    {SourceName.openalex, SourceName.s2, SourceName.arxiv}
)

#: An anchor is a claim about one specific paper, so resolution is near-exact or nothing.
ANCHOR_TITLE_RATIO = 95

#: Title-resolution search must not be bounded by the run window — anchors are often classics.
ANCHOR_SEARCH_WINDOW = (date(1900, 1, 1), date(2100, 1, 1))

#: Raw source type strings that are not scholarly works (§8.3). Compared case-folded.
NON_SCHOLARLY_TYPES: frozenset[str] = frozenset(
    {"paratext", "erratum", "dataset", "peer-review", "libguides", "supplementary-materials"}
)


@dataclass
class RetrieveOptions:
    per_query: int = DEFAULT_PER_QUERY
    max_candidates: int = DEFAULT_MAX_CANDIDATES
    include_preprints: bool = True
    include_all_types: bool = False
    cache: bool | None = None
    round: int = 1


@dataclass
class RetrieveResult:
    candidates: list[Candidate]
    stats: RetrievalStats
    batches: list[str]
    counts: Counts
    per_query_hits: dict[str, int] = field(default_factory=dict)
    added: list[Candidate] = field(default_factory=list)


class AllSourcesFailed(RuntimeError):
    """Every routed, available source failed. The CLI turns this into exit 1 (§6)."""


# --- routing ----------------------------------------------------------------


def route(
    domain: Domain, plan: QueryPlan, override: list[SourceName] | None = None
) -> list[SourceName]:
    """`--sources` wins; else the domain map, plus arXiv for `general` if any query is a method."""
    if override:
        return list(dict.fromkeys(override))
    selected = list(ROUTING[domain])
    if domain is Domain.general and any(query.type.value == "method" for query in plan.queries):
        selected.append(SourceName.arxiv)
    return selected


def build_sources(names: list[SourceName], client: HttpClient) -> dict[SourceName, Source]:
    builders = {
        SourceName.openalex: OpenAlexSource,
        SourceName.s2: S2Source,
        SourceName.arxiv: ArxivSource,
    }
    return {name: builders[name](client) for name in names if name in IMPLEMENTED_SOURCES}


# --- §8.1 fan-out -----------------------------------------------------------


def fan_out(
    plan: QueryPlan,
    sources: dict[SourceName, Source],
    window: tuple[date, date],
    *,
    per_query: int,
    settings: Settings,
    cache: bool | None = None,
    on_event: Callable[..., None] | None = None,
    queries: Sequence[Query] | None = None,
) -> tuple[list[Candidate], dict[str, SourceStats], dict[str, int]]:
    """Every query against every routed source, in a stable order.

    Order matters downstream: it is the tie-break for dedup ("first seen wins") and the input to
    the round-robin cap. Query order × source order × rank, always.

    `queries` overrides `plan.queries` — the gap round fans out `plan.round2` and nothing else.
    """
    hits: list[Candidate] = []
    stats: dict[str, SourceStats] = {
        name.value: SourceStats(auth=auth_mode(settings, name.value)) for name in sources
    }
    per_query_hits: dict[str, int] = {}

    for query in plan.queries if queries is None else queries:
        for name, source in sources.items():
            stat = stats[name.value]
            stat.queried += 1
            try:
                found = source.search(query.text, window, limit=per_query, cache=cache)
            except Exception as exc:
                # Deliberately broad: one query failing one source (HTTP error, a malformed record,
                # a schema surprise) must not end the scan. It is recorded, and the run continues on
                # whatever the other sources returned. Only *every* source failing is fatal (§6).
                stat.failed += 1
                log.warning("%s query %s failed: %s", name.value, query.id, exc)
                _emit(
                    on_event,
                    "source_query_failed",
                    source=name.value,
                    query_id=query.id,
                    auth=stat.auth,
                    error=str(exc),
                )
                continue

            stamped = [
                candidate.model_copy(
                    update={
                        "origins": [
                            origin.model_copy(update={"query_id": query.id})
                            for origin in candidate.origins
                        ]
                    }
                )
                for candidate in found
            ]
            stat.hits += len(stamped)
            per_query_hits[query.id] = per_query_hits.get(query.id, 0) + len(stamped)
            hits.extend(stamped)
            _emit(
                on_event,
                "source_query",
                source=name.value,
                query_id=query.id,
                auth=stat.auth,
                hits=len(stamped),
            )

    for name, stat in stats.items():
        if stat.queried and not stat.hits and not stat.failed:
            # Not an error — but a source answering every query with zero results is nearly always
            # queries written for it wrongly (S2's /paper/search matches keywords, not sentences).
            log.warning(
                "%s answered %d queries with 0 hits — the queries may be too long for it",
                name,
                stat.queried,
            )
            _emit(on_event, "source_returned_nothing", source=name, queried=stat.queried)

    if stats and all(stat.failed == stat.queried for stat in stats.values()):
        raise AllSourcesFailed(
            "every routed source failed: "
            + ", ".join(sorted(stats))
            + " — see the stage log for status codes"
        )
    return hits, stats, per_query_hits


def _emit(on_event: Callable[..., None] | None, event: str, **fields: object) -> None:
    if on_event is not None:
        on_event(event, **fields)


# --- anchors (S4.5) ---------------------------------------------------------


def resolve_anchors(
    anchors: list[Anchor],
    adapters: dict[SourceName, Source],
    window: tuple[date, date],
    *,
    cache: bool | None = None,
    on_event: Callable[..., None] | None = None,
) -> list[Candidate]:
    """Pin the papers the brief already names into the candidate pool.

    DOI first (unambiguous), else a title search on every adapter accepting only a hit at ratio
    ≥ 95 — an anchor that resolves to the wrong paper would then seed expansion around the wrong
    neighbourhood, which is worse than not resolving at all. Unresolved anchors are warned about
    and recorded in the stage log, never silently dropped.

    Anchors bypass the §8.3 filters and the §8.4 cap: the user pinned them, which outranks our
    heuristics. The window only *tags* them (`outside_window`), same as expansion references.
    """
    resolved: list[Candidate] = []
    openalex = adapters.get(SourceName.openalex)

    for index, anchor in enumerate(anchors):
        candidate: Candidate | None = None
        source_used: SourceName | None = None

        if anchor.doi and openalex is not None:
            try:
                candidate = openalex.get_by_doi(anchor.doi, cache=cache)
                source_used = SourceName.openalex
            except Exception as exc:
                log.warning("anchor doi lookup failed for %s: %s", anchor.doi, exc)

        if candidate is None and anchor.title:
            best_ratio = 0.0
            for name, adapter in adapters.items():
                try:
                    hits = adapter.search(anchor.title, ANCHOR_SEARCH_WINDOW, limit=3, cache=cache)
                except Exception as exc:
                    log.warning("anchor title search failed on %s: %s", name.value, exc)
                    continue
                for hit in hits:
                    ratio = title_similarity(anchor.title, hit.title)
                    if ratio >= ANCHOR_TITLE_RATIO and ratio > best_ratio:
                        candidate, source_used, best_ratio = hit, name, ratio

        if candidate is None:
            log.warning("anchor could not be resolved: %s", anchor.doi or anchor.title)
            _emit(
                on_event,
                "anchor_unresolved",
                doi=anchor.doi,
                title=anchor.title,
            )
            continue

        pinned = candidate.model_copy(
            update={
                "origins": [Origin(source=source_used, relation=Relation.anchor, rank=index)],
                "outside_window": not _in_window(candidate, window),
            }
        )
        resolved.append(with_cid(pinned))
        _emit(
            on_event,
            "anchor_resolved",
            cid=resolved[-1].cid,
            title=candidate.title,
            source=source_used.value,
        )

    return resolved


# --- §8.3 filters -----------------------------------------------------------


def must_not_pattern(phrase: str) -> re.Pattern[str]:
    """Word-boundary match, so `AI` never fires on `AIDS` and `nudge` never on `nudged`.

    `(?<!\\w)…(?!\\w)` rather than `\\b…\\b`: identical for word-character phrases, and correct for
    ones that start or end with punctuation (`COVID-19`, `p-value`).
    """
    return re.compile(rf"(?<!\w){re.escape(phrase.strip())}(?!\w)", re.IGNORECASE)


def apply_filters(
    candidates: list[Candidate],
    plan: QueryPlan,
    window: tuple[date, date],
    *,
    include_all_types: bool = False,
    include_preprints: bool = True,
    tag_outside_window: bool = False,
) -> tuple[list[Candidate], RetrievalDropped]:
    """Spec §8.3. Reasons are checked in a fixed order so each drop is counted exactly once.

    `tag_outside_window` is what expansion passes (§8.5): a reference published before the window
    is the foundational paper the brief is missing, so it is marked rather than discarded.
    """
    patterns = [must_not_pattern(phrase) for phrase in plan.must_not if phrase.strip()]
    dropped = RetrievalDropped()
    kept: list[Candidate] = []

    for candidate in candidates:
        if candidate.is_retracted:
            dropped.retracted += 1
            continue
        if patterns and _matches_any(candidate, patterns):
            dropped.must_not += 1
            continue
        if not include_all_types and (candidate.raw_type or "").casefold() in NON_SCHOLARLY_TYPES:
            dropped.type += 1
            continue
        if not _in_window(candidate, window):
            if not tag_outside_window:
                dropped.window += 1
                continue
            candidate = candidate.model_copy(update={"outside_window": True})
        if not include_preprints and candidate.type is WorkType.preprint:
            dropped.preprint += 1
            continue
        kept.append(candidate)

    return kept, dropped


def _matches_any(candidate: Candidate, patterns: list[re.Pattern[str]]) -> bool:
    haystack = f"{candidate.title}\n{candidate.abstract or ''}"
    return any(pattern.search(haystack) for pattern in patterns)


def _in_window(candidate: Candidate, window: tuple[date, date]) -> bool:
    """Belt and braces: both sources filter server-side, but a merged record can carry a new date.

    A record with no date at all is kept — dropping it would silently lose papers whose only sin is
    thin metadata, and `verify` will resolve the real date later.
    """
    start, end = window
    if candidate.publication_date:
        try:
            published = date.fromisoformat(candidate.publication_date)
        except ValueError:
            return True
        return start <= published <= end
    if candidate.year is not None:
        return start.year <= candidate.year <= end.year
    return True


# --- §8.4 cap ---------------------------------------------------------------


def cap_round_robin(
    candidates: list[Candidate],
    plan: QueryPlan,
    max_candidates: int,
    *,
    queries: Sequence[Query] | None = None,
) -> tuple[list[Candidate], int]:
    """Take candidates one query at a time, best rank first, so no query can swamp the pool.

    The returned order is the round-robin order, which also interleaves queries across screening
    batches — each batch reaches the screening agent topically mixed rather than as one query's
    result list. Applied even when nothing is cut, so ordering does not depend on the pool size.
    """
    ordered_queries = plan.queries if queries is None else queries
    buckets: dict[str, list[tuple[int, int]]] = {query.id: [] for query in ordered_queries}
    unassigned: list[int] = []

    for index, candidate in enumerate(candidates):
        best: dict[str, int] = {}
        for origin in candidate.origins:
            if origin.relation is Relation.query and origin.query_id:
                best[origin.query_id] = min(best.get(origin.query_id, origin.rank), origin.rank)
        if not best:
            unassigned.append(index)
            continue
        for query_id, rank in best.items():
            buckets.setdefault(query_id, []).append((rank, index))

    for bucket in buckets.values():
        bucket.sort()

    order = [query.id for query in ordered_queries] + [
        key for key in buckets if key not in {query.id for query in ordered_queries}
    ]
    pointers = dict.fromkeys(order, 0)
    selected: list[int] = []
    seen: set[int] = set()

    while len(selected) < max_candidates:
        progressed = False
        for query_id in order:
            bucket = buckets.get(query_id, ())
            position = pointers[query_id]
            while position < len(bucket) and bucket[position][1] in seen:
                position += 1
            pointers[query_id] = position
            if position >= len(bucket):
                continue
            index = bucket[position][1]
            pointers[query_id] = position + 1
            seen.add(index)
            selected.append(index)
            progressed = True
            if len(selected) >= max_candidates:
                break
        if not progressed:
            break

    for index in unassigned:
        if len(selected) >= max_candidates:
            break
        if index not in seen:
            seen.add(index)
            selected.append(index)

    kept = [candidates[index] for index in selected]
    return kept, len(candidates) - len(kept)


# --- §9.3 screening batches -------------------------------------------------


def write_batches(
    run_dir: Path,
    candidates: list[Candidate],
    plan: QueryPlan,
    *,
    size: int = BATCH_SIZE,
    prefix: str = "",
) -> list[str]:
    """Write `screen-batches/01.json`… (or `x01.json`… when expansion calls it, §9.3).

    Only the caller's own series is cleared: re-running `retrieve` must not delete expansion's
    batches, and re-running `expand` must not delete retrieval's.
    """
    batch_dir = Path(run_dir) / "screen-batches"
    batch_dir.mkdir(parents=True, exist_ok=True)
    for stale in sorted(batch_dir.glob(f"{prefix}[0-9][0-9].json")):
        stale.unlink()

    ids: list[str] = []
    for number, start in enumerate(range(0, len(candidates), size), start=1):
        batch_id = f"{prefix}{number:02d}"
        batch = ScreenBatch(
            batch=batch_id,
            sub_criteria=plan.sub_criteria,
            items=[_batch_item(candidate) for candidate in candidates[start : start + size]],
        )
        run_module.write_model(batch_dir / f"{batch_id}.json", batch)
        ids.append(batch_id)
    return ids


def _batch_item(candidate: Candidate) -> ScreenBatchItem:
    """The screening agent sees title, abstract and provenance — never ids or citation counts.

    Falls back to the `tldr` when a record has no abstract, so a paper is not screened on its title
    alone when a summary exists.
    """
    text = candidate.abstract or candidate.tldr
    return ScreenBatchItem(
        cid=candidate.cid,
        title=candidate.title,
        abstract_600=text[:ABSTRACT_PREVIEW_CHARS] if text else None,
        year=candidate.year,
        venue=candidate.venue,
        origin_count=len(candidate.origins),
        outside_window=candidate.outside_window,
    )


# --- orchestration ----------------------------------------------------------


def run_retrieve(
    run_dir: Path,
    info: RunInfo,
    plan: QueryPlan,
    client: HttpClient,
    *,
    sources: list[SourceName],
    window: tuple[date, date],
    options: RetrieveOptions,
    on_event: Callable[..., None] | None = None,
    existing: list[Candidate] | None = None,
) -> RetrieveResult:
    """Fan out → dedup → filter → cap → batches, then write `candidates.json`.

    The gap round (`options.round == 2`) runs `plan.round2` and only that, and *adds* to `existing`:
    round 1's pool already survived a cap, and re-capping the union would silently un-screen papers
    the agent has already scored. So the cap applies to the additions, with the same budget.
    """
    started = time.monotonic()
    adapters = build_sources(sources, client)
    unavailable = [name for name in sources if name not in adapters]
    for name in unavailable:
        log.warning("source %s is routed but not built in this version — skipping", name.value)
    if not adapters:
        raise AllSourcesFailed(
            "no usable source: "
            + ", ".join(name.value for name in sources)
            + f" — built in this version: {', '.join(sorted(n.value for n in IMPLEMENTED_SOURCES))}"
        )

    gap_round = options.round == 2
    queries = plan.round2 if gap_round else plan.queries
    prefix = "r" if gap_round else ""
    known = list(existing or [])

    raw, per_source, per_query_hits = fan_out(
        plan,
        adapters,
        window,
        per_query=options.per_query,
        settings=client.settings,
        cache=options.cache,
        on_event=on_event,
        queries=queries,
    )
    _emit(on_event, "fan_out", hits=len(raw), per_query=per_query_hits)

    deduped, dedup_report = deduplicate(raw)
    _emit(on_event, "dedup", kept=len(deduped), merged=dedup_report.merged_by)

    filtered, dropped = apply_filters(
        deduped,
        plan,
        window,
        include_all_types=options.include_all_types,
        include_preprints=options.include_preprints,
    )
    _emit(on_event, "filter", kept=len(filtered), dropped=dropped.model_dump())

    capped, dropped.cap = cap_round_robin(filtered, plan, options.max_candidates, queries=queries)
    _emit(on_event, "cap", kept=len(capped), dropped=dropped.cap)

    if plan.anchors:
        # Anchors join after the cap, on purpose: they are exempt from it, and dedup merges a
        # query-found copy with its anchor so the paper carries both origins.
        pinned = resolve_anchors(
            plan.anchors, adapters, window, cache=options.cache, on_event=on_event
        )
        capped, _anchor_dedup = deduplicate(capped + pinned)
        _emit(on_event, "anchors", resolved=len(pinned), of=len(plan.anchors))

    for name in unavailable:
        per_source[name.value] = SourceStats(
            unavailable=True, auth=auth_mode(client.settings, name.value)
        )

    stats = RetrievalStats(
        per_source=per_source,
        deduped_remaining=len(deduped),
        abstracts_present=sum(1 for candidate in capped if candidate.abstract),
        dropped=dropped,
        cost_estimate_usd=round(_cost(adapters), 6),
        duration_s=round(time.monotonic() - started, 3),
    )
    if gap_round:
        # Existing first, so round 1's order and cids are stable and its origins absorb anything
        # the gap queries re-found.
        known_cids = {candidate.cid for candidate in known}
        merged, _ = deduplicate(known + capped)
        additions = [c for c in merged if c.cid not in known_cids]
        pool = [c for c in merged if c.cid in known_cids] + additions
        _emit(on_event, "gap_round", known=len(known), added=len(additions))
    else:
        additions = capped
        pool = capped

    counts = Counts(retrieved=len(raw), deduped=len(pool))

    run_module.write_model(
        Path(run_dir) / "candidates.json", CandidatesFile(run=info, candidates=pool)
    )
    batches = write_batches(run_dir, additions, plan, prefix=prefix)
    _emit(on_event, "batches", count=len(batches))

    return RetrieveResult(
        candidates=pool,
        stats=stats,
        batches=batches,
        counts=counts,
        per_query_hits=per_query_hits,
        added=additions,
    )


def _cost(adapters: dict[SourceName, Source]) -> float:
    return sum(getattr(adapter, "cost_usd", 0.0) for adapter in adapters.values())
