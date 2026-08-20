"""Citation-graph expansion: seeds, tagging, caps, ranking (spec §8.5, §9.5)."""

from __future__ import annotations

import json
from datetime import date

import httpx
import pytest
import respx

from conftest import make_candidate, make_plan, settings_for
from research_scan import expand
from research_scan.dedup import with_cid
from research_scan.http import HttpClient
from research_scan.schema import (
    Candidate,
    Expanded,
    Origin,
    Relation,
    RunInfo,
    ScreenFile,
    SourceName,
)
from research_scan.sources import s2 as s2_module
from research_scan.sources.base import SourceQueryError
from research_scan.sources.s2 import S2Source

WINDOW = (date(2023, 8, 1), date(2026, 8, 18))
ANCHOR = date(2026, 8, 18)


def screen_of(**scores: int) -> ScreenFile:
    return ScreenFile.model_validate(
        {"scores": [{"cid": cid, "score": score, "reason": "x"} for cid, score in scores.items()]}
    )


def graph_candidate(title: str, seed_cid: str, relation: Relation, **kwargs) -> Candidate:
    return make_candidate(
        title=title,
        origins=[Origin(source=SourceName.s2, relation=relation, seed_id=seed_cid, rank=0)],
        **kwargs,
    )


class FakeGraph:
    """Stands in for a source's references/citations/recommendations."""

    def __init__(self, references=None, citations=None, recommendations=None, fail=()):
        self._references = references or {}
        self._citations = citations or {}
        self._recommendations = recommendations or []
        self._fail = set(fail)

    def references(self, candidate, *, limit=30, window=None, cache=None):
        if "references" in self._fail:
            raise SourceQueryError("s2 HTTP 500")
        return self._references.get(candidate.cid, [])[:limit]

    def citations(self, candidate, *, limit=30, window=None, cache=None):
        if "citations" in self._fail:
            raise SourceQueryError("s2 HTTP 500")
        return self._citations.get(candidate.cid, [])[:limit]

    def recommendations(self, seeds, *, limit=40, cache=None):
        if "recommendations" in self._fail:
            raise SourceQueryError("s2 HTTP 429")
        return self._recommendations[:limit]

    def lookup(self, **kwargs):
        return None


# --- seed selection ---------------------------------------------------------


def test_seeds_are_only_papers_screened_relevant():
    pool = [
        with_cid(make_candidate(title="Central", doi="10.1000/a")),
        with_cid(make_candidate(title="Tangential", doi="10.1000/b")),
        with_cid(make_candidate(title="Off topic", doi="10.1000/c")),
    ]
    scores = {pool[0].cid: 3, pool[1].cid: 1, pool[2].cid: 0}

    seeds = expand.select_seeds(pool, scores, 15)

    assert [seed.title for seed in seeds] == ["Central"]


def test_seeds_are_ordered_by_score_then_origin_count():
    two_origins = with_cid(
        make_candidate(
            title="Found twice",
            doi="10.1000/b",
            origins=[
                Origin(source=SourceName.openalex, relation=Relation.query, query_id="Q1", rank=0),
                Origin(source=SourceName.s2, relation=Relation.query, query_id="Q2", rank=1),
            ],
        )
    )
    once = with_cid(make_candidate(title="Found once", doi="10.1000/c"))
    best = with_cid(make_candidate(title="Best", doi="10.1000/a"))
    scores = {best.cid: 3, two_origins.cid: 2, once.cid: 2}

    seeds = expand.select_seeds([once, two_origins, best], scores, 15)

    assert [seed.title for seed in seeds] == ["Best", "Found twice", "Found once"]


def test_seed_cap_is_honoured():
    pool = [with_cid(make_candidate(title=f"P{n}", doi=f"10.1000/{n}")) for n in range(20)]
    scores = dict.fromkeys((c.cid for c in pool), 3)
    assert len(expand.select_seeds(pool, scores, 15)) == 15


def test_out_of_window_papers_are_never_seeds():
    """Expansion grows from what is current; a tagged classic is a result, not a starting point."""
    classic = with_cid(make_candidate(title="Classic", doi="10.1000/old", year=2001))
    classic = classic.model_copy(update={"outside_window": True})
    assert expand.select_seeds([classic], {classic.cid: 3}, 15) == []


# --- gap-round seeds (V1.1) --------------------------------------------------


def gap_candidate(title: str, doi: str, query_id: str) -> object:
    return with_cid(
        make_candidate(
            title=title,
            doi=doi,
            origins=[
                Origin(
                    source=SourceName.openalex,
                    relation=Relation.query,
                    query_id=query_id,
                    rank=0,
                )
            ],
        )
    )


def test_the_gap_round_seeds_only_from_what_the_gap_round_found():
    from_gap = gap_candidate("From a gap query", "10.1000/a", "G1")
    from_reformulation = gap_candidate("From a reformulation", "10.1000/c", "R1")
    from_round_one = gap_candidate("From round one", "10.1000/b", "Q1")
    scores = dict.fromkeys((c.cid for c in (from_gap, from_reformulation, from_round_one)), 3)

    new = {from_gap.cid, from_reformulation.cid}
    seeds = expand.select_gap_seeds(
        [from_round_one, from_gap, from_reformulation], scores, {"G1", "R1"}, new
    )

    assert sorted(seed.title for seed in seeds) == ["From a gap query", "From a reformulation"]


def test_a_round_one_paper_the_gap_queries_re_found_is_not_a_new_seed():
    """It gains a `round2` origin and a high origin count, and would otherwise win the slot."""
    refound = with_cid(
        make_candidate(
            title="Re-found",
            doi="10.1000/d",
            origins=[
                Origin(source=SourceName.openalex, relation=Relation.query, query_id="Q1", rank=0),
                Origin(source=SourceName.s2, relation=Relation.query, query_id="G1", rank=1),
            ],
        )
    )
    fresh = gap_candidate("Actually new", "10.1000/e", "G1")
    scores = {refound.cid: 3, fresh.cid: 3}

    seeds = expand.select_gap_seeds([refound, fresh], scores, {"G1"}, {fresh.cid})

    assert [seed.title for seed in seeds] == ["Actually new"]


def test_a_paper_that_is_not_a_gap_round_addition_is_never_seeded():
    paper = gap_candidate("Already in the pool", "10.1000/a", "G1")
    assert expand.select_gap_seeds([paper], {paper.cid: 3}, {"G1"}, set()) == []


def test_the_gap_round_seeds_at_most_five():
    pool = [gap_candidate(f"P{n}", f"10.1000/{n}", "G1") for n in range(9)]
    scores = dict.fromkeys((c.cid for c in pool), 3)
    new = {c.cid for c in pool}
    assert len(expand.select_gap_seeds(pool, scores, {"G1"}, new)) == expand.GAP_SEEDS


# --- ranking ----------------------------------------------------------------


def test_additions_rank_by_seed_links_before_citations():
    linked_twice = make_candidate(
        title="Cited by two seeds",
        doi="10.1000/a",
        citation_count=5,
        year=2024,
        origins=[
            Origin(source=SourceName.s2, relation=Relation.references, seed_id="a" * 12, rank=0),
            Origin(source=SourceName.s2, relation=Relation.references, seed_id="b" * 12, rank=1),
        ],
    )
    popular = graph_candidate(
        "Cited by one seed",
        "a" * 12,
        Relation.references,
        doi="10.1000/b",
        citation_count=5000,
        year=2024,
    )

    ranked = expand.rank_additions([popular, linked_twice], ANCHOR.year)

    assert ranked[0].title == "Cited by two seeds"


def test_citations_per_year_breaks_the_tie():
    recent = graph_candidate(
        "Recent", "a" * 12, Relation.references, doi="10.1000/a", citation_count=40, year=2025
    )
    old = graph_candidate(
        "Old", "a" * 12, Relation.references, doi="10.1000/b", citation_count=60, year=2015
    )
    assert [c.title for c in expand.rank_additions([old, recent], ANCHOR.year)] == ["Recent", "Old"]


# --- the whole stage --------------------------------------------------------


@pytest.fixture
def prepared(tmp_path):
    seed = with_cid(make_candidate(title="Seed paper", doi="10.1000/seed", openalex="W1"))
    info = RunInfo.model_validate(
        {
            "run_dir": str(tmp_path),
            "slug": "t",
            "date": "2026-08-18",
            "brief_path": str(tmp_path / "brief.md"),
            "defaults": {"domain": "behavioral"},
        }
    )
    return tmp_path, info, seed


def run_expand(prepared, graph, *, options=None, plan=None):
    run_dir, info, seed = prepared
    return expand.run_expand(
        run_dir,
        info,
        plan or make_plan(),
        [seed],
        screen_of(**{seed.cid: 3}),
        graph,
        graph,
        settings=settings_for(S2_API_KEY="fake-s2-key-wxyz"),
        window=WINDOW,
        options=options or expand.ExpandOptions(),
        anchor=ANCHOR,
    )


def test_out_of_window_references_are_tagged_not_dropped(prepared):
    """§8.5's central rule — the foundational slots depend on it."""
    run_dir, _, seed = prepared
    old_reference = graph_candidate(
        "A 2004 classic",
        seed.cid,
        Relation.references,
        doi="10.1000/classic",
        year=2004,
        publication_date="2004-05-01",
    )
    recent = graph_candidate(
        "A 2025 citation",
        seed.cid,
        Relation.citations,
        doi="10.1000/recent",
        year=2025,
        publication_date="2025-05-01",
    )

    result = run_expand(
        prepared,
        FakeGraph(references={seed.cid: [old_reference]}, citations={seed.cid: [recent]}),
    )

    assert len(result.expanded.added_outside_window) == 1
    assert len(result.expanded.added) == 1
    assert result.expanded.dropped.retracted == 0

    written = json.loads((run_dir / "candidates.json").read_text())["candidates"]
    classic = next(c for c in written if c["title"] == "A 2004 classic")
    assert classic["outside_window"] is True
    assert classic["origins"][0]["relation"] == "references"
    assert classic["origins"][0]["seed_id"] == seed.cid


def test_expansion_still_drops_retracted_and_must_not(prepared):
    _, _, seed = prepared
    plan = make_plan(must_not=["cryptocurrency"])
    additions = [
        graph_candidate(
            "Retracted work", seed.cid, Relation.references, doi="10.1000/r", is_retracted=True
        ),
        graph_candidate("A cryptocurrency study", seed.cid, Relation.references, doi="10.1000/c"),
        graph_candidate(
            "An erratum", seed.cid, Relation.references, doi="10.1000/e", raw_type="erratum"
        ),
        graph_candidate("A keeper", seed.cid, Relation.references, doi="10.1000/k", year=2024),
    ]

    result = run_expand(prepared, FakeGraph(references={seed.cid: additions}), plan=plan)

    assert result.expanded.dropped.retracted == 1
    assert result.expanded.dropped.must_not == 1
    assert result.expanded.dropped.type == 1
    assert len(result.expanded.added) == 1


def test_caps_apply_separately_to_each_window(prepared):
    _, _, seed = prepared
    in_window = [
        graph_candidate(f"In {n}", seed.cid, Relation.citations, doi=f"10.1000/i{n}", year=2025)
        for n in range(10)
    ]
    outside = [
        graph_candidate(f"Out {n}", seed.cid, Relation.references, doi=f"10.1000/o{n}", year=2005)
        for n in range(10)
    ]

    result = run_expand(
        prepared,
        FakeGraph(references={seed.cid: outside}, citations={seed.cid: in_window}),
        options=expand.ExpandOptions(max_new=3, max_outside_window=2),
    )

    assert len(result.expanded.added) == 3
    assert len(result.expanded.added_outside_window) == 2
    assert result.expanded.dropped.cap == 15


def test_an_addition_already_in_the_pool_becomes_another_origin_not_a_duplicate(prepared):
    """Origin count is a ranking signal; a rediscovered paper should gain one, not be re-added."""
    run_dir, _, seed = prepared
    rediscovered = graph_candidate(
        "Seed paper", seed.cid, Relation.citations, doi="10.1000/seed", openalex="W1"
    )

    result = run_expand(prepared, FakeGraph(citations={seed.cid: [rediscovered]}))

    assert result.expanded.added == []
    written = json.loads((run_dir / "candidates.json").read_text())["candidates"]
    assert len(written) == 1
    assert len(written[0]["origins"]) == 2


def test_expansion_writes_x_batches_and_leaves_retrieval_batches_alone(prepared):
    run_dir, _, seed = prepared
    batch_dir = run_dir / "screen-batches"
    batch_dir.mkdir()
    (batch_dir / "01.json").write_text("retrieval")

    additions = [
        graph_candidate(f"Ref {n}", seed.cid, Relation.references, doi=f"10.1000/{n}", year=2024)
        for n in range(30)
    ]
    result = run_expand(prepared, FakeGraph(references={seed.cid: additions}))

    assert result.expanded.batches == ["x01", "x02"]
    assert (batch_dir / "01.json").read_text() == "retrieval"
    assert (batch_dir / "x01.json").exists()
    assert json.loads((run_dir / "expanded.json").read_text())["batches"] == ["x01", "x02"]


def test_expanded_json_matches_the_contract(prepared):
    run_dir, _, seed = prepared
    run_expand(
        prepared,
        FakeGraph(
            references={
                seed.cid: [
                    graph_candidate("R", seed.cid, Relation.references, doi="10.1000/r", year=2024)
                ]
            }
        ),
    )
    document = Expanded.model_validate(json.loads((run_dir / "expanded.json").read_text()))
    assert document.seeds == [seed.cid]
    assert len(document.added) == 1


def test_a_failing_graph_call_is_logged_not_fatal(prepared):
    _, _, seed = prepared
    graph = FakeGraph(
        citations={
            seed.cid: [
                graph_candidate(
                    "Survivor", seed.cid, Relation.citations, doi="10.1000/s", year=2025
                )
            ]
        },
        fail={"references", "recommendations"},
    )
    result = run_expand(prepared, graph)
    assert len(result.expanded.added) == 1


def test_no_seeds_is_an_explained_failure(prepared):
    run_dir, info, seed = prepared
    with pytest.raises(expand.NoSeeds, match="nothing to grow from"):
        expand.run_expand(
            run_dir,
            info,
            make_plan(),
            [seed],
            screen_of(**{seed.cid: 1}),
            FakeGraph(),
            FakeGraph(),
            settings=settings_for(),
            window=WINDOW,
            options=expand.ExpandOptions(),
            anchor=ANCHOR,
        )


def test_recommendations_are_collected_once_for_the_whole_seed_set(prepared):
    _, _, seed = prepared
    recommended = [
        make_candidate(
            title="Recommended",
            doi="10.1000/rec",
            year=2025,
            origins=[Origin(source=SourceName.s2, relation=Relation.recommendations, rank=0)],
        )
    ]
    result = run_expand(prepared, FakeGraph(recommendations=recommended))
    assert len(result.expanded.added) == 1


# --- the S2 graph adapter over recorded shapes ------------------------------


@pytest.fixture
def client(fake_settings):
    with HttpClient(fake_settings, cache=False, sleep=lambda _: None, max_retries=1) as http_client:
        yield http_client


@respx.mock
def test_s2_references_survive_a_publisher_elided_reference_list(client):
    """A real response: S2 answers 200 with `data: null` when the publisher withheld references."""
    respx.get(url__regex=r".*/references").mock(
        return_value=httpx.Response(200, json={"data": None, "citingPaperInfo": {}})
    )
    seed = with_cid(make_candidate(doi="10.1000/x"))
    assert S2Source(client).references(seed, limit=30) == []


@respx.mock
def test_s2_references_are_ranked_by_citation_count(client):
    respx.get(url__regex=r".*/references").mock(
        return_value=httpx.Response(
            200,
            json={
                "data": [
                    {"citedPaper": {"paperId": "a", "title": "Rarely cited", "citationCount": 2}},
                    {"citedPaper": {"paperId": "b", "title": "Widely cited", "citationCount": 900}},
                ]
            },
        )
    )
    refs = S2Source(client).references(with_cid(make_candidate(doi="10.1000/x")), limit=30)

    assert [ref.title for ref in refs] == ["Widely cited", "Rarely cited"]
    assert refs[0].origins[0].relation is Relation.references
    assert refs[0].origins[0].seed_id is not None


@respx.mock
def test_s2_citations_keep_only_the_window_and_the_newest(client):
    respx.get(url__regex=r".*/citations").mock(
        return_value=httpx.Response(
            200,
            json={
                "data": [
                    {
                        "citingPaper": {
                            "paperId": "a",
                            "title": "Too old",
                            "publicationDate": "2019-01-01",
                        }
                    },
                    {
                        "citingPaper": {
                            "paperId": "b",
                            "title": "Older",
                            "publicationDate": "2024-01-01",
                        }
                    },
                    {
                        "citingPaper": {
                            "paperId": "c",
                            "title": "Newest",
                            "publicationDate": "2026-01-01",
                        }
                    },
                ]
            },
        )
    )
    cites = S2Source(client).citations(
        with_cid(make_candidate(doi="10.1000/x")), limit=30, window=WINDOW
    )
    assert [c.title for c in cites] == ["Newest", "Older"]


@respx.mock
def test_s2_recommendations_post_the_whole_seed_set(client):
    route = respx.post(s2_module.RECOMMENDATIONS_URL).mock(
        return_value=httpx.Response(
            200, json={"recommendedPapers": [{"paperId": "z", "title": "Like these"}]}
        )
    )
    seeds = [
        with_cid(make_candidate(doi="10.1000/a")),
        with_cid(make_candidate(doi="10.1000/b", title="B")),
    ]

    found = S2Source(client).recommendations(seeds, limit=40)

    assert [c.title for c in found] == ["Like these"]
    body = json.loads(route.calls[0].request.content)
    assert body["positivePaperIds"] == ["DOI:10.1000/a", "DOI:10.1000/b"]
    assert found[0].origins[0].relation is Relation.recommendations


@respx.mock
def test_graph_calls_never_request_tldr(client):
    """The graph endpoints 400 on `tldr`; reusing SEARCH_FIELDS there silently killed expansion."""
    references = respx.get(url__regex=r".*/references").mock(
        return_value=httpx.Response(200, json={"data": []})
    )
    citations = respx.get(url__regex=r".*/citations").mock(
        return_value=httpx.Response(200, json={"data": []})
    )
    recommendations = respx.post(s2_module.RECOMMENDATIONS_URL).mock(
        return_value=httpx.Response(200, json={"recommendedPapers": []})
    )
    seed = with_cid(make_candidate(doi="10.1000/x"))
    source = S2Source(client)

    source.references(seed, limit=5)
    source.citations(seed, limit=5)
    source.recommendations([seed], limit=5)

    for route in (references, citations, recommendations):
        assert "tldr" not in route.calls[0].request.url.params["fields"]
    assert "tldr" in s2_module.SEARCH_FIELDS  # search still gets it


@respx.mock
def test_s2_graph_returns_empty_for_a_paper_it_does_not_have(client):
    respx.get(url__regex=r".*/references").mock(return_value=httpx.Response(404))
    assert S2Source(client).references(with_cid(make_candidate(doi="10.1000/x")), limit=5) == []


def test_s2_graph_skips_a_candidate_with_no_usable_identifier(client):
    assert S2Source(client).references(make_candidate(), limit=5) == []


# --- anchors always seed (S4.5) ---------------------------------------------


def anchored_candidate(title: str, doi: str, **kwargs):
    return with_cid(
        make_candidate(
            title=title,
            doi=doi,
            origins=[Origin(source=SourceName.openalex, relation=Relation.anchor, rank=0)],
            **kwargs,
        )
    )


def test_an_anchor_seeds_regardless_of_screen_score():
    anchor = anchored_candidate("Pinned classic", "10.1000/pinned")
    seeds = expand.select_seeds([anchor], {anchor.cid: 0}, 15)
    assert [seed.cid for seed in seeds] == [anchor.cid]


def test_an_out_of_window_anchor_still_seeds():
    anchor = anchored_candidate("Pinned classic", "10.1000/pinned", year=2004)
    anchor = anchor.model_copy(update={"outside_window": True})
    assert expand.select_seeds([anchor], {}, 15) == [anchor]


def test_anchors_ride_on_top_of_the_seed_cap():
    anchor = anchored_candidate("Pinned", "10.1000/pinned")
    pool = [with_cid(make_candidate(title=f"P{n}", doi=f"10.1000/{n}")) for n in range(20)]
    scores = dict.fromkeys((c.cid for c in pool), 3)

    seeds = expand.select_seeds([anchor, *pool], scores, 15)

    assert len(seeds) == 16  # 15 scored + the anchor, not 15 total
    assert seeds[0].cid == anchor.cid


def test_an_anchor_reaches_the_recommendations_call(prepared):
    """Seeds feed positivePaperIds; an anchor must be among them."""
    run_dir, info, seed = prepared
    anchor = anchored_candidate("Pinned classic", "10.1000/pinned")

    class RecordingGraph(FakeGraph):
        def __init__(self):
            super().__init__()
            self.recommendation_seeds = None

        def recommendations(self, seeds, *, limit=40, cache=None):
            self.recommendation_seeds = [s.cid for s in seeds]
            return []

    graph = RecordingGraph()
    expand.run_expand(
        run_dir,
        info,
        make_plan(),
        [seed, anchor],
        screen_of(**{seed.cid: 3, anchor.cid: 0}),
        graph,
        graph,
        settings=settings_for(),
        window=WINDOW,
        options=expand.ExpandOptions(),
        anchor=ANCHOR,
    )

    assert anchor.cid in graph.recommendation_seeds
    assert seed.cid in graph.recommendation_seeds


def test_expansion_records_the_auth_mode_of_both_graph_sources(prepared):
    """Expansion leans hardest on S2's graph endpoints, so its auth mode is the one that bites."""
    run_dir, info, seed = prepared
    events: list[tuple[str, dict]] = []

    result = expand.run_expand(
        run_dir,
        info,
        make_plan(),
        [seed],
        screen_of(**{seed.cid: 3}),
        FakeGraph(),
        FakeGraph(),
        settings=settings_for(S2_API_KEY="fake-s2-key-wxyz"),
        window=WINDOW,
        options=expand.ExpandOptions(),
        anchor=ANCHOR,
        on_event=lambda event, **fields: events.append((event, fields)),
    )

    assert result.stats.auth == {"s2": "key", "openalex": "anon"}
    assert ("auth", {"s2": "key", "openalex": "anon"}) in events
