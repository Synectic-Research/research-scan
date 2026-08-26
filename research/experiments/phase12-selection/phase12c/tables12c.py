"""Phase-1.2C — render every table the report carries, straight from results/*.json."""
from __future__ import annotations

import json
import statistics
from collections import Counter, defaultdict

import common12c as C
import ladders

KEYS = ("K0", "K1", "K2", "K3")
CELL_ORDER = [f"{t}/{a}/{o}" for t in C.SLUGS for a in C.ARMS for o in C.ORDERINGS]


def main() -> None:
    m = json.loads((C.HERE / "results" / "measurements.json").read_text())
    inv = json.loads((C.HERE / "results" / "inventory.json").read_text())
    ks = json.loads((C.HERE / "results" / "key_stability.json").read_text())
    ruling = json.loads((C.HERE / "results" / "ruling.json").read_text())
    replays = json.loads((C.HERE / "results" / "replays.json").read_text())
    cells = m["cells"]
    out: list[str] = []
    w = out.append

    # 1 — feature inventory ---------------------------------------------------------
    w("## 1. Feature inventory — `ranked.json`, over all "
      f"{inv['runs']} recorded runs / {inv['ranked_rows_total']} rows\n")
    w("| field | rows carrying it | values observed |")
    w("|---|---|---|")
    vals = inv["observed_values"]
    shown = {"overall": "overall", "evidence_level": "evidence_level", "relation": "relation"}
    for f, pct in inv["ranked_field_presence_pct"].items():
        v = ""
        if f in shown:
            v = ", ".join(f"`{a}`×{b}" for a, b in vals[shown[f]].items())
        elif f == "criteria":
            v = ("per-criterion grades, ids "
                 + " / ".join(f"{t}: {','.join(i)}" for t, i in inv["criterion_ids_seen"].items())
                 + "; grade counts " + ", ".join(f"`{a}`×{b}"
                                                 for a, b in vals["criteria.grade"].items()))
        elif f == "flags":
            v = ", ".join(f"`{k.split('.')[1]}` true×{c.get('True', 0)}"
                          for k, c in vals.items() if k.startswith("flags."))
        w(f"| `{f}` | {pct}% | {v} |")
    w("")
    w("Joinable from the 1.1 / 1.2A artefacts (recorded once per topic, identical in every "
      "replicate by construction):\n")
    w("| topic | shortlist rows | screen | criteria_supported | origin_count | "
      "best_retrieval_rank | date | T1 rank unique |")
    w("|---|---|---|---|---|---|---|---|")
    for t, j in inv["joinable_shortlist_features"].items():
        n = j["non_null"]
        w(f"| `{t}` | {j['rows']} | {n['screen_score']} | {n['criteria_supported']} | "
          f"{n['origin_count']} | {n['best_retrieval_rank']} | {n['publication_date']} | "
          f"{'yes' if j['t1_rank_unique'] else 'NO'} |")
    w("")

    # 2 — K0 validation --------------------------------------------------------------
    ok = sum(1 for r in replays.values() if r["keys"]["K0"]["reproduces_recorded"])
    w("## 2. K0 control validation\n")
    w(f"`select.select` replayed with the shipped `order_key`, over `ranked.json` order, "
      f"reproduces the recorded `evidence.json` top-10 **cid-for-cid and in rank order in "
      f"{ok}/{len(replays)} runs**. Recall recomputed from the replayed sets equals Phase-1.2B's "
      f"`evalrun.score` figures in {m['cells_checked']}/{m['cells_checked']} cells "
      f"(`recall_validated = {m['recall_validated']}`).\n")

    # 3 — per-ladder results ---------------------------------------------------------
    w("## 3. Per-ladder results\n")
    w("`ceil` is Phase-1.2B's reachable ceiling; `base` the recorded baseline. Reserve fills are "
      "`foundational / contradicting / review / backfill / diversity`, summed over the cell.\n")
    w("| cell | n | ceil | base | key | recall@10 per run | worst | mean | mean pairwise J | "
      "reserve fills | criterion coverage |")
    w("|---|---|---|---|---|---|---|---|---|---|---|")
    for cell in CELL_ORDER:
        if cell not in cells:
            continue
        row = cells[cell]
        for k in KEYS:
            v = row["keys"][k]
            r = v["reserve_fills"]
            fills = " / ".join(str(sum(r[x])) for x in
                               ("foundational", "contradicting", "review", "backfill", "diversity"))
            cov = ", ".join(sorted(set(v["criterion_coverage"])))
            first = k == "K0"
            w(f"| {cell if first else ''} | {row['n'] if first else ''} | "
              f"{row['reachable_ceiling'] if first else ''} | {row['baseline'] if first else ''} "
              f"| **{k}** | {', '.join(str(x) for x in v['recall10_runs'])} | "
              f"**{v['recall10_worst']}** | {v['recall10_mean']} | {v['jaccard_mean']} | "
              f"{fills} | {cov} |")
    w("")

    w("### Per-golden inclusion frequency, by ladder — the two G1-passing R40 cells\n")
    for cell in ("defaults-savings/R40/O1", "llm-lit-search/R40/O1"):
        row = cells[cell]
        w(f"**`{cell}`** — n = {row['n']}, reachable ceiling {row['reachable_ceiling']}\n")
        names = sorted(row["keys"]["K0"]["inclusion_freq"])
        w("| golden | " + " | ".join(KEYS) + " |")
        w("|---|" + "---|" * len(KEYS))
        for n in names:
            w(f"| {n[:62]} | " + " | ".join(row["keys"][k]["inclusion_freq"][n] for k in KEYS)
              + " |")
        w("")

    # 4 — tie depth -------------------------------------------------------------------
    w("## 4. Tie depth at the cut boundary\n")
    w("Per run, the two in-window rows straddling the last filled main slot are compared and the "
      "first key tier at which they differ is recorded. \"terminal\" means the ladder fell through "
      "to its last tier — T1 rank for K1–K3, and for K0 the stable sort over `ranked.json` order, "
      "i.e. the reranker's own emitted order. Determinism by fiat: reproducible, and carrying no "
      "signal.\n")
    w("| key | tiers | resolved at each tier (of 30 runs) | fell through to terminal | "
      "mean tie band (full prefix) | mean `overall` band |")
    w("|---|---|---|---|---|---|")
    for k in KEYS:
        rows = [r for r in m["tie_depth"] if r["key"] == k]
        c = Counter(r["resolved_tier"] for r in rows)
        order = [t for t in ladders.TIERS[k] if t in c]
        w(f"| **{k}** | {len(ladders.TIERS[k])} | "
          + ", ".join(f"`{t}` {c[t]}" for t in order)
          + f" | **{sum(r['terminal'] for r in rows)}/{len(rows)}** | "
          f"{statistics.mean(r['band_width'] for r in rows):.2f} | "
          f"{statistics.mean(r['overall_band_width'] for r in rows):.1f} |")
    w("")
    w("### The saturation band, per run — K0, `overall` band at the boundary\n")
    w("Column `1.2B tie` is the count Phase-1.2B reported as \"rows tied on the exact key "
      "deciding tenth place\"; reproduced here as the K0 prefix `(overall, criteria_sum)`.\n")
    w("| run | in-window rows | cut at | boundary `overall` | rows sharing it | 1.2B tie |")
    w("|---|---|---|---|---|---|")
    for r in [x for x in m["tie_depth"] if x["key"] == "K0"]:
        w(f"| `{r['run']}` | {r['in_window_rows']} | {r['cut_position']} | "
          f"{r['boundary_overall']} | **{r['overall_band_width']}** | {r['band_by_depth'][1]} |")
    w("")

    # 5 — decomposition ---------------------------------------------------------------
    w("## 5. TIE-LOSS vs SCORE-LOSS decomposition\n")
    w("One row per (run, golden) where the golden **reached the reranker** and was not emitted "
      "under K0. The boundary row is the weakest in-window pick the run actually emitted. "
      "`SCORE_LOSS` = the golden's `overall` is strictly below the boundary row's, so **no ladder "
      "beginning with `overall DESC` can recover it, by construction**. `TIE_LOSS_BAND` = equal "
      "`overall`, so a richer key *could* in principle recover it — whether one *does* is the "
      "replay's own answer, in the last two columns.\n")
    w("| topic | arm | verdict counts | K1 rescues | K2 rescues | K3 rescues |")
    w("|---|---|---|---|---|---|")
    agg = defaultdict(list)
    for r in m["decomposition"]:
        if r["verdict"] != "emitted":
            agg[(r["topic"], r["arm"])].append(r)
    for (t, a), rows in agg.items():
        c = Counter(r["verdict"] for r in rows)
        res = {k: sum(1 for r in rows if k in r["saved_by"]) for k in KEYS[1:]}
        w(f"| `{t}` | {a} | " + ", ".join(f"{v} {kk.replace('_', '-')}" for kk, v in c.items())
          + f" | {res['K1']}/{len(rows)} | {res['K2']}/{len(rows)} | {res['K3']}/{len(rows)} |")
    w("")
    w("### Per golden, on the two G1-passing R40 cells\n")
    w("| topic | golden | runs reached | emitted (K0) | TIE-LOSS | SCORE-LOSS | "
      "golden `overall` | boundary `overall` |")
    w("|---|---|---|---|---|---|---|---|")
    g = defaultdict(lambda: {"c": Counter(), "ov": set(), "bov": set()})
    for r in m["decomposition"]:
        if r["arm"] != "R40":
            continue
        e = g[(r["topic"], r["golden"])]
        e["c"][r["verdict"]] += 1
        e["ov"].add(r["golden_overall"])
        e["bov"].add(r["boundary_overall"])
    for (t, name), e in g.items():
        tot = sum(e["c"].values())
        w(f"| `{t}` | {name[:52]} | {tot} | {e['c']['emitted']} | "
          f"{e['c']['TIE_LOSS_BAND'] + e['c']['TIE_LOSS_STRICT']} | {e['c']['SCORE_LOSS']} | "
          f"{sorted(e['ov'])} | {sorted(e['bov'])} |")
    w("")
    w("### Net golden delta of each ladder, whole slice\n")
    w("| ladder | tie-band losses rescued | goldens K0 emitted that the ladder loses | net |")
    w("|---|---|---|---|")
    for k in KEYS[1:]:
        w(f"| **{k}** | {ruling['tie_band_rescued_by'][k]}/{ruling['tie_band_total']} | "
          f"{ruling['goldens_lost_by_ladder'][k]}/{ruling['goldens_K0_emitted']} | "
          f"**{ruling['net_golden_delta'][k]:+d}** |")
    w("")

    # 6 — key-tier run stability -------------------------------------------------------
    w("## 6. Is the tie-break key itself run-stable?\n")
    w("Percentage of candidate rows whose value for that tier is **identical across every "
      "replicate of the cell**. Upstream-joined tiers (screen, `criteria_supported`, "
      "`origin_count`, `best_retrieval_rank`, date, T1 rank) are 100% by construction — they are "
      "recorded once and never re-asked.\n")
    w("| cell | n | rows | `overall` | grade histogram | `overall`+histogram | `relation` | "
      "`flags.review` | `flags.contradicts` |")
    w("|---|---|---|---|---|---|---|---|---|")
    for cell in CELL_ORDER:
        if cell not in ks:
            continue
        r = ks[cell]
        w(f"| `{cell}` | {r['n_replicates']} | {r['rows']} | "
          + " | ".join(f"{r[t]['pct_stable']}%" for t in
                       ("overall", "histogram", "overall+hist", "relation",
                        "review_flag", "contradicts_flag")) + " |")
    w("")

    # 7 — ruling -----------------------------------------------------------------------
    w("## 7. Decision rule\n")
    w("| ladder | key tiers | worst recall@10 t1 R40 (base 5) | worst recall@10 t2 R40 (base 3) | "
      "mean J t1 R40 | mean J t2 R40 | mean of the two |")
    w("|---|---|---|---|---|---|---|")
    for k in KEYS:
        p = ruling["per_key"][k]
        w(f"| **{k}** | {p['key_length']} | "
          f"{p['worst_recall_by_topic']['defaults-savings/R40/O1']}/10 | "
          f"{p['worst_recall_by_topic']['llm-lit-search/R40/O1']}/6 | "
          f"{p['jaccard_by_topic']['defaults-savings/R40/O1']} | "
          f"{p['jaccard_by_topic']['llm-lit-search/R40/O1']} | "
          f"{p['jaccard_mean_of_topics']} |")
    w("")
    w(f"Step 1 (worst-run recall@10 per topic) separates nothing: survivors "
      f"{ruling['step1_survivors']}. Step 2 (mean Jaccard) conflicts across topics — "
      f"{ruling['jaccard_winner_by_topic']} — and averaging the two topics selects "
      f"**{ruling['winner']}**.\n")
    w(f"**Winner restores stability AND worst-run recall at R40 on both topics: "
      f"`{ruling['winner_restores_stability_and_worst_run_recall']}`.**\n")
    w(f"**RULING: {ruling['ruling']}.**\n")

    (C.HERE / "results" / "tables.md").write_text("\n".join(out))
    print("\n".join(out[:40]))
    print(f"\n… wrote {len(out)} lines to results/tables.md")


if __name__ == "__main__":
    main()
