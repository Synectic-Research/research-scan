"""Offline check of the three probe orderings: same set, no cross-band movement, real movement."""
from __future__ import annotations
import json, sys, types
from pathlib import Path

HERE = Path(__file__).resolve().parent
REPO = HERE.parents[3]
sys.path.insert(0, str(REPO / "research/experiments/phase11-golden"))
sys.modules.setdefault("anthropic", types.ModuleType("anthropic"))
sys.path.insert(0, str(HERE))
import stability as ST  # noqa: E402

for topic, slug in (("defaults-savings", "p11-t1"), ("llm-lit-search", "p11-t2")):
    sl = json.loads((HERE / "shortlists" / f"{slug}-T1at40.json").read_text())
    for arm in ("R15", "R20", "R25", "R40"):
        i_rows, o_rows = ST.RR.cut(sl, ST.ARMS[arm])
        canon = i_rows + o_rows
        bands = ST._bands(i_rows) + ST._bands(o_rows)
        band_sizes = [len(b) for b in bands]
        line = f"{topic:16s} {arm:4s} n={len(canon):3d} bands={len(bands):2d} sizes={band_sizes}"
        for o in ("O2", "O3"):
            new = ST.reorder(i_rows, o) + ST.reorder(o_rows, o)
            assert {r['cid'] for r in new} == {r['cid'] for r in canon}
            pos0 = {r["cid"]: i for i, r in enumerate(canon)}
            moved = sum(1 for i, r in enumerate(new) if pos0[r["cid"]] != i)
            maxmove = max((abs(pos0[r["cid"]] - i) for i, r in enumerate(new)), default=0)
            # band containment: every row keeps its (score, criteria_supported)
            keys0 = [(r.get("score"), r.get("criteria_supported")) for r in canon]
            keys1 = [(r.get("score"), r.get("criteria_supported")) for r in new]
            line += f" | {o}: moved={moved} max={maxmove} bands_intact={keys0 == keys1}"
        print(line)
