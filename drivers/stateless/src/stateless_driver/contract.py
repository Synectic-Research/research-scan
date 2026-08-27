"""The screening driver's CID contract, reconciled instead of all-or-nothing.

Ported unchanged from
`23d7c360590e4d44db986812c390d9026ede9a13:research/experiments/phase12-selection/contract.py`,
the module Phase-1.2A measured and Phase-1.2C and Phase-1.4 then ran on every chunk. Its tests
came with it (`tests/test_contract.py`), against the same recorded fixtures. Edits belong here
now; the evidence tree stays frozen. One mechanical deviation from that file, so this tree can
sit inside the repo's own lint gate: `Callable` and `Iterable` are imported from
`collections.abc`.

Phase-1.2A — the screening driver's CID contract, reconciled instead of all-or-nothing.

The Phase-1.1 driver validated a batch response with `lib/common.validate_batch_scores`, whose
first act is `sorted(got) != sorted(want) -> raise`. One spurious row therefore discarded 25
correct judgements, and did so six times in a row on `llm-lit-search/x02` because the defect is
deterministic: the structured-output decoder pads the array with a mangled variant of a real cid
and labels the padding `"duplicate placeholder"`.

This module replaces that single predicate with a reconciliation between the cids a batch asked
for and the rows a call returned. The judgements are never touched — every rule below is about
the wire shape.

    unknown cid (incl. repeated)      discard the row, log it, do not retry
    expected cid twice, same judgement  keep one, log it
    expected cid twice, judgements differ  that cid is unsatisfied -> retry it (bounded)
    expected cid missing              retry the missing records (sub-batch when supported)
    row fails the field contract      that cid is unsatisfied -> retry it, log why
    retries exhausted                 fail the batch with a recorded reason, keep what is valid

Drop-in for the phase-11 driver: `screen.py::_one` calls `C.validate_batch_scores(batch, payload)`;
`reconcile(batch, payload).scores` is the same list on a clean response, and the retry decision
moves from "did it raise" to `Reconciliation.verdict`. Nothing in `lib/common.py` is edited — the
Phase-1.1 artefacts stay exactly as measured.

**Phase-1.2C, the rerank path.** The same wire defect recurred on `rerank.py`, which does its own
all-or-nothing check (`got != want -> raise`) and re-issues the whole 13-row chunk: one recorded
call returned `extra=['5716814f6adf_placeholder']` while *dropping four real cids*, so the retry
re-paid for nine correct RankedEntries to recover four. Reconciliation is stage-agnostic — only
the array key and the per-row field contract differ — so `rows_key` and `validate_row` are
parameters with the screening shape as their default. `phase12c/rerank_contract.py` supplies the
rerank shape.

**v0.6.0.** Two rules were widened here, and only here — the evidence tree keeps the module as
Phase-1.2A measured it. First, duplicates are collapsed only when they agree on every accepted
judgement field (`JUDGMENT_FIELDS`), not on the score alone: two rows can carry the same score and
disagree about which criteria the paper satisfied, and `criteria_hit` reaches `screen.json`.
Second, a disagreement now costs its own cid rather than the response: invalidating all 25 rows to
re-ask about 1 is the same waste this module was written to remove, one level up. The two ported
assertions that encoded the old whole-batch rule were rewritten to the new one, not relaxed —
they now pin the kept rows and the minimal sub-batch as well.
"""

from __future__ import annotations

import re
from collections.abc import Callable, Iterable
from dataclasses import dataclass, field
from typing import Any

CID_RE = re.compile(r"^[0-9a-f]{12}$")

#: Never loop. One initial call plus at most this many retries, then the batch fails, recorded.
MAX_RETRIES = 2

#: What a reconciliation tells the driver to do next.
COMPLETE = "complete"        # every expected cid satisfied
INVALID = "invalid"          # the response has no rows array at all: nothing in it can be read
INCOMPLETE = "incomplete"    # some expected cids unsatisfied; the satisfied ones are good


@dataclass
class Reconciliation:
    """One response, partitioned against the cids its batch asked for."""

    verdict: str
    scores: list[dict] = field(default_factory=list)
    missing: list[str] = field(default_factory=list)
    reason: str = ""
    provenance: list[dict] = field(default_factory=list)

    def note(self, event: str, **fields: Any) -> None:
        self.provenance.append({"event": event, **fields})


@dataclass
class BatchOutcome:
    """The driver's result for one batch, after however many bounded attempts it took."""

    batch: str
    ok: bool
    scores: list[dict] = field(default_factory=list)
    missing: list[str] = field(default_factory=list)
    attempts: int = 0
    reason: str = ""
    provenance: list[dict] = field(default_factory=list)


def _validate_row(row: dict, known_criteria: set[str]) -> tuple[dict | None, str]:
    """The Phase-1.1 field contract, unrelaxed, applied to one row instead of to the array."""
    if not isinstance(row.get("score"), int) or isinstance(row.get("score"), bool):
        return None, "score is not an integer"
    if not 0 <= row["score"] <= 3:
        return None, f"score {row['score']} out of range"
    if not isinstance(row.get("reason"), str) or not row["reason"]:
        return None, "missing reason"
    hits = row.get("criteria_hit") or []
    if not isinstance(hits, list):
        return None, "criteria_hit is not a list"
    bad = [h for h in hits if h not in known_criteria]
    if bad:
        return None, f"unknown criteria ids {bad}"
    if row["score"] >= 2 and not hits:
        return None, f"score {row['score']} with empty criteria_hit"
    return {
        "cid": row["cid"],
        "score": row["score"],
        "reason": row["reason"],
        "criteria_hit": hits if row["score"] >= 2 else [],
    }, ""


#: Default array key, duplicate discriminator and per-row contract: the screening shape this
#: module was written for. The rerank shape overrides all three (`phase12c/rerank_contract.py`).
SCORES_KEY = "scores"
SCORE_FIELD = "score"

#: The accepted judgement fields, besides the score, that two copies of a cid have to agree on
#: before they can be collapsed into one. Phase-1.2A compared the score alone, which was too
#: narrow: two rows can carry the same score and disagree about *which* criteria the paper
#: satisfied, and `criteria_hit` is an accepted field that reaches `screen.json` and the
#: shortlist's second tier. Collapsing those picked one attribution over another silently.
JUDGMENT_FIELDS = ("criteria_hit",)


def _judgment(row: dict, score_field: str, judgment_fields: Iterable[str]) -> tuple:
    """One row's judgement, normalised so that only real disagreement counts as disagreement.

    Lists are compared as sets: `["C1", "C2"]` and `["C2", "C1", "C2"]` are the same attribution
    written two ways, and re-asking the model about that would spend a call on nothing. Everything
    is stringified so a malformed value compares rather than raising.
    """
    parts: list[Any] = [("score", repr(row.get(score_field)))]
    for name in judgment_fields:
        value = row.get(name)
        if isinstance(value, list):
            parts.append((name, "list", *sorted({repr(item) for item in value})))
        else:
            parts.append((name, "scalar", repr(value)))
    return tuple(parts)


def reconcile(
    batch: dict,
    payload: Any,
    *,
    rows_key: str = SCORES_KEY,
    score_field: str = SCORE_FIELD,
    judgment_fields: tuple[str, ...] = JUDGMENT_FIELDS,
    validate_row: Callable[[dict, set[str]], tuple[dict | None, str]] | None = None,
) -> Reconciliation:
    """Partition a batch response against `batch['items']`. Never raises on model output.

    `rows_key` / `score_field` / `judgment_fields` / `validate_row` select the stage's wire shape.
    The reconciliation rules — unknown cids discarded without a retry, duplicates collapsed only
    when they agree on every accepted judgement field, a disagreement or a bad row costing its own
    cid rather than the batch — are the same at every stage.
    """
    validate_row = validate_row or _validate_row
    want = [item["cid"] for item in batch["items"]]
    want_set = set(want)
    known = {criterion["id"] for criterion in batch["sub_criteria"]}

    rec = Reconciliation(verdict=INVALID)
    rows = payload.get(rows_key) if isinstance(payload, dict) else None
    if not isinstance(rows, list):
        rec.note("no_scores_array", got=type(payload).__name__, key=rows_key)
        rec.missing = list(want)
        rec.reason = f"no {rows_key} array"
        return rec

    # 1. Unknown cids never reach the judgement layer, and never earn a retry: a batch cannot be
    #    made to stop hallucinating a 26th row by asking it again — six recorded attempts proved it.
    by_cid: dict[str, list[dict]] = {}
    for row in rows:
        cid = row.get("cid") if isinstance(row, dict) else None
        if not isinstance(cid, str) or cid not in want_set:
            rec.note("unknown_cid_discarded", cid=cid,
                     well_formed=bool(isinstance(cid, str) and CID_RE.match(cid)),
                     reason=(row or {}).get("reason") if isinstance(row, dict) else None)
            continue
        by_cid.setdefault(cid, []).append(row)

    # 2. Duplicates of an expected cid. Same judgement -> keep one. A disagreement in any accepted
    #    field -> that cid is unresolved and is re-asked; the rest of the response still stands.
    #    The contradiction is about one paper, so it costs one paper: making it invalidate the
    #    response re-bought 24 correct judgements to recover 1, which is the waste this module
    #    exists to remove.
    conflicting: list[str] = []
    chosen: dict[str, dict] = {}
    for cid, group in by_cid.items():
        if len(group) > 1:
            judgments = {_judgment(row, score_field, judgment_fields) for row in group}
            if len(judgments) > 1:
                conflicting.append(cid)
                rec.note("duplicate_conflicting", cid=cid,
                         scores=sorted({str(row.get(score_field)) for row in group}),
                         fields=sorted(_disagreeing_fields(group, score_field, judgment_fields)))
                continue
            rec.note("duplicate_identical_collapsed", cid=cid, copies=len(group),
                     score=group[0].get(score_field))
        chosen[cid] = group[0]

    # 3. Field contract, per row. A bad row costs its own cid, not the batch.
    unresolved = set(conflicting)
    for cid in want:
        row = chosen.get(cid)
        if cid in unresolved or row is None:
            rec.missing.append(cid)
            continue
        clean, why = validate_row(row, known)
        if clean is None:
            rec.note("row_rejected", cid=cid, why=why)
            rec.missing.append(cid)
            continue
        rec.scores.append(clean)

    rec.verdict = COMPLETE if not rec.missing else INCOMPLETE
    rec.reason = "" if not rec.missing else f"{len(rec.missing)} cid(s) unsatisfied"
    if conflicting:
        rec.reason += f"; conflicting duplicate judgements for {sorted(conflicting)}"
    return rec


def _disagreeing_fields(
    group: list[dict], score_field: str, judgment_fields: Iterable[str]
) -> set[str]:
    """Which accepted fields the copies of one cid actually disagreed about — for the log."""
    names = [score_field, *judgment_fields]
    return {
        name
        for index, name in enumerate(names)
        if len({_judgment(row, score_field, judgment_fields)[index] for row in group}) > 1
    }


def sub_batch(batch: dict, cids: Iterable[str]) -> dict:
    """The same batch, narrowed to the cids still owed. Same rubric, same sub-criteria."""
    keep = set(cids)
    return {**batch, "items": [item for item in batch["items"] if item["cid"] in keep]}


def screen_batch(
    batch: dict,
    call: Callable[[dict], Any],
    *,
    max_retries: int = MAX_RETRIES,
    supports_sub_batch: bool = True,
    rows_key: str = SCORES_KEY,
    score_field: str = SCORE_FIELD,
    judgment_fields: tuple[str, ...] = JUDGMENT_FIELDS,
    validate_row: Callable[[dict, set[str]], tuple[dict | None, str]] | None = None,
) -> BatchOutcome:
    """Call, reconcile, retry what is owed — at most `max_retries` times, then fail on the record.

    `call` takes a batch dict and returns the decoded payload. Exceptions from it are recorded and
    count as attempts, so a transport failure cannot loop either.
    """
    want = [item["cid"] for item in batch["items"]]
    outcome = BatchOutcome(batch=batch.get("batch", "?"), ok=False, missing=list(want))
    accepted: dict[str, dict] = {}
    owed = list(want)
    ask = batch

    for attempt in range(max_retries + 1):
        outcome.attempts = attempt + 1
        try:
            payload = call(ask)
        except Exception as exc:  # noqa: BLE001 — a failed call is data, not a crash
            outcome.provenance.append(
                {"event": "call_failed", "attempt": outcome.attempts,
                 "error": f"{type(exc).__name__}: {exc}"[:400]}
            )
            outcome.reason = f"{type(exc).__name__}: {exc}"[:400]
            continue

        rec = reconcile(ask, payload, rows_key=rows_key, score_field=score_field,
                        judgment_fields=judgment_fields, validate_row=validate_row)
        for entry in rec.provenance:
            outcome.provenance.append({"attempt": outcome.attempts, **entry})

        if rec.verdict == INVALID:
            # The attempt is discarded, not the batch: rows banked by earlier attempts stand.
            outcome.reason = rec.reason
            outcome.provenance.append(
                {"event": "batch_invalid", "attempt": outcome.attempts, "reason": rec.reason}
            )
            ask = batch if not accepted else sub_batch(batch, owed)
            continue

        for row in rec.scores:
            accepted.setdefault(row["cid"], row)
        owed = [cid for cid in want if cid not in accepted]
        outcome.missing = list(owed)

        if not owed:
            outcome.ok = True
            outcome.reason = ""
            break

        outcome.reason = rec.reason
        if attempt < max_retries:
            ask = sub_batch(batch, owed) if supports_sub_batch else batch
            outcome.provenance.append(
                {"event": "retry", "attempt": outcome.attempts, "owed": len(owed),
                 "mode": "sub_batch" if supports_sub_batch else "whole_batch"}
            )

    outcome.scores = [accepted[cid] for cid in want if cid in accepted]
    if not outcome.ok:
        outcome.provenance.append(
            {"event": "batch_failed", "attempts": outcome.attempts, "reason": outcome.reason,
             "kept": len(outcome.scores), "missing": len(outcome.missing)}
        )
    return outcome
