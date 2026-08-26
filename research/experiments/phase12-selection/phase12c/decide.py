"""Phase-1.2C — apply the slice's decision rule to the replayed ladders and render the tables.

Decision rule, lexicographically over ladders: (1) max worst-run recall@10 per topic;
(2) max mean Jaccard; (3) shortest key. Evaluated on the two R40 O1 cells — the only arm that
passed Phase-1.2B's G1 (frontier sufficiency), so the only arm where a recall number means
anything. The whole-slice picture is reported beside it and is not favourably rounded.
"""
from __future__ import annotations

import json
import statistics
from collections import Counter

import common12c as C
import ladders

KEYS = ("K0", "K1", "K2", "K3")
DECISIVE = ("defaults-savings/R40/O1", "llm-lit-search/R40/O1")
J_THRESHOLD = 0.65          # Phase-1.2B's G4 diagnostic threshold, not doctrine


def main() -> None:
    m = json.loads((C.HERE / "results" / "measurements.json").read_text())
    ks = json.loads((C.HERE / "results" / "key_stability.json").read_text())
    cells = m["cells"]

    per_key = {}
    for k in KEYS:
        worst = {c: cells[c]["keys"][k]["recall10_worst"] for c in DECISIVE}
        jac = {c: cells[c]["keys"][k]["jaccard_mean"] for c in DECISIVE}
        per_key[k] = {
            "worst_recall_by_topic": worst,
            "jaccard_by_topic": jac,
            "jaccard_mean_of_topics": round(statistics.mean(jac.values()), 4),
            "key_length": len(ladders.TIERS[k]),
            "meets_baseline": {c: worst[c] >= C.BASELINE_RECALL10[c.split("/")[0]]
                               for c in DECISIVE},
            "meets_jaccard": {c: jac[c] >= J_THRESHOLD for c in DECISIVE},
        }

    # (1) worst-run recall, per topic — a ladder wins only if >= on both and > on one.
    def dominates(a, b):
        wa, wb = per_key[a]["worst_recall_by_topic"], per_key[b]["worst_recall_by_topic"]
        return all(wa[c] >= wb[c] for c in DECISIVE) and any(wa[c] > wb[c] for c in DECISIVE)

    survivors = [k for k in KEYS if not any(dominates(o, k) for o in KEYS)]
    step1 = list(survivors)
    # (2) mean Jaccard — per topic first; the rule does not say how to resolve a per-topic
    # conflict, so both readings are reported and the ruling is checked against both.
    j_winner_by_topic = {c: max(survivors, key=lambda k: per_key[k]["jaccard_by_topic"][c])
                         for c in DECISIVE}
    best_avg = max(survivors, key=lambda k: per_key[k]["jaccard_mean_of_topics"])
    survivors2 = [k for k in survivors
                  if per_key[k]["jaccard_mean_of_topics"]
                  == per_key[best_avg]["jaccard_mean_of_topics"]]
    # (3) shortest key
    winner = min(survivors2, key=lambda k: per_key[k]["key_length"])

    # Does the winner clear the gate the slice sets for "selection is the fix"?
    restores = (all(per_key[winner]["meets_baseline"].values())
                and all(per_key[winner]["meets_jaccard"].values()))

    decomp = m["decomposition"]
    losses = [r for r in decomp if r["verdict"] != "emitted"]
    tie = [r for r in losses if r["verdict"].startswith("TIE_LOSS")]
    score = [r for r in losses if r["verdict"] == "SCORE_LOSS"]
    emitted = [r for r in decomp if r["verdict"] == "emitted"]
    rescue = {k: sum(1 for r in tie if k in r["saved_by"]) for k in KEYS[1:]}
    regress = {k: sum(1 for r in emitted if k not in r["saved_by"]) for k in KEYS[1:]}

    decisive_losses = [r for r in losses if f"{r['topic']}/{r['arm']}" in
                       {"defaults-savings/R40", "llm-lit-search/R40"}]

    ruling = {
        "winner": winner,
        "step1_survivors": step1,
        "jaccard_winner_by_topic": j_winner_by_topic,
        "jaccard_conflict_across_topics": len(set(j_winner_by_topic.values())) > 1,
        "winner_restores_stability_and_worst_run_recall": restores,
        "per_key": per_key,
        "decomposition_all_cells": dict(Counter(r["verdict"] for r in losses)),
        "decomposition_R40_only": dict(Counter(r["verdict"] for r in decisive_losses)),
        "score_loss_share_all": round(len(score) / len(losses), 3),
        "score_loss_share_R40": round(
            sum(1 for r in decisive_losses if r["verdict"] == "SCORE_LOSS")
            / len(decisive_losses), 3),
        "tie_band_rescued_by": rescue,
        "tie_band_total": len(tie),
        "goldens_K0_emitted": len(emitted),
        "goldens_lost_by_ladder": regress,
        "net_golden_delta": {k: rescue[k] - regress[k] for k in KEYS[1:]},
        "key_tier_run_stability_R40": {
            c: {"overall_pct_stable": ks[c]["overall"]["pct_stable"],
                "histogram_pct_stable": ks[c]["histogram"]["pct_stable"]}
            for c in DECISIVE},
        "ruling": ("SELECTION FIX SUFFICIENT" if restores else "PHASE 1.4 NECESSARY"),
    }
    (C.HERE / "results" / "ruling.json").write_text(json.dumps(ruling, indent=1))
    print(json.dumps({k: v for k, v in ruling.items() if k != "per_key"}, indent=1))
    print()
    for k in KEYS:
        p = per_key[k]
        print(f"{k}: worst {p['worst_recall_by_topic']} J {p['jaccard_by_topic']} "
              f"avgJ {p['jaccard_mean_of_topics']} len {p['key_length']}")


if __name__ == "__main__":
    main()
