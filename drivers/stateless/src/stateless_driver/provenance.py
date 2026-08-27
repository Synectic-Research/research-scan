"""The record every driver run writes: what judged, under what, at what settings, and what it cost.

A cognition artifact with no provenance is a model's opinion of unknown origin. This record is
what makes one reproducible enough to argue with — and it is deliberately a description of
*configuration and outcome*, never of *access*: no key, no token, no endpoint, no account or
organisation identifier reaches it. What it carries is the run's identity and clock, the model,
the effort and thinking configuration, the sampling parameters, the hashes of the texts that
steer the judgement, the wire schema's version, the concurrency and batch size, where execution
happened, how many attempts it took, what came out, and what it cost.

Every key in `EngineProvenance` is present in every serialised record, including the ones a run
cannot fill. A field that is absent is ambiguous — nobody can tell "not measured" from "forgotten"
six months later — so unfilled fields serialise as `null` and say so.
"""

from __future__ import annotations

import hashlib
import re
from dataclasses import asdict, dataclass
from datetime import UTC, datetime
from typing import Any

from stateless_driver import ENGINE_ID, ENGINE_PROTOCOL_VERSION, __version__, prompt

#: The shape of this record. Bumped when a field is added, removed or re-meant — a reader that
#: knows this number knows which keys to expect and what they mean.
PROVENANCE_SCHEMA_VERSION = "1.0.0"

#: Where the judgement physically ran. `provider-api` means: off this machine, in a provider's
#: service, under that provider's own model revisions. It is a property of this run, not a
#: permanent property of the architecture — an engine running on this machine records its own.
EXECUTION_CLASS = "provider-api"

#: The unit every `usage` count is in. Provider-reported, never re-derived here.
TOKEN_UNIT = "tokens"

#: The unit `cost` is in when a run has one. Stated even when the amount is null, so the number
#: is never read in the wrong currency.
CURRENCY = "USD"


def digest(text: str) -> str:
    """`sha256:<hex>` — long enough to be an identity, prefixed so it is never mistaken for one."""
    return "sha256:" + hashlib.sha256(text.encode("utf-8")).hexdigest()


def utc_now() -> str:
    """ISO-8601 in UTC, with the offset written out: `2026-08-27T20:41:03.123456+00:00`."""
    return datetime.now(UTC).isoformat()


@dataclass
class Sampling:
    """Everything that moves the distribution the judgement is drawn from."""

    max_tokens: int
    temperature: float | None = None
    top_p: float | None = None


@dataclass
class Pricing:
    """USD per million tokens. Supplied by the caller, never shipped: a stale price table baked
    into a provenance record is worse than an absent one, because it reads as measured."""

    input_per_mtok: float
    output_per_mtok: float
    cache_read_per_mtok: float = 0.0
    cache_write_per_mtok: float = 0.0

    def usd(self, usage: dict[str, Any]) -> float:
        """Cost of one usage total. The total already spans initial calls and their retries."""
        return round(
            usage.get("input_tokens", 0) / 1e6 * self.input_per_mtok
            + usage.get("output_tokens", 0) / 1e6 * self.output_per_mtok
            + usage.get("cache_read_tokens", 0) / 1e6 * self.cache_read_per_mtok
            + usage.get("cache_write_tokens", 0) / 1e6 * self.cache_write_per_mtok,
            6,
        )


@dataclass
class EngineProvenance:
    """One run of one engine. Serialised beside the artifact it produced."""

    # --- identity and clock
    provenance_schema_version: str
    run_id: str | None
    started_at: str
    completed_at: str | None

    # --- what judged
    engine_protocol_version: str
    engine_id: str
    engine_version: str
    model_id: str
    model_revision_or_hash: list[str] | None

    # --- under what
    rubric_hash: str
    prompt_template_hash: str
    brief_hash: str
    response_schema_version: str
    response_schema_hash: str
    effort_or_thinking_configuration: dict[str, Any]
    sampling_parameters: dict[str, Any]

    # --- how it ran
    batch_size: int | None
    max_concurrency: int
    execution_class: str
    prompt_cache: bool

    # --- what came of it
    attempt_count: int | None = None
    retry_summary: dict[str, Any] | None = None
    input_record_count: int | None = None
    accepted_record_count: int | None = None
    unresolved_cids: list[str] | None = None
    usage: dict[str, Any] | None = None
    token_unit: str = TOKEN_UNIT
    cost: float | None = None
    currency: str = CURRENCY
    completion_status: str = "started"

    def as_dict(self) -> dict[str, Any]:
        return asdict(self)


def build(
    *,
    model_id: str,
    rubric: str,
    brief: str,
    effort: str,
    thinking: str,
    sampling: Sampling,
    max_concurrency: int,
    prompt_cache: bool,
    run_id: str | None = None,
    batch_size: int | None = None,
    started_at: str | None = None,
) -> EngineProvenance:
    """The record for a run that is about to start. The outcome fields are filled by `finalize`."""
    return EngineProvenance(
        provenance_schema_version=PROVENANCE_SCHEMA_VERSION,
        run_id=run_id,
        started_at=started_at or utc_now(),
        completed_at=None,
        engine_protocol_version=ENGINE_PROTOCOL_VERSION,
        engine_id=ENGINE_ID,
        engine_version=__version__,
        model_id=model_id,
        model_revision_or_hash=None,
        rubric_hash=digest(rubric),
        # The template, not the filled prompt: one hash for the whole run, and it changes when the
        # instructions change rather than when the batch does. `brief_hash` covers the run's input.
        prompt_template_hash=digest(prompt.SYSTEM_TEMPLATE + prompt.USER_TEMPLATE),
        brief_hash=digest(brief),
        response_schema_version=prompt.SCHEMA_VERSION,
        response_schema_hash=digest(repr(prompt.SCREEN_OUTPUT_SCHEMA)),
        effort_or_thinking_configuration={"effort": effort, "thinking": thinking},
        sampling_parameters=asdict(sampling),
        batch_size=batch_size,
        max_concurrency=max_concurrency,
        execution_class=EXECUTION_CLASS,
        prompt_cache=prompt_cache,
    )


def finalize(
    record: EngineProvenance,
    outcomes: list[Any],
    *,
    usage: dict[str, Any],
    input_record_count: int,
    model_revision_or_hash: list[str] | None = None,
    pricing: Pricing | None = None,
    completed_at: str | None = None,
) -> EngineProvenance:
    """Close the record against what the run actually did.

    `usage` is the engine's running total, which every call adds to — the initial call for a batch
    and each of its retries alike — so the tokens and the cost derived from them cover the retries
    rather than the first attempt only. `attempt_count` is the same total counted per batch.
    """
    attempts = sum(outcome.attempts for outcome in outcomes)
    unresolved = sorted({cid for outcome in outcomes for cid in outcome.missing})
    accepted = sum(len(outcome.scores) for outcome in outcomes)

    record.completed_at = completed_at or utc_now()
    record.model_revision_or_hash = model_revision_or_hash
    record.attempt_count = attempts
    record.retry_summary = {
        "batches": len(outcomes),
        "batches_first_try": sum(1 for outcome in outcomes if outcome.attempts == 1),
        "batches_retried": sum(1 for outcome in outcomes if outcome.attempts > 1),
        "batches_failed": sorted(outcome.batch for outcome in outcomes if not outcome.ok),
        "attempts_total": attempts,
        "max_attempts_on_one_batch": max((o.attempts for o in outcomes), default=0),
    }
    record.input_record_count = input_record_count
    record.accepted_record_count = accepted
    record.unresolved_cids = unresolved
    record.usage = dict(usage)
    record.cost = pricing.usd(usage) if pricing else None
    record.completion_status = "complete" if not unresolved else "incomplete"
    return record


#: Word-parts a provenance record's field names must never contain, asserted in the driver's own
#: tests. The list is the point of the module: a record is safe to commit, publish and diff.
#: Matched per word, so `max_tokens` is configuration while `auth_token` is a credential.
FORBIDDEN_WORDS = frozenset(
    {
        "key",
        "apikey",
        "auth",
        "authorization",
        "token",
        "bearer",
        "secret",
        "credential",
        "credentials",
        "password",
        "endpoint",
        "url",
        "host",
        "account",
        "organization",
        "org",
    }
)

#: `token_unit` names the unit every count in `usage` is in. It is the one field whose name
#: contains a forbidden word part and is not a credential, so it is allowed by name rather than
#: by pattern.
ALLOWED_FIELDS = frozenset({"token_unit"})


def is_safe(record: Any) -> bool:
    """No credential, no endpoint, no bearer of either — at any depth, through lists as well."""
    if isinstance(record, dict):
        for key, value in record.items():
            if key not in ALLOWED_FIELDS and (
                set(re.split(r"[^a-z0-9]+", key.lower())) & FORBIDDEN_WORDS
            ):
                return False
            if not is_safe(value):
                return False
        return True
    if isinstance(record, list):
        return all(is_safe(item) for item in record)
    if isinstance(record, str):
        return not ("://" in record or record.startswith("sk-"))
    return True
