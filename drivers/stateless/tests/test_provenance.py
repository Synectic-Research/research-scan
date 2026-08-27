"""The record every run writes: complete, configuration-only, and never a credential."""

from __future__ import annotations

import json
import re

from stateless_driver import ENGINE_ID, ENGINE_PROTOCOL_VERSION, contract, engine, provenance

#: Every key a serialised record carries, filled or null. A reader that knows
#: `provenance_schema_version` knows to expect exactly these.
REQUIRED = {
    "provenance_schema_version",
    "run_id",
    "started_at",
    "completed_at",
    "engine_protocol_version",
    "engine_id",
    "engine_version",
    "model_id",
    "model_revision_or_hash",
    "rubric_hash",
    "prompt_template_hash",
    "response_schema_version",
    "effort_or_thinking_configuration",
    "sampling_parameters",
    "batch_size",
    "max_concurrency",
    "execution_class",
    "attempt_count",
    "retry_summary",
    "input_record_count",
    "accepted_record_count",
    "unresolved_cids",
    "usage",
    "cost",
    "currency",
    "completion_status",
}


def record(**overrides):
    kwargs = {
        "model_id": "claude-sonnet-5",
        "rubric": "# rubric\nscore 0-3",
        "brief": "Purpose: research\n\nthe brief",
        "effort": "high",
        "thinking": engine.THINKING,
        "sampling": provenance.Sampling(max_tokens=24000),
        "max_concurrency": 8,
        "prompt_cache": True,
    }
    kwargs.update(overrides)
    return provenance.build(**kwargs)


def outcome(batch: str, *, ok: bool, attempts: int, scores: int, missing=()):
    return contract.BatchOutcome(
        batch=batch,
        ok=ok,
        scores=[{"cid": f"{index:012x}"} for index in range(scores)],
        missing=list(missing),
        attempts=attempts,
    )


# --- completeness -----------------------------------------------------------


def test_every_required_field_is_present_even_before_the_run_has_anything_to_report():
    """A missing key is ambiguous six months later; an explicit null is not."""
    payload = record().as_dict()

    assert set(payload) >= REQUIRED
    for key in ("completed_at", "model_revision_or_hash", "attempt_count", "cost"):
        assert payload[key] is None
    assert payload["completion_status"] == "started"


def test_every_required_field_survives_json_serialisation():
    payload = json.loads(json.dumps(record().as_dict()))
    assert set(payload) >= REQUIRED


def test_the_record_names_the_engine_and_where_it_ran():
    payload = record().as_dict()
    assert payload["engine_id"] == ENGINE_ID
    assert payload["engine_protocol_version"] == ENGINE_PROTOCOL_VERSION
    assert payload["provenance_schema_version"] == provenance.PROVENANCE_SCHEMA_VERSION
    assert payload["execution_class"] == "provider-api"
    assert payload["effort_or_thinking_configuration"] == {"effort": "high", "thinking": "disabled"}
    assert payload["sampling_parameters"]["max_tokens"] == 24000


def test_the_units_are_stated_rather_than_assumed():
    payload = record().as_dict()
    assert payload["token_unit"] == "tokens"
    assert payload["currency"] == "USD", "stated even when the amount is null"


def test_timestamps_are_iso_8601_utc_with_an_explicit_offset():
    payload = provenance.finalize(
        record(), [outcome("01", ok=True, attempts=1, scores=2)], usage={}, input_record_count=2
    ).as_dict()

    for key in ("started_at", "completed_at"):
        assert re.match(r"^\d{4}-\d{2}-\d{2}T\d{2}:\d{2}:\d{2}(\.\d+)?\+00:00$", payload[key]), key


def test_every_hash_names_its_algorithm():
    payload = record().as_dict()
    for key in ("rubric_hash", "prompt_template_hash", "brief_hash", "response_schema_hash"):
        assert payload[key].startswith("sha256:"), key


# --- what the run did -------------------------------------------------------


def test_the_outcome_fields_close_against_what_the_run_actually_did():
    outcomes = [
        outcome("01", ok=True, attempts=1, scores=25),
        outcome("02", ok=True, attempts=2, scores=25),
        outcome("03", ok=False, attempts=3, scores=23, missing=["aaaaaaaaaaaa", "bbbbbbbbbbbb"]),
    ]

    payload = provenance.finalize(
        record(), outcomes, usage={"calls": 6}, input_record_count=75
    ).as_dict()

    assert payload["attempt_count"] == 6
    assert payload["input_record_count"] == 75
    assert payload["accepted_record_count"] == 73
    assert payload["unresolved_cids"] == ["aaaaaaaaaaaa", "bbbbbbbbbbbb"]
    assert payload["completion_status"] == "incomplete"
    assert payload["retry_summary"] == {
        "batches": 3,
        "batches_first_try": 1,
        "batches_retried": 2,
        "batches_failed": ["03"],
        "attempts_total": 6,
        "max_attempts_on_one_batch": 3,
    }


def test_a_run_that_resolved_every_cid_is_recorded_complete():
    payload = provenance.finalize(
        record(), [outcome("01", ok=True, attempts=1, scores=25)], usage={}, input_record_count=25
    ).as_dict()

    assert payload["completion_status"] == "complete"
    assert payload["unresolved_cids"] == []


def test_usage_and_cost_cover_the_retries_and_not_only_the_first_attempt():
    """The engine's total is per call, so a retried batch is counted twice — which is the point."""
    first = engine.Usage(input_tokens=1000, output_tokens=500, calls=1)
    retry = engine.Usage(input_tokens=400, output_tokens=200, calls=1)
    total = engine.Usage()
    total.add(first)
    total.add(retry)

    pricing = provenance.Pricing(input_per_mtok=3.0, output_per_mtok=15.0)
    payload = provenance.finalize(
        record(),
        [outcome("01", ok=True, attempts=2, scores=25)],
        usage=total.as_dict(),
        pricing=pricing,
        input_record_count=25,
    ).as_dict()

    assert payload["usage"]["calls"] == 2, "the retry is a call and is counted"
    assert payload["usage"]["input_tokens"] == 1400
    assert payload["attempt_count"] == 2
    # 1400/1e6*3 + 700/1e6*15 — both attempts, not the first one only.
    assert payload["cost"] == pricing.usd(total.as_dict()) == 0.0147
    assert payload["cost"] > pricing.usd(first.as_dict())
    assert payload["currency"] == "USD"


def test_cost_is_null_rather_than_guessed_when_no_price_table_is_supplied():
    """A stale price table baked into a record reads as measured; an explicit null does not."""
    payload = provenance.finalize(
        record(), [outcome("01", ok=True, attempts=1, scores=1)], usage={}, input_record_count=1
    ).as_dict()

    assert payload["cost"] is None
    assert payload["currency"] == "USD"


def test_the_resolved_model_revision_is_recorded_when_the_provider_reports_one():
    payload = provenance.finalize(
        record(),
        [outcome("01", ok=True, attempts=1, scores=1)],
        usage={},
        input_record_count=1,
        model_revision_or_hash=["claude-sonnet-5-20260101"],
    ).as_dict()

    assert payload["model_revision_or_hash"] == ["claude-sonnet-5-20260101"]


# --- the hashes -------------------------------------------------------------


def test_a_changed_rubric_changes_its_hash_and_nothing_else():
    before, after = record().as_dict(), record(rubric="# rubric\nscore 0-2").as_dict()
    assert before["rubric_hash"] != after["rubric_hash"]
    assert before["prompt_template_hash"] == after["prompt_template_hash"]


def test_the_prompt_template_hash_covers_the_template_not_the_batch():
    """One hash for the whole run: the batch varies by design and the instructions do not."""
    assert record().as_dict()["prompt_template_hash"] == record(brief="Purpose: build\n").as_dict()[
        "prompt_template_hash"
    ]


def test_the_brief_is_hashed_never_carried():
    payload = record().as_dict()
    assert payload["brief_hash"].startswith("sha256:")
    assert "the brief" not in repr(payload)


# --- redaction --------------------------------------------------------------

#: Secrets of each shape a driver could plausibly leak, planted so the scan has something to find.
PLANTED = {
    "api_key": "sk-ant-api03-NOTAREALKEYbutshapedlikeone",
    "auth_token": "Bearer eyJhbGciOiJIUzI1NiJ9.payload.signature",
    "credentialed_url": "https://user:pa55w0rd@api.example.com/v1/messages",
    "base_url": "https://api.anthropic.com",
    "env_dump": "ANTHROPIC_API_KEY=sk-ant-api03-NOTAREALKEYbutshapedlikeone",
}


def test_a_finished_record_carries_no_planted_secret_anywhere_in_its_serialisation():
    """The whole serialised record is scanned, not a field list: a leak takes any key it likes."""
    payload = provenance.finalize(
        record(),
        [outcome("01", ok=True, attempts=2, scores=25)],
        usage=engine.Usage(input_tokens=10, output_tokens=5, calls=2).as_dict(),
        input_record_count=25,
        model_revision_or_hash=["claude-sonnet-5-20260101"],
        pricing=provenance.Pricing(input_per_mtok=3.0, output_per_mtok=15.0),
    ).as_dict()
    serialised = json.dumps(payload)

    assert provenance.is_safe(payload)
    for label, secret in PLANTED.items():
        assert secret not in serialised, label
    for fragment in ("sk-ant-", "Bearer ", "://", "pa55w0rd", "ANTHROPIC_API_KEY"):
        assert fragment not in serialised, fragment


def test_each_planted_secret_is_caught_wherever_it_is_hidden():
    """The scan itself is tested: a check that cannot fail is not a check."""
    assert not provenance.is_safe({"api_key": PLANTED["api_key"]})
    assert not provenance.is_safe({"sampling_parameters": {"auth_token": PLANTED["auth_token"]}})
    assert not provenance.is_safe({"model_id": PLANTED["credentialed_url"]})
    assert not provenance.is_safe({"base_url": PLANTED["base_url"]})
    assert not provenance.is_safe({"model_id": "sk-ant-not-a-model"})
    # Buried in a list, which an earlier version of the scan walked straight past.
    assert not provenance.is_safe({"model_revision_or_hash": [PLANTED["credentialed_url"]]})
    assert not provenance.is_safe({"retry_summary": {"notes": [{"endpoint": "x"}]}})


def test_the_scan_does_not_fire_on_configuration_that_merely_sounds_like_a_credential():
    assert provenance.is_safe({"sampling_parameters": {"max_tokens": 24000}})
    assert provenance.is_safe({"token_unit": "tokens"})
    assert provenance.is_safe(record().as_dict())
