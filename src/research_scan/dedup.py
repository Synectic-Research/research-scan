# SPDX-License-Identifier: Apache-2.0
"""Identifier normalisation, `cid` derivation, and merging (spec §8.2).

The same paper reaches us from OpenAlex and Semantic Scholar with different identifier
formatting, a different abstract, and a different citation count. Everything downstream joins on
`cid`, so this module has one job: make the same paper produce the same `cid` every run, and merge
the two records without losing what either one knew.

Matching is exact-identifier first (DOI, then arXiv, then PMID). Only when no identifier matches do
we fall back to fuzzy titles — and then only with a corroborating signal, because "Attention Is All
You Need" is a title several unrelated papers have flirted with.
"""

from __future__ import annotations

import hashlib
import re
import unicodedata
from dataclasses import dataclass, field

from rapidfuzz import fuzz

from research_scan.schema import Candidate, Ids, Origin, WorkType

#: rapidfuzz ratio on normalised titles, above which two records are the same paper (§8.2).
TITLE_MATCH_RATIO = 92

_DOI_PREFIXES = (
    "https://doi.org/",
    "http://doi.org/",
    "https://dx.doi.org/",
    "http://dx.doi.org/",
    "doi:",
)
_ARXIV_PREFIXES = ("arxiv:", "arxiv.org/abs/", "https://arxiv.org/abs/", "http://arxiv.org/abs/")
_ARXIV_VERSION = re.compile(r"v\d+$")
_PUNCTUATION = re.compile(r"[^\w\s]", re.UNICODE)
_WHITESPACE = re.compile(r"\s+")


def normalise_doi(value: str | None) -> str | None:
    """`https://doi.org/10.1257/AER.20210881` → `10.1257/aer.20210881`."""
    if not value:
        return None
    text = value.strip()
    lowered = text.lower()
    for prefix in _DOI_PREFIXES:
        if lowered.startswith(prefix):
            text = text[len(prefix) :]
            break
    text = text.strip().lower()
    return text or None


def normalise_arxiv(value: str | None) -> str | None:
    """`arXiv:2501.10120v2` → `2501.10120`. Versions are noise for identity."""
    if not value:
        return None
    text = value.strip()
    lowered = text.lower()
    for prefix in _ARXIV_PREFIXES:
        if lowered.startswith(prefix):
            text = text[len(prefix) :]
            break
    text = _ARXIV_VERSION.sub("", text.strip().lower())
    return text or None


#: arXiv registers its DOIs with DataCite, not Crossref, so `10.48550/...` never resolves there.
ARXIV_DOI_PREFIX = "10.48550/arxiv."


def arxiv_id_from_doi(value: str | None) -> str | None:
    """`10.48550/arXiv.2310.00340` → `2310.00340`. None for any other DOI."""
    if not value:
        return None
    text = normalise_doi(value) or ""
    if not text.startswith(ARXIV_DOI_PREFIX):
        return None
    return normalise_arxiv(text[len(ARXIV_DOI_PREFIX) :])


def is_arxiv_doi(value: str | None) -> bool:
    return arxiv_id_from_doi(value) is not None


def normalise_pmid(value: str | None) -> str | None:
    """`https://pubmed.ncbi.nlm.nih.gov/37993839` → `37993839`."""
    if not value:
        return None
    text = value.strip().rstrip("/")
    if "/" in text:
        text = text.rsplit("/", 1)[-1]
    return text or None


def normalise_title(value: str | None) -> str:
    """Casefold, strip accents and punctuation, collapse whitespace. Used for matching only."""
    if not value:
        return ""
    decomposed = unicodedata.normalize("NFKD", value)
    stripped = "".join(char for char in decomposed if not unicodedata.combining(char))
    return _WHITESPACE.sub(" ", _PUNCTUATION.sub(" ", stripped.casefold())).strip()


def title_similarity(left: str | None, right: str | None) -> float:
    """rapidfuzz ratio over normalised titles. 0 when either side is missing."""
    if not left or not right:
        return 0.0
    return fuzz.ratio(normalise_title(left), normalise_title(right))


def normalise_ids(ids: Ids) -> Ids:
    return Ids(
        doi=normalise_doi(ids.doi),
        arxiv=normalise_arxiv(ids.arxiv),
        pmid=normalise_pmid(ids.pmid),
        openalex=ids.openalex,
        s2=ids.s2,
    )


def surname(name: str | None) -> str:
    """Last whitespace-separated token, normalised. Good enough for a corroborating signal."""
    if not name:
        return ""
    parts = normalise_title(name).split()
    return parts[-1] if parts else ""


def first_author_surname(candidate: Candidate) -> str:
    return surname(candidate.authors[0].name) if candidate.authors else ""


def primary_id(candidate: Candidate) -> tuple[str, str]:
    """The identifier that defines this paper's `cid`, in the §8.2 priority order."""
    ids = candidate.ids
    if ids.doi:
        return "doi", ids.doi
    if ids.arxiv:
        return "arxiv", ids.arxiv
    if ids.pmid:
        return "pmid", ids.pmid
    year = candidate.year if candidate.year is not None else ""
    return "title", f"{normalise_title(candidate.title)}|{year}"


def derive_cid(candidate: Candidate) -> str:
    """First 12 hex of sha1 of `<kind>:<value>`.

    The kind is part of the hashed string so a DOI and a title that happen to share a byte string
    cannot collide, and so a record's `cid` says which identifier it was anchored to.
    """
    kind, value = primary_id(candidate)
    return hashlib.sha1(f"{kind}:{value}".encode()).hexdigest()[:12]


def with_cid(candidate: Candidate) -> Candidate:
    """Normalise the identifiers, then stamp the derived `cid`."""
    normalised = candidate.model_copy(update={"ids": normalise_ids(candidate.ids)})
    return normalised.model_copy(update={"cid": derive_cid(normalised)})


def merge(existing: Candidate, incoming: Candidate) -> Candidate:
    """Union of what both records knew, with the `cid` recomputed from the merged identifiers.

    Recomputing matters: an S2-only arXiv record that later merges with a DOI-bearing OpenAlex
    record must end up under the DOI's `cid`, not keep the arXiv one it was created with.
    """
    ids = Ids(
        doi=existing.ids.doi or incoming.ids.doi,
        arxiv=existing.ids.arxiv or incoming.ids.arxiv,
        pmid=existing.ids.pmid or incoming.ids.pmid,
        openalex=existing.ids.openalex or incoming.ids.openalex,
        s2=existing.ids.s2 or incoming.ids.s2,
    )
    abstract = max((existing.abstract or "", incoming.abstract or ""), key=len) or None
    merged = existing.model_copy(
        update={
            "ids": ids,
            "abstract": abstract,
            "tldr": existing.tldr or incoming.tldr,
            "title": existing.title or incoming.title,
            "authors": _longer(existing.authors, incoming.authors),
            "year": existing.year if existing.year is not None else incoming.year,
            "publication_date": existing.publication_date or incoming.publication_date,
            "venue": existing.venue or incoming.venue,
            "type": existing.type if existing.type is not WorkType.other else incoming.type,
            "raw_type": existing.raw_type or incoming.raw_type,
            "citation_count": max(existing.citation_count, incoming.citation_count),
            "influential_citation_count": _max_optional(
                existing.influential_citation_count, incoming.influential_citation_count
            ),
            "is_retracted": existing.is_retracted or incoming.is_retracted,
            "oa_url": existing.oa_url or incoming.oa_url,
            "origins": _merge_origins(existing.origins, incoming.origins),
            "outside_window": existing.outside_window and incoming.outside_window,
        }
    )
    return merged.model_copy(update={"cid": derive_cid(merged)})


def _longer(left: list, right: list) -> list:
    """The fuller author list wins — a search hit is often truncated to the first author."""
    return left if len(left) >= len(right) else right


def _max_optional(left: int | None, right: int | None) -> int | None:
    if left is None:
        return right
    if right is None:
        return left
    return max(left, right)


def _merge_origins(existing: list[Origin], incoming: list[Origin]) -> list[Origin]:
    """Keep every distinct discovery path — origin count is a ranking signal (§8.1)."""
    merged = list(existing)
    seen = {_origin_key(origin) for origin in existing}
    for origin in incoming:
        key = _origin_key(origin)
        if key not in seen:
            seen.add(key)
            merged.append(origin)
    return merged


def _origin_key(origin: Origin) -> tuple:
    return (origin.source, origin.relation, origin.query_id, origin.seed_id, origin.rank)


@dataclass
class DedupReport:
    """What collapsed into what, so the log can explain a shrinking candidate count."""

    input_count: int = 0
    merged_by: dict[str, int] = field(default_factory=dict)

    @property
    def merged_total(self) -> int:
        return sum(self.merged_by.values())

    def record(self, reason: str) -> None:
        self.merged_by[reason] = self.merged_by.get(reason, 0) + 1


def deduplicate(candidates: list[Candidate]) -> tuple[list[Candidate], DedupReport]:
    """Collapse duplicates, preserving first-seen order (query order × source order × rank)."""
    report = DedupReport(input_count=len(candidates))
    kept: list[Candidate] = []
    by_doi: dict[str, int] = {}
    by_arxiv: dict[str, int] = {}
    by_pmid: dict[str, int] = {}

    for raw in candidates:
        candidate = with_cid(raw)
        index, reason = _find_match(candidate, kept, by_doi, by_arxiv, by_pmid)
        if index is None:
            kept.append(candidate)
            _index(candidate, len(kept) - 1, by_doi, by_arxiv, by_pmid)
            continue
        report.record(reason)
        kept[index] = merge(kept[index], candidate)
        _index(kept[index], index, by_doi, by_arxiv, by_pmid)

    return kept, report


def _find_match(
    candidate: Candidate,
    kept: list[Candidate],
    by_doi: dict[str, int],
    by_arxiv: dict[str, int],
    by_pmid: dict[str, int],
) -> tuple[int | None, str]:
    for value, index_map, reason in (
        (candidate.ids.doi, by_doi, "doi"),
        (candidate.ids.arxiv, by_arxiv, "arxiv"),
        (candidate.ids.pmid, by_pmid, "pmid"),
    ):
        if value and value in index_map:
            return index_map[value], reason

    title = normalise_title(candidate.title)
    if not title:
        return None, ""
    for index, other in enumerate(kept):
        if fuzz.ratio(title, normalise_title(other.title)) < TITLE_MATCH_RATIO:
            continue
        if _corroborated(candidate, other):
            return index, "title"
    return None, ""


def _corroborated(candidate: Candidate, other: Candidate) -> bool:
    """A fuzzy title alone is not enough: same first author, or years within one (§8.2)."""
    left, right = first_author_surname(candidate), first_author_surname(other)
    if left and right and left == right:
        return True
    if candidate.year is not None and other.year is not None:
        return abs(candidate.year - other.year) <= 1
    return False


def _index(
    candidate: Candidate,
    position: int,
    by_doi: dict[str, int],
    by_arxiv: dict[str, int],
    by_pmid: dict[str, int],
) -> None:
    if candidate.ids.doi:
        by_doi[candidate.ids.doi] = position
    if candidate.ids.arxiv:
        by_arxiv[candidate.ids.arxiv] = position
    if candidate.ids.pmid:
        by_pmid[candidate.ids.pmid] = position
