# SPDX-License-Identifier: Apache-2.0
"""Crossref `/works/{doi}` — verification only, never a search engine here (spec §7, §10.5).

Crossref answers one question: does this DOI resolve, and to what. Its `update-to` field carries
retraction notices, but not reliably from the retracted work's own record — the Wakefield MMR
paper resolves with `update-to: null` and only a `RETRACTED:` title prefix. So retraction is
decided by OpenAlex's `is_retracted` plus either of Crossref's two tells, and the prefix is
stripped before the title comparison so a retraction cannot masquerade as a title mismatch.
"""

from __future__ import annotations

import logging
import re
from dataclasses import dataclass

from research_scan.dedup import title_similarity
from research_scan.http import HttpClient
from research_scan.sources.base import SourceQueryError

log = logging.getLogger(__name__)

WORKS_URL = "https://api.crossref.org/works/{doi}"
SEARCH_URL = "https://api.crossref.org/works"

#: Bibliographic-search acceptance: near-exact or nothing. A DOI-less record is being *identified*,
#: not fuzzily matched, and Crossref happily returns same-author-different-paper items.
BIBLIOGRAPHIC_TITLE_RATIO = 95
BIBLIOGRAPHIC_YEAR_TOLERANCE = 1
BIBLIOGRAPHIC_ROWS = 5

_RETRACTED_PREFIX = re.compile(r"^\s*(retracted|withdrawn)\s*[:\-–]\s*", re.IGNORECASE)
_RETRACTION_UPDATE_TYPES = frozenset({"retraction", "withdrawal", "removal"})


@dataclass(frozen=True)
class CrossrefRecord:
    """The slice of a Crossref work `verify` compares a ranked entry against."""

    doi: str
    title: str
    year: int | None
    first_author_surname: str
    retracted: bool


class CrossrefUnavailable(SourceQueryError):
    """403 or 429 — skip Crossref for the rest of the run and note it once (§10.5)."""


class CrossrefSource:
    """Lookup by DOI. Not a `Source`: it never searches, so it implements no search()."""

    def __init__(self, client: HttpClient) -> None:
        self._client = client

    def lookup(self, doi: str, *, cache: bool | None = None) -> CrossrefRecord | None:
        """The record, or None when the DOI does not resolve. Raises when Crossref shuts us out."""
        response = self._client.get(WORKS_URL.format(doi=doi), cache=cache)
        if response.status_code in (403, 429):
            raise CrossrefUnavailable(f"crossref HTTP {response.status_code}")
        if response.status_code == 404:
            return None
        if not response.ok:
            raise SourceQueryError(f"crossref HTTP {response.status_code}")

        return _parse(response.json().get("message") or {}, fallback_doi=doi)

    def search_bibliographic(
        self,
        title: str,
        first_author_surname: str | None,
        year: int | None,
        *,
        cache: bool | None = None,
    ) -> CrossrefRecord | None:
        """Identify a DOI-less record by title + author + year (spec S4.5, verify hardening).

        Accepts only a near-exact hit: title ratio ≥ 95 AND year within ±1. Verified live: the
        search reliably returns same-author-*different*-paper items, so anything looser would
        verify the wrong work — the one failure verification exists to prevent.
        """
        params: dict[str, object] = {
            "query.bibliographic": title,
            "rows": BIBLIOGRAPHIC_ROWS,
            "select": "DOI,title,author,issued,update-to",
        }
        if first_author_surname:
            params["query.author"] = first_author_surname
        response = self._client.get(SEARCH_URL, params=params, cache=cache)
        if response.status_code in (403, 429):
            raise CrossrefUnavailable(f"crossref HTTP {response.status_code}")
        if not response.ok:
            raise SourceQueryError(f"crossref HTTP {response.status_code}")

        best: CrossrefRecord | None = None
        best_ratio = 0.0
        for item in (response.json().get("message") or {}).get("items") or []:
            record = _parse(item, fallback_doi=item.get("DOI") or "")
            ratio = title_similarity(title, record.title)
            if ratio < BIBLIOGRAPHIC_TITLE_RATIO:
                continue
            if (
                year is not None
                and record.year is not None
                and abs(year - record.year) > BIBLIOGRAPHIC_YEAR_TOLERANCE
            ):
                continue
            if ratio > best_ratio:
                best, best_ratio = record, ratio
        return best


def _parse(message: dict, *, fallback_doi: str) -> CrossrefRecord:
    titles = message.get("title") or []
    raw_title = titles[0] if titles else ""
    return CrossrefRecord(
        doi=(message.get("DOI") or fallback_doi).lower(),
        title=_RETRACTED_PREFIX.sub("", raw_title).strip(),
        year=_year(message),
        first_author_surname=_first_author(message),
        retracted=bool(_RETRACTED_PREFIX.match(raw_title)) or _has_retraction_notice(message),
    )


def _year(message: dict) -> int | None:
    for field in ("issued", "published", "published-print", "published-online"):
        parts = ((message.get(field) or {}).get("date-parts") or [[]])[0]
        if parts and isinstance(parts[0], int):
            return parts[0]
    return None


def _first_author(message: dict) -> str:
    for author in message.get("author") or []:
        if author.get("sequence") == "first" or author is (message.get("author") or [None])[0]:
            return (author.get("family") or "").strip()
    return ""


def _has_retraction_notice(message: dict) -> bool:
    return any(
        (update.get("type") or "").lower() in _RETRACTION_UPDATE_TYPES
        for update in message.get("update-to") or []
    )
