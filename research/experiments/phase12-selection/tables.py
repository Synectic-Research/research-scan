"""Render the sweep tables for the Phase-1.2A report. Reads results/sweep.json only."""
from __future__ import annotations
import json
from pathlib import Path

HERE = Path(__file__).parent
data = {r["key"]: r for r in json.loads((HERE / "results/sweep.json").read_text())}
ORDER = ["T0", "T1", "T2"]
CAPS = ["40", "60", "80", "120", "inf"]


def block(key: str) -> str:
    r = data[key]
    out = [f"#### `{key}` — {r['label']}", ""]
    out.append(f"pool screened {r['pool_screened']} · ≥2 population **{r['pool_ge2']}** "
               f"({r['pool_ge2_in_window']} in-window, {r['pool_ge2_out_window']} out) · "
               f"goldens retrieved **{r['goldens_retrieved']}/{r['goldens_expected']}** · "
               f"goldens ≥2 **{r['goldens_ge2']}** · "
               f"`criteria_hit` present: **{'yes' if r['criteria_available'] else 'no'}**")
    out.append("")
    out.append("| config | shortlist (in+out) | goldens ≥2 kept | lost to cap | lost to ordering "
               "| criterion coverage | contradicting (retro) | foundational | score 3 | score 2 |")
    out.append("|---|---|---|---|---|---|---|---|---|---|")
    for pol in ORDER:
        for cap in CAPS:
            c = r["configs"][f"{pol}@{cap}"]
            diag = " *(diag)*" if cap == "inf" else ""
            out.append(
                f"| **{pol}@{cap}**{diag} | {c['shortlist_size']} ({c['shortlist_in']}+{c['shortlist_out']}) "
                f"| **{len(c['goldens_surviving'])}/{r['goldens_ge2']}** "
                f"| {len(c['goldens_lost_to_cap'])} | {len(c['goldens_lost_to_ordering'])} "
                f"| {c['criteria_covered']}/{c['criteria_total']} "
                f"| {c['contradicting_retained_retrospective']} "
                f"| {c['foundational_retained']} | {c['score3_retained']} | {c['score2_retained']} |")
    out.append("")
    return "\n".join(out)


def named_table() -> str:
    out = ["| input run | config | OpenScholar | LitSearch |", "|---|---|---|---|"]
    for key in ["t2-stateless", "t2-control", "t2-control+attr"]:
        r = data[key]
        for pol in ORDER:
            for cap in CAPS:
                c = r["configs"][f"{pol}@{cap}"]
                cells = []
                for name in ("OpenScholar", "LitSearch"):
                    f = c["named_fate"].get(name)
                    if f is None:
                        cells.append("not retrieved")
                    else:
                        mark = "**in**" if f["in_shortlist"] else "out"
                        cells.append(f"{mark} (rank {f['policy_rank']})")
                out.append(f"| `{key}` | {pol}@{cap} | {cells[0]} | {cells[1]} |")
    return "\n".join(out)


def survival_matrix() -> str:
    keys = ["t1-stateless", "t2-stateless", "t1-control", "t2-control",
            "t1-control+attr", "t2-control+attr"]
    out = ["| config | " + " | ".join(f"`{k}`" for k in keys) + " | pooled (stateless) |",
           "|---|" + "---|" * (len(keys) + 1)]
    for pol in ORDER:
        for cap in CAPS:
            row, pooled, denom = [], 0, 0
            for k in keys:
                c = data[k]["configs"][f"{pol}@{cap}"]
                kept, tot = len(c["goldens_surviving"]), data[k]["goldens_ge2"]
                row.append(f"{kept}/{tot}")
                if k.endswith("stateless"):
                    pooled += kept
                    denom += tot
            out.append(f"| {pol}@{cap} | " + " | ".join(row) + f" | **{pooled}/{denom}** |")
    return "\n".join(out)


if __name__ == "__main__":
    parts = ["## Per-run sweep tables", ""]
    for key in data:
        parts.append(block(key))
    parts += ["## OpenScholar / LitSearch fate, every configuration", "", named_table(), "",
              "## Golden survival matrix", "", survival_matrix(), ""]
    (HERE / "results/tables.md").write_text("\n".join(parts))
    print("\n".join(parts))
