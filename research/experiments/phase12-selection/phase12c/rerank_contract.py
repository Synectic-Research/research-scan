"""Phase-1.2C — the rerank stage's wire shape for `contract.py`'s reconciliation.

Phase-1.2B recorded the x02 padding defect on the rerank path: one call in 60 returned
`extra=['5716814f6adf_placeholder']` **while dropping four real cids**, and `rerank.py`'s
all-or-nothing check (`got != want -> raise`, rerank.py:169-176) threw away nine correct
RankedEntries to go and fetch four. Reconciliation keeps the nine and re-asks the four.

Nothing here relaxes the field contract. `_validate_entry` is `rerank.py`'s own post-decode
checks plus its `output_schema` required-fields list, applied to one row instead of to the
array — so a row this module accepts is a row the frozen driver would have accepted.
"""
from __future__ import annotations

import sys
from pathlib import Path
from typing import Any, Callable

P12 = Path(__file__).resolve().parent.parent
sys.path.insert(0, str(P12))
sys.path.insert(0, str(P12.parents[1] / "phase11-golden"))

import contract  # noqa: E402

#: `rerank.py::output_schema` — the array `{"ranked": [...]}` and the field that discriminates
#: a conflicting duplicate (the screening stage's `score`).
RANKED_KEY = "ranked"
RANKED_SCORE_FIELD = "overall"

EVIDENCE_LEVELS = frozenset({
    "systematic-review", "meta-analysis", "rct", "prospective", "observational",
    "experimental", "computational", "qualitative", "other",
})
RELATIONS = frozenset({
    "design-changing", "plan-influencing", "closely-related", "contradicting", "foundational",
})
FLAGS = ("review", "contradicts", "methods_paper")
TEXT_FIELDS = ("key_finding", "methodology", "why_it_matters", "relevance_reason")


def _validate_entry(row: dict, known_criteria: set[str]) -> tuple[dict | None, str]:
    """`rerank.py`'s field contract, unrelaxed, applied to one RankedEntry."""
    crit = row.get("criteria")
    if not isinstance(crit, dict):
        return None, "criteria is not an object"
    missing = sorted(known_criteria - set(crit))
    if missing:
        return None, f"criteria missing {missing}"
    extra = sorted(set(crit) - known_criteria)
    if extra:
        return None, f"unknown criteria ids {extra}"
    for cid_key, grade in crit.items():
        if not isinstance(grade, int) or isinstance(grade, bool) or not 0 <= grade <= 3:
            return None, f"criterion {cid_key} grade {grade!r} out of range"

    overall = row.get("overall")
    if not isinstance(overall, int) or isinstance(overall, bool) or not 0 <= overall <= 3:
        return None, f"overall {overall!r} out of range"
    if row.get("evidence_level") not in EVIDENCE_LEVELS:
        return None, f"evidence_level {row.get('evidence_level')!r} not in the enum"
    if row.get("relation") not in RELATIONS:
        return None, f"relation {row.get('relation')!r} not in the enum"

    flags = row.get("flags")
    if not isinstance(flags, dict) or any(not isinstance(flags.get(f), bool) for f in FLAGS):
        return None, "flags missing a boolean"

    for f in TEXT_FIELDS:
        if not isinstance(row.get(f), str) or not row[f]:
            return None, f"missing {f}"

    # rerank.py:174-176 — an entry with no limitations failed the whole chunk. Now it costs
    # only its own cid.
    lim = row.get("limitations")
    if not isinstance(lim, list) or not lim or any(not isinstance(x, str) or not x for x in lim):
        return None, "empty limitations"

    return {
        "cid": row["cid"],
        "criteria": {k: crit[k] for k in sorted(crit)},
        "overall": overall,
        "evidence_level": row["evidence_level"],
        "relation": row["relation"],
        "flags": {f: flags[f] for f in FLAGS},
        "key_finding": row["key_finding"],
        "methodology": row["methodology"],
        "why_it_matters": row["why_it_matters"],
        "limitations": list(lim),
        "relevance_reason": row["relevance_reason"],
    }, ""


def reconcile(batch: dict, payload: Any) -> contract.Reconciliation:
    """`contract.reconcile`, bound to the rerank wire shape."""
    return contract.reconcile(batch, payload, rows_key=RANKED_KEY,
                              score_field=RANKED_SCORE_FIELD, validate_row=_validate_entry)


def rerank_chunk(
    batch: dict,
    call: Callable[[dict], Any],
    *,
    max_retries: int = contract.MAX_RETRIES,
    supports_sub_batch: bool = True,
) -> contract.BatchOutcome:
    """`contract.screen_batch`, bound to the rerank wire shape.

    `batch` is `{"batch": tag, "items": [record_payload, …], "sub_criteria": [...]}` — `items`
    carry `cid`, which is all reconciliation needs. `outcome.scores` holds the RankedEntries,
    in the batch's own order, exactly as `ranked.json` records them.
    """
    return contract.screen_batch(
        batch, call, max_retries=max_retries, supports_sub_batch=supports_sub_batch,
        rows_key=RANKED_KEY, score_field=RANKED_SCORE_FIELD, validate_row=_validate_entry,
    )
