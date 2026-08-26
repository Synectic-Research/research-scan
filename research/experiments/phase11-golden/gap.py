"""ONE stateless call writing the gap round's `round2` queries (SKILL.md §4, plan rubric).

Runs only when `coverage.json.gap_round.should_run` is true — the profile's own trigger, not a
forced round. High reasoning ON, like planning: this is a planning judgement, not screening.

Usage:  python gap.py <topic>
"""

from __future__ import annotations

import json
import sys
import time
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parent))
from lib import common as C  # noqa: E402

import anthropic  # noqa: E402

GAP_SCHEMA = {
    "type": "object",
    "additionalProperties": False,
    "properties": {
        "round2": {
            "type": "array",
            "items": {
                "type": "object",
                "additionalProperties": False,
                "properties": {
                    "id": {"type": "string"},
                    "type": {
                        "type": "string",
                        "enum": ["gap", "direct", "terminology", "mechanism", "method",
                                 "adjacent", "contradictory", "review", "emerging"],
                    },
                    "text": {"type": "string"},
                    "mode": {"type": "string", "enum": ["semantic", "keyword"]},
                    "target_criterion": {"type": ["string", "null"]},
                },
                "required": ["id", "type", "text", "mode", "target_criterion"],
            },
        }
    },
    "required": ["round2"],
}


def prompt(run: Path) -> str:
    coverage = json.loads((run / "coverage.json").read_text())
    plan = json.loads((run / "queries.json").read_text())
    return f"""You are writing the gap round of a research-scan run. `coverage` has reported
which sub-criteria came back thin; you write `round2` and nothing else.

{C.purpose_line(run)}

# The brief

{(run / "brief.md").read_text()}

# The plan you already wrote

```json
{json.dumps(plan, ensure_ascii=False, indent=1)}
```

# What coverage reports

```json
{json.dumps(coverage, ensure_ascii=False, indent=1)}
```

# The plan rubric

{C.rubric("plan-rubric")}

# What to write

For every sub-criterion marked `thin` — and, when none is marked thin, for the single criterion
with the fewest `hits` — write **1-2** queries `{{"id": "G1…", "type": "gap",
"target_criterion": "<criterion id>", "text": "2-4 core terms", "mode": "semantic"}}`, aimed at
the vocabulary that criterion's literature actually uses, not a rewording of the query that
already failed. Then add **at most 2** reformulations (`"id": "R1…"`, keeping the original's
`type`, `target_criterion` null unless one criterion is the point) of the lowest-yield query in
`coverage.queries`.

Ids must not collide with the plan's existing query ids. `type: "gap"` requires a real
`target_criterion`. Eight `round2` queries maximum. If nothing is thin and nothing is worth
reformulating, return an empty `round2`.
"""


def main() -> None:
    topic = sys.argv[1]
    run = C.run_dir(topic)
    coverage = json.loads((run / "coverage.json").read_text())
    gap = coverage.get("gap_round") or {}
    if not gap.get("should_run"):
        print(f"{topic}: gap round not triggered — {gap.get('reasons')}")
        C.write_json(C.EXP / "stages" / f"gap-{topic}.json",
                     {"topic": topic, "ran": False, "reasons": gap.get("reasons"),
                      "cost_usd": 0.0, "calls": 0})
        return

    client = anthropic.Anthropic(api_key=C.env_key(), timeout=1800.0, max_retries=2)
    plan = json.loads((run / "queries.json").read_text())
    known_ids = {q["id"] for q in plan["queries"]}
    criteria = {c["id"] for c in plan["sub_criteria"]}

    attempts, last_err = 0, ""
    while attempts < C.MAX_ATTEMPTS:
        attempts += 1
        C.check_cap(0.30)
        t0 = time.monotonic()
        try:
            with client.messages.stream(
                model=C.MODEL,
                max_tokens=C.MAX_TOKENS,
                messages=[{"role": "user", "content": prompt(run)}],
                thinking={"type": "adaptive"},
                output_config={"effort": C.EFFORT,
                               "format": {"type": "json_schema", "schema": GAP_SCHEMA}},
            ) as stream:
                message = stream.get_final_message()
            dt = time.monotonic() - t0
            C.record(f"gap/{topic}", message.usage.model_dump(), C.cost_of(message.usage), dt)
            payload = json.loads(next(b.text for b in message.content if b.type == "text"))
            qs = payload["round2"]
            if len(qs) > 8:
                raise ValueError(f"{len(qs)} round2 queries, max 8")
            for q in qs:
                if q["id"] in known_ids:
                    raise ValueError(f"round2 id {q['id']} collides with an existing query id")
                if q["type"] == "gap" and q.get("target_criterion") not in criteria:
                    raise ValueError(f"gap query {q['id']} has no real target_criterion")
                if len(q["text"].split()) > 30:
                    raise ValueError(f"{q['id']} text over 30 words")
            break
        except C.CapExceeded:
            raise
        except Exception as exc:  # noqa: BLE001
            last_err = f"{type(exc).__name__}: {exc}"
            print(f"  gap/{topic} attempt {attempts} failed: {last_err[:200]}")
            if attempts < C.MAX_ATTEMPTS:
                time.sleep(2 ** attempts)
    else:
        sys.exit(f"gap-query call failed for {topic}: {last_err}")

    plan["round2"] = qs
    (run / "queries.json").write_text(json.dumps(plan, indent=1, ensure_ascii=False))
    ok, msg = C.schema_check(run / "queries.json", "QueryPlan")

    res = C.result_from(f"gap/{topic}", message, dt, attempts)
    summary = C.summarise([res])
    summary.update({
        "topic": topic, "ran": True, "n_round2": len(qs),
        "round2": qs, "queries_schema_valid": ok, "queries_schema_msg": msg,
        "trigger_reasons": gap.get("reasons"), "cumulative_spend_usd": C.spent(),
    })
    C.write_json(C.EXP / "stages" / f"gap-{topic}.json", summary)
    print(json.dumps({k: v for k, v in summary.items() if k != "failed_tags"}, indent=1))


if __name__ == "__main__":
    main()
