"""Stratified rerank at depth k — Phase 1's R15 mechanics, generalised over k.

The cut keeps the shortlist's own in/out-of-window proportion (shortlist.py's 40:12 caps), so
the out-of-window rows `emit` needs for its foundational slots survive every depth. A flat
prefix would take k in-window rows and zero out-of-window ones, which would measure the cut
rule rather than the reranker. No new numeric weights: the ratio is the one already in the code.

High reasoning ON (thinking adaptive, effort high) at every depth, as in Phase 1.

Usage:  python rerank.py <topic> <R10|R15|R20|R25|Rall>
"""

from __future__ import annotations

import argparse
import json
import shutil
import sys
import time
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parent))
from lib import common as C  # noqa: E402

import anthropic  # noqa: E402

CUTS = {"R10": 10, "R15": 15, "R20": 20, "R25": 25, "Rall": 10**6}

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


def system_blocks(run: Path, queries: dict) -> list[dict]:
    sub = "\n".join(f"- {c['id']} — {c['name']}: {c['text']}" for c in queries["sub_criteria"])
    text = f"""You are reranking shortlisted papers for a research-scan run.

{C.purpose_line(run)}

# The brief

{C.brief_text(run)}

# The plan's sub-criteria (score every one of these per paper)

{sub}

Brief summary the plan recorded:
{queries['brief_summary']}

# The rerank rubric

{C.rubric("rerank-rubric")}

# Output

Return `{{"ranked": [...]}}` — one RankedEntry per record you were given, in the order given.
Copy each `cid` verbatim. Do not write `verification`; `verify` fills it.
"""
    return [{"type": "text", "text": text, "cache_control": {"type": "ephemeral"}}]


def record_payload(row: dict) -> dict:
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
    """First n of the shortlist, keeping its own in/out-of-window proportion."""
    if n >= len(shortlist["in_window"]) + len(shortlist["outside_window"]):
        return shortlist["in_window"], shortlist["outside_window"]
    ratio = C.IN_WINDOW_CAP / (C.IN_WINDOW_CAP + C.OUT_WINDOW_CAP)
    n_in = min(len(shortlist["in_window"]), round(n * ratio))
    n_out = min(len(shortlist["outside_window"]), n - n_in)
    n_in = min(len(shortlist["in_window"]), n - n_out)
    return shortlist["in_window"][:n_in], shortlist["outside_window"][:n_out]


def call(client, run, tag, system, rows, criteria_ids) -> tuple[C.CallResult, list]:
    payload = [record_payload(r) for r in rows]
    user = (
        f"Rerank these {len(payload)} shortlisted records. Score every sub-criterion for each.\n\n"
        "```json\n" + json.dumps(payload, ensure_ascii=False, indent=1) + "\n```"
    )
    attempts, last_err, schema_fail, errs = 0, "", False, []
    while attempts < C.MAX_ATTEMPTS:
        attempts += 1
        C.check_cap(0.80)
        t0 = time.monotonic()
        try:
            with client.messages.stream(
                model=C.MODEL,
                max_tokens=C.RERANK_MAX_TOKENS,
                system=system,
                messages=[{"role": "user", "content": user}],
                thinking={"type": "adaptive"},
                output_config={"effort": C.EFFORT,
                               "format": {"type": "json_schema",
                                          "schema": output_schema(criteria_ids)}},
            ) as stream:
                message = stream.get_final_message()
            dt = time.monotonic() - t0
            C.record(tag, message.usage.model_dump(), C.cost_of(message.usage), dt)
            try:
                ranked = json.loads(
                    next(b.text for b in message.content if b.type == "text"))["ranked"]
                want = {r["cid"] for r in rows}
                got = {r["cid"] for r in ranked}
                if got != want:
                    raise ValueError(f"cid mismatch: missing={sorted(want - got)[:4]} "
                                     f"extra={sorted(got - want)[:4]}")
                for r in ranked:
                    if not r["limitations"]:
                        raise ValueError(f"empty limitations for {r['cid']}")
            except Exception:
                schema_fail = True
                raise
            res = C.result_from(tag, message, dt, attempts)
            res.schema_failure = schema_fail
            res.attempt_errors = errs
            print(f"  {tag}  {dt:6.1f}s  ${res.cost_usd:.4f}  in={res.input_tokens} "
                  f"cr={res.cache_read} out={res.output_tokens} (think {res.thinking_tokens})")
            return res, ranked
        except C.CapExceeded:
            raise
        except Exception as exc:  # noqa: BLE001
            last_err = f"{type(exc).__name__}: {exc}"
            errs.append(last_err[:400])
            print(f"  {tag} attempt {attempts} failed: {last_err[:200]}")
            if attempts < C.MAX_ATTEMPTS:
                time.sleep(2 ** attempts)
    return C.CallResult(tag=tag, ok=False, seconds=0.0, attempts=attempts,
                        error=last_err, schema_failure=schema_fail, attempt_errors=errs), []


def main() -> None:
    ap = argparse.ArgumentParser()
    ap.add_argument("topic")
    ap.add_argument("arm", choices=list(CUTS))
    args = ap.parse_args()
    n = CUTS[args.arm]

    src = C.run_dir(args.topic)
    base = C.SWEEP / C.TOPICS[args.topic]["slug"] / args.arm
    run = base / "run"
    if run.exists():
        shutil.rmtree(run)
    run.parent.mkdir(parents=True, exist_ok=True)
    shutil.copytree(src, run)
    for stale in ("ranked.json", "evidence.json", "evidence.md", "evidence.bib",
                  "verify.log.jsonl"):
        (run / stale).unlink(missing_ok=True)
    manifest = json.loads((run / "manifest.json").read_text())
    manifest["run"]["run_dir"] = str(run)
    manifest["run"]["brief_path"] = str(run / "brief.md")
    (run / "manifest.json").write_text(json.dumps(manifest, indent=1))

    shortlist = json.loads((run / "shortlist.json").read_text())
    queries = json.loads((run / "queries.json").read_text())
    criteria_ids = [c["id"] for c in queries["sub_criteria"]]
    in_rows, out_rows = cut(shortlist, n)
    rows = in_rows + out_rows
    print(f"{args.topic} {args.arm}: shortlist "
          f"{len(shortlist['in_window'])}+{len(shortlist['outside_window'])} -> reranking "
          f"{len(in_rows)}+{len(out_rows)} = {len(rows)}   spent ${C.spent():.4f}")

    client = anthropic.Anthropic(api_key=C.env_key(), timeout=1800.0, max_retries=2)
    system = system_blocks(run, queries)
    results, ranked_all = [], []
    t0 = time.monotonic()
    for i in range(0, len(rows), C.RERANK_CHUNK):
        chunk = rows[i:i + C.RERANK_CHUNK]
        res, ranked = call(client, run, f"rerank/{args.topic}/{args.arm}/c{i // C.RERANK_CHUNK + 1}",
                           system, chunk, criteria_ids)
        results.append(res)
        ranked_all.extend(ranked)
    wall = time.monotonic() - t0

    (run / "ranked.json").write_text(json.dumps(ranked_all, indent=1))
    ok, msg = C.schema_check(run / "ranked.json", "Ranked")
    vcode, vout = C.run_cli(["research-scan", "verify", "--run", str(run), "--json", "--quiet"])
    ecode, eout = C.run_cli(["research-scan", "emit", "--run", str(run), "--json", "--quiet"])
    print(f"ranked schema {ok}; verify exit {vcode}; emit exit {ecode}")

    summary = C.summarise(results)
    summary.update({
        "topic": args.topic, "arm": args.arm, "cut": n,
        "reranked": len(ranked_all), "in_window": len(in_rows), "outside_window": len(out_rows),
        "reranked_cids": [r["cid"] for r in rows],
        "stage_wall_s": round(wall, 2),
        "ranked_schema_valid": ok, "ranked_schema_msg": msg,
        "shortlist_size": len(shortlist["in_window"]) + len(shortlist["outside_window"]),
        "verify_exit": vcode, "emit_exit": ecode,
        "verify_out": vout.strip()[:400], "emit_out": eout.strip()[:400],
        "frontier_tokens": sum(r.input_tokens + r.output_tokens for r in results),
        "cumulative_spend_usd": C.spent(),
    })
    if ecode == 0 and (run / "evidence.json").exists():
        ev = json.loads((run / "evidence.json").read_text())
        summary["top10_cids"] = [p["cid"] for p in ev["packets"]]
        summary["top10_dois"] = [(p.get("ids") or {}).get("doi") for p in ev["packets"]]
        summary["selection_reasons"] = [p.get("selection_reason") for p in ev["packets"]]
    C.dump_results(base / "calls.json", results)
    C.write_json(base / "summary.json", summary)
    print(json.dumps({k: v for k, v in summary.items()
                      if k not in ("failed_tags", "reranked_cids")}, indent=1))


if __name__ == "__main__":
    main()
