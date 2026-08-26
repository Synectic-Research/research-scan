"""Measurements, recovery curves and the gate verdict.

Reads arm outputs only; makes no API calls. Runs `research-scan shortlist` on a copy of the
run per screening arm to get that arm's shortlist ids (CLI work, no model, no writes to the
saved run).

Usage:  python analyze.py [--out report.md]
"""

from __future__ import annotations

import argparse
import json
import shutil
import subprocess
import sys
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parent))
from lib import common as C  # noqa: E402

SCREEN_ARMS = ["B", "C", "D"]
RERANK_ARMS = ["R52", "R25", "R15"]
GATE_COST_FRACTION = 0.20
GATE_BINARY = 0.95
GATE_EXACT = 0.80
GATE_TOP10 = 8


def shortlist_for(arm: str) -> dict | None:
    """Run the real shortlist step on this arm's screen.json, in a scratch copy of the run."""
    src = C.ARMS / arm / "screen.json"
    if not src.exists():
        return None
    run = C.ARMS / arm / "run"
    if run.exists():
        shutil.rmtree(run)
    shutil.copytree(C.RUN, run)
    for stale in ("ranked.json", "evidence.json", "evidence.md", "evidence.bib",
                  "verify.log.jsonl", "shortlist.json"):
        (run / stale).unlink(missing_ok=True)
    shutil.copy(src, run / "screen.json")
    proc = subprocess.run(
        ["research-scan", "shortlist", "--run", str(run), "--json", "--quiet"],
        capture_output=True, text=True,
    )
    if proc.returncode != 0:
        return {"error": proc.stderr[-300:]}
    sl = json.loads((run / "shortlist.json").read_text())
    return {
        "ids": [r["cid"] for r in sl["in_window"]] + [r["cid"] for r in sl["outside_window"]],
        "in_window": len(sl["in_window"]),
        "outside_window": len(sl["outside_window"]),
    }


def agreement(arm_scores: dict[str, int], base: dict[str, int]) -> dict:
    shared = [c for c in arm_scores if c in base]
    exact = sum(1 for c in shared if arm_scores[c] == base[c])
    binary = sum(1 for c in shared if (arm_scores[c] >= 2) == (base[c] >= 2))
    a2 = {c for c in shared if arm_scores[c] >= 2}
    b2 = {c for c in shared if base[c] >= 2}
    return {
        "n": len(shared),
        "exact": round(exact / len(shared), 4) if shared else 0.0,
        "binary_ge2": round(binary / len(shared), 4) if shared else 0.0,
        "jaccard_ge2": round(len(a2 & b2) / len(a2 | b2), 4) if (a2 | b2) else 0.0,
        "ge2_count": len(a2),
        "ge2_baseline": len(b2),
        "false_pos": len(a2 - b2),
        "false_neg": len(b2 - a2),
    }


def recovery_curve(order: list[str], arm_scores: dict[str, int], target: set[str]) -> list[dict]:
    """At each decile of the priority queue: how much of `target` is behind us."""
    rows, n = [], len(order)
    for pct in range(10, 101, 10):
        k = round(n * pct / 100)
        seen = set(order[:k])
        enc = seen & target
        found = {c for c in enc if arm_scores.get(c, 0) >= 2}
        rows.append({
            "pct": pct, "screened": k,
            "encountered": round(len(enc) / len(target), 4) if target else 0.0,
            "found": round(len(found) / len(target), 4) if target else 0.0,
        })
    return rows


def main() -> None:
    ap = argparse.ArgumentParser()
    ap.add_argument("--out", default=str(C.EXP / "report.md"))
    args = ap.parse_args()

    base = json.loads((C.ARMS / "A" / "baseline.json").read_text())
    base_scores: dict[str, int] = base["scores"]
    base_shortlist = set(base["shortlist_ids"])
    base_top_dois = base["top10_dois"]

    out: dict = {"baseline": base["share"], "arms": {}, "rerank": {}, "gate": {}}

    for arm in SCREEN_ARMS:
        summ_path = C.ARMS / arm / "summary.json"
        if not summ_path.exists():
            continue
        summ = json.loads(summ_path.read_text())
        scores = {s["cid"]: s["score"]
                  for s in json.loads((C.ARMS / arm / "screen.json").read_text())["scores"]}
        agr = agreement(scores, base_scores)
        sl = shortlist_for(arm)
        row = {**summ, "agreement": agr}
        if sl and "ids" in sl:
            ids = set(sl["ids"])
            row["shortlist"] = {
                "size": len(ids), "in_window": sl["in_window"],
                "outside_window": sl["outside_window"],
                "overlap_with_baseline": len(ids & base_shortlist),
                "overlap_frac": round(len(ids & base_shortlist) / len(base_shortlist), 4),
            }
        else:
            row["shortlist"] = sl or {"error": "no screen.json"}
        out["arms"][arm] = row

    # arm D recovery curves
    order_path = C.ARMS / "D" / "priority-order.json"
    if order_path.exists() and (C.ARMS / "D" / "screen.json").exists():
        order = [c for b in json.loads(order_path.read_text()).values() for c in b]
        d_scores = {s["cid"]: s["score"]
                    for s in json.loads((C.ARMS / "D" / "screen.json").read_text())["scores"]}
        out["recovery"] = {
            "ge2_set": recovery_curve(order, d_scores, set(base["ge2_set"])),
            "top10": recovery_curve(order, d_scores, set(base["top10_cids"])),
            "contradicting": recovery_curve(order, d_scores, set(base["contradicting_cids"])),
        }

    for sub in RERANK_ARMS:
        p = C.ARMS / "rerank" / sub / "summary.json"
        if not p.exists():
            continue
        s = json.loads(p.read_text())
        if "top10_dois" in s:
            s["top10_overlap"] = len(set(base_top_dois) & set(s["top10_dois"]))
            s["missing_vs_baseline"] = [d for d in base_top_dois if d not in set(s["top10_dois"])]
        s["frontier_tokens_per_item"] = round(
            (s["input_tokens"] + s["cache_read_tokens"] + s["output_tokens"]) / 10, 1
        )
        out["rerank"][sub] = s

    # ------------------------------------------------------------------ gate
    b_screen_cost = base["share"]["screening_cost_usd"]
    b_rerank_cost = base["share"]["rerank_cost_usd"]
    gate = {}
    for arm in ("C", "D"):
        a = out["arms"].get(arm)
        if not a:
            continue
        frac = a["cost_usd"] / b_screen_cost
        gate[arm] = {
            "cost_usd": round(a["cost_usd"], 4),
            "baseline_screening_share_usd": b_screen_cost,
            "cost_fraction": round(frac, 4),
            "cost_pass": frac <= GATE_COST_FRACTION,
            "binary_ge2": a["agreement"]["binary_ge2"],
            "binary_pass": a["agreement"]["binary_ge2"] >= GATE_BINARY,
            "exact": a["agreement"]["exact"],
            "exact_pass": a["agreement"]["exact"] >= GATE_EXACT,
        }
    # The judge runs only because every sub-arm came in under 8/10 overlap; when it has run,
    # the gate's own fallback applies: judged precision within 0.1 of baseline also passes.
    judge_dir = C.ARMS / "judge"
    judged: dict[str, dict] = {}
    if (judge_dir / "summary.json").exists():
        for r in json.loads((judge_dir / "summary.json").read_text())["runs"]:
            judged[r["label"]] = r
        out["judged"] = judged
    base_prec = judged.get("baseline", {}).get("precision_ge2_in_window")

    gate["rerank"] = {}
    for sub in RERANK_ARMS:
        if sub not in out["rerank"]:
            continue
        overlap = out["rerank"][sub].get("top10_overlap") or 0
        prec = judged.get(sub, {}).get("precision_ge2_in_window")
        delta = None if (prec is None or base_prec is None) else round(abs(prec - base_prec), 4)
        gate["rerank"][sub] = {
            "top10_overlap": overlap,
            "overlap_pass": overlap >= GATE_TOP10,
            "judged_precision": prec,
            "baseline_judged_precision": base_prec,
            "judged_delta": delta,
            "judged_pass": delta is not None and delta <= 0.1,
            "pass": overlap >= GATE_TOP10 or (delta is not None and delta <= 0.1),
            "cost_usd": round(out["rerank"][sub]["cost_usd"], 4),
            "baseline_rerank_share_usd": b_rerank_cost,
        }
    gate["any_rerank_pass"] = any(v["pass"] for v in gate["rerank"].values()) if gate["rerank"] else False
    out["gate"] = gate
    out["total_api_spend_usd"] = round(C.spent(), 4)

    # ---------------------------------------------- full-scan extrapolation
    # Replay cannot reproduce retrieval, so the CLI stages and the plan/report turns are carried
    # from the baseline at their measured cost and duration; only screening and rerank are replaced.
    per = base["stage_attribution"]["per_stage"]
    secs = {w["stage"]: w["seconds"] for w in base["stage_windows"]}
    carried_cost = (per["plan"]["cost_usd"] + per["coverage_shortlist_cli"]["cost_usd"]
                    + per["emit_and_report"]["cost_usd"])
    carried_wall = (secs["plan"] + secs["retrieve_cli"] + secs["expand_cli"]
                    + secs["coverage_shortlist_cli"] + secs["verify_cli"]
                    + secs["emit_and_report"])
    armc = out["arms"].get("C")
    if armc:
        est = {}
        for sub in RERANK_ARMS:
            r = out["rerank"].get(sub)
            if not r:
                continue
            combined = armc["cost_usd"] + r["cost_usd"]
            est[f"C+{sub}"] = {
                "full_scan_cost_usd": round(carried_cost + combined, 4),
                "full_scan_wall_s": round(carried_wall + armc["stage_wall_s"]
                                          + r["stage_wall_s"], 1),
                "screening_plus_rerank_cost_usd": round(combined, 4),
                "vs_baseline_share_pct": round(
                    combined / base["share"]["screening_plus_rerank_cost_usd"] * 100, 1),
                "vs_baseline_full_cost_pct": round(
                    (carried_cost + combined) / base["whole_scan"]["cost_usd"] * 100, 1),
            }
        out["extrapolation"] = {
            "carried_from_baseline_cost_usd": round(carried_cost, 4),
            "carried_from_baseline_wall_s": round(carried_wall, 1),
            "baseline_full_cost_usd": base["whole_scan"]["cost_usd"],
            "baseline_full_wall_s": base["whole_scan"]["wall_s_manifest"],
            "estimates": est,
        }

    C.write_json(C.EXP / "measurements.json", out)
    Path(args.out).write_text(render(out, base))
    print(json.dumps(out, indent=1, default=str)[:12000])
    print(f"\n--- tables written to {args.out} ---")


def _n(x) -> str:
    return f"{x:,}" if isinstance(x, int) else str(x)


def render(out: dict, base: dict) -> str:
    """The measurements table, the recovery curves and the gate, as markdown."""
    b = out["baseline"]
    L: list[str] = []

    L.append("## 2. Measurements\n")
    cols = ["arm", "calls", "input tok", "cache-read tok", "output tok", "(thinking)",
            "cost USD", "stage wall s", "exact agr", "binary ≥2", "≥2 Jaccard",
            "shortlist ∩ base", "top-10 ∩ base"]
    L.append("| " + " | ".join(cols) + " |")
    L.append("|" + "---|" * len(cols))
    L.append(f"| A (baseline, screening share) | {base['stage_attribution']['per_stage']['screen_round1']['turns'] + base['stage_attribution']['per_stage']['screen_expansion']['turns']} turns "
             f"| {_n(base['stage_attribution']['per_stage']['screen_round1']['input'] + base['stage_attribution']['per_stage']['screen_expansion']['input'])} "
             f"| {_n(base['stage_attribution']['per_stage']['screen_round1']['cache_read'] + base['stage_attribution']['per_stage']['screen_expansion']['cache_read'])} "
             f"| {_n(base['stage_attribution']['per_stage']['screen_round1']['output'] + base['stage_attribution']['per_stage']['screen_expansion']['output'])} "
             f"| {_n(base['stage_attribution']['per_stage']['screen_round1']['thinking'] + base['stage_attribution']['per_stage']['screen_expansion']['thinking'])} "
             f"| {b['screening_cost_usd']} | {b['screening_seconds']} | 1.000 | 1.000 | 1.000 "
             f"| {base['counts']['shortlist']}/{base['counts']['shortlist']} | 10/10 |")
    for arm in SCREEN_ARMS:
        a = out["arms"].get(arm)
        if not a:
            continue
        ag, sl = a["agreement"], a.get("shortlist") or {}
        L.append(
            f"| {arm} | {a['calls']} | {_n(a['input_tokens'])} | {_n(a['cache_read_tokens'])} "
            f"| {_n(a['output_tokens'])} | {_n(a['thinking_tokens'])} | {a['cost_usd']:.4f} "
            f"| {a['stage_wall_s']:.0f} | {ag['exact']:.3f} | {ag['binary_ge2']:.3f} "
            f"| {ag['jaccard_ge2']:.3f} "
            f"| {sl.get('overlap_with_baseline','-')}/{base['counts']['shortlist']} | — |")
    L.append(f"| A (baseline, rerank share) | {base['stage_attribution']['per_stage']['rerank']['turns']} turns "
             f"| {_n(base['stage_attribution']['per_stage']['rerank']['input'])} "
             f"| {_n(base['stage_attribution']['per_stage']['rerank']['cache_read'])} "
             f"| {_n(base['stage_attribution']['per_stage']['rerank']['output'])} "
             f"| {_n(base['stage_attribution']['per_stage']['rerank']['thinking'])} "
             f"| {b['rerank_cost_usd']} | {b['rerank_seconds']} | — | — | — | — | 10/10 |")
    for sub in RERANK_ARMS:
        r = out["rerank"].get(sub)
        if not r:
            continue
        L.append(
            f"| {sub} (rerank {r['reranked']}) | {r['calls']} | {_n(r['input_tokens'])} "
            f"| {_n(r['cache_read_tokens'])} | {_n(r['output_tokens'])} | {_n(r['thinking_tokens'])} "
            f"| {r['cost_usd']:.4f} | {r['stage_wall_s']:.0f} | — | — | — | — "
            f"| {r.get('top10_overlap','-')}/10 |")
    L.append("")
    L.append("Frontier tokens per accepted evidence item (rerank tokens ÷ 10):\n")
    L.append("| sub-arm | reranked | rerank tokens | tokens / accepted item |")
    L.append("|---|---|---|---|")
    for sub in RERANK_ARMS:
        r = out["rerank"].get(sub)
        if r:
            tot = r["input_tokens"] + r["cache_read_tokens"] + r["output_tokens"]
            L.append(f"| {sub} | {r['reranked']} | {_n(tot)} | {r['frontier_tokens_per_item']:.0f} |")

    if "recovery" in out:
        L.append("\n## 3. Arm D recovery curves\n")
        L.append("`found` = arm D screened it *and* scored it ≥2. "
                 "`enc` = it had been reached in the queue at all.\n")
        L.append("| % screened | items | ≥2 set found | ≥2 set enc | top-10 found | top-10 enc "
                 "| contradicting found | contradicting enc |")
        L.append("|---|---|---|---|---|---|---|---|")
        rc = out["recovery"]
        for i in range(len(rc["ge2_set"])):
            g, t, c = rc["ge2_set"][i], rc["top10"][i], rc["contradicting"][i]
            L.append(f"| {g['pct']}% | {g['screened']} | {g['found']:.1%} | {g['encountered']:.1%} "
                     f"| {t['found']:.1%} | {t['encountered']:.1%} "
                     f"| {c['found']:.1%} | {c['encountered']:.1%} |")

    L.append("\n## 4. Gate\n")
    L.append("| criterion | threshold | arm | value | verdict |")
    L.append("|---|---|---|---|---|")
    for arm in ("C", "D"):
        g = out["gate"].get(arm)
        if not g:
            continue
        L.append(f"| screening cost vs baseline screening share | ≤ 20% | {arm} "
                 f"| ${g['cost_usd']:.4f} / ${g['baseline_screening_share_usd']:.4f} "
                 f"= {g['cost_fraction']:.1%} | {'PASS' if g['cost_pass'] else 'FAIL'} |")
        L.append(f"| binary ≥2 agreement | ≥ 95% | {arm} | {g['binary_ge2']:.2%} "
                 f"| {'PASS' if g['binary_pass'] else 'FAIL'} |")
        L.append(f"| exact score agreement | ≥ 80% | {arm} | {g['exact']:.2%} "
                 f"| {'PASS' if g['exact_pass'] else 'FAIL'} |")
    for sub, g in out["gate"].get("rerank", {}).items():
        L.append(f"| rerank top-10 overlap | ≥ 8/10 | {sub} | {g['top10_overlap']}/10 "
                 f"| {'PASS' if g['overlap_pass'] else 'FAIL'} |")
    for sub, g in out["gate"].get("rerank", {}).items():
        if g.get("judged_precision") is not None:
            L.append(f"| — fallback: judged precision vs baseline | within 0.1 | {sub} "
                     f"| {g['judged_precision']:.2f} vs {g['baseline_judged_precision']:.2f} "
                     f"(Δ {g['judged_delta']:.2f}) | {'PASS' if g['judged_pass'] else 'FAIL'} |")
    passers = [s for s, g in out["gate"].get("rerank", {}).items() if g["pass"]]
    L.append(f"| **rerank criterion overall** (≥8/10 **or** judged within 0.1) | — | any sub-arm "
             f"| {', '.join(passers) if passers else 'none'} | "
             f"{'PASS' if passers else 'FAIL'} |")

    if "judged" in out:
        L.append("\n### Judge detail (claude-fable-5, eval/judge-prompt.md)\n")
        L.append("| list | in-window packets | precision ≥2 | mean score | foundational scores |")
        L.append("|---|---|---|---|---|")
        for lbl in ("baseline", "R52", "R25", "R15"):
            j = out["judged"].get(lbl)
            if j:
                L.append(f"| {lbl} | {j['in_window_n']} | {j['precision_ge2_in_window']:.2f} "
                         f"| {j['mean_score_in_window']} | {j['foundational_scores']} |")
    if "extrapolation" in out:
        e = out["extrapolation"]
        L.append("\n### Extrapolated full scan\n")
        L.append(f"Replay cannot reproduce retrieval. Plan, the CLI stages and the report turn are "
                 f"carried from the baseline at their measured values "
                 f"(${e['carried_from_baseline_cost_usd']:.3f}, "
                 f"{e['carried_from_baseline_wall_s']:.0f}s); only screening and rerank are "
                 f"replaced.\n")
        L.append("| configuration | full-scan cost | full-scan wall | screen+rerank vs baseline share |")
        L.append("|---|---|---|---|")
        L.append(f"| baseline (measured) | ${e['baseline_full_cost_usd']:.2f} "
                 f"| {e['baseline_full_wall_s']:.0f}s ({e['baseline_full_wall_s']/60:.1f} min) "
                 f"| 100% |")
        for k, v in e["estimates"].items():
            L.append(f"| {k} | ${v['full_scan_cost_usd']:.2f} "
                     f"({v['vs_baseline_full_cost_pct']:.0f}% of baseline) "
                     f"| {v['full_scan_wall_s']:.0f}s ({v['full_scan_wall_s']/60:.1f} min) "
                     f"| {v['vs_baseline_share_pct']:.1f}% |")

    L.append(f"\nTotal API spend this slice: **${out['total_api_spend_usd']:.2f}** of the $12 cap.")
    return "\n".join(L) + "\n"


if __name__ == "__main__":
    main()
