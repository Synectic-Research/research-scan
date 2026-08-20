"""Source adapters against responses recorded from the real APIs (spec §7, §8.1)."""

from __future__ import annotations

from datetime import date
from pathlib import Path

import httpx
import pytest
import respx

from conftest import load_fixture, make_candidate
from research_scan.http import HttpClient
from research_scan.schema import Relation, SourceName, WorkType
from research_scan.sources import arxiv as arxiv_module
from research_scan.sources import openalex as openalex_module
from research_scan.sources import s2 as s2_module
from research_scan.sources.arxiv import ArxivSource
from research_scan.sources.base import SourceQueryError
from research_scan.sources.openalex import OpenAlexSource, reconstruct_abstract
from research_scan.sources.s2 import S2Source

WINDOW = (date(2023, 8, 1), date(2026, 8, 18))


@pytest.fixture
def client(fake_settings, tmp_path) -> HttpClient:
    with HttpClient(fake_settings, cache=False, sleep=lambda _: None, max_retries=1) as http_client:
        yield http_client


# --- abstract reconstruction ------------------------------------------------


def test_reconstruct_abstract_orders_by_position():
    index = {"the": [0, 3], "cat": [1], "sat": [2], "mat": [4]}
    assert reconstruct_abstract(index) == "the cat sat the mat"


@pytest.mark.parametrize("empty", [None, {}, {"word": []}])
def test_reconstruct_abstract_handles_empty(empty):
    assert reconstruct_abstract(empty) is None


# --- OpenAlex ---------------------------------------------------------------


@respx.mock
def test_openalex_parses_a_recorded_response(client):
    payload = load_fixture("openalex_defaults.json")
    respx.get(openalex_module.WORKS_URL).mock(return_value=httpx.Response(200, json=payload))

    source = OpenAlexSource(client)
    candidates = source.search("default enrollment retirement saving", WINDOW, limit=3)

    assert len(candidates) == 3
    top = candidates[0]
    assert top.title == "Default Options and Retirement Saving Dynamics"
    assert top.ids.doi == "https://doi.org/10.1257/aer.20210881"  # normalised later, by dedup
    assert top.ids.openalex.startswith("W")
    assert top.venue == "American Economic Review"
    assert top.type is WorkType.article
    assert top.raw_type == "article"
    assert top.year == 2025
    assert top.citation_count > 0
    assert top.is_retracted is False
    assert top.abstract and "retirement" in top.abstract.lower()
    assert top.authors[0].name == "Taha Choukhmane"
    assert len(top.origins) == 1
    assert top.origins[0].source is SourceName.openalex
    assert top.origins[0].relation is Relation.query
    assert top.origins[0].rank == 0
    assert top.origins[0].query_id is None  # stamped by fan_out, not by the source


@respx.mock
def test_openalex_sends_the_window_and_retraction_filter(client):
    route = respx.get(openalex_module.WORKS_URL).mock(
        return_value=httpx.Response(200, json={"meta": {}, "results": []})
    )

    OpenAlexSource(client).search("defaults", WINDOW, limit=20)

    params = route.calls[0].request.url.params
    assert params["search"] == "defaults"
    assert "from_publication_date:2023-08-01" in params["filter"]
    assert "to_publication_date:2026-08-18" in params["filter"]
    assert "is_retracted:false" in params["filter"]
    assert params["per_page"] == "20"
    assert "abstract_inverted_index" in params["select"]


@respx.mock
def test_openalex_ranks_hits_in_result_order(client):
    respx.get(openalex_module.WORKS_URL).mock(
        return_value=httpx.Response(200, json=load_fixture("openalex_nudge.json"))
    )
    candidates = OpenAlexSource(client).search("nudge", WINDOW, limit=3)
    assert [candidate.origins[0].rank for candidate in candidates] == [0, 1, 2]


@respx.mock
def test_openalex_accumulates_the_reported_cost(client):
    respx.get(openalex_module.WORKS_URL).mock(
        return_value=httpx.Response(200, json={"meta": {"cost_usd": 0.001}, "results": []})
    )
    source = OpenAlexSource(client)
    source.search("a", WINDOW, limit=1)
    source.search("b", WINDOW, limit=1)
    assert source.cost_usd == pytest.approx(0.002)


@respx.mock
def test_openalex_raises_on_a_bad_status(client):
    respx.get(openalex_module.WORKS_URL).mock(return_value=httpx.Response(403))
    with pytest.raises(SourceQueryError, match="403"):
        OpenAlexSource(client).search("a", WINDOW, limit=1)


@respx.mock
def test_openalex_survives_a_record_missing_everything_optional(client):
    respx.get(openalex_module.WORKS_URL).mock(
        return_value=httpx.Response(
            200,
            json={
                "meta": {},
                "results": [
                    {
                        "id": "https://openalex.org/W9",
                        "title": None,
                        "display_name": "Only a display name",
                        "doi": None,
                        "authorships": None,
                        "primary_location": None,
                        "abstract_inverted_index": None,
                        "open_access": None,
                        "ids": None,
                        "type": None,
                    }
                ],
            },
        )
    )

    candidate = OpenAlexSource(client).search("a", WINDOW, limit=1)[0]

    assert candidate.title == "Only a display name"
    assert candidate.abstract is None
    assert candidate.venue is None
    assert candidate.type is WorkType.other
    assert candidate.citation_count == 0


def test_openalex_has_no_recommendations_endpoint(client):
    """references/citations landed in S2; "papers like these" is Semantic Scholar's alone."""
    with pytest.raises(NotImplementedError):
        OpenAlexSource(client).recommendations([make_candidate()], limit=1)


def test_openalex_graph_needs_an_openalex_id(client):
    assert OpenAlexSource(client).references(make_candidate(doi="10.1000/x"), limit=5) == []
    assert OpenAlexSource(client).citations(make_candidate(doi="10.1000/x"), limit=5) == []


# --- Semantic Scholar -------------------------------------------------------


@respx.mock
def test_s2_parses_a_recorded_response(client):
    respx.get(s2_module.SEARCH_URL).mock(
        return_value=httpx.Response(200, json=load_fixture("s2_defaults.json"))
    )

    candidates = S2Source(client).search("default enrollment retirement saving", WINDOW, limit=3)

    assert len(candidates) == 3
    top = candidates[0]
    assert top.title == "Default Options and Retirement Saving Dynamics"
    assert top.ids.doi == "10.1257/aer.20210881"
    assert top.ids.s2
    assert top.abstract and len(top.abstract) > 100
    assert top.type is WorkType.article
    assert top.citation_count > 0
    assert top.is_retracted is False  # S2 carries no retraction flag; `verify` catches it
    assert top.origins[0].source is SourceName.s2


@respx.mock
def test_s2_sends_the_date_window(client):
    route = respx.get(s2_module.SEARCH_URL).mock(
        return_value=httpx.Response(200, json={"data": []})
    )

    S2Source(client).search("defaults", WINDOW, limit=20)

    params = route.calls[0].request.url.params
    assert params["publicationDateOrYear"] == "2023-08-01:2026-08-18"
    assert params["limit"] == "20"
    assert "tldr" in params["fields"]


@respx.mock
def test_s2_treats_an_empty_open_access_url_as_missing(client):
    respx.get(s2_module.SEARCH_URL).mock(
        return_value=httpx.Response(
            200,
            json={
                "data": [
                    {
                        "paperId": "p1",
                        "title": "A paper",
                        "openAccessPdf": {"url": "", "status": None},
                        "externalIds": {"DOI": "10.1000/x"},
                    }
                ]
            },
        )
    )
    assert S2Source(client).search("a", WINDOW, limit=1)[0].oa_url is None


@pytest.mark.parametrize(
    ("types", "arxiv", "venue", "doi", "expected"),
    [
        (["JournalArticle"], None, "American Economic Review", "10.1/x", WorkType.article),
        (["Review"], None, "Psych Bulletin", "10.1/x", WorkType.review),
        (["BookSection"], None, "A Handbook", "10.1/x", WorkType.book_chapter),
        (["JournalArticle"], "2501.10120", "arXiv.org", None, WorkType.preprint),
        (["JournalArticle"], "2501.10120", "Nature", "10.1/x", WorkType.article),
        ([], "2501.10120", None, None, WorkType.preprint),
        ([], None, "PsyArXiv", None, WorkType.preprint),
        ([], None, None, None, WorkType.other),
    ],
)
def test_s2_work_type_mapping(types, arxiv, venue, doi, expected):
    assert s2_module._work_type(types, arxiv, venue, doi) is expected


@respx.mock
def test_s2_raises_on_a_bad_status(client):
    respx.get(s2_module.SEARCH_URL).mock(return_value=httpx.Response(429))
    with pytest.raises(SourceQueryError, match="429"):
        S2Source(client).search("a", WINDOW, limit=1)


@respx.mock
def test_s2_retracted_publication_type_marks_the_candidate(client):
    """S2 has no is_retracted flag; "Retracted" in publicationTypes is its signal (S4.5)."""
    respx.get(s2_module.SEARCH_URL).mock(
        return_value=httpx.Response(
            200,
            json={
                "data": [
                    {
                        "paperId": "p1",
                        "title": "A withdrawn study",
                        "publicationTypes": ["JournalArticle", "Retracted"],
                        "externalIds": {"DOI": "10.1000/x"},
                    }
                ]
            },
        )
    )
    candidate = S2Source(client).search("a", WINDOW, limit=1)[0]
    assert candidate.is_retracted is True


@respx.mock
def test_s2_survives_a_record_missing_everything_optional(client):
    respx.get(s2_module.SEARCH_URL).mock(
        return_value=httpx.Response(200, json={"data": [{"paperId": "p2", "title": "Bare"}]})
    )
    candidate = S2Source(client).search("a", WINDOW, limit=1)[0]
    assert candidate.title == "Bare"
    assert candidate.year is None
    assert candidate.authors == []


# --- credential reach (S10e) ------------------------------------------------


@respx.mock
def test_every_s2_endpoint_carries_the_api_key(client):
    """`x-api-key` on all four S2 calls, not just `/paper/search`.

    The topic-2 diagnostic could not answer "was this run authenticated?" from the run dir, and
    the graph endpoints are the ones expansion leans on hardest. Auth is injected per *host* in
    `HttpClient._authorize`, so a new endpoint on `api.semanticscholar.org` cannot opt out — this
    test is what keeps that true if the injection ever moves to a call site.
    """
    seed = make_candidate(doi="10.1234/seed")
    routes = {
        "search": respx.get(s2_module.SEARCH_URL).mock(
            return_value=httpx.Response(200, json={"data": []})
        ),
        "references": respx.get(url__regex=r".*/references").mock(
            return_value=httpx.Response(200, json={"data": []})
        ),
        "citations": respx.get(url__regex=r".*/citations").mock(
            return_value=httpx.Response(200, json={"data": []})
        ),
        "recommendations": respx.post(s2_module.RECOMMENDATIONS_URL).mock(
            return_value=httpx.Response(200, json={"recommendedPapers": []})
        ),
    }
    source = S2Source(client)

    source.search("agentic literature search", WINDOW, limit=5)
    source.references(seed, limit=5)
    source.citations(seed, limit=5, window=WINDOW)
    source.recommendations([seed], limit=5)

    for name, route in routes.items():
        assert route.called, f"{name} was never requested"
        for call in route.calls:
            assert call.request.headers.get("x-api-key") == "fake-s2-key-wxyz", (
                f"{name} went out without the S2 key"
            )


# --- reference ranking (S10g) -----------------------------------------------


def _ref_row(title: str, year: int, cites: int, month: str = "06") -> dict:
    return {
        "title": title,
        "year": year,
        "publicationDate": f"{year}-{month}-01",
        "citationCount": cites,
        "externalIds": {},
        "authors": [],
    }


def test_rank_references_reserves_slots_for_newest_in_window():
    """The LitSearch failure: a recent in-window benchmark must survive a list of old classics.

    Absolute-citation ordering put it 40th-69th in three seeds' reference lists; either the
    citations-per-year head or the recency reservation has to carry it now.
    """
    window = (date(2024, 1, 1), date(2026, 8, 19))
    classics = [_ref_row(f"classic {i}", 2010, 2000 - i) for i in range(8)]
    recent = _ref_row("recent benchmark", 2024, 6)  # 2/yr — dead last by every citation measure
    rows = classics + [recent]

    chosen = s2_module.rank_references(rows, limit=6, window=window)

    assert len(chosen) == 6
    assert recent in chosen  # holds a reserved slot despite the citation gap
    # the head is still the best classics, by citations-per-year
    assert chosen[0]["title"] == "classic 0"


def test_rank_references_prefers_earning_rate_over_absolute_count():
    window = (date(2024, 1, 1), date(2026, 8, 19))
    old_giant = _ref_row("old giant", 2006, 1050)  # 1050 / 21y = 50/yr
    fast_riser = _ref_row("fast riser", 2024, 200)  # 200 / 3y ≈ 67/yr
    rows = [old_giant, fast_riser] + [_ref_row(f"mid {i}", 2015, 100) for i in range(4)]

    chosen = s2_module.rank_references(rows, limit=2, window=window)

    assert chosen[0]["title"] == "fast riser"
    assert chosen[1]["title"] == "old giant"


def test_rank_references_tops_up_when_in_window_references_run_out():
    """A seed citing only classics must still fill every slot — the reservation never wastes one."""
    window = (date(2024, 1, 1), date(2026, 8, 19))
    rows = [_ref_row(f"classic {i}", 2005, 500 - i) for i in range(6)]

    chosen = s2_module.rank_references(rows, limit=6, window=window)

    assert len(chosen) == 6
    assert {row["title"] for row in chosen} == {f"classic {i}" for i in range(6)}


def test_rank_references_without_a_window_still_fills_the_limit():
    rows = [_ref_row(f"paper {i}", 2020, 50 - i) for i in range(5)]
    chosen = s2_module.rank_references(rows, limit=3, window=None)
    assert [row["title"] for row in chosen] == ["paper 0", "paper 1", "paper 2"]


# --- arXiv (S10g, spec §7) --------------------------------------------------

ARXIV_FIXTURE = (Path(__file__).parent / "fixtures" / "arxiv-search.atom.xml").read_text(
    encoding="utf-8"
)
ARXIV_WINDOW = (date(2024, 1, 1), date(2026, 8, 19))


def test_arxiv_query_mapping_prefixes_and_joins():
    """Bare multi-word queries are effectively OR on arXiv (verified live) — never send one."""
    assert (
        arxiv_module.to_search_query("agentic academic paper search")
        == "all:agentic AND all:academic AND all:paper AND all:search"
    )
    assert arxiv_module.to_search_query('survey AND "paper search"') == (
        'all:survey AND all:"paper search"'
    )
    assert arxiv_module.to_search_query("retrieval NOT patent") == (
        "all:retrieval ANDNOT all:patent"
    )
    assert arxiv_module.to_search_query('(survey OR review) AND "paper search"') == (
        '( all:survey OR all:review ) AND all:"paper search"'
    )


@respx.mock
def test_arxiv_search_parses_the_recorded_feed(client):
    respx.get(url__regex=r"https://export\.arxiv\.org/api/query.*").mock(
        return_value=httpx.Response(200, text=ARXIV_FIXTURE)
    )
    hits = ArxivSource(client).search("agentic academic paper search", ARXIV_WINDOW, limit=10)

    assert hits, "recorded feed produced no candidates"
    first = hits[0]
    assert first.ids.arxiv == "2606.20235"  # version stripped from ...v1
    assert first.ids.doi == "10.48550/arXiv.2606.20235"  # synthesised so dedup merges copies
    assert first.title.startswith("ScholarQuest")
    assert first.type is WorkType.preprint
    assert first.publication_date == "2026-06-18"
    assert first.abstract and "  " not in first.abstract  # whitespace squashed
    assert first.authors and first.oa_url and first.oa_url.endswith("2606.20235v1")
    assert [c.origins[0].rank for c in hits] == list(range(len(hits)))
    assert all(c.origins[0].source is SourceName.arxiv for c in hits)
    # sortBy=submittedDate descending, so the feed arrives newest-first
    dates = [c.publication_date for c in hits]
    assert dates == sorted(dates, reverse=True)


@respx.mock
def test_arxiv_window_is_applied_client_side(client):
    respx.get(url__regex=r"https://export\.arxiv\.org/api/query.*").mock(
        return_value=httpx.Response(200, text=ARXIV_FIXTURE)
    )
    narrow = (date(2026, 6, 1), date(2026, 6, 30))
    hits = ArxivSource(client).search("agentic academic paper search", narrow, limit=10)
    assert hits and all("2026-06-01" <= c.publication_date <= "2026-06-30" for c in hits)


@respx.mock
def test_arxiv_error_feed_raises_source_query_error(client):
    error_feed = (
        '<?xml version="1.0" encoding="UTF-8"?>'
        '<feed xmlns="http://www.w3.org/2005/Atom"><entry>'
        "<id>http://export.arxiv.org/api/errors#malformed</id>"
        "<title>Error</title><summary>search_query malformed</summary>"
        "</entry></feed>"
    )
    respx.get(url__regex=r"https://export\.arxiv\.org/api/query.*").mock(
        return_value=httpx.Response(200, text=error_feed)
    )
    with pytest.raises(SourceQueryError, match="malformed"):
        ArxivSource(client).search("bad query", ARXIV_WINDOW, limit=5)


@respx.mock
def test_arxiv_http_error_raises_source_query_error(client):
    respx.get(url__regex=r"https://export\.arxiv\.org/api/query.*").mock(
        return_value=httpx.Response(503)
    )
    with pytest.raises(SourceQueryError, match="503"):
        ArxivSource(client).search("anything", ARXIV_WINDOW, limit=5)


def test_arxiv_is_category_neutral_and_graphless():
    assert "cat:" not in arxiv_module.to_search_query("agentic paper search cs.IR")
    assert ArxivSource.supports_graph is False
