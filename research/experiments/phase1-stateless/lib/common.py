"""Shared plumbing for the Phase-1 stateless-screening replay experiment.

Read-only against the saved run directory. Every write goes under
research/experiments/phase1-stateless/. Nothing here is part of the shipped package.
"""

from __future__ import annotations

import json
import os
import re
import subprocess
import time
from dataclasses import dataclass, field, asdict
from pathlib import Path

REPO = Path(__file__).resolve().parents[4]
EXP = REPO / "research/experiments/phase1-stateless"
RUN = REPO / "research/scans/2026-08-26-claim-grounding-sonnet"
SESSION = REPO / "research/scans/claim-grounding-sonnet.session.json"
RUBRICS = REPO / "skills/research-scan/references"
ARMS = EXP / "arms"
LEDGER = EXP / "spend.json"

# Sonnet 5 list pricing, USD per token. Verified against the baseline session json:
# these four rates reproduce total_cost_usd = 6.4480633 exactly from its token counts.
PRICE = {
    "input": 2.00e-6,
    "output": 10.00e-6,
    "cache_write": 2.50e-6,
    "cache_read": 0.20e-6,
}

SPEND_CAP_USD = 12.00

MODEL = "claude-sonnet-5"  # the model the baseline session resolved to (modelUsage key)
EFFORT = "high"  # the effort every baseline assistant turn ran at (transcript `effort`)
MAX_TOKENS = 24000


# --------------------------------------------------------------------------- ledger


def _load_ledger() -> dict:
    if LEDGER.exists():
        return json.loads(LEDGER.read_text())
    return {"total_usd": 0.0, "calls": []}


def spent() -> float:
    return _load_ledger()["total_usd"]


def record(tag: str, usage: dict, cost: float, seconds: float) -> None:
    led = _load_ledger()
    led["total_usd"] = round(led["total_usd"] + cost, 6)
    led["calls"].append(
        {"tag": tag, "cost_usd": cost, "seconds": seconds, "usage": usage, "at": time.time()}
    )
    LEDGER.write_text(json.dumps(led, indent=1))


class CapExceeded(RuntimeError):
    pass


def check_cap(projected: float = 0.0) -> None:
    if spent() + projected >= SPEND_CAP_USD:
        raise CapExceeded(f"spend cap ${SPEND_CAP_USD} would be exceeded (spent ${spent():.2f})")


def cost_of(usage) -> float:
    """USD for one API response's usage block."""
    u = usage if isinstance(usage, dict) else usage.model_dump()
    return (
        (u.get("input_tokens") or 0) * PRICE["input"]
        + (u.get("output_tokens") or 0) * PRICE["output"]
        + (u.get("cache_creation_input_tokens") or 0) * PRICE["cache_write"]
        + (u.get("cache_read_input_tokens") or 0) * PRICE["cache_read"]
    )


def thinking_tokens(usage) -> int:
    u = usage if isinstance(usage, dict) else usage.model_dump()
    det = u.get("output_tokens_details") or {}
    return (det.get("thinking_tokens") if isinstance(det, dict) else None) or 0


# --------------------------------------------------------------------------- inputs


def brief_text() -> str:
    return (RUN / "brief.md").read_text()


def purpose_line() -> str:
    """The declared purpose, as the pipeline carries it into screening."""
    first = brief_text().splitlines()[0].strip()
    assert first.startswith("Purpose:"), first
    return first


def screen_rubric() -> str:
    return (RUBRICS / "screen-rubric.md").read_text()


def rerank_rubric() -> str:
    return (RUBRICS / "rerank-rubric.md").read_text()


def batches() -> dict[str, dict]:
    """Batch id -> payload, in the order the baseline saw them."""
    out = {}
    for p in sorted((RUN / "screen-batches").glob("*.json")):
        out[p.stem] = json.loads(p.read_text())
    return out


def candidates() -> list[dict]:
    return json.loads((RUN / "candidates.json").read_text())["candidates"]


def baseline_screen() -> dict[str, dict]:
    return {s["cid"]: s for s in json.loads((RUN / "screen.json").read_text())["scores"]}


def baseline_ranked() -> list[dict]:
    return json.loads((RUN / "ranked.json").read_text())


def baseline_top_dois() -> list[str]:
    ev = json.loads((RUN / "evidence.json").read_text())
    return [p["ids"]["doi"] for p in ev["packets"]]


def baseline_top_cids() -> list[str]:
    ev = json.loads((RUN / "evidence.json").read_text())
    return [p["cid"] for p in ev["packets"]]


# --------------------------------------------------------------------------- prompts

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

# Structured outputs rejects `minimum`/`maximum` on an integer ("For 'integer' type,
# properties maximum, minimum are not supported"), so the wire schema bounds `score` with an
# enum instead. SCREEN_ENTRY_SCHEMA above keeps the bounds and is what the model is shown.
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


def screen_prompt(batch: dict) -> str:
    """The whole context one stateless screening call gets. Nothing else."""
    return f"""You are screening one batch of retrieved papers for a research-scan run.

{purpose_line()}

# The brief

{brief_text()}

# The screening rubric

{screen_rubric()}

# The batch to score

Score every item in `items` below. The `sub_criteria` block in this batch is the one the
rubric's `criteria_hit` field refers to.

```json
{json.dumps(batch, ensure_ascii=False, indent=1)}
```

# Output

Return a JSON object `{{"scores": [...]}}` with exactly one entry per item in this batch,
each entry matching the `ScreenScore` contract:

```json
{json.dumps(SCREEN_ENTRY_SCHEMA, indent=1)}
```

Copy each `cid` verbatim from the batch. Score every item. Do not add items.
"""


# --------------------------------------------------------------------------- validation


CID_RE = re.compile(r"^[0-9a-f]{12}$")


def validate_batch_scores(batch: dict, payload: dict) -> list[dict]:
    """Shape-check one batch response against the ScreenScore contract. Raises on failure."""
    want = [i["cid"] for i in batch["items"]]
    known = {c["id"] for c in batch["sub_criteria"]}
    scores = payload.get("scores")
    if not isinstance(scores, list):
        raise ValueError("no scores array")
    got = [s.get("cid") for s in scores]
    if sorted(got) != sorted(want):
        missing = sorted(set(want) - set(got))
        extra = sorted(set(got) - set(want))
        raise ValueError(f"cid mismatch: missing={missing[:5]} extra={extra[:5]}")
    if len(set(got)) != len(got):
        raise ValueError("duplicate cids")
    out = []
    for s in scores:
        if not CID_RE.match(s["cid"]):
            raise ValueError(f"bad cid {s['cid']!r}")
        if not isinstance(s["score"], int) or not 0 <= s["score"] <= 3:
            raise ValueError(f"bad score for {s['cid']}")
        if not isinstance(s.get("reason"), str) or not s["reason"]:
            raise ValueError(f"missing reason for {s['cid']}")
        hits = s.get("criteria_hit") or []
        bad = [h for h in hits if h not in known]
        if bad:
            raise ValueError(f"unknown criteria ids {bad} for {s['cid']}")
        if s["score"] >= 2 and not hits:
            raise ValueError(f"score {s['score']} with empty criteria_hit for {s['cid']}")
        entry = {"cid": s["cid"], "score": s["score"], "reason": s["reason"]}
        entry["criteria_hit"] = hits if s["score"] >= 2 else []
        out.append(entry)
    return out


def schema_check(path: Path, model: str) -> tuple[bool, str]:
    """Validate a file on disk against `research-scan schema --name <model>`."""
    proc = subprocess.run(
        ["research-scan", "schema", "--name", model], capture_output=True, text=True
    )
    if proc.returncode != 0:
        return False, f"schema command failed: {proc.stderr[:200]}"
    schema = json.loads(proc.stdout)
    try:
        import jsonschema  # type: ignore
    except ImportError:
        return False, "jsonschema not installed"
    try:
        jsonschema.validate(json.loads(path.read_text()), schema)
    except jsonschema.ValidationError as exc:  # type: ignore[attr-defined]
        return False, f"{list(exc.absolute_path)}: {exc.message[:200]}"
    return True, "ok"


# --------------------------------------------------------------------------- results


@dataclass
class CallResult:
    tag: str
    ok: bool
    seconds: float
    input_tokens: int = 0
    output_tokens: int = 0
    thinking_tokens: int = 0
    cache_read: int = 0
    cache_write: int = 0
    cost_usd: float = 0.0
    attempts: int = 0
    error: str = ""
    scores: list = field(default_factory=list)


def summarise(results: list[CallResult]) -> dict:
    ok = [r for r in results if r.ok]
    return {
        "calls": len(results),
        "calls_ok": len(ok),
        "calls_failed": len(results) - len(ok),
        "failed_tags": [r.tag for r in results if not r.ok],
        "input_tokens": sum(r.input_tokens for r in results),
        "cache_read_tokens": sum(r.cache_read for r in results),
        "cache_write_tokens": sum(r.cache_write for r in results),
        "output_tokens": sum(r.output_tokens for r in results),
        "thinking_tokens": sum(r.thinking_tokens for r in results),
        "cost_usd": round(sum(r.cost_usd for r in results), 6),
        "api_seconds_sum": round(sum(r.seconds for r in results), 2),
        "retries": sum(max(0, r.attempts - 1) for r in results),
    }


def write_json(path: Path, obj) -> None:
    path.parent.mkdir(parents=True, exist_ok=True)
    path.write_text(json.dumps(obj, indent=1, ensure_ascii=False))


def dump_results(path: Path, results: list[CallResult]) -> None:
    write_json(path, [{k: v for k, v in asdict(r).items() if k != "scores"} for r in results])


def env_key() -> str:
    key = os.environ.get("ANTHROPIC_API_KEY")
    if not key:
        raise RuntimeError("ANTHROPIC_API_KEY not set")
    return key
