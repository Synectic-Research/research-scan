"""The retrieval pipeline: routing, filters, caps, batches (spec §8.1–§8.4, §9.3)."""

from __future__ import annotations

import json
from datetime import date

import pytest

from conftest import make_candidate, make_plan, settings_for
from research_scan import retrieve
from research_scan.schema import (
    Domain,
    Origin,
    Relation,
    ScreenBatch,
    SourceName,
    WorkType,
)
from research_scan.sources.base import SourceQueryError

WINDOW = (date(2023, 8, 1), date(2026, 8, 18))
ANON = settings_for()
KEYED = settings_for(S2_API_KEY="fake-s2-key-wxyz")


class FakeSource:
    """A source that hands back whatever the test decided it found."""

    supports_graph = True

    def __init__(self, name: SourceName, results: dict[str, list], fail: set[str] | None = None):
        self.name = name
        self._results = results
        self._fail = fail or set()
        self.calls: list[str] = []

    def search(self, query, window, *, limit, cache=None):
        self.calls.append(query)
        if query in self._fail:
            raise SourceQueryError(f"{self.name.value} refused {query!r}")
        found = self._results.get(query, [])[:limit]
        return [
            candidate.model_copy(
                update={"origins": [Origin(source=self.name, relation=Relation.query, rank=rank)]}
            )
            for rank, candidate in enumerate(found)
        ]


# --- routing ----------------------------------------------------------------


@pytest.mark.parametrize(
    ("domain", "expected"),
    [
        (Domain.behavioral, ["openalex", "s2"]),
        (Domain.cs, ["openalex", "s2", "arxiv"]),
        (Domain.biomed, ["openalex", "s2", "pubmed"]),
        (Domain.general, ["openalex", "s2"]),
    ],
)
def test_routing_map(domain, expected):
    plan = make_plan(domain=domain.value)
    assert [name.value for name in retrieve.route(domain, plan)] == expected


def test_general_domain_adds_arxiv_when_a_query_is_a_method_query():
    payload = make_plan().model_dump(mode="json", by_alias=True)
    payload["domain"] = "general"
    payload["queries"][5] = {
        "id": "Q6",
        "type": "method",
        "text": "instrumental variables",
        "mode": "keyword",
    }
    plan = make_plan(**payload)
    assert SourceName.arxiv in retrieve.route(Domain.general, plan)


def test_sources_override_wins_over_routing():
    plan = make_plan()
    routed = retrieve.route(Domain.biomed, plan, [SourceName.openalex])
    assert routed == [SourceName.openalex]


def test_only_built_sources_get_an_adapter():
    adapters = retrieve.build_sources(
        [SourceName.openalex, SourceName.s2, SourceName.arxiv, SourceName.pubmed], None
    )
    # arXiv joined the built set in S10g; PubMed stays S6.
    assert set(adapters) == {SourceName.openalex, SourceName.s2, SourceName.arxiv}


# --- §8.1 fan-out -----------------------------------------------------------


def test_fan_out_stamps_the_query_id_on_every_origin():
    plan = make_plan()
    source = FakeSource(
        SourceName.openalex, {query.text: [make_candidate()] for query in plan.queries}
    )

    hits, stats, per_query = retrieve.fan_out(
        plan, {SourceName.openalex: source}, WINDOW, per_query=20, settings=ANON
    )

    assert len(hits) == 6
    assert {hit.origins[0].query_id for hit in hits} == {f"Q{n}" for n in range(1, 7)}
    assert stats["openalex"].queried == 6
    assert stats["openalex"].hits == 6
    assert per_query == dict.fromkeys([f"Q{n}" for n in range(1, 7)], 1)


def test_fan_out_records_a_failing_query_and_keeps_going():
    plan = make_plan()
    results = {query.text: [make_candidate()] for query in plan.queries}
    source = FakeSource(SourceName.openalex, results, fail={plan.queries[0].text})

    hits, stats, _ = retrieve.fan_out(
        plan, {SourceName.openalex: source}, WINDOW, per_query=20, settings=ANON
    )

    assert len(hits) == 5
    assert stats["openalex"].failed == 1
    assert stats["openalex"].queried == 6


def test_fan_out_raises_only_when_every_source_fails_every_query():
    plan = make_plan()
    all_texts = {query.text for query in plan.queries}
    sources = {
        SourceName.openalex: FakeSource(SourceName.openalex, {}, fail=all_texts),
        SourceName.s2: FakeSource(SourceName.s2, {}, fail=all_texts),
    }

    with pytest.raises(retrieve.AllSourcesFailed):
        retrieve.fan_out(plan, sources, WINDOW, per_query=20, settings=ANON)


def test_one_source_surviving_is_not_a_failure():
    plan = make_plan()
    all_texts = {query.text for query in plan.queries}
    sources = {
        SourceName.openalex: FakeSource(SourceName.openalex, {}, fail=all_texts),
        SourceName.s2: FakeSource(SourceName.s2, {plan.queries[0].text: [make_candidate()]}),
    }

    hits, stats, _ = retrieve.fan_out(plan, sources, WINDOW, per_query=20, settings=ANON)

    assert len(hits) == 1
    assert stats["openalex"].failed == 6
    assert stats["s2"].failed == 0


def test_fan_out_respects_per_query():
    plan = make_plan()
    many = [make_candidate(title=f"Paper {n}", doi=f"10.1000/{n}") for n in range(50)]
    source = FakeSource(SourceName.openalex, {plan.queries[0].text: many})

    hits, _, _ = retrieve.fan_out(
        plan, {SourceName.openalex: source}, WINDOW, per_query=5, settings=ANON
    )

    assert len(hits) == 5


# --- §8.3 filters -----------------------------------------------------------


def test_must_not_matches_at_word_boundaries_only():
    pattern = retrieve.must_not_pattern("AI")
    assert pattern.search("the role of AI in policy")
    assert not pattern.search("AIDS prevention trials")
    assert not pattern.search("Thailand")


def test_must_not_handles_phrases_with_punctuation():
    pattern = retrieve.must_not_pattern("COVID-19")
    assert pattern.search("during COVID-19 lockdowns")
    assert not pattern.search("COVID-1938 was not a thing")


def test_must_not_filters_title_and_abstract_case_insensitively():
    plan = make_plan(must_not=["cryptocurrency", "AI"])
    candidates = [
        make_candidate(title="Defaults in Cryptocurrency wallets", doi="10.1000/a"),
        make_candidate(title="Defaults", abstract="We used AI to classify.", doi="10.1000/b"),
        make_candidate(title="Defaults and AIDS awareness", doi="10.1000/c"),
    ]

    kept, dropped = retrieve.apply_filters(candidates, plan, WINDOW)

    assert [candidate.ids.doi for candidate in kept] == ["10.1000/c"]
    assert dropped.must_not == 2


def test_retracted_candidates_are_dropped_and_counted():
    kept, dropped = retrieve.apply_filters(
        [make_candidate(doi="10.1000/a", is_retracted=True), make_candidate(doi="10.1000/b")],
        make_plan(),
        WINDOW,
    )
    assert len(kept) == 1
    assert dropped.retracted == 1


@pytest.mark.parametrize("raw_type", ["paratext", "erratum", "dataset", "Dataset", "peer-review"])
def test_non_scholarly_types_are_dropped(raw_type):
    kept, dropped = retrieve.apply_filters(
        [make_candidate(doi="10.1000/a", raw_type=raw_type)], make_plan(), WINDOW
    )
    assert kept == []
    assert dropped.type == 1


def test_include_all_types_keeps_them():
    kept, dropped = retrieve.apply_filters(
        [make_candidate(doi="10.1000/a", raw_type="erratum")],
        make_plan(),
        WINDOW,
        include_all_types=True,
    )
    assert len(kept) == 1
    assert dropped.type == 0


def test_a_dissertation_is_not_mistaken_for_paratext():
    kept, _ = retrieve.apply_filters(
        [make_candidate(doi="10.1000/a", raw_type="dissertation", work_type=WorkType.other)],
        make_plan(),
        WINDOW,
    )
    assert len(kept) == 1


def test_window_filter_uses_the_publication_date():
    kept, dropped = retrieve.apply_filters(
        [
            make_candidate(doi="10.1000/a", publication_date="2019-01-01"),
            make_candidate(doi="10.1000/b", publication_date="2024-06-01"),
        ],
        make_plan(),
        WINDOW,
    )
    assert [candidate.ids.doi for candidate in kept] == ["10.1000/b"]
    assert dropped.window == 1


def test_window_filter_falls_back_to_the_year_and_keeps_undated_records():
    kept, _ = retrieve.apply_filters(
        [
            make_candidate(doi="10.1000/a", year=2019, publication_date=None),
            make_candidate(doi="10.1000/b", year=2024, publication_date=None),
            make_candidate(doi="10.1000/c", year=None, publication_date=None),
        ],
        make_plan(),
        WINDOW,
    )
    assert [candidate.ids.doi for candidate in kept] == ["10.1000/b", "10.1000/c"]


def test_no_include_preprints_drops_them():
    kept, dropped = retrieve.apply_filters(
        [
            make_candidate(doi="10.1000/a", work_type=WorkType.preprint, raw_type="preprint"),
            make_candidate(doi="10.1000/b"),
        ],
        make_plan(),
        WINDOW,
        include_preprints=False,
    )
    assert len(kept) == 1
    assert dropped.preprint == 1


def test_preprints_are_kept_by_default():
    kept, dropped = retrieve.apply_filters(
        [make_candidate(doi="10.1000/a", work_type=WorkType.preprint, raw_type="preprint")],
        make_plan(),
        WINDOW,
    )
    assert len(kept) == 1
    assert dropped.preprint == 0


def test_each_drop_is_counted_once_under_its_first_reason():
    plan = make_plan(must_not=["cryptocurrency"])
    kept, dropped = retrieve.apply_filters(
        [
            make_candidate(
                title="Retracted cryptocurrency study", doi="10.1000/a", is_retracted=True
            )
        ],
        plan,
        WINDOW,
    )
    assert kept == []
    assert dropped.retracted == 1
    assert dropped.must_not == 0


# --- §8.4 cap ---------------------------------------------------------------


def candidates_for(query_id: str, count: int, offset: int = 0):
    return [
        make_candidate(
            title=f"{query_id} paper {rank}",
            doi=f"10.1000/{query_id}-{rank}",
            origins=[
                Origin(
                    source=SourceName.openalex,
                    relation=Relation.query,
                    query_id=query_id,
                    rank=rank,
                )
            ],
        )
        for rank in range(offset, offset + count)
    ]


def test_cap_takes_from_every_query_before_taking_a_second_from_any():
    plan = make_plan()
    pool = candidates_for("Q1", 30) + candidates_for("Q2", 30)

    kept, dropped = retrieve.cap_round_robin(pool, plan, 10)

    assert len(kept) == 10
    assert dropped == 50
    by_query = [candidate.origins[0].query_id for candidate in kept]
    assert by_query.count("Q1") == 5
    assert by_query.count("Q2") == 5


def test_cap_does_not_let_one_query_dominate():
    plan = make_plan()
    pool = candidates_for("Q1", 100) + candidates_for("Q2", 3)

    kept, _ = retrieve.cap_round_robin(pool, plan, 10)

    assert [candidate.origins[0].query_id for candidate in kept].count("Q2") == 3


def test_cap_prefers_better_ranks_within_a_query():
    plan = make_plan()
    pool = candidates_for("Q1", 10)

    kept, _ = retrieve.cap_round_robin(pool, plan, 3)

    assert [candidate.origins[0].rank for candidate in kept] == [0, 1, 2]


def test_cap_keeps_a_multi_query_candidate_exactly_once():
    plan = make_plan()
    shared = make_candidate(
        doi="10.1000/shared",
        origins=[
            Origin(source=SourceName.openalex, relation=Relation.query, query_id="Q1", rank=0),
            Origin(source=SourceName.s2, relation=Relation.query, query_id="Q2", rank=0),
        ],
    )
    kept, _ = retrieve.cap_round_robin([shared, *candidates_for("Q1", 5)], plan, 4)

    assert sum(1 for candidate in kept if candidate.ids.doi == "10.1000/shared") == 1


def test_cap_below_the_limit_drops_nothing():
    plan = make_plan()
    pool = candidates_for("Q1", 3) + candidates_for("Q2", 2)
    kept, dropped = retrieve.cap_round_robin(pool, plan, 250)
    assert len(kept) == 5
    assert dropped == 0


def test_cap_is_deterministic():
    plan = make_plan()
    pool = candidates_for("Q1", 20) + candidates_for("Q3", 20)
    first = [candidate.ids.doi for candidate in retrieve.cap_round_robin(pool, plan, 7)[0]]
    second = [candidate.ids.doi for candidate in retrieve.cap_round_robin(pool, plan, 7)[0]]
    assert first == second


# --- §9.3 batches -----------------------------------------------------------


def test_batches_are_numbered_and_capped_at_twenty_five(tmp_path):
    plan = make_plan()
    pool = [
        make_candidate(title=f"Paper {n}", doi=f"10.1000/{n}", abstract="x" * 900)
        for n in range(60)
    ]

    ids = retrieve.write_batches(tmp_path, pool, plan)

    assert ids == ["01", "02", "03"]
    first = ScreenBatch.model_validate(
        json.loads((tmp_path / "screen-batches" / "01.json").read_text())
    )
    assert first.batch == "01"
    assert len(first.items) == 25
    assert len(first.sub_criteria) == 3
    assert first.sub_criteria[0].id == "C1"
    assert len(first.items[0].abstract_600) == 600


def test_batch_items_carry_provenance_but_not_identifiers(tmp_path):
    plan = make_plan()
    candidate = make_candidate(
        doi="10.1000/a",
        venue="Journal of Defaults",
        origins=[
            Origin(source=SourceName.openalex, relation=Relation.query, query_id="Q1", rank=0),
            Origin(source=SourceName.s2, relation=Relation.query, query_id="Q2", rank=1),
        ],
    )

    retrieve.write_batches(tmp_path, [candidate], plan)
    payload = json.loads((tmp_path / "screen-batches" / "01.json").read_text())

    item = payload["items"][0]
    assert item["origin_count"] == 2
    assert item["venue"] == "Journal of Defaults"
    assert set(item) == {
        "cid",
        "title",
        "abstract_600",
        "year",
        "venue",
        "origin_count",
        "outside_window",
    }


def test_batch_falls_back_to_the_tldr_when_there_is_no_abstract(tmp_path):
    retrieve.write_batches(
        tmp_path,
        [make_candidate(doi="10.1000/a", abstract=None, tldr="Defaults win.")],
        make_plan(),
    )
    payload = json.loads((tmp_path / "screen-batches" / "01.json").read_text())
    assert payload["items"][0]["abstract_600"] == "Defaults win."


def test_rewriting_batches_clears_stale_ones_but_not_expansion_batches(tmp_path):
    plan = make_plan()
    batch_dir = tmp_path / "screen-batches"
    batch_dir.mkdir()
    (batch_dir / "07.json").write_text("stale")
    (batch_dir / "x01.json").write_text("expansion")

    retrieve.write_batches(tmp_path, [make_candidate(doi="10.1000/a")], plan)

    assert not (batch_dir / "07.json").exists()
    assert (batch_dir / "x01.json").read_text() == "expansion"
    assert (batch_dir / "01.json").exists()


# --- anchors (S4.5) ---------------------------------------------------------


class FakeAnchorSource(FakeSource):
    """FakeSource plus the DOI-lookup path anchors use."""

    def __init__(self, name, results=None, by_doi=None, fail=None):
        super().__init__(name, results or {}, fail)
        self._by_doi = by_doi or {}
        self.doi_lookups: list[str] = []

    def get_by_doi(self, doi, *, cache=None):
        self.doi_lookups.append(doi)
        return self._by_doi.get(doi)


def anchor_plan(*anchors: dict):
    payload = make_plan().model_dump(mode="json", by_alias=True)
    payload["anchors"] = list(anchors)
    return make_plan(**payload)


def test_an_anchor_resolves_by_doi_and_bypasses_the_window():
    classic = make_candidate(
        title="Save More Tomorrow", doi="10.1086/380085", year=2004, publication_date="2004-02-01"
    )
    source = FakeAnchorSource(SourceName.openalex, by_doi={"10.1086/380085": classic})
    plan = anchor_plan({"doi": "10.1086/380085"})

    resolved = retrieve.resolve_anchors(plan.anchors, {SourceName.openalex: source}, WINDOW)

    assert len(resolved) == 1
    pinned = resolved[0]
    assert source.doi_lookups == ["10.1086/380085"]
    assert pinned.origins[0].relation is Relation.anchor
    assert pinned.outside_window is True  # 2004 is before the window: tagged, never dropped
    assert pinned.cid  # stamped


def test_an_anchor_resolves_by_near_exact_title():
    paper = make_candidate(
        title="Save More Tomorrow: Using Behavioral Economics", doi="10.1086/380085"
    )
    source = FakeAnchorSource(
        SourceName.openalex,
        results={"Save More Tomorrow: Using Behavioral Economics": [paper]},
    )
    plan = anchor_plan({"title": "Save More Tomorrow: Using Behavioral Economics"})

    resolved = retrieve.resolve_anchors(plan.anchors, {SourceName.openalex: source}, WINDOW)

    assert len(resolved) == 1
    assert resolved[0].origins[0].relation is Relation.anchor


def test_a_merely_similar_title_does_not_resolve_an_anchor():
    """An anchor pinned to the wrong paper would seed expansion around the wrong neighbourhood."""
    wrong = make_candidate(title="Save Less Yesterday: A Different Paper Entirely", doi="10.1000/x")
    source = FakeAnchorSource(
        SourceName.openalex,
        results={"Save More Tomorrow: Using Behavioral Economics": [wrong]},
    )
    plan = anchor_plan({"title": "Save More Tomorrow: Using Behavioral Economics"})

    resolved = retrieve.resolve_anchors(plan.anchors, {SourceName.openalex: source}, WINDOW)

    assert resolved == []


def test_an_unresolvable_anchor_is_recorded_not_silent():
    events = []
    source = FakeAnchorSource(SourceName.openalex)
    plan = anchor_plan({"doi": "10.9999/nowhere"})

    resolved = retrieve.resolve_anchors(
        plan.anchors,
        {SourceName.openalex: source},
        WINDOW,
        on_event=lambda event, **fields: events.append((event, fields)),
    )

    assert resolved == []
    assert any(event == "anchor_unresolved" for event, _ in events)


def test_an_anchor_found_by_a_query_merges_rather_than_duplicates():
    from research_scan.dedup import deduplicate, with_cid

    query_hit = with_cid(make_candidate(title="Shared paper", doi="10.1000/shared", query_id="Q1"))
    anchor_copy = with_cid(
        make_candidate(
            title="Shared paper",
            doi="10.1000/shared",
            origins=[Origin(source=SourceName.openalex, relation=Relation.anchor, rank=0)],
        )
    )

    merged, _ = deduplicate([query_hit, anchor_copy])

    assert len(merged) == 1
    relations = {origin.relation for origin in merged[0].origins}
    assert Relation.anchor in relations and Relation.query in relations


def test_fan_out_records_the_auth_mode_per_source():
    """The run dir must be able to answer "was this authenticated?" without a live probe.

    A 429 from an anonymous client and a 429 from a keyed one are different bugs; the topic-2
    diagnostic could not tell them apart from `retrieval.log.jsonl` alone.
    """
    plan = make_plan()
    sources = {
        SourceName.openalex: FakeSource(SourceName.openalex, {}),
        SourceName.s2: FakeSource(SourceName.s2, {}),
    }
    events: list[tuple[str, dict]] = []

    _, stats, _ = retrieve.fan_out(
        plan,
        sources,
        WINDOW,
        per_query=20,
        settings=KEYED,
        on_event=lambda event, **fields: events.append((event, fields)),
    )

    assert stats["s2"].auth == "key"
    assert stats["openalex"].auth == "anon"  # KEYED carries only S2_API_KEY
    assert all(
        fields["auth"] == ("key" if fields["source"] == "s2" else "anon")
        for event, fields in events
        if event == "source_query"
    )


def test_default_cap_scales_with_built_source_count():
    """450 was measured against two sources; a routed third must not shrink per-source depth.

    Routing arXiv in without scaling made the round-robin cap displace a golden paper sitting 36
    deep in an S2 query (S10g) — the cap guards against one query dominating, not against depth.
    """
    assert retrieve.scaled_max_candidates(1) == 225
    assert retrieve.scaled_max_candidates(2) == retrieve.DEFAULT_MAX_CANDIDATES == 450
    assert retrieve.scaled_max_candidates(3) == 675
    assert retrieve.scaled_max_candidates(0) == 225  # degenerate, never routed in practice
