# SPDX-License-Identifier: Apache-2.0
"""Verification against the live record (spec §10.5) — the anti-hallucination contract.

Nothing reaches `evidence.json` on the strength of a model having written it down. Every ranked
entry is checked against Crossref and OpenAlex: the DOI must resolve, the title must match, the
year must be within one, the first author's surname must agree. A failure does not delete the
paper — it marks it, and `evidence.md` prints `[UNVERIFIED — check manually]`. The one exception is
retraction, which is fatal: `emit` drops those (§10.4).

Metadata is never "repaired" from the live record either. A mismatch is a fact about our data
worth showing a human, not something to quietly overwrite.
"""

from __future__ import annotations

import logging
import time
from collections.abc import Callable
from dataclasses import dataclass, field
from datetime import date

from research_scan.dedup import (
    arxiv_id_from_doi,
    first_author_surname,
    is_arxiv_doi,
    normalise_arxiv,
    surname,
    title_similarity,
)
from research_scan.schema import (
    Candidate,
    Mismatch,
    RankedEntry,
    Verification,
    VerificationStats,
    VerifiedBy,
)
from research_scan.sources.base import SourceQueryError
from research_scan.sources.crossref import CrossrefRecord, CrossrefSource, CrossrefUnavailable

log = logging.getLogger(__name__)

DEFAULT_TITLE_RATIO = 90
STRICT_TITLE_RATIO = 95
YEAR_TOLERANCE = 1


@dataclass
class VerifyOptions:
    strict: bool = False
    cache: bool | None = None

    @property
    def title_ratio(self) -> int:
        return STRICT_TITLE_RATIO if self.strict else DEFAULT_TITLE_RATIO


@dataclass
class VerifyResult:
    entries: list[RankedEntry]
    stats: VerificationStats
    unverified: list[tuple[str, list[Mismatch]]] = field(default_factory=list)


def title_ratio(left: str, right: str) -> float:
    return title_similarity(left, right)


def verify_entry(
    candidate: Candidate,
    *,
    crossref: CrossrefRecord | None,
    crossref_attempted: bool,
    openalex: dict | None,
    ratio: int,
    today: date,
    s2_retracted: bool = False,
) -> Verification:
    """Compare one candidate against whatever the live records said (§10.5)."""
    mismatches: list[Mismatch] = []
    verified_by: list[VerifiedBy] = []
    best_ratio: float | None = None

    if crossref is not None:
        verified_by.append(VerifiedBy.crossref)
        best_ratio = title_ratio(candidate.title, crossref.title)
        if best_ratio < ratio:
            mismatches.append(Mismatch.title)
        if not _year_agrees(candidate.year, crossref.year):
            mismatches.append(Mismatch.year)
        if not _author_agrees(candidate, crossref.first_author_surname):
            mismatches.append(Mismatch.author)
        if crossref.retracted:
            mismatches.append(Mismatch.retracted)
    elif crossref_attempted and candidate.ids.doi:
        mismatches.append(Mismatch.doi_unresolved)

    if openalex is not None:
        verified_by.append(VerifiedBy.openalex)
        oa_title = openalex.get("title") or openalex.get("display_name") or ""
        if oa_title:
            oa_ratio = title_ratio(candidate.title, oa_title)
            best_ratio = oa_ratio if best_ratio is None else max(best_ratio, oa_ratio)
            if oa_ratio < ratio and Mismatch.title not in mismatches and crossref is None:
                mismatches.append(Mismatch.title)
        if openalex.get("is_retracted") and Mismatch.retracted not in mismatches:
            mismatches.append(Mismatch.retracted)
    if s2_retracted and Mismatch.retracted not in mismatches:
        # Supplementary signal from S2 publicationTypes. It never joins verified_by — it says
        # something about the paper's status, nothing about whether we have the right paper.
        mismatches.append(Mismatch.retracted)
        if crossref is None and not _year_agrees(candidate.year, openalex.get("publication_year")):
            mismatches.append(Mismatch.year)

    # An arXiv DOI is DataCite-registered, so Crossref was never asked. OpenAlex is the live record
    # that decides `verified`; the arXiv id only corroborates, and only when a second source
    # independently supplied one that agrees — that is the guard against an OpenAlex mis-merge.
    embedded = arxiv_id_from_doi(candidate.ids.doi)
    if embedded is not None:
        ours = normalise_arxiv(candidate.ids.arxiv)
        if ours is None:
            pass  # nothing independent to cross-check against; OpenAlex stands alone
        elif ours == embedded:
            verified_by.append(VerifiedBy.arxiv)
        else:
            log.warning(
                "arXiv id disagreement for %s: record says %s, DOI says %s",
                candidate.cid,
                ours,
                embedded,
            )

    # An arXiv-only record has no DOI to resolve; its S2 identity is what stands in (§10.5).
    if crossref is None and openalex is None:
        if candidate.ids.arxiv and embedded is None:
            verified_by.append(VerifiedBy.arxiv)
            if candidate.ids.s2:
                verified_by.append(VerifiedBy.s2)
        elif not verified_by:
            mismatches.append(Mismatch.no_record)

    return Verification(
        verified=bool(verified_by) and not mismatches,
        verified_by=verified_by,
        verified_on=today.isoformat(),
        title_match_ratio=round(best_ratio, 1) if best_ratio is not None else None,
        mismatches=mismatches,
    )


def _year_agrees(ours: int | None, theirs: int | None) -> bool:
    if ours is None or theirs is None:
        return True  # nothing to disagree about; not evidence of a wrong paper
    return abs(ours - theirs) <= YEAR_TOLERANCE


def _author_agrees(candidate: Candidate, theirs: str) -> bool:
    ours = first_author_surname(candidate)
    if not ours or not theirs:
        return True
    return ours == surname(theirs)


def run_verify(
    entries: list[RankedEntry],
    candidates: dict[str, Candidate],
    crossref_source: CrossrefSource,
    openalex_source: object,
    s2_source: object | None = None,
    *,
    options: VerifyOptions,
    today: date | None = None,
    on_event: Callable[..., None] | None = None,
) -> VerifyResult:
    """Verify every ranked entry, in order, against the live record."""
    started = time.monotonic()
    today = today or date.today()
    crossref_available = True
    crossref_skipped = False
    verified_entries: list[RankedEntry] = []
    unverified: list[tuple[str, list[Mismatch]]] = []

    for entry in entries:
        candidate = candidates.get(entry.cid)
        if candidate is None:
            # shortlist/emit both reject unknown cids; belt and braces so verify cannot crash.
            verification = Verification(
                verified=False,
                verified_on=today.isoformat(),
                mismatches=[Mismatch.no_record],
            )
            verified_entries.append(entry.model_copy(update={"verification": verification}))
            continue

        crossref_record: CrossrefRecord | None = None
        crossref_attempted = False
        # arXiv DOIs are DataCite-registered: Crossref 404s on every one of them, and reading that
        # as `doi_unresolved` marked genuinely fine papers unverified. Don't ask.
        if candidate.ids.doi and crossref_available and not is_arxiv_doi(candidate.ids.doi):
            crossref_attempted = True
            try:
                crossref_record = crossref_source.lookup(candidate.ids.doi, cache=options.cache)
            except CrossrefUnavailable as exc:
                # §10.5: one refusal ends Crossref for the whole run; OpenAlex carries verification.
                crossref_available = False
                crossref_skipped = True
                crossref_attempted = False
                log.warning("crossref unavailable (%s) — verifying via OpenAlex for the rest", exc)
                _emit(on_event, "crossref_skipped", reason=str(exc))
            except SourceQueryError as exc:
                log.warning("crossref lookup failed for %s: %s", candidate.ids.doi, exc)
        elif not candidate.ids.doi and not candidate.ids.arxiv and crossref_available:
            # No DOI at all: try to *identify* the record via bibliographic search (S4.5). The
            # acceptance gate lives in the source: title ratio ≥ 95 and year ±1, or nothing —
            # verified live, the search happily returns same-author-different-paper items.
            try:
                crossref_record = crossref_source.search_bibliographic(
                    candidate.title,
                    first_author_surname(candidate) or None,
                    candidate.year,
                    cache=options.cache,
                )
                if crossref_record is not None:
                    log.info(
                        "bibliographic search identified %s as %s",
                        entry.cid,
                        crossref_record.doi,
                    )
                    _emit(
                        on_event,
                        "bibliographic_match",
                        cid=entry.cid,
                        doi=crossref_record.doi,
                    )
            except CrossrefUnavailable as exc:
                crossref_available = False
                crossref_skipped = True
                log.warning("crossref unavailable (%s) — verifying via OpenAlex for the rest", exc)
                _emit(on_event, "crossref_skipped", reason=str(exc))
            except SourceQueryError as exc:
                log.warning("bibliographic search failed for %s: %s", entry.cid, exc)

        openalex_record: dict | None = None
        try:
            openalex_record = openalex_source.lookup(
                doi=candidate.ids.doi, openalex_id=candidate.ids.openalex, cache=options.cache
            )
        except SourceQueryError as exc:
            log.warning("openalex lookup failed for %s: %s", entry.cid, exc)

        s2_retracted = False
        if s2_source is not None and candidate.ids.s2:
            try:
                types = s2_source.lookup_publication_types(candidate.ids.s2, cache=options.cache)
                s2_retracted = "Retracted" in types
            except SourceQueryError as exc:
                log.warning("s2 publicationTypes lookup failed for %s: %s", entry.cid, exc)

        verification = verify_entry(
            candidate,
            crossref=crossref_record,
            crossref_attempted=crossref_attempted,
            openalex=openalex_record,
            ratio=options.title_ratio,
            today=today,
            s2_retracted=s2_retracted or candidate.is_retracted,
        )
        verified_entries.append(entry.model_copy(update={"verification": verification}))
        if not verification.verified:
            unverified.append((candidate.title, verification.mismatches))
        _emit(
            on_event,
            "verified",
            cid=entry.cid,
            ok=verification.verified,
            by=[item.value for item in verification.verified_by],
            mismatches=[item.value for item in verification.mismatches],
        )

    stats = VerificationStats(
        verified=sum(1 for entry in verified_entries if entry.verification.verified),
        unverified=len(unverified),
        dropped_retracted=sum(
            1 for entry in verified_entries if Mismatch.retracted in entry.verification.mismatches
        ),
        crossref_skipped=crossref_skipped,
        duration_s=round(time.monotonic() - started, 3),
    )
    return VerifyResult(entries=verified_entries, stats=stats, unverified=unverified)


def _emit(on_event: Callable[..., None] | None, event: str, **fields: object) -> None:
    if on_event is not None:
        on_event(event, **fields)
