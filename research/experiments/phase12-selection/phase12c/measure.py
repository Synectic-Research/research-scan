"""Phase-1.2C — per-key, per-cell measurements and the two branch-deciding diagnostics.

Recall is defined by golden cid membership and is *validated against Phase-1.2B's recorded
`evalrun.score` figures on K0* before any other key's recall is reported (`recall_validated`).
"""
from __future__ import annotations

import itertools
import json
import statistics
from collections import Counter, defaultdict

import common12c as C
import analyze12b as A          # Phase-1.2B's golden table, unchanged
import ladders
from replay import pairs_for, resolve_depth

KEYS = ("K0", "K1", "K2", "K3")


def jaccard(a: set, b: set) -> float:
    return len(a & b) / len(a | b) if (a | b) else 1.0


def golden_cids(topic: str) -> dict[str, str]:
    """golden display name -> cid, for goldens that have one in this pool."""
    return {g["name"]: g["cid"] for g in A.golden_table(topic).values() if g["cid"]}


def main() -> None:
    replays = json.loads((C.HERE / "results" / "replays.json").read_text())
    cells12b = json.loads((C.P12B / "results" / "cells.json").read_text())
    runs = {r.key: r for r in C.runs()}

    per_run: dict[str, dict] = {}
    tie_rows: list[dict] = []
    decomp_rows: list[dict] = []

    for key, run in runs.items():
        rep = replays[key]
        feats = C.shortlist_features(run.topic)
        ranks = C.t1_rank(run.topic)
        keyfns = ladders.make_keys(feats, ranks)
        pairs = pairs_for(run)
        by_cid = {e.cid: (c, e) for c, e in pairs}
        sent = set(run.summary["sent_order"])
        goldens = golden_cids(run.topic)
        criteria_ids = [c["id"] for c in run.load("queries.json")["sub_criteria"]]

        entry = {}
        for kname in KEYS:
            r = rep["keys"][kname]
            emitted = r["emitted"]
            found = {n: (cid in emitted) for n, cid in goldens.items()}
            covered = {
                cid_key for cid_key in criteria_ids
                if any(by_cid[c][1].criteria.get(cid_key, 0) >= 2 for c in emitted if c in by_cid)
            }
            entry[kname] = {
                "emitted": emitted,
                "recall10": sum(found.values()),
                "found": found,
                "reasons": Counter(r["reasons"]),
                "criterion_coverage": [len(covered), len(criteria_ids)],
                "relation_contradicting": sum(
                    1 for c in emitted
                    if by_cid[c][1].relation is not None
                    and by_cid[c][1].relation.value == "contradicting"),
            }

            # ---- (a) TIE DEPTH at the cut boundary -------------------------------------
            merit = r["in_window_merit"]
            n_inw = len(r["in_window_emitted"])
            tiers = ladders.TIERS[kname]
            if 0 < n_inw < len(merit):
                lo, hi = by_cid[merit[n_inw - 1]], by_cid[merit[n_inw]]
                depth, tier = resolve_depth(keyfns[kname], tiers, lo, hi)
                kb = keyfns[kname](lo)
                band = [c for c in merit if keyfns[kname](by_cid[c])[:-1] == kb[:-1]]
                b_overall = by_cid[merit[n_inw - 1]][1].overall
                overall_band = [c for c in merit if by_cid[c][1].overall == b_overall]
                tie_rows.append({
                    "run": key, "topic": run.topic, "arm": run.arm, "ordering": run.ordering,
                    "key": kname, "cut_position": n_inw, "resolved_at": depth,
                    "resolved_tier": tier, "terminal": depth == len(tiers) - 1,
                    # rows sharing the boundary row's whole key prefix, terminal tie-break excluded
                    "band_width": len(band),
                    # rows sharing the boundary row's key prefix at each depth: [tier0, tier0+1, …].
                    # Phase-1.2B's "2-5 rows tied on the deciding key" is depth 2 under K0.
                    "band_by_depth": [
                        len([c for c in merit
                             if keyfns[kname](by_cid[c])[:i + 1] == kb[:i + 1]])
                        for i in range(len(kb))
                    ],
                    # rows sharing the boundary row's `overall` — the saturation band no ladder
                    # beginning with `overall DESC` can reorder across
                    "overall_band_width": len(overall_band),
                    "boundary_overall": b_overall,
                    "in_window_rows": len(merit),
                })

        # ---- (b) TIE-LOSS vs SCORE-LOSS, against the K0 boundary -----------------------
        k0 = rep["keys"]["K0"]
        boundary = k0["boundary_cid"]
        if boundary:
            b_cand, b_entry = by_cid[boundary]
            b_key = ladders.SHIPPED_ORDER_KEY((b_cand, b_entry))
            for name, cid in goldens.items():
                if cid not in sent or cid not in by_cid:
                    continue                       # never reached the reranker: upstream loss
                if cid in k0["emitted"]:
                    verdict = "emitted"
                else:
                    g_cand, g_entry = by_cid[cid]
                    g_key = ladders.SHIPPED_ORDER_KEY((g_cand, g_entry))
                    if g_entry.overall < b_entry.overall:
                        verdict = "SCORE_LOSS"
                    elif g_key == b_key:
                        verdict = "TIE_LOSS_STRICT"
                    elif g_entry.overall == b_entry.overall:
                        verdict = "TIE_LOSS_BAND"
                    else:
                        verdict = "SLOT_LOSS"
                decomp_rows.append({
                    "run": key, "topic": run.topic, "arm": run.arm, "ordering": run.ordering,
                    "rep": run.rep, "golden": name, "cid": cid, "verdict": verdict,
                    "golden_overall": by_cid[cid][1].overall,
                    "boundary_overall": b_entry.overall,
                    "boundary_cid": boundary,
                    "saved_by": [k for k in KEYS if cid in rep["keys"][k]["emitted"]],
                })
        per_run[key] = entry

    # ---- aggregate to cells ---------------------------------------------------------
    cells: dict[str, dict] = {}
    by_cell: dict[str, list[str]] = defaultdict(list)
    for key in per_run:
        by_cell[key.rsplit("/rep", 1)[0]].append(key)

    for cell, members in by_cell.items():
        topic = cell.split("/")[0]
        goldens = golden_cids(topic)
        rec = cells12b.get(cell.replace(f"{topic}/", f"{topic}/"), {})
        row = {"n": len(members), "topic": topic,
               "reachable_ceiling": rec.get("reachable_ceiling"),
               "expected": rec.get("expected"),
               "baseline": C.BASELINE_RECALL10[topic],
               "recorded_recall10": rec.get("recall10_runs"),
               "keys": {}}
        for kname in KEYS:
            recalls = [per_run[m][kname]["recall10"] for m in members]
            tops = [set(per_run[m][kname]["emitted"]) for m in members]
            pw = [jaccard(a, b) for a, b in itertools.combinations(tops, 2)]
            freq = {n: sum(1 for m in members if per_run[m][kname]["found"][n])
                    for n in goldens}
            row["keys"][kname] = {
                "recall10_runs": recalls,
                "recall10_worst": min(recalls), "recall10_mean": round(statistics.mean(recalls), 3),
                "jaccard_mean": round(statistics.mean(pw), 4) if pw else None,
                "jaccard_min": round(min(pw), 4) if pw else None,
                "inclusion_freq": {n: f"{v}/{len(members)}" for n, v in sorted(freq.items())},
                "reserve_fills": {
                    "foundational": [per_run[m][kname]["reasons"].get("foundational", 0)
                                     for m in members],
                    "contradicting": [per_run[m][kname]["reasons"].get("contradicting", 0)
                                      for m in members],
                    "review": [per_run[m][kname]["reasons"].get("review", 0) for m in members],
                    "backfill": [per_run[m][kname]["reasons"].get("backfill", 0) for m in members],
                    "diversity": [per_run[m][kname]["reasons"].get("diversity", 0)
                                  for m in members],
                },
                "relation_contradicting": [per_run[m][kname]["relation_contradicting"]
                                           for m in members],
                "criterion_coverage": [f"{per_run[m][kname]['criterion_coverage'][0]}"
                                       f"/{per_run[m][kname]['criterion_coverage'][1]}"
                                       for m in members],
            }
        cells[cell] = row

    # recall validation: K0 replay recall must equal Phase-1.2B's recorded evalrun figures
    validated, checked = True, 0
    for cell, row in cells.items():
        recorded = row["recorded_recall10"]
        if recorded is not None:
            checked += 1
            if row["keys"]["K0"]["recall10_runs"] != recorded:
                validated = False
                print("RECALL MISMATCH", cell, recorded, row["keys"]["K0"]["recall10_runs"])

    out = {"recall_validated": validated, "cells_checked": checked,
           "cells": cells, "tie_depth": tie_rows, "decomposition": decomp_rows,
           "per_run": per_run}
    (C.HERE / "results" / "measurements.json").write_text(json.dumps(out, indent=1, default=str))
    print(f"recall validated against Phase-1.2B evalrun figures on K0: {validated} "
          f"({checked} cells)")
    print(f"tie-depth observations: {len(tie_rows)}  decomposition rows: {len(decomp_rows)}")
    print(Counter(r["verdict"] for r in decomp_rows))


if __name__ == "__main__":
    main()
