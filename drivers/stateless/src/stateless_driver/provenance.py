"""The record every driver run writes: what judged, under what, at what settings.

A cognition artifact with no provenance is a model's opinion of unknown origin. This record is
what makes one reproducible enough to argue with — and it is deliberately a description of
*configuration*, never of *access*: no key, no token, no endpoint, no account or organisation
identifier reaches it. What it carries is the model, the effort and thinking configuration, the
sampling parameters, the hashes of the two texts that steer the judgement, the wire schema's
version, the concurrency the run used, and where execution happened.
"""

from __future__ import annotations

import hashlib
import re
from dataclasses import asdict, dataclass, field
from typing import Any

from stateless_driver import ENGINE_ID, ENGINE_PROTOCOL_VERSION, __version__, prompt

#: Where the judgement physically ran. `provider-api` means: off this machine, in a provider's
#: service, under that provider's own model revisions.
EXECUTION_CLASS = "provider-api"


def digest(text: str) -> str:
    """`sha256:<hex>` — long enough to be an identity, prefixed so it is never mistaken for one."""
    return "sha256:" + hashlib.sha256(text.encode("utf-8")).hexdigest()


@dataclass
class Sampling:
    """Everything that moves the distribution the judgement is drawn from."""

    max_tokens: int
    temperature: float | None = None
    top_p: float | None = None


@dataclass
class EngineProvenance:
    """One run of one engine. Serialised beside the artifact it produced."""

    engine_protocol_version: str
    engine_id: str
    engine_version: str
    model_id: str
    rubric_hash: str
    prompt_template_hash: str
    schema_version: str
    schema_hash: str
    effort: str
    thinking: str
    sampling: dict[str, Any]
    max_concurrency: int
    execution_class: str
    prompt_cache: bool
    brief_hash: str
    model_resolved: list[str] = field(default_factory=list)

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
) -> EngineProvenance:
    """The record for a run that is about to start. `model_resolved` is filled in as calls land."""
    return EngineProvenance(
        engine_protocol_version=ENGINE_PROTOCOL_VERSION,
        engine_id=ENGINE_ID,
        engine_version=__version__,
        model_id=model_id,
        rubric_hash=digest(rubric),
        # The template, not the filled prompt: one hash for the whole run, and it changes when the
        # instructions change rather than when the batch does. `brief_hash` covers the run's input.
        prompt_template_hash=digest(prompt.SYSTEM_TEMPLATE + prompt.USER_TEMPLATE),
        schema_version=prompt.SCHEMA_VERSION,
        schema_hash=digest(repr(prompt.SCREEN_OUTPUT_SCHEMA)),
        effort=effort,
        thinking=thinking,
        sampling=asdict(sampling),
        max_concurrency=max_concurrency,
        execution_class=EXECUTION_CLASS,
        prompt_cache=prompt_cache,
        brief_hash=digest(brief),
    )


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


def is_safe(record: dict[str, Any]) -> bool:
    """No credential, no endpoint, no bearer of either — at any depth."""
    for key, value in record.items():
        if set(re.split(r"[^a-z0-9]+", key.lower())) & FORBIDDEN_WORDS:
            return False
        if isinstance(value, dict) and not is_safe(value):
            return False
        if isinstance(value, str) and ("://" in value or value.startswith("sk-")):
            return False
    return True
