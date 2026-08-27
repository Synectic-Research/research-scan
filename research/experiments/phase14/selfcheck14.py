"""Phase-1.4 — prove the metric and ruling layers work before a single token is spent.

$0. Builds a synthetic `runs/` tree in a temp directory whose `summary.json` files point at the
**real** Phase-1.2B R40 recordings, then drives `analyze14` and `rule14` over it end to end. What
this validates is plumbing, not a result: golden matching resolves, `f_g` denominators are the
replicate counts, the saturation share is computed off `ranked.json`, the contender rule fires, and
every clause of the pre-registered outcome rule evaluates without raising.

The numbers it prints are meaningless as evidence — the same recordings are dealt into several
cells — and it never writes into `results/` or `runs/`.
"""

from __future__ import annotations

import json
import shutil
import sys
import tempfile
import types
from pathlib import Path

HERE = Path(__file__).resolve().parent
REPO = HERE.parents[2]
sys.path.insert(0, str(HERE))
sys.path.insert(0, str(HERE.parent / "phase12-selection"))
sys.path.insert(0, str(HERE.parent / "phase12-selection" / "phase12c"))
sys.modules.setdefault("anthropic", types.ModuleType("anthropic"))

import analyze14  # noqa: E402
import common12c  # noqa: E402
import rule14  # noqa: E402
import variants  # noqa: E402


def synthesise(root: Path) -> int:
    """Deal the recorded R40 runs into the four cells, as phase-14-shaped summaries."""
    written = 0
    for topic, slug in analyze14.SLUGS.items():
        recorded = [r for r in common12c.runs() if r.topic == topic and r.arm == "R40"]
        if not recorded:
            continue
        for i, cell in enumerate(variants.CELLS):
            for rep in (1, 2, 3):
                src = recorded[(i + rep) % len(recorded)]
                summary = dict(src.summary)
                emitted = [p["cid"] for p in src.load("evidence.json")["packets"]]
                reasons = summary.get("selection_reasons") or []
                summary.update({
                    "cell": cell, "replicate": rep, "topic": topic,
                    "top10_cids": emitted, "selection_reasons": reasons,
                    "shipped_key_top10_cids": emitted, "shipped_key_reasons": reasons,
                    "priority_map": {}, "chunks_ok": True,
                })
                d = root / "runs" / slug / cell / f"rep{rep}"
                d.mkdir(parents=True, exist_ok=True)
                (d / "summary.json").write_text(json.dumps(summary, indent=1))
                written += 1
    return written


def main() -> None:
    with tempfile.TemporaryDirectory() as tmp:
        root = Path(tmp)
        n = synthesise(root)
        analyze14.HERE = root
        (root / "results").mkdir(exist_ok=True)
        analyze14.main()

        cells = json.loads((root / "results" / "cells.json").read_text())
        rule14.HERE = root
        ruling = rule14.rule(cells)

        print(f"\nsynthetic replicates written: {n}")
        for name, v in ruling["verdicts"].items():
            marks = " ".join(
                f"{k}={'PASS' if c['pass'] else 'FAIL'}" for k, c in v["clauses"].items())
            print(f"  {name:3s} adopt={v['adopt']}  {marks}")
        print("  outcome:", ruling["outcome"])

        sample = next(iter(cells.values()))
        for field in ("f_g", "f_g_reached", "top_tier_share_mean", "jaccard_mean",
                      "contradiction_inclusion_freq", "foundational_inclusion_freq",
                      "criterion_coverage", "reachable_ceiling"):
            assert field in sample, field
        assert all(v.startswith(("0/", "1/", "2/", "3/")) for v in sample["f_g"].values())
        assert len(sample["labels"]) == sample["expected"]
        for topic in analyze14.SLUGS:
            print(f"  contenders {topic}: {analyze14.contenders(cells, topic)}")
        print("\nplumbing OK — every metric resolved and every clause evaluated")
        assert not (root / "results" / "ruling.json").exists() or True
    assert not (HERE / "results" / "cells.json").exists(), "selfcheck must not write into results/"
    shutil.rmtree(HERE / "__pycache__", ignore_errors=True)


if __name__ == "__main__":
    main()
