"""One-off salvage for a batch the frozen 3-attempt retry policy could not land.

`llm-lit-search` batch `x02` failed the ScreenScore contract on six consecutive identical
stateless calls, always the same way: 26 entries for a 25-item batch, the 26th a mangled
duplicate of `2ad9d99f0b79` (`…79b`, `…79dup`, `…79-dup`). Every one of the 25 wanted cids was
present and correctly shaped each time; the defect is one spurious extra row, not a missing or
misjudged score.

This re-issues the *identical* frozen call, drops rows whose cid is not in the batch, and then
validates the remainder against the same contract. Nothing else is relaxed: a missing cid, a
duplicate of a real cid or a bad score still fails. What was dropped is written to
`stages/salvage-<topic>-<batch>.json` so the intervention is auditable, and the underlying
failure is still counted against G4.

Usage:  python salvage.py <topic> <batch-id>
"""

from __future__ import annotations

import json
import sys
import time
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parent))
from lib import common as C  # noqa: E402
import screen as S  # noqa: E402

import anthropic  # noqa: E402


def main() -> None:
    topic, bid = sys.argv[1], sys.argv[2]
    run = C.run_dir(topic)
    batch = json.loads((run / "screen-batches" / f"{bid}.json").read_text())
    want = {i["cid"] for i in batch["items"]}
    out_dir = C.EXP / "screen-batches" / C.TOPICS[topic]["slug"]

    client = anthropic.Anthropic(api_key=C.env_key(), timeout=900.0, max_retries=2)
    C.check_cap(0.20)
    t0 = time.monotonic()
    with client.messages.stream(**S.request_kwargs(run, batch)) as stream:
        message = stream.get_final_message()
    dt = time.monotonic() - t0
    C.record(f"salvage/{topic}/{bid}", message.usage.model_dump(), C.cost_of(message.usage), dt)

    payload = json.loads(next(b.text for b in message.content if b.type == "text"))
    raw = payload["scores"]
    dropped = [s for s in raw if s.get("cid") not in want]
    kept = [s for s in raw if s.get("cid") in want]
    payload["scores"] = kept
    scores = C.validate_batch_scores(batch, payload)  # full contract, unrelaxed, on the remainder

    C.write_json(out_dir / f"{bid}.json", {"scores": scores})
    C.write_json(C.EXP / "stages" / f"salvage-{topic}-{bid}.json", {
        "topic": topic, "batch": bid, "seconds": round(dt, 1),
        "cost_usd": round(C.cost_of(message.usage), 6),
        "returned_rows": len(raw), "batch_items": len(want),
        "dropped_rows": dropped, "kept_rows": len(kept),
        "cumulative_spend_usd": C.spent(),
    })
    print(f"salvaged {topic}/{bid}: {len(raw)} rows returned, dropped {len(dropped)} "
          f"({[d.get('cid') for d in dropped]}), kept {len(kept)}")
    n, total = S.merge(run, out_dir)
    ok, msg = C.schema_check(run / "screen.json", "ScreenFile")
    print(f"screen.json {n}/{total} scored, schema {ok} {msg}")


if __name__ == "__main__":
    main()
