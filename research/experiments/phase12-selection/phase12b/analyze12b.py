"""Phase-1.2B analysis — stage fates, inclusion frequencies, recall, Jaccard, cost.

Golden matching and recall are never re-derived by hand: `evalrun.score` and `evalrun.match_kind`
from the shipped package do it, exactly as Phase 1.1's `analyze.py` does.

Run with the REPO venv.
"""
from __future__ import annotations

import itertools
import json
import statistics
import sys
import types
from collections import defaultdict
from pathlib import Path

HERE = Path(__file__).resolve().parent
P12 = HERE.parent
REPO = P12.parents[2]
sys.path.insert(0, str(P12))
sys.path.insert(0, str(REPO / "research/experiments/phase11-golden"))
sys.modules.setdefault("anthropic", types.ModuleType("anthropic"))

import sweep as S  # noqa: E402
from research_scan import evalrun  # noqa: E402
from research_scan.schema import Candidate, CandidatesFile, Evidence, Ranked  # noqa: E402
from research_scan import run as runmod  # noqa: E402

SLUGS = {"defaults-savings": "p11-t1", "llm-lit-search": "p11-t2"}
BASELINE_RECALL10 = {"defaults-savings": 5, "llm-lit-search": 3}
STATELESS_KEY = {"defaults-savings": "t1-stateless", "llm-lit-search": "t2-stateless"}
FATE_STAGES = ("screen_keep", "shortlist_keep", "rk_keep", "rerank_top10", "final_emit")


def golden_table(topic: str) -> dict:
    """golden doi -> {name, cid, screen score} over the Phase-1.1 stateless pool."""
    run = next(r for r in S.RUNS if r.key == STATELESS_KEY[topic])
    data = run.load()
    gm = S.golden_map(topic, data["candidates"])
    out = {}
    for doi, g in gm.items():
        cid = g["cid"]
        out[doi] = {"name": g["name"], "cid": cid,
                    "screen_score": data["screen"].get(cid, {}).get("score") if cid else None,
                    "title": g["title"]}
    return out


def load_replicates(topic: str, arm: str, ordering: str) -> list[dict]:
    base = HERE / "runs" / SLUGS[topic] / arm / ordering
    out = []
    for d in sorted(base.glob("rep*"), key=lambda p: int(p.name[3:])):
        f = d / "summary.json"
        if f.is_file():
            out.append(json.loads(f.read_text()))
    return out


def jaccard(a: set, b: set) -> float:
    return len(a & b) / len(a | b) if (a | b) else 1.0


def replicate_metrics(summary: dict, goldens: dict) -> dict:
    run = REPO / summary["run_dir"]
    ev = json.loads((run / "evidence.json").read_text())
    ranked = {e["cid"]: e for e in json.loads((run / "ranked.json").read_text())}
    emitted = [p["cid"] for p in ev["packets"]]
    reasons = [p.get("selection_reason") for p in ev["packets"]]
    criteria_ids = [c["id"] for c in json.loads((run / "queries.json").read_text())["sub_criteria"]]
    covered = {c for c in criteria_ids
               if any((ranked[cid].get("criteria") or {}).get(c, 0) >= 2
                      for cid in emitted if cid in ranked)}
    topic = summary["topic"]
    res = evalrun.score(evalrun.load_topic(evalrun.find_topic(topic, REPO / "eval/golden")),
                        run, evalrun.load_run(run))
    sent = set(summary["sent_order"])
    shortlist = json.loads((run / "shortlist.json").read_text())
    sl_cids = ({r["cid"] for r in shortlist["in_window"]}
               | {r["cid"] for r in shortlist["outside_window"]})
    fates = {}
    for doi, g in goldens.items():
        cid = g["cid"]
        fates[g["name"]] = {
            "cid": cid, "screen_score": g["screen_score"],
            "screen_keep": bool(cid) and (g["screen_score"] or 0) >= 2,
            "shortlist_keep": bool(cid) and cid in sl_cids,
            "rk_keep": bool(cid) and cid in sent,
            "rerank_top10": bool(cid) and cid in emitted,
            "final_emit": bool(cid) and cid in emitted,
            "emit_rank": (emitted.index(cid) + 1) if cid in emitted else None,
            "rank_overall": ranked[cid].get("overall") if cid in ranked else None,
            "rank_relation": ranked[cid].get("relation") if cid in ranked else None,
        }
    return {
        "replicate": summary["replicate"], "ordering": summary["ordering"],
        "emitted": emitted, "selection_reasons": reasons,
        "recall_10": res.found_at_10, "expected": res.expected,
        "recall_25": res.found_at_25,
        "foundational_slots": reasons.count("foundational"),
        "contradicting_slots": reasons.count("contradicting"),
        "review_slots": reasons.count("review"),
        "backfill_slots": reasons.count("backfill"),
        "relation_contradicting": sum(1 for cid in emitted
                                      if ranked.get(cid, {}).get("relation") == "contradicting"),
        "criterion_coverage": [len(covered), len(criteria_ids)],
        "fates": fates,
        "frontier_tokens": summary["frontier_tokens"], "cost_usd": summary["cost_usd"],
        "wall_s": summary["stage_wall_s"], "calls": summary["calls"],
        "retries": summary["retries"], "schema_failures": summary["schema_failures"],
        "verify_exit": summary["verify_exit"], "emit_exit": summary["emit_exit"],
    }


def ceiling(topic: str, arm: str) -> int:
    """Max attainable recall@10: goldens the stratified cut actually delivers to the reranker.

    Read from the offline stage-fate table, not from any run's output. A cell cannot emit a
    paper the reranker was never shown, so every recall gate has to be read against this.
    """
    ff = json.loads((HERE / "results" / "frontier_fate.json").read_text())
    rows = ff[topic]["policies"]["T1@40"]["rows"]
    return sum(1 for r in rows.values() if r["reaches_reranker"].get(arm))


def cell(topic: str, arm: str, ordering: str = "O1") -> dict | None:
    reps = load_replicates(topic, arm, ordering)
    if not reps:
        return None
    goldens = golden_table(topic)
    m = [replicate_metrics(s, goldens) for s in reps]
    tops = [set(r["emitted"]) for r in m]
    pairs = [jaccard(a, b) for a, b in itertools.combinations(tops, 2)]
    freq = defaultdict(int)
    for r in m:
        for name, f in r["fates"].items():
            freq[name] += int(f["final_emit"])
    recalls = [r["recall_10"] for r in m]
    return {
        "topic": topic, "arm": arm, "ordering": ordering, "n": len(m),
        "expected": m[0]["expected"],
        "recall10_runs": recalls,
        "recall10_worst": min(recalls), "recall10_mean": round(statistics.mean(recalls), 3),
        "recall10_best": max(recalls),
        "baseline_recall10": BASELINE_RECALL10[topic],
        "reachable_ceiling": ceiling(topic, arm),
        "g1_frontier_sufficient": ceiling(topic, arm) == sum(
            1 for g in golden_table(topic).values()
            if g["cid"] and (g["screen_score"] or 0) >= 2
            and g["cid"] in {r["cid"] for r in json.loads(
                (HERE / "shortlists" / f"{SLUGS[topic]}-T1at40.json").read_text())["in_window"]}
            | {r["cid"] for r in json.loads(
                (HERE / "shortlists" / f"{SLUGS[topic]}-T1at40.json").read_text())[
                "outside_window"]}),
        "g2_pass_worst": min(recalls) >= BASELINE_RECALL10[topic],
        "jaccard_pairs": [round(p, 4) for p in pairs],
        "jaccard_mean": round(statistics.mean(pairs), 4) if pairs else None,
        "jaccard_min": round(min(pairs), 4) if pairs else None,
        "inclusion_freq": {k: f"{v}/{len(m)}" for k, v in sorted(freq.items())},
        "foundational_slots": [r["foundational_slots"] for r in m],
        "contradicting_slots": [r["contradicting_slots"] for r in m],
        "relation_contradicting": [r["relation_contradicting"] for r in m],
        "review_slots": [r["review_slots"] for r in m],
        "criterion_coverage": [f"{r['criterion_coverage'][0]}/{r['criterion_coverage'][1]}"
                               for r in m],
        "frontier_tokens_mean": round(statistics.mean(r["frontier_tokens"] for r in m)),
        "cost_usd_sum": round(sum(r["cost_usd"] for r in m), 4),
        "cost_usd_mean": round(statistics.mean(r["cost_usd"] for r in m), 4),
        "wall_s_mean": round(statistics.mean(r["wall_s"] for r in m), 1),
        "calls": sum(r["calls"] for r in m),
        "retries": sum(r["retries"] for r in m),
        "schema_failures": sum(r["schema_failures"] for r in m),
        "replicates": m,
    }


def main() -> None:
    arms = sys.argv[1:] or ["R15", "R20", "R25", "R40"]
    out = {}
    for topic in SLUGS:
        for arm in arms:
            for ordering in ("O1", "O2", "O3"):
                c = cell(topic, arm, ordering)
                if c:
                    out[f"{topic}/{arm}/{ordering}"] = c
    (HERE / "results" / "cells.json").write_text(json.dumps(out, indent=1, default=str))
    for k, c in out.items():
        print(f"{k:42s} n={c['n']} ceil={c['reachable_ceiling']} "
              f"recall10 {c['recall10_runs']} worst={c['recall10_worst']}"
              f"/{c['expected']} mean={c['recall10_mean']} J={c['jaccard_mean']} "
              f"found={ {n: v for n, v in c['inclusion_freq'].items() if not v.startswith('0/')} } "
              f"${c['cost_usd_sum']}")


if __name__ == "__main__":
    main()
