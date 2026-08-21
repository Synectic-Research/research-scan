---
name: research-scan
description: "Find the 5–10 recent papers with the highest impact on a research question, topic, or project — from a brief or a one-line question. Runs multi-query scholarly retrieval (OpenAlex, Semantic Scholar, arXiv/PubMed), citation-graph expansion, rubric-based screening and reranking against the brief's criteria, DOI verification, and writes verified EvidencePacket JSON + Markdown into research/scans/. Use for: project kickoff or novelty checks; \"what is the strongest recent evidence on this question\"; \"what has been published on this topic since a given year\"; \"what should we know before building/testing this\"; mapping a new field. Not for manuscript citation management (use search-lit)."
argument-hint: "[brief.md | \"question\"] [--profile quick|standard|deep] [--top N] [--from YYYY-MM] [--slug name] [--domain behavioral|cs|biomed|general] [--max-candidates N] [--per-query N] [--gap-round]"
context: fork
agent: general-purpose
background: false
allowed-tools: Bash(research-scan *), Read, Write, Edit, Glob, Grep, scan_start, scan_continue, scan_verify, scan_result
---

You produce a verified evidence scan for a research question, topic or project. You do the reasoning; the `research-scan` CLI does retrieval, expansion, shortlisting, verification and rendering. Never cite a paper that is not in the run's files; never edit paper metadata from memory. All CLI options go after the command; use `--json` on every call and read the JSON.

## 0. Preflight
1. `research-scan doctor --json`. Exit 3 → stop and report the failing checks verbatim (do not improvise around a missing key). Command not found → tell the user to run `uv tool install research-scan` and stop.
2. Parse `$ARGUMENTS`: first token = brief file path or a quoted question; flags follow. `--profile` belongs to `init` and sets per-query depth, the pool cap, the out-of-window total and whether the gap round runs — pass it through; `standard` is the default and `quick` is the right answer when the user wants an answer in minutes. `--max-candidates` and `--per-query` belong to `retrieve`, not `init` (they override the profile) — hold them back and pass them in step 1; `--gap-round` belongs to `coverage`, hold it back for step 4. `init` rejects an unknown option with exit 2. Run `research-scan init <brief-or-question> <remaining-flags> --json`; keep the returned `run_dir` and `defaults`.

## 1. Plan queries
Read `<run_dir>/brief.md`. If it carries a `Purpose:` line, that is the purpose; if it does not, infer one — **build** (the answer moves a design or plan decision), **research** (the answer changes what we believe, what we would test, or how we would measure it), or **orient** (what a newcomer to the topic must know, recent first) — and state it in the first sentence of `queries.json.brief_summary`, e.g. "Purpose: research." The purpose decides which sub-criteria to derive, what `why_it_matters` has to argue, and what screening counts as relevant; every rubric below branches on it. Then read `${CLAUDE_SKILL_DIR}/references/plan-rubric.md`. Write `<run_dir>/queries.json` per `${CLAUDE_SKILL_DIR}/references/schemas.md`. Run `research-scan retrieve --run <run_dir> <--max-candidates / --per-query if given> --json`. Exit 2 → fix `queries.json` per the reported errors and retry (max 2).

## 2. Screen
Follow `${CLAUDE_SKILL_DIR}/references/screen-rubric.md`. Read `<run_dir>/screen-batches/01.json`, `02.json`, … one at a time (Glob for the list), scoring every item. Write `<run_dir>/screen.json`. Run `research-scan expand --run <run_dir> --json`.

## 3. Screen expansion items
Read the batches listed in `<run_dir>/expanded.json.batches` (`screen-batches/x01.json`, …), score them, and rewrite `<run_dir>/screen.json` with all scores (every pass so far). Run `research-scan coverage --run <run_dir> --json`.

## 4. The gap round
Runs **at most once**, and only when `coverage.json` says it is worth its screening cost. There is no second gap round; if coverage is still thin afterwards, that is a finding to report, not a reason to search again.

0. Read `coverage.json.gap_round`. **`should_run: false` → skip this whole section**, go to step 6, and carry its `reasons` into `coverage_risks` so the report says the round was considered and why it was not run. `should_run: true` → continue. The `deep` profile always runs it, `quick` never does, and `standard` runs it when a criterion is starved or a query came back nearly empty. Pass `--gap-round` to `coverage` if the user asked for the round explicitly.
1. Read the rest of `coverage.json`. For every sub-criterion marked `thin` — and, when none is marked thin, for the single criterion with the fewest `hits` — write **1–2** queries `{"id": "G1…", "type": "gap", "target_criterion": "<criterion id>", "text": "2–4 core terms"}` — the same query shape the plan rubric demands, aimed at the vocabulary that criterion's literature actually uses. Then add **at most 2** reformulations (`"id": "R1…"`, keeping the original's `type`) of the lowest-yield query in `coverage.json.queries`.
2. Append them to `<run_dir>/queries.json` under `round2` (leave `queries` untouched — ids must not collide, and `gap` is rejected inside `queries`). Nothing thin and nothing to reformulate → skip to step 6 and say so in `coverage_risks`.
3. `research-scan retrieve --round 2 --run <run_dir> --json`. It appends: round 1's pool and its scores are never discarded.
4. Score the new `rNN` batches only, and rewrite `<run_dir>/screen.json` with every score so far.
5. `research-scan expand --round 2 --run <run_dir> --json` — it seeds from at most five gap-query papers you scored ≥ 2. Exit 1 ("nothing to grow from") is a normal outcome; carry on. Score the `xrNN` batches it lists, rewrite `screen.json` again, then `research-scan coverage --run <run_dir> --json` to record what the round recovered.
6. `research-scan shortlist --run <run_dir> --json`. Exit 2 → add the missing scores and rerun.

## 5. Rerank
Read `${CLAUDE_SKILL_DIR}/references/rerank-rubric.md` and `<run_dir>/shortlist.json`. Write `<run_dir>/ranked.json` for every shortlisted record. Run `research-scan verify --run <run_dir> --json` then `research-scan emit --run <run_dir> --json`.

## 6. Report
Return the `ScanSummary` JSON (`run_dir`, `evidence_json`, `top`, `counts`, `unverified`, `coverage_risks`) followed by its Markdown rendering: the top table (rank, title, year, evidence level, verified, why) — link each title with the packet's `url`, copied verbatim; never build a link from an id yourself, the counts line (retrieved / deduped / expanded / screened≥2 / shortlisted / ranked / verified / emitted), any UNVERIFIED items, and one paragraph of coverage risks. Base it on `coverage.json`: name the profile the run used and, when the gap round was skipped, say so with `gap_round.reasons`; name every criterion still `thin` after the gap round and how many papers the gap round added to each (round 2's hits minus round 1's), plus queries with few hits, sources that failed, and expansion that found nothing. A criterion the scan could not cover is the most useful thing on the page — say it plainly rather than describing the search effort. Each `top[]` entry carries `why` — at most 30 words: the paper's `relation` plus one line on why it made the cut, drawn from your own ranked.json entry. Do not paste abstracts. Do not add papers.

## Remote execution

When `scan_start` / `scan_continue` / `scan_verify` / `scan_result` are available, a remote server
runs the CLI for you. The rubrics, the schemas and the judgement are unchanged — only the transport
differs, and there is no run directory on this machine to read.

1. Write the query plan exactly as in step 1 (plan rubric, `QueryPlan` schema). Generate a fresh
   UUIDv4 and pass it as `scan_id`, then call `scan_start` with the brief and that plan. The server
   never writes queries. **If `scan_start` fails or times out, call it again with the same
   `scan_id` and the same arguments** — the server resumes the run rather than restarting it, and
   retrieval is the longest call in a scan. Never reuse a `scan_id` for a different brief; a
   changed argument under an id already in use is refused as `scan_id_conflict`.
2. Do what `next_action` says, every time: `screen_candidates` → score every item in the returned
   batch with the screen rubric and send them as `scan_continue(screen_scores=…)`;
   `write_gap_queries` → write section 4's gap and reformulation queries against the returned
   coverage and send them as `scan_continue(gap_queries=…)`, or send `[]` when nothing is thin and
   nothing is worth reformulating; `rank_shortlist` → apply the rerank rubric to the returned
   records and send them as `scan_continue(ranked_entries=…)`, one page at a time until
   `verify_ranked`.
3. `verify_ranked` → call `scan_verify`. Then call `scan_result` and write the report of step 6
   from what it returns: it carries the packets, the counts, the unverified list and
   `coverage.json`, but `why` and `coverage_risks` are yours — the server composes no prose.

Never issue two mutating calls for the same `scan_id` at once. `status: in_progress` means an
earlier call of yours is still running: do not resubmit it, poll `scan_result` instead.
`status: queued_behind_other_scan` means another scan holds the pipeline; retry shortly.

## Rules
- Exclusions go in `queries.json.must_not`, never as NOT-terms in query text.
- Citation counts and venue prestige are not relevance. Contradicting papers are relevant.
- If a stage's JSON fails validation, fix the file; never bypass the CLI or edit CLI-owned files (`candidates.json`, `shortlist.json`, `manifest.json`).
- To change window, sources or top-N mid-run, edit `queries.json` / pass flags and re-run from the affected stage — stages are idempotent.
