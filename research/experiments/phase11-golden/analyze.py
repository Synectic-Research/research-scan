"""Every number in the Phase-1.1 report, computed from the run files.

Run with the REPO venv (it imports `research_scan` for golden matching and the selection
ordering, so recall is never re-derived here by hand):

    .venv/bin/python research/experiments/phase11-golden/analyze.py
"""

from __future__ import annotations

import json
from collections import Counter
from pathlib import Path

from research_scan import evalrun
from research_scan.schema import CandidatesFile, Evidence, Ranked, ScreenFile

REPO = Path(__file__).resolve().parents[3]
EXP = REPO / "research/experiments/phase11-golden"
ARMS = ["R10", "R15", "R20", "R25", "Rall"]

#: `stage_wall_s` of every screening invocation, per topic. Two invocations of topic 2's
#: `expand` family are counted because both really happened: the first exhausted the frozen
#: 3-attempt policy on batch `x02`, the second re-ran the same policy and failed the same way.
SCREEN_WALLS = {
    "defaults-savings": {"main": 72.65, "expand": 38.62, "gap": 49.41, "gapexpand": 33.94},
    "llm-lit-search": {"main": 70.28, "expand": 75.48, "expand-retry": 56.67,
                       "salvage-x02": 17.1, "gap": 49.69, "gapexpand": 36.51},
}
TOPICS = [("defaults-savings", "p11-t1"), ("llm-lit-search", "p11-t2")]

# Recorded baselines, re-verified from the repo rather than taken from the slice prompt:
#   recall@10 / recall@25 — docs/measurements.md "V1 acceptance run", eval/results/*.json
#   candidates recall at `standard` — docs/measurements.md v0.2.2 corrected profile table
#   slot fills — the acceptance runs' own evidence.json
BASELINE = {
    "defaults-savings": {
        "run": "2026-08-19-s3-e2e", "profile_of_run": "quick-depth",
        "recall_10": (5, 10), "recall_25": (8, 10),
        "candidates_recall_standard": (8, 10),
        "foundational_slots": 2, "contradicting_reason": 0, "relation_contradicting": 0,
        "review_slots": 1,
    },
    "llm-lit-search": {
        "run": "2026-08-19-topic2b", "profile_of_run": "deep",
        "recall_10": (3, 6), "recall_25": (4, 6),
        "candidates_recall_standard": (5, 6),
        "foundational_slots": 2, "contradicting_reason": 0, "relation_contradicting": 2,
        "review_slots": 1,
    },
}


def _cli_seconds(ts: dict) -> dict:
    from datetime import datetime
    out = {}
    for key in sorted({k.split(".")[0] for k in ts}):
        a, b = ts.get(f"{key}.started_at"), ts.get(f"{key}.finished_at")
        if a and b:
            out[key] = round(
                (datetime.fromisoformat(b) - datetime.fromisoformat(a)).total_seconds(), 2)
    return out


def read(path, model):
    return model.model_validate_json(path.read_text())


def golden_cids(topic: str, run: Path) -> dict:
    """golden doi -> {cid, matched_by, title} for every expected paper present in the pool."""
    gt = evalrun.load_topic(evalrun.find_topic(topic, REPO / "eval/golden"))
    pool = {c.cid: c for c in read(run / "candidates.json", CandidatesFile).candidates}
    out = {}
    for paper in gt.expected:
        hit = None
        for cand in pool.values():
            kind = evalrun.match_kind(paper, cand)
            if kind:
                hit = {"cid": cand.cid, "matched_by": kind, "title": cand.title,
                       "outside_window": cand.outside_window,
                       "origins": evalrun.describe_origins(cand)[:4]}
                break
        out[paper.doi] = {"title": paper.title, "why": paper.why, **(hit or {"cid": None})}
    return out


def main() -> None:
    report: dict = {"topics": {}, "arms": {}, "pooled": {}}

    pool_scores = Counter()
    golden_scores = Counter()
    g1_retrieved = g1_ge2 = 0
    g1_items = []

    for topic, slug in TOPICS:
        run = EXP / "runs" / slug
        manifest = json.loads((run / "manifest.json").read_text())
        screen_rows = {s.cid: s for s in read(run / "screen.json", ScreenFile).scores}
        screen = {cid: r.score for cid, r in screen_rows.items()}
        cands = read(run / "candidates.json", CandidatesFile).candidates
        shortlist = json.loads((run / "shortlist.json").read_text())
        cut_order = ([r["cid"] for r in shortlist["in_window"]]
                     + [r["cid"] for r in shortlist["outside_window"]])
        in_ids = {r["cid"] for r in shortlist["in_window"]}
        gold = golden_cids(topic, run)

        pool_scores.update(screen.values())
        for doi, g in gold.items():
            if g["cid"]:
                golden_scores[screen[g["cid"]]] += 1

        # per-arm membership
        arm_state = {}
        for arm in ARMS:
            base = EXP / "sweep" / slug / arm
            if not (base / "summary.json").exists():
                continue
            s = json.loads((base / "summary.json").read_text())
            arm_run = base / "run"
            ev = read(arm_run / "evidence.json", Evidence)
            ranked = {e.cid: e for e in read(arm_run / "ranked.json", Ranked).root}
            emitted = [p.cid for p in ev.packets]
            reasons = [p.selection_reason.value if p.selection_reason else None
                       for p in ev.packets]
            criteria_ids = [c["id"] for c in
                            json.loads((arm_run / "queries.json").read_text())["sub_criteria"]]
            covered = {c for c in criteria_ids
                       if any((ranked[cid].criteria or {}).get(c, 0) >= 2
                              for cid in emitted if cid in ranked)}
            ev_res = evalrun.score(
                evalrun.load_topic(evalrun.find_topic(topic, REPO / "eval/golden")),
                arm_run, evalrun.load_run(arm_run))
            judge_path = EXP / "judge" / f"{slug}-{arm}.json"
            judge = json.loads(judge_path.read_text()) if judge_path.exists() else None
            arm_state[arm] = {
                "cut": s["reranked"], "in_window": s["in_window"],
                "outside_window": s["outside_window"],
                "reranked_cids": set(s["reranked_cids"]),
                "emitted": emitted, "selection_reasons": reasons,
                "foundational_slots": reasons.count("foundational"),
                "contradicting_slots": reasons.count("contradicting"),
                "review_slots": reasons.count("review"),
                "backfill_slots": reasons.count("backfill"),
                "relation_contradicting": sum(
                    1 for cid in emitted
                    if cid in ranked and ranked[cid].relation
                    and ranked[cid].relation.value == "contradicting"),
                "criterion_coverage": f"{len(covered)}/{len(criteria_ids)}",
                "recall_10": (ev_res.found_at_10, ev_res.expected),
                "recall_25": (ev_res.found_at_25, ev_res.expected),
                "frontier_tokens": s["frontier_tokens"],
                "cost_usd": s["cost_usd"], "wall_s": s["stage_wall_s"],
                "retries": s["retries"], "schema_failures": s["schema_failures"],
                "verify_exit": s["verify_exit"], "emit_exit": s["emit_exit"],
                "ranked_schema_valid": s["ranked_schema_valid"],
                "judge": None if judge is None else {
                    "precision_ge2_in_window": judge["precision_ge2_in_window"],
                    "mean_score_in_window": judge["mean_score_in_window"],
                    "in_window_n": judge["in_window_n"],
                    "foundational_scores": judge["foundational_scores"],
                    "cost_usd": judge["cost_usd"],
                },
            }

        # golden fate table
        fates = []
        for doi, g in gold.items():
            cid = g["cid"]
            score = screen.get(cid) if cid else None
            row = {
                "doi": doi, "title": g["title"], "cid": cid,
                "retrieved": cid is not None,
                "screen_reason": screen_rows[cid].reason if cid else None,
                "criteria_hit": list(screen_rows[cid].criteria_hit or []) if cid else None,
                "matched_by": g.get("matched_by"),
                "outside_window": g.get("outside_window"),
                "origins": g.get("origins"),
                "screen_score": score,
                "screened_ge2": bool(cid) and score is not None and score >= 2,
                "shortlisted": bool(cid) and cid in cut_order,
                "shortlist_pos": (cut_order.index(cid) + 1) if cid in cut_order else None,
                "shortlist_side": ("in_window" if cid in in_ids
                                   else ("outside_window" if cid in cut_order else None)),
                "in_cut": {a: (cid in st["reranked_cids"]) for a, st in arm_state.items()},
                "in_top10": {a: (cid in st["emitted"]) for a, st in arm_state.items()},
            }
            fates.append(row)
            if cid:
                g1_retrieved += 1
                if row["screened_ge2"]:
                    g1_ge2 += 1
                else:
                    g1_items.append({"topic": topic, "doi": doi, "score": score,
                                     "title": g["title"]})

        # Screening spend from the ledger, not from the stage summaries: the ledger records every
        # attempt, including the six that never landed on `llm-lit-search/x02`, and the stage
        # summary of a re-invocation overwrites its predecessor's.
        ledger = json.loads((EXP / "spend.json").read_text())["calls"]
        pref = (f"screen/{topic}/", f"salvage/{topic}/")
        screen_ledger = [c for c in ledger if c["tag"].startswith(pref)]

        # Measured stage wall for every screening invocation of this topic, including the two
        # that ended in the unrecovered x02 failure. Sourced from each invocation's own
        # `stage_wall_s`; the first `main` pass of topic 1 printed to stdout rather than a log.
        walls = SCREEN_WALLS[topic]

        stages = {}
        for f in sorted((EXP / "stages").glob("screen-*.json")):
            if f.name.startswith("screen-calls"):
                continue
            s = json.loads(f.read_text())
            if s.get("topic") == topic:
                stages[s["family"]] = s
        plan = json.loads((EXP / "stages" / f"plan-{topic}.json").read_text())
        gap = json.loads((EXP / "stages" / f"gap-{topic}.json").read_text())
        salvage = [json.loads(p.read_text())
                   for p in (EXP / "stages").glob(f"salvage-{topic}-*.json")]

        report["topics"][topic] = {
            "slug": slug,
            "run_dir": str(run),
            "purpose": json.loads((run / "purpose.json").read_text())["purpose"],
            "defaults": manifest["run"]["defaults"],
            "per_source": {k: {"hits": v["hits"], "failed": v["failed"], "auth": v["auth"]}
                           for k, v in manifest["retrieval"]["per_source"].items()},
            "retrieval_dropped": manifest["retrieval"]["dropped"],
            "expansion": manifest.get("expansion"),
            "pool": len(cands),
            "outside_window_in_pool": sum(1 for c in cands if c.outside_window),
            "score_distribution": dict(sorted(Counter(screen.values()).items())),
            "screened_ge2": sum(1 for v in screen.values() if v >= 2),
            "shortlist": {"in_window": len(shortlist["in_window"]),
                          "outside_window": len(shortlist["outside_window"])},
            "plan": {k: plan[k] for k in ("cost_usd", "api_seconds_sum", "output_tokens",
                                          "thinking_tokens", "purpose", "n_queries",
                                          "n_sub_criteria")},
            "gap": {k: gap.get(k) for k in ("ran", "n_round2", "cost_usd", "api_seconds_sum",
                                            "trigger_reasons")},
            "screen_spend_ledger": {
                "calls_including_failed_attempts": len(screen_ledger),
                "cost_usd": round(sum(c["cost_usd"] for c in screen_ledger), 6),
            },
            "screen_wall_measured": {"passes": walls, "total_s": round(sum(walls.values()), 2)},
            "screen_stages": {k: {kk: v[kk] for kk in
                                  ("calls", "calls_ok", "calls_failed", "cost_usd",
                                   "stage_wall_s", "retries", "schema_failures", "scored",
                                   "input_tokens", "cache_read_tokens", "output_tokens")}
                              for k, v in stages.items()},
            "salvage": salvage,
            "cli_stage_seconds": _cli_seconds(manifest.get("timestamps") or {}),
            "golden_fate": fates,
            "arms": {a: {k: v for k, v in st.items() if k != "reranked_cids"}
                     for a, st in arm_state.items()},
            "baseline": BASELINE[topic],
        }

    # ----------------------------------------------------- stage-loss accounting
    def loss_stage(f, arm):
        if not f["retrieved"]:
            return "not-retrieved"
        if not f["screened_ge2"]:
            return "screening (<2)"
        if not f["shortlisted"]:
            return "shortlist cap"
        if not f["in_cut"].get(arm):
            return f"{arm} cut"
        if not f["in_top10"].get(arm):
            return "rerank / emit ordering"
        return "emitted"

    stage_loss = {}
    for arm in ARMS:
        counts = Counter()
        per_topic = {}
        for topic, _ in TOPICS:
            rows = report["topics"][topic]["golden_fate"]
            here = Counter(loss_stage(f, arm) for f in rows)
            per_topic[topic] = dict(here)
            counts.update(here)
        stage_loss[arm] = {"pooled": dict(counts), "per_topic": per_topic}
    for topic, _ in TOPICS:
        for f in report["topics"][topic]["golden_fate"]:
            f["loss_stage"] = {a: loss_stage(f, a) for a in ARMS}
    report["pooled"]["stage_loss"] = stage_loss

    # ------------------------------------------------------------------ gates
    bar = 15 if g1_retrieved >= 16 else g1_retrieved - 1
    report["pooled"]["G1"] = {
        "retrieved": g1_retrieved, "ge2": g1_ge2, "bar": bar,
        "raw_ge2_over_16": f"{g1_ge2}/16",
        "conditional": f"{g1_ge2}/{g1_retrieved}",
        "pass": g1_ge2 >= bar, "misses": g1_items,
    }

    g2 = {}
    for topic, _ in TOPICS:
        st = report["topics"][topic]["arms"].get("R15")
        b = BASELINE[topic]
        if st:
            g2[topic] = {
                "recall_10": st["recall_10"], "baseline_recall_10": b["recall_10"],
                "pass_vs_recorded_recall10": st["recall_10"][0] >= b["recall_10"][0],
                "recall_25": st["recall_25"], "baseline_recall_25": b["recall_25"],
            }
    report["pooled"]["G2"] = g2

    g3 = {}
    for topic, _ in TOPICS:
        st = report["topics"][topic]["arms"].get("R15")
        b = BASELINE[topic]
        if st:
            g3[topic] = {
                "foundational": (st["foundational_slots"], b["foundational_slots"]),
                "contradicting_reason": (st["contradicting_slots"], b["contradicting_reason"]),
                "relation_contradicting": (st["relation_contradicting"],
                                           b["relation_contradicting"]),
                "review": (st["review_slots"], b["review_slots"]),
                "pass": (st["foundational_slots"] >= b["foundational_slots"]
                         and st["relation_contradicting"] >= b["relation_contradicting"]),
            }
    report["pooled"]["G3"] = g3

    # G4 is counted from the ledger, which records every attempt that reached the API — the
    # per-stage calls.json files are overwritten by a re-invocation and would undercount.
    ledger_all = json.loads((EXP / "spend.json").read_text())["calls"]
    pipeline = [c for c in ledger_all if not c["tag"].startswith("judge/")]
    per_tag = Counter(c["tag"] for c in pipeline)
    repeats = {t: n for t, n in per_tag.items() if n > 1}
    # One repeat is an operator artefact, not a model or API failure: the shell running the
    # topic-1 sweep was killed at a 10-minute timeout part-way through `R25/c1`, and the arm was
    # then re-run from the start. It is excluded from the retry rate and named here.
    ORPHAN = "rerank/defaults-savings/R25/c1"
    retries = sum(n - 1 for t, n in repeats.items()) - (1 if ORPHAN in repeats else 0)
    logical = len(per_tag)
    report["pooled"]["G4"] = {
        "api_calls_total": len(ledger_all),
        "pipeline_calls": len(pipeline),
        "pipeline_logical_units": logical,
        "repeat_attempts_by_tag": repeats,
        "operator_orphan_excluded": ORPHAN,
        "schema_retries": retries,
        "retry_rate_over_logical_units": round(retries / logical, 4),
        "retry_rate_over_attempts": round(retries / (len(pipeline) - 1), 4),
        "unrecovered_schema_failures": ["screen/llm-lit-search/x02"],
        "unrecovered_under_frozen_policy": 1,
        "attempts_that_batch_took": per_tag.get("screen/llm-lit-search/x02"),
        "salvaged_batches": ["llm-lit-search/x02"],
        "verify_exit_nonzero": [f"{t}/{a}" for t, _ in TOPICS for a in ARMS
                                if report["topics"][t]["arms"][a]["verify_exit"]],
        "emit_exit_nonzero": [f"{t}/{a}" for t, _ in TOPICS for a in ARMS
                              if report["topics"][t]["arms"][a]["emit_exit"]],
        "ranked_schema_invalid": [f"{t}/{a}" for t, _ in TOPICS for a in ARMS
                                  if not report["topics"][t]["arms"][a]["ranked_schema_valid"]],
        "pass": False,
    }

    # ------------------------------------------------------------ P(golden | score)
    report["pooled"]["p_golden_given_score"] = {
        str(s): {
            "pool": pool_scores.get(s, 0),
            "golden": golden_scores.get(s, 0),
            "p": round(golden_scores.get(s, 0) / pool_scores[s], 6) if pool_scores.get(s) else None,
        }
        for s in (0, 1, 2, 3)
    }
    report["pooled"]["pool_score_distribution"] = dict(sorted(pool_scores.items()))
    report["pooled"]["cumulative_spend_usd"] = json.loads(
        (EXP / "spend.json").read_text())["total_usd"]

    (EXP / "measurements.json").write_text(json.dumps(report, indent=1, default=str))
    print(json.dumps(report["pooled"], indent=1, default=str))


if __name__ == "__main__":
    main()
