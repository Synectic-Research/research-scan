"""Phase-1.4 — the metric layer. Written and committed before the first replicate was run.

Golden matching is never re-derived by hand: `evalrun.matches` from the shipped package decides
whether a candidate is a golden paper, exactly as `evalrun.score` does, so a recall figure here
cannot drift from what `research-scan eval` would report.

Metrics, in the slice's own order:

  primary    per-golden inclusion frequency f_g, every golden named;
             mean and minimum recall@10 per cell;
             contradiction inclusion frequency;
             foundational inclusion frequency, frontier-conditional;
             criterion coverage;
             top-tier population share — the saturation metric.
  secondary  mean and minimum pairwise Jaccard over the emitted sets.

Every per-cell figure is computed twice for the S cells: once under the cell's own ordering key
(the reported result) and once under the shipped key over the identical `ranked.json`. The
difference between the two is what separates "the rubric changed the judgements" from
"`priority_rank` changed the selection".
"""

from __future__ import annotations

import itertools
import json
import statistics
import sys
from collections import defaultdict
from pathlib import Path

HERE = Path(__file__).resolve().parent
REPO = HERE.parents[2]
sys.path.insert(0, str(HERE))

import variants  # noqa: E402

from research_scan import evalrun  # noqa: E402
from research_scan.schema import CandidatesFile  # noqa: E402

SLUGS = {"defaults-savings": "p11-t1", "llm-lit-search": "p11-t2"}

#: Phase-1.1's recorded figures. CONTEXT ONLY — every comparison in the ruling is against C0.
HISTORICAL_RECALL10 = {"defaults-savings": 5, "llm-lit-search": 3}

#: Short labels, so the f_g table names every golden without wrapping. Derived from the golden
#: file's own titles, never from a run's output.
SHORT = {
    "10.1257/aer.20210881": "Choukhmane — Default Options & Retirement Saving Dynamics",
    "10.3386/w32828": "Choi — Smaller than We Thought?",
    "10.3386/w31601": "Beshears — 12% Default Contribution Rate",
    "10.3386/w32074": "Berk — Employer-Based Short-Term Savings",
    "10.3386/w7682": "Madrian & Shea — The Power of Suggestion",
    "10.1086/380085": "Thaler & Benartzi — Save More Tomorrow",
    "10.3386/w8651": "Choi — For Better or For Worse",
    "10.1017/bpp.2018.43": "Jachimowicz — Default-effects meta-analysis",
    "10.1162/qjec.2009.124.4.1639": "Carroll — Optimal Defaults & Active Decisions",
    "10.1093/qje/qju013": "Chetty — Active vs Passive & Crowd-Out",
    "10.48550/arXiv.2501.10120": "PaSa",
    "10.48550/arXiv.2605.29234": "RollingEval",
    "10.48550/arXiv.2606.20235": "ScholarQuest",
    "10.48550/arXiv.2407.18940": "LitSearch",
    "10.48550/arXiv.2411.14199": "OpenScholar",
    "10.48550/arXiv.2402.01788": "LitLLM",
}


def label(doi: str) -> str:
    return SHORT.get(doi, doi)


# ------------------------------------------------------------------- loading


def load_replicates(topic: str, cell: str) -> list[dict]:
    base = HERE / "runs" / SLUGS[topic] / cell
    out = []
    if not base.is_dir():
        return out
    for d in sorted(base.glob("rep*"), key=lambda p: int(p.name[3:])):
        f = d / "summary.json"
        if f.is_file():
            out.append(json.loads(f.read_text()))
    return out


def golden_map(topic: str, run: Path) -> dict[str, dict]:
    """golden doi -> {label, cid or None}. `evalrun.matches` decides identity, not this module."""
    spec = evalrun.load_topic(evalrun.find_topic(topic, REPO / "eval/golden"))
    candidates = CandidatesFile.model_validate(json.loads((run / "candidates.json").read_text()))
    out = {}
    for paper in spec.expected:
        hit = next((c for c in candidates.candidates if evalrun.matches(paper, c)), None)
        out[paper.doi] = {"label": label(paper.doi), "cid": hit.cid if hit else None}
    return out


# ------------------------------------------------------------------- per replicate


def replicate_metrics(summary: dict, goldens: dict, *, key: str = "cell") -> dict:
    """One replicate, under either the cell's own selection (`key='cell'`) or the shipped one."""
    run = REPO / summary["run_dir"]
    field = "top10_cids" if key == "cell" else "shipped_key_top10_cids"
    reason_field = "selection_reasons" if key == "cell" else "shipped_key_reasons"
    emitted = summary[field] or []
    reasons = summary[reason_field] or []

    ranked = {e["cid"]: e for e in json.loads((run / "ranked.json").read_text())}
    criteria_ids = [c["id"] for c in json.loads((run / "queries.json").read_text())["sub_criteria"]]
    covered = {
        c for c in criteria_ids
        if any((ranked[cid].get("criteria") or {}).get(c, 0) >= 2
               for cid in emitted if cid in ranked)
    }
    sent = set(summary["sent_order"])

    fates = {}
    for doi, g in goldens.items():
        cid = g["cid"]
        fates[doi] = {
            "label": g["label"], "cid": cid,
            "reached_reranker": bool(cid) and cid in sent,
            "emitted": bool(cid) and cid in emitted,
            "emit_rank": (emitted.index(cid) + 1) if cid in emitted else None,
            "overall": ranked[cid].get("overall") if cid in ranked else None,
            "relation": ranked[cid].get("relation") if cid in ranked else None,
            "priority_rank": (summary.get("priority_map") or {}).get(cid),
        }

    overalls = [e["overall"] for e in ranked.values()]
    return {
        "replicate": summary["replicate"], "cell": summary["cell"], "topic": summary["topic"],
        "emitted": emitted, "reasons": reasons,
        "recall_10": sum(1 for f in fates.values() if f["emitted"]),
        "expected": len(goldens),
        "reached": sum(1 for f in fates.values() if f["reached_reranker"]),
        "review_slots": reasons.count("review"),
        "contradicting_slots": reasons.count("contradicting"),
        "foundational_slots": reasons.count("foundational"),
        "backfill_slots": reasons.count("backfill"),
        "diversity_slots": reasons.count("diversity"),
        "relation_contradicting": sum(
            1 for cid in emitted if ranked.get(cid, {}).get("relation") == "contradicting"),
        "relation_foundational": sum(
            1 for cid in emitted if ranked.get(cid, {}).get("relation") == "foundational"),
        "criterion_coverage": [len(covered), len(criteria_ids)],
        "rows": len(ranked),
        "top_tier_rows": sum(1 for o in overalls if o == 3),
        "top_tier_share": round(sum(1 for o in overalls if o == 3) / len(overalls), 4),
        "overall_histogram": {str(v): overalls.count(v) for v in (0, 1, 2, 3)},
        "fates": fates,
        "cost_usd": summary["cost_usd"], "wall_s": summary["stage_wall_s"],
        "calls": summary["calls"], "retries": summary["retries"],
        "chunks_ok": summary.get("chunks_ok"),
        "verify_exit": summary["verify_exit"], "emit_exit": summary["emit_exit"],
    }


def jaccard(a: set, b: set) -> float:
    return len(a & b) / len(a | b) if (a | b) else 1.0


# ------------------------------------------------------------------- per cell


def cell(topic: str, name: str, *, key: str = "cell") -> dict | None:
    reps = load_replicates(topic, name)
    if not reps:
        return None
    goldens = golden_map(topic, REPO / reps[0]["run_dir"])
    m = [replicate_metrics(s, goldens, key=key) for s in reps]
    n = len(m)

    freq: dict[str, int] = defaultdict(int)
    reached: dict[str, int] = defaultdict(int)
    for r in m:
        for doi, f in r["fates"].items():
            freq[doi] += int(f["emitted"])
            reached[doi] += int(f["reached_reranker"])

    tops = [set(r["emitted"]) for r in m]
    pairs = [jaccard(a, b) for a, b in itertools.combinations(tops, 2)]
    recalls = [r["recall_10"] for r in m]

    return {
        "topic": topic, "cell": name, "key": key, "n": n,
        "rubric_sha16": variants.digest(name),
        "expected": m[0]["expected"],
        "reachable_ceiling": max(r["reached"] for r in m),
        "recall10_runs": recalls,
        "recall10_mean": round(statistics.mean(recalls), 3),
        "recall10_min": min(recalls), "recall10_max": max(recalls),
        "historical_recall10": HISTORICAL_RECALL10[topic],
        "f_g": {doi: f"{freq[doi]}/{n}" for doi in goldens},
        "f_g_counts": {doi: freq[doi] for doi in goldens},
        "f_g_reached": {doi: f"{reached[doi]}/{n}" for doi in goldens},
        "labels": {doi: g["label"] for doi, g in goldens.items()},
        "top_tier_share_mean": round(statistics.mean(r["top_tier_share"] for r in m), 4),
        "top_tier_share_runs": [r["top_tier_share"] for r in m],
        "top_tier_rows_runs": [r["top_tier_rows"] for r in m],
        "overall_histogram_sum": {
            v: sum(r["overall_histogram"][v] for r in m) for v in ("0", "1", "2", "3")},
        "contradicting_slots": [r["contradicting_slots"] for r in m],
        "relation_contradicting": [r["relation_contradicting"] for r in m],
        "contradiction_inclusion_freq": round(
            sum(1 for r in m if r["relation_contradicting"] > 0) / n, 3),
        "foundational_slots": [r["foundational_slots"] for r in m],
        "foundational_inclusion_freq": round(
            sum(1 for r in m if r["foundational_slots"] > 0) / n, 3),
        "review_slots": [r["review_slots"] for r in m],
        "backfill_slots": [r["backfill_slots"] for r in m],
        "criterion_coverage": [f"{r['criterion_coverage'][0]}/{r['criterion_coverage'][1]}"
                               for r in m],
        "criterion_coverage_full": sum(
            1 for r in m if r["criterion_coverage"][0] == r["criterion_coverage"][1]),
        "jaccard_pairs": [round(p, 4) for p in pairs],
        "jaccard_mean": round(statistics.mean(pairs), 4) if pairs else None,
        "jaccard_min": round(min(pairs), 4) if pairs else None,
        "cost_usd_sum": round(sum(r["cost_usd"] for r in m), 4),
        "wall_s_mean": round(statistics.mean(r["wall_s"] for r in m), 1),
        "calls": sum(r["calls"] for r in m), "retries": sum(r["retries"] for r in m),
        "all_chunks_ok": all(r["chunks_ok"] for r in m),
        "verify_exits": sorted({r["verify_exit"] for r in m}),
        "emit_exits": sorted({r["emit_exit"] for r in m}),
        "replicates": m,
    }


def contenders(cells: dict, topic: str) -> list[str]:
    """The extension rule: within 1 golden of the per-topic lead on mean recall@10.

    The second limb of the pre-registered rule — "any cell where a gate ruling would flip between
    replicates" — is `spread_flips`: a cell whose per-run recall straddles C0's mean, so which side
    of the C0 comparison it lands on depends on which replicate you read.
    """
    here = {c: cells[f"{topic}/{c}"] for c in variants.CELLS if f"{topic}/{c}" in cells}
    if not here:
        return []
    lead = max(c["recall10_mean"] for c in here.values())
    control = here.get("C0")
    out = []
    for name, c in here.items():
        near_lead = c["recall10_mean"] >= lead - 1
        spread_flips = bool(control and min(c["recall10_runs"])
                            < control["recall10_mean"] < max(c["recall10_runs"]))
        if near_lead or spread_flips:
            out.append(name)
    return sorted(out, key=list(variants.CELLS).index)


def main() -> None:
    out, secondary = {}, {}
    for topic in SLUGS:
        for name in variants.CELLS:
            c = cell(topic, name)
            if c:
                out[f"{topic}/{name}"] = c
            s = cell(topic, name, key="shipped")
            if s:
                secondary[f"{topic}/{name}"] = s
    (HERE / "results").mkdir(exist_ok=True)
    (HERE / "results" / "cells.json").write_text(json.dumps(out, indent=1, default=str))
    (HERE / "results" / "cells_shipped_key.json").write_text(
        json.dumps(secondary, indent=1, default=str))

    for k, c in out.items():
        found = {c["labels"][d]: v for d, v in c["f_g"].items() if not v.startswith("0/")}
        print(f"{k:28s} n={c['n']} ceil={c['reachable_ceiling']}/{c['expected']} "
              f"recall10 {c['recall10_runs']} mean={c['recall10_mean']} min={c['recall10_min']} "
              f"top3share={c['top_tier_share_mean']} J={c['jaccard_mean']} ${c['cost_usd_sum']}")
        print(f"{'':28s} found: {found}")
    for topic in SLUGS:
        print(f"contenders {topic}: {contenders(out, topic)}")


if __name__ == "__main__":
    main()
