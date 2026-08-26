"""Phase-1.2B — sequential rerank-stability driver.

Frozen from Phase 1.1: model, effort, thinking, rerank prompt, RankedEntry schema, chunk size,
attempt policy and the stratified cut are imported from `phase11-golden/rerank.py` and
`phase11-golden/lib/common.py` and never re-implemented here. What this driver adds is:

  * the shortlist comes from Phase-1.2A's T1 policy (`build_shortlists.py`), not the shipped T0;
  * replicates — the same frozen call issued N independent times per cell;
  * deterministic within-band re-orderings (O1/O2/O3) for the order-sensitivity probe;
  * its own spend ledger and cap, so Phase 1.1's ledger of record is not written to.

Usage:
    stability.py run   <topic> <arm> <ordering> <rep>
    stability.py plan                                  # print the cell list, spend nothing
"""

from __future__ import annotations

import argparse
import fcntl
import hashlib
import json
import os
import shutil
import sys
import time
from pathlib import Path

HERE = Path(__file__).resolve().parent
P12 = HERE.parent
REPO = P12.parents[2]
P11 = REPO / "research/experiments/phase11-golden"
sys.path.insert(0, str(P11))

from lib import common as C  # noqa: E402

# --- own ledger and cap. Phase 1.1's spend.json is a measurement of record; never appended to.
C.LEDGER = HERE / "results" / "spend.json"
C.SPEND_CAP_USD = 18.00
C.LEDGER.parent.mkdir(parents=True, exist_ok=True)


def _locked_record(tag: str, usage: dict, cost: float, seconds: float) -> None:
    """`C.record` under an flock, so the two topic streams cannot lose each other's writes.

    Same file, same shape, same rounding as the Phase-1.1 ledger — only the mutual exclusion
    is new, and it is needed because this slice runs two streams against one cap.
    """
    lock = C.LEDGER.with_suffix(".lock")
    lock.touch(exist_ok=True)
    with open(lock, "r+") as fh:
        fcntl.flock(fh, fcntl.LOCK_EX)
        try:
            led = json.loads(C.LEDGER.read_text()) if C.LEDGER.exists() else {
                "total_usd": 0.0, "calls": []}
            led["total_usd"] = round(led["total_usd"] + cost, 6)
            led["calls"].append({"tag": tag, "cost_usd": cost, "seconds": seconds,
                                 "usage": usage, "at": time.time()})
            C.LEDGER.write_text(json.dumps(led, indent=1))
        finally:
            fcntl.flock(fh, fcntl.LOCK_UN)


C.record = _locked_record

import rerank as RR  # noqa: E402  (frozen Phase-1.1 mechanics)

import anthropic  # noqa: E402

ARMS = {"R15": 15, "R20": 20, "R25": 25, "R40": 40, "Rall": 10**6}
ORDERINGS = ("O1", "O2", "O3")
POLICY = "T1@40"          # T1@80 is byte-identical at every arm here — see results/shortlists.json
HASH_SALT = "phase12b-O3"


# ----------------------------------------------------------------- orderings (probe)

def _bands(rows: list[dict]) -> list[list[dict]]:
    """Contiguous runs of equal (screen score, criteria_supported).

    The canonical list is already sorted on those two keys first, so a band is exactly the set
    of rows the shortlist policy considers indistinguishable on its two leading features. No
    row ever crosses a band, so no global shuffle can occur.
    """
    out: list[list[dict]] = []
    last = object()
    for row in rows:
        key = (row.get("score"), row.get("criteria_supported"))
        if key != last:
            out.append([])
            last = key
        out[-1].append(row)
    return out


def reorder(rows: list[dict], ordering: str) -> list[dict]:
    if ordering == "O1":
        return list(rows)
    out: list[dict] = []
    for band in _bands(rows):
        if ordering == "O2":
            out.extend(reversed(band))
        elif ordering == "O3":
            out.extend(sorted(band, key=lambda r: hashlib.sha256(
                (HASH_SALT + r["cid"]).encode()).hexdigest()))
        else:
            raise ValueError(ordering)
    return out


# ----------------------------------------------------------------- run materialisation

NEEDED = ("brief.md", "purpose.json", "queries.json", "manifest.json", "coverage.json")


def materialise(topic: str, arm: str, ordering: str, rep: int) -> tuple[Path, dict]:
    slug = C.TOPICS[topic]["slug"]
    src = P11 / "runs" / slug
    base = HERE / "runs" / slug / arm / ordering / f"rep{rep}"
    run = base / "run"
    if run.exists():
        shutil.rmtree(run)
    run.mkdir(parents=True)
    for name in NEEDED:
        if (src / name).is_file():
            shutil.copy2(src / name, run / name)
    # candidates.json is 3-4 MB and read-only for every stage here: hardlink it.
    os.link(src / "candidates.json", run / "candidates.json")

    shortlist = json.loads(
        (HERE / "shortlists" / f"{slug}-{POLICY.replace('@', 'at')}.json").read_text())
    (run / "shortlist.json").write_text(json.dumps(shortlist, indent=1))

    manifest = json.loads((run / "manifest.json").read_text())
    manifest["run"]["run_dir"] = str(run)
    manifest["run"]["brief_path"] = str(run / "brief.md")
    (run / "manifest.json").write_text(json.dumps(manifest, indent=1))
    return run, shortlist


# ----------------------------------------------------------------- one replicate

def one(topic: str, arm: str, ordering: str, rep: int) -> dict:
    n = ARMS[arm]
    run, shortlist = materialise(topic, arm, ordering, rep)
    queries = json.loads((run / "queries.json").read_text())
    criteria_ids = [c["id"] for c in queries["sub_criteria"]]

    in_rows, out_rows = RR.cut(shortlist, n)          # frozen stratified cut
    canonical = in_rows + out_rows
    rows = reorder(in_rows, ordering) + reorder(out_rows, ordering)
    assert {r["cid"] for r in rows} == {r["cid"] for r in canonical}, "ordering changed the set"

    tag_base = f"rr/{topic}/{arm}/{ordering}/r{rep}"
    print(f"{tag_base}: shortlist {len(shortlist['in_window'])}+"
          f"{len(shortlist['outside_window'])} -> {len(in_rows)}+{len(out_rows)}={len(rows)}"
          f"   ledger ${C.spent():.4f}")

    client = anthropic.Anthropic(api_key=C.env_key(), timeout=1800.0, max_retries=2)
    system = RR.system_blocks(run, queries)
    results, ranked_all = [], []
    t0 = time.monotonic()
    for i in range(0, len(rows), C.RERANK_CHUNK):
        chunk = rows[i:i + C.RERANK_CHUNK]
        res, ranked = RR.call(client, run, f"{tag_base}/c{i // C.RERANK_CHUNK + 1}",
                              system, chunk, criteria_ids)
        results.append(res)
        ranked_all.extend(ranked)
    wall = time.monotonic() - t0

    (run / "ranked.json").write_text(json.dumps(ranked_all, indent=1))
    ok, msg = C.schema_check(run / "ranked.json", "Ranked")
    vcode, vout = C.run_cli(["research-scan", "verify", "--run", str(run), "--json", "--quiet"])
    ecode, eout = C.run_cli(["research-scan", "emit", "--run", str(run), "--json", "--quiet"])

    summary = C.summarise(results)
    summary.update({
        "topic": topic, "arm": arm, "cut": n, "ordering": ordering, "replicate": rep,
        "policy": POLICY,
        "reranked": len(ranked_all), "in_window": len(in_rows), "outside_window": len(out_rows),
        "sent_order": [r["cid"] for r in rows],
        "canonical_order": [r["cid"] for r in canonical],
        "stage_wall_s": round(wall, 2),
        "ranked_schema_valid": ok, "ranked_schema_msg": msg,
        "verify_exit": vcode, "emit_exit": ecode,
        "verify_out": vout.strip()[:400], "emit_out": eout.strip()[:400],
        "frontier_tokens": sum(r.input_tokens + r.output_tokens for r in results),
        "cumulative_spend_usd": C.spent(),
        "run_dir": str(run.relative_to(REPO)),
    })
    if ecode == 0 and (run / "evidence.json").exists():
        ev = json.loads((run / "evidence.json").read_text())
        summary["top10_cids"] = [p["cid"] for p in ev["packets"]]
        summary["selection_reasons"] = [p.get("selection_reason") for p in ev["packets"]]
        summary["alternates_cids"] = [p["cid"] for p in ev.get("alternates", [])]
    C.dump_results(run.parent / "calls.json", results)
    C.write_json(run.parent / "summary.json", summary)
    print(f"  -> ${summary['cost_usd']:.4f}  {wall:.0f}s  verify={vcode} emit={ecode}  "
          f"ledger ${C.spent():.4f}")
    return summary


def main() -> None:
    ap = argparse.ArgumentParser()
    ap.add_argument("cmd", choices=["run", "plan"])
    ap.add_argument("topic", nargs="?")
    ap.add_argument("arm", nargs="?")
    ap.add_argument("ordering", nargs="?", default="O1")
    ap.add_argument("rep", nargs="?", type=int, default=1)
    args = ap.parse_args()
    if args.cmd == "plan":
        print(json.dumps({"topics": list(C.TOPICS), "arms": ARMS, "orderings": ORDERINGS,
                          "policy": POLICY, "ledger": str(C.LEDGER),
                          "cap_usd": C.SPEND_CAP_USD, "spent": C.spent()}, indent=1))
        return
    one(args.topic, args.arm, args.ordering, args.rep)


if __name__ == "__main__":
    main()
