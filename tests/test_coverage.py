"""Coverage counting (V1.1): attribution in, per-criterion counts out. No judgement anywhere."""

from __future__ import annotations

from conftest import make_candidate, make_plan
from research_scan import coverage
from research_scan.schema import (
    Candidate,
    CoverageFile,
    Origin,
    Profile,
    Relation,
    RunInfo,
    ScreenFile,
    SourceName,
)


def info() -> RunInfo:
    return RunInfo(
        run_dir="research/scans/2026-08-19-t",
        slug="t",
        date="2026-08-19",
        brief_path="brief.md",
        defaults={},
    )


def screen(*rows: tuple[str, int, list[str]]) -> ScreenFile:
    return ScreenFile.model_validate(
        {
            "scores": [
                {"cid": cid, "score": score, "reason": "because", "criteria_hit": hits}
                for cid, score, hits in rows
            ]
        }
    )


def candidate(cid: str, *, query_id: str | None = "Q1", seed_id: str | None = None) -> Candidate:
    relation = Relation.references if seed_id else Relation.query
    return make_candidate(
        cid=cid,
        origins=[
            Origin(
                source=SourceName.openalex,
                relation=relation,
                query_id=query_id if not seed_id else None,
                seed_id=seed_id,
                rank=1,
            )
        ],
    )


def test_a_criterion_counts_only_papers_screening_kept():
    plan = make_plan()
    pool = [candidate("a" * 12), candidate("b" * 12), candidate("c" * 12)]
    scores = screen(
        ("a" * 12, 3, ["C1"]),
        ("b" * 12, 2, ["C1", "C2"]),
        ("c" * 12, 1, ["C1"]),  # tangential: attributed, but not kept
    )
    snapshot = coverage.build(info(), plan, pool, scores).rounds[0]
    hits = {c.id: c.hits for c in snapshot.criteria}
    assert hits == {"C1": 2, "C2": 1, "C3": 0}
    assert snapshot.ge2 == 2


def test_hits_split_by_query_type_and_source():
    plan = make_plan()
    paper = make_candidate(
        cid="a" * 12,
        origins=[
            Origin(source=SourceName.openalex, relation=Relation.query, query_id="Q1", rank=1),
            Origin(source=SourceName.s2, relation=Relation.query, query_id="Q5", rank=2),
        ],
    )
    snapshot = coverage.build(info(), plan, [paper], screen(("a" * 12, 3, ["C1"]))).rounds[0]
    c1 = next(c for c in snapshot.criteria if c.id == "C1")
    assert c1.by_query_type == {"direct": 1, "review": 1}
    assert c1.by_source == {"openalex": 1, "s2": 1}


def test_a_graph_origin_reports_its_relation_not_a_query_type():
    plan = make_plan()
    paper = candidate("a" * 12, seed_id="b" * 12)
    snapshot = coverage.build(info(), plan, [paper], screen(("a" * 12, 3, ["C1"]))).rounds[0]
    c1 = next(c for c in snapshot.criteria if c.id == "C1")
    assert c1.by_query_type == {"references": 1}


def test_thin_is_a_count_not_an_opinion():
    plan = make_plan()
    pool = [candidate(f"{i:012x}") for i in range(6)]
    scores = screen(*[(f"{i:012x}", 2, ["C1"]) for i in range(6)])
    snapshot = coverage.build(info(), plan, pool, scores).rounds[0]
    thin = {c.id: c.thin for c in snapshot.criteria}
    assert thin == {"C1": False, "C2": True, "C3": True}
    assert coverage.thin_criteria(snapshot) == ["C2", "C3"]


def test_per_query_yield_counts_the_surviving_pool():
    plan = make_plan()
    pool = [candidate("a" * 12, query_id="Q1"), candidate("b" * 12, query_id="Q2")]
    scores = screen(("a" * 12, 3, ["C1"]), ("b" * 12, 0, []))
    snapshot = coverage.build(info(), plan, pool, scores).rounds[0]
    yields = {y.query_id: (y.pool, y.ge2) for y in snapshot.queries}
    assert yields["Q1"] == (1, 1)
    assert yields["Q2"] == (1, 0)
    assert yields["Q6"] == (0, 0)


def test_seed_precision_is_the_kept_share_of_a_seed_s_neighbours():
    plan = make_plan()
    seed = "e" * 12
    pool = [candidate("a" * 12, seed_id=seed), candidate("b" * 12, seed_id=seed)]
    scores = screen(("a" * 12, 3, ["C1"]), ("b" * 12, 1, []))
    snapshot = coverage.build(info(), plan, pool, scores).rounds[0]
    assert [(s.seed_id, s.neighbours, s.ge2, s.precision) for s in snapshot.seeds] == [
        (seed, 2, 1, 0.5)
    ]


def test_a_kept_paper_with_no_attribution_is_counted_not_hidden():
    plan = make_plan()
    pool = [candidate("a" * 12)]
    snapshot = coverage.build(info(), plan, pool, screen(("a" * 12, 3, []))).rounds[0]
    assert snapshot.unattributed_ge2 == 1
    assert all(c.hits == 0 for c in snapshot.criteria)


def test_the_round_comes_from_the_plan_so_re_running_replaces_its_own_snapshot():
    plan = make_plan()
    pool = [candidate("a" * 12)]
    scores = screen(("a" * 12, 3, ["C1"]))
    first = coverage.build(info(), plan, pool, scores)
    again = coverage.build(info(), plan, pool, scores, previous=first)
    assert [r.round for r in again.rounds] == [1]

    gap = make_plan(
        round2=[{"id": "G1", "type": "gap", "text": "thin thing", "target_criterion": "C2"}]
    )
    after = coverage.build(info(), gap, pool, scores, previous=again)
    assert [r.round for r in after.rounds] == [1, 2]
    assert isinstance(after, CoverageFile)


def test_an_unknown_criterion_id_is_reported_rather_than_counted_as_nothing():
    plan = make_plan()
    report = coverage.validate_criteria_hit(plan, screen(("a" * 12, 3, ["C9"])))
    assert not report.ok
    assert report.lines() == ["aaaaaaaaaaaa: unknown criterion 'C9'"]


def test_a_kept_paper_without_attribution_is_a_warning_not_a_failure():
    plan = make_plan()
    report = coverage.validate_criteria_hit(plan, screen(("a" * 12, 3, [])))
    assert report.ok
    assert report.missing == ["a" * 12]


# --- the gap-round trigger (v0.2.1) -----------------------------------------


def snapshot_with(hits: list[int], pools: list[int] | None = None) -> object:
    plan = make_plan()
    pool = []
    scores = []
    n = 0
    for criterion, count in zip(plan.sub_criteria, hits, strict=False):
        for _ in range(count):
            cid = f"{n:012x}"
            n += 1
            pool.append(candidate(cid))
            scores.append((cid, 3, [criterion.id]))
    snap = coverage.build(info(), plan, pool, screen(*scores)).rounds[0]
    if pools is not None:
        snap.queries = [
            q.model_copy(update={"pool": p}) for q, p in zip(snap.queries, pools, strict=False)
        ]
    return snap


def test_an_even_pool_does_not_pay_for_a_gap_round():
    advice = coverage.advise(
        snapshot_with([20, 20, 20], [40, 40, 40, 40, 40, 40]), Profile.standard
    )
    assert advice.should_run is False
    assert "even across the criteria" in advice.reasons[0]


def test_a_criterion_under_the_absolute_floor_fires_it():
    advice = coverage.advise(snapshot_with([3, 20, 20], [40, 40, 40, 40, 40, 40]), Profile.standard)
    assert advice.should_run is True
    assert "under 8" in advice.reasons[0]


def test_a_criterion_far_under_the_median_fires_it_even_when_it_clears_the_floor():
    """The case both reference runs are in: nothing is starved, one criterion is a fifth."""
    advice = coverage.advise(
        snapshot_with([12, 60, 100], [40, 40, 40, 40, 40, 40]), Profile.standard
    )
    assert advice.should_run is True
    assert "against a median of 60" in advice.reasons[0]


def test_a_starved_query_fires_it():
    advice = coverage.advise(snapshot_with([20, 20, 20], [40, 3, 40, 40, 40, 40]), Profile.standard)
    assert advice.should_run is True
    assert "under 20 papers" in advice.reasons[0]


def test_quick_never_runs_it_and_deep_always_does():
    even = snapshot_with([20, 20, 20], [40, 40, 40, 40, 40, 40])
    assert coverage.advise(even, Profile.quick).should_run is False
    assert coverage.advise(even, Profile.deep).should_run is True


def test_the_flag_overrides_the_profile_and_the_counts():
    even = snapshot_with([20, 20, 20], [40, 40, 40, 40, 40, 40])
    advice = coverage.advise(even, Profile.quick, forced=True)
    assert advice.should_run is True
    assert advice.forced is True
