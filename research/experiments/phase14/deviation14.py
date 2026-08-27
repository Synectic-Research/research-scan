"""Phase-1.4 — the one protocol deviation, and a bound on what it could have changed.

`llm-lit-search/S` has four replicates, not five. `rep4` was attempted twice and died both times
inside `contract14.check_batch` on chunk 3 with `PriorityContractViolation` — the slice's own
pre-registered exit-2 class:

    a1  1 overall==3 row(s) carry no rank: ['5197bbb391c8']; ranks not unique: [4]
    a2  ranks not unique: [3]

The violation is raised *after* reconciliation has accepted the chunk, by design, so the
reconcile-and-re-ask path cannot recover it and the replicate has no emitted set. It is therefore
missing-not-at-random: the cell that failed to produce it is the cell whose contract failed.

Counting it as evidence rather than as absence is the honest treatment, and it cuts two ways:

  * it is a robustness fact about FACTOR S, recorded below and in the report — 1 of 20 S-cell
    replicates could not satisfy the `priority_rank` contract the factor itself introduces, and it
    is the only contract failure in all 40 attempted runs of the slice;
  * it must not be allowed to become a loophole. Dropping a failed replicate flatters the cell it
    was dropped from, so this module asks the adversarial question directly: is there ANY value the
    missing replicate could have taken that flips a clause in S's favour?

The bound is exact, not probabilistic. `recall@10` is integer-valued and can never exceed the
cell's reachable ceiling — how many goldens the frozen R40 frontier delivers to the reranker at
all — so the best case for S is a fifth replicate at the ceiling, with every golden emitted.
"""

from __future__ import annotations

import json
import statistics
import sys
from pathlib import Path

HERE = Path(__file__).resolve().parent
sys.path.insert(0, str(HERE))

import rule14  # noqa: E402

TOPIC = "llm-lit-search"
CELL = "S"


def bound(cells: dict) -> dict:
    cand, ctrl = cells[f"{TOPIC}/{CELL}"], cells[f"{TOPIC}/C0"]
    ceiling = cand["reachable_ceiling"]
    observed = cand["recall10_runs"]
    n_target = ctrl["n"]

    # The best case: the missing replicate scores the ceiling and emits every reachable golden.
    best_runs = observed + [ceiling]
    best_mean = round(statistics.mean(best_runs), 3)
    best_delta = round(best_mean - ctrl["recall10_mean"], 3)

    # What each clause would need from the missing replicate, solved for x.
    need_noninf = rule14.NON_INFERIORITY + ctrl["recall10_mean"]
    x_noninf = round(need_noninf * n_target - sum(observed), 3)
    need_material = rule14.MATERIAL_RECALL_GAIN + ctrl["recall10_mean"]
    x_material = round(need_material * n_target - sum(observed), 3)

    # The stable-golden clause: PaSa is 4/5 in C0 and 0/4 in S. Best case adds one hit.
    stable = {}
    for doi, text in ctrl["f_g"].items():
        if rule14._frac(text) >= rule14.STABLE_IN_C0:
            hits = cand["f_g_counts"].get(doi, 0)
            best_fg = (hits + 1) / n_target
            stable[ctrl["labels"][doi]] = {
                "c0": text,
                "s_observed": cand["f_g"].get(doi),
                "s_best_case": f"{hits + 1}/{n_target}",
                "best_case_fraction": round(best_fg, 3),
                "floor": rule14.STABLE_FLOOR,
                "breach_stands": best_fg < rule14.STABLE_FLOOR,
            }

    # Saturation is a both-topics clause and defaults-savings is complete at n=5, so it is already
    # decided there regardless of anything this topic does.
    d_cand, d_ctrl = cells[f"defaults-savings/{CELL}"], cells["defaults-savings/C0"]
    d_cut = round(1 - d_cand["top_tier_share_mean"] / d_ctrl["top_tier_share_mean"], 4)

    return {
        "deviation": {
            "cell": f"{TOPIC}/{CELL}",
            "missing_replicate": 4,
            "n_recorded": cand["n"],
            "n_target": n_target,
            "class": "contract14.PriorityContractViolation",
            "exit_code": 2,
            "attempts": 2,
            "chunk": "c3",
            "violations": [
                "1 overall==3 row(s) carry no rank: ['5197bbb391c8']; ranks not unique: [4]",
                "ranks not unique: [3]",
            ],
            "log": "logs/p11-t2-S-rep4.log",
            "recoverable_by_reask": False,
            "only_contract_failure_in_slice": True,
            "s_cell_replicates_attempted": 10,
        },
        "bound": {
            "reachable_ceiling": ceiling,
            "observed_runs": observed,
            "best_case_runs": best_runs,
            "best_case_mean": best_mean,
            "c0_mean": ctrl["recall10_mean"],
            "best_case_delta_vs_c0": best_delta,
            "non_inferiority": {
                "needs_missing_replicate_to_score": x_noninf,
                "ceiling": ceiling,
                "attainable": x_noninf <= ceiling,
            },
            "materially_better": {
                "needs_missing_replicate_to_score": x_material,
                "ceiling": ceiling,
                "attainable": x_material <= ceiling,
                "defaults_savings_delta": round(
                    d_cand["recall10_mean"] - d_ctrl["recall10_mean"], 3),
            },
            "no_stable_golden_lost": stable,
            "substantially_less_saturated": {
                "defaults_savings_cut": d_cut,
                "required": rule14.SATURATION_RELATIVE_CUT,
                "topic_complete_at_n5": True,
                "already_failed_independently_of_this_topic": d_cut < rule14.SATURATION_RELATIVE_CUT,
            },
        },
    }


def _flippable(b: dict) -> list[str]:
    """Which clauses the missing replicate could still flip in the cell's favour, at its best case.

    `no_stable_golden_lost` fails if ANY stable golden breaches, so it flips only when NO breach
    survives the best case — not when some individual breach could be lifted.
    """
    out = [k for k in ("non_inferiority", "materially_better") if b[k]["attainable"]]
    if not any(v["breach_stands"] for v in b["no_stable_golden_lost"].values()):
        out.append("no_stable_golden_lost")
    if not b["substantially_less_saturated"]["already_failed_independently_of_this_topic"]:
        out.append("substantially_less_saturated")
    return out


def main() -> None:
    cells = json.loads((HERE / "results" / "cells.json").read_text())
    out = bound(cells)
    b = out["bound"]
    flippable = _flippable(b)
    out["clauses_the_deviation_could_flip"] = flippable
    out["verdict_robust_to_deviation"] = not flippable

    (HERE / "results" / "deviation_s_r4.json").write_text(json.dumps(out, indent=1, default=str))

    print(f"deviation: {out['deviation']['cell']} rep4 — {out['deviation']['class']}, "
          f"{out['deviation']['attempts']} attempts, both on {out['deviation']['chunk']}")
    print(f"  n={b['observed_runs']} (n={out['deviation']['n_recorded']} of "
          f"{out['deviation']['n_target']}), ceiling={b['reachable_ceiling']}")
    print(f"  best case: runs {b['best_case_runs']} mean={b['best_case_mean']} "
          f"vs C0 {b['c0_mean']} -> delta {b['best_case_delta_vs_c0']:+}")
    print(f"  non-inferiority needs rep4 >= {b['non_inferiority']['needs_missing_replicate_to_score']}"
          f" (ceiling {b['reachable_ceiling']}) -> attainable="
          f"{b['non_inferiority']['attainable']}")
    print(f"  materially-better needs rep4 >= "
          f"{b['materially_better']['needs_missing_replicate_to_score']}"
          f" (ceiling {b['reachable_ceiling']}) -> attainable="
          f"{b['materially_better']['attainable']}")
    for lab, v in b["no_stable_golden_lost"].items():
        print(f"  stable golden {lab}: C0 {v['c0']}, S {v['s_observed']}, best case "
              f"{v['s_best_case']} vs floor {v['floor']} -> breach stands={v['breach_stands']}")
    print(f"  saturation already failed on defaults-savings at n=5: "
          f"cut {b['substantially_less_saturated']['defaults_savings_cut']} < "
          f"{b['substantially_less_saturated']['required']}")
    print(f"\nclauses the deviation could flip: {flippable or 'none'}")
    print(f"VERDICT ROBUST TO DEVIATION: {out['verdict_robust_to_deviation']}")


if __name__ == "__main__":
    main()
