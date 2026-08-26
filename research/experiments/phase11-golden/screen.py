"""Stateless parallel screening — Phase 1 arm C mechanics, unchanged.

One call per batch. Each call carries only: purpose line, brief, screen rubric, batch payload,
ScreenScore contract. No conversation, no run state, no tools, thinking OFF, effort high,
max_concurrency 8, 3 attempts.

The stable prefix (purpose + brief + rubric + schema) is byte-identical across every call in a
topic, so it sits in `system` behind one ephemeral cache breakpoint. That changes billing, not
content. The first call is issued alone to warm it, then the rest fan out.

`screen.json` is rewritten from every per-batch file on disk after each pass, so a later family
never discards an earlier one's scores.

Usage:  python screen.py <topic> {main|expand|gap|gapexpand}
"""

from __future__ import annotations

import asyncio
import json
import sys
import time
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parent))
from lib import common as C  # noqa: E402

import anthropic  # noqa: E402


def system_blocks(run: Path) -> list[dict]:
    return [{
        "type": "text",
        "text": C.screen_system(run),
        "cache_control": {"type": "ephemeral"},
    }]


def request_kwargs(run: Path, batch: dict) -> dict:
    return {
        "model": C.MODEL,
        "max_tokens": C.MAX_TOKENS,
        "system": system_blocks(run),
        "messages": [{
            "role": "user",
            "content": "Score every item in this batch.\n\n```json\n"
                       + json.dumps(batch, ensure_ascii=False, indent=1) + "\n```",
        }],
        "thinking": {"type": "disabled"},
        "output_config": {
            "effort": C.EFFORT,
            "format": {"type": "json_schema", "schema": C.SCREEN_OUTPUT_SCHEMA},
        },
    }


async def _one(client, sem, run, out_dir, topic, bid, batch) -> C.CallResult:
    async with sem:
        attempts, last_err, schema_fail, errs = 0, "", False, []
        while attempts < C.MAX_ATTEMPTS:
            attempts += 1
            t0 = time.monotonic()
            try:
                C.check_cap(0.20)
                async with client.messages.stream(**request_kwargs(run, batch)) as stream:
                    message = await stream.get_final_message()
                dt = time.monotonic() - t0
                C.record(f"screen/{topic}/{bid}", message.usage.model_dump(),
                         C.cost_of(message.usage), dt)
                try:
                    scores = C.validate_batch_scores(
                        batch, json.loads(next(b.text for b in message.content if b.type == "text"))
                    )
                except Exception:
                    schema_fail = True
                    raise
                C.write_json(out_dir / f"{bid}.json", {"scores": scores})
                res = C.result_from(f"screen/{topic}/{bid}", message, dt, attempts, scores)
                res.schema_failure = schema_fail
                res.attempt_errors = errs
                print(f"  {topic}/{bid}  {dt:6.1f}s  ${res.cost_usd:.4f}  "
                      f"in={res.input_tokens} cr={res.cache_read} out={res.output_tokens}")
                return res
            except C.CapExceeded:
                raise
            except Exception as exc:  # noqa: BLE001
                last_err = f"{type(exc).__name__}: {exc}"
                errs.append(last_err[:400])
                print(f"  {topic}/{bid} attempt {attempts} failed: {last_err[:180]}")
                if attempts < C.MAX_ATTEMPTS:
                    await asyncio.sleep(2 ** attempts)
        return C.CallResult(tag=f"screen/{topic}/{bid}", ok=False, seconds=0.0,
                            attempts=attempts, error=last_err, schema_failure=schema_fail,
                            attempt_errors=errs)


async def run_batches(run, out_dir, topic, batches) -> list[C.CallResult]:
    client = anthropic.AsyncAnthropic(api_key=C.env_key(), timeout=900.0, max_retries=2)
    sem = asyncio.Semaphore(C.MAX_CONCURRENCY)
    ids = list(batches)
    if not ids:
        return []
    first = await _one(client, sem, run, out_dir, topic, ids[0], batches[ids[0]])
    rest = await asyncio.gather(
        *[_one(client, sem, run, out_dir, topic, b, batches[b]) for b in ids[1:]]
    )
    return [first, *rest]


def merge(run: Path, out_dir: Path) -> tuple[int, int]:
    """Rewrite screen.json from every per-batch file so far, in candidates.json order."""
    scores: dict[str, dict] = {}
    for path in sorted(out_dir.glob("*.json")):
        for s in json.loads(path.read_text())["scores"]:
            scores[s["cid"]] = s
    cands = json.loads((run / "candidates.json").read_text())["candidates"]
    ordered = [scores[c["cid"]] for c in cands if c["cid"] in scores]
    (run / "screen.json").write_text(json.dumps({"scores": ordered}, indent=1, ensure_ascii=False))
    return len(ordered), len(cands)


FAMILIES = {"main": "[0-9]*", "expand": "x[0-9]*", "gap": "r[0-9]*", "gapexpand": "xr[0-9]*"}


def main() -> None:
    topic, family = sys.argv[1], sys.argv[2]
    pattern = FAMILIES[family]
    run = C.run_dir(topic)
    out_dir = C.EXP / "screen-batches" / C.TOPICS[topic]["slug"]
    out_dir.mkdir(parents=True, exist_ok=True)

    paths = sorted((run / "screen-batches").glob(f"{pattern}.json"))
    todo = {p.stem: json.loads(p.read_text()) for p in paths if not (out_dir / p.name).exists()}
    print(f"{topic} family {pattern!r}: {len(paths)} batches, {len(todo)} to score, "
          f"spent so far ${C.spent():.4f}")

    t0 = time.monotonic()
    results = asyncio.run(run_batches(run, out_dir, topic, todo)) if todo else []
    wall = time.monotonic() - t0

    n, total = merge(run, out_dir)
    ok, msg = C.schema_check(run / "screen.json", "ScreenFile")

    summary = C.summarise(results)
    summary.update({
        "topic": topic, "family": family, "glob": pattern, "stage_wall_s": round(wall, 2),
        "scored": n, "candidates": total, "complete": n == total,
        "schema_valid": ok, "schema_msg": msg, "cumulative_spend_usd": C.spent(),
    })
    C.dump_results(C.EXP / "stages" / f"screen-calls-{topic}-{family}.json", results)
    C.write_json(C.EXP / "stages" / f"screen-{topic}-{family}.json", summary)
    print(json.dumps({k: v for k, v in summary.items() if k != "failed_tags"}, indent=1))
    if not ok or not summary["complete"]:
        print("WARNING: screen.json incomplete or invalid", file=sys.stderr)


if __name__ == "__main__":
    main()
