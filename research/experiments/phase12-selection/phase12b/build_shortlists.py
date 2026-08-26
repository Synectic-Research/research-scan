"""Phase-1.2B — materialise the T1@40 and T1@80 shortlists for both Phase-1.1 stateless runs.

Deterministic, no model calls. Reuses Phase-1.2A's `sweep.py` ordering verbatim (T1 =
score DESC, criteria_supported DESC, origin_count DESC, best_retrieval_rank ASC, date DESC)
and writes a `shortlist.json` in the shipped shape (full candidate rows, `score` and
`outside_window` merged in) so `rerank.py`'s frozen mechanics can consume it unchanged.

Also answers, offline, whether the two policies differ at all as *rerank inputs*: the
stratified cut takes a prefix of each list, and a cap is a truncation of the same order.
"""
from __future__ import annotations

import json
import sys
from pathlib import Path

HERE = Path(__file__).resolve().parent
P12 = HERE.parent
REPO = P12.parents[2]
sys.path.insert(0, str(P12))
sys.path.insert(0, str(REPO / "research/experiments/phase11-golden"))

import sweep as S  # noqa: E402
from lib import common as C  # noqa: E402

POLICIES = {"T1@40": ("T1", 40), "T1@80": ("T1", 80)}
TOPICS = {"defaults-savings": "t1-stateless", "llm-lit-search": "t2-stateless"}


def shortlist_for(run: S.Run, policy: str, cap: int) -> dict:
    data = run.load()
    from research_scan.coverage import KEPT_SCORE
    pool = [S.features(cid, data) for cid in data["candidates"]
            if data["screen"].get(cid, {}).get("score", 0) >= KEPT_SCORE]
    kept_in, kept_out, _ = S.build(pool, data["criteria"], policy, cap)

    def row(f):
        cand = dict(data["candidates"][f["cid"]])
        cand["score"] = data["screen"][f["cid"]]["score"]
        cand["outside_window"] = f["outside_window"]
        # Carried for the order-sensitivity probe's band definition only; `record_payload`
        # never sends it to the model.
        cand["criteria_supported"] = f["criteria_supported"]
        return cand

    return {"in_window": [row(f) for f in kept_in],
            "outside_window": [row(f) for f in kept_out]}


def main() -> None:
    out: dict = {"shortlists": {}, "cut_identity": {}}
    for topic, key in TOPICS.items():
        run = next(r for r in S.RUNS if r.key == key)
        built = {}
        for name, (policy, cap) in POLICIES.items():
            sl = shortlist_for(run, policy, cap)
            built[name] = sl
            path = HERE / "shortlists" / f"{C.TOPICS[topic]['slug']}-{name.replace('@','at')}.json"
            path.parent.mkdir(parents=True, exist_ok=True)
            path.write_text(json.dumps(sl, indent=1))
            out["shortlists"][f"{topic}/{name}"] = {
                "in_window": len(sl["in_window"]), "outside_window": len(sl["outside_window"]),
                "path": str(path.relative_to(REPO)),
            }
        for arm, n in (("R15", 15), ("R20", 20), ("R25", 25), ("R30", 30)):
            cuts = {}
            for name, sl in built.items():
                i, o = C_cut(sl, n)
                cuts[name] = [r["cid"] for r in i] + [r["cid"] for r in o]
            out["cut_identity"][f"{topic}/{arm}"] = {
                "n_in_out": {k: [len(C_cut(built[k], n)[0]), len(C_cut(built[k], n)[1])]
                             for k in built},
                "identical": cuts["T1@40"] == cuts["T1@80"],
                "size": len(cuts["T1@40"]),
            }
    (HERE / "results" / "shortlists.json").write_text(json.dumps(out, indent=1))
    print(json.dumps(out["cut_identity"], indent=1))
    print(json.dumps(out["shortlists"], indent=1))


def _rerank_module():
    """Load the frozen Phase-1.1 rerank driver for its `cut()` — no duplicated cut logic.

    `anthropic` is stubbed because nothing here calls the API; the module imports it at top level.
    """
    import types
    sys.modules.setdefault("anthropic", types.ModuleType("anthropic"))
    import importlib.util
    src = REPO / "research/experiments/phase11-golden/rerank.py"
    spec = importlib.util.spec_from_file_location("p11_rerank", src)
    mod = importlib.util.module_from_spec(spec)
    spec.loader.exec_module(mod)
    return mod


_RR = None


def C_cut(sl, n):
    global _RR
    if _RR is None:
        _RR = _rerank_module()
    return _RR.cut(sl, n)


if __name__ == "__main__":
    main()
