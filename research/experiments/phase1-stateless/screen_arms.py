"""ARMS B / C / D — replay the saved run's screening through stateless API calls.

  B  stateless sequential, adaptive thinking ON   (closest match to baseline behaviour)
  C  stateless parallel (max_concurrency 8), thinking OFF
  D  C's mechanics, batches re-cut in deterministic priority order; nothing is skipped

Every call carries exactly one batch: the brief, the screen rubric, the purpose line, the
batch payload and the ScreenScore contract. No conversation, no run state, no tools.

The stable half of that context (brief + rubric + purpose + schema) is byte-identical across
all 24 calls, so it goes in `system` behind one ephemeral cache breakpoint. That changes
billing, not content; `--no-cache` measures the uncached counterfactual.

Usage:  python screen_arms.py {B|C|D} [--no-cache] [--limit N]
"""

from __future__ import annotations

import argparse
import asyncio
import json
import math
import sys
import time
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parent))
from lib import common as C  # noqa: E402

import anthropic  # noqa: E402

MAX_CONCURRENCY = 8
MAX_ATTEMPTS = 3  # first attempt + 2 retries, per the slice's failure rule
BATCH_SIZE = 25  # the batch size the baseline run used


# --------------------------------------------------------------------------- prompt


def system_blocks(use_cache: bool) -> list[dict]:
    """The stable prefix: identical for every batch in every arm."""
    text = f"""You are screening one batch of retrieved papers for a research-scan run.
Score every item in the batch you are given. You have no memory of other batches and need none.

{C.purpose_line()}

# The brief

{C.brief_text()}

# The screening rubric

{C.screen_rubric()}

# The contract for each entry you return

Return a JSON object `{{"scores": [...]}}` with exactly one entry per item in the batch,
each entry matching this `ScreenScore` schema:

```json
{json.dumps(C.SCREEN_ENTRY_SCHEMA, indent=1)}
```

Copy each `cid` verbatim from the batch. Score every item. Never invent or omit a cid.
`criteria_hit` lists ids from the batch's own `sub_criteria` block; it is required on a
score of 2 or 3 and must be empty on 0 and 1.
"""
    block: dict = {"type": "text", "text": text}
    if use_cache:
        block["cache_control"] = {"type": "ephemeral"}
    return [block]


def user_content(batch: dict) -> str:
    return (
        "Score every item in this batch.\n\n```json\n"
        + json.dumps(batch, ensure_ascii=False, indent=1)
        + "\n```"
    )


def request_kwargs(batch: dict, thinking_on: bool, use_cache: bool) -> dict:
    return {
        "model": C.MODEL,
        "max_tokens": C.MAX_TOKENS,
        "system": system_blocks(use_cache),
        "messages": [{"role": "user", "content": user_content(batch)}],
        "thinking": {"type": "adaptive"} if thinking_on else {"type": "disabled"},
        "output_config": {
            "effort": C.EFFORT,
            "format": {"type": "json_schema", "schema": C.SCREEN_OUTPUT_SCHEMA},
        },
    }


def parse(message) -> dict:
    text = next(b.text for b in message.content if b.type == "text")
    return json.loads(text)


def result_from(tag, message, seconds, attempts, scores) -> C.CallResult:
    u = message.usage
    return C.CallResult(
        tag=tag,
        ok=True,
        seconds=seconds,
        input_tokens=u.input_tokens or 0,
        output_tokens=u.output_tokens or 0,
        thinking_tokens=C.thinking_tokens(u),
        cache_read=u.cache_read_input_tokens or 0,
        cache_write=u.cache_creation_input_tokens or 0,
        cost_usd=C.cost_of(u),
        attempts=attempts,
        scores=scores,
    )


# --------------------------------------------------------------------------- arm B


def run_sequential(batches: dict[str, dict], out_dir: Path, use_cache: bool) -> list[C.CallResult]:
    client = anthropic.Anthropic(api_key=C.env_key(), timeout=900.0, max_retries=2)
    results: list[C.CallResult] = []
    for bid, batch in batches.items():
        C.check_cap(0.20)
        attempts, last_err = 0, ""
        while attempts < MAX_ATTEMPTS:
            attempts += 1
            t0 = time.monotonic()
            try:
                with client.messages.stream(**request_kwargs(batch, True, use_cache)) as stream:
                    message = stream.get_final_message()
                dt = time.monotonic() - t0
                C.record(f"B/{bid}", message.usage.model_dump(), C.cost_of(message.usage), dt)
                scores = C.validate_batch_scores(batch, parse(message))
                res = result_from(f"B/{bid}", message, dt, attempts, scores)
                C.write_json(out_dir / "batches" / f"{bid}.json", {"scores": scores})
                results.append(res)
                print(f"  B/{bid}  {dt:6.1f}s  ${res.cost_usd:.4f}  "
                      f"in={res.input_tokens} cr={res.cache_read} out={res.output_tokens} "
                      f"(think {res.thinking_tokens})")
                break
            except Exception as exc:  # noqa: BLE001
                last_err = f"{type(exc).__name__}: {exc}"
                print(f"  B/{bid}  attempt {attempts} failed: {last_err[:160]}")
                if attempts < MAX_ATTEMPTS:
                    time.sleep(2 ** attempts)
        else:
            results.append(C.CallResult(tag=f"B/{bid}", ok=False, seconds=0.0,
                                        attempts=attempts, error=last_err))
    return results


# --------------------------------------------------------------------------- arms C/D


async def _one(client, sem, arm, bid, batch, out_dir, use_cache) -> C.CallResult:
    async with sem:
        attempts, last_err = 0, ""
        while attempts < MAX_ATTEMPTS:
            attempts += 1
            t0 = time.monotonic()
            try:
                C.check_cap(0.20)
                async with client.messages.stream(
                    **request_kwargs(batch, False, use_cache)
                ) as stream:
                    message = await stream.get_final_message()
                dt = time.monotonic() - t0
                C.record(f"{arm}/{bid}", message.usage.model_dump(),
                         C.cost_of(message.usage), dt)
                scores = C.validate_batch_scores(batch, parse(message))
                # idempotent per-batch output: a retry rewrites exactly this one file
                C.write_json(out_dir / "batches" / f"{bid}.json", {"scores": scores})
                res = result_from(f"{arm}/{bid}", message, dt, attempts, scores)
                print(f"  {arm}/{bid}  {dt:6.1f}s  ${res.cost_usd:.4f}  "
                      f"in={res.input_tokens} cr={res.cache_read} out={res.output_tokens}")
                return res
            except C.CapExceeded:
                raise
            except Exception as exc:  # noqa: BLE001
                last_err = f"{type(exc).__name__}: {exc}"
                print(f"  {arm}/{bid}  attempt {attempts} failed: {last_err[:160]}")
                if attempts < MAX_ATTEMPTS:
                    await asyncio.sleep(2 ** attempts)
        return C.CallResult(tag=f"{arm}/{bid}", ok=False, seconds=0.0,
                            attempts=attempts, error=last_err)


async def run_parallel(arm, batches, out_dir, use_cache) -> list[C.CallResult]:
    client = anthropic.AsyncAnthropic(api_key=C.env_key(), timeout=900.0, max_retries=2)
    sem = asyncio.Semaphore(MAX_CONCURRENCY)
    ids = list(batches)
    # Warm the shared prefix with the first batch so the other 23 read the cache instead of
    # each writing its own copy. Counted in the arm's cost and wall time like any other call.
    first = await _one(client, sem, arm, ids[0], batches[ids[0]], out_dir, use_cache)
    rest = await asyncio.gather(
        *[_one(client, sem, arm, b, batches[b], out_dir, use_cache) for b in ids[1:]]
    )
    return [first, *rest]


# --------------------------------------------------------------------------- arm D order


def priority(cand: dict) -> tuple:
    """Deterministic per-candidate priority from features already in candidates.json.

    Order-only: it decides *when* a candidate is screened, never *whether*. Higher is sooner.
    """
    origins = cand["origins"]
    query_origins = [o for o in origins if o["relation"] == "query"]
    n_queries = len({o["query_id"] for o in query_origins if o["query_id"]})
    n_sources = len({o["source"] for o in origins})
    n_origins = len(origins)
    best_rank = min((o["rank"] for o in query_origins), default=200)
    is_anchor = any(o["relation"] == "anchor" for o in origins)
    from_expansion = any(
        o["relation"] in ("references", "citations", "recommendations") for o in origins
    )
    year = cand.get("year") or 2020
    age = max(1, 2026 - year + 1)
    cites_per_year = (cand.get("citation_count") or 0) / age

    score = (
        3.0 * float(is_anchor)
        + 2.0 * n_queries
        + 1.0 * n_sources
        + 0.5 * n_origins
        + 2.0 * (1.0 / (1.0 + best_rank))
        + 0.6 * math.log1p(cites_per_year)
        + 0.4 * float(from_expansion)
    )
    # ties broken deterministically, never randomly
    return (round(score, 6), -best_rank, cand["cid"])


def priority_batches() -> dict[str, dict]:
    """Re-cut the same 572 item payloads into priority-ordered batches of 25.

    Item payloads are lifted verbatim from the saved batch files, so arm D differs from
    arm C in item ordering and grouping only — never in a single byte of any item.
    """
    src = C.batches()
    template = next(iter(src.values()))["sub_criteria"]
    items = {i["cid"]: i for b in src.values() for i in b["items"]}
    cands = {c["cid"]: c for c in C.candidates()}
    order = sorted(items, key=lambda cid: priority(cands[cid]), reverse=True)
    out: dict[str, dict] = {}
    for n, start in enumerate(range(0, len(order), BATCH_SIZE), start=1):
        bid = f"p{n:02d}"
        out[bid] = {
            "batch": bid,
            "sub_criteria": template,
            "items": [items[cid] for cid in order[start:start + BATCH_SIZE]],
        }
    return out


# --------------------------------------------------------------------------- merge


def merge(arm: str, out_dir: Path, batch_ids: list[str]) -> tuple[int, int]:
    """Deterministic merge into an arm-local screen.json, in candidates.json order."""
    scores: dict[str, dict] = {}
    for bid in batch_ids:
        path = out_dir / "batches" / f"{bid}.json"
        if not path.exists():
            continue
        for s in json.loads(path.read_text())["scores"]:
            scores[s["cid"]] = s
    ordered = [scores[c["cid"]] for c in C.candidates() if c["cid"] in scores]
    C.write_json(out_dir / "screen.json", {"scores": ordered})
    return len(ordered), len(C.candidates())


def main() -> None:
    ap = argparse.ArgumentParser()
    ap.add_argument("arm", choices=["B", "C", "D"])
    ap.add_argument("--no-cache", action="store_true")
    ap.add_argument("--limit", type=int, default=0)
    args = ap.parse_args()

    use_cache = not args.no_cache
    batches = priority_batches() if args.arm == "D" else C.batches()
    if args.limit:
        batches = dict(list(batches.items())[: args.limit])
    out_dir = C.ARMS / args.arm
    if args.arm == "D":
        C.write_json(out_dir / "priority-order.json",
                     {bid: [i["cid"] for i in b["items"]] for bid, b in batches.items()})

    print(f"arm {args.arm}: {len(batches)} batches, cache={use_cache}, "
          f"spent so far ${C.spent():.4f}")
    t0 = time.monotonic()
    if args.arm == "B":
        results = run_sequential(batches, out_dir, use_cache)
    else:
        results = asyncio.run(run_parallel(args.arm, batches, out_dir, use_cache))
    wall = time.monotonic() - t0

    n, total = merge(args.arm, out_dir, list(batches))
    ok, msg = C.schema_check(out_dir / "screen.json", "ScreenFile")

    summary = C.summarise(results)
    summary.update({
        "arm": args.arm,
        "stage_wall_s": round(wall, 2),
        "cache_enabled": use_cache,
        "scored": n,
        "candidates": total,
        "complete": n == total,
        "schema_valid": ok,
        "schema_msg": msg,
        "cumulative_spend_usd": C.spent(),
    })
    C.dump_results(out_dir / "calls.json", results)
    C.write_json(out_dir / "summary.json", summary)
    print(json.dumps(summary, indent=1))


if __name__ == "__main__":
    main()
