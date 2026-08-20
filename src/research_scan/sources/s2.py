# SPDX-License-Identifier: Apache-2.0
"""Semantic Scholar `/graph/v1` — the second search voice and the citation graph (§7, §8.1, §8.5).

S2 earns its place by disagreeing with OpenAlex: a different index, different relevance ranking,
first-class arXiv coverage, `tldr` summaries, and the references/citations/recommendations trio
that expansion runs on. It carries no retraction flag, so `is_retracted` is always False here — a
retracted paper that only S2 found is caught at `verify` (§14.4), not now.

Neither the references nor the citations endpoint sorts, so both fetch a wider page and rank
locally: references by citation count, citations by recency (§8.5).
"""

from __future__ import annotations

import logging
from datetime import date

from research_scan.http import HttpClient
from research_scan.schema import Author, Candidate, Ids, Origin, Relation, SourceName, WorkType
from research_scan.sources.base import SourceQueryError

log = logging.getLogger(__name__)

SEARCH_URL = "https://api.semanticscholar.org/graph/v1/paper/search"
PAPER_URL = "https://api.semanticscholar.org/graph/v1/paper/{id}"
REFERENCES_URL = "https://api.semanticscholar.org/graph/v1/paper/{id}/references"
CITATIONS_URL = "https://api.semanticscholar.org/graph/v1/paper/{id}/citations"
RECOMMENDATIONS_URL = "https://api.semanticscholar.org/recommendations/v1/papers"
MAX_LIMIT = 100

#: How wide to page the unsorted graph endpoints before ranking locally.
GRAPH_FETCH_LIMIT = 100

SEARCH_FIELDS = (
    "paperId,externalIds,title,abstract,venue,year,publicationDate,citationCount,"
    "influentialCitationCount,authors,tldr,openAccessPdf,publicationTypes"
)

#: The graph endpoints reject `tldr` outright — `{"error": "Unrecognized or unsupported fields:
#: [tldr]"}` — so they get their own list. Verified against the live API.
GRAPH_FIELDS = (
    "paperId,externalIds,title,abstract,venue,year,publicationDate,citationCount,"
    "influentialCitationCount,authors,openAccessPdf,publicationTypes"
)

#: S2 `publicationTypes` → our WorkType. Order matters: the first match in this list wins.
_TYPE_PRIORITY: tuple[tuple[str, WorkType], ...] = (
    ("Review", WorkType.review),
    ("BookSection", WorkType.book_chapter),
    ("JournalArticle", WorkType.article),
    ("Conference", WorkType.article),
    ("Study", WorkType.article),
)

#: Venues that mean "preprint" regardless of what `publicationTypes` claims.
_PREPRINT_VENUES = (
    "arxiv",
    "biorxiv",
    "medrxiv",
    "psyarxiv",
    "socarxiv",
    "ssrn",
    "research square",
    "osf",
)


class S2Source:
    """Semantic Scholar search. References, citations and recommendations arrive in S2."""

    name = SourceName.s2
    supports_graph = True

    def __init__(self, client: HttpClient) -> None:
        self._client = client

    def search(
        self,
        query: str,
        window: tuple[date, date],
        *,
        limit: int,
        cache: bool | None = None,
    ) -> list[Candidate]:
        start, end = window
        response = self._client.get(
            SEARCH_URL,
            params={
                "query": query,
                "limit": min(limit, MAX_LIMIT),
                "publicationDateOrYear": f"{start.isoformat()}:{end.isoformat()}",
                "fields": SEARCH_FIELDS,
            },
            cache=cache,
        )
        if not response.ok:
            raise SourceQueryError(f"s2 HTTP {response.status_code}")

        results = response.json().get("data") or []
        return [self._to_candidate(item, rank) for rank, item in enumerate(results)]

    def references(
        self,
        candidate: Candidate,
        *,
        limit: int = 30,
        window: tuple[date, date] | None = None,
        cache: bool | None = None,
    ) -> list[Candidate]:
        """Works this one cites: most-cited *per year*, with slots held for the newest (§8.5).

        Absolute citation count buried recent work: on the llm-lit-search reference run, a 2024
        benchmark cited by three seeds ranked 40th-69th in their reference lists behind decade-old
        classics and was cut at 30, three times over (S10g). Citations-per-year keeps the classics
        that are still earning their count while a third of the slots go to the newest in-window
        references — where a 2024-2026 brief's prior art actually lives.

        Returns [] when S2 does not know the paper, or when the publisher has elided its reference
        list — S2 answers 200 with `data: null` for that, which is not an error.
        """
        paper_id = s2_paper_id(candidate)
        if paper_id is None:
            return []
        rows = self._graph(REFERENCES_URL, paper_id, "citedPaper", cache=cache)
        return self._to_candidates(
            rank_references(rows, limit, window), Relation.references, candidate.cid
        )

    def citations(
        self,
        candidate: Candidate,
        *,
        limit: int = 30,
        window: tuple[date, date] | None = None,
        cache: bool | None = None,
    ) -> list[Candidate]:
        """Works citing this one — the newest `limit`, restricted to the window (§8.5)."""
        paper_id = s2_paper_id(candidate)
        if paper_id is None:
            return []
        rows = self._graph(CITATIONS_URL, paper_id, "citingPaper", cache=cache)
        if window is not None:
            rows = [row for row in rows if _within(row, window)]
        rows.sort(key=_sort_date, reverse=True)
        return self._to_candidates(rows[:limit], Relation.citations, candidate.cid)

    def recommendations(
        self,
        seeds: list[Candidate],
        *,
        limit: int = 40,
        cache: bool | None = None,
    ) -> list[Candidate]:
        """ "Papers like these" for the whole seed set in one POST (§8.5)."""
        positive = [pid for pid in (s2_paper_id(seed) for seed in seeds) if pid]
        if not positive:
            return []
        response = self._client.post(
            RECOMMENDATIONS_URL,
            params={"limit": min(limit, MAX_LIMIT), "fields": GRAPH_FIELDS},
            json_body={"positivePaperIds": positive, "negativePaperIds": []},
            cache=cache,
        )
        if not response.ok:
            raise SourceQueryError(f"s2 recommendations HTTP {response.status_code}")
        rows = response.json().get("recommendedPapers") or []
        return self._to_candidates(rows, Relation.recommendations, None)

    def _graph(self, url: str, paper_id: str, key: str, *, cache: bool | None) -> list[dict]:
        response = self._client.get(
            url.format(id=paper_id),
            params={"limit": GRAPH_FETCH_LIMIT, "fields": GRAPH_FIELDS},
            cache=cache,
        )
        if response.status_code == 404:
            return []  # S2 simply does not have this paper
        if not response.ok:
            raise SourceQueryError(f"s2 graph HTTP {response.status_code}")
        # `data` is null when the publisher elided the reference list — a 200, not a failure.
        rows = response.json().get("data") or []
        return [row[key] for row in rows if row.get(key)]

    def _to_candidates(
        self, rows: list[dict], relation: Relation, seed_id: str | None
    ) -> list[Candidate]:
        candidates = []
        for rank, row in enumerate(rows):
            candidate = self._to_candidate(row, rank)
            candidates.append(
                candidate.model_copy(
                    update={
                        "origins": [
                            Origin(
                                source=SourceName.s2,
                                relation=relation,
                                seed_id=seed_id,
                                rank=rank,
                            )
                        ]
                    }
                )
            )
        return candidates

    def lookup_publication_types(self, paper_id: str, *, cache: bool | None = None) -> list[str]:
        """One paper's publicationTypes, for the verify-time retraction check.

        Returns [] when S2 does not know the paper. Honest caveat, verified live: S2 does NOT mark
        the canonical Wakefield retraction, so this is a supplementary signal beside OpenAlex's
        `is_retracted`, never a replacement for it.
        """
        response = self._client.get(
            PAPER_URL.format(id=paper_id), params={"fields": "publicationTypes"}, cache=cache
        )
        if response.status_code == 404:
            return []
        if not response.ok:
            raise SourceQueryError(f"s2 HTTP {response.status_code}")
        return response.json().get("publicationTypes") or []

    def _to_candidate(self, item: dict, rank: int) -> Candidate:
        external = item.get("externalIds") or {}
        arxiv = external.get("ArXiv")
        publication_types = item.get("publicationTypes") or []
        tldr = item.get("tldr") or {}
        open_access = item.get("openAccessPdf") or {}
        venue = item.get("venue") or None

        return Candidate(
            cid="0" * 12,  # replaced by dedup.with_cid once identifiers are normalised
            title=item.get("title") or "(untitled)",
            abstract=item.get("abstract"),
            tldr=tldr.get("text"),
            authors=[
                Author(name=author["name"], s2_id=author.get("authorId"))
                for author in item.get("authors") or []
                if author.get("name")
            ],
            year=item.get("year"),
            publication_date=item.get("publicationDate"),
            venue=venue,
            type=_work_type(publication_types, arxiv, venue, external.get("DOI")),
            raw_type=publication_types[0] if publication_types else None,
            ids=Ids(
                doi=external.get("DOI"),
                arxiv=arxiv,
                pmid=external.get("PubMed"),
                s2=item.get("paperId"),
            ),
            citation_count=item.get("citationCount") or 0,
            influential_citation_count=item.get("influentialCitationCount"),
            # S2 has no is_retracted flag, but "Retracted" can appear in publicationTypes.
            is_retracted="Retracted" in publication_types,
            oa_url=open_access.get("url") or None,  # S2 sends "" when it has no PDF
            origins=[Origin(source=SourceName.s2, relation=Relation.query, rank=rank)],
        )


def s2_paper_id(candidate: Candidate) -> str | None:
    """S2's own id if we have it, else a DOI or arXiv reference S2 accepts in place of one."""
    if candidate.ids.s2:
        return candidate.ids.s2
    if candidate.ids.doi:
        return f"DOI:{candidate.ids.doi}"
    if candidate.ids.arxiv:
        return f"ARXIV:{candidate.ids.arxiv}"
    return None


def rank_references(rows: list[dict], limit: int, window: tuple[date, date] | None) -> list[dict]:
    """Order a seed's references: citations-per-year first, newest-in-window reserved (§8.5, S10g).

    Two-thirds of `limit` go to the highest citations-per-year (age measured against the window
    end, minimum one year, so a missing year neither inflates nor crashes). The last third is
    reserved for the newest in-window references not already chosen — filled back from the
    citations-per-year order when a seed cites fewer in-window works than there are slots, so the
    reservation never wastes a slot.
    """
    anchor_year = window[1].year if window else date.today().year

    def per_year(row: dict) -> float:
        age = max(1, anchor_year - (row.get("year") or anchor_year) + 1)
        return (row.get("citationCount") or 0) / age

    ordered = sorted(rows, key=per_year, reverse=True)
    recent_slots = limit // 3
    head = ordered[: limit - recent_slots]
    tail = ordered[limit - recent_slots :]

    recent: list[dict] = []
    if window is not None:
        recent = sorted(
            (row for row in tail if _within(row, window)), key=_sort_date, reverse=True
        )[:recent_slots]
    chosen = head + recent
    if len(chosen) < limit:
        taken = {id(row) for row in chosen}
        chosen += [row for row in tail if id(row) not in taken][: limit - len(chosen)]
    return chosen


def _sort_date(row: dict) -> str:
    """Sort key for recency: full date when S2 has one, else the year, else the epoch."""
    return row.get("publicationDate") or (f"{row['year']}-01-01" if row.get("year") else "0000")


def _within(row: dict, window: tuple[date, date]) -> bool:
    start, end = window
    raw = row.get("publicationDate")
    if raw:
        try:
            return start <= date.fromisoformat(raw) <= end
        except ValueError:
            return True
    year = row.get("year")
    return start.year <= year <= end.year if year else True


def _work_type(
    publication_types: list[str], arxiv: str | None, venue: str | None, doi: str | None
) -> WorkType:
    """S2 has no `preprint` type; the preprint server's name is the reliable signal.

    The venue check runs first because S2 labels most arXiv records `JournalArticle`. An arXiv id
    alone is not enough — plenty of published articles also have one.
    """
    venue_lower = (venue or "").lower()
    if any(venue_lower.startswith(name) for name in _PREPRINT_VENUES):
        return WorkType.preprint
    for label, work_type in _TYPE_PRIORITY:
        if label in publication_types:
            return work_type
    if arxiv and not doi:
        return WorkType.preprint
    return WorkType.other
