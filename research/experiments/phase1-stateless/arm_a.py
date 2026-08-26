"""ARM A — baseline bookkeeping. No model calls.

Extracts, from the immutable saved run and its session telemetry, everything the other arms
are measured against: per-candidate scores, the >=2 set, shortlist ids, the top-10 DOIs, and
the baseline's cost / time / token numbers with a stage decomposition.

The screening+rerank *share* of the baseline is derived two ways:
  1. stage clock  — from manifest.json timestamps, which bracket each CLI stage exactly;
     the gaps between one CLI stage finishing and the next starting are agent work.
  2. turn cost    — from the session transcript, attributing each assistant turn's billed
     tokens to the stage window its timestamp falls in.
Both are reported; the report uses (2) for cost and (1) for time.
"""

from __future__ import annotations

import json
import sys
from datetime import datetime, timezone
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parent))
from lib import common as C  # noqa: E402

TRANSCRIPT = Path.home() / (
    ".claude/projects/-Users-nabergoj-Projects-research-scan/"
    "ee2b298c-69cb-4f3e-9c4a-4cb2b7672f62.jsonl"
)


def _ts(s: str) -> float:
    return datetime.fromisoformat(s.replace("Z", "+00:00")).timestamp()


def stage_windows(manifest: dict) -> list[dict]:
    """Agent-work windows between CLI stages, from manifest timestamps."""
    t = manifest["timestamps"]
    return [
        {"stage": "plan", "start": _ts(t["init.finished_at"]), "end": _ts(t["retrieve.started_at"])},
        {"stage": "retrieve_cli", "start": _ts(t["retrieve.started_at"]),
         "end": _ts(t["retrieve.finished_at"])},
        {"stage": "screen_round1", "start": _ts(t["retrieve.finished_at"]),
         "end": _ts(t["expand.started_at"])},
        {"stage": "expand_cli", "start": _ts(t["expand.started_at"]),
         "end": _ts(t["expand.finished_at"])},
        {"stage": "screen_expansion", "start": _ts(t["expand.finished_at"]),
         "end": _ts(t["coverage.started_at"])},
        {"stage": "coverage_shortlist_cli", "start": _ts(t["coverage.started_at"]),
         "end": _ts(t["shortlist.finished_at"])},
        {"stage": "rerank", "start": _ts(t["shortlist.finished_at"]),
         "end": _ts(t["verify.started_at"])},
        {"stage": "verify_cli", "start": _ts(t["verify.started_at"]),
         "end": _ts(t["verify.finished_at"])},
        {"stage": "emit_and_report", "start": _ts(t["verify.finished_at"]),
         "end": _ts(t["emit.finished_at"])},
    ]


def attribute_turns(windows: list[dict]) -> dict:
    """Bill each assistant turn to the stage window containing its timestamp."""
    rows = [json.loads(line) for line in TRANSCRIPT.open()]
    # One API request appears as up to 3 assistant rows (one per content-block group), each
    # carrying the same usage block. Dedupe by requestId: doing so reproduces the session
    # json's totals exactly (output 146359, cache_read 13340895, thinking 77635).
    by_request: dict[str, dict] = {}
    for r in rows:
        if r.get("type") == "assistant" and r.get("message", {}).get("usage"):
            by_request.setdefault(r["requestId"], r)
    turns = list(by_request.values())
    per = {w["stage"]: {"turns": 0, "cost_usd": 0.0, "output": 0, "thinking": 0,
                        "cache_read": 0, "cache_write": 0, "input": 0} for w in windows}
    per["outside_stages"] = dict(per[windows[0]["stage"]])
    total = {"turns": 0, "cost_usd": 0.0}
    for turn in turns:
        ts = _ts(turn["timestamp"])
        usage = turn["message"]["usage"]
        cost = C.cost_of(usage)
        total["turns"] += 1
        total["cost_usd"] += cost
        bucket = "outside_stages"
        for w in windows:
            if w["start"] <= ts < w["end"]:
                bucket = w["stage"]
                break
        b = per[bucket]
        b["turns"] += 1
        b["cost_usd"] += cost
        b["input"] += usage.get("input_tokens", 0)
        b["output"] += usage.get("output_tokens", 0)
        b["thinking"] += C.thinking_tokens(usage)
        b["cache_read"] += usage.get("cache_read_input_tokens", 0)
        b["cache_write"] += usage.get("cache_creation_input_tokens", 0)
    for b in per.values():
        b["cost_usd"] = round(b["cost_usd"], 4)
    total["cost_usd"] = round(total["cost_usd"], 4)
    return {"per_stage": per, "transcript_total": total}


def main() -> None:
    manifest = json.loads((C.RUN / "manifest.json").read_text())
    session = json.loads(C.SESSION.read_text())
    screen = C.baseline_screen()
    shortlist = json.loads((C.RUN / "shortlist.json").read_text())
    ranked = C.baseline_ranked()

    windows = stage_windows(manifest)
    attribution = attribute_turns(windows)
    per = attribution["per_stage"]

    screen_stages = ["screen_round1", "screen_expansion"]
    rerank_stages = ["rerank"]
    screen_cost = sum(per[s]["cost_usd"] for s in screen_stages)
    rerank_cost = sum(per[s]["cost_usd"] for s in rerank_stages)
    screen_time = sum(w["end"] - w["start"] for w in windows if w["stage"] in screen_stages)
    rerank_time = sum(w["end"] - w["start"] for w in windows if w["stage"] in rerank_stages)

    ge2 = sorted(cid for cid, s in screen.items() if s["score"] >= 2)
    shortlist_ids = [r["cid"] for r in shortlist["in_window"]] + [
        r["cid"] for r in shortlist["outside_window"]
    ]
    contradicting = sorted(r["cid"] for r in ranked if r.get("relation") == "contradicting")

    out = {
        "model": session["modelUsage"] and next(iter(session["modelUsage"])),
        "tool_version": manifest["tool_version"],
        "whole_scan": {
            "cost_usd": session["total_cost_usd"],
            "num_turns": session["num_turns"],
            "wall_s_session": session["duration_ms"] / 1000,
            "wall_s_manifest": manifest["counts"]["wall_clock_s"],
            "input_tokens": session["usage"]["input_tokens"],
            "output_tokens": session["usage"]["output_tokens"],
            "thinking_tokens": session["usage"]["output_tokens_details"]["thinking_tokens"],
            "cache_read_tokens": session["usage"]["cache_read_input_tokens"],
            "cache_write_tokens": session["usage"]["cache_creation_input_tokens"],
        },
        "stage_windows": [
            {**w, "seconds": round(w["end"] - w["start"], 1)} for w in windows
        ],
        "stage_attribution": attribution,
        "share": {
            "screening_cost_usd": round(screen_cost, 4),
            "rerank_cost_usd": round(rerank_cost, 4),
            "screening_plus_rerank_cost_usd": round(screen_cost + rerank_cost, 4),
            "screening_seconds": round(screen_time, 1),
            "rerank_seconds": round(rerank_time, 1),
            "screening_plus_rerank_seconds": round(screen_time + rerank_time, 1),
            "share_of_total_cost": round(
                (screen_cost + rerank_cost) / session["total_cost_usd"], 4
            ),
        },
        "counts": {
            "candidates": len(screen),
            "ge2": len(ge2),
            "shortlist": len(shortlist_ids),
            "ranked": len(ranked),
            "emitted": len(C.baseline_top_cids()),
        },
        "score_histogram": {
            str(k): sum(1 for s in screen.values() if s["score"] == k) for k in range(4)
        },
        "scores": {cid: s["score"] for cid, s in screen.items()},
        "ge2_set": ge2,
        "shortlist_ids": shortlist_ids,
        "top10_cids": C.baseline_top_cids(),
        "top10_dois": C.baseline_top_dois(),
        "contradicting_cids": contradicting,
    }
    C.write_json(C.ARMS / "A" / "baseline.json", out)
    print(json.dumps({k: v for k, v in out.items()
                      if k in ("model", "whole_scan", "share", "counts", "score_histogram")},
                     indent=1))
    print("\nstage windows:")
    for w in out["stage_windows"]:
        print(f"  {w['stage']:24s} {w['seconds']:8.1f}s  "
              f"${per.get(w['stage'], {}).get('cost_usd', 0):6.3f}  "
              f"{per.get(w['stage'], {}).get('turns', 0):3d} turns")
    print(f"  {'outside_stages':24s} {'-':>8s}   ${per['outside_stages']['cost_usd']:6.3f}  "
          f"{per['outside_stages']['turns']:3d} turns")
    print(f"\ntranscript total ${attribution['transcript_total']['cost_usd']} "
          f"vs session ${session['total_cost_usd']:.4f}")


if __name__ == "__main__":
    main()
