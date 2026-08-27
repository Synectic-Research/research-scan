"""Phase-1.4 — one replicate of one cell, end to end.

Frozen and imported, never re-implemented: model, effort, thinking, `record_payload`, the user turn,
the stratified `cut`, `RERANK_CHUNK`, attempt policy, the cost model, the T1@40 shortlist and its
canonical (O1) ordering, `verify`, `emit` and every slot rule in `research_scan.select`.

Varied: the rerank rubric text (the 2x2), and — in the S cells only — one wire field and the
ordering key the top tier is read under.

Each replicate writes, under `runs/<slug>/<cell>/rep<N>/`:

    run/                the materialised run directory (`ranked.json`, `evidence.json`, …)
    run/priority.json   cid -> priority_rank, S cells only; never inside `ranked.json`
    summary.json        the cell's own selection, plus the shipped-key selection over the same rows
    calls.json          per-call usage and cost

Both selections are recorded for every cell. In C0 and C they must be identical to each other and
to what the CLI's `emit` wrote — asserted per run, which is this slice's control validation. In S
and SC the difference between them is the decomposition that says whether a change came from the
rubric moving the judgements or from `priority_rank` moving the selection.

Usage:
    run14.py plan
    run14.py run <topic> <cell> <rep>
"""

from __future__ import annotations

import argparse
import fcntl
import json
import os
import shutil
import sys
import time
from pathlib import Path

HERE = Path(__file__).resolve().parent
P12 = HERE.parent / "phase12-selection"
P12B = P12 / "phase12b"
REPO = HERE.parents[2]
P11 = REPO / "research/experiments/phase11-golden"
sys.path.insert(0, str(HERE))
sys.path.insert(0, str(P11))

from lib import common as C  # noqa: E402

# --- own ledger and cap. Phases 1.1 and 1.2B keep their measurements of record untouched.
C.LEDGER = HERE / "results" / "spend.json"
# Raised from $30.00 for stage 2: stage 1 spent $17.2796 and the 16-run extension projects to
# ~$28.8, which falls inside `check_cap`'s 0.80 look-ahead against the old cap and would have
# aborted a replicate mid-chunk. A budget guard, not a pre-registered threshold.
C.SPEND_CAP_USD = 33.00
C.LEDGER.parent.mkdir(parents=True, exist_ok=True)


def _locked_record(tag: str, usage: dict, cost: float, seconds: float) -> None:
    """`C.record` under an flock, so parallel topic streams cannot lose each other's writes."""
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

import anthropic  # noqa: E402
import contract14  # noqa: E402
import driver14  # noqa: E402
import select14  # noqa: E402
import variants  # noqa: E402

from research_scan.schema import CandidatesFile, Ranked  # noqa: E402

ARM = "R40"
CUT = 40
ORDERING = "O1"           # the frozen canonical candidate ordering; 1.2B's order probe is closed
POLICY = "T1@40"
SLUGS = {"defaults-savings": "p11-t1", "llm-lit-search": "p11-t2"}
NEEDED = ("brief.md", "purpose.json", "queries.json", "manifest.json", "coverage.json")


# ----------------------------------------------------------------- materialisation


def materialise(topic: str, cell: str, rep: int) -> tuple[Path, dict]:
    slug = SLUGS[topic]
    src = P11 / "runs" / slug
    base = HERE / "runs" / slug / cell / f"rep{rep}"
    run = base / "run"
    if run.exists():
        shutil.rmtree(run)
    run.mkdir(parents=True)
    for name in NEEDED:
        if (src / name).is_file():
            shutil.copy2(src / name, run / name)
    os.link(src / "candidates.json", run / "candidates.json")   # 3-4 MB, read-only everywhere

    shortlist = json.loads(
        (P12B / "shortlists" / f"{slug}-{POLICY.replace('@', 'at')}.json").read_text())
    (run / "shortlist.json").write_text(json.dumps(shortlist, indent=1))

    manifest = json.loads((run / "manifest.json").read_text())
    manifest["run"]["run_dir"] = str(run)
    manifest["run"]["brief_path"] = str(run / "brief.md")
    (run / "manifest.json").write_text(json.dumps(manifest, indent=1))
    return run, shortlist


def pairs_for(run: Path):
    """(candidate, entry) in `ranked.json` order — exactly what `cli.emit` builds (cli.py:762)."""
    ranked = Ranked.model_validate(json.loads((run / "ranked.json").read_text()))
    candidates = CandidatesFile.model_validate(json.loads((run / "candidates.json").read_text()))
    by_cid = {c.cid: c for c in candidates.candidates}
    return [(by_cid[e.cid], e) for e in ranked.root]


# ----------------------------------------------------------------- one replicate


def one(topic: str, cell: str, rep: int) -> dict:
    if cell not in variants.CELLS:
        raise SystemExit(f"unknown cell {cell!r}; expected one of {variants.CELLS}")
    bad = variants.check_contamination()
    if bad:
        raise SystemExit(f"contamination check failed: {bad}")

    priority_on = variants.uses_priority_rank(cell)
    run, shortlist = materialise(topic, cell, rep)
    queries = json.loads((run / "queries.json").read_text())
    criteria_ids = [c["id"] for c in queries["sub_criteria"]]
    driver14.assert_control_prompt_identical(run, queries, C)

    RR = driver14.frozen_rerank()
    in_rows, out_rows = RR.cut(shortlist, CUT)
    rows = in_rows + out_rows                     # O1: the canonical order, unpermuted

    tag_base = f"p14/{topic}/{cell}/r{rep}"
    print(f"{tag_base}: shortlist {len(shortlist['in_window'])}+{len(shortlist['outside_window'])}"
          f" -> {len(in_rows)}+{len(out_rows)}={len(rows)}  rubric={variants.digest(cell)}"
          f"  priority={'on' if priority_on else 'off'}  ledger ${C.spent():.4f}")

    client = anthropic.Anthropic(api_key=C.env_key(), timeout=1800.0, max_retries=2)
    system = driver14.system_blocks(run, queries, cell, C)
    results, ranked_all, priority, provenance = [], [], {}, []
    t0 = time.monotonic()
    for i in range(0, len(rows), C.RERANK_CHUNK):
        chunk = rows[i:i + C.RERANK_CHUNK]
        tag = f"{tag_base}/c{i // C.RERANK_CHUNK + 1}"
        batch = driver14.make_batch(tag, chunk, queries["sub_criteria"])
        call = driver14.api_caller(client, C, system, criteria_ids, tag, results,
                                   priority=priority_on)
        outcome = driver14.rerank_chunk(batch, call, priority=priority_on)
        provenance.append({"batch": tag, "ok": outcome.ok, "attempts": outcome.attempts,
                           "missing": outcome.missing, "reason": outcome.reason,
                           "provenance": outcome.provenance})
        entries, ranks = contract14.strip_priority(outcome.scores)
        ranked_all.extend(entries)
        priority.update(ranks)
        print(f"  {tag}  ok={outcome.ok} attempts={outcome.attempts} "
              f"kept={len(entries)}/{len(chunk)}  ledger ${C.spent():.4f}")
    wall = time.monotonic() - t0

    (run / "ranked.json").write_text(json.dumps(ranked_all, indent=1))
    if priority_on:
        (run / "priority.json").write_text(json.dumps(priority, indent=1))
    ok, msg = C.schema_check(run / "ranked.json", "Ranked")
    vcode, vout = C.run_cli(["research-scan", "verify", "--run", str(run), "--json", "--quiet"])
    ecode, eout = C.run_cli(["research-scan", "emit", "--run", str(run), "--json", "--quiet"])

    manifest = json.loads((run / "manifest.json").read_text())
    top = manifest["defaults"]["top"]
    foundational = manifest["defaults"]["foundational"]

    cell_sel, shipped_sel, emitted_cli = None, None, None
    if ecode == 0 and (run / "evidence.json").exists():
        pairs = pairs_for(run)
        shipped_sel = select14.selection(pairs, select14.shipped_key,
                                         top=top, foundational=foundational)
        cell_sel = select14.selection(pairs, select14.key_for(cell, priority),
                                      top=top, foundational=foundational)
        emitted_cli = [p["cid"] for p in json.loads((run / "evidence.json").read_text())["packets"]]
        # Control validation: the shipped-key replay must reproduce the CLI's own emit, in order.
        if shipped_sel["emitted"] != emitted_cli:
            raise AssertionError(
                f"{tag_base}: shipped-key replay does not reproduce `emit`\n"
                f"  emit:   {emitted_cli}\n  replay: {shipped_sel['emitted']}")
        if not priority_on and cell_sel["emitted"] != emitted_cli:
            raise AssertionError(f"{tag_base}: non-S cell selection diverged from `emit`")

    summary = C.summarise(results)
    summary.update({
        "topic": topic, "cell": cell, "replicate": rep, "arm": ARM, "cut": CUT,
        "ordering": ORDERING, "policy": POLICY,
        "rubric_sha16": variants.digest(cell), "priority_rank": priority_on,
        "reranked": len(ranked_all), "in_window": len(in_rows), "outside_window": len(out_rows),
        "sent_order": [r["cid"] for r in rows],
        "chunks": provenance,
        "chunks_ok": all(p["ok"] for p in provenance),
        "stage_wall_s": round(wall, 2),
        "ranked_schema_valid": ok, "ranked_schema_msg": msg,
        "verify_exit": vcode, "emit_exit": ecode,
        "verify_out": vout.strip()[:400], "emit_out": eout.strip()[:400],
        "priority_map": priority,
        "top10_cids": cell_sel["emitted"] if cell_sel else None,
        "selection_reasons": cell_sel["reasons"] if cell_sel else None,
        "alternates_cids": cell_sel["alternates"] if cell_sel else None,
        "in_window_merit": cell_sel["in_window_merit"] if cell_sel else None,
        "shipped_key_top10_cids": shipped_sel["emitted"] if shipped_sel else None,
        "shipped_key_reasons": shipped_sel["reasons"] if shipped_sel else None,
        "cli_emit_top10_cids": emitted_cli,
        "frontier_tokens": sum(r.input_tokens + r.output_tokens for r in results),
        "cumulative_spend_usd": C.spent(),
        "run_dir": str(run.relative_to(REPO)),
    })
    C.dump_results(run.parent / "calls.json", results)
    C.write_json(run.parent / "summary.json", summary)
    print(f"  -> ${summary['cost_usd']:.4f}  {wall:.0f}s  verify={vcode} emit={ecode}  "
          f"ledger ${C.spent():.4f}")
    return summary


def main() -> None:
    ap = argparse.ArgumentParser()
    ap.add_argument("cmd", choices=["run", "plan"])
    ap.add_argument("topic", nargs="?")
    ap.add_argument("cell", nargs="?")
    ap.add_argument("rep", nargs="?", type=int, default=1)
    args = ap.parse_args()
    if args.cmd == "plan":
        print(json.dumps({
            "topics": list(SLUGS), "cells": list(variants.CELLS), "arm": ARM,
            "ordering": ORDERING, "policy": POLICY, "chunk": C.RERANK_CHUNK,
            "model": C.MODEL, "effort": C.EFFORT,
            "rubric_sha16": {c: variants.digest(c) for c in variants.CELLS},
            "contamination": variants.check_contamination() or "clean",
            "ledger": str(C.LEDGER), "cap_usd": C.SPEND_CAP_USD, "spent": C.spent(),
        }, indent=1))
        return
    one(args.topic, args.cell, args.rep)


if __name__ == "__main__":
    main()
