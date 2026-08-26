"""Phase-1.2C — the recorded Phase-1.2B rerank failure, reconstructed as a test fixture.

Reconstructed from artefacts, not invented. Each field below is quoted from a recorded file:

  chunk cids      `phase12b/runs/p11-t1/R15/O1/rep2/summary.json` → `sent_order[:13]`
                  (`lib/common.RERANK_CHUNK = 13`)
  the failure     `phase12b/runs/p11-t1/R15/O1/rep2/calls.json` → `attempt_errors[0]`:
                  "ValueError: cid mismatch: missing=['27753f3a0af1', '3b4211254cf6',
                   '5a5e499f6ec3', '9e3699988af6'] extra=['5716814f6adf_placeholder']"
                  and `attempts: 2`, `schema_failure: true` — one wasted whole-chunk re-issue.
  criterion ids   `phase12b/runs/p11-t1/…/run/queries.json` → C1…C6

The response *bodies* were not recorded — only the cid partition was. The nine surviving rows
are therefore synthesised as well-formed RankedEntries; every assertion in the test suite is
about the cid partition and the retry decision, which are exactly what the record fixes.
"""
from __future__ import annotations

import json
from pathlib import Path

HERE = Path(__file__).resolve().parent
REP2 = HERE.parent / "phase12b" / "runs" / "p11-t1" / "R15" / "O1" / "rep2"
RERANK_CHUNK = 13                      # lib/common.RERANK_CHUNK, frozen

#: The exact four cids the recorded call dropped, and the exact ghost it added.
RECORDED_MISSING = ["27753f3a0af1", "3b4211254cf6", "5a5e499f6ec3", "9e3699988af6"]
RECORDED_GHOST = "5716814f6adf_placeholder"


def chunk_cids() -> list[str]:
    return json.loads((REP2 / "summary.json").read_text())["sent_order"][:RERANK_CHUNK]


def criteria_ids() -> list[str]:
    return [c["id"] for c in sub_criteria()]


def sub_criteria() -> list[dict]:
    return json.loads((REP2 / "run" / "queries.json").read_text())["sub_criteria"]


def entry(cid: str, ids: list[str], *, overall: int = 2, **over) -> dict:
    """A well-formed RankedEntry, the shape `rerank.py::entry_schema` requires."""
    row = {
        "cid": cid,
        "criteria": {c: 2 for c in ids},
        "overall": overall,
        "evidence_level": "experimental",
        "relation": "closely-related",
        "flags": {"review": False, "contradicts": False, "methods_paper": False},
        "key_finding": f"finding for {cid}",
        "methodology": f"methodology for {cid}",
        "why_it_matters": f"why {cid} matters",
        "limitations": ["a stated limitation"],
        "relevance_reason": f"relevance of {cid}",
    }
    row.update(over)
    return row


def batch() -> dict:
    """The failing chunk, as `contract.reconcile` reconciles against it."""
    return {"batch": "rr/defaults-savings/R15/O1/r2/c1",
            "items": [{"cid": c} for c in chunk_cids()],
            "sub_criteria": sub_criteria()}


def x02_payload() -> dict:
    """The recorded response: nine of the thirteen wanted cids, plus the `_placeholder` ghost."""
    ids = criteria_ids()
    kept = [c for c in chunk_cids() if c not in RECORDED_MISSING]
    rows = [entry(c, ids) for c in kept]
    ghost = entry(RECORDED_GHOST, ids)
    ghost["relevance_reason"] = "duplicate placeholder"
    rows.append(ghost)
    return {"ranked": rows}


def clean_payload(cids: list[str] | None = None) -> dict:
    ids = criteria_ids()
    return {"ranked": [entry(c, ids) for c in (cids or chunk_cids())]}
