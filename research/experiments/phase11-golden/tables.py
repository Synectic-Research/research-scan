"""Render the report's tables from measurements.json. No numbers are computed here."""

from __future__ import annotations

import json
from pathlib import Path

EXP = Path(__file__).resolve().parent
M = json.loads((EXP / "measurements.json").read_text())
ARMS = ["R10", "R15", "R20", "R25", "Rall"]
OUT = []


def w(line=""):
    OUT.append(line)


def frac(t):
    return f"{t[0]}/{t[1]}"


# --- 1. frozen configuration -------------------------------------------------
w("### Per-topic run record\n")
w("| | topic 1 `defaults-savings` | topic 2 `llm-lit-search` |")
w("|---|---|---|")
rows = [
    ("run dir", lambda t: f"`{Path(t['run_dir']).relative_to(EXP.parents[2])}`"),
    ("profile / domain / window",
     lambda t: f"{t['defaults']['profile']} · {t['defaults']['domain']} · "
               f"from {t['defaults']['window']['from']}"),
    ("purpose inferred by the planning call", lambda t: f"`{t['purpose']}`"),
    ("routed sources (hits, failed)",
     lambda t: ", ".join(f"{k} {v['hits']}/{v['failed']}" for k, v in t["per_source"].items())),
    ("pool screened", lambda t: str(t["pool"])),
    ("out-of-window in pool", lambda t: str(t["outside_window_in_pool"])),
    ("screened ≥2", lambda t: str(t["screened_ge2"])),
    ("shortlist (in+out)",
     lambda t: f"{t['shortlist']['in_window']}+{t['shortlist']['outside_window']}"),
    ("gap round", lambda t: f"ran, {t['gap']['n_round2']} queries" if t["gap"]["ran"] else "no"),
]
for label, fn in rows:
    a, b = M["topics"]["defaults-savings"], M["topics"]["llm-lit-search"]
    w(f"| {label} | {fn(a)} | {fn(b)} |")

# --- 2. golden fate ----------------------------------------------------------
for topic in ("defaults-savings", "llm-lit-search"):
    t = M["topics"][topic]
    w(f"\n### {topic} — golden fate\n")
    w("| golden paper | retrieved | screen | ≥2 | shortlist pos | in R15 cut | in R15 top-10 |")
    w("|---|---|---|---|---|---|---|")
    for f in t["golden_fate"]:
        pos = f["shortlist_pos"]
        side = {"in_window": "in", "outside_window": "out"}.get(f["shortlist_side"], "")
        w(f"| `{f['doi']}` {f['title'][:44]} | {'yes' if f['retrieved'] else '**no**'} "
          f"| {f['screen_score'] if f['screen_score'] is not None else '—'} "
          f"| {'yes' if f['screened_ge2'] else '**no**'} "
          f"| {f'{pos} ({side})' if pos else '—'} "
          f"| {'yes' if f['in_cut'].get('R15') else 'no'} "
          f"| {'yes' if f['in_top10'].get('R15') else 'no'} |")

# --- 3. sweep ----------------------------------------------------------------
w("\n### Rerank-depth sweep\n")
w("| topic | arm | reranked (in+out) | recall@10 | recall@25 | foundational | contradicting "
  "(reason / relation) | review | criterion coverage | frontier tok | tok/item | cost | wall s "
  "| judged precision | judged mean |")
w("|---|---|---|---|---|---|---|---|---|---|---|---|---|---|---|")
for topic in ("defaults-savings", "llm-lit-search"):
    t = M["topics"][topic]
    for a in ARMS:
        s = t["arms"].get(a)
        if not s:
            continue
        j = s.get("judge") or {}
        w(f"| {topic} | {a} | {s['cut']} ({s['in_window']}+{s['outside_window']}) "
          f"| {frac(s['recall_10'])} | {frac(s['recall_25'])} | {s['foundational_slots']}/2 "
          f"| {s['contradicting_slots']} / {s['relation_contradicting']} | {s['review_slots']} "
          f"| {s['criterion_coverage']} | {s['frontier_tokens']} "
          f"| {s['frontier_tokens'] // 10} | ${s['cost_usd']:.4f} | {s['wall_s']:.0f} "
          f"| {j.get('precision_ge2_in_window', '—')} | {j.get('mean_score_in_window', '—')} |")

# --- 4. P(golden | score) ----------------------------------------------------
w("\n### P(golden | screen score), pooled over both topics\n")
w("| score | pool | golden | P(golden \\| score) |")
w("|---|---|---|---|")
for s in ("0", "1", "2", "3"):
    r = M["pooled"]["p_golden_given_score"][s]
    p = r["p"]
    w(f"| {s} | {r['pool']} | {r['golden']} | {'—' if p is None else f'{p:.5f}'} |")
tot = sum(v["pool"] for v in M["pooled"]["p_golden_given_score"].values())
totg = sum(v["golden"] for v in M["pooled"]["p_golden_given_score"].values())
w(f"| **all** | **{tot}** | **{totg}** | **{totg / tot:.5f}** |")

# --- 5. cost / time ----------------------------------------------------------
w("\n### Model spend and wall clock, per topic\n")
w("| stage | t1 calls | t1 cost | t1 wall s | t2 calls | t2 cost | t2 wall s |")
w("|---|---|---|---|---|---|---|")
t1, t2 = M["topics"]["defaults-savings"], M["topics"]["llm-lit-search"]


def stage_row(label, get):
    a, b = get(t1), get(t2)
    w(f"| {label} | {a[0]} | ${a[1]:.4f} | {a[2]:.1f} | {b[0]} | ${b[1]:.4f} | {b[2]:.1f} |")


stage_row("plan (1 stateless call)",
          lambda t: (1, t["plan"]["cost_usd"], t["plan"]["api_seconds_sum"]))
w("| screen · per-family breakdown | see `screen_wall_measured` in measurements.json | | | | | |")
stage_row("gap queries (1 stateless call)",
          lambda t: (1 if t["gap"]["ran"] else 0, t["gap"]["cost_usd"] or 0.0,
                     t["gap"]["api_seconds_sum"] or 0.0))
stage_row("rerank R15", lambda t: (
    2, t["arms"]["R15"]["cost_usd"], t["arms"]["R15"]["wall_s"]))
for t in (t1, t2):
    t["_screen_cost"] = sum(v["cost_usd"] for v in t["screen_stages"].values())
    t["_screen_wall"] = sum(v["stage_wall_s"] for v in t["screen_stages"].values())
    t["_screen_calls"] = sum(v["calls"] for v in t["screen_stages"].values())
stage_row("**screening total** (ledger: every attempt)", lambda t: (
    t["screen_spend_ledger"]["calls_including_failed_attempts"],
    t["screen_spend_ledger"]["cost_usd"], t["screen_wall_measured"]["total_s"]))
stage_row("**scan total (plan + screen + gap + R15 + CLI)**", lambda t: (
    t["screen_spend_ledger"]["calls_including_failed_attempts"] + 2
    + (1 if t["gap"]["ran"] else 0),
    t["screen_spend_ledger"]["cost_usd"] + t["plan"]["cost_usd"]
    + (t["gap"]["cost_usd"] or 0) + t["arms"]["R15"]["cost_usd"],
    t["screen_wall_measured"]["total_s"] + t["plan"]["api_seconds_sum"]
    + (t["gap"]["api_seconds_sum"] or 0) + t["arms"]["R15"]["wall_s"]
    + sum(t["cli_stage_seconds"].values())))

w("\n### CLI stage seconds (no model spend)\n")
w("| stage | t1 | t2 |")
w("|---|---|---|")
for k in sorted(set(t1["cli_stage_seconds"]) | set(t2["cli_stage_seconds"])):
    w(f"| {k} | {t1['cli_stage_seconds'].get(k, '—')} | {t2['cli_stage_seconds'].get(k, '—')} |")

(EXP / "tables.md").write_text("\n".join(OUT) + "\n")
print("\n".join(OUT))
