# SPDX-License-Identifier: Apache-2.0
"""Logging setup (canon §8): human-readable INFO on stderr, machine-readable JSONL per stage.

The stderr stream is for the human watching a run. The per-stage `<stage>.log.jsonl` in the run
directory is for answering "why did retrieval return 40 papers instead of 200" a week later:
per-source counts, HTTP status histogram, durations, and every drop.
"""

from __future__ import annotations

import json
import logging
import sys
import time
from datetime import UTC, datetime
from pathlib import Path
from typing import Any

from research_scan.config import Settings, redact_text

ROOT_LOGGER = "research_scan"


class RedactingFilter(logging.Filter):
    """Replace every known secret in a record's message and args.

    Applied to the handler rather than the logger so that it covers every module, including
    third-party records emitted under our namespace.
    """

    def __init__(self, secrets: tuple[str, ...]) -> None:
        super().__init__()
        self._secrets = tuple(secrets)

    def filter(self, record: logging.LogRecord) -> bool:
        if not self._secrets:
            return True
        if isinstance(record.msg, str):
            record.msg = redact_text(record.msg, self._secrets)
        if record.args:
            if isinstance(record.args, dict):
                record.args = {
                    key: redact_text(value, self._secrets) if isinstance(value, str) else value
                    for key, value in record.args.items()
                }
            else:
                record.args = tuple(
                    redact_text(value, self._secrets) if isinstance(value, str) else value
                    for value in record.args
                )
        return True


def configure(
    level: str = "INFO", *, quiet: bool = False, settings: Settings | None = None
) -> None:
    """Install the stderr handler. Idempotent — safe to call once per CLI invocation."""
    logger = logging.getLogger(ROOT_LOGGER)
    for handler in list(logger.handlers):
        logger.removeHandler(handler)

    handler = logging.StreamHandler(sys.stderr)
    handler.setFormatter(logging.Formatter("%(levelname)-7s %(name)s: %(message)s"))
    if settings is not None:
        handler.addFilter(RedactingFilter(settings.secrets()))
    logger.addHandler(handler)
    logger.setLevel(logging.CRITICAL if quiet else _level(level))
    logger.propagate = False


def _level(level: str) -> int:
    resolved = logging.getLevelName(level.upper())
    return resolved if isinstance(resolved, int) else logging.INFO


def get_logger(name: str) -> logging.Logger:
    return logging.getLogger(name)


class StageLog:
    """Append-only JSONL for one stage, written into the run directory.

    Used as a context manager so entry and exit (with duration) are recorded even when the stage
    raises. Every string value passes through the same redaction as the stderr handler.
    """

    def __init__(self, run_dir: Path, stage: str, *, settings: Settings | None = None) -> None:
        self.path = Path(run_dir) / f"{stage}.log.jsonl"
        self.stage = stage
        self._secrets = settings.secrets() if settings is not None else ()
        self._started = 0.0

    def __enter__(self) -> StageLog:
        self.path.parent.mkdir(parents=True, exist_ok=True)
        self.path.write_text("", encoding="utf-8")  # one file per run of this stage
        self._started = time.monotonic()
        self.event("enter")
        return self

    def __exit__(
        self, exc_type: type[BaseException] | None, exc: BaseException | None, tb: object
    ) -> None:
        self.event(
            "exit",
            duration_s=round(time.monotonic() - self._started, 3),
            failed=exc_type is not None,
            error=str(exc) if exc is not None else None,
        )

    def event(self, event: str, **fields: Any) -> None:
        record = {
            "ts": datetime.now(UTC).isoformat(timespec="seconds"),
            "stage": self.stage,
            "event": event,
            **fields,
        }
        line = json.dumps(_scrub(record, self._secrets), default=str)
        with self.path.open("a", encoding="utf-8") as handle:
            handle.write(line + "\n")


def _scrub(value: Any, secrets: tuple[str, ...]) -> Any:
    if not secrets:
        return value
    if isinstance(value, str):
        return redact_text(value, secrets)
    if isinstance(value, dict):
        return {key: _scrub(item, secrets) for key, item in value.items()}
    if isinstance(value, list):
        return [_scrub(item, secrets) for item in value]
    return value
