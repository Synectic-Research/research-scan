"""Phase-1.2B — separate L_shortlist / L_cut / L_rerank / L_select for every golden, per cell.

The pipeline has no reranker-produced top-10 distinct from `emit`: the reranker scores every row
it is given and `emit`'s selection rules order and cut. So `rerank_top10` is defined here as
"would be in the top 10 by the reranker's own `overall`, ties broken by the order emit uses",
which is what makes L_rerank (scored too low) separable from L_select (scored high enough, then
displaced by a selection rule: first-author diversity, guarantees, foundational slots, backfill).
"""
from __future__ import annotations

import json
import sys
import types
from collections import Counter
from pathlib import Path

HERE = Path(__file__).resolve().parent
sys.path.insert(0, str(HERE))
sys.modules.setdefault("anthropic", types.ModuleType("anthropic"))
import analyze12b as A  # noqa: E402

ARMS = ["R15", "R20", "R25", "R40"]


def merit_rank(run, ranked: dict, cid: str) -> int:
    """1-based position under `select.order_key` alone — the shipped merit order, no slot rules.

    Below 10 means the reranker's own scores put the paper outside the top ten (L_rerank);
    at or above means the scores were good enough and a selection rule displaced it (L_select).
    """
    cands = {c["cid"]: c for c in json.loads(
        (run / "candidates.json").read_text())["candidates"]}
    def key(k):
        e = ranked[k]
        c = cands[k]
        return (e.get("overall", 0), sum((e.get("criteria") or {}).values()),
                len(c.get("origins") or []), c.get("publication_date") or "0000-00-00")
    order = sorted(ranked, key=key, reverse=True)
    return order.index(cid) + 1


def fate_of(topic: str, arm: str, ordering: str = "O1") -> dict:
    cells = json.loads((HERE / "results" / "cells.json").read_text())
    c = cells.get(f"{topic}/{arm}/{ordering}")
    if not c:
        return {}
    goldens = A.golden_table(topic)
    sl = json.loads(
        (HERE / "shortlists" / f"{A.SLUGS[topic]}-T1at40.json").read_text())
    sl_cids = {r["cid"] for r in sl["in_window"]} | {r["cid"] for r in sl["outside_window"]}
    out = {}
    for doi, g in goldens.items():
        name, cid = g["name"], g["cid"]
        tally = Counter()
        for rep in c["replicates"]:
            run = A.REPO / json.loads(
                (HERE / "runs" / A.SLUGS[topic] / arm / ordering
                 / f"rep{rep['replicate']}" / "summary.json").read_text())["run_dir"]
            sent = set(json.loads((run.parent / "summary.json").read_text())["sent_order"])
            ranked = {e["cid"]: e for e in json.loads((run / "ranked.json").read_text())}
            emitted = rep["emitted"]
            if not cid or (g["screen_score"] or 0) < 2:
                tally["L_screen"] += 1
            elif cid not in sl_cids:
                tally["L_shortlist"] += 1
            elif cid not in sent:
                tally["L_cut"] += 1
            elif cid in emitted:
                tally["emitted"] += 1
            else:
                tally["L_select" if merit_rank(run, ranked, cid) <= 10
                      else "L_rerank"] += 1
        out[name] = {"cid": cid, "screen": g["screen_score"], "n": c["n"], "tally": dict(tally)}
    return out


if __name__ == "__main__":
    report = {}
    for topic in A.SLUGS:
        for arm in ARMS:
            f = fate_of(topic, arm)
            if f:
                report[f"{topic}/{arm}"] = f
    (HERE / "results" / "stagefate.json").write_text(json.dumps(report, indent=1))
    for key, f in report.items():
        print(f"\n=== {key} ===")
        for name, row in f.items():
            t = row["tally"]
            print(f"  {name[:56]:56s} screen={row['screen']}  " +
                  "  ".join(f"{k}={v}/{row['n']}" for k, v in t.items()))
