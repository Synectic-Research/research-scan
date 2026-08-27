"""The call path: one batch per call, no conversation, a bounded worker pool.

Arm C of the Phase-1 stateless replay, productionised. What was measured stays measured: one
batch per call, thinking off, the stable prefix cached once and read by every later call, and
the reconciling CID contract deciding what a response was worth
(`552f09c:research/experiments/phase1-stateless/measurements.json`).

The pool is threads rather than `asyncio`: the work is entirely I/O-bound, and the ported
`contract.screen_batch` — the piece with the retry rule in it — stays the synchronous function
Phase-1.2A measured and tested rather than being rewritten into a coroutine.
"""

from __future__ import annotations

import logging
import time
from concurrent.futures import ThreadPoolExecutor
from dataclasses import dataclass, field
from typing import Any

from stateless_driver import accept, contract, prompt

log = logging.getLogger("stateless_driver")

DEFAULT_MODEL = "claude-sonnet-5"
DEFAULT_EFFORT = "high"
DEFAULT_MAX_TOKENS = 24000
DEFAULT_MAX_CONCURRENCY = 8

#: Thinking is off, and that is a measured choice rather than a default: arm B (thinking on) cost
#: 1.7× arm C for the same 572 judgements, and screening is a bounded classification against a
#: rubric the prompt already carries.
THINKING = "disabled"


@dataclass
class Usage:
    input_tokens: int = 0
    output_tokens: int = 0
    cache_read: int = 0
    cache_write: int = 0
    calls: int = 0
    seconds: float = 0.0

    def add(self, other: Usage) -> None:
        self.input_tokens += other.input_tokens
        self.output_tokens += other.output_tokens
        self.cache_read += other.cache_read
        self.cache_write += other.cache_write
        self.calls += other.calls
        self.seconds += other.seconds

    def as_dict(self) -> dict[str, Any]:
        return {
            "calls": self.calls,
            "input_tokens": self.input_tokens,
            "output_tokens": self.output_tokens,
            "cache_read_tokens": self.cache_read,
            "cache_write_tokens": self.cache_write,
            "api_seconds_sum": round(self.seconds, 2),
        }


@dataclass
class Engine:
    """One configured engine. `call` is the only thing that touches the provider."""

    client: Any
    system: str
    model: str = DEFAULT_MODEL
    effort: str = DEFAULT_EFFORT
    max_tokens: int = DEFAULT_MAX_TOKENS
    prompt_cache: bool = True
    usage: Usage = field(default_factory=Usage)
    models_seen: set[str] = field(default_factory=set)
    calls: list[dict] = field(default_factory=list)

    def system_blocks(self) -> list[dict]:
        block: dict = {"type": "text", "text": self.system}
        if self.prompt_cache:
            block["cache_control"] = {"type": "ephemeral"}
        return [block]

    def request(self, batch: dict) -> dict:
        return {
            "model": self.model,
            "max_tokens": self.max_tokens,
            "system": self.system_blocks(),
            "messages": [{"role": "user", "content": prompt.user_text(batch)}],
            "thinking": {"type": THINKING},
            "output_config": {
                "effort": self.effort,
                "format": {"type": "json_schema", "schema": prompt.SCREEN_OUTPUT_SCHEMA},
            },
        }

    def call(self, batch: dict) -> Any:
        """One stateless screening call. Returns the decoded, shape-checked body — nothing more."""
        started = time.monotonic()
        with self.client.messages.stream(**self.request(batch)) as stream:
            message = stream.get_final_message()
        seconds = time.monotonic() - started

        text = next(block.text for block in message.content if block.type == "text")
        usage = message.usage
        one = Usage(
            input_tokens=usage.input_tokens or 0,
            output_tokens=usage.output_tokens or 0,
            cache_read=usage.cache_read_input_tokens or 0,
            cache_write=usage.cache_creation_input_tokens or 0,
            calls=1,
            seconds=seconds,
        )
        self.usage.add(one)
        self.models_seen.add(getattr(message, "model", "") or self.model)
        self.calls.append(
            {"batch": batch.get("batch", "?"), "seconds": round(seconds, 2), **one.as_dict()}
        )
        # Steps 1 and 2 of the acceptance chain start here; `screen_batch` runs the rest.
        return accept.check_wire_schema(accept.decode(text))


def screen(
    engine: Engine,
    batches: dict[str, dict],
    *,
    max_concurrency: int = DEFAULT_MAX_CONCURRENCY,
) -> list[contract.BatchOutcome]:
    """Every batch through the contract, in batch-id order, over a bounded pool of workers.

    The first batch runs alone: it writes the shared prefix into the prompt cache that the rest
    then read, and starting the pool cold makes every worker write its own copy of it.
    """
    ids = list(batches)
    if not ids:
        return []

    def one(bid: str) -> contract.BatchOutcome:
        outcome = contract.screen_batch(
            batches[bid], engine.call, validate_row=accept.screen_row
        )
        log.info(
            "batch %s: %s, %d accepted, %d attempt(s)%s",
            bid,
            "ok" if outcome.ok else "FAILED",
            len(outcome.scores),
            outcome.attempts,
            "" if outcome.ok else f", {len(outcome.missing)} unsatisfied: {outcome.reason}",
        )
        return outcome

    first = one(ids[0])
    if len(ids) == 1:
        return [first]
    with ThreadPoolExecutor(max_workers=max(1, max_concurrency)) as pool:
        rest = list(pool.map(one, ids[1:]))
    return [first, *rest]
