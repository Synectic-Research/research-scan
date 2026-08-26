"""Phase-1.2C — the rerank chunk loop with `contract.py`'s sub-batch re-ask wired in.

**No model is called by this slice.** This is the call path the next slice that spends tokens
should use in place of `rerank.py::call`. Everything that decides an answer — model, effort,
thinking, prompt, `entry_schema`/`output_schema`, `record_payload`, `cut`, `RERANK_CHUNK`,
`MAX_ATTEMPTS`, the ledger — is imported from the frozen Phase-1.1 driver and never
re-implemented here. `phase11-golden/rerank.py` is a measurement of record and is not edited.

What changes is one block: `rerank.py:169-176` validated the decoded array all-or-nothing —

    want = {r["cid"] for r in rows}
    got  = {r["cid"] for r in ranked}
    if got != want: raise ValueError("cid mismatch …")       # re-issue the whole chunk

— and Phase-1.2B recorded that predicate discarding nine correct RankedEntries because the
decoder padded the array with `5716814f6adf_placeholder` and dropped four real cids with it.
Here the same response is reconciled: the nine are banked, the ghost is discarded without
earning a retry, and only the four still owed are re-asked as a sub-batch.
"""
from __future__ import annotations

import importlib.util
import json
import sys
import time
from pathlib import Path

HERE = Path(__file__).resolve().parent
P11 = HERE.parents[1] / "phase11-golden"
sys.path.insert(0, str(HERE))
sys.path.insert(0, str(P11))

import rerank_contract  # noqa: E402


def frozen_rerank():
    """Load `phase11-golden/rerank.py` for its prompt, schema, payload and cut. Read, never run."""
    spec = importlib.util.spec_from_file_location("p11_rerank", P11 / "rerank.py")
    mod = importlib.util.module_from_spec(spec)
    spec.loader.exec_module(mod)
    return mod


def make_batch(tag: str, rows: list[dict], sub_criteria: list[dict]) -> dict:
    """One chunk, in the shape `contract.reconcile` reconciles against.

    `items` are the frozen driver's own `record_payload` rows, so a sub-batch re-ask sends the
    identical record text for the cids it still owes — a narrowed ask, not a different one.
    """
    RR = frozen_rerank()
    return {
        "batch": tag,
        "items": [RR.record_payload(r) for r in rows],
        "sub_criteria": list(sub_criteria),
    }


def user_message(items: list[dict]) -> str:
    """`rerank.py::call`'s user turn, regenerated from whatever `items` the batch now holds."""
    return (
        f"Rerank these {len(items)} shortlisted records. Score every sub-criterion for each.\n\n"
        "```json\n" + json.dumps(items, ensure_ascii=False, indent=1) + "\n```"
    )


def api_caller(client, C, system, criteria_ids, tag: str, results: list):
    """Return the `call(batch) -> payload` closure `rerank_chunk` drives.

    Cost, cap check and `CallResult` bookkeeping stay exactly the frozen driver's. Decoding
    stops at `json.loads`: validation is the reconciliation's job now, so a malformed row no
    longer costs the chunk.
    """
    RR = frozen_rerank()
    attempt = {"n": 0}

    def call(batch: dict):
        attempt["n"] += 1
        sub_tag = f"{tag}/a{attempt['n']}" if attempt["n"] > 1 else tag
        C.check_cap(0.80)
        t0 = time.monotonic()
        with client.messages.stream(
            model=C.MODEL,
            max_tokens=C.RERANK_MAX_TOKENS,
            system=system,
            messages=[{"role": "user", "content": user_message(batch["items"])}],
            thinking={"type": "adaptive"},
            output_config={"effort": C.EFFORT,
                           "format": {"type": "json_schema",
                                      "schema": RR.output_schema(criteria_ids)}},
        ) as stream:
            message = stream.get_final_message()
        dt = time.monotonic() - t0
        C.record(sub_tag, message.usage.model_dump(), C.cost_of(message.usage), dt)
        results.append(C.result_from(sub_tag, message, dt, attempt["n"]))
        return json.loads(next(b.text for b in message.content if b.type == "text"))

    return call


def rerank_chunk(batch: dict, call, **kw):
    """Thin re-export so a driver imports one name from one module."""
    return rerank_contract.rerank_chunk(batch, call, **kw)
