"""The call path: one batch per call, thinking off, and the contract deciding what a call bought."""

from __future__ import annotations

from stateless_driver import engine as engine_module

from conftest import FakeClient, row

WANT = ["aaaaaaaaaaaa", "bbbbbbbbbbbb"]


def build(responder, **overrides) -> engine_module.Engine:
    kwargs = {"client": FakeClient(responder), "system": "system prefix"}
    kwargs.update(overrides)
    return engine_module.Engine(**kwargs)


def clean(_request, _n):
    return {"scores": [row(cid) for cid in WANT]}


def test_the_request_is_one_stateless_call_with_thinking_off(batch):
    engine = build(clean)
    engine.call(batch)

    request = engine.client.messages.requests[0]
    assert request["thinking"] == {"type": "disabled"}
    assert request["output_config"]["effort"] == engine_module.DEFAULT_EFFORT
    assert request["output_config"]["format"]["type"] == "json_schema"
    assert len(request["messages"]) == 1
    assert request["messages"][0]["role"] == "user"
    assert request["system"][0]["cache_control"] == {"type": "ephemeral"}


def test_the_stable_prefix_is_not_cached_when_caching_is_off(batch):
    engine = build(clean, prompt_cache=False)
    engine.call(batch)
    assert "cache_control" not in engine.client.messages.requests[0]["system"][0]


def test_usage_and_the_resolved_model_are_recorded_per_call(batch):
    engine = build(clean)
    engine_module.screen(engine, {"01": batch})

    assert engine.usage.calls == 1
    assert engine.usage.input_tokens == 1000
    assert engine.models_seen == {"claude-sonnet-5-20260101"}
    assert engine.calls[0]["batch"] == "01"


def test_a_spurious_extra_row_no_longer_destroys_the_batch(batch):
    """The recorded x02 defect, at driver level: 2 correct rows survive a hallucinated third."""

    def padded(_request, _n):
        return {"scores": [row(cid) for cid in WANT] + [row("ccccccccccccc_dup", reason="dup")]}

    engine = build(padded)
    outcome = engine_module.screen(engine, {"01": batch})[0]

    assert outcome.ok
    assert [entry["cid"] for entry in outcome.scores] == WANT
    assert engine.usage.calls == 1  # a ghost row never buys another call
    assert [event["event"] for event in outcome.provenance] == ["unknown_cid_discarded"]


def test_a_missing_cid_is_re_asked_as_a_sub_batch(batch):
    def drops_one(request, n):
        if n == 1:
            return {"scores": [row("aaaaaaaaaaaa")]}
        asked = request["messages"][0]["content"]
        assert "bbbbbbbbbbbb" in asked and "aaaaaaaaaaaa" not in asked
        return {"scores": [row("bbbbbbbbbbbb")]}

    engine = build(drops_one)
    outcome = engine_module.screen(engine, {"01": batch})[0]

    assert outcome.ok
    assert [entry["cid"] for entry in outcome.scores] == WANT
    assert engine.usage.calls == 2


def test_a_batch_that_never_completes_fails_on_the_record_with_what_it_did_get(batch):
    engine = build(lambda _request, _n: {"scores": [row("aaaaaaaaaaaa")]})
    outcome = engine_module.screen(engine, {"01": batch})[0]

    assert not outcome.ok
    assert [entry["cid"] for entry in outcome.scores] == ["aaaaaaaaaaaa"]
    assert outcome.missing == ["bbbbbbbbbbbb"]
    assert outcome.attempts == 3  # bounded: one call plus contract.MAX_RETRIES
    assert outcome.provenance[-1]["event"] == "batch_failed"


def test_a_raising_call_is_data_not_a_crash(batch):
    engine = build(lambda _request, _n: RuntimeError("connection reset"))
    outcome = engine_module.screen(engine, {"01": batch})[0]

    assert not outcome.ok
    assert "connection reset" in outcome.reason
    assert outcome.attempts == 3


def test_every_batch_is_screened_and_the_first_one_runs_alone(batch):
    batches = {f"{n:02d}": {**batch, "batch": f"{n:02d}"} for n in range(1, 6)}
    engine = build(clean)

    outcomes = engine_module.screen(engine, batches, max_concurrency=4)

    assert [outcome.batch for outcome in outcomes] == list(batches)
    assert engine.usage.calls == 5
    assert engine.client.messages.requests[0]["messages"][0]["content"].count('"batch": "01"') == 1
