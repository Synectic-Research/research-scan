# research-scan

Find the 5–10 recent papers with the highest impact on a research question, topic or project,
starting from a brief or a one-line question.

The work is split in two, deliberately.

**The CLI is deterministic and model-free.** It retrieves across OpenAlex, Semantic Scholar and
arXiv, walks the citation graph, dedups, counts coverage per criterion, shortlists, verifies every
DOI against the live record, applies the selection rules and renders the result. It contains no LLM
SDK and makes no judgement about a paper.

**The skill supplies the cognition.** Planning the queries, scoring each candidate 0–3, writing gap
queries when coverage is thin, and reranking the shortlist are all model decisions, made against
rubrics that ship as plain Markdown in `skills/research-scan/references/`. Whatever agent hosts the
skill executes them.

Files are the interface between the two halves, which is what lets Claude Code, Codex, Cursor or a
plain Python loop drive the same chain over the same artifacts.

Two things bound the result. A **purpose** — `build`, `research` or `orient` — decides what a paper
has to do to earn a slot. A **profile** — `quick`, `standard` or `deep` — decides how much the scan
costs. Both are described under [How it works](#how-it-works).

Output is a run directory of validated JSON plus a Markdown brief you can hand to a human, in which
every paper's DOI, title, year and first author were checked against the live record.

## Install

Python ≥ 3.11 and [uv](https://docs.astral.sh/uv/).

```bash
uvx research-scan doctor          # run any command without installing
uv tool install research-scan     # or put it on PATH permanently
```

## Configure

`configure` asks for each credential, shows what is already set, writes
`~/.config/research-scan/.env` with mode `0600` inside a `0700` directory, and finishes by running
`doctor`.

```bash
research-scan configure          # `setup` is an alias for the same command
```

Keys are read without echo. Re-running is safe: every variable shows its current value masked to the
last four characters, Enter keeps it, typing replaces it. Anything already in the file that
`configure` does not ask about — comments included — is left exactly as it was. If stdin is not a
terminal it prints the file to write and exits 2 rather than hanging, which is the behaviour you
want in a Dockerfile or a provisioning script.

| Variable | Needed for |
|---|---|
| `OPENALEX_API_KEY` | OpenAlex, the primary source. **Required**; `doctor` exits 3 without it. |
| `OPENALEX_MAILTO` | Strongly recommended. Raises OpenAlex to 5 req/s and joins the Crossref polite pool. |
| `S2_API_KEY` | Recommended. Semantic Scholar search and citation-graph expansion work without it, throttled to roughly a third of the rate; `doctor` warns. |
| `NCBI_API_KEY` | Optional. PubMed only: 10 req/s instead of 3. |

To write the file by hand instead, `.env.example` in the repo is the template. Process environment
beats `~/.config/research-scan/.env`, which beats a repo-local `./.env`.

## Check it works

`doctor` invokes every source live with the cache bypassed, rather than listing what it thinks is
configured.

```bash
research-scan doctor             # a four-line summary and a verdict
research-scan doctor --verbose   # every check, with timings and paths
research-scan doctor --json      # machine-readable; this is the CI/agent interface
```

```
Research Scan <version>
✓ configuration
✓ OpenAlex   ✓ Semantic Scholar   ✓ Crossref   ✓ arXiv   ✓ PubMed
✓ writable run store
Ready.
```

Exit 0 means go. Exit 3 means a mandatory check failed; see [Troubleshooting](#troubleshooting). The
checks and the exit code are identical in all three output modes — only the presentation differs.

## Your first scan

With the skill installed, ask for a scan in your agent:

```
/research-scan "what is the strongest recent evidence that default enrolment changes how much
                people save?" --profile quick
```

A one-line question works. A brief works better, because the planning step maps each section of it
onto a specific part of the search plan. The template is
`skills/research-scan/examples/brief.example.md` — a worked `build` brief — and
`brief.research-example.md` is the same template at `Purpose: research`.

```
/research-scan research/my-brief.md --profile standard --top 10
```

| Brief section | What it feeds |
|---|---|
| **`Purpose:` line** | Which sub-criteria the plan derives and what `why_it_matters` must argue. `build`, `research` or `orient`; omit it and the agent infers one. |
| **What this is about** | The `brief_summary` and the domain routing. Say the setting, not just the topic. |
| **What we need to decide or answer** | The sub-criteria every paper is scored against. Name the actual open choices, or the actual questions. |
| **What we already believe (the premise)** | The `contradictory` query. A scan that only confirms the premise is not evidence. |
| **Exclusions** | `queries.json.must_not`, enforced in code at word boundaries — never as NOT-terms in query text. |
| **Known papers or authors** | `anchors`: pinned into the pool, exempt from the filters and the cap, always used as expansion seeds. |

Results land in `research/scans/<YYYY-MM-DD>-<slug>/`. See [Outputs](#outputs).

Full argument list:

```
/research-scan <brief.md | "question"> [--profile quick|standard|deep] [--top N] [--foundational N]
                                       [--from YYYY-MM] [--to YYYY-MM] [--slug name]
                                       [--domain behavioral|cs|biomed|general]
                                       [--max-candidates N] [--per-query N]
```

## Connect your agent

Two front doors to the same pipeline. The skill is where the rubrics live, so it is the one that
carries the screening and reranking cognition; the MCP server exposes the same four decision points
as tools for any client that speaks MCP.

### Claude Code — the skill

Any one of these; all three point at the same `skills/research-scan/`.

```bash
# 1. symlink a clone — edits to the rubrics take effect immediately
ln -s "$PWD/skills/research-scan" ~/.claude/skills/research-scan

# 2. load the repo as a plugin, per invocation (it carries .claude-plugin/plugin.json)
claude --plugin-dir /path/to/research-scan

# 3. skills CLI
npx skills add Synectic-Research/research-scan
```

### Any MCP client — stdio

`research-scan mcp` speaks MCP on stdin/stdout and nothing else. It reads no token and needs none:
the process is trusted because your client launched it. Nothing extra to install — the server
ships with the package.

```json
{
  "mcpServers": {
    "research-scan": {
      "command": "uvx",
      "args": ["research-scan", "mcp"]
    }
  }
}
```

| Client | Where that goes |
|---|---|
| Claude Code | `.mcp.json` in the project root |
| Claude Desktop | `claude_desktop_config.json` |
| Cursor | `.cursor/mcp.json` |

Four tools, one per model decision the pipeline needs: `scan_start` (you supply the query plan),
`scan_continue` (screening scores, gap queries, or a page of rerank entries), `scan_verify` and
`scan_result`. The stage order, the artifacts and every judgement are the same as the skill's — the
adapter drives the CLI as a subprocess and reads its exit codes. Run `research-scan mcp --help` for
the other transport.

## How it works

```
brief ─▶ [plan queries] ─▶ retrieve ─▶ [screen 0–3] ─▶ expand ─▶ [screen] ─▶ coverage
      ─▶ [gap round, if coverage is thin] ─▶ shortlist ─▶ [rerank] ─▶ verify ─▶ emit
```

Bracketed steps are the agent's; the rest are CLI stages. Each stage is idempotent and re-runnable:
change `queries.json` or pass a flag and re-run from the stage it affects. The CLI owns
`candidates.json`, `shortlist.json`, `manifest.json` and `evidence.*`; the agent owns
`queries.json`, `screen.json` and `ranked.json`. Neither edits the other's files.

### Purpose

Declared on the brief's `Purpose:` line, or inferred. It decides which sub-criteria the plan derives,
what screening counts as relevant, and what `why_it_matters` has to argue.

| Purpose | A paper earns its place by | Example |
|---|---|---|
| `build` | moving a design or plan decision | "What should we know before we design the enrolment flow?" |
| `research` | changing what we believe, what we would test, or how we would measure it | "What is the strongest recent evidence that default enrolment affects how much people save?" |
| `orient` | being something a newcomer must know, recent first | "I am new to mechanistic interpretability — what must I read, recent first?" |

### Profiles

One flag sets how much the scan costs. `--profile` belongs to `init` and is recorded in the manifest;
an explicit flag still overrides it — `--per-query 60` means 60 whatever the profile says.

| Profile | Per query | Pool cap | Out-of-window total | Gap round |
|---|---|---|---|---|
| `quick` | 20 | 250 | 12 | never |
| `standard` (default) | 40 | 450 | 20 | when coverage is uneven |
| `deep` | 40 | 450 × sources ÷ 2 | 30 | always |

The out-of-window total is a budget for the whole run, not a per-stage allowance. Start at
`standard`; use `quick` for "what is out there" and `deep` when a miss is expensive. Measured recall
for each is under [Measured results](#measured-results).

### The gap round

Runs at most once, and on `standard` only when `coverage` reports that the criteria are unevenly
covered or that a query came back nearly empty — otherwise it is skipped and the report says so.
`coverage` counts, per sub-criterion, how many papers screening kept; the agent writes one or two
queries against the criteria that came back thinnest; `retrieve --round 2` and `expand --round 2`
add what they find. Round 1's papers and their scores are never discarded — the pool only grows.

## Supported sources

| Source | Used for | Status |
|---|---|---|
| **OpenAlex** | Primary search, metadata, retraction flag, graph fallback | Implemented. Requires a key. |
| **Semantic Scholar** | Search, and citation-graph expansion over references, citations and recommendations | Implemented. Key optional, throttled without one. |
| **arXiv** | Extra source for `cs`, and for `general` when a query is a method query | Implemented. |
| **PubMed** | Routed for `biomed` | **Routed but not built yet.** A biomed scan runs on OpenAlex + Semantic Scholar and records `unavailable: true` in `manifest.json` — routed-but-missing is recorded, never dropped quietly. |
| **Crossref** | DOI verification only; never a retrieval source | Implemented. Verification degrades to OpenAlex if it is unreachable. |

`--domain` picks the routing: `behavioral` and `general` → OpenAlex + Semantic Scholar; `cs` → those
plus arXiv; `biomed` → those plus PubMed. `--sources` overrides the map outright.

## Measured results

Two curated golden topics — behavioural economics and LLM literature-search agents — scored at the
candidates stage and by an independent judge model. These are two topics, not a benchmark against
other tools.

| Profile | Candidates screened | Recall (topic 1 · topic 2) | ≈ wall clock |
|---|---|---|---|
| `quick` | ~355 | 7/10 · 4/6 | 20–25 min |
| `standard` | ~570 | 8/10 · 5/6 | 35–40 min |
| `deep` | 575–805 | 9/10 · 5/6 | 40–55 min |

Judged precision of the in-window top 10: **0.875 on both topics**, by an independent judge.

Recall climbs with the pool and efficiency falls with it: `quick` returns 0.199 recall per 100
candidates screened on topic 1 where `deep` returns 0.157. What separates the profiles most is the
out-of-window budget (12 / 20 / 30) — topic 1's remaining misses are all pre-window classics, and
each step up admits one more.

Full tables, what was tried and reverted, and the rules the numbers obey:
[`docs/measurements.md`](docs/measurements.md).

## Outputs

Everything lands in `research/scans/<YYYY-MM-DD>-<slug>/`:

| File | What it is |
|---|---|
| `evidence.json` | The deliverable: one `EvidencePacket` per paper — metadata, rerank scores, key finding, why it matters, limitations, and the verification record. |
| `evidence.md` | The same list rendered for a human. Foundational classics render after the current work, ranks running straight through, so a 2004 paper reads as context rather than as the answer. |
| `evidence.bib` | BibTeX for the emitted papers. Suppress with `--no-bib`. |
| `manifest.json` | The audit trail. Every drop — retracted, `must_not`, type filter, pool cap — and every source that failed after retries is counted here. Nothing is capped silently. |
| `coverage.json` | Per sub-criterion, how many kept papers cover it, split by query type and source, plus per-query yield and per-seed expansion precision. One snapshot per round, so what the gap round recovered is a delta. Rendered as a Coverage section in `evidence.md`. |
| `queries.json`, `candidates.json`, `screen.json`, `expanded.json`, `shortlist.json`, `ranked.json` | The intermediate stages, all schema-validated. |
| `retrieval.log.jsonl`, `expansion.log.jsonl`, `verify.log.jsonl` | Per-stage structured logs. |

A paper whose DOI did not resolve, or whose title, year or first author disagreed with the live
record, is **flagged, not silently repaired**: it ships with `mismatches[]` and an `[UNVERIFIED —
check manually]` marker. Only retraction removes a paper.

Print any data contract with `research-scan schema --name <Model>`, or all of them as Markdown with
`research-scan schema --md`.

## Cost and time

Wall clock tracks the candidate pool, because screening is the long pole. Measured end to end
(`counts.wall_clock_s`, `init` → `emit`):

| Pool | Screening batches | Wall clock |
|---|---|---|
| ~675 candidates — cs, 3 sources at the default cap | ~27 | **37 min** |
| ~250 candidates — 2 sources at the default cap | ~10 | **22 min** |
| ~120 candidates — `--max-candidates 120` | 5 | **19 min** |

OpenAlex bills ≈ $0.008 either way — `per_page` is free depth, so pool size costs almost nothing in
API money.

**Agent tokens are the real cost**, and they do not fall as fast as the pool does: the 120-candidate
run still cost ≈ $5.70 in frontier-model tokens and ran only 3 minutes quicker than the
250-candidate one, because reranking (52 full records, regardless of pool size) and fixed stage
overhead dominate once screening is small. `--max-candidates` is the right dial for a runaway cs
pool, not a way to make a scan cheap.

The default cap scales with the number of built sources (450 × n/2, so 675 for cs, 450 for two).
`--max-candidates` and `--per-query` belong to `retrieve` and override it per run. Both are run
flags, not config.

## Headless

The skill returns a `ScanSummary`, so a scan can run unattended and hand structured JSON to whatever
comes next:

```bash
claude -p "Use the research-scan skill to scan brief.md with --slug nightly --top 5. \
           When it finishes, return its ScanSummary as your final answer." \
  --plugin-dir /path/to/research-scan \
  --allowedTools "Bash(research-scan *),Read,Write,Edit,Glob,Grep" \
  --output-format json \
  --json-schema "$(research-scan schema --name ScanSummary)" \
  > scan.json

jq '.structured_output.counts' scan.json
```

**Ask for the skill in prose; do not use a bare `/research-scan …` slash command here.** The skill
declares `context: fork`, so a bare slash command runs entirely inside the fork and the session
returns `num_turns: 0` with `result: "Command completed"` — the scan succeeds and writes its run
directory, but there is no top-level assistant turn for `--json-schema` to bind to and
`structured_output` comes back `null`. Phrasing it as an instruction makes the session invoke the
skill, receive the fork's report and emit the `ScanSummary` itself, which is what the schema
attaches to. Verified both ways on 2026-08-19.

Two more flags to get right:

- `--plugin-dir` is unnecessary if the skill is already installed under `~/.claude/skills/`. Never
  combine it with `--bare`: bare mode skips `--plugin-dir`, so the skill would not load at all.
- `--allowedTools` must carry `Bash(research-scan *)`, `Read`, `Write`, `Edit`, `Glob` and `Grep`.
  `Glob` is not optional — the skill globs `screen-batches/` to find the batches to score.

## Not for

**Systematic reviews.** There is no PRISMA trail and no workflow for screening thousands of records.

**Manuscript citation management.** `evidence.bib` is a courtesy, not a library. Use a citation
manager.

**Full-text work.** Retrieval and screening run on titles, abstracts and metadata. No PDF is
fetched, parsed or read.

**Google Scholar, Scopus, Web of Science, PsycInfo** are not sources and are not planned: none
offers a personal-key API or a ToS-compatible path.

## Troubleshooting

**`doctor` exits 3.** A mandatory check failed — read the check name and fix that, rather than
working around it. A missing `OPENALEX_API_KEY` is a `FAIL`, and the OpenAlex probes are then
reported as `SKIP` rather than as passing, because they were never run. A missing `S2_API_KEY` or
`NCBI_API_KEY` is only a `WARN`: the scan still runs, throttled. The default output names what to
do; `--verbose` gives the full check list with timings, and `--sources openalex,s2` narrows what is
checked.

**Reading `doctor` from a script or an agent.** `doctor --json` is the interface, and its keys are
stable. `ready` is the boolean, `providers` maps each checked source to `ok` / `warn` / `fail` /
`skip` — `skip` meaning the probe never ran, which is never the same as passing — and `checks`
carries every individual result. The exit code is the same in all three output modes.

**`arxiv HTTP 429, cs/physics routing skipped`.** arXiv rate-limits aggressively (the client already
holds to 1 request / 3 s) and returns 429 under load. This is a `WARN`, not a failure: cs scans fall
back to OpenAlex + Semantic Scholar, which carry arXiv preprints anyway — you lose the same-day
listings and one origin signal, not coverage. Re-run later if recency matters; per-source query
counts and failures are in `manifest.json` under `retrieval.per_source`.

**Semantic Scholar backlog.** S2 answers 429/503 when its queue is deep. `http.py` retries and then
returns the last response rather than raising — a bad status is data. Graph expansion falls back to
OpenAlex's bare-id reference list, which works but cannot be ranked (ordering it would cost a
metadata fetch per reference), so expansion recall drops. `expansion.log.jsonl` records it per call.

**A stage exits 2.** An agent-written file failed validation. The error lists every offending path;
unknown keys are rejected everywhere, so a typo surfaces instead of being swallowed. Fix the file and
re-run that stage.

**`research-scan mcp` cannot import the server.** `fastmcp` is a core dependency, so this means an
incomplete install rather than a missing option — reinstall with `uv tool install research-scan`.
`research-scan version --json` reports `"mcp": "enabled"` on an intact install.

## Shell completion

```bash
eval "$(research-scan completion bash)"   # add to ~/.bashrc
eval "$(research-scan completion zsh)"    # add to ~/.zshrc
research-scan completion fish > ~/.config/fish/completions/research-scan.fish
```

## Development

```bash
git clone https://github.com/Synectic-Research/research-scan
cd research-scan
uv sync
uv run ruff check && uv run pytest -q     # the before-commit gate
uv run pytest -m live                     # the only tests that touch the network
uv tool install --editable .              # put research-scan on PATH, tracking the working tree
```

`src/research_scan/schema.py` is the source of truth: it generates the JSON Schema, the contract
docs the agent reads (`skills/research-scan/references/schemas.md` — regenerate it in the same
commit, a test compares them), and the exit-2 error messages.

`AGENTS.md` holds the operating doctrine, [`docs/measurements.md`](docs/measurements.md) the
measured results behind the current defaults, and `eval/` the golden-set harness
(`research-scan eval --topic <t> --run <dir>`).

[`CONTRIBUTING.md`](CONTRIBUTING.md) · [`SECURITY.md`](SECURITY.md) ·
[`CHANGELOG.md`](CHANGELOG.md) · [`CODE_OF_CONDUCT.md`](CODE_OF_CONDUCT.md) ·
[`CITATION.cff`](CITATION.cff) · [`LICENSE`](LICENSE) (Apache-2.0)

Dependencies keep their own licenses; [`THIRD_PARTY_LICENSES.md`](THIRD_PARTY_LICENSES.md) says what
they are and how to regenerate the table.
