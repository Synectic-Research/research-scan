"""Phase-1.4 — the `priority_rank` contract, and the row validator that carries it.

The slice pre-registers four rules and one consequence:

    all `overall == 3` rows carry a priority_rank      violation -> exit 2
    ranks unique
    ranks contiguous from 1
    no `overall < 3` row carries one

`PriorityContractViolation` is the exit-2 class. It is raised by `check_batch` *after* the chunk has
been reconciled and accepted — a rank contract is a property of the whole batch, so it cannot be a
per-row field check, and it must not be one either: making a bad rank cost its own cid would let a
chunk quietly ship a rank order with a hole in it.

The per-row validator is `rerank_contract._validate_entry` — the frozen Phase-1.1 field contract,
unrelaxed — with `priority_rank` type-checked and carried through. Reconciliation semantics
(unknown cids discarded without a retry, identical duplicates collapsed, conflicting duplicates
invalidating the response, a bad row costing its own cid) are `contract.py`'s, unchanged.
"""

from __future__ import annotations

import sys
from pathlib import Path
from typing import Any

HERE = Path(__file__).resolve().parent
P12 = HERE.parent / "phase12-selection"
P12C = P12 / "phase12c"
sys.path.insert(0, str(P12C))
sys.path.insert(0, str(P12))

import contract  # noqa: E402
import rerank_contract  # noqa: E402
from schema14 import MAX_RANK, PRIORITY_KEY  # noqa: E402


class PriorityContractViolation(RuntimeError):
    """A chunk's `priority_rank` block is not a strict contiguous order over its 3s. Exit 2."""

    EXIT_CODE = 2

    def __init__(self, batch: str, violations: list[str], rows: list[dict]) -> None:
        super().__init__(f"{batch}: priority_rank contract violated: {'; '.join(violations)}")
        self.batch = batch
        self.violations = violations
        self.rows = [
            {"cid": r.get("cid"), "overall": r.get("overall"), PRIORITY_KEY: r.get(PRIORITY_KEY)}
            for r in rows
        ]


def validate_entry_with_priority(row: dict, known_criteria: set[str]) -> tuple[dict | None, str]:
    """`rerank_contract._validate_entry` plus the `priority_rank` field's own type check.

    Only the field's *shape* is checked here. Whether the ranks form a strict contiguous order is a
    batch-level question, and lives in `check_batch`.
    """
    clean, why = rerank_contract._validate_entry(row, known_criteria)
    if clean is None:
        return None, why
    rank = row.get(PRIORITY_KEY)
    if not isinstance(rank, int) or isinstance(rank, bool):
        return None, f"{PRIORITY_KEY} {rank!r} is not an integer"
    if not 0 <= rank <= MAX_RANK:
        return None, f"{PRIORITY_KEY} {rank} out of range 0..{MAX_RANK}"
    clean[PRIORITY_KEY] = rank
    return clean, ""


def check_batch(batch_tag: str, rows: list[dict]) -> None:
    """The four pre-registered rules, over one accepted chunk. Raises on any violation."""
    violations: list[str] = []

    top = [r for r in rows if r.get("overall") == 3]
    below = [r for r in rows if r.get("overall") != 3]

    missing = [r["cid"] for r in top if not r.get(PRIORITY_KEY)]
    if missing:
        violations.append(f"{len(missing)} overall==3 row(s) carry no rank: {sorted(missing)[:6]}")

    stray = [r["cid"] for r in below if r.get(PRIORITY_KEY)]
    if stray:
        violations.append(f"{len(stray)} overall<3 row(s) carry a rank: {sorted(stray)[:6]}")

    ranks = [r[PRIORITY_KEY] for r in top if r.get(PRIORITY_KEY)]
    if len(set(ranks)) != len(ranks):
        dupes = sorted({x for x in ranks if ranks.count(x) > 1})
        violations.append(f"ranks not unique: {dupes}")

    if ranks and sorted(set(ranks)) != list(range(1, len(set(ranks)) + 1)):
        violations.append(f"ranks not contiguous from 1: {sorted(ranks)}")

    if violations:
        raise PriorityContractViolation(batch_tag, violations, rows)


def strip_priority(rows: list[dict]) -> tuple[list[dict], dict[str, int]]:
    """Split an accepted chunk into (shipped-schema RankedEntries, cid -> rank).

    `ranked.json` must validate against the shipped `Ranked` model, which is `extra="forbid"`. The
    ranks go to `priority.json` beside it, so `verify` and `emit` run byte-identically in every
    cell.
    """
    entries, priority = [], {}
    for row in rows:
        entry = {k: v for k, v in row.items() if k != PRIORITY_KEY}
        entries.append(entry)
        if PRIORITY_KEY in row:
            priority[row["cid"]] = row[PRIORITY_KEY]
    return entries, priority


def rerank_chunk(batch: dict, call: Any, *, priority: bool, **kw) -> contract.BatchOutcome:
    """`contract.screen_batch` bound to the rerank wire shape, with or without `priority_rank`."""
    return contract.screen_batch(
        batch,
        call,
        rows_key=rerank_contract.RANKED_KEY,
        score_field=rerank_contract.RANKED_SCORE_FIELD,
        validate_row=validate_entry_with_priority if priority else rerank_contract._validate_entry,
        **kw,
    )
