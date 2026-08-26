"""RERANK-CUT — R52 / R25 / R15, run on arm C's merged screening scores.

For each sub-arm:
  1. copy the saved run's structure into arms/rerank/<sub>/run (the saved run is never written to)
  2. substitute arm C's screen.json
  3. `research-scan shortlist --run <copy>`
  4. cut the shortlist to N, keeping the shortlist's own 40:12 in/out-of-window proportion so
     the out-of-window rows emit needs for its foundational slots survive the cut
  5. rerank the cut through stateless API calls (high reasoning ON in all three sub-arms)
  6. `research-scan verify`, then `research-scan emit`
  7. compare the resulting top-10 DOI set against the baseline's

Usage:  python rerank_arms.py {R52|R25|R15} [--source-arm C] [--chunk 13]
"""

from __future__ import annotations

import argparse
import json
import shutil
import subprocess
import sys
import time
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parent))
from lib import common as C  # noqa: E402

import anthropic  # noqa: E402

CUTS = {"R52": 52, "R25": 25, "R15": 15}
MAX_ATTEMPTS = 3
IN_WINDOW_CAP, OUT_WINDOW_CAP = 40, 12  # shortlist.py DEFAULT_MAX_{IN,OUTSIDE}_WINDOW

EVIDENCE_LEVELS = [
    "systematic-review", "meta-analysis", "rct", "prospective", "observational",
    "experimental", "computational", "qualitative", "other",
]
RELATIONS = [
    "design-changing", "plan-influencing", "closely-related", "contradicting", "foundational",
]


def entry_schema(criteria_ids: list[str]) -> dict:
    return {
        "type": "object",
        "additionalProperties": False,
        "properties": {
            "cid": {"type": "string"},
            "criteria": {
                "type": "object",
                "additionalProperties": False,
                "properties": {c: {"type": "integer", "enum": [0, 1, 2, 3]} for c in criteria_ids},
                "required": criteria_ids,
            },
            "overall": {"type": "integer", "enum": [0, 1, 2, 3]},
            "evidence_level": {"type": "string", "enum": EVIDENCE_LEVELS},
            "relation": {"type": "string", "enum": RELATIONS},
            "flags": {
                "type": "object",
                "additionalProperties": False,
                "properties": {
                    "review": {"type": "boolean"},
                    "contradicts": {"type": "boolean"},
                    "methods_paper": {"type": "boolean"},
                },
                "required": ["review", "contradicts", "methods_paper"],
            },
            "key_finding": {"type": "string"},
            "methodology": {"type": "string"},
            "why_it_matters": {"type": "string"},
            "limitations": {"type": "array", "items": {"type": "string"}},
            "relevance_reason": {"type": "string"},
        },
        "required": [
            "cid", "criteria", "overall", "evidence_level", "relation", "flags",
            "key_finding", "methodology", "why_it_matters", "limitations", "relevance_reason",
        ],
    }


def output_schema(criteria_ids: list[str]) -> dict:
    return {
        "type": "object",
        "additionalProperties": False,
        "properties": {"ranked": {"type": "array", "items": entry_schema(criteria_ids)}},
        "required": ["ranked"],
    }


def system_blocks(queries: dict) -> list[dict]:
    sub = "\n".join(f"- {c['id']} — {c['name']}: {c['text']}" for c in queries["sub_criteria"])
    text = f"""You are reranking shortlisted papers for a research-scan run.

{C.purpose_line()}

# The brief

{C.brief_text()}

# The plan's sub-criteria (score every one of these per paper)

{sub}

Brief summary the plan recorded:
{queries['brief_summary']}

# The rerank rubric

{C.rerank_rubric()}

# Output

Return `{{"ranked": [...]}}` — one RankedEntry per record you were given, in the order given.
Copy each `cid` verbatim. Do not write `verification`; `verify` fills it.
"""
    return [{"type": "text", "text": text, "cache_control": {"type": "ephemeral"}}]


def record_payload(row: dict) -> dict:
    """Full metadata, as shortlist.json hands it to the reranker."""
    return {
        "cid": row["cid"],
        "title": row["title"],
        "abstract": row.get("abstract"),
        "tldr": row.get("tldr"),
        "authors": [a["name"] for a in row.get("authors") or []][:8],
        "year": row.get("year"),
        "venue": row.get("venue"),
        "type": row.get("type"),
        "citation_count": row.get("citation_count"),
        "screen_score": row.get("score"),
        "outside_window": row.get("outside_window"),
    }


def cut(shortlist: dict, n: int) -> tuple[list[dict], list[dict]]:
    """Take the first N of the shortlist, keeping its own in/out-of-window proportion."""
    if n >= len(shortlist["in_window"]) + len(shortlist["outside_window"]):
        return shortlist["in_window"], shortlist["outside_window"]
    n_in = min(len(shortlist["in_window"]), round(n * IN_WINDOW_CAP / (IN_WINDOW_CAP + OUT_WINDOW_CAP)))
    n_out = min(len(shortlist["outside_window"]), n - n_in)
    n_in = min(len(shortlist["in_window"]), n - n_out)
    return shortlist["in_window"][:n_in], shortlist["outside_window"][:n_out]


def run_cli(args: list[str]) -> tuple[int, str]:
    proc = subprocess.run(args, capture_output=True, text=True)
    return proc.returncode, (proc.stdout or "") + (proc.stderr or "")


def call(client, sub, tag, system, rows, criteria_ids) -> tuple[C.CallResult, list]:
    payload = [record_payload(r) for r in rows]
    user = (
        f"Rerank these {len(payload)} shortlisted records. Score every sub-criterion for each.\n\n"
        "```json\n" + json.dumps(payload, ensure_ascii=False, indent=1) + "\n```"
    )
    attempts, last_err = 0, ""
    while attempts < MAX_ATTEMPTS:
        attempts += 1
        C.check_cap(0.60)
        t0 = time.monotonic()
        try:
            with client.messages.stream(
                model=C.MODEL,
                max_tokens=48000,
                system=system,
                messages=[{"role": "user", "content": user}],
                thinking={"type": "adaptive"},  # high reasoning ON in all three sub-arms
                output_config={
                    "effort": C.EFFORT,
                    "format": {"type": "json_schema", "schema": output_schema(criteria_ids)},
                },
            ) as stream:
                message = stream.get_final_message()
            dt = time.monotonic() - t0
            C.record(tag, message.usage.model_dump(), C.cost_of(message.usage), dt)
            text = next(b.text for b in message.content if b.type == "text")
            ranked = json.loads(text)["ranked"]
            want = {r["cid"] for r in rows}
            got = {r["cid"] for r in ranked}
            if got != want:
                raise ValueError(f"cid mismatch: missing={sorted(want - got)[:4]} "
                                 f"extra={sorted(got - want)[:4]}")
            for r in ranked:
                if not r["limitations"]:
                    raise ValueError(f"empty limitations for {r['cid']}")
            u = message.usage
            res = C.CallResult(
                tag=tag, ok=True, seconds=dt,
                input_tokens=u.input_tokens or 0, output_tokens=u.output_tokens or 0,
                thinking_tokens=C.thinking_tokens(u),
                cache_read=u.cache_read_input_tokens or 0,
                cache_write=u.cache_creation_input_tokens or 0,
                cost_usd=C.cost_of(u), attempts=attempts,
            )
            print(f"  {tag}  {dt:6.1f}s  ${res.cost_usd:.4f}  in={res.input_tokens} "
                  f"cr={res.cache_read} out={res.output_tokens} (think {res.thinking_tokens})")
            return res, ranked
        except C.CapExceeded:
            raise
        except Exception as exc:  # noqa: BLE001
            last_err = f"{type(exc).__name__}: {exc}"
            print(f"  {tag}  attempt {attempts} failed: {last_err[:180]}")
            if attempts < MAX_ATTEMPTS:
                time.sleep(2 ** attempts)
    return C.CallResult(tag=tag, ok=False, seconds=0.0, attempts=attempts, error=last_err), []


def main() -> None:
    ap = argparse.ArgumentParser()
    ap.add_argument("sub", choices=list(CUTS))
    ap.add_argument("--source-arm", default="C")
    ap.add_argument("--chunk", type=int, default=13)
    args = ap.parse_args()
    n = CUTS[args.sub]

    base = C.ARMS / "rerank" / args.sub
    run = base / "run"
    if run.exists():
        shutil.rmtree(run)
    run.parent.mkdir(parents=True, exist_ok=True)
    # copy the saved run's structure; the saved run itself is only ever read
    shutil.copytree(C.RUN, run)
    for stale in ("ranked.json", "evidence.json", "evidence.md", "evidence.bib",
                  "verify.log.jsonl", "shortlist.json"):
        (run / stale).unlink(missing_ok=True)
    shutil.copy(C.ARMS / args.source_arm / "screen.json", run / "screen.json")
    # keep run_dir self-consistent so the CLI resolves paths inside the copy
    manifest = json.loads((run / "manifest.json").read_text())
    manifest["run"]["run_dir"] = str(run)
    manifest["run"]["brief_path"] = str(run / "brief.md")
    (run / "manifest.json").write_text(json.dumps(manifest, indent=1))

    code, out = run_cli(["research-scan", "shortlist", "--run", str(run), "--json", "--quiet"])
    print(f"shortlist exit={code}: {out.strip()[:300]}")
    if code != 0:
        sys.exit(f"shortlist failed for {args.sub}")

    shortlist = json.loads((run / "shortlist.json").read_text())
    queries = json.loads((run / "queries.json").read_text())
    criteria_ids = [c["id"] for c in queries["sub_criteria"]]
    in_rows, out_rows = cut(shortlist, n)
    rows = in_rows + out_rows
    print(f"{args.sub}: shortlist {len(shortlist['in_window'])}+{len(shortlist['outside_window'])}"
          f" -> reranking {len(in_rows)}+{len(out_rows)} = {len(rows)}")

    client = anthropic.Anthropic(api_key=C.env_key(), timeout=1800.0, max_retries=2)
    system = system_blocks(queries)
    results, ranked_all = [], []
    t0 = time.monotonic()
    for i in range(0, len(rows), args.chunk):
        chunk = rows[i:i + args.chunk]
        res, ranked = call(client, args.sub, f"{args.sub}/c{i // args.chunk + 1}",
                           system, chunk, criteria_ids)
        results.append(res)
        ranked_all.extend(ranked)
    wall = time.monotonic() - t0

    # shortlist.json order is the contract for ranked.json membership, not order
    (run / "ranked.json").write_text(json.dumps(ranked_all, indent=1))
    ok, msg = C.schema_check(run / "ranked.json", "Ranked")
    print(f"ranked.json schema: {ok} {msg}")

    vcode, vout = run_cli(["research-scan", "verify", "--run", str(run), "--json", "--quiet"])
    print(f"verify exit={vcode}: {vout.strip()[:300]}")
    ecode, eout = run_cli(["research-scan", "emit", "--run", str(run), "--json", "--quiet"])
    print(f"emit exit={ecode}: {eout.strip()[:300]}")

    summary = C.summarise(results)
    summary.update({
        "sub_arm": args.sub, "source_arm": args.source_arm, "cut": n,
        "reranked": len(ranked_all), "in_window": len(in_rows), "outside_window": len(out_rows),
        "stage_wall_s": round(wall, 2), "ranked_schema_valid": ok, "ranked_schema_msg": msg,
        "shortlist_size": len(shortlist["in_window"]) + len(shortlist["outside_window"]),
        "verify_exit": vcode, "emit_exit": ecode,
        "cumulative_spend_usd": C.spent(),
    })
    if ecode == 0 and (run / "evidence.json").exists():
        ev = json.loads((run / "evidence.json").read_text())
        summary["top10_dois"] = [p["ids"]["doi"] for p in ev["packets"]]
        summary["top10_cids"] = [p["cid"] for p in ev["packets"]]
        base_dois = set(C.baseline_top_dois())
        summary["top10_overlap"] = len(base_dois & set(summary["top10_dois"]))
    C.dump_results(base / "calls.json", results)
    C.write_json(base / "summary.json", summary)
    print(json.dumps({k: v for k, v in summary.items() if k != "failed_tags"}, indent=1))


if __name__ == "__main__":
    main()
