# SPDX-License-Identifier: Apache-2.0
"""The contract every source implements (spec §5, §7).

Search is mandatory; the graph methods are optional and a source that cannot do them says so
via `supports_graph`. `retrieve` and `expand` route on this, never on the source's name.

Implementations: OpenAlex and Semantic Scholar in S1, arXiv and PubMed in S6.
"""

from __future__ import annotations

from datetime import date
from typing import Protocol, runtime_checkable

from research_scan.schema import Candidate, SourceName


class SourceQueryError(RuntimeError):
    """One query against one source failed.

    Retrieval records it in the manifest and carries on; only *every* routed source failing is an
    exit-1 condition (§6). Sources raise this instead of returning empty so a genuine zero-hit
    query stays distinguishable from a dead endpoint.
    """


@runtime_checkable
class Source(Protocol):
    """A scholarly index research-scan can query."""

    name: SourceName

    #: False for sources that only search (arXiv, PubMed), True for OpenAlex and S2.
    supports_graph: bool

    def search(
        self,
        query: str,
        window: tuple[date, date],
        *,
        limit: int,
        cache: bool | None = None,
    ) -> list[Candidate]:
        """Top `limit` hits for one query, most relevant first, as partial Candidates.

        Each returned Candidate carries exactly one `origins` entry with `relation="query"` and its
        rank; the caller stamps `query_id` and the `cid`. Filters and dedup are the caller's job,
        not the source's. Raises :class:`SourceQueryError` when the endpoint refuses the query.
        """
        ...

    def references(
        self,
        candidate: Candidate,
        *,
        limit: int,
        window: tuple[date, date] | None = None,
    ) -> list[Candidate]:
        """Works this candidate cites (spec §8.5). May return [] if the id is unknown upstream.

        `window` steers ordering only (recency-reserved slots, S10g); out-of-window references are
        still returned — expansion tags them rather than dropping them.
        """
        ...

    def citations(self, candidate: Candidate, *, limit: int) -> list[Candidate]:
        """Works citing this candidate, newest first."""
        ...

    def recommendations(self, seeds: list[Candidate], *, limit: int) -> list[Candidate]:
        """Papers-like-these for the whole seed set in one call."""
        ...
