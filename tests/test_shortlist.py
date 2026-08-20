"""Coverage validation and the ordered cut (spec §8.7, §9.6)."""

from __future__ import annotations

from conftest import make_candidate
from research_scan import shortlist
from research_scan.dedup import with_cid
from research_scan.schema import Origin, Relation, ScreenFile, SourceName


def screen(*pairs: tuple[str, int]) -> ScreenFile:
    return ScreenFile.model_validate(
        {"scores": [{"cid": cid, "score": score, "reason": "why"} for cid, score in pairs]}
    )


def pool(*specs) -> list:
    return [
        with_cid(make_candidate(title=title, doi=doi, **kwargs)) for title, doi, kwargs in specs
    ]


# --- coverage ---------------------------------------------------------------


def test_full_coverage_is_ok():
    candidates = pool(("A", "10.1000/a", {}), ("B", "10.1000/b", {}))
    report = shortlist.validate_coverage(
        candidates, screen((candidates[0].cid, 3), (candidates[1].cid, 1))
    )
    assert report.ok
    assert report.lines() == []


def test_a_missing_score_is_reported_with_its_cid():
    candidates = pool(("A", "10.1000/a", {}), ("B", "10.1000/b", {}))
    report = shortlist.validate_coverage(candidates, screen((candidates[0].cid, 3)))

    assert not report.ok
    assert report.missing == [candidates[1].cid]
    assert candidates[1].cid in report.lines()[0]


def test_a_duplicate_score_is_reported():
    candidates = pool(("A", "10.1000/a", {}))
    report = shortlist.validate_coverage(
        candidates, screen((candidates[0].cid, 3), (candidates[0].cid, 2))
    )
    assert report.duplicate == [candidates[0].cid]
    assert "duplicate" in report.lines()[0]


def test_a_score_for_an_unknown_cid_is_reported():
    candidates = pool(("A", "10.1000/a", {}))
    report = shortlist.validate_coverage(
        candidates, screen((candidates[0].cid, 3), ("deadbeef0000", 3))
    )
    assert report.unknown == ["deadbeef0000"]
    assert "not in candidates.json" in report.lines()[0]


def test_the_report_samples_rather_than_printing_hundreds():
    candidates = pool(*[(f"P{n}", f"10.1000/{n}", {}) for n in range(30)])
    report = shortlist.validate_coverage(candidates, screen())
    assert "+20 more" in report.lines()[0]


# --- ordering and cuts ------------------------------------------------------


def test_only_papers_scored_two_or_more_reach_the_reranker():
    candidates = pool(("Central", "10.1000/a", {}), ("Tangential", "10.1000/b", {}))
    result = shortlist.build(candidates, screen((candidates[0].cid, 2), (candidates[1].cid, 1)))
    assert [item.title for item in result.in_window] == ["Central"]


def test_ordering_is_score_then_origin_count_then_recency():
    two_origins = with_cid(
        make_candidate(
            title="Two origins",
            doi="10.1000/b",
            publication_date="2024-01-01",
            origins=[
                Origin(source=SourceName.openalex, relation=Relation.query, query_id="Q1", rank=0),
                Origin(source=SourceName.s2, relation=Relation.query, query_id="Q2", rank=0),
            ],
        )
    )
    newer = with_cid(make_candidate(title="Newer", doi="10.1000/c", publication_date="2026-01-01"))
    top = with_cid(
        make_candidate(title="Top score", doi="10.1000/a", publication_date="2023-01-01")
    )

    result = shortlist.build(
        [newer, two_origins, top],
        screen((top.cid, 3), (two_origins.cid, 2), (newer.cid, 2)),
    )

    assert [item.title for item in result.in_window] == ["Top score", "Two origins", "Newer"]


def test_the_two_windows_are_cut_separately():
    in_window = pool(*[(f"In {n}", f"10.1000/i{n}", {}) for n in range(50)])
    outside = [
        with_cid(make_candidate(title=f"Out {n}", doi=f"10.1000/o{n}")).model_copy(
            update={"outside_window": True}
        )
        for n in range(15)
    ]
    all_candidates = in_window + outside
    scores = screen(*[(candidate.cid, 3) for candidate in all_candidates])

    result = shortlist.build(all_candidates, scores)

    assert len(result.in_window) == shortlist.DEFAULT_MAX_IN_WINDOW
    assert len(result.outside_window) == shortlist.DEFAULT_MAX_OUTSIDE_WINDOW


def test_caps_are_overridable():
    candidates = pool(*[(f"P{n}", f"10.1000/{n}", {}) for n in range(10)])
    result = shortlist.build(
        candidates,
        screen(*[(c.cid, 3) for c in candidates]),
        max_in_window=4,
        max_outside_window=1,
    )
    assert len(result.in_window) == 4


def test_shortlist_rows_are_full_records_carrying_their_score():
    candidates = pool(("A", "10.1000/a", {"abstract": "Full text here.", "venue": "A Journal"}))
    result = shortlist.build(candidates, screen((candidates[0].cid, 3)))

    row = result.in_window[0]
    assert row.score == 3
    assert row.abstract == "Full text here."
    assert row.venue == "A Journal"
    assert row.ids.doi == "10.1000/a"


def test_the_outside_window_default_is_twelve():
    """Raised from 5 in S4.5: the smaller cap discarded screened-3 classics before reranking."""
    assert shortlist.DEFAULT_MAX_OUTSIDE_WINDOW == 12
