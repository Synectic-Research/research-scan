"""Phase-1.2A Part 2 — offline shortlist-policy sweep. No model calls, no repo changes.

Recomputes `shortlist.build` from recorded pre-shortlist inputs (`candidates.json` + `screen.json`)
under 3 orderings x 5 in-window caps, for both Phase-1.1 stateless runs and both recorded
conversational control runs. Everything here is deterministic; the only inputs are files.

Policies
    T0  score DESC, origin_count DESC, date DESC                      (shipped `shortlist.order_key`)
    T1  score DESC, criteria_supported DESC, origin_count DESC,
        best_retrieval_rank ASC, date DESC                            (date demoted to last)
    T2  T1 plus a stratified reserve: per sub-criterion, the top `THIN_CRITERION_HITS` T1-ordered
        candidates carrying that criterion are admitted before the T1 backfill fills the rest.

Caps apply to the in-window list only. `max_outside_window` is held at the shipped default (12) in
every configuration, because the out-of-window list is a separate cap and is not what the slice is
sweeping; cap=None is the diagnostic uncapped arm.
"""

from __future__ import annotations

import json
import sys
from dataclasses import dataclass
from pathlib import Path

REPO = Path(__file__).resolve().parents[3]
sys.path.insert(0, str(REPO / "src"))

from research_scan import evalrun  # noqa: E402
from research_scan.coverage import KEPT_SCORE  # noqa: E402
from research_scan.schema import THIN_CRITERION_HITS  # noqa: E402
from research_scan.select import CONTRADICTING_SLOTS, DEFAULT_FOUNDATIONAL  # noqa: E402
from research_scan.shortlist import DEFAULT_MAX_OUTSIDE_WINDOW  # noqa: E402

CAPS = [40, 60, 80, 120, None]
POLICIES = ["T0", "T1", "T2"]
NAMED = {  # papers the slice requires named in every configuration
    "llm-lit-search": {"10.48550/arXiv.2411.14199": "OpenScholar",
                       "10.48550/arXiv.2407.18940": "LitSearch",
                       "10.48550/arXiv.2501.10120": "PaSa",
                       "10.48550/arXiv.2402.01788": "LitLLM"},
    "defaults-savings": {},
}


# --------------------------------------------------------------------------- inputs

@dataclass
class Run:
    key: str
    label: str
    topic: str
    run_dir: Path
    criteria_from: Path | None = None   # attribution overlay when the run's own file has none
    ranked_from: Path | None = None     # for the retrospective contradicting count

    def load(self) -> dict:
        cands = json.loads((self.run_dir / "candidates.json").read_text())["candidates"]
        screen = json.loads((self.run_dir / "screen.json").read_text())["scores"]
        by_cid = {c["cid"]: c for c in cands}
        rows = {}
        for entry in screen:
            rows[entry["cid"]] = entry
        overlay = {}
        if self.criteria_from is not None:
            for entry in json.loads((self.criteria_from / "screen.json").read_text())["scores"]:
                overlay[entry["cid"]] = entry.get("criteria_hit") or []
        plan = json.loads((self.run_dir / "queries.json").read_text())
        criteria = [c["id"] for c in plan["sub_criteria"]]
        ranked = {}
        source = self.ranked_from or self.run_dir
        if (source / "ranked.json").is_file():
            for entry in json.loads((source / "ranked.json").read_text()):
                ranked[entry["cid"]] = entry.get("relation")
        return {"candidates": by_cid, "screen": rows, "overlay": overlay,
                "criteria": criteria, "ranked_relation": ranked}


RUNS = [
    Run("t1-stateless", "topic 1 defaults-savings — Phase-1.1 stateless", "defaults-savings",
        REPO / "research/experiments/phase11-golden/runs/p11-t1"),
    Run("t2-stateless", "topic 2 llm-lit-search — Phase-1.1 stateless", "llm-lit-search",
        REPO / "research/experiments/phase11-golden/runs/p11-t2"),
    Run("t1-control", "topic 1 defaults-savings — conversational control (s3-e2e)",
        "defaults-savings", REPO / "research/scans/2026-08-19-s3-e2e",
        criteria_from=None),
    Run("t2-control", "topic 2 llm-lit-search — conversational control (topic2b)",
        "llm-lit-search", REPO / "research/scans/2026-08-19-topic2b",
        criteria_from=None),
    Run("t1-control+attr", "topic 1 control, criteria overlay from p-standard-t1",
        "defaults-savings", REPO / "research/scans/2026-08-19-s3-e2e",
        criteria_from=REPO / "research/scans/2026-08-19-p-standard-t1"),
    Run("t2-control+attr", "topic 2 control, criteria overlay from p-standard-t2",
        "llm-lit-search", REPO / "research/scans/2026-08-19-topic2b",
        criteria_from=REPO / "research/scans/2026-08-19-p-standard-t2"),
]


# --------------------------------------------------------------------------- ordering

def features(cid: str, data: dict) -> dict:
    cand = data["candidates"][cid]
    entry = data["screen"][cid]
    hits = entry.get("criteria_hit") or data["overlay"].get(cid) or []
    ranks = [o["rank"] for o in cand.get("origins", [])]
    return {
        "cid": cid,
        "score": entry["score"],
        "criteria_hit": list(hits),
        "criteria_supported": len(hits),
        "origin_count": len(cand.get("origins", [])),
        "best_retrieval_rank": min(ranks) if ranks else 10**6,
        "date": cand.get("publication_date") or "0000-00-00",
        "outside_window": bool(cand.get("outside_window")),
        "title": cand.get("title", ""),
    }


def key_t0(f: dict) -> tuple:
    return (f["score"], f["origin_count"], f["date"])


def key_t1(f: dict) -> tuple:
    # Descending sort throughout; rank is inverted so that ASC-on-rank falls out of it.
    return (f["score"], f["criteria_supported"], f["origin_count"],
            -f["best_retrieval_rank"], f["date"])


def order(pool: list[dict], policy: str) -> list[dict]:
    """Stable, so ties keep `candidates.json` order — exactly what shipped `shortlist.build` does."""
    key = key_t0 if policy == "T0" else key_t1
    return sorted(pool, key=key, reverse=True)


def stratified(pool: list[dict], criteria: list[str], cap: int | None) -> tuple[list[dict], dict]:
    """T2: fill each criterion's reserve from the T1 order, then backfill by T1 (§ reserve rules).

    The reserve depth is `THIN_CRITERION_HITS` — the repo's own count for "this criterion has
    enough kept papers" (`coverage.py`). No new number is invented.
    """
    ranked = order(pool, "T1")
    reserved: list[dict] = []
    seen: set[str] = set()
    per_criterion: dict[str, int] = {}
    for criterion in criteria:
        taken = 0
        for f in ranked:
            if taken >= THIN_CRITERION_HITS:
                break
            if criterion not in f["criteria_hit"]:
                continue
            taken += 1
            if f["cid"] not in seen:
                seen.add(f["cid"])
                reserved.append(f)
        per_criterion[criterion] = taken
    if cap is not None and len(reserved) > cap:
        reserved = [f for f in ranked if f["cid"] in seen][:cap]
        seen = {f["cid"] for f in reserved}
    backfill = [f for f in ranked if f["cid"] not in seen]
    room = None if cap is None else max(0, cap - len(reserved))
    chosen = reserved + (backfill if room is None else backfill[:room])
    return order(chosen, "T1"), {"reserved": len(reserved), "per_criterion": per_criterion}


def build(pool: list[dict], criteria: list[str], policy: str, cap: int | None) -> tuple[list, list, dict]:
    inw = [f for f in pool if not f["outside_window"]]
    out = [f for f in pool if f["outside_window"]]
    meta: dict = {}
    if policy == "T2":
        kept_in, meta = stratified(inw, criteria, cap)
    else:
        ordered = order(inw, policy)
        kept_in = ordered if cap is None else ordered[:cap]
    kept_out = order(out, "T1" if policy != "T0" else "T0")[:DEFAULT_MAX_OUTSIDE_WINDOW]
    return kept_in, kept_out, meta


# --------------------------------------------------------------------------- golden matching

def golden_map(topic_name: str, candidates: dict) -> dict:
    topic = evalrun.load_topic(evalrun.find_topic(topic_name, REPO / "eval/golden"))
    from research_scan.schema import Candidate
    out = {}
    for paper in topic.expected:
        hit = None
        for cid, raw in candidates.items():
            if evalrun.match_kind(paper, Candidate.model_validate(raw)) is not None:
                hit = cid
                break
        out[paper.doi] = {"cid": hit, "title": paper.title or "",
                          "name": NAMED[topic_name].get(paper.doi, paper.title or paper.doi)}
    return out


# --------------------------------------------------------------------------- the sweep

def sweep_run(run: Run) -> dict:
    data = run.load()
    # candidates.json order, because shipped `shortlist.build` sorts that list and Python's sort
    # is stable: ties resolve to pool order, and a control arm has to reproduce that byte for byte.
    pool = [features(cid, data) for cid in data["candidates"]
            if data["screen"].get(cid, {}).get("score", 0) >= KEPT_SCORE]
    goldens = golden_map(run.topic, data["candidates"])

    ge2 = {doi: g for doi, g in goldens.items()
           if g["cid"] and data["screen"].get(g["cid"], {}).get("score", 0) >= KEPT_SCORE}

    configs = {}
    membership: dict[tuple[str, int | None], set[str]] = {}
    for policy in POLICIES:
        for cap in CAPS:
            kept_in, kept_out, meta = build(pool, data["criteria"], policy, cap)
            cids = {f["cid"] for f in kept_in} | {f["cid"] for f in kept_out}
            membership[(policy, cap)] = cids
            rank_of = {f["cid"]: i + 1 for i, f in enumerate(order(
                [f for f in pool if not f["outside_window"]], "T1" if policy != "T0" else "T0"))}
            per_crit = {c: sum(1 for f in kept_in if c in f["criteria_hit"])
                        for c in data["criteria"]}
            contradicting = sum(1 for cid in cids
                                if data["ranked_relation"].get(cid) == "contradicting")
            configs[f"{policy}@{cap or 'inf'}"] = {
                "policy": policy, "cap": cap,
                "shortlist_in": len(kept_in), "shortlist_out": len(kept_out),
                "shortlist_size": len(kept_in) + len(kept_out),
                "score3_retained": sum(1 for f in kept_in + kept_out if f["score"] == 3),
                "score2_retained": sum(1 for f in kept_in + kept_out if f["score"] == 2),
                "foundational_retained": len(kept_out),
                "criteria_covered": sum(1 for v in per_crit.values() if v),
                "criteria_total": len(data["criteria"]),
                "per_criterion": per_crit,
                "reserve": meta,
                "contradicting_retained_retrospective": contradicting,
                "goldens_surviving": sorted(g["name"] for doi, g in ge2.items()
                                            if g["cid"] in cids),
                "goldens_lost": sorted(g["name"] for doi, g in ge2.items()
                                       if g["cid"] not in cids),
                "named_fate": {g["name"]: {
                    "in_shortlist": g["cid"] in cids,
                    "policy_rank": rank_of.get(g["cid"]),
                } for doi, g in ge2.items() if g["name"] in NAMED[run.topic].values()},
            }

    # "lost to ordering" = excluded here but reachable at the SAME cap under another swept policy.
    for name, cfg in configs.items():
        cap = cfg["cap"]
        recoverable = set().union(*(membership[(p, cap)] for p in POLICIES))
        lost = [g for doi, g in ge2.items() if g["cid"] not in membership[(cfg["policy"], cap)]]
        cfg["goldens_lost_to_ordering"] = sorted(
            g["name"] for g in lost if g["cid"] in recoverable)
        cfg["goldens_lost_to_cap"] = sorted(
            g["name"] for g in lost if g["cid"] not in recoverable)

    return {
        "key": run.key, "label": run.label, "topic": run.topic,
        "run_dir": str(run.run_dir.relative_to(REPO)),
        "criteria_overlay": str(run.criteria_from.relative_to(REPO)) if run.criteria_from else None,
        "criteria_available": any(f["criteria_supported"] for f in pool),
        "pool_screened": len(data["screen"]),
        "pool_ge2": len(pool),
        "pool_ge2_in_window": sum(1 for f in pool if not f["outside_window"]),
        "pool_ge2_out_window": sum(1 for f in pool if f["outside_window"]),
        "goldens_expected": len(goldens),
        "goldens_retrieved": sum(1 for g in goldens.values() if g["cid"]),
        "goldens_ge2": len(ge2),
        "golden_detail": {g["name"]: {
            "cid": g["cid"],
            "screen_score": data["screen"].get(g["cid"], {}).get("score") if g["cid"] else None,
            "outside_window": bool(g["cid"] and data["candidates"][g["cid"]].get("outside_window")),
        } for g in goldens.values()},
        "slot_policy_note": {
            "foundational_slots": DEFAULT_FOUNDATIONAL,
            "contradicting_slots": CONTRADICTING_SLOTS,
            "reserve_depth_per_criterion": THIN_CRITERION_HITS,
            "max_outside_window": DEFAULT_MAX_OUTSIDE_WINDOW,
        },
        "configs": configs,
    }


def main() -> None:
    out = [sweep_run(run) for run in RUNS]
    path = Path(__file__).parent / "results" / "sweep.json"
    path.write_text(json.dumps(out, indent=1))
    for r in out:
        print(f"{r['key']:18s} pool>=2 {r['pool_ge2']:4d} "
              f"(in {r['pool_ge2_in_window']}, out {r['pool_ge2_out_window']})  "
              f"goldens retrieved {r['goldens_retrieved']}/{r['goldens_expected']} "
              f">=2 {r['goldens_ge2']}  criteria_available={r['criteria_available']}")
    print(f"\nwrote {path}")


if __name__ == "__main__":
    main()


def check_control_reproduces_shipped() -> list[str]:
    """T0@40 must reproduce each run's recorded `shortlist.json` exactly, or the sweep is fiction."""
    lines = []
    for run in RUNS:
        recorded = run.run_dir / "shortlist.json"
        if not recorded.is_file():
            lines.append(f"{run.key}: no recorded shortlist.json to check against")
            continue
        want = json.loads(recorded.read_text())
        data = run.load()
        pool = [features(cid, data) for cid in data["candidates"]
                if data["screen"].get(cid, {}).get("score", 0) >= KEPT_SCORE]
        kept_in, kept_out, _ = build(pool, data["criteria"], "T0", 40)
        got_in = [f["cid"] for f in kept_in]
        got_out = [f["cid"] for f in kept_out]
        ok_in = got_in == [c["cid"] for c in want["in_window"]]
        ok_out = got_out == [c["cid"] for c in want["outside_window"]][:len(got_out)]
        lines.append(f"{run.key}: in_window identical={ok_in}  outside_window prefix "
                     f"identical={ok_out} (recomputed {len(got_out)} vs recorded "
                     f"{len(want['outside_window'])})")
    return lines
