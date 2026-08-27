"""The one prompt this engine sends, and the wire schema it demands back.

The stable half — purpose line, brief, rubric, output contract — is byte-identical across every
call in a run and goes in `system` behind one cache breakpoint. The batch is the only thing that
varies, which is what makes the calls stateless: no conversation, no run state, no tools.

Ported from the Phase-1.1/1.2 arm-C driver
(`552f09c462dce07a7c20fa3f30e85c3264f42346:research/experiments/phase1-stateless/screen_arms.py`,
`.../lib/common.py`). The templates are module constants so `provenance.py` can
hash exactly what was sent — a prompt that changes without its hash changing is a measurement
that cannot be reproduced.
"""

from __future__ import annotations

import json

#: What the model is shown. Bounds live here; the wire schema below drops the ones structured
#: outputs rejects ("For 'integer' type, properties maximum, minimum are not supported").
SCREEN_ENTRY_SCHEMA = {
    "type": "object",
    "additionalProperties": False,
    "properties": {
        "cid": {"type": "string", "description": "12 lowercase hex chars, copied from the batch."},
        "score": {"type": "integer", "minimum": 0, "maximum": 3},
        "reason": {"type": "string", "description": "At most 20 words."},
        "criteria_hit": {
            "type": "array",
            "items": {"type": "string"},
            "description": "Sub-criterion ids satisfied. Required on 2 and 3; empty on 0 and 1.",
        },
    },
    "required": ["cid", "score", "reason", "criteria_hit"],
}

_WIRE_ENTRY = {
    "type": "object",
    "additionalProperties": False,
    "properties": {
        "cid": {"type": "string", "description": "12 lowercase hex chars, copied from the batch."},
        "score": {"type": "integer", "enum": [0, 1, 2, 3]},
        "reason": {"type": "string", "description": "At most 20 words."},
        "criteria_hit": {"type": "array", "items": {"type": "string"}},
    },
    "required": ["cid", "score", "reason", "criteria_hit"],
}

SCREEN_OUTPUT_SCHEMA = {
    "type": "object",
    "additionalProperties": False,
    "properties": {"scores": {"type": "array", "items": _WIRE_ENTRY}},
    "required": ["scores"],
}

#: The wire shape's own version. It travels in the provenance record, so a schema change is
#: visible in the artefacts of every run made after it.
SCHEMA_VERSION = "screen-scores/1"

SYSTEM_TEMPLATE = """You are screening one batch of retrieved papers for a research-scan run.
Score every item in the batch you are given. You have no memory of other batches and need none.

{purpose}

# The brief

{brief}

# The screening rubric

{rubric}

# The contract for each entry you return

Return a JSON object `{{"scores": [...]}}` with exactly one entry per item in the batch,
each entry matching this `ScreenScore` schema:

```json
{schema}
```

Copy each `cid` verbatim from the batch. Score every item. Never invent or omit a cid.
`criteria_hit` lists ids from the batch's own `sub_criteria` block; it is required on a
score of 2 or 3 and must be empty on 0 and 1.
"""

USER_TEMPLATE = "Score every item in this batch.\n\n```json\n{batch}\n```"


def system_text(purpose: str, brief: str, rubric: str) -> str:
    return SYSTEM_TEMPLATE.format(
        purpose=purpose,
        brief=brief,
        rubric=rubric,
        schema=json.dumps(SCREEN_ENTRY_SCHEMA, indent=1),
    )


def user_text(batch: dict) -> str:
    return USER_TEMPLATE.format(batch=json.dumps(batch, ensure_ascii=False, indent=1))


def purpose_line(brief: str) -> str:
    """The declared purpose, as the pipeline carries it into screening."""
    first = brief.splitlines()[0].strip() if brief.strip() else ""
    if not first.startswith("Purpose:"):
        raise ValueError("brief.md must open with a `Purpose:` line")
    return first
