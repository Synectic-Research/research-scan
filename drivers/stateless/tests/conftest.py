"""A fake provider client, so every call path in the driver is testable without spending."""

from __future__ import annotations

import json
from dataclasses import dataclass, field
from typing import Any

import pytest


@dataclass
class FakeUsage:
    input_tokens: int = 1000
    output_tokens: int = 500
    cache_read_input_tokens: int = 0
    cache_creation_input_tokens: int = 0


@dataclass
class FakeBlock:
    text: str
    type: str = "text"


@dataclass
class FakeMessage:
    content: list[FakeBlock]
    usage: FakeUsage = field(default_factory=FakeUsage)
    model: str = "claude-sonnet-5-20260101"


class _Stream:
    def __init__(self, message: FakeMessage) -> None:
        self._message = message

    def __enter__(self) -> _Stream:
        return self

    def __exit__(self, *exc: object) -> bool:
        return False

    def get_final_message(self) -> FakeMessage:
        return self._message


class FakeMessages:
    def __init__(self, responder) -> None:
        self._responder = responder
        self.requests: list[dict[str, Any]] = []

    def stream(self, **kwargs: Any) -> _Stream:
        self.requests.append(kwargs)
        body = self._responder(kwargs, len(self.requests))
        if isinstance(body, Exception):
            raise body
        return _Stream(FakeMessage(content=[FakeBlock(json.dumps(body))]))


class FakeClient:
    """`responder(request, call_number)` returns the body to answer with, or an exception."""

    def __init__(self, responder) -> None:
        self.messages = FakeMessages(responder)


@pytest.fixture
def batch() -> dict:
    return {
        "batch": "01",
        "sub_criteria": [{"id": "C1", "name": "n", "text": "t"}],
        "items": [
            {"cid": "aaaaaaaaaaaa", "title": "A"},
            {"cid": "bbbbbbbbbbbb", "title": "B"},
        ],
    }


def row(cid: str, score: int = 3, reason: str = "central to the brief", hits=("C1",)) -> dict:
    return {"cid": cid, "score": score, "reason": reason, "criteria_hit": list(hits)}
