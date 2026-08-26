"""Phase-1.2B — offline stage-fate: where every golden stands in the T1 order, and whether the
stratified cut at each depth k actually delivers it to the reranker.

Deterministic. No model calls. This is G1's evidence, computed before any tokens are spent.
"""
from __future__ import annotations

import json
import sys
import types
from pathlib import Path

HERE = Path(__file__).resolve().parent
P12 = HERE.parent
REPO = P12.parents[2]
sys.path.insert(0, str(P12))
sys.path.insert(0, str(REPO / "research/experiments/phase11-golden"))
sys.modules.setdefault("anthropic", types.ModuleType("anthropic"))

import importlib.util  # noqa: E402
import sweep as S  # noqa: E402
from research_scan.coverage import KEPT_SCORE  # noqa: E402

spec = importlib.util.spec_from_file_location(
    "p11_rerank", REPO / "research/experiments/phase11-golden/rerank.py")
RR = importlib.util.module_from_spec(spec)
spec.loader.exec_module(RR)

TOPICS = {"defaults-savings": "t1-stateless", "llm-lit-search": "t2-stateless"}
DEPTHS = {"R15": 15, "R20": 20, "R25": 25, "R30": 30, "R40": 40, "Rall": 10**6}
CAPS = {"T1@40": 40, "T1@80": 80}


def main() -> None:
    out = {}
    for topic, key in TOPICS.items():
        run = next(r for r in S.RUNS if r.key == key)
        data = run.load()
        pool = [S.features(cid, data) for cid in data["candidates"]
                if data["screen"].get(cid, {}).get("score", 0) >= KEPT_SCORE]
        goldens = S.golden_map(topic, data["candidates"])
        rows = []
        for doi, g in goldens.items():
            cid = g["cid"]
            score = data["screen"].get(cid, {}).get("score") if cid else None
            rows.append({"doi": doi, "name": g["name"], "title": g["title"], "cid": cid,
                         "retrieved": cid is not None, "screen_score": score,
                         "screen_keep": bool(cid) and (score or 0) >= KEPT_SCORE})
        full_in = S.order([f for f in pool if not f["outside_window"]], "T1")
        full_out = S.order([f for f in pool if f["outside_window"]], "T1")
        full_rank = {"in_window": {f["cid"]: i + 1 for i, f in enumerate(full_in)},
                     "outside_window": {f["cid"]: i + 1 for i, f in enumerate(full_out)}}
        for r in rows:
            r["t1_list"] = ("in_window" if r["cid"] in full_rank["in_window"]
                            else "outside_window" if r["cid"] in full_rank["outside_window"]
                            else None)
            r["t1_rank_uncapped"] = (full_rank["in_window"].get(r["cid"])
                                     or full_rank["outside_window"].get(r["cid"]))
        per_policy = {}
        for pname, cap in CAPS.items():
            kept_in, kept_out, _ = S.build(pool, data["criteria"], "T1", cap)
            sl = {"in_window": [{"cid": f["cid"]} for f in kept_in],
                  "outside_window": [{"cid": f["cid"]} for f in kept_out]}
            rank_in = {f["cid"]: i + 1 for i, f in enumerate(kept_in)}
            rank_out = {f["cid"]: i + 1 for i, f in enumerate(kept_out)}
            depths = {}
            for arm, n in DEPTHS.items():
                i_rows, o_rows = RR.cut(sl, n)
                depths[arm] = {"cids": {r["cid"] for r in i_rows} | {r["cid"] for r in o_rows},
                               "n_in": len(i_rows), "n_out": len(o_rows)}
            per_policy[pname] = {
                "shortlist_in": len(kept_in), "shortlist_out": len(kept_out),
                "rows": {r["name"]: {
                    "in_shortlist": bool(r["cid"]) and (
                        r["cid"] in rank_in or r["cid"] in rank_out),
                    "list": ("in_window" if r["cid"] in rank_in
                             else "outside_window" if r["cid"] in rank_out else None),
                    "rank": rank_in.get(r["cid"]) or rank_out.get(r["cid"]),
                    "reaches_reranker": {a: (r["cid"] in d["cids"]) for a, d in depths.items()},
                } for r in rows if r["screen_keep"]},
                "cut_shape": {a: [d["n_in"], d["n_out"]] for a, d in depths.items()},
            }
        out[topic] = {"goldens": rows, "policies": per_policy}
    (HERE / "results" / "frontier_fate.json").write_text(json.dumps(out, indent=1, default=str))

    for topic, d in out.items():
        print(f"\n=== {topic} ===")
        for r in d["goldens"]:
            print(f"  {r['name'][:52]:52s} retr={r['retrieved']} score={r['screen_score']} "
                  f"| T1 uncapped {r.get('t1_list')} rank {r.get('t1_rank_uncapped')}")
        for pname, p in d["policies"].items():
            print(f"  -- {pname}  shortlist {p['shortlist_in']}+{p['shortlist_out']}  "
                  f"cuts {p['cut_shape']}")
            for name, row in p["rows"].items():
                reach = " ".join(a for a, v in row["reaches_reranker"].items() if v) or "NONE"
                lst = row["list"] or "-- CUT --"
                rk = row["rank"] if row["rank"] is not None else "-"
                print(f"     {name[:52]:52s} {lst:15s} rank {rk:>4}  -> {reach}")


if __name__ == "__main__":
    main()
