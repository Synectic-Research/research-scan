"""The record every run writes: complete, configuration-only, and never a credential."""

from __future__ import annotations

from stateless_driver import ENGINE_ID, ENGINE_PROTOCOL_VERSION, engine, provenance

REQUIRED = {
    "engine_protocol_version",
    "engine_id",
    "engine_version",
    "model_id",
    "rubric_hash",
    "prompt_template_hash",
    "schema_version",
    "effort",
    "thinking",
    "sampling",
    "max_concurrency",
    "execution_class",
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


def test_every_required_field_is_present():
    assert set(record().as_dict()) >= REQUIRED


def test_the_record_names_the_engine_and_where_it_ran():
    payload = record().as_dict()
    assert payload["engine_id"] == ENGINE_ID
    assert payload["engine_protocol_version"] == ENGINE_PROTOCOL_VERSION
    assert payload["execution_class"] == "provider-api"
    assert payload["thinking"] == "disabled"
    assert payload["sampling"]["max_tokens"] == 24000


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


def test_no_credential_endpoint_or_token_can_be_in_the_record():
    assert provenance.is_safe(record().as_dict())
    assert not provenance.is_safe({"api_key": "sk-ant-…"})
    assert not provenance.is_safe({"sampling": {"auth_token": "…"}})
    assert not provenance.is_safe({"model_id": "https://api.example.com/v1/messages"})
    assert not provenance.is_safe({"model_id": "sk-ant-not-a-model"})
    assert provenance.is_safe({"sampling": {"max_tokens": 24000}})  # not a credential


def test_the_resolved_model_is_recorded_when_the_provider_reports_one():
    entry = record()
    entry.model_resolved = ["claude-sonnet-5-20260101"]
    assert entry.as_dict()["model_resolved"] == ["claude-sonnet-5-20260101"]
