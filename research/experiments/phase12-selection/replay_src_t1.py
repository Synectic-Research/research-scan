"""Ship gate for the v0.6.0 shortlist key: does `src` reproduce Phase-1.2A's T1, and what does
the `cid` tier move?

Two parts, both replay — no model calls, no network, and no artefact under this tree is edited.

  (a) `research_scan.shortlist`'s new key, run **without** its final `cid ASC` tier, must
      reproduce this arc's T1 ordering cid-for-cid on all six frozen inputs, at every swept cap
      and in both windows. Phase-1.2A's `sweep.py` is imported, not re-implemented, so the
      comparison is against the ordering that arc actually measured.
  (b) With `cid ASC` enabled, every position that differs from (a) must sit inside a group whose
      rows are fully tied on all five preceding fields. The count of moved rows is reported.

Usage:  python replay_src_t1.py [--json results/src-t1-replay.json]
"""

from __future__ import annotations

import argparse
import json
import sys
from pathlib import Path

HERE = Path(__file__).resolve().parent
REPO = HERE.parents[2]
sys.path.insert(0, str(HERE))
sys.path.insert(0, str(REPO / "src"))

import sweep as S  # noqa: E402

from research_scan import shortlist  # noqa: E402
from research_scan.coverage import KEPT_SCORE  # noqa: E402
from research_scan.schema import Candidate, ScoredCandidate, ScreenFile  # noqa: E402

CAPS = [40, 60, 80, 120, None]
UNCAPPED = 10**9


def src_inputs(run: S.Run) -> tuple[list[Candidate], ScreenFile, set[str], dict[str, int]]:
    """The same recorded files the sweep reads, as the shipped contracts see them.

    The overlay arms carry their `criteria_hit` from `p-standard-*` exactly as `sweep.features`
    applies it, so both implementations are handed one identical attribution.
    """
    data = run.load()
    candidates = [Candidate.model_validate(raw) for raw in data["candidates"].values()]
    rows = []
    for cid, entry in data["screen"].items():
        hits = entry.get("criteria_hit") or data["overlay"].get(cid) or []
        rows.append(
            {
                "cid": cid,
                "score": entry["score"],
                "reason": entry.get("reason") or "recorded",
                "criteria_hit": list(hits),
            }
        )
    screen = ScreenFile.model_validate({"scores": rows})
    known = set(data["criteria"])
    supported = {
        entry.cid: shortlist.criteria_supported(entry.criteria_hit, known)
        for entry in screen.scores
    }
    return candidates, screen, known, supported


def scored_pool(candidates: list[Candidate], screen: ScreenFile) -> list[ScoredCandidate]:
    """`build`'s own pool, in `candidates.json` order — what a stable sort resolves ties to."""
    scores = {entry.cid: entry.score for entry in screen.scores}
    return [
        ScoredCandidate(**candidate.model_dump(), score=scores[candidate.cid])
        for candidate in candidates
        if scores.get(candidate.cid, 0) >= KEPT_SCORE
    ]


def src_order(
    pool: list[ScoredCandidate], supported: dict[str, int], *, with_cid: bool
) -> tuple[list[str], list[str]]:
    """The shipped key, optionally minus its last tier. Everything else is `build`'s own logic."""

    def key(item: ScoredCandidate) -> tuple:
        full = shortlist.order_key(item, supported.get(item.cid, 0))
        return full if with_cid else full[:-1]

    inside = sorted((item for item in pool if not item.outside_window), key=key)
    outside = sorted((item for item in pool if item.outside_window), key=key)
    return [item.cid for item in inside], [item.cid for item in outside]


def tie_prefix(pool: list[ScoredCandidate], supported: dict[str, int]) -> dict[str, tuple]:
    return {
        item.cid: shortlist.order_key(item, supported.get(item.cid, 0))[:-1] for item in pool
    }


def moved_rows(before: list[str], after: list[str], prefixes: dict[str, tuple]) -> dict:
    """Positions that changed, and whether each change stayed inside a full-tie band."""
    moved = [(i, b, a) for i, (b, a) in enumerate(zip(before, after, strict=True)) if b != a]
    outside_ties = [
        {"position": i, "without_cid": b, "with_cid": a}
        for i, b, a in moved
        if prefixes[b] != prefixes[a]
    ]
    return {
        "rows": len(before),
        "moved": len(moved),
        "moved_cids": sorted({cid for _, b, a in moved for cid in (b, a)}),
        "reordered_outside_a_tie_band": outside_ties,
        "membership_identical_uncapped": sorted(before) == sorted(after),
    }


def check_run(run: S.Run) -> dict:
    data = run.load()
    candidates, screen, known, supported = src_inputs(run)
    pool = scored_pool(candidates, screen)

    # The sweep's own features, so (a) compares orderings rather than two readings of one file.
    sweep_pool = [
        S.features(cid, data)
        for cid in data["candidates"]
        if data["screen"].get(cid, {}).get("score", 0) >= KEPT_SCORE
    ]
    raw_counts = {f["cid"]: f["criteria_supported"] for f in sweep_pool}
    attribution = {
        "rows_with_criteria_hit": sum(1 for f in sweep_pool if f["criteria_supported"]),
        "rows_where_unique_and_valid_differs": sorted(
            cid for cid, count in raw_counts.items() if count != supported.get(cid, 0)
        ),
    }

    without_in, without_out = src_order(pool, supported, with_cid=False)
    with_in, with_out = src_order(pool, supported, with_cid=True)

    part_a = {}
    for cap in CAPS:
        want_in, want_out, _ = S.build(sweep_pool, data["criteria"], "T1", cap)
        limit = UNCAPPED if cap is None else cap
        part_a[f"T1@{cap or 'inf'}"] = {
            "in_window_identical": [f["cid"] for f in want_in] == without_in[:limit],
            "outside_window_identical": [f["cid"] for f in want_out]
            == without_out[: shortlist.DEFAULT_MAX_OUTSIDE_WINDOW],
            "in_window_rows": len(want_in),
            "outside_window_rows": len(want_out),
        }

    prefixes = tie_prefix(pool, supported)
    part_b = {
        "in_window": moved_rows(without_in, with_in, prefixes),
        "outside_window": moved_rows(without_out, with_out, prefixes),
        "membership_at_shipped_caps": {
            "in_window_40_identical": sorted(without_in[:40]) == sorted(with_in[:40]),
            "outside_window_12_identical": sorted(without_out[:12]) == sorted(with_out[:12]),
        },
    }

    # The shipped call path, end to end, at the shipped caps — build(), not a re-sort.
    built = shortlist.build(candidates, screen, known_criteria=known)
    part_b["build_matches_with_cid_arm"] = (
        [row.cid for row in built.in_window] == with_in[: shortlist.DEFAULT_MAX_IN_WINDOW]
        and [row.cid for row in built.outside_window]
        == with_out[: shortlist.DEFAULT_MAX_OUTSIDE_WINDOW]
    )

    return {
        "key": run.key,
        "label": run.label,
        "run_dir": str(run.run_dir.relative_to(REPO)),
        "criteria_overlay": str(run.criteria_from.relative_to(REPO)) if run.criteria_from else None,
        "pool_ge2": len(pool),
        "pool_in_window": len(without_in),
        "pool_outside_window": len(without_out),
        "attribution": attribution,
        "part_a_reproduces_phase12a_t1": part_a,
        "part_b_cid_tier": part_b,
    }


def main() -> None:
    ap = argparse.ArgumentParser()
    ap.add_argument("--json", default=str(HERE / "results" / "src-t1-replay.json"))
    ap.add_argument(
        "--fixtures",
        nargs="?",
        const=str(REPO / "tests/fixtures/shortlist-phase12a-t1.json"),
        default=None,
        help="Also write the repo's regression-lock fixture.",
    )
    args = ap.parse_args()

    results = [check_run(run) for run in S.RUNS]
    part_a_ok = all(
        cfg["in_window_identical"] and cfg["outside_window_identical"]
        for r in results
        for cfg in r["part_a_reproduces_phase12a_t1"].values()
    )
    part_b_ok = all(
        not r["part_b_cid_tier"][window]["reordered_outside_a_tie_band"]
        and r["part_b_cid_tier"][window]["membership_identical_uncapped"]
        for r in results
        for window in ("in_window", "outside_window")
    )
    build_ok = all(r["part_b_cid_tier"]["build_matches_with_cid_arm"] for r in results)
    affected = sum(
        r["part_b_cid_tier"][window]["moved"]
        for r in results
        for window in ("in_window", "outside_window")
    )

    summary = {
        "part_a_all_six_inputs_reproduce_t1": part_a_ok,
        "part_b_every_reordering_inside_a_tie_band": part_b_ok,
        "build_matches_the_with_cid_arm": build_ok,
        "cid_affected_rows_total": affected,
        "runs": results,
    }
    out = Path(args.json)
    out.parent.mkdir(parents=True, exist_ok=True)
    out.write_text(json.dumps(summary, indent=1))

    for r in results:
        b = r["part_b_cid_tier"]
        print(
            f"{r['key']:18s} pool>=2 {r['pool_ge2']:4d}  "
            f"(a) {'OK ' if all(c['in_window_identical'] and c['outside_window_identical'] for c in r['part_a_reproduces_phase12a_t1'].values()) else 'FAIL'}  "
            f"(b) moved in/out {b['in_window']['moved']}/{b['outside_window']['moved']}  "
            f"outside-tie-band {len(b['in_window']['reordered_outside_a_tie_band'])}"
        )
    if args.fixtures:
        write_fixtures(Path(args.fixtures))
    print(f"\npart (a) {part_a_ok} · part (b) {part_b_ok} · build {build_ok} · "
          f"cid-affected rows {affected}\nwrote {out}")



def fixture_for(run: S.Run) -> dict:
    """The gate's inputs and both orderings, small enough to live in `tests/fixtures/`.

    Only the fields the order reads are carried, and only rows that clear the screening
    threshold: everything else is irrelevant to a shortlist ordering and would make the
    regression lock a copy of two run directories, four of which are not in the repo.
    """
    data = run.load()
    candidates, screen, known, supported = src_inputs(run)
    pool = scored_pool(candidates, screen)
    hits = {entry.cid: entry.criteria_hit for entry in screen.scores}

    without_in, without_out = src_order(pool, supported, with_cid=False)
    with_in, with_out = src_order(pool, supported, with_cid=True)
    want_in, want_out, _ = S.build(
        [
            S.features(cid, data)
            for cid in data["candidates"]
            if data["screen"].get(cid, {}).get("score", 0) >= KEPT_SCORE
        ],
        data["criteria"],
        "T1",
        None,
    )
    assert [f["cid"] for f in want_in] == without_in
    assert [f["cid"] for f in want_out] == without_out[: shortlist.DEFAULT_MAX_OUTSIDE_WINDOW]

    fixture = {
        "run": run.key,
        "label": run.label,
        "source": str(run.run_dir.relative_to(REPO)),
        "criteria": sorted(known),
        "phase12a_t1": {"in_window": without_in, "outside_window": without_out},
        "with_cid_tier": {"in_window": with_in, "outside_window": with_out},
    }
    if run.criteria_from is not None:
        # An overlay arm is its base arm's pool plus one attribution, and saying so keeps the
        # fixture from carrying a second copy of 301 identical rows.
        fixture["pool_from"] = next(
            other.key for other in S.RUNS if other.run_dir == run.run_dir and other.criteria_from is None
        )
        fixture["criteria_overlay"] = str(run.criteria_from.relative_to(REPO))
        fixture["criteria_hit"] = {
            item.cid: hits[item.cid] for item in pool if hits.get(item.cid)
        }
        return fixture
    fixture["pool"] = [
        {
            "cid": item.cid,
            "score": item.score,
            "criteria_hit": hits.get(item.cid, []),
            "ranks": [origin.rank for origin in item.origins],
            "date": item.publication_date,
            "outside_window": item.outside_window,
        }
        for item in pool
    ]
    return fixture


def write_fixtures(path: Path) -> None:
    payload = {
        "what": (
            "Phase-1.2A's frozen shortlist inputs, reduced to the fields the order reads, with"
            " the T1 ordering that arc measured and the same ordering under the shipped cid tier."
        ),
        "generated_by": "research/experiments/phase12-selection/replay_src_t1.py --fixtures",
        "runs": [fixture_for(run) for run in S.RUNS],
    }
    path.parent.mkdir(parents=True, exist_ok=True)
    path.write_text(json.dumps(payload, indent=1))
    print(f"wrote {path} ({path.stat().st_size // 1024} KB)")

if __name__ == "__main__":
    main()
