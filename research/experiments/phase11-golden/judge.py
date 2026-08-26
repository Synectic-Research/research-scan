"""Independent judge over a run's top 10 — eval/judge-prompt.md mechanics, run statelessly.

Same as Phase 1: claude-fable-5, effort high, thinking always on (the parameter is omitted
entirely because Fable rejects it), the JudgeFile schema and packet projection from
eval/judge.sh. Reported metric: judged precision over the in-window packets; the foundational
packets are scored on canonicity and reported separately.

Usage:  python judge.py <label> <run-dir> [<label> <run-dir> ...]
"""

from __future__ import annotations

import json
import sys
import time
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parent))
from lib import common as C  # noqa: E402

import anthropic  # noqa: E402

JUDGE_SCHEMA = {
    "type": "object",
    "additionalProperties": False,
    "properties": {
        "run_dir": {"type": "string"},
        "judge_model": {"type": "string"},
        "scores": {
            "type": "array",
            "items": {
                "type": "object",
                "additionalProperties": False,
                "properties": {
                    "rank": {"type": "integer"},
                    "cid": {"type": "string"},
                    "score": {"type": "integer", "enum": [0, 1, 2, 3]},
                    "reason": {"type": "string"},
                },
                "required": ["rank", "cid", "score", "reason"],
            },
        },
    },
    "required": ["run_dir", "judge_model", "scores"],
}


def build_prompt(run: Path) -> str:
    prompt = (C.REPO / "eval/judge-prompt.md").read_text()
    brief = (run / "brief.md").read_text()
    sub = json.dumps(json.loads((run / "queries.json").read_text())["sub_criteria"])
    ev = json.loads((run / "evidence.json").read_text())
    packets = {
        "run_dir": ev["run"]["run_dir"],
        "packets": [
            {k: p.get(k) for k in ("rank", "cid", "selection_reason", "title", "year",
                                   "venue", "abstract", "key_finding", "why_it_matters")}
            for p in ev["packets"]
        ],
    }
    return (
        f"{prompt}\n\n## The brief\n\n{brief}\n\n## Sub-criteria\n\n{sub}\n\n"
        f"## The packets to score\n\n{json.dumps(packets, ensure_ascii=False, indent=1)}"
    )


def run_one(client, label: str, run: Path) -> dict:
    C.check_cap(0.80)
    t0 = time.monotonic()
    with client.messages.stream(
        model=C.JUDGE_MODEL,
        max_tokens=32000,
        output_config={"effort": "high",
                       "format": {"type": "json_schema", "schema": JUDGE_SCHEMA}},
        messages=[{"role": "user", "content": build_prompt(run)}],
    ) as stream:
        message = stream.get_final_message()
    dt = time.monotonic() - t0
    cost = C.cost_of(message.usage, C.JUDGE_PRICE)
    C.record(f"judge/{label}", message.usage.model_dump(), cost, dt)
    if message.stop_reason == "refusal":
        raise RuntimeError(f"judge refused: {message.stop_details}")
    payload = json.loads(next(b.text for b in message.content if b.type == "text"))

    ev = json.loads((run / "evidence.json").read_text())
    reason_by_cid = {p["cid"]: p.get("selection_reason") for p in ev["packets"]}
    in_window = [s for s in payload["scores"] if reason_by_cid.get(s["cid"]) != "foundational"]
    foundational = [s for s in payload["scores"] if reason_by_cid.get(s["cid"]) == "foundational"]
    prec = (sum(1 for s in in_window if s["score"] >= 2) / len(in_window)) if in_window else None

    out = {
        "label": label,
        "run_dir": str(run),
        "judge_model": C.JUDGE_MODEL,
        "seconds": round(dt, 1),
        "cost_usd": round(cost, 4),
        "input_tokens": message.usage.input_tokens or 0,
        "output_tokens": message.usage.output_tokens or 0,
        "thinking_tokens": C.thinking_tokens(message.usage),
        "n_scored": len(payload["scores"]),
        "in_window_n": len(in_window),
        "foundational_n": len(foundational),
        "precision_ge2_in_window": round(prec, 4) if prec is not None else None,
        "mean_score_in_window": round(
            sum(s["score"] for s in in_window) / len(in_window), 3) if in_window else None,
        "foundational_scores": [s["score"] for s in foundational],
        "scores": payload["scores"],
    }
    C.write_json(C.EXP / "judge" / f"{label}.json", out)
    print(f"{label:28s} precision(in-window >=2) = {out['precision_ge2_in_window']} over "
          f"{out['in_window_n']}  mean {out['mean_score_in_window']}  "
          f"foundational {out['foundational_scores']}  ${cost:.4f}  {dt:.0f}s")
    return out


def main() -> None:
    args = sys.argv[1:]
    if not args or len(args) % 2:
        sys.exit("usage: judge.py <label> <run-dir> [<label> <run-dir> ...]")
    client = anthropic.Anthropic(api_key=C.env_key(), timeout=1800.0, max_retries=2)
    results = []
    for label, run in zip(args[::2], args[1::2]):
        path = C.EXP / "judge" / f"{label}.json"
        if path.exists():
            print(f"{label}: already judged, skipping")
            results.append(json.loads(path.read_text()))
            continue
        results.append(run_one(client, label, Path(run)))
    C.write_json(C.EXP / "judge" / "summary.json",
                 {"judge_model": C.JUDGE_MODEL,
                  "runs": [{k: v for k, v in r.items() if k != "scores"} for r in results],
                  "cumulative_spend_usd": C.spent()})
    print(f"\ncumulative spend ${C.spent():.4f}")


if __name__ == "__main__":
    main()
