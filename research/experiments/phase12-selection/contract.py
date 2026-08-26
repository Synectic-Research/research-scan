"""Phase-1.2A — the screening driver's CID contract, reconciled instead of all-or-nothing.

The Phase-1.1 driver validated a batch response with `lib/common.validate_batch_scores`, whose
first act is `sorted(got) != sorted(want) -> raise`. One spurious row therefore discarded 25
correct judgements, and did so six times in a row on `llm-lit-search/x02` because the defect is
deterministic: the structured-output decoder pads the array with a mangled variant of a real cid
and labels the padding `"duplicate placeholder"`.

This module replaces that single predicate with a reconciliation between the cids a batch asked
for and the rows a call returned. The judgements are never touched — every rule below is about
the wire shape.

    unknown cid (incl. repeated)      discard the row, log it, do not retry
    expected cid twice, same score    keep one, log it
    expected cid twice, scores differ batch invalid -> retry (bounded)
    expected cid missing              retry the missing records (sub-batch when supported)
    row fails the field contract      that cid is unsatisfied -> retry it, log why
    retries exhausted                 fail the batch with a recorded reason, keep what is valid

Drop-in for the phase-11 driver: `screen.py::_one` calls `C.validate_batch_scores(batch, payload)`;
`reconcile(batch, payload).scores` is the same list on a clean response, and the retry decision
moves from "did it raise" to `Reconciliation.verdict`. Nothing in `lib/common.py` is edited — the
Phase-1.1 artefacts stay exactly as measured.
"""

from __future__ import annotations

import re
from dataclasses import dataclass, field
from typing import Any, Callable, Iterable

CID_RE = re.compile(r"^[0-9a-f]{12}$")

#: Never loop. One initial call plus at most this many retries, then the batch fails, recorded.
MAX_RETRIES = 2

#: What a reconciliation tells the driver to do next.
COMPLETE = "complete"        # every expected cid satisfied
INVALID = "invalid"          # conflicting duplicates: this response cannot be trusted at all
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


def reconcile(batch: dict, payload: Any) -> Reconciliation:
    """Partition a batch response against `batch['items']`. Never raises on model output."""
    want = [item["cid"] for item in batch["items"]]
    want_set = set(want)
    known = {criterion["id"] for criterion in batch["sub_criteria"]}

    rec = Reconciliation(verdict=INVALID)
    rows = payload.get("scores") if isinstance(payload, dict) else None
    if not isinstance(rows, list):
        rec.note("no_scores_array", got=type(payload).__name__)
        rec.missing = list(want)
        rec.reason = "no scores array"
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

    # 2. Duplicates of an expected cid. Same score -> keep one. Different scores -> the response
    #    is self-contradictory about a judgement, which is the one case worth another call.
    conflicting: list[str] = []
    chosen: dict[str, dict] = {}
    for cid, group in by_cid.items():
        if len(group) > 1:
            scores = {row.get("score") for row in group}
            if len(scores) > 1:
                conflicting.append(cid)
                rec.note("duplicate_conflicting", cid=cid, scores=sorted(map(str, scores)))
                continue
            rec.note("duplicate_identical_collapsed", cid=cid, copies=len(group),
                     score=group[0].get("score"))
        chosen[cid] = group[0]

    if conflicting:
        rec.verdict = INVALID
        rec.missing = list(want)
        rec.reason = f"conflicting duplicate scores for {sorted(conflicting)}"
        return rec

    # 3. Field contract, per row. A bad row costs its own cid, not the batch.
    for cid in want:
        row = chosen.get(cid)
        if row is None:
            rec.missing.append(cid)
            continue
        clean, why = _validate_row(row, known)
        if clean is None:
            rec.note("row_rejected", cid=cid, why=why)
            rec.missing.append(cid)
            continue
        rec.scores.append(clean)

    rec.verdict = COMPLETE if not rec.missing else INCOMPLETE
    rec.reason = "" if not rec.missing else f"{len(rec.missing)} cid(s) unsatisfied"
    return rec


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

        rec = reconcile(ask, payload)
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

        outcome.reason = f"{len(owed)} cid(s) unsatisfied"
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
