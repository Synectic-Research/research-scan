# SPDX-License-Identifier: Apache-2.0
"""OpenAlex `/works` — primary search, metadata, and the retraction flag (spec §7, §8.1).

Two OpenAlex quirks shape this module. Abstracts arrive as `abstract_inverted_index`
(`{word: [positions]}`) and have to be rebuilt in code. And `type` carries values `WorkType` does
not model (`paratext`, `erratum`, `dataset`, …), so the raw string is kept on the Candidate for the
§8.3 type filter to act on.
"""

from __future__ import annotations

import logging
from datetime import date

from research_scan.http import HttpClient
from research_scan.schema import Author, Candidate, Ids, Origin, Relation, SourceName, WorkType
from research_scan.sources.base import SourceQueryError

log = logging.getLogger(__name__)

WORKS_URL = "https://api.openalex.org/works"
MAX_PER_PAGE = 200

#: Trimmed with `select=` — a full work object is ~10 KB and we use a fraction of it.
SELECT_FIELDS = (
    "id,doi,title,publication_date,publication_year,type,authorships,primary_location,"
    "cited_by_count,is_retracted,abstract_inverted_index,open_access,ids"
)

#: `verify` only needs enough to confirm identity and retraction status (§10.5).
VERIFY_FIELDS = "id,doi,title,publication_year,publication_date,is_retracted,authorships"

_WORK_TYPES: dict[str, WorkType] = {
    "article": WorkType.article,
    "preprint": WorkType.preprint,
    "review": WorkType.review,
    "book-chapter": WorkType.book_chapter,
}


def reconstruct_abstract(inverted_index: dict[str, list[int]] | None) -> str | None:
    """`{"the": [0, 4], "cat": [1]}` → `the cat … the …`. Returns None for missing or empty."""
    if not inverted_index:
        return None
    positions: list[tuple[int, str]] = [
        (position, word) for word, places in inverted_index.items() for position in places
    ]
    if not positions:
        return None
    positions.sort()
    return " ".join(word for _, word in positions)


def _strip_url(value: str | None) -> str | None:
    if not value:
        return None
    return value.rstrip("/").rsplit("/", 1)[-1] or None


class OpenAlexSource:
    """OpenAlex, the mandatory source. Also the graph fallback when S2 lacks an id (S2 slice)."""

    name = SourceName.openalex
    supports_graph = True

    def __init__(self, client: HttpClient) -> None:
        self._client = client
        #: OpenAlex bills per search call and reports it in `meta.cost_usd`.
        self.cost_usd = 0.0

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
            WORKS_URL,
            params={
                "search": query,
                "filter": (
                    f"from_publication_date:{start.isoformat()},"
                    f"to_publication_date:{end.isoformat()},"
                    "is_retracted:false"
                ),
                "sort": "relevance_score:desc",
                "per_page": min(limit, MAX_PER_PAGE),
                "select": SELECT_FIELDS,
            },
            cache=cache,
        )
        if not response.ok:
            raise SourceQueryError(f"openalex HTTP {response.status_code}")

        payload = response.json()
        self.cost_usd += float((payload.get("meta") or {}).get("cost_usd") or 0.0)
        results = payload.get("results") or []
        return [self._to_candidate(item, rank) for rank, item in enumerate(results)]

    def lookup(
        self,
        *,
        doi: str | None = None,
        openalex_id: str | None = None,
        cache: bool | None = None,
    ) -> dict | None:
        """One work by identifier — the raw record, for `verify` to compare against (§10.5)."""
        if openalex_id:
            filter_value = f"openalex:{openalex_id}"
        elif doi:
            filter_value = f"doi:https://doi.org/{doi}"
        else:
            return None
        response = self._client.get(
            WORKS_URL,
            params={"filter": filter_value, "select": VERIFY_FIELDS, "per_page": 1},
            cache=cache,
        )
        if not response.ok:
            raise SourceQueryError(f"openalex HTTP {response.status_code}")
        results = response.json().get("results") or []
        return results[0] if results else None

    def get_by_doi(self, doi: str, *, cache: bool | None = None) -> Candidate | None:
        """One work by DOI as a full Candidate — the anchor-resolution path (S4.5).

        Distinct from `lookup`, which fetches the trimmed VERIFY_FIELDS for `verify`.
        """
        response = self._client.get(
            WORKS_URL,
            params={
                "filter": f"doi:https://doi.org/{doi}",
                "select": SELECT_FIELDS,
                "per_page": 1,
            },
            cache=cache,
        )
        if not response.ok:
            raise SourceQueryError(f"openalex HTTP {response.status_code}")
        results = response.json().get("results") or []
        return self._to_candidate(results[0], 0) if results else None

    def references(
        self,
        candidate: Candidate,
        *,
        limit: int = 30,
        window: tuple[date, date] | None = None,
        cache: bool | None = None,
    ) -> list[Candidate]:
        """Fallback when S2 does not know the paper: `referenced_works`, then a batch get (§8.5).

        `window` is accepted for signature parity with S2 but unused: `referenced_works` is bare
        ids, so any recency-aware ordering would need a metadata fetch for *every* reference
        before slicing — not worth it for the fallback path (S10g).
        """
        if not candidate.ids.openalex:
            return []
        response = self._client.get(
            f"{WORKS_URL}/{candidate.ids.openalex}",
            params={"select": "id,referenced_works"},
            cache=cache,
        )
        if not response.ok:
            raise SourceQueryError(f"openalex HTTP {response.status_code}")
        ids = [_strip_url(url) for url in (response.json().get("referenced_works") or [])]
        return self._by_ids(
            [work_id for work_id in ids if work_id][:limit], Relation.references, candidate.cid
        )

    def citations(
        self,
        candidate: Candidate,
        *,
        limit: int = 30,
        window: tuple[date, date] | None = None,
        cache: bool | None = None,
    ) -> list[Candidate]:
        """Fallback for §8.5: works citing this one, newest first, inside the window."""
        if not candidate.ids.openalex:
            return []
        filters = [f"cites:{candidate.ids.openalex}"]
        if window is not None:
            filters.append(f"from_publication_date:{window[0].isoformat()}")
            filters.append(f"to_publication_date:{window[1].isoformat()}")
        response = self._client.get(
            WORKS_URL,
            params={
                "filter": ",".join(filters),
                "sort": "publication_date:desc",
                "per_page": min(limit, MAX_PER_PAGE),
                "select": SELECT_FIELDS,
            },
            cache=cache,
        )
        if not response.ok:
            raise SourceQueryError(f"openalex HTTP {response.status_code}")
        return self._stamp(response.json().get("results") or [], Relation.citations, candidate.cid)

    def recommendations(self, seeds: list[Candidate], *, limit: int) -> list[Candidate]:
        raise NotImplementedError("OpenAlex has no recommendations endpoint")

    def _by_ids(self, work_ids: list[str], relation: Relation, seed_id: str) -> list[Candidate]:
        """Fetch works in pages of 50 using OpenAlex's `|` OR syntax."""
        collected: list[dict] = []
        for start in range(0, len(work_ids), 50):
            batch = work_ids[start : start + 50]
            response = self._client.get(
                WORKS_URL,
                params={
                    "filter": f"openalex:{'|'.join(batch)}",
                    "per_page": len(batch),
                    "select": SELECT_FIELDS,
                },
            )
            if not response.ok:
                raise SourceQueryError(f"openalex HTTP {response.status_code}")
            collected.extend(response.json().get("results") or [])
        return self._stamp(collected, relation, seed_id)

    def _stamp(self, items: list[dict], relation: Relation, seed_id: str | None) -> list[Candidate]:
        stamped = []
        for rank, item in enumerate(items):
            candidate = self._to_candidate(item, rank)
            stamped.append(
                candidate.model_copy(
                    update={
                        "origins": [
                            Origin(
                                source=SourceName.openalex,
                                relation=relation,
                                seed_id=seed_id,
                                rank=rank,
                            )
                        ]
                    }
                )
            )
        return stamped

    def _to_candidate(self, item: dict, rank: int) -> Candidate:
        raw_type = item.get("type")
        ids = item.get("ids") or {}
        location = item.get("primary_location") or {}
        source = location.get("source") or {}
        open_access = item.get("open_access") or {}

        return Candidate(
            cid="0" * 12,  # replaced by dedup.with_cid once identifiers are normalised
            title=item.get("title") or item.get("display_name") or "(untitled)",
            abstract=reconstruct_abstract(item.get("abstract_inverted_index")),
            authors=_authors(item.get("authorships")),
            year=item.get("publication_year"),
            publication_date=item.get("publication_date"),
            venue=source.get("display_name"),
            type=_WORK_TYPES.get(raw_type or "", WorkType.other),
            raw_type=raw_type,
            ids=Ids(
                doi=item.get("doi"),
                pmid=_strip_url(ids.get("pmid")),
                openalex=_strip_url(item.get("id")),
            ),
            citation_count=item.get("cited_by_count") or 0,
            is_retracted=bool(item.get("is_retracted")),
            oa_url=open_access.get("oa_url"),
            origins=[Origin(source=SourceName.openalex, relation=Relation.query, rank=rank)],
        )


def _authors(authorships: list[dict] | None) -> list[Author]:
    authors: list[Author] = []
    for entry in authorships or []:
        author = entry.get("author") or {}
        name = author.get("display_name") or entry.get("raw_author_name")
        if not name:
            continue
        authors.append(Author(name=name, openalex_id=_strip_url(author.get("id"))))
    return authors
