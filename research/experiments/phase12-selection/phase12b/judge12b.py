"""Phase-1.2B judge — the frozen Phase-1.1 judge (Fable 5, effort high, JudgeFile schema),
pointed at this slice's ledger and output directory. No prompt or model change.

Usage: judge12b.py <label> <run-dir> [<label> <run-dir> ...]
"""
from __future__ import annotations

import sys
from pathlib import Path

HERE = Path(__file__).resolve().parent
REPO = HERE.parents[3]
sys.path.insert(0, str(REPO / "research/experiments/phase11-golden"))

from lib import common as C  # noqa: E402

C.LEDGER = HERE / "results" / "spend.json"
C.SPEND_CAP_USD = 18.00
C.EXP = HERE                      # judge writes under phase12b/judge/

import judge as J  # noqa: E402  (frozen)

if __name__ == "__main__":
    J.main()
