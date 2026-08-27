# SPDX-License-Identifier: Apache-2.0
"""Pydantic v2 data contracts for every file research-scan reads or writes (spec §9).

This module is the source of truth. `research-scan schema` prints the JSON Schema;
`research-scan schema --md` renders `skills/research-scan/references/schemas.md`, which is
what the hosting agent actually reads before writing `queries.json`, `screen.json` or
`ranked.json`. A test asserts the generated file is current.

Every model forbids unknown keys: a typo in an agent-written file has to surface as an
actionable `exit 2`, not as a silently ignored field.
"""

from __future__ import annotations

import enum
import json
import types
from typing import Annotated, Any, Literal, Union, get_args, get_origin

from pydantic import (
    BaseModel,
    ConfigDict,
    Field,
    RootModel,
    StringConstraints,
    ValidationError,
    field_validator,
    model_validator,
)

MONTH_PATTERN = r"^\d{4}-(0[1-9]|1[0-2])$"
CID_PATTERN = r"^[0-9a-f]{12}$"

Month = Annotated[str, StringConstraints(pattern=MONTH_PATTERN)]
Cid = Annotated[str, StringConstraints(pattern=CID_PATTERN)]
# Strict, because the shortlist's first tier reads this number. Lax coercion turned `true` into
# 1 and `"3"` into 3, so a malformed screen file bought a place in the order instead of exiting 2.
Score = Annotated[int, Field(ge=0, le=3, strict=True)]

MAX_QUERY_WORDS = 30
MAX_ROUND2_QUERIES = 8
THIN_CRITERION_HITS = 5
MAX_SCREEN_REASON_WORDS = 20


class Model(BaseModel):
    """Base for every contract: unknown keys are errors, aliases are accepted both ways."""

    model_config = ConfigDict(extra="forbid", populate_by_name=True, str_strip_whitespace=True)


# --------------------------------------------------------------------------- enums


class Domain(enum.StrEnum):
    behavioral = "behavioral"
    cs = "cs"
    biomed = "biomed"
    general = "general"


class QueryType(enum.StrEnum):
    direct = "direct"
    terminology = "terminology"
    mechanism = "mechanism"
    method = "method"
    adjacent = "adjacent"
    contradictory = "contradictory"
    review = "review"
    emerging = "emerging"
    gap = "gap"


class Profile(enum.StrEnum):
    """The cost/recall dial, chosen at `init` and recorded in `manifest.defaults` (v0.2.1)."""

    quick = "quick"
    standard = "standard"
    deep = "deep"


class QueryMode(enum.StrEnum):
    semantic = "semantic"
    keyword = "keyword"


class WorkType(enum.StrEnum):
    article = "article"
    preprint = "preprint"
    review = "review"
    book_chapter = "book-chapter"
    other = "other"


class SourceName(enum.StrEnum):
    openalex = "openalex"
    s2 = "s2"
    arxiv = "arxiv"
    pubmed = "pubmed"


class Relation(enum.StrEnum):
    query = "query"
    references = "references"
    citations = "citations"
    recommendations = "recommendations"
    anchor = "anchor"


class EvidenceLevel(enum.StrEnum):
    systematic_review = "systematic-review"
    meta_analysis = "meta-analysis"
    rct = "rct"
    prospective = "prospective"
    observational = "observational"
    experimental = "experimental"
    computational = "computational"
    qualitative = "qualitative"
    other = "other"


class VerifiedBy(enum.StrEnum):
    crossref = "crossref"
    openalex = "openalex"
    arxiv = "arxiv"
    s2 = "s2"


class Mismatch(enum.StrEnum):
    doi_unresolved = "doi_unresolved"
    title = "title"
    year = "year"
    author = "author"
    retracted = "retracted"
    no_record = "no_record"


class BriefRelation(enum.StrEnum):
    """How a paper stands to the brief — orthogonal to how it was found (`Relation`).

    Any of the first four earns `overall=3`: closely-related high-quality work is not scored down
    for being non-actionable.
    """

    design_changing = "design-changing"
    plan_influencing = "plan-influencing"
    closely_related = "closely-related"
    contradicting = "contradicting"
    foundational = "foundational"


class SelectionReason(enum.StrEnum):
    score = "score"
    foundational = "foundational"
    review = "review"
    contradicting = "contradicting"
    diversity = "diversity"
    backfill = "backfill"


#: Query types a plan must always contain (spec §9.1).
MANDATORY_QUERY_TYPES: tuple[QueryType, ...] = (
    QueryType.direct,
    QueryType.terminology,
    QueryType.contradictory,
    QueryType.review,
)


# --------------------------------------------------------------------------- run scaffolding


class Window(Model):
    """Publication window, inclusive months. `to: null` means "up to today"."""

    from_: Month | None = Field(
        default=None, alias="from", description="Earliest publication month, `YYYY-MM`."
    )
    to: Month | None = Field(
        default=None, description="Latest publication month, or null for today."
    )


class Defaults(Model):
    """Run parameters written by `init`; command flags and `queries.json` may override them."""

    window: Window = Field(default_factory=Window, description="Default 36 months back → today.")
    top: int = Field(default=10, ge=1, description="Papers to emit.")
    foundational: int = Field(
        default=2, ge=0, description="Of `top`, slots reserved for out-of-window classics."
    )
    domain: Domain = Field(
        default=Domain.general, description="Routing domain; the agent resolves `auto` itself."
    )
    sources: list[SourceName] = Field(
        default_factory=lambda: [SourceName.openalex, SourceName.s2],
        description="Sources the routing map selected.",
    )
    profile: Profile = Field(
        default=Profile.standard,
        description="Cost/recall dial: per-query depth, pool cap, out-of-window total, gap round.",
    )


class RunInfo(Model):
    """Identity of one scan. Printed by `init` on stdout and embedded in every file."""

    run_dir: str = Field(
        description="Path to the run directory, e.g. `research/scans/2026-08-18-kickoff`."
    )
    slug: str = Field(description="Short run name.")
    date: str = Field(description="Run creation date, `YYYY-MM-DD`.")
    brief_path: str = Field(description="Path to `brief.md` inside the run directory.")
    defaults: Defaults


# ------------------------------------------------------------------ queries.json (agent → CLI)


class SubCriterion(Model):
    """One decomposed dimension of the brief; screening and reranking both score against these."""

    id: str = Field(description="Stable id, e.g. `C1`.")
    name: str = Field(description="Two or three words, e.g. `population/setting`.")
    text: str = Field(description="What would make a paper satisfy this criterion.")


class Query(Model):
    """One search query aimed at one research community's vocabulary."""

    id: str = Field(description="Stable id, e.g. `Q1`.")
    type: QueryType = Field(description="What this query is reaching for.")
    text: str = Field(
        description=f"The query itself, ≤ {MAX_QUERY_WORDS} words. Exclusions never go here."
    )
    mode: QueryMode = Field(
        default=QueryMode.semantic, description="`keyword` allows Boolean syntax."
    )
    target_criterion: str | None = Field(
        default=None,
        description="Sub-criterion id this query is reaching for. Required on a `gap` query.",
    )

    @field_validator("text")
    @classmethod
    def _bounded_length(cls, value: str) -> str:
        if len(value.split()) > MAX_QUERY_WORDS:
            raise ValueError(f"query text must be at most {MAX_QUERY_WORDS} words")
        return value


class Anchor(Model):
    """A paper the brief already names. Pinned into retrieval and always used as an expansion seed.

    Resolution is by DOI when given, else by near-exact title match — an anchor is a claim about a
    specific paper, so fuzzy-ish matching would pin the wrong one.
    """

    title: str | None = Field(default=None, description="Exact-ish title; matched at ratio ≥ 95.")
    doi: str | None = Field(default=None, description="Preferred: resolves without ambiguity.")

    @model_validator(mode="after")
    def _has_an_identity(self) -> Anchor:
        if not (self.title or self.doi):
            raise ValueError("an anchor needs a title or a doi")
        return self


class QueryPlan(Model):
    """`queries.json` — the plan the agent writes before `retrieve` (spec §9.1, §10.1)."""

    brief_summary: str = Field(
        description="One paragraph restating the project in the agent's words."
    )
    domain: Domain = Field(
        description="Routing domain. Never `auto` — resolve it in the plan step."
    )
    window: Window | None = Field(
        default=None, description="Overrides the run defaults when present."
    )
    sub_criteria: list[SubCriterion] = Field(min_length=3, max_length=6)
    must_not: list[str] = Field(
        default_factory=list,
        description=(
            "Exclusion phrases, enforced in code at word boundaries. Never NOT-terms in query text."
        ),
    )
    queries: list[Query] = Field(min_length=6, max_length=8)
    anchors: list[Anchor] = Field(
        default_factory=list,
        description="Papers the brief already names. Pinned into the pool and always seeded.",
    )
    round2: list[Query] = Field(
        default_factory=list,
        max_length=MAX_ROUND2_QUERIES,
        description=(
            "The gap round: queries written after `coverage`, against thin sub-criteria."
            " Empty until the gap round; `retrieve --round 2` runs these and only these."
        ),
    )

    @model_validator(mode="after")
    def _plan_is_coherent(self) -> QueryPlan:
        query_ids = [query.id for query in self.queries] + [query.id for query in self.round2]
        if len(set(query_ids)) != len(query_ids):
            raise ValueError("query ids must be unique across `queries` and `round2`")

        criterion_ids = [criterion.id for criterion in self.sub_criteria]
        if len(set(criterion_ids)) != len(criterion_ids):
            raise ValueError("sub_criteria ids must be unique")

        present = {query.type for query in self.queries}
        missing = [t.value for t in MANDATORY_QUERY_TYPES if t not in present]
        if missing:
            raise ValueError(f"missing mandatory query types: {', '.join(missing)}")

        if any(query.type is QueryType.gap for query in self.queries):
            raise ValueError("`gap` queries belong in `round2`, not in `queries`")

        known = set(criterion_ids)
        for query in [*self.queries, *self.round2]:
            if query.type is QueryType.gap and not query.target_criterion:
                raise ValueError(f"gap query {query.id} must name a target_criterion")
            if query.target_criterion and query.target_criterion not in known:
                raise ValueError(
                    f"query {query.id} targets unknown criterion {query.target_criterion!r}"
                )
        return self


# --------------------------------------------------------------------------- candidates.json (CLI)


class Author(Model):
    name: str
    s2_id: str | None = None
    openalex_id: str | None = None


class Ids(Model):
    """Every identifier known for a work. `cid` is derived from these in priority order."""

    doi: str | None = Field(default=None, description="Lower-cased, bare (no `https://doi.org/`).")
    arxiv: str | None = Field(default=None, description="Version-stripped, e.g. `2501.10120`.")
    pmid: str | None = None
    openalex: str | None = None
    s2: str | None = None


class Origin(Model):
    """One discovery path that produced a candidate. A paper keeps every origin it earned."""

    source: SourceName
    relation: Relation = Field(description="`query` for search hits; the rest come from expansion.")
    query_id: str | None = Field(default=None, description="Set when `relation` is `query`.")
    seed_id: Cid | None = Field(default=None, description="Set for expansion relations.")
    # Zero-based: every source builds its origins with `enumerate(results)`, so the top hit is
    # rank 0 and `ge=0` is the real floor, not an off-by-one. Strict for the same reason `Score`
    # is — the shortlist's fourth tier reads this, and `true` coerced to rank 1.
    rank: int = Field(ge=0, strict=True, description="Position in that source's result list.")


class Candidate(Model):
    """One deduplicated work. The unit that flows from `retrieve` to `emit`."""

    cid: Cid = Field(
        description=(
            "First 12 hex of `sha1('<kind>:<value>')` for the highest-priority identifier"
            " (doi > arxiv > pmid > normalised title+year). Stable across runs."
        )
    )
    title: str
    abstract: str | None = None
    tldr: str | None = Field(
        default=None, description="Semantic Scholar's one-line summary, when present."
    )
    authors: list[Author] = Field(default_factory=list)
    year: int | None = Field(default=None, description="Null when the source reports no year.")
    publication_date: str | None = Field(default=None, description="`YYYY-MM-DD` when known.")
    venue: str | None = None
    type: WorkType = WorkType.other
    raw_type: str | None = Field(
        default=None,
        description=(
            "The source's own type string, kept because `WorkType` collapses paratext, errata and"
            " datasets into `other` and the §8.3 type filter has to tell them apart."
        ),
    )
    ids: Ids = Field(default_factory=Ids)
    citation_count: int = Field(default=0, ge=0)
    influential_citation_count: int | None = None
    is_retracted: bool = False
    oa_url: str | None = None
    origins: list[Origin] = Field(default_factory=list)
    outside_window: bool = Field(
        default=False, description="True for expansion references published before the window."
    )


class CandidatesFile(Model):
    """`candidates.json` — everything retrieval and expansion found, after dedup and filters."""

    run: RunInfo
    candidates: list[Candidate]


# --------------------------------------------------------------------------- screening


class ScreenBatchItem(Model):
    """One item as the screening agent sees it: trimmed, no ids, no citation counts."""

    cid: Cid
    title: str
    abstract_600: str | None = Field(
        default=None, description="Abstract truncated to 600 characters."
    )
    year: int | None = None
    venue: str | None = None
    origin_count: int = Field(default=0, ge=0, description="How many discovery paths found it.")
    outside_window: bool = False


class ScreenBatch(Model):
    """`screen-batches/NN.json` — one batch of ≤ 25 items (`xNN` for expansion batches)."""

    batch: str = Field(
        description="Batch id: `01` retrieval, `x01` expansion, `r01`/`xr01` the gap round."
    )
    sub_criteria: list[SubCriterion] = Field(description="Copied from `queries.json`.")
    items: list[ScreenBatchItem]


class ScreenScore(Model):
    """0 off-topic · 1 tangential · 2 relevant to ≥ 1 sub-criterion · 3 central."""

    cid: Cid
    score: Score
    reason: str = Field(description=f"At most {MAX_SCREEN_REASON_WORDS} words.")
    criteria_hit: list[str] = Field(
        default_factory=list,
        description=(
            "Sub-criterion ids this paper satisfies. Required on any score ≥ 2; `coverage` counts"
            " them per criterion. Empty on pre-v0.2 files, which count as unattributed."
        ),
    )

    @field_validator("reason")
    @classmethod
    def _bounded_reason(cls, value: str) -> str:
        if len(value.split()) > MAX_SCREEN_REASON_WORDS:
            raise ValueError(f"reason must be at most {MAX_SCREEN_REASON_WORDS} words")
        return value


class ScreenFile(Model):
    """`screen.json` — every cid in `candidates.json` scored exactly once (rewritten in round 2)."""

    scores: list[ScreenScore]


# --------------------------------------------------------------------------- expansion


class ExpansionDropped(Model):
    retracted: int = 0
    must_not: int = 0
    type: int = Field(default=0, description="Paratext, errata and datasets reached via the graph.")
    cap: int = 0


class Expanded(Model):
    """`expanded.json` — what citation-graph expansion added, and what it refused to add."""

    seeds: list[Cid] = Field(description="Candidates that scored ≥ 2 and were used as seeds.")
    added: list[Cid]
    added_outside_window: list[Cid]
    dropped: ExpansionDropped = Field(default_factory=ExpansionDropped)
    batches: list[str] = Field(description="New screening batch ids, e.g. `x01`.")


# --------------------------------------------------------------------------- coverage


class CriterionCoverage(Model):
    """How well one sub-criterion is covered by the papers screening kept."""

    id: str
    name: str
    hits: int = Field(ge=0, description="Candidates scored ≥ 2 whose `criteria_hit` names this id.")
    by_query_type: dict[str, int] = Field(
        default_factory=dict, description="Hits split by the query type that found them."
    )
    by_source: dict[str, int] = Field(
        default_factory=dict, description="Hits split by the source that found them."
    )
    thin: bool = Field(
        description=f"`hits` is below {THIN_CRITERION_HITS}: the gap round targets it."
    )


class QueryYield(Model):
    """What one query actually contributed to the surviving pool."""

    query_id: str
    type: QueryType
    pool: int = Field(ge=0, description="Candidates in the pool carrying an origin from it.")
    ge2: int = Field(ge=0, description="How many of those screened ≥ 2.")


class SeedPrecision(Model):
    """The share of one seed's new neighbours that screening kept."""

    seed_id: Cid
    neighbours: int = Field(ge=0, description="Candidates reached from this seed.")
    ge2: int = Field(ge=0)
    precision: float = Field(ge=0, le=1)


class CoverageRound(Model):
    """One snapshot of the pool: round 1 before the gap round, round 2 after it."""

    round: int = Field(ge=1, le=2)
    screened: int = Field(ge=0)
    ge2: int = Field(ge=0)
    unattributed_ge2: int = Field(
        default=0, ge=0, description="Scored ≥ 2 but with no `criteria_hit` — coverage cannot see."
    )
    criteria: list[CriterionCoverage] = Field(default_factory=list)
    queries: list[QueryYield] = Field(default_factory=list)
    seeds: list[SeedPrecision] = Field(default_factory=list)


class GapRoundAdvice(Model):
    """Whether the gap round is worth its screening cost on this run (v0.2.1).

    Deterministic, like everything else `coverage` writes: the profile decides the policy and three
    fixed thresholds decide the rest. The agent obeys it; `--gap-round` overrides it.
    """

    should_run: bool
    profile: Profile
    forced: bool = Field(default=False, description="`--gap-round` was passed.")
    reasons: list[str] = Field(
        default_factory=list, description="Why, in words, for `coverage_risks`."
    )


class CoverageFile(Model):
    """`coverage.json` — one snapshot per round, so what the gap round recovered is a delta."""

    run: RunInfo
    rounds: list[CoverageRound] = Field(default_factory=list)
    gap_round: GapRoundAdvice | None = Field(
        default=None, description="Recommendation from the latest round's counts."
    )


# --------------------------------------------------------------------------- shortlist


class ScoredCandidate(Candidate):
    """A candidate carrying its screening score."""

    score: Score


class Shortlist(Model):
    """`shortlist.json` — ordered, cut, and ready for the rerank step. Full records, not stubs."""

    in_window: list[ScoredCandidate]
    outside_window: list[ScoredCandidate] = Field(default_factory=list)


# ------------------------------------------------------------------ ranked.json + verification


class RankedFlags(Model):
    review: bool = Field(default=False, description="A review or meta-analysis.")
    contradicts: bool = Field(default=False, description="Contradicts a premise of the brief.")
    methods_paper: bool = Field(
        default=False, description="Contributes a method rather than a finding."
    )


class Verification(Model):
    """Added by `verify` (spec §10.5). Never written by the agent."""

    verified: bool
    verified_by: list[VerifiedBy] = Field(default_factory=list)
    verified_on: str = Field(description="`YYYY-MM-DD`.")
    title_match_ratio: float | None = Field(default=None, ge=0, le=100)
    mismatches: list[Mismatch] = Field(default_factory=list)


class RankedEntry(Model):
    """One reranked paper. The agent writes everything except `verification`."""

    cid: Cid = Field(description="Must already exist in `shortlist.json`.")
    criteria: dict[str, Score] = Field(description="Sub-criterion id → 0–3.")
    overall: Score = Field(description="Holistic 0–3, not an average of `criteria`.")
    evidence_level: EvidenceLevel
    relation: BriefRelation | None = Field(
        default=None,
        description=(
            "How this paper stands to the brief. Required by the rerank rubric going forward;"
            " optional here so pre-S4.5 runs still validate."
        ),
    )
    flags: RankedFlags = Field(default_factory=RankedFlags)
    key_finding: str = Field(
        description="One sentence, with the abstract's numbers when it gives them."
    )
    methodology: str = Field(description="Say `abstract-only` when the abstract is all there is.")
    why_it_matters: str = Field(description="Specific to this project's design decisions.")
    limitations: list[str] = Field(min_length=1)
    relevance_reason: str
    verification: Verification | None = Field(default=None, description="Filled in by `verify`.")


class Ranked(RootModel[list[RankedEntry]]):
    """`ranked.json` — a bare JSON array of RankedEntry."""


# --------------------------------------------------------------------------- evidence


class EvidencePacket(Candidate, RankedEntry):
    """A candidate ⊕ its rerank ⊕ its verification ⊕ why it was selected. The shippable unit."""

    verification: Verification = Field(description="Required here: `emit` exits 2 without it.")
    rank: int = Field(ge=1)
    selection_reason: SelectionReason
    url: str | None = None


class Evidence(Model):
    """`evidence.json` — the deliverable. `emit` never adds a paper that is not ranked."""

    run: RunInfo
    packets: list[EvidencePacket]
    alternates: list[EvidencePacket] = Field(default_factory=list)


# --------------------------------------------------------------------------- manifest


class SourceStats(Model):
    queried: int = Field(default=0, description="Queries sent to this source.")
    hits: int = Field(default=0, description="Raw hits returned, before dedup.")
    failed: int = Field(default=0, description="Queries that failed after retries.")
    unavailable: bool = Field(
        default=False, description="Routed to, but not built in this version (arXiv/PubMed: S6)."
    )
    auth: Literal["key", "anon"] = Field(
        default="anon",
        description="Whether a credential was sent to this source's host, so a 429 is readable.",
    )


class RetrievalDropped(Model):
    retracted: int = 0
    must_not: int = 0
    type: int = 0
    window: int = Field(default=0, description="Slipped past the source-side date filter.")
    preprint: int = Field(default=0, description="Dropped by `--no-include-preprints`.")
    cap: int = 0


class RetrievalStats(Model):
    per_source: dict[str, SourceStats] = Field(default_factory=dict)
    deduped_remaining: int = Field(
        default=0,
        description=(
            "Candidates left immediately after dedup, before the §8.3 filters and the §8.4 cap."
            " `Counts.deduped` is the *post-cap* pool and is usually smaller."
        ),
    )
    abstracts_present: int = Field(
        default=0, description="Candidates carrying an abstract; the S1 gate wants ≥ 80 %."
    )
    dropped: RetrievalDropped = Field(default_factory=RetrievalDropped)
    cost_estimate_usd: float = Field(default=0.0, description="OpenAlex reports this per call.")
    duration_s: float = 0.0


class ExpansionStats(Model):
    seeds: int = 0
    added: int = 0
    added_outside_window: int = 0
    dropped: ExpansionDropped = Field(default_factory=ExpansionDropped)
    auth: dict[str, Literal["key", "anon"]] = Field(
        default_factory=dict,
        description="Auth mode per graph source, same contract as SourceStats.auth.",
    )
    duration_s: float = 0.0


class VerificationStats(Model):
    verified: int = 0
    unverified: int = 0
    dropped_retracted: int = 0
    crossref_skipped: bool = Field(default=False, description="Set once if Crossref 403/429'd.")
    duration_s: float = 0.0


class EmitStats(Model):
    top: int = 0
    foundational: int = 0
    contradicting: int = Field(
        default=1,
        description="Counter-result slots asked for, before the half-of-top cap.",
    )
    emitted: int = 0
    alternates: int = 0
    dropped_retracted: int = 0
    duration_s: float = 0.0


class Counts(Model):
    """The one-line audit trail printed in the ScanSummary."""

    retrieved: int = 0
    deduped: int = Field(
        default=0,
        description=(
            "Candidates remaining after dedup, filters and the cap — i.e. what is in"
            " `candidates.json`. See `RetrievalStats.deduped_remaining` for the post-dedup count;"
            " when the cap binds the two differ a lot (measured: 600 raw → 543 deduped → 28)."
        ),
    )
    expanded: int = 0
    screened_ge2: int = 0
    shortlisted: int = 0
    ranked: int = 0
    verified: int = 0
    emitted: int = 0
    wall_clock_s: float | None = Field(
        default=None,
        description="init.started_at → emit.finished_at. Set by `emit`; null until then.",
    )


class Manifest(Model):
    """`manifest.json` — CLI-owned. Each command upserts its own section; nothing is silent."""

    run: RunInfo
    defaults: Defaults
    retrieval: RetrievalStats | None = None
    retrieval_round2: RetrievalStats | None = Field(
        default=None, description="The gap round's retrieval. Round 1's section is never replaced."
    )
    expansion: ExpansionStats | None = None
    expansion_round2: ExpansionStats | None = Field(
        default=None, description="The gap round's expansion."
    )
    verification: VerificationStats | None = None
    emit: EmitStats | None = None
    counts: Counts = Field(default_factory=Counts)
    tool_version: str
    timestamps: dict[str, str] = Field(
        default_factory=dict, description="Stage name → ISO timestamp."
    )


# --------------------------------------------------------------------------- returned to the caller


MAX_WHY_WORDS = 30


class SummaryPaper(Model):
    rank: int = Field(ge=1)
    title: str
    year: int | None = None
    doi: str | None = None
    url: str | None = Field(
        default=None,
        description=(
            "Copied verbatim from the packet's `url`. `select.canonical_url` is the only place that"
            " decides what a paper's link is; nothing downstream re-derives it."
        ),
    )
    evidence_level: EvidenceLevel
    verified: bool
    why: str = Field(
        description=f"≤ {MAX_WHY_WORDS} words: the relation plus one line on why it made the cut."
    )

    @field_validator("why")
    @classmethod
    def _bounded_why(cls, value: str) -> str:
        if len(value.split()) > MAX_WHY_WORDS:
            raise ValueError(f"why must be at most {MAX_WHY_WORDS} words")
        return value


class UnverifiedPaper(Model):
    title: str
    mismatches: list[Mismatch]


class ScanSummary(Model):
    """The skill's return value, and the `--json-schema` for headless runs (spec §9.10)."""

    run_dir: str
    evidence_json: str
    top: list[SummaryPaper]
    counts: Counts
    unverified: list[UnverifiedPaper] = Field(default_factory=list)
    coverage_risks: str = Field(
        description="Thin queries, failed sources, expansion that found nothing."
    )


# --------------------------------------------------------------------------- eval


class EvalMiss(Model):
    doi: str
    why: str = Field(description="Terminology gap, source gap, or out of window.")


class JudgeScore(Model):
    rank: int = Field(ge=1)
    cid: Cid | None = None
    score: Score
    reason: str | None = Field(
        default=None, description="One line. A score with no reason is unauditable."
    )


class JudgeSummary(Model):
    """The judge's verdict, split by what each packet was selected to do.

    `precision_ge2` is the raw share over every judged packet. It is not the acceptance number:
    `emit` reserves the last slots for out-of-window classics, and the judge scores those on the
    same "does this inform a decision the brief names" scale, which a classic cannot win. Reporting
    only the raw share measures the emit policy rather than the reranker, so both numbers ship.
    """

    precision_ge2: float | None = Field(
        default=None,
        ge=0,
        le=1,
        description="Share of all judged packets scoring ≥ 2, foundational slots included.",
    )
    precision_ge2_in_window: float | None = Field(
        default=None,
        ge=0,
        le=1,
        description=(
            "Share of judged packets whose `selection_reason` is not `foundational` — the §14.6"
            " acceptance number. Null when the evidence was not available to partition by."
        ),
    )
    per_rank: list[JudgeScore] = Field(default_factory=list)
    foundational: list[JudgeScore] = Field(
        default_factory=list,
        description="The judged foundational packets, held out of `precision_ge2_in_window`.",
    )


class JudgeFile(Model):
    """What `eval/judge.sh` writes and `eval --judge` reads (spec §13).

    Produced by a different, stronger model than the one that wrote `ranked.json` (canon §3) — the
    judge must not share the reranker's priors, or the score correlates with nothing.
    """

    run_dir: str | None = None
    judge_model: str | None = Field(default=None, description="Recorded so a run can be audited.")
    scores: list[JudgeScore]


class GoldenPaper(Model):
    """One paper you would be surprised a scan missed (spec §13)."""

    doi: str = Field(description="Primary DOI, lower-cased and bare.")
    arxiv: str | None = Field(default=None, description="Set when the paper is arXiv-native.")
    title: str | None = Field(
        default=None,
        description="Enables the fuzzy-title fallback when no identifier is shared.",
    )
    aliases: list[str] = Field(
        default_factory=list,
        description=(
            "Other identifiers under which a run may legitimately surface this work — a preprint"
            " or working-paper DOI, or a known-bad upstream link. Each one counts as a match."
        ),
    )
    why: str = Field(description="Why missing this one would be a real failure.")
    found_in_s3e2e: bool | None = Field(
        default=None,
        description="Whether the run this set was drafted against found it; keeps bias visible.",
    )

    def identifiers(self) -> set[str]:
        """Every identifier that should count as finding this paper."""
        found = {self.doi.strip().lower()}
        found.update(item.strip().lower() for item in self.aliases if item.strip())
        if self.arxiv:
            found.add(self.arxiv.strip().lower())
        return found


class GoldenTopic(Model):
    """`eval/golden/<topic>.yaml` — the curated set a scan is scored against (spec §13).

    `status` stays `draft` until the maintainer has ratified every expected DOI. Nothing else
    may set it.
    """

    topic: str
    status: Literal["draft", "ratified-with-caveat", "ratified"] = Field(
        default="draft",
        description=(
            "Only the maintainer promotes a topic. `ratified-with-caveat` means read `notes` first."
        ),
    )
    brief: str = Field(description="The brief a scan of this topic should be run from.")
    window: Window = Field(default_factory=Window)
    domain: Domain = Domain.general
    exclusions: list[str] = Field(
        default_factory=list, description="Feeds `queries.json.must_not`."
    )
    expected: list[GoldenPaper] = Field(min_length=1)
    notes: str | None = None


class CandidateHit(Model):
    """One expected paper checked against `candidates.json` alone (spec §13, S10e)."""

    doi: str = Field(description="The golden entry's primary DOI, as written.")
    title: str | None = Field(default=None, description="The golden entry's title, if it has one.")
    present: bool = Field(description="Whether retrieval or expansion put this paper in the pool.")
    cid: Cid | None = Field(default=None, description="The candidate it matched, when present.")
    matched_by: Literal["doi", "alias", "arxiv", "title"] | None = Field(
        default=None,
        description="Which identifier connected them — `alias` means only the published DOI did.",
    )
    origins: list[str] = Field(
        default_factory=list,
        description="`source:relation:query-or-seed:rank` per origin, so a miss names its stage.",
    )
    screen_score: int | None = Field(
        default=None, description="Its screen.json score; null when the run has not screened yet."
    )


class CandidatesRecall(Model):
    """Recall measured at the candidate pool — retrieval quality with the agent stages removed."""

    expected: int = Field(ge=0)
    found: int = Field(ge=0)
    recall: float = Field(ge=0, le=1)
    screened: bool = Field(
        default=False, description="Whether screen.json was present to read scores from."
    )
    papers: list[CandidateHit] = Field(default_factory=list)


class EvalResult(Model):
    """`eval/results/<date>-<topic>.json` (spec §9.11, §13)."""

    topic: str
    run_dir: str
    expected: int = Field(ge=0)
    found_at_10: int = Field(ge=0)
    found_at_25: int = Field(ge=0)
    recall_10: float = Field(ge=0, le=1)
    recall_25: float = Field(ge=0, le=1)
    profile: Profile | None = Field(
        default=None, description="The run's cost/recall profile, from `manifest.defaults`."
    )
    pool_size: int | None = Field(
        default=None, ge=0, description="Candidates the agent had to screen."
    )
    wall_clock_s: float | None = Field(default=None, ge=0, description="From `counts`.")
    recall_per_100_screened: float | None = Field(
        default=None,
        ge=0,
        description="Recall bought per 100 screened candidates: the cost side of a gate row.",
    )
    misses: list[EvalMiss] = Field(default_factory=list)
    judged: JudgeSummary | None = None
    candidates: CandidatesRecall | None = Field(
        default=None, description="Set by `--stage candidates`; null for a full scoring run."
    )


# --------------------------------------------------------------------------- registry + rendering

#: Public model registry. Order is the order of `schema --md`, and is part of the contract.
MODELS: dict[str, type[BaseModel]] = {
    "RunInfo": RunInfo,
    "Defaults": Defaults,
    "Window": Window,
    "QueryPlan": QueryPlan,
    "SubCriterion": SubCriterion,
    "Query": Query,
    "Anchor": Anchor,
    "CandidatesFile": CandidatesFile,
    "Candidate": Candidate,
    "Author": Author,
    "Ids": Ids,
    "Origin": Origin,
    "ScreenBatch": ScreenBatch,
    "ScreenBatchItem": ScreenBatchItem,
    "ScreenFile": ScreenFile,
    "ScreenScore": ScreenScore,
    "Expanded": Expanded,
    "ExpansionDropped": ExpansionDropped,
    "CoverageFile": CoverageFile,
    "CoverageRound": CoverageRound,
    "GapRoundAdvice": GapRoundAdvice,
    "CriterionCoverage": CriterionCoverage,
    "QueryYield": QueryYield,
    "SeedPrecision": SeedPrecision,
    "Shortlist": Shortlist,
    "ScoredCandidate": ScoredCandidate,
    "Ranked": Ranked,
    "RankedEntry": RankedEntry,
    "RankedFlags": RankedFlags,
    "Verification": Verification,
    "Evidence": Evidence,
    "EvidencePacket": EvidencePacket,
    "Manifest": Manifest,
    "Counts": Counts,
    "RetrievalStats": RetrievalStats,
    "RetrievalDropped": RetrievalDropped,
    "SourceStats": SourceStats,
    "ExpansionStats": ExpansionStats,
    "VerificationStats": VerificationStats,
    "EmitStats": EmitStats,
    "ScanSummary": ScanSummary,
    "SummaryPaper": SummaryPaper,
    "UnverifiedPaper": UnverifiedPaper,
    "CandidateHit": CandidateHit,
    "CandidatesRecall": CandidatesRecall,
    "EvalResult": EvalResult,
    "EvalMiss": EvalMiss,
    "JudgeSummary": JudgeSummary,
    "JudgeScore": JudgeScore,
    "JudgeFile": JudgeFile,
    "GoldenTopic": GoldenTopic,
    "GoldenPaper": GoldenPaper,
}

#: Grouping used by `schema --md`. Every registry name appears exactly once.
SECTIONS: tuple[tuple[str, str, tuple[str, ...]], ...] = (
    (
        "Run scaffolding",
        "Written by `init`, embedded everywhere else.",
        ("RunInfo", "Defaults", "Window"),
    ),
    (
        "queries.json — agent writes",
        "The plan step's output. Read `references/plan-rubric.md` before writing this.",
        ("QueryPlan", "SubCriterion", "Query", "Anchor"),
    ),
    (
        "candidates.json — CLI writes",
        "Everything retrieval and expansion found, after dedup and filters.",
        ("CandidatesFile", "Candidate", "Author", "Ids", "Origin"),
    ),
    (
        "screen-batches/ and screen.json",
        "The CLI writes the batches; the agent writes the scores.",
        ("ScreenBatch", "ScreenBatchItem", "ScreenFile", "ScreenScore"),
    ),
    (
        "expanded.json and shortlist.json — CLI writes",
        "Citation-graph expansion, then the ordered cut handed to the rerank step.",
        ("Expanded", "ExpansionDropped", "Shortlist", "ScoredCandidate"),
    ),
    (
        "coverage.json — CLI writes",
        "Deterministic coverage of the sub-criteria. What the gap round is aimed at.",
        (
            "CoverageFile",
            "CoverageRound",
            "GapRoundAdvice",
            "CriterionCoverage",
            "QueryYield",
            "SeedPrecision",
        ),
    ),
    (
        "ranked.json — agent writes, CLI adds verification",
        "Read `references/rerank-rubric.md`. Never introduce a cid absent from `shortlist.json`.",
        ("Ranked", "RankedEntry", "RankedFlags", "Verification"),
    ),
    (
        "evidence.json — CLI writes",
        "The deliverable. `emit` applies the selection rules; it never adds a paper.",
        ("Evidence", "EvidencePacket"),
    ),
    (
        "manifest.json — CLI writes",
        "One section per command. Caps and drops are recorded, never silent.",
        (
            "Manifest",
            "Counts",
            "RetrievalStats",
            "RetrievalDropped",
            "SourceStats",
            "ExpansionStats",
            "VerificationStats",
            "EmitStats",
        ),
    ),
    (
        "ScanSummary — the skill's return value",
        "Also the `--json-schema` for `claude -p` runs.",
        ("ScanSummary", "SummaryPaper", "UnverifiedPaper"),
    ),
    (
        "EvalResult",
        "Golden-set recall plus merged judge scores.",
        (
            "EvalResult",
            "EvalMiss",
            "CandidatesRecall",
            "CandidateHit",
            "JudgeSummary",
            "JudgeScore",
        ),
    ),
    (
        "Eval inputs",
        "The curated topic file and the independent judge's output.",
        ("GoldenTopic", "GoldenPaper", "JudgeFile"),
    ),
)

_PRIMITIVES: dict[type, str] = {
    str: "string",
    int: "integer",
    float: "number",
    bool: "boolean",
    dict: "object",
    list: "array",
    Any: "any",
}


def format_errors(error: ValidationError, *, path: str | None = None) -> list[str]:
    """Turn a ValidationError into the actionable lines an agent can repair a file from."""
    lines: list[str] = []
    for item in error.errors():
        location = ".".join(str(part) for part in item["loc"]) or "(root)"
        prefix = f"{path}: " if path else ""
        lines.append(f"{prefix}{location}: {item['msg']}")
    return lines


def json_schema(name: str) -> dict[str, Any]:
    """JSON Schema for one registered model. Raises KeyError for an unknown name."""
    return MODELS[name].model_json_schema(by_alias=True)


def all_schemas() -> dict[str, dict[str, Any]]:
    return {name: json_schema(name) for name in MODELS}


def markdown() -> str:
    """Render `references/schemas.md`. Deterministic — a test compares it to the file on disk."""
    lines: list[str] = [
        "# research-scan data contracts",
        "",
        "Generated by `research-scan schema --md`. Do not edit by hand.",
        "",
        "Unknown keys are rejected everywhere: a typo in an agent-written file surfaces as"
        " `exit 2` with the offending path, not as a silently dropped field.",
        "",
    ]
    for title, blurb, names in SECTIONS:
        lines += [f"## {title}", "", blurb, ""]
        for name in names:
            lines += _render_model(name, MODELS[name])
    return "\n".join(lines).rstrip() + "\n"


def _render_model(name: str, model: type[BaseModel]) -> list[str]:
    lines = [f"### {name}", ""]
    doc = (model.__doc__ or "").strip().split("\n\n")[0]
    if doc:
        lines += [" ".join(doc.split()), ""]

    if issubclass(model, RootModel):
        root = model.model_fields["root"]
        lines += [f"Root type: {_type_name(root.annotation)}.", ""]
        return lines

    lines += ["| Field | Type | Required | Default | Notes |", "|---|---|---|---|---|"]
    for field_name, field in model.model_fields.items():
        wire_name = field.alias or field_name
        required = "yes" if field.is_required() else "no"
        lines.append(
            f"| `{wire_name}` | {_type_name(field.annotation)} | {required} |"
            f" {_default(field)} | {_notes(field)} |"
        )
    lines.append("")
    return lines


def _escape(text: str) -> str:
    """A literal pipe inside a table cell ends the cell, even within a code span."""
    return text.replace("|", "\\|")


def _default(field: Any) -> str:
    if field.is_required():
        return "—"
    if field.default_factory is not None:
        return _factory_default(field.default_factory)
    default = field.default
    if default is None:
        return "`null`"
    if isinstance(default, enum.Enum):
        return f"`{default.value}`"
    return f"`{json.dumps(default)}`"


def _factory_default(factory: Any) -> str:
    try:
        produced = factory()
    except TypeError:  # pydantic passes validated data to some factories
        return "empty"
    if isinstance(produced, BaseModel):
        return "all defaults"
    if produced == [] or produced == {}:
        return "empty"
    if isinstance(produced, list):
        values = [item.value if isinstance(item, enum.Enum) else item for item in produced]
        return f"`{_escape(json.dumps(values))}`"
    return "empty"


def _notes(field: Any) -> str:
    parts: list[str] = []
    if field.description:
        parts.append(_escape(field.description))
    constraint = _metadata_note(field.metadata)
    if constraint:
        parts.append(constraint)
    return " ".join(parts) or "—"


def _metadata_note(metadata: Any) -> str:
    notes: list[str] = []
    for item in metadata:
        # A nested `Field(...)` (e.g. Score inside dict[str, Score]) carries its own metadata list.
        nested = getattr(item, "metadata", None)
        if nested:
            notes.append(_metadata_note(nested))
        pattern = getattr(item, "pattern", None)
        if pattern:
            notes.append(f"pattern `{_escape(pattern)}`")
        for attribute, label in (
            ("ge", "≥"),
            ("le", "≤"),
            ("gt", ">"),
            ("lt", "<"),
            ("min_length", "min length"),
            ("max_length", "max length"),
        ):
            value = getattr(item, attribute, None)
            if value is not None:
                notes.append(f"{label} {value}")
    return ", ".join(note for note in notes if note)


def _type_name(annotation: Any) -> str:
    if annotation is None or annotation is type(None):
        return "null"
    if hasattr(annotation, "__metadata__"):
        base = _type_name(get_args(annotation)[0])
        note = _metadata_note(annotation.__metadata__)
        return f"{base} ({note})" if note else base

    origin = get_origin(annotation)
    if origin is Literal:
        return " · ".join(f"`{json.dumps(arg)}`" for arg in get_args(annotation))
    if origin in (Union, types.UnionType):
        parts = [_type_name(arg) for arg in get_args(annotation)]
        return " or ".join(dict.fromkeys(parts))
    if origin in (list, set, frozenset, tuple):
        inner = ", ".join(_type_name(arg) for arg in get_args(annotation) if arg is not Ellipsis)
        return f"array of {inner}" if inner else "array"
    if origin is dict:
        key, value = get_args(annotation)
        return f"object ({_type_name(key)} → {_type_name(value)})"

    if isinstance(annotation, type):
        if issubclass(annotation, enum.Enum):
            return " · ".join(f"`{member.value}`" for member in annotation)
        if issubclass(annotation, BaseModel):
            return f"[{annotation.__name__}](#{annotation.__name__.lower()})"
        return _PRIMITIVES.get(annotation, annotation.__name__)
    return _PRIMITIVES.get(annotation, str(annotation))
