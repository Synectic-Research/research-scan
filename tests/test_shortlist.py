"""Coverage validation and the ordered cut (spec §8.7, §9.6)."""

from __future__ import annotations

import itertools
import json
from pathlib import Path

import pytest
from pydantic import ValidationError

from conftest import make_candidate
from research_scan import shortlist
from research_scan.dedup import with_cid
from research_scan.schema import (
    Candidate,
    Origin,
    Relation,
    ScoredCandidate,
    ScreenFile,
    ScreenScore,
    SourceName,
)


def screen(*pairs: tuple[str, int]) -> ScreenFile:
    return ScreenFile.model_validate(
        {"scores": [{"cid": cid, "score": score, "reason": "why"} for cid, score in pairs]}
    )


def attributed(*triples: tuple[str, int, list[str]]) -> ScreenFile:
    """A screen file carrying `criteria_hit`, which is what the v0.2+ contract requires at ≥ 2."""
    return ScreenFile.model_validate(
        {
            "scores": [
                {"cid": cid, "score": score, "reason": "why", "criteria_hit": hits}
                for cid, score, hits in triples
            ]
        }
    )


def candidate(cid: str, **kwargs) -> Candidate:
    """A candidate with an explicit cid — the order's last tier needs cids it can distinguish."""
    return make_candidate(cid=cid, **kwargs)


def origins(*ranks: int) -> list[Origin]:
    return [
        Origin(source=SourceName.openalex, relation=Relation.query, query_id=f"Q{n}", rank=rank)
        for n, rank in enumerate(ranks, start=1)
    ]


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


def test_ordering_is_score_then_origin_count_then_recency_when_nothing_else_separates():
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


# --- the T1 lexicographic order (v0.6.0) ------------------------------------


def test_criteria_supported_outranks_origin_count_and_recency():
    """The tier that fixes the defect: breadth of criteria beats both the count and the date."""
    broad = candidate("aaaaaaaaaaaa", title="Two criteria", publication_date="2023-01-01")
    narrow = candidate(
        "bbbbbbbbbbbb",
        title="One criterion, two origins, newer",
        publication_date="2026-01-01",
        origins=origins(0, 3),
    )

    result = shortlist.build(
        [narrow, broad],
        attributed((broad.cid, 3, ["C1", "C2"]), (narrow.cid, 3, ["C1"])),
    )

    assert [row.title for row in result.in_window] == [
        "Two criteria",
        "One criterion, two origins, newer",
    ]


def test_best_retrieval_rank_outranks_recency():
    """Where the screen cannot separate two papers, what the sources ranked higher wins."""
    ranked_first = candidate("aaaaaaaaaaaa", title="Rank 1", publication_date="2023-01-01",
                             origins=origins(1))
    ranked_later = candidate("bbbbbbbbbbbb", title="Rank 30", publication_date="2026-01-01",
                             origins=origins(30))

    result = shortlist.build(
        [ranked_later, ranked_first],
        attributed((ranked_first.cid, 3, ["C1"]), (ranked_later.cid, 3, ["C1"])),
    )

    assert [row.title for row in result.in_window] == ["Rank 1", "Rank 30"]


def test_best_retrieval_rank_is_the_best_of_every_origin():
    assert shortlist.best_retrieval_rank(candidate("aaaaaaaaaaaa", origins=origins(9, 2, 40))) == 2


def test_a_candidate_with_no_origin_sorts_behind_every_ranked_one():
    graph_only = candidate("aaaaaaaaaaaa", title="No origin", origins=[])
    ranked = candidate("bbbbbbbbbbbb", title="Ranked last page", origins=origins(199))

    result = shortlist.build(
        [graph_only, ranked],
        attributed((graph_only.cid, 3, ["C1"]), (ranked.cid, 3, ["C1"])),
    )

    assert shortlist.best_retrieval_rank(graph_only) == shortlist.NO_RETRIEVAL_RANK
    assert [row.title for row in result.in_window] == ["Ranked last page", "No origin"]


def test_recency_still_breaks_a_tie_the_earlier_tiers_leave():
    older = candidate("aaaaaaaaaaaa", title="Older", publication_date="2024-01-01")
    newer = candidate("bbbbbbbbbbbb", title="Newer", publication_date="2026-01-01")

    result = shortlist.build(
        [older, newer], attributed((older.cid, 3, ["C1"]), (newer.cid, 3, ["C1"]))
    )

    assert [row.title for row in result.in_window] == ["Newer", "Older"]


def test_a_paper_with_no_date_sorts_last_within_its_band():
    dated = candidate("aaaaaaaaaaaa", title="Dated", publication_date="2024-01-01")
    undated = candidate("bbbbbbbbbbbb", title="Undated", publication_date=None)

    result = shortlist.build(
        [undated, dated], attributed((dated.cid, 3, ["C1"]), (undated.cid, 3, ["C1"]))
    )

    assert [row.title for row in result.in_window] == ["Dated", "Undated"]


def test_cid_is_the_final_tie_break_so_the_order_is_total():
    """Fully tied rows resolve on cid, not on the order `candidates.json` happened to carry."""
    rows = [
        candidate(cid, title=cid, publication_date="2025-01-01")
        for cid in ("cccccccccccc", "aaaaaaaaaaaa", "bbbbbbbbbbbb")
    ]
    scores = attributed(*[(row.cid, 3, ["C1"]) for row in rows])

    forward = shortlist.build(rows, scores)
    reversed_input = shortlist.build(list(reversed(rows)), scores)

    assert [row.cid for row in forward.in_window] == [
        "aaaaaaaaaaaa",
        "bbbbbbbbbbbb",
        "cccccccccccc",
    ]
    assert [row.cid for row in reversed_input.in_window] == [
        row.cid for row in forward.in_window
    ]


def test_the_key_is_the_documented_tier_order():
    row = candidate("aaaaaaaaaaaa", publication_date="2025-01-01", origins=origins(4, 9))
    key = shortlist.order_key(ScoredCandidate(**row.model_dump(), score=3), 2)

    assert key[:4] == (-3, -2, -2, 4)
    assert key[4] == shortlist._Descending("2025-01-01")
    assert key[5] == "aaaaaaaaaaaa"


# --- criteria_supported -----------------------------------------------------


def test_criteria_supported_counts_each_criterion_once():
    assert shortlist.criteria_supported(["C1", "C1", "C2"]) == 2


def test_criteria_supported_ignores_ids_the_plan_does_not_define():
    """`queries.json` is the authority: a typo cannot buy a place in the order."""
    assert shortlist.criteria_supported(["C1", "C9"], known={"C1", "C2"}) == 1
    assert shortlist.criteria_supported(["C1", "C9"]) == 2


def test_an_unattributed_pre_v02_screen_file_no_ops_that_tier():
    """Pre-v0.2 `screen.json` carries `criteria_hit: []`; the remaining tiers still decide."""
    two_origins = candidate("aaaaaaaaaaaa", title="Two origins", publication_date="2023-01-01",
                            origins=origins(5, 5))
    newer = candidate("bbbbbbbbbbbb", title="Newer", publication_date="2026-01-01",
                      origins=origins(5))

    result = shortlist.build(
        [newer, two_origins], screen((two_origins.cid, 3), (newer.cid, 3))
    )

    assert [row.title for row in result.in_window] == ["Two origins", "Newer"]


# --- regression lock: the Phase-1.2A frozen inputs --------------------------

#: Both topics, both eras, and the two control arms swept with and without the `p-standard`
#: attribution overlay — the six inputs Phase-1.2A measured T1 on
#: (`552f09c462dce07a7c20fa3f30e85c3264f42346:research/experiments/phase12-selection/results/
#: report_head.md` §2). The fixture carries only the fields the order reads; it is regenerated
#: by that arc's `replay_src_t1.py --fixtures`, whose run is recorded in
#: `results/src-t1-replay.json`.
PHASE12A = json.loads(
    (Path(__file__).parent / "fixtures" / "shortlist-phase12a-t1.json").read_text(encoding="utf-8")
)


def _phase12a_run(name: str) -> dict:
    return next(run for run in PHASE12A["runs"] if run["run"] == name)


def _phase12a_pool(run: dict) -> tuple[list, ScreenFile, set[str]]:
    """The frozen rows, rebuilt as the contracts `build` takes."""
    base = _phase12a_run(run["pool_from"]) if "pool_from" in run else run
    overlay = run.get("criteria_hit", {})
    candidates, scores = [], []
    for row in base["pool"]:
        candidates.append(
            make_candidate(
                cid=row["cid"],
                title=row["cid"],
                publication_date=row["date"],
                origins=origins(*row["ranks"]),
            ).model_copy(update={"outside_window": row["outside_window"]})
        )
        hits = overlay.get(row["cid"], row["criteria_hit"])
        scores.append(
            {"cid": row["cid"], "score": row["score"], "reason": "recorded", "criteria_hit": hits}
        )
    return candidates, ScreenFile.model_validate({"scores": scores}), set(run["criteria"])


@pytest.mark.parametrize("name", [run["run"] for run in PHASE12A["runs"]])
def test_the_shipped_key_without_its_cid_tier_reproduces_phase12a_t1(name):
    """Part (a) of the v0.6.0 gate: the order Phase-1.2A measured, cid for cid, uncapped."""
    run = _phase12a_run(name)
    candidates, screen_file, known = _phase12a_pool(run)
    supported = {
        entry.cid: shortlist.criteria_supported(entry.criteria_hit, known)
        for entry in screen_file.scores
    }
    scores = {entry.cid: entry.score for entry in screen_file.scores}
    rows = [
        ScoredCandidate(**item.model_dump(), score=scores[item.cid])
        for item in candidates
        if scores[item.cid] >= shortlist.SHORTLIST_SCORE_THRESHOLD
    ]

    def without_cid(item):
        return shortlist.order_key(item, supported[item.cid])[:-1]

    inside = [row.cid for row in sorted((r for r in rows if not r.outside_window), key=without_cid)]
    outside = [row.cid for row in sorted((r for r in rows if r.outside_window), key=without_cid)]

    assert inside == run["phase12a_t1"]["in_window"]
    assert outside == run["phase12a_t1"]["outside_window"]


@pytest.mark.parametrize("name", [run["run"] for run in PHASE12A["runs"]])
def test_the_cid_tier_only_reorders_rows_that_are_fully_tied(name):
    """Part (b): every position that moves is inside a band tied on all five earlier fields."""
    run = _phase12a_run(name)
    candidates, screen_file, known = _phase12a_pool(run)
    supported = {
        entry.cid: shortlist.criteria_supported(entry.criteria_hit, known)
        for entry in screen_file.scores
    }
    rows = {
        item.cid: ScoredCandidate(
            **item.model_dump(),
            score=next(e.score for e in screen_file.scores if e.cid == item.cid),
        )
        for item in candidates
    }
    prefix = {cid: shortlist.order_key(row, supported[cid])[:-1] for cid, row in rows.items()}

    for window in ("in_window", "outside_window"):
        before, after = run["phase12a_t1"][window], run["with_cid_tier"][window]
        assert sorted(before) == sorted(after)
        for was, now in zip(before, after, strict=True):
            assert prefix[was] == prefix[now]


@pytest.mark.parametrize("name", [run["run"] for run in PHASE12A["runs"]])
def test_build_reproduces_the_recorded_shipped_order(name):
    """The whole shipped path — `build`, at the shipped caps — against the recorded order."""
    run = _phase12a_run(name)
    candidates, screen_file, known = _phase12a_pool(run)

    result = shortlist.build(candidates, screen_file, known_criteria=known)

    assert [row.cid for row in result.in_window] == (
        run["with_cid_tier"]["in_window"][: shortlist.DEFAULT_MAX_IN_WINDOW]
    )
    assert [row.cid for row in result.outside_window] == (
        run["with_cid_tier"]["outside_window"][: shortlist.DEFAULT_MAX_OUTSIDE_WINDOW]
    )


# --- field domains the order depends on (v0.6.0 audit) ----------------------


@pytest.mark.parametrize("bad", [True, "2", 2.5, float("inf"), float("nan")])
def test_a_score_outside_the_int_contract_is_rejected_at_the_schema(bad):
    """The first tier reads this number: lax coercion turned `true` into 1 and `"3"` into 3."""
    with pytest.raises(ValidationError):
        ScreenFile.model_validate(
            {"scores": [{"cid": "aaaaaaaaaaaa", "score": bad, "reason": "why"}]}
        )


@pytest.mark.parametrize("bad", [True, "1", 1.5, -1])
def test_a_malformed_retrieval_rank_is_rejected_at_the_schema(bad):
    """Ranks are strict non-negative ints, so `best_retrieval_rank` never parses anything."""
    with pytest.raises(ValidationError):
        Origin(source=SourceName.openalex, relation=Relation.query, query_id="Q1", rank=bad)


def test_rank_zero_is_valid_because_ranks_are_zero_based():
    """Every source enumerates from 0; the top hit is rank 0, not rank 1."""
    assert Origin(
        source=SourceName.openalex, relation=Relation.query, query_id="Q1", rank=0
    ).rank == 0


@pytest.mark.parametrize("bad", [True, 1, None])
def test_a_non_string_criterion_id_is_rejected_at_the_schema(bad):
    with pytest.raises(ValidationError):
        ScreenFile.model_validate(
            {
                "scores": [
                    {"cid": "aaaaaaaaaaaa", "score": 2, "reason": "why", "criteria_hit": [bad]}
                ]
            }
        )


@pytest.mark.parametrize("bad", ["", "   ", "C9", "c1"])
def test_criteria_supported_ignores_empty_and_unknown_ids(bad):
    """Empty, whitespace-only, unknown and wrongly-cased ids are not criterion ids."""
    assert shortlist.criteria_supported(["C1", bad], known={"C1", "C2"}) == 1


def test_criteria_supported_dedupes_after_the_schema_normalises_whitespace():
    hits = ScreenScore(
        cid="aaaaaaaaaaaa", score=2, reason="why", criteria_hit=["  C1  ", "C1", "C2"]
    ).criteria_hit
    assert shortlist.criteria_supported(hits, known={"C1", "C2"}) == 2


@pytest.mark.parametrize("bad", ["not-a-date", "2024", "2024-03", "2024-13-01", "2024-02-30", ""])
def test_a_malformed_date_sorts_with_the_unknowns_rather_than_as_a_string(bad):
    """`"2024-13-01"` outranks `"2025-01-01"` as a raw string; as a date it is simply unknown."""
    assert shortlist.order_date(bad) == shortlist.NO_DATE

    dated = candidate("aaaaaaaaaaaa", title="Dated", publication_date="2025-01-01")
    malformed = candidate("bbbbbbbbbbbb", title="Malformed", publication_date=bad)
    result = shortlist.build(
        [malformed, dated], attributed((dated.cid, 3, ["C1"]), (malformed.cid, 3, ["C1"]))
    )
    assert [row.title for row in result.in_window] == ["Dated", "Malformed"]


def test_a_real_date_is_carried_through_unchanged():
    assert shortlist.order_date("2024-02-29") == "2024-02-29"


def test_a_duplicate_cid_is_an_error_rather_than_a_silently_dropped_paper():
    """`cid` is the order's last tier, so it has to identify exactly one row."""
    rows = [candidate("aaaaaaaaaaaa")]
    duplicated = ScreenFile.model_validate(
        {
            "scores": [
                {"cid": "aaaaaaaaaaaa", "score": 3, "reason": "first"},
                {"cid": "aaaaaaaaaaaa", "score": 2, "reason": "second"},
            ]
        }
    )

    with pytest.raises(ValueError, match="more than once"):
        shortlist.build(rows, duplicated)


def test_a_candidate_the_screen_never_named_is_left_out_rather_than_scored_zero():
    scored = candidate("aaaaaaaaaaaa", title="Scored")
    unscored = candidate("bbbbbbbbbbbb", title="Never screened")

    result = shortlist.build([scored, unscored], screen((scored.cid, 3)))

    assert [row.title for row in result.in_window] == ["Scored"]


# --- artifact-level tier policy ---------------------------------------------


def test_a_row_with_no_valid_hits_scores_zero_in_a_mixed_artifact():
    """Mixed artifact: the unattributed row is not exempted from the tier, it scores 0."""
    attributed_row = candidate("bbbbbbbbbbbb", title="Attributed", publication_date="2020-01-01")
    unattributed = candidate("aaaaaaaaaaaa", title="Unattributed", publication_date="2026-01-01")

    result = shortlist.build(
        [unattributed, attributed_row],
        attributed((attributed_row.cid, 3, ["C1"]), (unattributed.cid, 3, ["C9"])),
        known_criteria={"C1", "C2"},
    )

    # Newer and alphabetically first, and it still loses: the tier is not skipped for it.
    assert [row.title for row in result.in_window] == ["Attributed", "Unattributed"]


def test_an_artifact_where_no_row_has_a_valid_hit_orders_exactly_as_if_the_tier_were_absent():
    """Artifact-level no-op, decided before sorting — not a pairwise `skip this tier`."""
    rows = [
        candidate("aaaaaaaaaaaa", title="Two origins", publication_date="2023-01-01",
                  origins=origins(5, 5)),
        candidate("bbbbbbbbbbbb", title="Newer", publication_date="2026-01-01",
                  origins=origins(5)),
        candidate("cccccccccccc", title="Best rank", publication_date="2021-01-01",
                  origins=origins(1)),
    ]
    # Every id is unknown to the plan, so no row earns a single valid hit.
    scores = attributed(*[(row.cid, 3, ["C9", "C8"]) for row in rows])

    with_tier = shortlist.build(rows, scores, known_criteria={"C1", "C2"})
    without_tier = sorted(
        (ScoredCandidate(**row.model_dump(), score=3) for row in rows),
        key=lambda item: shortlist.order_key(item, 0),
    )

    assert [row.cid for row in with_tier.in_window] == [row.cid for row in without_tier]
    assert all(
        shortlist.criteria_supported(entry.criteria_hit, {"C1", "C2"}) == 0
        for entry in scores.scores
    )


def test_the_order_does_not_depend_on_the_order_the_pool_arrives_in():
    """Permutation invariance: a total order plus a stable sort is input-order independent."""
    rows = [
        candidate("aaaaaaaaaaaa", title="A", publication_date="2025-01-01", origins=origins(3)),
        candidate("bbbbbbbbbbbb", title="B", publication_date="2025-01-01", origins=origins(3)),
        candidate("cccccccccccc", title="C", publication_date="2025-01-01", origins=origins(3)),
        candidate("dddddddddddd", title="D", publication_date="2024-01-01", origins=origins(3)),
        candidate("eeeeeeeeeeee", title="E", publication_date="2025-01-01", origins=origins(0)),
    ]
    scores = attributed(*[(row.cid, 3, ["C1"]) for row in rows])
    expected = [row.cid for row in shortlist.build(rows, scores).in_window]

    for permutation in itertools.permutations(rows):
        assert [row.cid for row in shortlist.build(list(permutation), scores).in_window] == expected


# --- Gate B instrumentation: what the cid tier actually moved ----------------

#: The caps Phase-1.2A swept, plus the shipped in-window cap. `None` is the uncapped arm.
SWEPT_CAPS = (shortlist.DEFAULT_MAX_IN_WINDOW, 60, 80, 120, None)


def _tie_bands(order: list[str], prefix: dict[str, tuple]) -> list[list[str]]:
    """Maximal runs of rows sharing all five tiers ahead of `cid` — the classes cid may reorder."""
    bands: list[list[str]] = []
    for cid in order:
        if bands and prefix[bands[-1][0]] == prefix[cid]:
            bands[-1].append(cid)
        else:
            bands.append([cid])
    return [band for band in bands if len(band) > 1]


def gate_b_counts(name: str) -> dict:
    """Tied groups, moved rows, boundary crossings and cap intersections for one frozen input."""
    run = _phase12a_run(name)
    candidates, screen_file, known = _phase12a_pool(run)
    supported = {
        entry.cid: shortlist.criteria_supported(entry.criteria_hit, known)
        for entry in screen_file.scores
    }
    scores = {entry.cid: entry.score for entry in screen_file.scores}
    rows = {
        item.cid: ScoredCandidate(**item.model_dump(), score=scores[item.cid])
        for item in candidates
    }
    prefix = {cid: shortlist.order_key(row, supported[cid])[:-1] for cid, row in rows.items()}

    report = {"run": name, "windows": {}}
    for window, caps in (("in_window", SWEPT_CAPS), ("outside_window", (12,))):
        before = run["phase12a_t1"][window]
        after = run["with_cid_tier"][window]
        bands = _tie_bands(after, prefix)
        banded = {cid for band in bands for cid in band}
        moved = [(was, now) for was, now in zip(before, after, strict=True) if was != now]
        crossings = [(was, now) for was, now in moved if prefix[was] != prefix[now]]
        cap_cuts = []
        for cap in caps:
            if cap is None or cap >= len(after):
                continue
            # A cap intersects a tied class when it splits one: the row at the cut and the row
            # before it share every tier ahead of `cid`.
            if prefix[after[cap - 1]] == prefix[after[cap]]:
                cap_cuts.append(cap)
            assert sorted(before[:cap]) == sorted(after[:cap]) or cap in cap_cuts, (
                f"{name}/{window}: cap {cap} changed membership without cutting a tied class"
            )
        report["windows"][window] = {
            "rows": len(after),
            "tied_groups": len(bands),
            "rows_in_tied_groups": len(banded),
            "largest_tied_group": max((len(band) for band in bands), default=0),
            "rows_moved": len(moved),
            "boundary_crossings": len(crossings),
            "caps_intersecting_a_tied_group": cap_cuts,
        }
    return report


@pytest.mark.parametrize("name", [run["run"] for run in PHASE12A["runs"]])
def test_gate_b_reports_no_boundary_crossing_on_any_frozen_input(name):
    """Part (b), counted: every moved row stayed inside a class tied on all five earlier tiers."""
    report = gate_b_counts(name)

    for window, counts in report["windows"].items():
        assert counts["boundary_crossings"] == 0, f"{name}/{window}: {counts}"
        # Anything that moved has to be inside a tied group; a group is what makes it possible.
        if counts["rows_moved"]:
            assert counts["rows_in_tied_groups"] >= counts["rows_moved"]


@pytest.mark.parametrize("name", [run["run"] for run in PHASE12A["runs"]])
def test_the_shipped_order_is_byte_stable_across_repeated_runs(name):
    """A total order plus a deterministic key: the same input serialises identically every time."""
    run = _phase12a_run(name)
    candidates, screen_file, known = _phase12a_pool(run)

    renders = {
        shortlist.build(candidates, screen_file, known_criteria=known).model_dump_json()
        for _ in range(3)
    }

    assert len(renders) == 1
