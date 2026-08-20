# SPDX-License-Identifier: Apache-2.0
"""arXiv API, routed for cs / physics / math / stats (spec §7). Search-only; no graph.

Wire facts, verified live (S10g):

* **Bare multi-word queries are effectively OR.** Under ``sortBy=submittedDate`` the top of the
  feed for a bare four-term query was whatever newest paper matched any one term — quantum
  entropies, rank-1 games. Terms must be AND-joined under ``all:`` prefixes; the same four terms
  so joined returned exactly the target literature.
* The feed is Atom XML. Entry ids carry versions (``…v2``), stripped to the bare arXiv id. A
  malformed query still answers 200, with a single error entry instead of results.
* Every arXiv paper has a registered DataCite DOI ``10.48550/arXiv.<id>``; it is synthesised here
  so dedup merges these records with the OpenAlex and S2 copies of the same preprint.

Results come newest-first by submission — this is deliberately the *recency* voice of §7 (OpenAlex
and S2 lag arXiv by days), not a second relevance ranking. The window is applied client-side,
which under a descending date sort only trims the tail. Category-neutral: no ``cat:`` filter is
ever added — routing already decided arXiv is worth asking, and cross-listings make category
guesses lossy.
"""

from __future__ import annotations

import re
import xml.etree.ElementTree as ET
from datetime import date

from research_scan.dedup import normalise_arxiv
from research_scan.schema import (
    Author,
    Candidate,
    Ids,
    Origin,
    Relation,
    SourceName,
    WorkType,
)
from research_scan.sources.base import SourceQueryError

QUERY_URL = "https://export.arxiv.org/api/query"
ATOM = "{http://www.w3.org/2005/Atom}"
ARXIV_NS = "{http://arxiv.org/schemas/atom}"

_TOKENS = re.compile(r'"[^"]*"|\(|\)|[^\s()"]+')
_OPERATORS = frozenset({"AND", "OR", "NOT", "ANDNOT"})


def to_search_query(text: str) -> str:
    """Map a plan query onto arXiv's grammar.

    Terms and quoted phrases get ``all:`` prefixes. A query with no explicit Boolean operators is
    AND-joined (the semantic-mode case); one that carries them keeps its own structure, with
    ``NOT`` spelled the way arXiv wants it (``ANDNOT``).
    """
    tokens = _TOKENS.findall(text)
    has_operators = any(token in _OPERATORS for token in tokens)
    parts: list[str] = []
    for token in tokens:
        if token in {"(", ")"}:
            parts.append(token)
        elif token in _OPERATORS:
            parts.append("ANDNOT" if token == "NOT" else token)
        else:
            term = f"all:{token}"
            if parts and not has_operators and parts[-1] not in {"("}:
                parts.append("AND")
            parts.append(term)
    return " ".join(parts)


class ArxivSource:
    name = SourceName.arxiv
    supports_graph = False

    def __init__(self, client: object) -> None:
        self._client = client

    def search(
        self,
        query: str,
        window: tuple[date, date],
        *,
        limit: int = 20,
        cache: bool | None = None,
    ) -> list[Candidate]:
        response = self._client.get(
            QUERY_URL,
            params={
                "search_query": to_search_query(query),
                "start": 0,
                "max_results": limit,
                "sortBy": "submittedDate",
                "sortOrder": "descending",
            },
            cache=cache,
        )
        if not response.ok:
            raise SourceQueryError(f"arxiv HTTP {response.status_code}")
        candidates: list[Candidate] = []
        for entry in parse_feed(response.text):
            candidate = _to_candidate(entry, rank=len(candidates))
            if _within(candidate, window):
                candidates.append(candidate)
        return candidates

    # arXiv has no citation graph; expansion never routes here (§8.5).
    def references(self, candidate: Candidate, **_: object) -> list[Candidate]:
        raise NotImplementedError("arxiv has no reference graph")

    def citations(self, candidate: Candidate, **_: object) -> list[Candidate]:
        raise NotImplementedError("arxiv has no citation graph")

    def recommendations(self, seeds: list[Candidate], **_: object) -> list[Candidate]:
        raise NotImplementedError("arxiv has no recommendations")


def parse_feed(text: str) -> list[ET.Element]:
    """Atom entries, or :class:`SourceQueryError` — arXiv reports bad queries as a 200 feed."""
    try:
        root = ET.fromstring(text)
    except ET.ParseError as exc:
        raise SourceQueryError(f"arxiv returned unparseable XML: {exc}") from exc
    entries = root.findall(f"{ATOM}entry")
    if len(entries) == 1:
        entry_id = entries[0].findtext(f"{ATOM}id") or ""
        if "api/errors" in entry_id:
            summary = _squash(entries[0].findtext(f"{ATOM}summary") or "malformed query")
            raise SourceQueryError(f"arxiv rejected the query: {summary}")
    return entries


def _to_candidate(entry: ET.Element, rank: int) -> Candidate:
    raw_id = (entry.findtext(f"{ATOM}id") or "").rsplit("/abs/", 1)[-1]
    arxiv_id = normalise_arxiv(raw_id) or raw_id
    published = (entry.findtext(f"{ATOM}published") or "")[:10] or None
    pdf_url = next(
        (
            link.get("href")
            for link in entry.findall(f"{ATOM}link")
            if link.get("title") == "pdf" or link.get("type") == "application/pdf"
        ),
        None,
    )
    primary = entry.find(f"{ARXIV_NS}primary_category")

    return Candidate(
        cid="0" * 12,  # replaced by dedup.with_cid once identifiers are normalised
        title=_squash(entry.findtext(f"{ATOM}title") or "(untitled)"),
        abstract=_squash(entry.findtext(f"{ATOM}summary") or "") or None,
        authors=[
            Author(name=name)
            for author in entry.findall(f"{ATOM}author")
            if (name := _squash(author.findtext(f"{ATOM}name") or ""))
        ],
        year=int(published[:4]) if published else None,
        publication_date=published,
        venue="arXiv",
        type=WorkType.preprint,
        raw_type=primary.get("term") if primary is not None else None,
        ids=Ids(doi=f"10.48550/arXiv.{arxiv_id}", arxiv=arxiv_id),
        citation_count=0,  # arXiv reports none; dedup keeps the max across merged records
        is_retracted=False,
        oa_url=pdf_url,
        origins=[Origin(source=SourceName.arxiv, relation=Relation.query, rank=rank)],
    )


def _within(candidate: Candidate, window: tuple[date, date]) -> bool:
    if not candidate.publication_date:
        return True  # never drop for missing metadata; §8.3 filters decide later
    published = date.fromisoformat(candidate.publication_date)
    return window[0] <= published <= window[1]


def _squash(text: str) -> str:
    return re.sub(r"\s+", " ", text).strip()
