"""Phase-1.2B — render the report tables from results/cells.json."""
from __future__ import annotations

import json
import statistics
from pathlib import Path

HERE = Path(__file__).resolve().parent
ARMS = ["R15", "R20", "R25", "R40"]
TOPICS = ["defaults-savings", "llm-lit-search"]
SHORT = {"defaults-savings": "t1", "llm-lit-search": "t2"}


def load() -> dict:
    return json.loads((HERE / "results" / "cells.json").read_text())


def cell_table(cells: dict) -> str:
    head = ("| cell | n | reachable ceiling | recall@10 per replicate | worst | mean | "
            "mean pairwise J | reserve fills (found/contra/review) | criterion coverage | "
            "frontier tok (mean) | $ (sum) | wall s (mean) |\n")
    head += "|---|---|---|---|---|---|---|---|---|---|---|---|\n"
    rows = []
    for topic in TOPICS:
        for arm in ARMS:
            c = cells.get(f"{topic}/{arm}/O1")
            if not c:
                continue
            exp = c["expected"]
            reps = ", ".join(f"{r}/{exp}" for r in c["recall10_runs"])
            fills = (f"{'/'.join(map(str, c['foundational_slots']))} · "
                     f"{'/'.join(map(str, c['contradicting_slots']))} · "
                     f"{'/'.join(map(str, c['review_slots']))}")
            rows.append(
                f"| **{SHORT[topic]} {arm}** | {c['n']} | {c['reachable_ceiling']}/{c['expected']} "
                f"| {reps} "
                f"| **{c['recall10_worst']}/{c['expected']}** | {c['recall10_mean']} "
                f"| {c['jaccard_mean']} | {fills} "
                f"| {', '.join(sorted(set(c['criterion_coverage'])))} "
                f"| {c['frontier_tokens_mean']:,} | ${c['cost_usd_sum']:.4f} "
                f"| {c['wall_s_mean']:.0f} |")
    return head + "\n".join(rows)


def inclusion_table(cells: dict) -> str:
    out = []
    for topic in TOPICS:
        names = None
        for arm in ARMS:
            c = cells.get(f"{topic}/{arm}/O1")
            if c:
                names = list(c["inclusion_freq"])
                break
        if not names:
            continue
        out.append(f"\n**{topic}**\n")
        out.append("| golden | screen | reaches reranker | "
                   + " | ".join(f"{a} inclusion" for a in ARMS) + " |")
        out.append("|---" * (3 + len(ARMS)) + "|")
        ff = json.loads((HERE / "results" / "frontier_fate.json").read_text())
        fate = ff[topic]["policies"]["T1@40"]["rows"]
        gold = {g["name"]: g for g in ff[topic]["goldens"]}
        for name in names:
            reach = " ".join(a for a in ARMS
                             if fate.get(name, {}).get("reaches_reranker", {}).get(a)) or "—"
            cellvals = []
            for arm in ARMS:
                c = cells.get(f"{topic}/{arm}/O1")
                cellvals.append(c["inclusion_freq"].get(name, "—") if c else "—")
            out.append(f"| {name} | {gold.get(name, {}).get('screen_score')} | {reach} | "
                       + " | ".join(cellvals) + " |")
    return "\n".join(out)


def probe_table(cells: dict, topic: str, arm: str) -> str:
    out = ["| ordering | n | recall@10 per replicate | mean | top-10 sets (pairwise J within) |",
           "|---|---|---|---|---|"]
    for o in ("O1", "O2", "O3"):
        c = cells.get(f"{topic}/{arm}/{o}")
        if not c:
            continue
        out.append(f"| {o} | {c['n']} | {', '.join(str(r) for r in c['recall10_runs'])} "
                   f"| {c['recall10_mean']} | {c['jaccard_mean']} |")
    return "\n".join(out)


def cross_ordering(cells: dict, topic: str, arm: str) -> dict:
    """Between-ordering Jaccard vs the within-ordering (replicate) Jaccard already measured."""
    import itertools
    groups = {}
    for o in ("O1", "O2", "O3"):
        c = cells.get(f"{topic}/{arm}/{o}")
        if c:
            groups[o] = [set(r["emitted"]) for r in c["replicates"]]
    within, between = [], []
    for o, tops in groups.items():
        within += [len(a & b) / len(a | b) for a, b in itertools.combinations(tops, 2)]
    for o1, o2 in itertools.combinations(groups, 2):
        for a in groups[o1]:
            for b in groups[o2]:
                between.append(len(a & b) / len(a | b))
    return {
        "within_n": len(within), "between_n": len(between),
        "within_mean": round(statistics.mean(within), 4) if within else None,
        "within_min": round(min(within), 4) if within else None,
        "between_mean": round(statistics.mean(between), 4) if between else None,
        "between_min": round(min(between), 4) if between else None,
        "within_pairs": [round(x, 4) for x in within],
        "between_pairs": [round(x, 4) for x in between],
    }


if __name__ == "__main__":
    cells = load()
    md = ["## Cell table\n", cell_table(cells), "\n## Golden inclusion frequencies\n",
          inclusion_table(cells)]
    (HERE / "results" / "tables.md").write_text("\n".join(md))
    print("\n".join(md))
