"""Independent judge over a scan's top 10 — eval/judge-prompt.md mechanics, run statelessly.

Invoked because every rerank sub-arm came in under 8/10 top-10 overlap with the baseline, which
the slice's disposition makes the trigger for judging both lists rather than trusting overlap.

Model: claude-fable-5. eval/judge.sh names Fable 5 as the judge slot, and canon §3 requires the
judge to be a different and stronger model than the reranker (Sonnet 5 here). Fable 5's thinking
is always on, so the `thinking` parameter is omitted entirely.

Reported metric: judged precision = share of in-window packets scoring >=2 (spec §14.6). The
`foundational` packets are scored on canonicity and reported separately, as the rubric requires.

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

JUDGE_MODEL = "claude-fable-5"
JUDGE_PRICE = {"input": 10.00e-6, "output": 50.00e-6,
               "cache_write": 12.50e-6, "cache_read": 1.00e-6}

# Structured outputs rejects minimum/maximum on integers, so the bounds become enums.
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


def judge_cost(usage) -> float:
    u = usage.model_dump()
    return (
        (u.get("input_tokens") or 0) * JUDGE_PRICE["input"]
        + (u.get("output_tokens") or 0) * JUDGE_PRICE["output"]
        + (u.get("cache_creation_input_tokens") or 0) * JUDGE_PRICE["cache_write"]
        + (u.get("cache_read_input_tokens") or 0) * JUDGE_PRICE["cache_read"]
    )


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
        model=JUDGE_MODEL,
        max_tokens=32000,
        # Fable 5: thinking is always on; passing `thinking` at all is rejected.
        output_config={"effort": "high",
                       "format": {"type": "json_schema", "schema": JUDGE_SCHEMA}},
        messages=[{"role": "user", "content": build_prompt(run)}],
    ) as stream:
        message = stream.get_final_message()
    dt = time.monotonic() - t0
    cost = judge_cost(message.usage)
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
        "judge_model": JUDGE_MODEL,
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
    C.write_json(C.ARMS / "judge" / f"{label}.json", out)
    print(f"{label:10s} precision(in-window >=2) = "
          f"{out['precision_ge2_in_window']} over {out['in_window_n']} packets  "
          f"mean {out['mean_score_in_window']}  foundational {out['foundational_scores']}  "
          f"${cost:.4f}  {dt:.0f}s")
    return out


def main() -> None:
    args = sys.argv[1:]
    if not args or len(args) % 2:
        sys.exit("usage: judge.py <label> <run-dir> [<label> <run-dir> ...]")
    client = anthropic.Anthropic(api_key=C.env_key(), timeout=1800.0, max_retries=2)
    results = []
    for label, run in zip(args[::2], args[1::2]):
        results.append(run_one(client, label, Path(run)))
    C.write_json(C.ARMS / "judge" / "summary.json",
                 {"judge_model": JUDGE_MODEL,
                  "runs": [{k: v for k, v in r.items() if k != "scores"} for r in results],
                  "cumulative_spend_usd": C.spent()})
    print(f"\ncumulative spend ${C.spent():.4f}")


if __name__ == "__main__":
    main()
