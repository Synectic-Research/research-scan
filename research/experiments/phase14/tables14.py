"""Phase-1.4 — the report's tables, rendered from `results/cells.json` and `results/ruling.json`.

Every number the report quotes resolves to a file under this directory. Nothing is retyped by hand:
the report body cites `results/tables.md`, which this module writes.
"""

from __future__ import annotations

import json
import statistics
import sys
from pathlib import Path

HERE = Path(__file__).resolve().parent
sys.path.insert(0, str(HERE))

import analyze14  # noqa: E402
import variants  # noqa: E402

CELLS = list(variants.CELLS)
TOPICS = list(analyze14.SLUGS)


def _mean(values) -> str:
    return f"{statistics.mean(values):.2f}" if values else "—"


def cells_table(cells: dict) -> str:
    rows = ["| cell | n | reachable ceiling | recall@10 per run | min | mean | Δ vs C0 | "
            "top-tier share | mean pairwise J | criterion coverage | cost |",
            "|---|---|---|---|---|---|---|---|---|---|---|"]
    for topic in TOPICS:
        ctrl = cells.get(f"{topic}/C0")
        rows.append(f"| **{topic}** | | | | | | | | | | |")
        for name in CELLS:
            c = cells.get(f"{topic}/{name}")
            if not c:
                rows.append(f"| {name} | — | | | | | | | | | |")
                continue
            delta = (f"{c['recall10_mean'] - ctrl['recall10_mean']:+.3f}"
                     if ctrl and name != "C0" else "—")
            rows.append(
                f"| **{name}** | {c['n']} | {c['reachable_ceiling']}/{c['expected']} | "
                f"{', '.join(map(str, c['recall10_runs']))} | **{c['recall10_min']}** | "
                f"{c['recall10_mean']} | {delta} | {c['top_tier_share_mean']:.3f} | "
                f"{c['jaccard_mean']} | {'/'.join(sorted(set(c['criterion_coverage'])))} | "
                f"${c['cost_usd_sum']:.2f} |")
    return "\n".join(rows)


def fg_table(cells: dict, topic: str) -> str:
    ctrl = cells.get(f"{topic}/C0")
    if not ctrl:
        return f"_no data for {topic}_"
    rows = [f"**`{topic}`** — every golden named, C0 vs each cell. `reached` is how many replicates"
            f" delivered the paper to the reranker at all; a golden the frontier never carries"
            f" cannot be emitted by any cell.\n",
            "| golden | reached (C0) | " + " | ".join(CELLS) + " |",
            "|---|---|" + "---|" * len(CELLS)]
    for doi, lab in ctrl["labels"].items():
        cs = []
        for name in CELLS:
            c = cells.get(f"{topic}/{name}")
            cs.append(c["f_g"].get(doi, "—") if c else "—")
        rows.append(f"| {lab} | {ctrl['f_g_reached'][doi]} | " + " | ".join(cs) + " |")
    return "\n".join(rows)


def saturation_table(cells: dict) -> str:
    rows = ["| topic | cell | n | rows | `overall` histogram 0/1/2/3 | top-tier rows per run | "
            "top-tier share | relative cut vs C0 |", "|---|---|---|---|---|---|---|---|"]
    for topic in TOPICS:
        ctrl = cells.get(f"{topic}/C0")
        for name in CELLS:
            c = cells.get(f"{topic}/{name}")
            if not c:
                continue
            hist = c["overall_histogram_sum"]
            cut = ("—" if not ctrl or name == "C0" or not ctrl["top_tier_share_mean"]
                   else f"{1 - c['top_tier_share_mean'] / ctrl['top_tier_share_mean']:+.1%}")
            rows.append(
                f"| {topic} | **{name}** | {c['n']} | {c['replicates'][0]['rows']} | "
                f"{hist['0']}/{hist['1']}/{hist['2']}/{hist['3']} | "
                f"{', '.join(map(str, c['top_tier_rows_runs']))} | "
                f"{c['top_tier_share_mean']:.3f} | {cut} |")
    return "\n".join(rows)


def slots_table(cells: dict) -> str:
    rows = ["| topic | cell | review | contradicting | foundational | backfill | "
            "contradiction incl. freq | foundational incl. freq |",
            "|---|---|---|---|---|---|---|---|"]
    for topic in TOPICS:
        for name in CELLS:
            c = cells.get(f"{topic}/{name}")
            if not c:
                continue
            rows.append(
                f"| {topic} | **{name}** | {_mean(c['review_slots'])} | "
                f"{_mean(c['contradicting_slots'])} | {_mean(c['foundational_slots'])} | "
                f"{_mean(c['backfill_slots'])} | {c['contradiction_inclusion_freq']} | "
                f"{c['foundational_inclusion_freq']} |")
    return "\n".join(rows)


def decomposition_table(cells: dict, shipped: dict) -> str:
    """S cells only: the cell's own selection vs the shipped key over one `ranked.json`."""
    rows = ["| topic | cell | recall@10 under the cell's key | under the shipped key | "
            "attributable to `priority_rank` |", "|---|---|---|---|---|"]
    for topic in TOPICS:
        for name in CELLS:
            if not variants.uses_priority_rank(name):
                continue
            a, b = cells.get(f"{topic}/{name}"), shipped.get(f"{topic}/{name}")
            if not a or not b:
                continue
            rows.append(
                f"| {topic} | **{name}** | {a['recall10_mean']} ({a['recall10_runs']}) | "
                f"{b['recall10_mean']} ({b['recall10_runs']}) | "
                f"{a['recall10_mean'] - b['recall10_mean']:+.3f} |")
    return "\n".join(rows) if len(rows) > 2 else "_no S-cell data yet_"


def ruling_table(ruling: dict) -> str:
    heads = ["materially better", "non-inferior both topics", "no stable golden lost",
             "no special-slot regression", "less saturated"]
    rows = ["| cell | " + " | ".join(heads) + " | **adopt** |",
            "|---|---|---|---|---|---|---|"]
    order = ["materially_better", "non_inferior_both_topics", "no_stable_golden_lost",
             "no_special_slot_regression", "substantially_less_saturated"]
    for name, v in ruling["verdicts"].items():
        marks = []
        for key in order:
            c = v["clauses"].get(key)
            marks.append("n/a" if c is None else ("PASS" if c["pass"] else "**FAIL**"))
        rows.append(f"| **{name}** | " + " | ".join(marks)
                    + f" | {'**ADOPT**' if v['adopt'] else 'no'} |")
    return "\n".join(rows)


def main() -> None:
    res = HERE / "results"
    cells = json.loads((res / "cells.json").read_text())
    shipped = json.loads((res / "cells_shipped_key.json").read_text())
    ruling = json.loads((res / "ruling.json").read_text())
    ledger = json.loads((res / "spend.json").read_text()) if (res / "spend.json").exists() else {}

    parts = [
        "## 1. Per-cell results\n",
        "`Δ vs C0` is the difference in mean recall@10 against the fresh control in the same"
        " topic. `reachable ceiling` is how many goldens the frozen R40 frontier delivers to the"
        " reranker; no cell can exceed it.\n",
        cells_table(cells),
        "\n\n## 2. Per-golden inclusion frequency `f_g`\n",
        fg_table(cells, "defaults-savings"),
        "\n",
        fg_table(cells, "llm-lit-search"),
        "\n\n## 3. Top-tier population share — the saturation metric\n",
        saturation_table(cells),
        "\n\n## 4. Guaranteed slots and special-slot inclusion\n",
        slots_table(cells),
        "\n\n## 5. Where an S-cell change came from\n",
        "The same `ranked.json`, selected twice: once under the cell's own ordering key, once under"
        " the shipped key. The gap is what `priority_rank` did; the rest is the rubric moving the"
        " judgements.\n",
        decomposition_table(cells, shipped),
        "\n\n## 6. The pre-registered outcome rule\n",
        f"Thresholds fixed before the first replicate: {json.dumps(ruling['thresholds'])}\n",
        ruling_table(ruling),
        f"\n\n**Main effects (mean recall@10):** `{json.dumps(ruling['main_effects'])}`\n",
        f"\n**OUTCOME: {ruling['outcome']}**\n",
    ]
    if ledger:
        parts.append(f"\n\n## 7. Spend\n\n`${ledger['total_usd']:.4f}` over "
                     f"{len(ledger['calls'])} recorded calls.\n")
    (res / "tables.md").write_text("\n".join(parts))
    print((res / "tables.md").read_text())


if __name__ == "__main__":
    main()
