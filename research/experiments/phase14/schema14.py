"""Phase-1.4 — the wire schema per cell, and the `priority_rank` contract.

The RankedEntry shape is the frozen Phase-1.1 one (`phase11-golden/rerank.py::entry_schema`),
imported and never re-implemented. The S cells add exactly one property.

**Why `priority_rank` is required on every row with `0` as its off value.** The shipped
`RankedEntry` model is `extra="forbid"` (`schema.py:47`), so `priority_rank` can never appear in
`ranked.json` — it is stripped before that file is written and recorded in a sidecar `priority.json`
instead, which is what keeps `verify` and `emit` running unchanged in every cell. On the wire it has
to be expressed in JSON Schema that structured outputs accepts, and a conditional requirement
("present iff `overall == 3`") is not expressible in the flat object schema this stage uses. A
required integer with `0` meaning "carries no rank" is the same contract in a shape the decoder can
enforce, and the driver checks the conditional half itself.

**Scope: one chunk.** `RERANK_CHUNK` is 13 and R40 is four chunks, so a rank is a strict order over
the 3s *in the batch the model was given*. That is the only coherent reading in a stateless pipeline
— the call cannot rank against records it never saw — and it is what the S rubric text says. How the
four per-chunk orders are merged into one selection order is `select14.MERGE`, pre-registered before
any call was issued.
"""

from __future__ import annotations

import importlib.util
from pathlib import Path

HERE = Path(__file__).resolve().parent
P11 = HERE.parent / "phase11-golden"

PRIORITY_KEY = "priority_rank"

#: Ranks 1..MAX_RANK, plus 0 for "not in the top tier". A chunk is at most `RERANK_CHUNK` records,
#: so 13 covers a chunk in which every record scored 3; the enum is sized from that, not guessed.
MAX_RANK = 13


def frozen_rerank():
    """Load `phase11-golden/rerank.py` for its schema builders. Read, never run."""
    spec = importlib.util.spec_from_file_location("p14_p11_rerank", P11 / "rerank.py")
    module = importlib.util.module_from_spec(spec)
    spec.loader.exec_module(module)
    return module


def entry_schema(criteria_ids: list[str], *, priority: bool) -> dict:
    """The frozen entry schema, plus `priority_rank` in the S cells and nothing else."""
    schema = frozen_rerank().entry_schema(criteria_ids)
    if not priority:
        return schema
    schema = {**schema, "properties": dict(schema["properties"]),
              "required": list(schema["required"])}
    schema["properties"][PRIORITY_KEY] = {
        "type": "integer",
        "enum": list(range(0, MAX_RANK + 1)),
        "description": (
            "Strict rank over the records in THIS batch scored `overall: 3` — 1 is best, then"
            " 2, 3, … with no gaps and no ties. Exactly 0 on every record scored 0, 1 or 2."
        ),
    }
    schema["required"].append(PRIORITY_KEY)
    return schema


def output_schema(criteria_ids: list[str], *, priority: bool) -> dict:
    return {
        "type": "object",
        "additionalProperties": False,
        "properties": {
            "ranked": {"type": "array",
                       "items": entry_schema(criteria_ids, priority=priority)}},
        "required": ["ranked"],
    }
