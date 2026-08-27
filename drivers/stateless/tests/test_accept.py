"""The acceptance chain: every step can reject, no step may repair."""

from __future__ import annotations

import pytest
from stateless_driver import accept

from conftest import row


def test_a_body_that_is_not_json_is_a_schema_error():
    with pytest.raises(accept.SchemaError):
        accept.decode("I screened the batch for you!")


@pytest.mark.parametrize(
    "payload",
    [[], {"results": []}, {"scores": {}}, {"scores": [[]]}, {"scores": [{"cid": "a"}]}],
    ids=["array", "wrong-key", "not-a-list", "row-not-object", "row-missing-fields"],
)
def test_the_wire_schema_is_checked_before_anything_else(payload):
    with pytest.raises(accept.SchemaError):
        accept.check_wire_schema(payload)


def test_a_clean_body_passes_the_schema_step_unchanged():
    payload = {"scores": [row("aaaaaaaaaaaa")]}
    assert accept.check_wire_schema(payload) is payload


def test_a_reason_over_the_word_bound_costs_its_own_row():
    long_reason = " ".join(["word"] * (accept.MAX_REASON_WORDS + 1))
    clean, why = accept.screen_row(row("aaaaaaaaaaaa", reason=long_reason), {"C1"})
    assert clean is None
    assert "over the 20 allowed" in why


def test_a_reason_at_the_bound_is_accepted():
    at_bound = " ".join(["word"] * accept.MAX_REASON_WORDS)
    clean, _ = accept.screen_row(row("aaaaaaaaaaaa", reason=at_bound), {"C1"})
    assert clean["reason"] == at_bound


def test_a_malformed_cid_is_rejected_rather_than_repaired():
    clean, why = accept.screen_row(row("AAAAAAAAAAAA"), {"C1"})
    assert clean is None
    assert "12 lowercase hex" in why


def test_the_row_contract_is_the_ported_one():
    """Unknown criterion, out-of-range score, ≥ 2 with no attribution — all still rejections."""
    assert accept.screen_row(row("aaaaaaaaaaaa", hits=("C9",)), {"C1"})[0] is None
    assert accept.screen_row(row("aaaaaaaaaaaa", score=7), {"C1"})[0] is None
    assert accept.screen_row(row("aaaaaaaaaaaa", score=2, hits=()), {"C1"})[0] is None


def test_an_accepted_row_carries_exactly_what_the_model_said():
    clean, _ = accept.screen_row(row("aaaaaaaaaaaa", score=3, reason="why", hits=("C1",)), {"C1"})
    assert clean == {"cid": "aaaaaaaaaaaa", "score": 3, "reason": "why", "criteria_hit": ["C1"]}


def test_provenance_rides_beside_the_rows_never_inside_them():
    """`ScreenScore` forbids unknown keys, so an engine field on a row would fail the package."""
    from stateless_driver import contract

    outcome = contract.BatchOutcome(batch="01", ok=True, scores=[row("aaaaaaaaaaaa")], attempts=1)
    accepted = accept.attach({"engine_id": "anthropic-stateless-reference"}, [outcome])

    assert accepted.scores == [row("aaaaaaaaaaaa")]
    assert set(accepted.scores[0]) == {"cid", "score", "reason", "criteria_hit"}
    assert accepted.as_dict()["provenance"]["engine_id"] == "anthropic-stateless-reference"
    assert accepted.as_dict()["batches"]["01"]["accepted"] == 1
