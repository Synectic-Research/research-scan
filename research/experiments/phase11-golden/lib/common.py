"""Shared plumbing for the Phase-1.1 golden-topic validation of the stateless architecture.

Frozen configuration, carried verbatim from Phase 1 arm C (screening) and R15 (rerank):
model `claude-sonnet-5`, effort `high`, screening thinking OFF, rerank thinking ON,
batch size 25 (the CLI's own), max_concurrency 8, 3 attempts per call.

Every write goes under research/experiments/phase11-golden/. Nothing here is part of the
shipped package; nothing under src/, skills/ or eval/ is touched.
"""

from __future__ import annotations

import json
import os
import re
import subprocess
import time
from dataclasses import asdict, dataclass, field
from pathlib import Path

REPO = Path(__file__).resolve().parents[4]
EXP = REPO / "research/experiments/phase11-golden"
RUNS = EXP / "runs"
SWEEP = EXP / "sweep"
RUBRICS = REPO / "skills/research-scan/references"
GOLDEN = REPO / "eval/golden"
LEDGER = EXP / "spend.json"

# Sonnet 5 list pricing, USD per token — the same four rates Phase 1 verified against the
# baseline session json (they reproduce its total_cost_usd exactly).
PRICE = {
    "input": 2.00e-6,
    "output": 10.00e-6,
    "cache_write": 2.50e-6,
    "cache_read": 0.20e-6,
}
# Fable 5 list pricing, for the judge slot only.
JUDGE_PRICE = {
    "input": 10.00e-6,
    "output": 50.00e-6,
    "cache_write": 12.50e-6,
    "cache_read": 1.00e-6,
}

SPEND_CAP_USD = 20.00

MODEL = "claude-sonnet-5"
EFFORT = "high"
JUDGE_MODEL = "claude-fable-5"
MAX_TOKENS = 24000
RERANK_MAX_TOKENS = 48000
MAX_CONCURRENCY = 8
MAX_ATTEMPTS = 3
RERANK_CHUNK = 13

# shortlist.py DEFAULT_MAX_{IN,OUTSIDE}_WINDOW — the ratio the stratified cut preserves.
IN_WINDOW_CAP, OUT_WINDOW_CAP = 40, 12

TOPICS = {
    "defaults-savings": {
        "slug": "p11-t1",
        # The anchor-free brief the recorded `standard` baseline ran on. Golden briefs never
        # carry anchors: naming the expected papers would pin them into retrieval.
        "brief": REPO / "research/scans/2026-08-19-p-standard-t1/brief.md",
        "domain": "behavioral",
        "window_from": "2023-08",
    },
    "llm-lit-search": {
        "slug": "p11-t2",
        "brief": REPO / "eval/briefs/llm-lit-search.md",
        "domain": "cs",
        "window_from": "2024-01",
    },
}

PROFILE = "standard"
TOP = 10
FOUNDATIONAL = 2


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


def cost_of(usage, price=PRICE) -> float:
    u = usage if isinstance(usage, dict) else usage.model_dump()
    return (
        (u.get("input_tokens") or 0) * price["input"]
        + (u.get("output_tokens") or 0) * price["output"]
        + (u.get("cache_creation_input_tokens") or 0) * price["cache_write"]
        + (u.get("cache_read_input_tokens") or 0) * price["cache_read"]
    )


def thinking_tokens(usage) -> int:
    u = usage if isinstance(usage, dict) else usage.model_dump()
    det = u.get("output_tokens_details") or {}
    return (det.get("thinking_tokens") if isinstance(det, dict) else None) or 0


# --------------------------------------------------------------------------- inputs


def rubric(name: str) -> str:
    return (RUBRICS / f"{name}.md").read_text()


def run_dir(topic: str) -> Path:
    return RUNS / TOPICS[topic]["slug"]


def brief_text(run: Path) -> str:
    return (run / "brief.md").read_text()


def purpose_line(run: Path) -> str:
    """The purpose the planning call inferred, as the pipeline carries it into screening."""
    return f"Purpose: {json.loads((run / 'purpose.json').read_text())['purpose']}."


def run_cli(args: list[str]) -> tuple[int, str]:
    proc = subprocess.run(args, capture_output=True, text=True, cwd=str(REPO))
    return proc.returncode, (proc.stdout or "") + (proc.stderr or "")


def schema_check(path: Path, model: str) -> tuple[bool, str]:
    code, out = run_cli(["research-scan", "schema", "--name", model])
    if code != 0:
        return False, f"schema command failed: {out[:200]}"
    schema = json.loads(out)
    import jsonschema

    try:
        jsonschema.validate(json.loads(path.read_text()), schema)
    except jsonschema.ValidationError as exc:
        return False, f"{list(exc.absolute_path)}: {exc.message[:200]}"
    return True, "ok"


# --------------------------------------------------------------------------- screening

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

# Structured outputs rejects minimum/maximum on an integer, so the wire schema uses an enum.
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


def screen_system(run: Path) -> str:
    """The stable prefix of every screening call — Phase 1 arm C's, verbatim in shape."""
    return f"""You are screening one batch of retrieved papers for a research-scan run.
Score every item in the batch you are given. You have no memory of other batches and need none.

{purpose_line(run)}

# The brief

{brief_text(run)}

# The screening rubric

{rubric("screen-rubric")}

# The contract for each entry you return

Return a JSON object `{{"scores": [...]}}` with exactly one entry per item in the batch,
each entry matching this `ScreenScore` schema:

```json
{json.dumps(SCREEN_ENTRY_SCHEMA, indent=1)}
```

Copy each `cid` verbatim from the batch. Score every item. Never invent or omit a cid.
`criteria_hit` lists ids from the batch's own `sub_criteria` block; it is required on a
score of 2 or 3 and must be empty on 0 and 1.
"""


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
        out.append(
            {
                "cid": s["cid"],
                "score": s["score"],
                "reason": s["reason"],
                "criteria_hit": hits if s["score"] >= 2 else [],
            }
        )
    return out


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
    schema_failure: bool = False
    attempt_errors: list = field(default_factory=list)
    scores: list = field(default_factory=list)


def result_from(tag, message, seconds, attempts, scores=None) -> CallResult:
    u = message.usage
    return CallResult(
        tag=tag,
        ok=True,
        seconds=seconds,
        input_tokens=u.input_tokens or 0,
        output_tokens=u.output_tokens or 0,
        thinking_tokens=thinking_tokens(u),
        cache_read=u.cache_read_input_tokens or 0,
        cache_write=u.cache_creation_input_tokens or 0,
        cost_usd=cost_of(u),
        attempts=attempts,
        scores=scores or [],
    )


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
        "schema_failures": sum(1 for r in results if r.schema_failure),
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
