"""Phase-1.4 — the rerank call path: frozen mechanics, one rubric substitution, one schema field.

Everything that decides an answer other than the two factors under test is imported from the frozen
Phase-1.1 driver and never re-implemented: model, effort, thinking, `record_payload`, the user turn,
`cut`, `RERANK_CHUNK`, `RERANK_MAX_TOKENS`, the cost model. The sub-batch re-ask from Phase-1.2C is
active, via `contract14.rerank_chunk`.

`system_blocks` is the one function that had to be copied rather than imported, because
`rerank.py::system_blocks` reads the rubric from `skills/` through `C.rubric` and this slice must
substitute a variant without touching that file. `assert_control_prompt_identical()` checks the copy
against the original for the C0 cell, byte for byte, at the top of every run — so "C0 is the frozen
prompt" is a per-run assertion, not a claim.
"""

from __future__ import annotations

import importlib.util
import json
import sys
import time
from pathlib import Path

HERE = Path(__file__).resolve().parent
P11 = HERE.parent / "phase11-golden"
sys.path.insert(0, str(HERE))
sys.path.insert(0, str(P11))

import contract14  # noqa: E402
import schema14  # noqa: E402
import variants  # noqa: E402


def frozen_rerank():
    spec = importlib.util.spec_from_file_location("p14_rerank", P11 / "rerank.py")
    module = importlib.util.module_from_spec(spec)
    spec.loader.exec_module(module)
    return module


def system_text(run: Path, queries: dict, rubric_text: str, C) -> str:
    """`rerank.py::system_blocks`'s text, the rubric supplied instead of read from `skills/`."""
    sub = "\n".join(f"- {c['id']} — {c['name']}: {c['text']}" for c in queries["sub_criteria"])
    return f"""You are reranking shortlisted papers for a research-scan run.

{C.purpose_line(run)}

# The brief

{C.brief_text(run)}

# The plan's sub-criteria (score every one of these per paper)

{sub}

Brief summary the plan recorded:
{queries['brief_summary']}

# The rerank rubric

{rubric_text}

# Output

Return `{{"ranked": [...]}}` — one RankedEntry per record you were given, in the order given.
Copy each `cid` verbatim. Do not write `verification`; `verify` fills it.
"""


def system_blocks(run: Path, queries: dict, cell: str, C) -> list[dict]:
    return [
        {
            "type": "text",
            "text": system_text(run, queries, variants.variant(cell), C),
            "cache_control": {"type": "ephemeral"},
        }
    ]


def assert_control_prompt_identical(run: Path, queries: dict, C) -> None:
    """The C0 system prompt must equal the frozen driver's, byte for byte."""
    mine = system_blocks(run, queries, "C0", C)
    theirs = frozen_rerank().system_blocks(run, queries)
    if mine != theirs:
        a, b = mine[0]["text"], theirs[0]["text"]
        where = next((i for i, (x, y) in enumerate(zip(a, b, strict=False)) if x != y),
                     min(len(a), len(b)))
        raise AssertionError(
            f"C0 system prompt diverges from the frozen driver at char {where}: "
            f"{a[where:where + 120]!r} != {b[where:where + 120]!r}"
        )


def make_batch(tag: str, rows: list[dict], sub_criteria: list[dict]) -> dict:
    RR = frozen_rerank()
    return {
        "batch": tag,
        "items": [RR.record_payload(r) for r in rows],
        "sub_criteria": list(sub_criteria),
    }


def user_message(items: list[dict]) -> str:
    return (
        f"Rerank these {len(items)} shortlisted records. Score every sub-criterion for each.\n\n"
        "```json\n" + json.dumps(items, ensure_ascii=False, indent=1) + "\n```"
    )


def api_caller(client, C, system, criteria_ids, tag: str, results: list, *, priority: bool):
    """The `call(batch) -> payload` closure `rerank_chunk` drives. Phase-1.2C's, plus the schema
    switch. Decoding stops at `json.loads`; validation is reconciliation's job."""
    attempt = {"n": 0}
    out_schema = schema14.output_schema(criteria_ids, priority=priority)

    def call(batch: dict):
        attempt["n"] += 1
        sub_tag = f"{tag}/a{attempt['n']}" if attempt["n"] > 1 else tag
        C.check_cap(0.80)
        t0 = time.monotonic()
        with client.messages.stream(
            model=C.MODEL,
            max_tokens=C.RERANK_MAX_TOKENS,
            system=system,
            messages=[{"role": "user", "content": user_message(batch["items"])}],
            thinking={"type": "adaptive"},
            output_config={
                "effort": C.EFFORT,
                "format": {"type": "json_schema", "schema": out_schema},
            },
        ) as stream:
            message = stream.get_final_message()
        dt = time.monotonic() - t0
        C.record(sub_tag, message.usage.model_dump(), C.cost_of(message.usage), dt)
        results.append(C.result_from(sub_tag, message, dt, attempt["n"]))
        return json.loads(next(b.text for b in message.content if b.type == "text"))

    return call


def rerank_chunk(batch: dict, call, *, priority: bool):
    """Reconcile-and-re-ask, then enforce the rank contract over what the chunk actually banked."""
    outcome = contract14.rerank_chunk(batch, call, priority=priority)
    if priority and outcome.ok:
        contract14.check_batch(outcome.batch, outcome.scores)
    return outcome
