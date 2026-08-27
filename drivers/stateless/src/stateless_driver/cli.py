"""`python -m stateless_driver --run <run-dir>` — screen one run's outstanding batches.

Reads `brief.md` and `screen-batches/*.json` from a Research Scan run directory, screens each
batch through one stateless call, and writes the accepted judgements to `screen.json` — the file
the agent owns in the conversational path, produced here by an engine instead. Everything the
engine produced, and everything it cost, is written under `<run>/engine/<stamp>/`.

`research-scan shortlist` remains the authority on the result: it re-validates `screen.json`
against the package's own contract and exits 2 on anything this driver let through.
"""

from __future__ import annotations

import argparse
import json
import logging
import os
import sys
import time
from pathlib import Path

from stateless_driver import accept, prompt, provenance
from stateless_driver import engine as engine_module

log = logging.getLogger("stateless_driver")

#: The skill's own rubric, when the driver is run from a checkout. `--rubric` overrides it.
DEFAULT_RUBRIC = (
    Path(__file__).resolve().parents[4] / "skills/research-scan/references/screen-rubric.md"
)


def read_batches(run_dir: Path, pattern: str) -> dict[str, dict]:
    return {
        path.stem: json.loads(path.read_text(encoding="utf-8"))
        for path in sorted((run_dir / "screen-batches").glob(pattern))
    }


def outstanding(batches: dict[str, dict], scored: set[str]) -> dict[str, dict]:
    """Batches with an unscored item. A batch already covered by `screen.json` is not re-bought."""
    return {
        bid: batch
        for bid, batch in batches.items()
        if any(item["cid"] not in scored for item in batch["items"])
    }


def merge(run_dir: Path, existing: list[dict], accepted: list[dict]) -> list[dict]:
    """Accepted rows over existing ones, ordered by `candidates.json` when the run has one."""
    rows = {row["cid"]: row for row in existing}
    rows.update({row["cid"]: row for row in accepted})
    candidates = run_dir / "candidates.json"
    if not candidates.is_file():
        return list(rows.values())
    order = [
        entry["cid"] for entry in json.loads(candidates.read_text(encoding="utf-8"))["candidates"]
    ]
    known = set(order)
    # A row for a cid this run never retrieved cannot enter pipeline state, whatever produced it.
    stray = sorted(cid for cid in rows if cid not in known)
    if stray:
        raise SystemExit(
            f"refusing to write: {len(stray)} scored cid(s) are not in candidates.json: {stray[:5]}"
        )
    return [rows[cid] for cid in order if cid in rows]


def write_json(path: Path, payload: object) -> None:
    path.parent.mkdir(parents=True, exist_ok=True)
    path.write_text(json.dumps(payload, indent=1, ensure_ascii=False), encoding="utf-8")


def parse_args(argv: list[str] | None = None) -> argparse.Namespace:
    parser = argparse.ArgumentParser(prog="stateless_driver", description=__doc__)
    parser.add_argument("--run", required=True, help="Research Scan run directory.")
    parser.add_argument("--rubric", default=str(DEFAULT_RUBRIC), help="Screening rubric markdown.")
    parser.add_argument("--model", default=engine_module.DEFAULT_MODEL)
    parser.add_argument("--effort", default=engine_module.DEFAULT_EFFORT)
    parser.add_argument("--max-tokens", type=int, default=engine_module.DEFAULT_MAX_TOKENS)
    parser.add_argument(
        "--max-concurrency", type=int, default=engine_module.DEFAULT_MAX_CONCURRENCY
    )
    parser.add_argument("--batches", default="*.json", help="Glob inside `screen-batches/`.")
    parser.add_argument("--all", action="store_true", help="Re-screen batches already scored.")
    parser.add_argument("--no-cache", action="store_true", help="Do not cache the stable prefix.")
    parser.add_argument(
        "--dry-run",
        action="store_true",
        help="Write the provenance record and the plan; make no calls and spend nothing.",
    )
    parser.add_argument("--log-level", default="INFO")
    return parser.parse_args(argv)


def main(argv: list[str] | None = None) -> int:
    args = parse_args(argv)
    logging.basicConfig(
        level=args.log_level.upper(), format="%(levelname)s %(message)s", stream=sys.stderr
    )

    run_dir = Path(args.run).expanduser().resolve()
    brief = (run_dir / "brief.md").read_text(encoding="utf-8")
    rubric = Path(args.rubric).read_text(encoding="utf-8")
    system = prompt.system_text(prompt.purpose_line(brief), brief, rubric)

    screen_path = run_dir / "screen.json"
    existing = (
        json.loads(screen_path.read_text(encoding="utf-8"))["scores"]
        if screen_path.is_file()
        else []
    )
    batches = read_batches(run_dir, args.batches)
    todo = batches if args.all else outstanding(batches, {row["cid"] for row in existing})

    record = provenance.build(
        model_id=args.model,
        rubric=rubric,
        brief=brief,
        effort=args.effort,
        thinking=engine_module.THINKING,
        sampling=provenance.Sampling(max_tokens=args.max_tokens),
        max_concurrency=args.max_concurrency,
        prompt_cache=not args.no_cache,
    )
    out_dir = run_dir / "engine" / time.strftime("%Y%m%dT%H%M%SZ", time.gmtime())
    write_json(out_dir / "provenance.json", record.as_dict())
    log.info(
        "%d batch(es) outstanding of %d · model %s · effort %s · thinking %s · concurrency %d",
        len(todo),
        len(batches),
        args.model,
        args.effort,
        engine_module.THINKING,
        args.max_concurrency,
    )

    if args.dry_run:
        plan = {bid: len(batch["items"]) for bid, batch in todo.items()}
        write_json(out_dir / "plan.json", {"batches": plan})
        log.info("dry run: no calls made, provenance written to %s", out_dir)
        return 0
    if not todo:
        log.info("nothing outstanding; screen.json already covers every batch")
        return 0

    key = os.environ.get("ANTHROPIC_API_KEY")
    if not key:
        raise SystemExit("ANTHROPIC_API_KEY is not set")
    import anthropic

    engine = engine_module.Engine(
        client=anthropic.Anthropic(api_key=key, timeout=900.0, max_retries=2),
        system=system,
        model=args.model,
        effort=args.effort,
        max_tokens=args.max_tokens,
        prompt_cache=not args.no_cache,
    )

    started = time.monotonic()
    outcomes = engine_module.screen(engine, todo, max_concurrency=args.max_concurrency)
    wall = time.monotonic() - started

    record.model_resolved = sorted(engine.models_seen)
    accepted = accept.attach(record.as_dict(), outcomes)
    write_json(out_dir / "provenance.json", record.as_dict())
    write_json(out_dir / "accepted.json", accepted.as_dict())
    (out_dir / "calls.jsonl").write_text(
        "".join(json.dumps(call) + "\n" for call in engine.calls), encoding="utf-8"
    )

    failed = [outcome.batch for outcome in outcomes if not outcome.ok]
    summary = {
        "run_dir": str(run_dir),
        "batches": len(todo),
        "batches_failed": failed,
        "accepted_rows": len(accepted.scores),
        "unsatisfied_cids": sorted(cid for outcome in outcomes for cid in outcome.missing),
        "wall_seconds": round(wall, 2),
        "usage": engine.usage.as_dict(),
    }
    write_json(out_dir / "summary.json", summary)

    merged = merge(run_dir, existing, accepted.scores)
    write_json(screen_path, {"scores": merged})
    log.info(
        "wrote %d score(s) to %s · %d call(s) in %.1fs · artefacts in %s",
        len(merged),
        screen_path,
        engine.usage.calls,
        wall,
        out_dir,
    )
    if failed:
        log.error("%d batch(es) failed on the record: %s", len(failed), ", ".join(failed))
        log.error("screen.json is short of %d cid(s)", len(summary["unsatisfied_cids"]))
        return 1
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
