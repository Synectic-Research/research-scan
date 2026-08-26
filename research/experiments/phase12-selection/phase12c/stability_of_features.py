"""Phase-1.2C — is the tie-break key itself run-stable?

A TIE-LOSS is only *recoverable* if the feature that would break the tie holds still across
replicates. This measures, per cell, how many distinct values each candidate's key tiers take
across that cell's replicates — separating tiers the model re-produces on every call
(`overall`, the per-criterion histogram) from tiers recorded upstream once and joined
(`screen`, `criteria_supported`, T1 rank, origin count, date).
"""
from __future__ import annotations

import json
import statistics
from collections import defaultdict  # noqa: F401  — used by the per-cid value map below

import common12c as C
import ladders
from replay import pairs_for


def main() -> None:
    cells = defaultdict(list)
    for run in C.runs():
        cells[f"{run.topic}/{run.arm}/{run.ordering}"].append(run)

    out = {}
    for cell, runs in cells.items():
        if len(runs) < 2:
            continue
        vals = defaultdict(lambda: defaultdict(set))
        for run in runs:
            for _, e in pairs_for(run):
                h = ladders._histogram(e)
                vals[e.cid]["overall"].add(e.overall)
                vals[e.cid]["histogram"].add(h)
                vals[e.cid]["overall+hist"].add((e.overall, *h))
                vals[e.cid]["relation"].add(e.relation.value if e.relation else None)
                vals[e.cid]["review_flag"].add(bool(e.flags.review))
                vals[e.cid]["contradicts_flag"].add(bool(e.flags.contradicts))
        shown = [c for c, v in vals.items() if len(v["overall"]) or True]
        row = {"n_replicates": len(runs), "rows": len(shown)}
        for tier in ("overall", "histogram", "overall+hist", "relation",
                     "review_flag", "contradicts_flag"):
            distinct = [len(vals[c][tier]) for c in shown]
            row[tier] = {
                "stable_rows": sum(1 for d in distinct if d == 1),
                "unstable_rows": sum(1 for d in distinct if d > 1),
                "pct_stable": round(100 * sum(1 for d in distinct if d == 1) / len(shown), 1),
                "mean_distinct_values": round(statistics.mean(distinct), 3),
                "max_distinct_values": max(distinct),
            }
        out[cell] = row

    # Upstream-joined tiers are recorded once per topic and are stable by construction.
    out["_note"] = ("screen score, criteria_supported, origin_count, best_retrieval_rank, date "
                    "and T1 rank are recorded once in the 1.1/1.2A artefacts and are identical "
                    "across every replicate by construction; only the model-produced tiers above "
                    "are resampled per call.")
    (C.HERE / "results" / "key_stability.json").write_text(json.dumps(out, indent=1))
    for cell, row in out.items():
        if cell.startswith("_"):
            continue
        print(f"{cell:30s} n={row['n_replicates']} rows={row['rows']}  "
              f"overall {row['overall']['pct_stable']}% stable · "
              f"histogram {row['histogram']['pct_stable']}% · "
              f"overall+hist {row['overall+hist']['pct_stable']}% · "
              f"relation {row['relation']['pct_stable']}%")


if __name__ == "__main__":
    main()
