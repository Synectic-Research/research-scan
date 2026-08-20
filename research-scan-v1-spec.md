# research-scan — V1 specification (Claude Code build brief)

| | |
|---|---|
| Document | V1 specification |
| Version | 1.1 |
| Date | 2026-08-18 |
| Stack | Python (uv + pydantic + ruff + pytest — canon §7) |
| Surfaces | CLI `research-scan` · Claude Code skill `/research-scan` (Codex/Cursor via the Agent Skills standard) · headless `claude -p` |

This is the specification the implementation was built against, kept unedited so the `§N` citations
throughout `AGENTS.md` and `docs/measurements.md` stay stable. Where the build deviated from it
deliberately, `AGENTS.md` records the amendment rather than this file being rewritten to match.

**One-line contract.** Given a project brief, return the 5–10 recently published papers most likely to change how the project is designed — as verified, structured evidence objects any agent can consume — from free/pay-per-use scholarly APIs, on any laptop, without an LLM API key in the tool itself.

**Assumptions (change them and the spec still holds).** Python, not TypeScript: the retrieval layer is data plumbing and your Python-research family already carries uv/pydantic/pytest. Reasoning (query planning, screening, reranking) is done by whichever agent hosts the skill; the CLI never calls a model. Behavioural/social science and AI/CS are first-class domains; biomedical is routed. `balanced` is the only mode in V1.

---

## 1. Goals, success criteria, non-goals

**Goals.** (G1) Recall the papers a strong human searcher would find, including ones that use different terminology than the brief. (G2) Rank for *design impact on this project*, not citation count. (G3) Every emitted paper is verified against a live scholarly record; nothing enters the output from model memory. (G4) One install on a user's laptop; one command in Claude Code; one shell line for programmatic use. (G5) Cheap: ≤ $0.20 source-API cost per scan; judge tokens are the only real spend.

**Success criteria (V1 acceptance, §14).** On the golden set (§13): recall@10 ≥ 0.5 and recall@25 ≥ 0.7 against curated expected papers; ≥ 80 % of the top 10 judged relevance ≥ 2/3 by an independent judge; 100 % of emitted DOIs verified or explicitly flagged; a fresh-machine install runs `research-scan doctor` green and completes one scan in ≤ 15 min wall-clock; `claude -p "/research-scan …"` returns schema-valid JSON.

**Non-goals (V1).** Systematic-review workflow (PRISMA trail, screening thousands) — that is search-lit's `systematic` mode or Elicit's SR API. Full-text retrieval, PDF parsing, Zotero, BibTeX-first citation management (search-lit owns those; research-scan emits a compatible `.bib` only as a courtesy). Embedding indices, vector stores, an MCP server, a web UI. Google Scholar, Scopus, Web of Science, PsycInfo, Embase (no personal-key API or ToS-compatible path — §7). Everything in §16 (Elicit, Exa, OSF-direct, modes) until its trigger fires.

---

## 2. What the research says (August 2026), and the design consequence

Verified from primary sources this session unless marked (vendor).

1. **Multi-query reformulation + citation-graph traversal is the recall mechanism; single-query database search is the ceiling.** Ai2 Paper Finder generates several LLM reformulations of the semantic criteria, queries multiple indices plus the Semantic Scholar API, tracks citations forward and backward, and reports 89 % perfectly-relevant / 98 % highly-relevant on LitSearch in full mode ([Ai2 blog](https://allenai.org/blog/paper-finder)). PaSa's crawler alternates *search* and *expand-citations* actions and reaches ~71 % crawler recall on RealScholarQuery, +37.8 % recall@20 over Google+GPT-4o ([PaSa](https://ar5iv.labs.arxiv.org/html/2501.10120)). Sahu, Charlin & Pal show bibliography expansion lifting recall from <20 % to >80 % on ROLLINGEVAL ([arXiv 2605.29234](https://arxiv.org/html/2605.29234v1)). → Stages 2–5 below are non-optional.
2. **Adaptive expansion beats fixed expansion; multi-hop traversal recovers different-terminology papers; agents mishandle negative constraints.** ScholarQuest (June 2026): best agent recall@100 0.314 vs 0.214 for the best non-agentic baseline; scope-controlled queries fail (R@100 ≈ 0.18) because agents treat exclusions as positive keywords; the failure mode is "off-target exploration" ([arXiv 2606.20235](https://arxiv.org/html/2606.20235v1)). → Exclusions are enforced in code filters, never in query text (§8.3); expansion is seeded only from screened-relevant papers (§8.5); the candidate pool is capped so off-target neighbourhoods cannot swamp the reranker.
3. **Decomposed relevance judgment is the reranking win.** Paper Finder's "mini breakthrough" was decomposing the query into sub-criteria and scoring each before combining ([Ai2 blog](https://allenai.org/blog/paper-finder)); RollingEval's strongest AI rerankers hit 86–88 % relevance where human citation lists scored 51 % ([arXiv 2605.29234](https://arxiv.org/html/2605.29234v1)). → The rerank rubric decomposes the brief into 3–6 sub-criteria scored 0–3 (§10.3). No hand-tuned weight vector: the model scores, code selects.
4. **Human reference lists are not ground truth; the golden set is a floor.** RollingEval: an LLM judge rated only 51 % of human citations moderately relevant or higher; humans cite collaborators 2.5× more ([arXiv 2605.29234](https://arxiv.org/html/2605.29234v1)). → Eval reports recall against curated papers *and* judged precision; a missed "expected" paper is a signal, not a failure by itself.
5. **Source economics changed in 2026.** OpenAlex requires API keys since Feb 2026, ~$1/day free allowance, ~$0.001 per search call, ID/DOI lookups free ([CASRAI](https://casrai.org/news/openalex-api-keys-mandatory-usage-based-pricing-2026); [OpenAlex docs](https://developers.openalex.org/api-reference/works/list-works)). Semantic Scholar: free key = 1 req/s across endpoints; unauthenticated = shared pool; recommendations + citations/references endpoints ([S2 tutorial](https://www.semanticscholar.org/product/api/tutorial)). Elicit API GA 2026-07-15 but Pro plan required and no references/citations/similar-papers endpoints ([Elicit docs](https://docs.elicit.com/)). Exa `category="publication"` launched 2026-07-23, paid ([Exa](https://exa.ai/blog/publications-search)). Web of Science Starter free tier = 50 req/day without times-cited ([Clarivate](https://developer.clarivate.com/apis/wos-starter)); Scopus needs an institutional API subscription ([pybliometrics](https://pybliometrics.readthedocs.io/en/stable/access.html)). → V1 = OpenAlex + Semantic Scholar (mandatory) + arXiv/PubMed (routed). OSF's own API only filters preprints by title ([ToolUniverse OSF tool](https://zitniklab.hms.harvard.edu/ToolUniverse/_modules/tooluniverse/osf_preprints_tool.html)), so PsyArXiv/SocArXiv coverage comes through OpenAlex's DOI ingestion, probed by `doctor` (§8.6).
6. **Claude Code mechanics (verified in docs).** Skills follow the Agent Skills open standard; frontmatter supports `context: fork`, `agent`, `background`, `allowed-tools` (space- or comma-separated; `Bash(cmd *)` prefix rules), `argument-hint`, `arguments`, `disable-model-invocation`, `model`, `effort`; `${CLAUDE_SKILL_DIR}` resolves bundled files; user-invoked skills work in `-p` mode by putting `/skill-name` in the prompt; `--output-format json --json-schema` returns schema-validated `structured_output`; `--bare` skips skill discovery so headless runs load the skill via `--plugin-dir`; Cowork/cloud sessions do not read `~/.claude/skills` ([skills docs](https://code.claude.com/docs/en/skills); [headless docs](https://code.claude.com/docs/en/headless); [plugins reference](https://code.claude.com/docs/en/plugins-reference)). → §11–12.

---

## 3. Design principles (and what changed from the chat proposal)

- **Retrieve cheaply in code, reason expensively in the agent.** The CLI is deterministic plumbing: HTTP, dedup, graph expansion, shortlist ordering, verification, selection rules, file I/O. Every judgment (queries, relevance, evidence level, "why it matters") happens in the hosting agent under a written rubric. Canon §5 "orchestrator holds no intelligence" applies literally.
- **Files are the interface.** Each stage reads/writes JSON in a run directory. Any agent (Claude Code, Codex, Cursor, a Python loop with its own model) can drive the same CLI. This is what makes it harness-agnostic and shareable.
- **Verified or flagged, never silent.** search-lit's anti-hallucination contract carried over (§10.5); retracted works never ship (§10.4).
- **No invented weights.** The chat proposal's 0.40/0.15/… formula is dropped: the rubric scores, code selects (§10.4). Weights return only if the eval justifies them.
- **Free first.** Elicit demoted from "primary" to "candidate add-on gated by eval". OpenAlex key + Semantic Scholar key are the only credentials.
- **One mode.** `balanced` (recent window + foundational slots). Other modes: §16.
- **Sequential over clever.** V1 screens candidates sequentially inside the forked skill (bounded by the candidate cap) rather than fanning out subagents, whose availability inside a forked skill is not verified. Parallel screening is a V1.1 optimisation (§16).

---

## 4. Architecture

```
brief.md ─▶ [A] plan ─▶ queries.json ─▶ [C] retrieve ─▶ candidates.json + screen-batches/ ─▶ [A] screen ─▶ screen.json
                                                                                                          │
   evidence.{json,md,bib} ◀─ [C] emit ◀─ [C] verify ◀─ ranked.json ◀─ [A] rerank ◀─ shortlist.json ◀─ [C] shortlist ◀─ [A] screen (round 2) ◀─ [C] expand ◀─┘
[A] = agent step under a rubric (SKILL.md + references/*.md)      [C] = CLI step (research-scan <cmd>)
```

| # | Stage | Owner | Input → Output | Notes |
|---|---|---|---|---|
| 1 | `plan` | Agent | `brief.md` → `queries.json` | 6–8 typed queries + sub-criteria + exclusions (§10.1) |
| 2 | `retrieve` | CLI | `queries.json` → `candidates.json`, `screen-batches/*.json` | OpenAlex + S2 (+ arXiv/PubMed if routed); per-query top-N; dedup; retraction/date/exclusion filters; abstracts materialised; trimmed screening batches written |
| 3 | `screen` | Agent | `screen-batches/*.json` → `screen.json` | listwise, ≤ 25 per batch, score 0–3 + one-line reason (§10.2) |
| 4 | `expand` | CLI | `screen.json` → `expanded.json`, new `screen-batches/x*.json` | seeds = score ≥ 2 (max 15); S2 references + citations + recommendations; OpenAlex fallback; filters; out-of-window references kept & tagged (§8.5) |
| 5 | `screen` (round 2) | Agent | expansion batches → `screen.json` (rewritten with the new scores added) | same rubric |
| 6 | `shortlist` | CLI | `screen.json` → `shortlist.json` | validates coverage of every cid (else exit 2 with the missing list); orders by score, origin count, recency; ≤ 40 in-window + ≤ 5 out-of-window records with full metadata (§8.7) |
| 7 | `rerank` | Agent | `shortlist.json` → `ranked.json` | decomposed sub-criteria 0–3, evidence level, flags, `key_finding`, `why_it_matters`, `limitations` (§10.3) |
| 8 | `verify` | CLI | `ranked.json` → `ranked.json` (+`verification`) | Crossref + OpenAlex; title/year/author match; retraction re-check (§10.5) |
| 9 | `emit` | CLI | `ranked.json` → `evidence.json`, `evidence.md`, `evidence.bib`, `manifest.json` (final) | selection rules (§10.4); never adds papers; drops retracted; unverified stay flagged |

Time budget: retrieve+expand+verify ≤ 3 min of HTTP at ≤ 1 req/s per host; agent steps dominate (≈ 8–10 screening batches + rerank of ≤ 45) → ≤ 15 min end-to-end on Opus-class.

---

## 5. Repository layout (one repo = Python package + Claude Code plugin + `npx skills`-compatible)

```
research-scan/
  README.md                          # install (the user path), 5-line usage, keys, troubleshooting
  AGENTS.md                          # canon §4 schema: Vocabulary / Commands / Boundaries / Done-state / Patterns / Anti-patterns / See also
  LICENSE                            # MIT
  pyproject.toml                     # name="research-scan"; requires-python=">=3.11" (dev on 3.13); [project.scripts] research-scan="research_scan.cli:app"
  uv.lock
  .env.example                       # OPENALEX_API_KEY= OPENALEX_MAILTO= S2_API_KEY= NCBI_API_KEY=   (only OPENALEX_API_KEY is mandatory)
  .claude-plugin/plugin.json         # {"name":"research-scan","version":"0.1.0","description":"..."} → `claude --plugin-dir .`
  skills/research-scan/
    SKILL.md                         # §11 verbatim (only `<owner>` substituted at S5)
    references/plan-rubric.md        # §10.1
    references/screen-rubric.md      # §10.2
    references/rerank-rubric.md      # §10.3
    references/schemas.md            # generated by `research-scan schema --md`; a test asserts it is current
    examples/brief.example.md
  src/research_scan/
    cli.py                           # typer app: init retrieve expand shortlist verify emit doctor eval schema
    config.py                        # env/.env loading, resolved paths, defaults, key redaction
    schema.py                        # pydantic v2: QueryPlan, Candidate, ScreenFile, Expanded, Shortlist, Ranked, Verification, EvidencePacket, Evidence, Manifest, RunInfo, ScanSummary, EvalResult
    http.py                          # httpx client, retries/backoff, per-host rate limiter, sqlite cache (7-day TTL)
    sources/base.py                  # Source protocol: search(query, window) → list[Candidate]; references/citations/recommendations
    sources/openalex.py  sources/s2.py  sources/arxiv.py  sources/pubmed.py  sources/crossref.py
    dedup.py                         # DOI/arXiv/PMID normalisation, cid derivation, title fuzzy match (rapidfuzz ≥ 92)
    expand.py                        # seed selection, graph calls, caps, out-of-window tagging
    shortlist.py                     # coverage validation + ordering (§8.7)
    verify.py                        # Crossref/OpenAlex verification → Verification model
    select.py                        # emit selection rules (§10.4)
    render.py                        # evidence.md / evidence.bib
    doctor.py                        # live invocation checks, cache bypassed (§8.6)
    evalrun.py                       # golden-set recall (§13)
    log.py                           # logging setup: human INFO on stderr, JSONL per stage in the run dir
  eval/golden/<topic>.yaml           # brief + expected DOIs (ratified by the maintainer, Crossref-verified) + exclusions
  eval/judge-prompt.md  eval/judge.sh   # independent-judge step (calls `claude -p`; outside the package)
  eval/results/                      # per-run results (gitignored except the documented acceptance run)
  tests/                             # pytest; httpx mocked with respx + recorded fixtures under tests/fixtures/; `-m live` for doctor
```

Dependencies (keep to these unless a slice proves a need): `httpx`, `pydantic>=2`, `typer`, `rapidfuzz`, `pyyaml`; dev: `pytest`, `respx`, `ruff`. No LLM SDK in the package. Paths are fixed: config `~/.config/research-scan/.env`, cache `~/.cache/research-scan/http.sqlite` (created on first use; `doctor` prints both).

---

## 6. CLI contract

**Shape.** `research-scan <command> [options]`. All options are per-command and follow the command (typer). Common options accepted by every command: `--run DIR` (default: newest dir under `./research/scans/`, or `$RESEARCH_SCAN_RUN`), `--json` (machine-readable stdout), `--quiet`, `--log-level INFO`, `--no-cache`. Every command validates its input file against the pydantic model; on failure it prints the error list (JSON under `--json`) and exits 2 so the agent can fix the file and retry. Exit codes: 0 ok · 1 runtime failure (all routed sources failed, or unrecoverable I/O) · 2 input/schema error · 3 `doctor` mandatory check failed.

**Precedence for run parameters** (window, top, foundational, domain, sources): explicit command flag > `queries.json` (agent-written) > `manifest.json.defaults` (written by `init`). `init` prints a `RunInfo` JSON to stdout so the planning agent sees the defaults it must respect.

| Command | Purpose | Options (beyond common) | Writes |
|---|---|---|---|
| `init <brief.md \| "question">` | Create run dir; copy/write `brief.md`; write `manifest.json` (`defaults` section); print `RunInfo` | `--slug`, `--from YYYY-MM`, `--to YYYY-MM`, `--top`, `--foundational`, `--domain` | `research/scans/<YYYY-MM-DD>-<slug>/{brief.md,manifest.json}` |
| `retrieve` | Run all queries against routed sources; dedup; filter; materialise abstracts; write screening batches | `--per-query`, `--max-candidates`, `--sources openalex,s2[,arxiv,pubmed]`, `--include-preprints/--no-include-preprints`, `--include-all-types` | `candidates.json`, `screen-batches/NN.json`, `retrieval.log.jsonl`, manifest `retrieval` section |
| `expand` | Citation-graph expansion from screened seeds | `--seeds`, `--max-new`, `--max-outside-window` | `expanded.json`, `screen-batches/xNN.json`, appends to `candidates.json` (`origins[].relation ≠ query`), manifest `expansion` |
| `shortlist` | Validate screen coverage; order; cut | `--max-in-window`, `--max-outside-window` | `shortlist.json` |
| `verify` | Verify every entry of `ranked.json` | `--strict` | `ranked.json` (adds `verification`), `verify.log.jsonl`, manifest `verification` |
| `emit` | Apply selection rules; render | `--top`, `--foundational`, `--bib/--no-bib` | `evidence.json`, `evidence.md`, `evidence.bib`, manifest `emit` + `counts` |
| `doctor` | Live invocation of each source (cache bypassed); keys; paths; PsyArXiv-DOI coverage probe | `--sources` | stdout table; exit 0/3 |
| `eval` | Score run(s) against golden topics | `--golden DIR`, `--topic NAME`, `--judge FILE` (merge a judge output) | `eval/results/<date>-<topic>.json` |
| `schema` | Print JSON Schema | `--name MODEL`, `--md` | stdout |

**Defaults (single source of truth; other sections refer here).**

| Parameter | Default | Where set |
|---|---|---|
| window | 36 months back → today | `init --from/--to`, `queries.json.window` |
| top / foundational | 10 / 2 | `init`, `emit` |
| per_query | 20 | `retrieve` |
| max_candidates | 250 | `retrieve` |
| seeds / max_new / max_outside_window (expand) | 15 / 100 / 20 | `expand` |
| shortlist max_in_window / max_outside_window | 40 / 5 | `shortlist` |
| title match ratio | 90 (`--strict` 95) | `verify` |
| cache TTL | 7 days | `http.py` |

**Rate limits & retries.** OpenAlex ≤ 5 req/s with key + `mailto`; S2 1 req/s with key, 0.3 req/s without; Crossref polite pool (`mailto` in User-Agent); arXiv 1 req/3 s; NCBI 3 req/s (10 with key). 3× exponential backoff on 429/5xx. A source that fails after retries is recorded in the manifest and stderr; `retrieve` exits 1 only if *all* routed sources fail.

**Logging (canon §8).** `logging` module; INFO human-readable to stderr; JSONL per stage in the run dir with entry/exit, per-source counts, HTTP status histogram, durations, estimated OpenAlex cost. No prompts, no secrets (keys are redacted by `config.py` before anything is logged).

---

## 7. Sources and routing

| Source | Role in V1 | Access | Notes |
|---|---|---|---|
| **OpenAlex** (`/works`) | Primary search + metadata + retraction flag + graph fallback | Free key (mandatory); ~$1/day free; `search=`, `filter=from_publication_date,to_publication_date,is_retracted:false,type`, `sort=relevance_score:desc`, `select=` to trim, `per_page` 50 | Abstracts arrive as `abstract_inverted_index` — reconstruct in code. Covers Crossref-registered preprints (PsyArXiv/SocArXiv/SSRN DOIs) — `doctor` probes a fixed PsyArXiv DOI. |
| **Semantic Scholar** (`/graph/v1`, `/recommendations/v1`) | Second search voice (`/paper/search`), references/citations, recommendations (`/papers` with `positivePaperIds`), `publicationDateOrYear`, `fieldsOfStudy`, `citationCount`, `influentialCitationCount`, `externalIds`, `tldr` | Free key (apply now; historical backlog); 1 req/s | Best graph + "papers like these"; covers arXiv. |
| **arXiv API** | Routed for cs / physics / math / stats | Free; `search_query`, `sortBy=submittedDate` | Same-day listings; OpenAlex/S2 lag days. |
| **PubMed E-utilities** | Routed for biomed / neuro | Free; key optional | Reuse search-lit's proven E-utilities patterns; no MeSH generation in V1. |
| **Crossref** (`/works/{doi}`) | Verification + retraction/update metadata | Free, polite pool | Never a search engine here. |

Routing: the agent sets `queries.json.domain` (resolving `auto` itself). CLI map: `behavioral` → openalex, s2 · `cs` → openalex, s2, arxiv · `biomed` → openalex, s2, pubmed · `general` → openalex, s2, plus arxiv if any query has `type: method`. `--sources` overrides. Deferred sources: §16 only.

---

## 8. Retrieval policy (deterministic, in code)

**8.1 Per query.** For each query: OpenAlex `search` with window and `is_retracted:false`, top `per_query`; S2 `/paper/search` with `publicationDateOrYear`, top `per_query`; routed extras. `mode: keyword` queries are sent verbatim (Boolean allowed on S2/PubMed/arXiv; OpenAlex `search` supports quoted phrases). Each hit becomes a `Candidate` with one `origins[]` entry `{source, relation: "query", query_id, rank}`; a paper found by several queries keeps all origins (origin count is a reranker signal).

**8.2 Normalisation, cid, dedup.** DOI lower-cased, `https://doi.org/` stripped; arXiv IDs normalised (`2501.10120v2` → `2501.10120`). `cid` = first 12 hex of sha1 of the primary id in priority doi > arxiv > pmid > `norm(title)+year` — stable across runs. Merge on DOI, else arXiv id, else PMID, else title fuzzy ratio ≥ 92 with same first-author surname or year ±1. Merged record keeps the union of identifiers, the longest abstract, max citation count, all origins.

**8.3 Filters.** Date window (publication date; first-seen for preprints); `is_retracted` false (OpenAlex) — retracted items dropped and counted; `must_not` phrases from `queries.json` matched case-insensitively at word boundaries (`\bphrase\b`) against title + abstract; type filter drops paratext/errata/datasets unless `--include-all-types`; no language filter in V1.

**8.4 Caps.** `per_query` × ≤ 8 queries × 2–3 sources → typically 150–250 after dedup; hard cap `max_candidates` by keeping best per-query ranks round-robin so no single query dominates. The manifest records what was dropped (no silent caps).

**8.5 Expansion.** Seeds = candidates with screen score ≥ 2, ordered by score then origin count, max `seeds`. Per seed: S2 references (top 30 by citationCount), S2 citations (newest 30 within window), plus one S2 recommendations call with all seeds as `positivePaperIds` (limit 40). OpenAlex `cites:` / `referenced_works` fallback when S2 lacks the id. New items pass 8.2 and 8.3 **except** that the date filter *tags* rather than drops references (`outside_window: true`); in-window additions capped at `max_new`, out-of-window at `max_outside_window`, both ranked by (number of seeds linking to it, citationCount ÷ age). New candidates carry `origins[] = {source, relation: references|citations|recommendations, seed_id, rank}`.

**8.6 Doctor (readiness gate = invoke, don't list).** With the cache bypassed: OpenAlex search for a fixed query (≥ 1 hit; reads `is_retracted`); OpenAlex lookup of a fixed PsyArXiv DOI (coverage probe); S2 search + one `/paper/{id}/references`; Crossref lookup of a fixed DOI; arXiv one query; PubMed one esearch (all sources by default; `--sources` narrows); config/cache paths writable; Python ≥ 3.11; key presence (masked). Result table:

| Check | Missing/failing → |
|---|---|
| OPENALEX_API_KEY present and OpenAlex search OK | FAIL → exit 3 (mandatory) |
| S2 search OK | WARN if no key or 429/5xx (exit 0); FAIL only if the endpoint is unreachable with a key |
| Crossref, arXiv, PubMed | WARN (verify degrades to OpenAlex; routed source skipped) |
| Paths writable, Python version | FAIL → exit 3 |

Doctor never reports a check it did not execute.

**8.7 Shortlist.** Validates that every cid in `candidates.json` has exactly one score in `screen.json` (else exit 2 listing missing/duplicate cids). Orders in-window candidates by score desc, origin count desc, publication_date desc; takes ≤ `max_in_window` with score ≥ 2. Separately takes ≤ `max_outside_window` out-of-window candidates with score ≥ 2 by the same order. Writes `shortlist.json` with full records (title, abstract, year, venue, ids, citation counts, origins, `outside_window`).

---

## 9. Data contracts (pydantic v2; `research-scan schema` is the source of truth; `references/schemas.md` is generated from it)

**9.1 `queries.json` (agent → CLI)**
```json
{
  "brief_summary": "one paragraph restating the project in the agent's words",
  "domain": "behavioral | cs | biomed | general",
  "window": {"from": "2023-08", "to": null},
  "sub_criteria": [{"id": "C1", "name": "problem match", "text": "..."}, {"id": "C2", "name": "population/setting", "text": "..."}],
  "must_not": ["phrase excluded in code"],
  "queries": [
    {"id": "Q1", "type": "direct", "text": "...", "mode": "semantic"},
    {"id": "Q2", "type": "terminology", "text": "...", "mode": "semantic"},
    {"id": "Q3", "type": "mechanism", "text": "...", "mode": "semantic"},
    {"id": "Q4", "type": "method", "text": "...", "mode": "keyword"},
    {"id": "Q5", "type": "adjacent", "text": "...", "mode": "semantic"},
    {"id": "Q6", "type": "contradictory", "text": "...", "mode": "semantic"},
    {"id": "Q7", "type": "review", "text": "...", "mode": "keyword"},
    {"id": "Q8", "type": "emerging", "text": "...", "mode": "semantic"}
  ]
}
```
Constraints: 6–8 queries; `type` ∈ {direct, terminology, mechanism, method, adjacent, contradictory, review, emerging}; `direct`, `terminology`, `contradictory`, `review` mandatory; `text` ≤ 30 words; 3–6 sub-criteria; `domain` never `auto` (the agent resolves it).

**9.2 `candidates.json` (CLI)** — `{"run": RunInfo, "candidates": [Candidate]}`; `Candidate = {cid, title, abstract|null, tldr|null, authors[{name, s2_id?, openalex_id?}], year, publication_date|null, venue|null, type: article|preprint|review|book-chapter|other, ids{doi?, arxiv?, pmid?, openalex?, s2?}, citation_count, influential_citation_count|null, is_retracted, oa_url|null, origins[{source: openalex|s2|arxiv|pubmed, relation: query|references|citations|recommendations, query_id|null, seed_id|null, rank}], outside_window: bool}`.

**9.3 `screen-batches/NN.json` (CLI → agent)** — `{"batch": "NN", "sub_criteria": [...copied from queries.json...], "items": [{cid, title, abstract_600, year, venue, origin_count, outside_window}]}`; retrieve writes `01..`, expand writes `x01..`.

**9.4 `screen.json` (agent → CLI)** — `{"scores": [{"cid", "score": 0|1|2|3, "reason": "≤ 20 words"}]}`. 0 off-topic · 1 tangential · 2 relevant to ≥ 1 sub-criterion · 3 central. Round 2 rewrites the file with the new scores added (Write, not append).

**9.5 `expanded.json` (CLI)** — `{"seeds": [cid], "added": [cid], "added_outside_window": [cid], "dropped": {"retracted": n, "must_not": n, "cap": n}, "batches": ["x01", ...]}`.

**9.6 `shortlist.json` (CLI)** — `{"in_window": [Candidate ⊕ {score}], "outside_window": [Candidate ⊕ {score}]}`.

**9.7 `ranked.json` (agent → CLI; CLI adds `verification`)** — array of `{cid, criteria: {C1: 0-3, ...}, overall: 0-3, evidence_level: systematic-review|meta-analysis|rct|prospective|observational|experimental|computational|qualitative|other, flags: {review, contradicts, methods_paper}, key_finding, methodology, why_it_matters, limitations[], relevance_reason}` ⊕ `verification: {verified: bool, verified_by: [crossref|openalex|arxiv|s2], verified_on, title_match_ratio, mismatches[]}` where `mismatches[]` items ∈ {doi_unresolved, title, year, author, retracted, no_record}.

**9.8 `evidence.json` (CLI)** — `{"run": RunInfo, "packets": [EvidencePacket], "alternates": [EvidencePacket]}`; `EvidencePacket = Candidate ⊕ ranked fields ⊕ verification ⊕ {rank, selection_reason: score|foundational|review|contradicting|diversity|backfill, url}`. `evidence.md`: table (rank, title, year, venue, evidence level, verified) then one block per paper; unverified rows carry `[UNVERIFIED — check manually]`. `evidence.bib`: search-lit-compatible entries with `verified`, `verified_by`, `verified_on`.

**9.9 `manifest.json` (CLI-owned; each command upserts its section)** — `{run: RunInfo, defaults{window, top, foundational, domain, sources}, retrieval{per_source{queried, hits, failed}, deduped_remaining, dropped{retracted, must_not, type, cap}, cost_estimate_usd, duration_s}, expansion{...}, verification{verified, unverified, dropped_retracted}, counts{retrieved, deduped, expanded, screened_ge2, shortlisted, ranked, verified, emitted}, tool_version, timestamps}`. `RunInfo = {run_dir, slug, date, brief_path, defaults}` — printed by `init` (stdout) and embedded in files.

**9.10 `ScanSummary` (skill's return value; also the `--json-schema` for headless)** — `{run_dir, evidence_json, top: [{rank, title, year, doi|null, evidence_level, verified}], counts (from manifest), unverified: [{title, mismatches}], coverage_risks: str}`.

**9.11 `EvalResult`** — `{topic, run_dir, expected: n, found_at_10, found_at_25, recall_10, recall_25, misses: [{doi, why}], judged: {precision_ge2|null, per_rank[]}}`.

---

## 10. Reasoning stages (the agent, under rubrics)

**10.1 Plan (`references/plan-rubric.md`).** Read the brief and the `RunInfo` defaults; write `brief_summary`; derive `sub_criteria` (3–6: problem, population/setting, mechanism/method, outcome/measure, constraints); write 6–8 queries covering the mandatory types, each aimed at a *different research community's vocabulary*; put every exclusion in `must_not`, never as NOT-terms in query text (research finding 2); resolve `domain`; keep the default window unless the brief argues for a longer one (slow-moving fields → 60 months). Then run `retrieve`.

**10.2 Screen (`references/screen-rubric.md`).** Read one batch file at a time; score every item 0–3 against the sub-criteria with a one-line reason; do not reward citation counts or venue prestige; do reward explicit contradiction of the brief's premise (it is relevant). Write `screen.json` once after all batches (round 1), rewrite it after the expansion batches (round 2). Sequential; no delegation in V1.

**10.3 Rerank (`references/rerank-rubric.md`).** For every record in `shortlist.json` (both lists): score each sub-criterion 0–3 from the abstract (state "abstract-only" in `methodology` if that is all there is); assign `evidence_level`; set `flags`; write `key_finding` (one sentence, with numbers when the abstract gives them), `methodology`, `why_it_matters` (specific to *this* project's design decisions), `limitations` (≥ 1), `relevance_reason`; `overall` is the model's holistic 0–3, not an average; ties are resolved by code (§10.4), not by the rubric. Never introduce a cid absent from `shortlist.json` — the CLI rejects it (exit 2).

**10.4 Selection (code, in `emit`).** Requires `verification` on every ranked entry (else exit 2 — run `verify`). Drop entries whose `mismatches` include `retracted` (count as `dropped_retracted`). Order by `overall` desc, criteria sum desc, origin count desc, publication_date desc. Fill `top − foundational` slots from in-window entries; unverified entries are eligible but rendered with the marker. Diversity: at most 2 papers sharing a first author. Guarantees: if any entry with `flags.review` (resp. `flags.contradicts`) has `overall ≥ 2`, at least one is included, displacing the lowest-scoring pick (`selection_reason: review|contradicting`). Fill `foundational` slots from `outside_window` entries with `overall ≥ 2` in the same order; empty foundational slots are backfilled from in-window alternates (`selection_reason: backfill`). Next 5 by order → `alternates`.

**10.5 Verification protocol (search-lit lineage).** For every ranked entry: Crossref `works/{doi}` must resolve; title fuzzy ratio ≥ 90 (`--strict` 95); year ±1; first-author surname match; OpenAlex `is_retracted` false and Crossref `update-to` free of retraction notices; DOI-less items (arXiv-only) verify by arXiv id + S2 record. Success → `verified: true` with `verified_by`. Any mismatch → `verified: false`, `mismatches[]` populated; the packet is kept (except retracted) and marked; the agent must never "repair" metadata from memory. Crossref 403/429 → skip Crossref for the rest of the run, verify via OpenAlex, note once in the manifest.

---

## 11. `skills/research-scan/SKILL.md` (verbatim; only `<owner>` is substituted at packaging)

```markdown
---
name: research-scan
description: Find the 5–10 recent papers most likely to change a project's design, from a project brief or question. Runs multi-query scholarly retrieval (OpenAlex, Semantic Scholar, arXiv/PubMed), citation-graph expansion, rubric-based screening and reranking, DOI verification, and writes verified EvidencePacket JSON + Markdown into research/scans/. Use for project kickoff, novelty checks, "what should we know before building this", or "what's the latest research on X for this project" — not for manuscript citation management (use search-lit).
argument-hint: "<brief.md | \"question\"> [--top N] [--from YYYY-MM] [--slug name] [--domain behavioral|cs|biomed|general]"
context: fork
agent: general-purpose
background: false
allowed-tools: Bash(research-scan *), Read, Write, Edit, Glob, Grep
---

You produce a verified evidence scan for a project. You do the reasoning; the `research-scan` CLI does retrieval, expansion, shortlisting, verification and rendering. Never cite a paper that is not in the run's files; never edit paper metadata from memory. All CLI options go after the command; use `--json` on every call and read the JSON.

## 0. Preflight
1. `research-scan doctor --json`. Exit 3 → stop and report the failing checks verbatim (do not improvise around a missing key). Command not found → tell the user to run `uv tool install git+https://github.com/<owner>/research-scan` and stop.
2. Parse `$ARGUMENTS`: first token = brief file path or a quoted question; flags follow. Run `research-scan init <brief-or-question> <flags> --json`; keep the returned `run_dir` and `defaults`.

## 1. Plan queries
Read `<run_dir>/brief.md` and `${CLAUDE_SKILL_DIR}/references/plan-rubric.md`. Write `<run_dir>/queries.json` per `${CLAUDE_SKILL_DIR}/references/schemas.md`. Run `research-scan retrieve --run <run_dir> --json`. Exit 2 → fix `queries.json` per the reported errors and retry (max 2).

## 2. Screen
Follow `${CLAUDE_SKILL_DIR}/references/screen-rubric.md`. Read `<run_dir>/screen-batches/01.json`, `02.json`, … one at a time (Glob for the list), scoring every item. Write `<run_dir>/screen.json`. Run `research-scan expand --run <run_dir> --json`.

## 3. Screen expansion items
Read the batches listed in `<run_dir>/expanded.json.batches` (`screen-batches/x01.json`, …), score them, and rewrite `<run_dir>/screen.json` with all scores (round 1 + round 2). Run `research-scan shortlist --run <run_dir> --json`. Exit 2 → add the missing scores and rerun.

## 4. Rerank
Read `${CLAUDE_SKILL_DIR}/references/rerank-rubric.md` and `<run_dir>/shortlist.json`. Write `<run_dir>/ranked.json` for every shortlisted record. Run `research-scan verify --run <run_dir> --json` then `research-scan emit --run <run_dir> --json`.

## 5. Report
Return the `ScanSummary` JSON (`run_dir`, `evidence_json`, `top`, `counts`, `unverified`, `coverage_risks`) followed by its Markdown rendering: the top table (rank, title, year, evidence level, verified), the counts line (retrieved / deduped / expanded / screened≥2 / shortlisted / ranked / verified / emitted), any UNVERIFIED items, and one paragraph of coverage risks (queries with few hits, sources that failed, expansion that found nothing). Do not paste abstracts. Do not add papers.

## Rules
- Exclusions go in `queries.json.must_not`, never as NOT-terms in query text.
- Citation counts and venue prestige are not relevance. Contradicting papers are relevant.
- If a stage's JSON fails validation, fix the file; never bypass the CLI or edit CLI-owned files (`candidates.json`, `shortlist.json`, `manifest.json`).
- To change window, sources or top-N mid-run, edit `queries.json` / pass flags and re-run from the affected stage — stages are idempotent.
```

Frontmatter notes: `context: fork` keeps a long, file-heavy procedure out of the caller's context and makes it callable from any agent loop as one unit; `background: false` so callers (and `-p`) get the result in-turn; `allowed-tools` covers exactly the procedure. Fallback if the fork's tool set ever bites: remove `context: fork`; the body is unchanged.

---

## 12. Invocation surfaces

**Interactive Claude Code.** `/research-scan research/brief.md --top 10` — or Claude auto-invokes on matching intent (the description carries the triggers). Output lands in `./research/scans/<date>-<slug>/`. Cowork sessions do not read `~/.claude/skills`: enable the skill on the claude.ai account there.

**From an agent loop inside Claude Code.** Any subagent or workflow step invokes `/research-scan <brief>`; the fork returns the `ScanSummary`; downstream steps read `evidence.json`. A custom subagent in `.claude/agents/` can preload it via its `skills` field.

**Headless / scripts / CI.**
```bash
claude -p "/research-scan research/brief.md --top 10 --slug kickoff" \
  --allowedTools "Bash(research-scan *),Read,Write,Edit,Glob,Grep" \
  --output-format json \
  --json-schema "$(research-scan schema --name ScanSummary)" | jq '.structured_output'
```
Cost appears in `total_cost_usd`. For reproducible CI use `--bare` and load the skill as a plugin: `claude --bare -p "…" --plugin-dir /path/to/research-scan --allowedTools "…"` (bare mode skips skill discovery and needs `ANTHROPIC_API_KEY`).

**Python / other harnesses.** The CLI stages are model-free: a Python loop runs `init → (own model writes queries.json) → retrieve → (screen) → expand → (screen) → shortlist → (rerank) → verify → emit` with any model, reusing the rubric files. Codex and Cursor read the same `SKILL.md` (Agent Skills standard); point their skills dir at `skills/research-scan/`.

---

## 13. Eval (canon §9: golden set as the spine; independent judge)

`eval/golden/<topic>.yaml`: `brief`, `expected: [{doi, why}]` (5–8 papers you would be surprised to miss — **supplied or ratified by the maintainer, each Crossref-verified before commit; Claude Code may propose, never decide**), `exclusions`, `window`. V1 topics: (1) a behavioural/consumer topic; (2) an AI/CS topic the maintainer knows cold (LLM agents for literature search is a natural one); (3) a cognitive-neuro/biomed topic (routes PubMed). `research-scan eval --topic T --run DIR` computes recall@10 over the emitted top-10 and recall@25 over `ranked.json` in §10.4 order, and lists misses. Judged precision: `eval/judge.sh` calls `claude -p --model <judge> --json-schema` with `eval/judge-prompt.md` (a different, stronger model than the reranker — canon §3; per `fable-dispatch`, Fable 5 is the first-choice judge slot) to score each top-10 packet 0–3; `research-scan eval --judge <file>` merges it into `EvalResult`. Gate for adding a source or a stage (§16): it must move recall@25 or judged precision on this set. Run skill-creator triggering evals (should/should-not prompts) once, per the skills docs.

---

## 14. Acceptance criteria (Definition of Done for V1)

1. `uv tool install git+<repo>` on a clean macOS user account (and a second machine) → `research-scan doctor` exits 0 with OpenAlex + S2 keys; without S2 key it WARNs and exits 0; without OpenAlex key it exits 3 with an actionable message.
2. `/research-scan examples/brief.example.md` in a fresh Claude Code session completes end-to-end in ≤ 15 min, writes every §9 file, and returns a `ScanSummary` per §11.5.
3. Every packet in `evidence.json` has `verification.verified` true, or false with non-empty `mismatches` and the `[UNVERIFIED]` marker in `evidence.md`; no packet cid is absent from `candidates.json`; `emit` exits 2 on a `ranked.json` lacking `verification` (tests).
4. A known retracted DOI injected into a retrieval fixture never appears in `candidates.json`; one injected only at `verify` (S2-only hit) is dropped by `emit` and counted in `dropped_retracted` (tests).
5. `must_not` phrases never appear (word-boundary match) in emitted titles/abstracts (test).
6. Golden set: recall@10 ≥ 0.5, recall@25 ≥ 0.7, judged precision ≥ 0.8 (documented run committed under `eval/results/`).
7. `claude -p "/research-scan …" --output-format json --json-schema "$(research-scan schema --name ScanSummary)"` returns schema-valid `structured_output` (documented run).
8. Re-running any stage with unchanged inputs makes zero network calls (cache) and produces outputs identical after stripping the volatile fields `timestamps`, `duration_s`, `verified_on`, `cost_estimate_usd` (test with a fixed clock).
9. `pytest` green with sources mocked (respx); `ruff check` clean; no LLM SDK in `pyproject.toml`; no key string appears in any run dir or log (test greps a fake key); `references/schemas.md` equals `research-scan schema --md` (test).
10. README install section verified by a second person — ask for their pasted `doctor` output (self-report is a claim).

---

## 15. Implementation plan for Claude Code (vertical slices; each ends green and demoable)

Kick-off prompt (paste into a Claude Code session started with `claude --worktree research-scan` in a fresh clone):

> Read `research-scan-v1-spec.md` in full. Build V1 in the slices below, one PR-sized commit per slice, tests first where there is anything worth testing. Use uv, Python 3.13 (requires-python ≥ 3.11), pydantic v2, typer, httpx, respx. Do not add an LLM SDK. Do not scrape any website. Stop after each slice with the gate output.

- **S0 — scaffold + doctor (½ day).** `pyproject.toml`, package skeleton, `config.py`, `http.py` (client, backoff, rate limiter, sqlite cache), `schema.py` with all §9 models + `research-scan schema`, `doctor` (§8.6), `AGENTS.md`, `.env.example`, `.claude-plugin/plugin.json`. Gate: `doctor` green locally; `schema --md` renders `references/schemas.md`.
- **S1 — retrieve (1 day).** OpenAlex + S2 sources, dedup/cid, filters, caps, batches, `init`, `retrieve`; recorded fixtures for both APIs; tests for dedup, filters (incl. word-boundary `must_not`), caps/round-robin, cid stability. Gate: `retrieve` on `examples/brief.example.md` with a hand-written `queries.json` yields 150–250 candidates with abstracts for ≥ 80 %, and `screen-batches/` populated.
- **S2 — expand + shortlist + verify + emit (1 day).** S2 refs/cites/recs, OpenAlex fallback, out-of-window tagging, `expand`; `shortlist`; Crossref/OpenAlex `verify`; `select.py` + `render.py` + `emit`; manifest sections. Tests for selection rules, backfill, retracted-at-verify drop, unverified path, coverage validation. Gate: full CLI chain runs on hand-written `screen.json` / `ranked.json`.
- **S3 — the skill (½ day).** `SKILL.md` (§11 verbatim), three rubrics, `examples/`. Run `/research-scan examples/brief.example.md` end-to-end in a fresh session; fix schema friction the agent hits (this is where the exit-2 messages earn their keep). Gate: acceptance 2 + 3.
- **S4 — eval (½ day + the maintainer's curation).** Golden YAMLs (the maintainer ratifies expected DOIs), `eval`, `eval/judge-prompt.md` + `eval/judge.sh`, first documented run. Gate: acceptance 6, or a written note classifying misses as terminology gaps (→ plan-rubric edits) vs source gaps (→ §16 candidates).
- **S5 — packaging + install (½ day).** README, substitute `<owner>`, `uv tool install git+…` from a clean user account, `npx skills add <owner>/research-scan` or symlink path, `--plugin-dir` headless run. Gate: acceptance 1, 7, 10.
- **S6 — arXiv + PubMed routing (½ day, can trail).** Two extra sources behind `domain`; reuse search-lit's E-utilities patterns. Gate: doctor covers them; golden topic 3 routes PubMed.

Build guardrails: worktree-per-writing-session; before-commit gate `ruff check && pytest`; hooks may block writes of `.env`; no network in unit tests (respx only) — `pytest -m live` for doctor tests only.

---

## 16. Deferred, with triggers (the only deferred list)

| Item | Trigger to build |
|---|---|
| Parallel screening via subagents | verified that a forked skill can spawn subagents (or `context: fork` dropped); screening > 40 % of wall-clock |
| `frontier` mode (12-month window, arXiv/preprints weighted, newest-citing pass) | first real "what happened this year" request |
| `systematic` mode | a project needs a defensible corpus — prefer search-lit or Elicit SR API first |
| Elicit as retriever | eval shows a recall@25 gap Elicit closes (needs Pro) |
| Exa `publication` | same gate; different-terminology recall |
| Embedding prefilter (S2 SPECTER2 via API) | screening tokens > ~30 % of run tokens |
| OSF direct / Europe PMC / SSRN | doctor's PsyArXiv coverage probe fails, or a topic misses preprints |
| Multi-hop expansion | ScholarQuest-style misses on adjacent-community topics |
| MCP server wrapper | an agent loop needs typed tool-calls rather than a skill |
| Plugin marketplace entry | a second consumer beyond the first (a sibling project's precedent: symlink v0.1 → plugin later) |

---

## 17. Sources consulted (this session)

Ai2 Paper Finder — https://allenai.org/blog/paper-finder · https://github.com/allenai/asta-paper-finder · PaSa — https://ar5iv.labs.arxiv.org/html/2501.10120 · ScholarQuest (2026) — https://arxiv.org/html/2606.20235v1 · Rethinking Literature Search Evaluation / RollingEval — https://arxiv.org/html/2605.29234v1 · OpenAlex works API — https://developers.openalex.org/api-reference/works/list-works · OpenAlex keys/pricing — https://casrai.org/news/openalex-api-keys-mandatory-usage-based-pricing-2026 · Semantic Scholar API tutorial — https://www.semanticscholar.org/product/api/tutorial · S2 release notes (discontinued) — https://github.com/allenai/s2-folks/blob/main/API_RELEASE_NOTES.md · Elicit API — https://docs.elicit.com/ · https://elicit.com/blog/the-elicit-api-and-mcp-powering-autonomous-research-engines · Exa publications — https://exa.ai/blog/publications-search · Web of Science Starter — https://developer.clarivate.com/apis/wos-starter · Scopus access — https://pybliometrics.readthedocs.io/en/stable/access.html · OSF preprints API usage — https://zitniklab.hms.harvard.edu/ToolUniverse/_modules/tooluniverse/osf_preprints_tool.html · Claude Code skills — https://code.claude.com/docs/en/skills · headless — https://code.claude.com/docs/en/headless · plugins reference — https://code.claude.com/docs/en/plugins-reference · search-lit skill (uploaded `.skill`, SKILL.md only).
