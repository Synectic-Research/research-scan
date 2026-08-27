"""The acceptance chain. Nothing a model returns becomes pipeline state without passing it.

    engine response
      → schema validation      the decoded body has the shape the wire schema demanded
      → CID reconciliation     rows are matched against the cids the batch asked for
      → value/range validation each row's fields are inside the contract
      → provenance attachment  the surviving rows are bound to the record of what produced them
      → accepted cognition artifact

Each step can only ever *reject*. None of them repairs a row, invents a judgement, renames a cid,
or fills a missing field from context, because a repaired judgement is indistinguishable from an
invented one and this engine has no standing to make either. What survives the chain is exactly
what the model said about papers the batch actually contained.
"""

from __future__ import annotations

import json
import re
from dataclasses import dataclass
from typing import Any

from stateless_driver import contract

CID_RE = re.compile(r"^[0-9a-f]{12}$")

#: `ScreenScore.reason` is bounded at 20 words by the package's own contract (`schema.py`), and a
#: file that breaks it is rejected at `research-scan shortlist` with exit 2. The driver enforces
#: it here so an over-long reason costs its own row rather than the whole run's screen.json.
MAX_REASON_WORDS = 20


class SchemaError(ValueError):
    """The body did not decode, or did not have the shape the schema demanded."""


def decode(text: str) -> Any:
    try:
        return json.loads(text)
    except json.JSONDecodeError as exc:
        raise SchemaError(f"response is not JSON: {exc}") from None


def check_wire_schema(payload: Any) -> Any:
    """Step 1. Shape only — never values, which belong to step 3, and never membership, step 2."""
    if not isinstance(payload, dict):
        raise SchemaError(f"response is {type(payload).__name__}, not an object")
    rows = payload.get("scores")
    if not isinstance(rows, list):
        raise SchemaError("response has no `scores` array")
    for row in rows:
        if not isinstance(row, dict):
            raise SchemaError(f"a row is {type(row).__name__}, not an object")
        missing = [field for field in ("cid", "score", "reason") if field not in row]
        if missing:
            raise SchemaError(f"a row is missing {missing}")
    return payload


def screen_row(row: dict, known_criteria: set[str]) -> tuple[dict | None, str]:
    """Step 3, per row: the ported field contract, plus the two bounds the package will enforce."""
    cid = row.get("cid")
    if not isinstance(cid, str) or not CID_RE.match(cid):
        return None, f"cid {cid!r} is not 12 lowercase hex characters"
    reason = row.get("reason")
    if isinstance(reason, str) and len(reason.split()) > MAX_REASON_WORDS:
        return None, f"reason is {len(reason.split())} words, over the {MAX_REASON_WORDS} allowed"
    return contract._validate_row(row, known_criteria)


@dataclass
class Accepted:
    """The artifact, bound to the record of what produced it. Written together, always."""

    provenance: dict[str, Any]
    scores: list[dict]
    batches: dict[str, dict]

    def as_dict(self) -> dict[str, Any]:
        return {"provenance": self.provenance, "batches": self.batches, "scores": self.scores}


def attach(provenance: dict[str, Any], outcomes: list[contract.BatchOutcome]) -> Accepted:
    """Step 4. Every accepted row, and what each batch cost to get, under one provenance record.

    The rows go into `screen.json` as the pipeline's own contract defines them — provenance rides
    beside the artifact rather than inside its rows, because `ScreenScore` forbids unknown keys
    and a contract with a hole in it for an engine's metadata is not a contract.
    """
    return Accepted(
        provenance=provenance,
        scores=[row for outcome in outcomes for row in outcome.scores],
        batches={
            outcome.batch: {
                "ok": outcome.ok,
                "attempts": outcome.attempts,
                "accepted": len(outcome.scores),
                "missing": outcome.missing,
                "reason": outcome.reason,
                "provenance": outcome.provenance,
            }
            for outcome in outcomes
        },
    )
