"""ONE stateless planning call per topic — writes `queries.json` from the plan rubric.

High reasoning ON (thinking adaptive, effort high), per the frozen configuration. Cost is
recorded under its own `plan/<topic>` tag so it can be reported separately.

Usage:  python plan.py <topic>
"""

from __future__ import annotations

import json
import sys
import time
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parent))
from lib import common as C  # noqa: E402

import anthropic  # noqa: E402

QUERY_TYPES = [
    "direct", "terminology", "mechanism", "method",
    "adjacent", "contradictory", "review", "emerging",
]

PLAN_SCHEMA = {
    "type": "object",
    "additionalProperties": False,
    "properties": {
        "purpose": {
            "type": "string",
            "enum": ["build", "research", "orient"],
            "description": "The purpose you inferred from the brief.",
        },
        "brief_summary": {"type": "string"},
        "domain": {"type": "string", "enum": ["behavioral", "cs", "biomed", "general"]},
        "window": {
            "type": "object",
            "additionalProperties": False,
            "properties": {
                "from": {"type": "string", "description": "YYYY-MM"},
                "to": {"type": ["string", "null"]},
            },
            "required": ["from", "to"],
        },
        "sub_criteria": {
            "type": "array",
            "items": {
                "type": "object",
                "additionalProperties": False,
                "properties": {
                    "id": {"type": "string"},
                    "name": {"type": "string"},
                    "text": {"type": "string"},
                },
                "required": ["id", "name", "text"],
            },
        },
        "must_not": {"type": "array", "items": {"type": "string"}},
        "queries": {
            "type": "array",
            "items": {
                "type": "object",
                "additionalProperties": False,
                "properties": {
                    "id": {"type": "string"},
                    "type": {"type": "string", "enum": QUERY_TYPES},
                    "text": {"type": "string"},
                    "mode": {"type": "string", "enum": ["semantic", "keyword"]},
                },
                "required": ["id", "type", "text", "mode"],
            },
        },
    },
    "required": [
        "purpose", "brief_summary", "domain", "window", "sub_criteria", "must_not", "queries",
    ],
}


def prompt(run: Path, info: dict) -> str:
    return f"""You are the planning step of a research-scan run. You write the query plan and
nothing else; the CLI runs it faithfully and will not second-guess a bad query.

# The brief

{(run / "brief.md").read_text()}

# The run the CLI created

```json
{json.dumps(info, indent=1)}
```

# The plan rubric

{C.rubric("plan-rubric")}

# Output

First decide the purpose. The brief carries no `Purpose:` line, so infer one — **build** (the
answer moves a design or plan decision), **research** (the answer changes what we believe, what
we would test, or how we would measure it), or **orient** (what a newcomer to the topic must
know, recent first) — return it in `purpose`, and state it in the first sentence of
`brief_summary`, e.g. "Purpose: research."

Then return the plan: `brief_summary`, `domain`, `window`, 3-6 `sub_criteria`, `must_not`, and
6-8 `queries` with all four mandatory types (`direct`, `terminology`, `contradictory`, `review`)
present. `anchors` are deliberately not requested: this brief names no papers. `round2` is
written later, after `coverage`.
"""


def validate(plan: dict) -> None:
    qs = plan["queries"]
    if not 6 <= len(qs) <= 8:
        raise ValueError(f"{len(qs)} queries, need 6-8")
    if len({q["id"] for q in qs}) != len(qs):
        raise ValueError("duplicate query ids")
    types = {q["type"] for q in qs}
    missing = {"direct", "terminology", "contradictory", "review"} - types
    if missing:
        raise ValueError(f"missing mandatory query types: {sorted(missing)}")
    for q in qs:
        if len(q["text"].split()) > 30:
            raise ValueError(f"{q['id']} text over 30 words")
    if not 3 <= len(plan["sub_criteria"]) <= 6:
        raise ValueError(f"{len(plan['sub_criteria'])} sub_criteria, need 3-6")
    if len({c["id"] for c in plan["sub_criteria"]}) != len(plan["sub_criteria"]):
        raise ValueError("duplicate sub_criterion ids")


def main() -> None:
    topic = sys.argv[1]
    run = C.run_dir(topic)
    info = json.loads((run / "manifest.json").read_text())["run"]

    client = anthropic.Anthropic(api_key=C.env_key(), timeout=1800.0, max_retries=2)
    attempts, last_err = 0, ""
    while attempts < C.MAX_ATTEMPTS:
        attempts += 1
        C.check_cap(0.30)
        t0 = time.monotonic()
        try:
            with client.messages.stream(
                model=C.MODEL,
                max_tokens=C.MAX_TOKENS,
                messages=[{"role": "user", "content": prompt(run, info)}],
                thinking={"type": "adaptive"},  # high reasoning ON for planning
                output_config={
                    "effort": C.EFFORT,
                    "format": {"type": "json_schema", "schema": PLAN_SCHEMA},
                },
            ) as stream:
                message = stream.get_final_message()
            dt = time.monotonic() - t0
            C.record(f"plan/{topic}", message.usage.model_dump(), C.cost_of(message.usage), dt)
            payload = json.loads(next(b.text for b in message.content if b.type == "text"))
            validate(payload)
            break
        except C.CapExceeded:
            raise
        except Exception as exc:  # noqa: BLE001
            last_err = f"{type(exc).__name__}: {exc}"
            print(f"  plan/{topic} attempt {attempts} failed: {last_err[:200]}")
            if attempts < C.MAX_ATTEMPTS:
                time.sleep(2 ** attempts)
    else:
        sys.exit(f"planning failed for {topic}: {last_err}")

    purpose = payload.pop("purpose")
    C.write_json(run / "purpose.json", {"purpose": purpose})
    (run / "queries.json").write_text(json.dumps(payload, indent=1, ensure_ascii=False))
    ok, msg = C.schema_check(run / "queries.json", "QueryPlan")

    res = C.result_from(f"plan/{topic}", message, dt, attempts)
    summary = C.summarise([res])
    summary.update({
        "topic": topic, "purpose": purpose, "queries_schema_valid": ok, "queries_schema_msg": msg,
        "n_queries": len(payload["queries"]), "n_sub_criteria": len(payload["sub_criteria"]),
        "domain": payload["domain"], "window": payload["window"],
        "cumulative_spend_usd": C.spent(),
    })
    C.write_json(C.EXP / "stages" / f"plan-{topic}.json", summary)
    print(json.dumps(summary, indent=1))


if __name__ == "__main__":
    main()
