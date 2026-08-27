"""Phase-1.4 — the pre-registered outcome rule, as code.

**Written and committed before the first replicate was run.** The slice states the rule in words:

    Adopt exactly the factor(s) that BEAT C0 in their own factor: materially better mean golden
    recall, no previously-stable golden (f_g >= 4/5 in C0) dropping below 3/5, no special-slot
    regression, non-inferior on both topics; for S additionally a substantially less saturated top
    tier. If no factor clears C0 -> Outcome C.

Three of those words are qualitative and have to be numbers before the data exists, or the ruling
becomes a negotiation with the result. These are those numbers, fixed in advance:

  "materially better"      mean recall@10 at least +1.0 golden above C0 on at least one topic.
                           One whole golden paper, because recall@10 is integer-valued per run and
                           anything smaller is a re-shuffle inside the same set of finds.
  "non-inferior on both"   mean recall@10 >= C0's on BOTH topics. No tolerance band: a cell that
                           loses ground on either topic has not cleared the control.
  "substantially less      mean top-tier population share at least 25% BELOW C0's, relatively, on
   saturated"              BOTH topics. The defect being tested is that the `overall == 3` band is
                           far larger than the slots it feeds (Phase-1.2C: 419/840 rows, and 23-27
                           of 40 in-window rows on llm-lit-search/R40), so the gate is a real
                           contraction of that band, not a nudge.

  "previously-stable"      f_g >= 0.8 in C0 (4/5 when C0 has five replicates), and the clause is
                           breached if that golden's f_g in the candidate cell falls below 0.6.
                           Expressed as fractions so the clause reads identically at n=3 and n=5.
  "special-slot            the mean per-run fill of each guaranteed reason — review, contradicting,
   regression"             foundational — must be >= C0's, and the contradiction and foundational
                           inclusion frequencies must be >= C0's. Any shortfall is a regression.

Contrasts. The slice says "BEAT C0 in their own factor", so each factor is ruled on its own simple
contrast against the fresh control — S vs C0, C vs C0 — and that is the binding test. The factorial
main effect (the average of S-C0 and SC-C, and of C-C0 and SC-S) is computed and reported alongside
as supporting evidence, and an interaction that contradicts the simple contrast is called out rather
than averaged away.
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

MATERIAL_RECALL_GAIN = 1.0        # goldens, mean recall@10, on at least one topic
NON_INFERIORITY = 0.0             # goldens, mean recall@10, on every topic
SATURATION_RELATIVE_CUT = 0.25    # required relative reduction in top-tier share, both topics
STABLE_IN_C0 = 0.8                # f_g at or above this in C0 makes a golden "previously stable"
STABLE_FLOOR = 0.6                # and it may not fall below this in the candidate cell

TOPICS = tuple(analyze14.SLUGS)
SLOT_KEYS = ("review_slots", "contradicting_slots", "foundational_slots")


def _mean(values: list[float]) -> float:
    return round(statistics.mean(values), 4) if values else 0.0


def _frac(text: str) -> float:
    num, den = text.split("/")
    return int(num) / int(den) if int(den) else 0.0


def compare(cells: dict, cell_name: str, control: str = "C0") -> dict:
    """One candidate cell against the control, on every clause, topic by topic."""
    clauses: dict[str, dict] = {}
    per_topic = {}
    for topic in TOPICS:
        cand = cells.get(f"{topic}/{cell_name}")
        ctrl = cells.get(f"{topic}/{control}")
        if not cand or not ctrl:
            per_topic[topic] = {"missing": True}
            continue

        stable_breaches = []
        for doi, text in ctrl["f_g"].items():
            if _frac(text) >= STABLE_IN_C0 and _frac(cand["f_g"].get(doi, "0/1")) < STABLE_FLOOR:
                stable_breaches.append(
                    {"golden": ctrl["labels"][doi], "c0": text, cell_name: cand["f_g"].get(doi)})

        slot_regressions = []
        for key in SLOT_KEYS:
            a, b = _mean(cand[key]), _mean(ctrl[key])
            if a < b:
                slot_regressions.append({"slot": key, "c0": b, cell_name: a})
        for key in ("contradiction_inclusion_freq", "foundational_inclusion_freq"):
            if cand[key] < ctrl[key]:
                slot_regressions.append({"slot": key, "c0": ctrl[key], cell_name: cand[key]})

        d_recall = round(cand["recall10_mean"] - ctrl["recall10_mean"], 3)
        sat_cut = (
            round(1 - cand["top_tier_share_mean"] / ctrl["top_tier_share_mean"], 4)
            if ctrl["top_tier_share_mean"] else 0.0
        )
        per_topic[topic] = {
            "n": cand["n"], "n_control": ctrl["n"],
            "recall10_mean": cand["recall10_mean"], "c0_recall10_mean": ctrl["recall10_mean"],
            "delta_recall10_mean": d_recall,
            "recall10_min": cand["recall10_min"], "c0_recall10_min": ctrl["recall10_min"],
            "top_tier_share": cand["top_tier_share_mean"],
            "c0_top_tier_share": ctrl["top_tier_share_mean"],
            "saturation_relative_cut": sat_cut,
            "stable_golden_breaches": stable_breaches,
            "slot_regressions": slot_regressions,
            "jaccard_mean": cand["jaccard_mean"], "c0_jaccard_mean": ctrl["jaccard_mean"],
        }

    live = {t: v for t, v in per_topic.items() if not v.get("missing")}
    deltas = [v["delta_recall10_mean"] for v in live.values()]
    clauses["materially_better"] = {
        "pass": bool(deltas) and max(deltas) >= MATERIAL_RECALL_GAIN,
        "detail": {t: v["delta_recall10_mean"] for t, v in live.items()},
        "threshold": f">= +{MATERIAL_RECALL_GAIN} on at least one topic",
    }
    clauses["non_inferior_both_topics"] = {
        "pass": bool(live) and len(live) == len(TOPICS)
        and all(d >= NON_INFERIORITY for d in deltas),
        "detail": {t: v["delta_recall10_mean"] for t, v in live.items()},
        "threshold": f">= {NON_INFERIORITY} on every topic",
    }
    clauses["no_stable_golden_lost"] = {
        "pass": all(not v["stable_golden_breaches"] for v in live.values()),
        "detail": {t: v["stable_golden_breaches"] for t, v in live.items()},
        "threshold": f"f_g >= {STABLE_IN_C0} in C0 may not fall below {STABLE_FLOOR}",
    }
    clauses["no_special_slot_regression"] = {
        "pass": all(not v["slot_regressions"] for v in live.values()),
        "detail": {t: v["slot_regressions"] for t, v in live.items()},
        "threshold": "review / contradicting / foundational fills and inclusion freqs >= C0",
    }
    if variants.uses_priority_rank(cell_name):
        cuts = [v["saturation_relative_cut"] for v in live.values()]
        clauses["substantially_less_saturated"] = {
            "pass": bool(cuts) and len(cuts) == len(TOPICS)
            and all(c >= SATURATION_RELATIVE_CUT for c in cuts),
            "detail": {t: v["saturation_relative_cut"] for t, v in live.items()},
            "threshold": f">= {SATURATION_RELATIVE_CUT:.0%} relative reduction on every topic",
        }

    return {
        "cell": cell_name, "control": control,
        "clauses": clauses,
        "adopt": all(c["pass"] for c in clauses.values()),
        "per_topic": per_topic,
    }


def main_effects(cells: dict) -> dict:
    """The factorial main effect of each factor: the mean of its two simple contrasts."""
    out = {}
    for factor, pairs in (("S", (("S", "C0"), ("SC", "C"))), ("C", (("C", "C0"), ("SC", "S")))):
        per_topic = {}
        for topic in TOPICS:
            contrasts = []
            for hi, lo in pairs:
                a, b = cells.get(f"{topic}/{hi}"), cells.get(f"{topic}/{lo}")
                if a and b:
                    contrasts.append(round(a["recall10_mean"] - b["recall10_mean"], 3))
            if contrasts:
                per_topic[topic] = {
                    "contrasts": {f"{hi}-{lo}": c
                                  for (hi, lo), c in zip(pairs, contrasts, strict=False)},
                    "main_effect": round(statistics.mean(contrasts), 3),
                    "interaction": round(contrasts[0] - contrasts[1], 3) if len(contrasts) == 2
                    else None,
                }
        out[factor] = per_topic
    return out


def rule(cells: dict) -> dict:
    verdicts = {name: compare(cells, name) for name in ("S", "C", "SC")}
    adopted = [name for name in ("S", "C") if verdicts[name]["adopt"]]
    if adopted == ["S", "C"] and verdicts["SC"]["adopt"]:
        outcome = "ADOPT BOTH (SC)"
    elif adopted:
        outcome = f"ADOPT {' + '.join(adopted)}"
    else:
        outcome = "OUTCOME C — freeze the current reranker"
    return {
        "thresholds": {
            "material_recall_gain": MATERIAL_RECALL_GAIN,
            "non_inferiority": NON_INFERIORITY,
            "saturation_relative_cut": SATURATION_RELATIVE_CUT,
            "stable_in_c0": STABLE_IN_C0, "stable_floor": STABLE_FLOOR,
        },
        "verdicts": verdicts,
        "main_effects": main_effects(cells),
        "adopted_factors": adopted,
        "outcome": outcome,
    }


def main() -> None:
    cells = json.loads((HERE / "results" / "cells.json").read_text())
    out = rule(cells)
    (HERE / "results" / "ruling.json").write_text(json.dumps(out, indent=1, default=str))
    for name, v in out["verdicts"].items():
        marks = " ".join(f"{k}={'PASS' if c['pass'] else 'FAIL'}" for k, c in v["clauses"].items())
        print(f"{name:3s} adopt={v['adopt']}  {marks}")
    print("main effects:", json.dumps(out["main_effects"], indent=1))
    print("OUTCOME:", out["outcome"])


if __name__ == "__main__":
    main()
