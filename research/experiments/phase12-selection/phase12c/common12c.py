"""Phase-1.2C — shared loading and joins for the offline tie-break replay.

Everything here reads recorded artefacts only. No model is called, nothing under `src/`,
`skills/` or `eval/` is written, and the shipped `research_scan.select` module is imported
rather than re-implemented: the slot rules (diversity cap, review/contradicting guarantees,
foundational reserve, backfill) are replayed *unchanged* in every ladder and only
`select.order_key` is swapped.
"""
from __future__ import annotations

import json
import sys
import types
from dataclasses import dataclass
from pathlib import Path

HERE = Path(__file__).resolve().parent
P12 = HERE.parent
P12B = P12 / "phase12b"
REPO = P12.parents[2]

sys.path.insert(0, str(P12B))
sys.path.insert(0, str(P12))
sys.path.insert(0, str(REPO / "research/experiments/phase11-golden"))
sys.modules.setdefault("anthropic", types.ModuleType("anthropic"))

SLUGS = {"defaults-savings": "p11-t1", "llm-lit-search": "p11-t2"}
BASELINE_RECALL10 = {"defaults-savings": 5, "llm-lit-search": 3}
ARMS = ("R15", "R20", "R25", "R40")
ORDERINGS = ("O1", "O2", "O3")


@dataclass(frozen=True)
class Run:
    """One recorded rerank run, with everything the replay needs already joined."""

    topic: str
    arm: str
    ordering: str
    rep: int
    run_dir: Path
    summary: dict

    @property
    def key(self) -> str:
        return f"{self.topic}/{self.arm}/{self.ordering}/rep{self.rep}"

    def load(self, name: str) -> object:
        return json.loads((self.run_dir / name).read_text())


def runs() -> list[Run]:
    out: list[Run] = []
    for topic, slug in SLUGS.items():
        for arm in ARMS:
            for ordering in ORDERINGS:
                base = P12B / "runs" / slug / arm / ordering
                if not base.is_dir():
                    continue
                for d in sorted(base.glob("rep*"), key=lambda p: int(p.name[3:])):
                    f = d / "summary.json"
                    if not f.is_file():
                        continue
                    summary = json.loads(f.read_text())
                    out.append(
                        Run(topic, arm, ordering, int(d.name[3:]),
                            REPO / summary["run_dir"], summary)
                    )
    return out


def shortlist(topic: str) -> dict:
    """The T1@40 shortlist this whole slice was reranked from (Phase-1.2B `build_shortlists.py`)."""
    return json.loads((P12B / "shortlists" / f"{SLUGS[topic]}-T1at40.json").read_text())


def t1_rank(topic: str) -> dict[str, int]:
    """cid -> 1-based rank in the T1 shortlist order. Unique by construction, so every ladder
    that terminates in it is a total order and every replay is deterministic."""
    sl = shortlist(topic)
    rows = list(sl["in_window"]) + list(sl["outside_window"])
    return {r["cid"]: i for i, r in enumerate(rows, start=1)}


def shortlist_features(topic: str) -> dict[str, dict]:
    """cid -> the 1.1/1.2A features the shortlist row carries: screen score,
    criteria_supported, origin_count, best_retrieval_rank, date, outside_window."""
    sl = shortlist(topic)
    out: dict[str, dict] = {}
    for bucket in ("in_window", "outside_window"):
        for row in sl[bucket]:
            origins = row.get("origins") or []
            ranks = [o.get("rank") for o in origins if isinstance(o, dict) and o.get("rank")]
            out[row["cid"]] = {
                "screen_score": row.get("score"),
                "criteria_supported": row.get("criteria_supported"),
                "origin_count": len(origins),
                "best_retrieval_rank": min(ranks) if ranks else None,
                "publication_date": row.get("publication_date"),
                "outside_window": bool(row.get("outside_window")),
            }
    return out
