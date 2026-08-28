# AGENTS.md — research-scan

Operating doctrine for this repo. Spec of record: `research-scan-v1-spec.md` — read the relevant
section before changing behaviour it defines. Section references below (`§9`, `§10.4`) are to it.

## Vocabulary

- **run** — one scan. A directory `research/scans/<YYYY-MM-DD>-<slug>/` holding every stage's file,
  relative to the process's cwd: the repo for a local scan, `$RESEARCH_SCAN_MCP_DATA/<scan_id>/`
  for one driven through the MCP adapter.
- **cid** — stable candidate id: first 12 hex of sha1 of the primary identifier, in the priority
  order doi > arxiv > pmid > `norm(title)+year` (§8.2). The join key across every file.
- **origin** — one discovery path that found a candidate (`query`, `references`, `citations`,
  `recommendations`). A paper keeps every origin it earns; origin count is a ranking signal.
- **in-window / outside-window** — inside the publication window, or an expansion reference from
  before it. Out-of-window papers are tagged, never dropped, and fill the `foundational` slots.
- **[A] stage / [C] stage** — a stage the agent performs under a rubric, versus one the CLI performs
  deterministically. `plan`, `screen`, `rerank` are [A]; everything else is [C].
- **verified / flagged** — a packet whose DOI resolved and whose title, year and first author match
  the live record, versus one kept with `mismatches[]` and an `[UNVERIFIED]` marker. Never silent.
- **purpose** — `build | research | orient`, declared on the brief's `Purpose:` line or inferred by
  the planner and written into the first sentence of `brief_summary`. Decides what counts as impact:
  which `sub_criteria` set is derived, what `why_it_matters` must argue, what screening rewards, and
  how the judge reads relevance. Not a schema field — it lives in prose, on purpose.
- **profile** — `quick | standard | deep`, chosen at `init` and recorded in `manifest.defaults`.
  Sets per-query depth, the pool cap, the out-of-window **total for the run**, and whether the gap
  round runs. Flags still override it.
- **gap round** — V1.1's one extra retrieval round, aimed by `coverage.json` at the sub-criteria
  round 1 covered thinnest. `queries.json.round2` holds its queries, `rNN`/`xrNN` its batches. It
  runs exactly once; "round 1 / round 2" already means the *screening* passes, hence the name.
- **slice** — S0…S6 in §15. One slice = one commit = one demoable gate.

## Commands

```bash
uv sync                                  # environment
uv run ruff check && uv run pytest -q    # the before-commit gate; both must be clean
uv run ruff format                       # canonical formatting (line length 100)
uv run pytest -m live                    # the only tests that touch the network (doctor)
uv run research-scan doctor              # readiness gate: invokes every source, exit 0 or 3
uv run research-scan schema --name ScanSummary   # one JSON Schema
uv run research-scan schema --md > skills/research-scan/references/schemas.md

# the whole chain; [A] marks the steps the agent does, not the CLI
uv run research-scan init skills/research-scan/examples/brief.example.md --slug smoke \
    --profile standard --json           # quick | standard | deep — the cost/recall dial
cp skills/research-scan/examples/queries.example.json research/scans/<run>/queries.json  # [A]
uv run research-scan retrieve --json      # add --no-cache to force fresh calls
#   [A] write screen.json from screen-batches/NN.json
uv run research-scan expand --json
#   [A] rewrite screen.json with the xNN batches added
uv run research-scan coverage --json        # per-criterion coverage + the gap-round verdict
#   read coverage.json.gap_round.should_run — false means skip the round and say why
#   [A] write queries.json.round2 against the thin criteria
uv run research-scan retrieve --round 2 --json   # appends; never evicts round 1
#   [A] score the rNN batches, rewrite screen.json
uv run research-scan expand --round 2 --json     # seeds from the gap round's own additions
#   [A] score the xrNN batches, rewrite screen.json
uv run research-scan shortlist --json
#   [A] write ranked.json from shortlist.json
uv run research-scan verify --json        # --strict raises the title bar to 95
uv run research-scan emit --json          # --top / --foundational / --contradicting / --no-bib

# the MCP server — one server object, two transports (see ## Boundaries for the data root)
uv run research-scan mcp                  # stdio: no token, no port, for a local agent runner
uv run research-scan mcp --http           # HTTP: needs RESEARCH_SCAN_MCP_TOKEN, binds loopback
uv run research-scan-mcp                  # the HTTP console script; _HOST / _PORT / _LOG override

# the entry surface
uv run research-scan configure            # interactive credential setup (alias: setup)
uv run research-scan version --json       # version, runtime, MCP availability
uv run research-scan completion zsh       # eval-able completion script

# eval, once a golden topic exists
uv run research-scan eval --topic <topic> --run <run-dir> --json
./eval/judge.sh <judge-model> <run-dir>   # spends judge tokens; model choice is the maintainer's
```

Regenerate `schemas.md` in the same commit as any change to `schema.py` — a test compares them.
The rubrics quote its field tables, so check them too when a contract moves.

## Boundaries

- **No LLM SDK in this package.** No `anthropic`, no prompts, no model calls in `src/`. Every
  judgment belongs to whatever drives the CLI. This is the property that makes the tool
  harness-agnostic. Amended at v0.6.0, in wording only: the ratified doctrine is "Research Scan
  core never depends on a model; optional cognition engines are explicit, replaceable,
  provenance-recorded, contract-bound, opt-in; default `engine=none`". `drivers/` holds one such
  engine as a repo-only reference — it is outside the package, carries its own `pyproject.toml`
  and `uv.lock`, is excluded from the sdist and was never in the wheel, and the package's own
  dependency list is byte-unchanged by it. The typed interface that would make an engine a
  supported surface has not shipped; until it does, the README's identity line does not move
  (`PLUGGABLE_COGNITION_ENGINE`).
- **Dependencies are the §5 list** (`httpx`, `pydantic`, `typer`, `rapidfuzz`, `pyyaml`; dev
  `pytest`, `respx`, `ruff`). Adding one needs a reason a slice actually proved. Amended at v0.3:
  `fastmcp` and `uvicorn`, exact-pinned, for the MCP server. Amended again at v0.5: they moved from
  the `mcp` extra into core, because MCP is a first-class surface and an extra made the documented
  client config depend on an incantation (`uvx --from 'research-scan[mcp]' …`) that people were
  always going to get wrong. `mcp = []` stays as an empty extra so existing invocations keep
  resolving. **The engine still imports neither** — `cli.py` imports `mcp_server` inside the `mcp`
  command body, never at module scope, so no other command pays fastmcp's import cost.
- **No scraping.** Documented APIs only. Sources beyond §7 are deferred until their §16 trigger.
- **Credentials only via `config.py`.** Nothing else reads `os.environ` for a key, so
  `Settings.redact()` sees every secret before anything is logged or cached.
- **Only `http.py` talks to the network.** Unit tests use `respx`; no test outside `-m live` opens
  a socket.
- **The CLI owns `candidates.json`, `shortlist.json`, `manifest.json`, `evidence.*`.** The agent
  owns `queries.json`, `screen.json`, `ranked.json`. Neither edits the other's files.
- **One session holds `main`; any other session works on a branch.** Two sessions were live on
  `main` on 2026-08-20 and the tip was *amended* under an active reader — the same subject came back
  under a new SHA mid-slice. An amend is a rewrite, so a concurrent writer can silently drop work
  that was already committed, and any SHA read a minute ago may no longer exist. This is the
  portfolio's single-writer rule, recorded here because this repo broke it: identify a commit by
  subject and diff, never by a remembered SHA, and branch when you are not the holder.
- **A version bump moves four files at once**: `pyproject.toml`, `.claude-plugin/plugin.json`,
  `CITATION.cff` and `server.json` (both its `version` and `packages[0].version`), plus a
  `## [X.Y.Z]` section in `CHANGELOG.md` that becomes the GitHub Release body. CI fails the build
  when they disagree, naming the file. Releases are cut by pushing a single tag ref — never
  `git push --tags`, which would push the private-era tags this repo still carries locally. The MCP
  registry publish stays manual so the Ed25519 domain key never enters CI. `RELEASING.md` is the
  procedure.
- **Never amend, rebase or force-push history that is already on `origin/main`.** `main` is
  single-writer *across sessions* and another agent or terminal may already have fetched or built
  on a commit; rewriting it collides with them silently. This was learned the hard way: v0.2.5's
  second commit was amended after its docs were finished and the rewrite hit another active
  session. A cleanup after a push goes on a branch, or waits for the next commit. Before a push,
  amend freely.
- Paths are fixed: `~/.config/research-scan/.env`, `~/.cache/research-scan/http.sqlite`, and for
  the MCP adapter only `$RESEARCH_SCAN_MCP_DATA` (default `~/.local/share/research-scan-mcp/runs/`),
  one directory per `scan_id`.
- **The MCP adapter shells out to the CLI**; it never imports a stage's internals. `mcp_server.py`
  holds tools, auth, validation, the `scan_id` → run-directory mapping and deterministic bridging,
  and no judgement about papers. Its one server-owned file, `mcp-options.json`, sits beside the run
  directory rather than inside it and holds deferred CLI flags only — never phase, which is always
  derived from the run's own artifacts.

## Done-state

A slice is done when `ruff check` and `pytest -q` are clean, the slice's gate in §15 has been run
and its output pasted, and the commit is one slice. Beyond that, V1 is done against §14 — the
acceptance list is the definition, not a summary of it.

Current state: **S0–S5 complete, V1.1 as v0.2.0, the simplification slices as v0.2.1–v0.2.3** — the whole
CLI chain runs, `init` through `emit`, with the gap round between screening and shortlist; the skill and its rubrics are
installed; `eval` scores a run against a golden topic; and the repo ships with a README, a version
tag and a documented acceptance run. arXiv landed early in S10g; what is left of S6 is PubMed
routing. Every registered command works, so `--help` never advertises vapour.

**Surfaces.** Remote-MCP portable; claude.ai transport proven end-to-end. Claude Code is the
established local surface. Cowork uses the same MCP/Skill architecture but was not separately
acceptance-tested.

**Golden-set status is the maintainer's alone.** `defaults-savings` is `ratified-with-caveat` (its
sampling-bias note is the caveat), `llm-lit-search` is `ratified`, topic 3 is a `draft` template.
Claude Code proposes and resolves DOIs live; it never promotes a topic. `eval` warns on any topic
that is not plainly `ratified`, and a test requires every entry of a promoted topic to carry a `why`.

**V1.1 (v0.2.0) — what shipped, and what did not.** Three items, each measured before it shipped;
every table is in `docs/measurements.md`.

- **Shipped: the coverage-driven gap round.** `criteria_hit` on screen entries, a deterministic
  `coverage` command, `retrieve --round 2` / `expand --round 2`. Topic 1 candidates recall
  8/10 → **9/10** (Carroll 2009, via a gap-round paper's bibliography); topic 2 unchanged at 5/6.
  Two things the design did not anticipate: a flat "fewer than 5 hits" threshold never fires on a
  real pool (the thinnest criterion on either topic is 12 of 104 and 301 kept papers), so the
  *agent* also targets the least-covered criterion; and the gap round needs its own out-of-window
  budget, because round 1's twenty slots go to methodology classics.
- **Shipped: the two rerank guards.** An off-domain cap in `rerank-rubric.md` and a relevance floor
  on the `review` selection guarantee. Both papers the S5 judge scored 1 leave the top 10, each
  replaced by a golden-set paper, with every judge-3 packet still in place. The `select.py` half
  alone is a zero-line diff on both reference runs — it ships as a guard; the rubric is the fix.
- **Tried, not shipped: full-bibliography expansion for anchors.** It does what it says (LitSearch
  30 → 41 references, a defaults meta-analysis 30 → 88) and buys no recall on either topic. The
  deciding arm: with the expansion caps lifted, the *per-seed slice* reaches 10/10 on topic 1 with
  byte-identical origins. All of the gain was the cap and none of it was the anchor branch, so the
  branch was reverted.
- **Still open, from the S5 judge:** the committed `foundational` judge scores predate the prompt
  that should have produced them (`eval/judge-prompt.md` now scores canonicity). Re-judge before
  quoting them.

**v0.2.1 — profiles, a bounded out-of-window total, a conditional gap round.** Robustness and
bounded cost, no new mechanisms. Measured profile table in `docs/measurements.md`:
`quick` 7/10 and ~~6/6~~ 4/6, `standard` 8/10 and 5/6, `deep` 9/10 and 5/6 on the two golden
topics, at pools of ~350, ~570 and 575/805. Three things that came out of measuring it:

- **The V1 acceptance table was never one setting.** `2026-08-19-s3-e2e` ran at per_query 20 /
  cap 250 — `quick` depth — and `2026-08-19-topic2b` at 40 / 675 — `deep`. Eval results are keyed
  by profile now so it cannot recur, and `EvalResult` carries `pool_size`, `wall_clock_s` and
  `recall_per_100_screened` so a recall number always ships with what it cost.
- ~~**`quick` beats `deep` on topic 2**~~ — **withdrawn at v0.2.2.** That 6/6 came from a run where
  arXiv failed all eight queries (`per_source.arxiv: 0 hits, 8 failed`, 29 × HTTP 429). Two clean
  re-runs give **4/6** at the same pool. Recall is monotone in the profile on both topics.
- **Tried, not shipped: the out-of-window ranking key** (in-window seeds, then log velocity). An
  exact no-op — identical ordering position for position. `log1p` is monotone, and every seed is
  in-window unless the user anchored a classic, in which case the restriction would demote the
  very references they pinned. Reverted.

**v0.2.2 — the two-profile collapse, measured and rejected.** A candidate `standard` of
20 / 250 / 12 plus the gap trigger was built and measured against the rule "recall ≥ current
`standard` on both topics with pool ≤ 420". It returned **7/10 at a pool of 521** and **4/6 at
619** — failing both terms on both topics — so the three profiles stay and the candidate was
reverted. What the run showed: the gap round reports `out: 0` once round 1 has spent the
out-of-window total, and every paper topic 1 still misses is pre-window, so no amount of extra
querying can reach them. **`standard` earns its place on its out-of-window budget of 20, not on its
query depth.** The three profiles are three points on one curve — 12, 20, 30 slots — and the middle
one is load-bearing.

**v0.2.3 — per-seed round-robin for out-of-window admissions: measured and reverted.** V1.2
candidate #1, built and A/B'd on the same retrieval pools at all three profiles. The pool held
identical in all six cells and topic 2 did not move, but topic 1 lost three golden papers at every
profile (7/10 → 4/10, 8/10 → 5/10, 9/10 → 6/10), so the no-drop condition failed and it was
reverted. Madrian & Shea 2001 — **4 seed links, global position 1** in the out-of-window set —
is dropped by round-robin, because every seed's rank-0 paper is admitted before any seed's rank-3
paper. The admitted set went from "every paper cited by ≥ 2 seeds" to "16 of 20 cited by exactly
one", and distinct seeds represented rose only 10 → 11 of 15.

The lesson, which is the durable part: **fair-share admission helps when the producers are
interchangeable and hurts when agreement between producers is itself the signal.** Queries are
interchangeable, so §8.4's round-robin over them is right and stays. Seeds are not — they all come
from the same screened-relevant set, so two seeds citing the same classic is consensus, not
redundancy.

**v0.2.3 measured on two topics; re-measure on topic 3 when the golden generator lands — reinstate
only if it wins there.** The literal caveat the maintainer asked for was written for a shipping change; the
change did not ship, so it applies to the *revert*: this decision also rests on two topics, one of
which (topic 2) is structurally blind to the policy because its remaining misses are in-window. A
third topic could overturn it in either direction.

**Defaults are frozen at v0.2.2.** `profiles.PROFILES`, `DEFAULT_SEEDS`, `DEFAULT_MAX_NEW`,
`SHORTLIST_SCORE_THRESHOLD`, the coverage thresholds and the selection constants are settled
numbers. Changing one requires the full gate: `eval --stage candidates` on **both** golden topics,
before and after, reported with `pool_size` and **`recall_per_100_screened`** alongside recall — a
change that buys recall by growing the pool has to say what it cost. A number that does not move
without loss elsewhere is reverted and recorded under "Tried, not shipped".

**A measured run is not quotable until every routed source reports `failed: 0`.** Check
`manifest.retrieval.per_source` before writing a number down. v0.2.1 published a 6/6 from a run
with arXiv dead in all eight queries; the manifest had said so all along.

**Leading V1.2 candidates, all measured, none acted on:**

1. ~~**Per-seed round-robin over out-of-window admissions**~~ — **REFUTED at v0.2.3**, see above.
   Measured on both topics at all three profiles: costs topic 1 three golden papers, gains nothing.
   The motivating observation (Carroll 2009 at rank 3 of its seed's list, rank 24 globally) came
   from the gap-round pool, where every candidate has one seed link and the seed-count term is
   inert; it does not survive contact with the round-1 pool, where that term is what surfaces the
   classics. Do not re-propose without a topic-3 measurement.
2. **The out-of-window total is the binding constraint on topic 1**, not the ranking. Lifting it
   entirely reaches 10/10; `deep`'s 30 reaches 9/10; `standard`'s 20 reaches 8/10. The profiles now
   make that trade explicit rather than hidden, which is as far as this slice goes.
3. **The off-domain cap assumes a population/setting sub-criterion exists.** Topic 2's five
   criteria are all method-and-evidence, so the cap has nothing to compare a setting against and
   falls back to `brief_summary`. Either the plan rubric requires that criterion or the cap names
   its fallback.
4. **Merge or sharpen the two `contradicts` signals in the rerank rubric.** `flags.contradicts`
   and `relation: contradicting` are near-identical in wording and are set at 3-9x different rates
   by the same reranker (table in `docs/measurements.md`). v0.2.5 works around it in `select.py` by
   keying satisfaction on the sharper signal; the defect is upstream, in the rubric. **Not a
   wording fix to slip into another slice** — the rubric feeds the judge, and re-wording it breaks
   judge comparability the same way the two prompt edits already did. It needs its own measured
   pass with a re-judge on both golden topics.
5. **A review that arrives on merit is displaceable by the counter-evidence reserve; one the
   guarantee promoted is not.** The review guarantee counts itself satisfied by any pick carrying
   `flags.review`, including one the ordering made, and the two-tier displacement rule only
   protects picks a guarantee itself made. Seen at `--contradicting 5` on an internal project
   brief, which lost a review the brief names. The obvious fix — protect whatever
   satisfies a guarantee — collides with the precedence v0.2.5 deliberately preserved, where a
   single main slot goes to the counter-result over the review. Needs a measured pass, not a patch.
6. **Re-baseline both golden topics' judge scores under the current judge prompt, before any
   future precision gate runs.** The committed scores predate two revisions of
   `eval/judge-prompt.md` — the `foundational` canonicity scoring and the per-purpose relevance
   branch — so they are not a valid "before" for anything. Any gate quoting
   `precision_ge2_in_window` has to re-roll both sides under one prompt, which means the baseline
   is owed work, not a lookup. v0.2.5 escaped needing it only because its A/B was byte-identical
   and no top-10 moved.
7. **The plan rubric's "2–4 core terms" rule breaks on IR-generic words.** Gap queries of
   `suggested amount anchoring` and `search string sensitivity` retrieved covalent-organic-framework
   photocatalysis and gravitational-wave searches. A domain-bound term is needed when the concept
   words are polysemous.

Installed locally as `uv tool install --editable .` (so `research-scan` is on PATH and tracks the
working tree) with `~/.claude/skills/research-scan` symlinked at `skills/research-scan`. Editing a
rubric changes the live skill; editing `src/` changes the live CLI.

**Three modules are not in §5**, added deliberately rather than growing `cli.py` past 500 lines:
`run.py` (run directory, manifest upsert, window resolution, parameter precedence — reused by every
stage from S2 on), `retrieve.py` (the §8.1–§8.4 pipeline), from V1.1 `coverage.py` (per-criterion
counting; pure functions, no judgement) and from v0.2.1 `profiles.py` (the three-row cost table).
From v0.3 a fifth: `mcp_server.py`, the remote adapter — outside the engine by construction, since
it drives the CLI as a subprocess. It brings a second `[project.scripts]` entry,
`research-scan-mcp`, where spec §5's pyproject line names one. The only in-package change it made
is `config.py`'s credential table: the adapter's token and data root are resolved through
`config.load()` like every other credential, so `Settings.redact()` sees the token before any log
line does.

**Schema additions beyond §9**, all additive: `Candidate.raw_type` (the §8.3 type filter needs the
source's own type string, which `WorkType` collapses), `RetrievalStats.abstracts_present`,
`SourceStats.unavailable` (routed but not yet built), `RetrievalDropped.window` / `.preprint`,
`ExpansionDropped.type`, `Counts.wall_clock_s`, `JudgeScore.reason`, three models §13 describes
only in prose (`GoldenTopic`, `GoldenPaper`, `JudgeFile`), and from S4.5: `RankedEntry.relation`
(`BriefRelation`), `SummaryPaper.why`, `QueryPlan.anchors` (`Anchor`), and `anchor` in the origins
`Relation` enum; and from S5: `JudgeSummary.precision_ge2_in_window` and `JudgeSummary.foundational`
(the raw `precision_ge2` mixes in slots emit reserved for classics, so it measures the selection
policy rather than the reranker — both ship, and the in-window share is the §14.6 number).
From v0.2.1: `Profile`, `Defaults.profile`, `GapRoundAdvice` on `CoverageFile`, and
`EvalResult.profile` / `.pool_size` / `.wall_clock_s` / `.recall_per_100_screened`.
From V1.1: `ScreenScore.criteria_hit`, `QueryType.gap`, `Query.target_criterion`,
`QueryPlan.round2`, the five coverage models (`CoverageFile`, `CoverageRound`, `CriterionCoverage`,
`QueryYield`, `SeedPrecision`), and `Manifest.retrieval_round2` / `.expansion_round2` — all additive,
so every pre-v0.2 run file still validates.
`shortlist --max-outside-window` defaults to 12, not the spec's 5 — the smaller cap discarded
screened-3 classics before reranking, demonstrated on the golden set.

## Spec amendments (as built)

Deviations from `research-scan-v1-spec.md` that are deliberate and current. The spec file is **not**
edited — it is the spec of record, and an as-built record that lives next to the doctrine is more
useful than a spec quietly rewritten to match whatever shipped. Two older deviations are recorded in
`## Done-state` above and belong to this list: **Three modules are not in §5** and **Schema
additions beyond §9**.

**The CLI has an entry surface the spec's §6 command table does not list: `configure`, `version`,
`completion`, and `mcp`.** §6 enumerated the pipeline stages, which is what the spec was about; none
of these four touch a stage. `configure` writes the credential file §5 fixes the path of, so
`config.py` gained its first writer and still owns that path alone. `mcp` makes the v0.3 adapter a
subcommand as well as a console script — the same server object over stdio, which is what a local
agent runner launches, with `--http` serving exactly what `research-scan-mcp` always did.
`fastmcp` is imported inside the command body, never at module scope, so the engine still does not
import it. `add_completion=False` stays: `completion` calls Typer's script generator directly rather
than adding a second completion surface to the root.

**v0.4.0: the frozen research-scan pipeline was successfully driven from claude.ai through remote
MCP in two end-to-end transport runs, including the forced gap round.** Permanent hosting and auth
are deferred until actual user demand. Evidence and its caveats are in
`docs/measurements.md` — those runs are transport/integration proof and are never quotable as
golden-set retrieval measurements.

**The pipeline is drivable over MCP, and the transport owns no research logic.** §11's skill runs
the CLI over a filesystem; v0.3 adds `mcp_server.py`, which exposes the same four model-decision
boundaries — write queries, screen a batch, write gap queries, rank a page — as MCP tools over
Streamable HTTP, using the existing `QueryPlan` / `ScreenScore` / `Query` / `RankedEntry` schemas as
the tool contracts. The stage order, the artifacts and every judgement are unchanged; the adapter
invokes the CLI as a subprocess and reads its documented exit codes, so nothing measured moves.
Auth applies to the HTTP transport only; stdio is unauthenticated because the client launched the
process. Over HTTP a shared token is accepted either as a bearer header or as the first path
segment. Bearer is the mechanism to use; the path-segment form exists only for clients that cannot
set headers, and it is strictly worse — a secret in a URL reaches browser history and proxy logs,
so it is acceptable for a short-lived local session and nothing more. With no token configured the
server still starts and answers 401 to every request, so it is health-checkable and never silently
open. One global lock serializes every scan's subprocess work: the
HTTP cache is one sqlite file and the rate limiter is per-process, and the 429 episode above is
what two concurrent scans would look like.

**The contract is impact on a question, topic or project — not only on a design.** §1's one-line
contract and the verbatim `SKILL.md` in §11 both say "most likely to change how the project is
designed". As built, the skill finds the 5–10 recent papers with the **highest impact on a research
question, topic, or project**, where impact is judged through a **purpose** the brief declares on a
`Purpose:` line or the planner infers and writes into the first sentence of `brief_summary`:

| Purpose | A paper earns its slot by |
|---|---|
| `build` | moving a design or plan decision |
| `research` | changing what we believe, what we would test, or how we would measure it — strongest evidence, closest prior work, contested findings, method precedents |
| `orient` | being something a newcomer to the topic must know, recent first |

No schema or code changed for this. `BriefRelation` already carried `design-changing`,
`plan-influencing`, `closely-related`, `contradicting` and `foundational`; `emit` already reserved
foundational slots; the rerank rubric already refused to score closely-related work down for being
non-actionable. Only the framing was narrow, and the narrowest string was the skill `description`,
which is also the trigger surface — so the old framing was costing invocations on exactly the
research and orient questions the tool answers best. What did change: the `description`, the brief
template's headings plus its `Purpose:` line, per-purpose `sub_criteria` sets and two query notes in
the plan rubric, a per-purpose `why_it_matters` test in the rerank rubric, one screening sentence,
and the judge's definition of relevance.

**The judge prompt now branches on purpose, and that breaks comparability again.**
`eval/judge-prompt.md` scores relevance in the sense the brief's purpose sets, defaulting to `build`
when a brief carries no `Purpose:` line — so a `research` scan is no longer marked down for
"informing no named decision", which is a test its brief never set. This is the second change to the
prompt since scores were committed (the first is the `foundational` caveat above). **Judge numbers
rolled before this edit are not comparable with numbers rolled after it.** No re-judge ships here;
re-judging is a measured change and this slice ships no numbers.

**`eval/briefs/llm-lit-search.md` keeps the old headings on purpose.** It is the input to a ratified
golden topic, and every committed number for `llm-lit-search` was measured from it as written.
Re-heading it would change what a scored run starts from, which is a measured change wearing a
docs-change costume. `examples/brief.research-example.md` is the reframed `research` template;
the eval brief stays frozen until a slice re-measures it.

**Known gap: an *inferred* purpose does not reach the judge.** `eval/judge.sh` passes `brief.md`
verbatim, so a declared `Purpose:` line arrives intact — but the planner's inferred purpose lives in
`queries.json.brief_summary`, which the judge is not given. A bare-question run whose purpose was
inferred as `research` will therefore be judged as `build`. Briefs that mean `research` or `orient`
should say so on the line; the alternative is passing `brief_summary` to the judge, which is a
harness change with its own before/after.

**The contradicting guarantee reserves a configurable number of slots, defaulting to one.**
§10.4 says "at least one is included"; as built that was exactly one, and one slot ships only the
loudest counter-result. `emit --contradicting N` reserves N (`select.CONTRADICTING_SLOTS` is the
default), capped at half the main slots — counter-evidence earns slots, it does not become the
page. The motivating case: a scan whose brief named a counter-result to one of its premises as an
open question ranked four counter-results at `overall` 3, and all four lost the ordering because a
paper that argues against one premise scores on one sub-criterion while a paper that answers the
brief scores on four. `order_key` is right and the guarantee is the place to fix it.

Three details the single-slot loop hid, each now a test:

- **A guarantee must not displace its own earlier pick.** `min(picks)` over every pick means the
  second counter-result evicts the first and the reserve never grows past one.
- **It must still be able to displace the *other* guarantee's pick.** With `--top 3
  --foundational 2` there is one main slot, and emit has always let the counter-result take it
  from the review, because the guarantees run in order and the last one wins. Protecting every
  guaranteed pick reversed that on `2026-08-19-headless-proof2` — caught by A/B, not by the suite.
  Displacement is two-tier now: a pick the ordering made, else another guarantee's, never its own.
- **The diversity cap binds inside the reserve.** Three papers from one contrarian lab is the
  failure `MAX_PER_FIRST_AUTHOR` exists to prevent, wearing the other flag.

**Satisfaction is keyed on `relation`, and §10.4's eligibility wording is narrowed with it.**
The reserve asks two questions and they are not the same one. *Is the reserve already full?* is now
`relation: contradicting`, falling back to `flags.contradicts` only when `relation` is null, which
is pre-S4.5 files and nothing else. *May this paper fill a reserve slot?* is **`flags.contradicts`
AND `overall >= 2` AND the same relation test** — a narrowing of §10.4, which names only the flag
and the floor. It is not optional: satisfaction counted on one signal and eligibility gated on
another lets the loop reserve a slot for counter-evidence and then fill it with a paper that does
not satisfy the reserve, which is not a reserve. The floor and the flag still bind; the relation is
a third condition on top of them, and it applies to the counter-evidence guarantee only — the
review slot is unchanged.

The measurement that forced it: `flags.contradicts` is additive, so a paper that answers the brief
and also pushes back on one premise carries it, and across the committed runs the flag is set 3-9x
more often than the relation (5 of 10 emitted against 0 on golden topic 1). Counting satisfaction
on the flag meant almost every run reached `_apply_guarantees` already "satisfied" by papers that
confirm the brief — **the guarantee had effectively never fired**. Full table in
`docs/measurements.md`.

**The keying is a zero-diff too, for two reasons worth knowing.** No packet, rank or
`selection_reason` moves on any of the 21 runs. Golden topic 1 does not move because both its
relation-contradicting papers are `outside_window` — the reserve draws from in-window only, and
those two are classics the foundational slots serve. Topic 2 does not move because two are already
emitted, so a reserve of 1 is satisfied on the honest signal. The keying is therefore semantically
real and empirically inert at a reserve of 1; its effect shows when the reserve is raised, or on a
run whose counter-evidence is in-window and outranked. No top-10 changed, so no judge was rolled.

**The default stays 1 because the defaults are frozen.** Measured as a zero-diff: `select()` re-run
in-process over all 21 committed runs that still have their pool reproduces every packet, rank,
`selection_reason` and alternate — both golden topics included. The three runs that differ
(`exp-r2-t1`, `exp-r2-t1-capdiag`, `exp-trigger-t1`) differ identically at HEAD; they predate the
V1.1 review floor. **Raising `CONTRADICTING_SLOTS` is a selection change and needs the judge, not
`eval --stage candidates`:** candidate recall cannot see emit, so the number that moves is
`precision_ge2_in_window`, and rolling it is the maintainer's call.

## Patterns

- **Files are the interface.** Every stage reads and writes JSON in the run directory, validated
  against `schema.py`. That is what lets Codex, Cursor or a plain Python loop drive the same CLI.
- **`schema.py` is the source of truth.** Models generate the JSON Schema, the docs the agent
  reads, and the exit-2 error messages. Add a field there first.
- **Bad input exits 2 with the pydantic error list**, so the agent can repair the file and retry.
  Unknown keys are rejected everywhere — a typo must surface, not be swallowed.
- **Nothing is capped silently.** Every drop (retracted, `must_not`, type, cap) is counted into
  `manifest.json`. Same for a source that failed after retries.
- **A bad status is data.** `http.py` returns the last response after retries; only a transport
  failure raises. `doctor` reports "429", it does not crash on it.
- **Injectable clocks.** `HttpClient` takes `sleep`/`monotonic`/`now` so cache-TTL, backoff and
  rate-limit behaviour is tested without waiting and re-runs are byte-identical (§14.8).
- **Invoke, don't list.** `doctor` proves a source works by calling it with the cache bypassed.
- **Per-endpoint field lists.** S2's graph endpoints reject `tldr` outright, so `GRAPH_FIELDS` is
  separate from `SEARCH_FIELDS`. Reusing one list across endpoints made every graph call 400 while
  the run still looked successful, because the OpenAlex fallback silently covered for it.
- **Flagged, not deleted.** Verification failure marks a packet and prints `[UNVERIFIED — check
  manually]`. Only retraction removes a paper, and only at `emit`.
- **Rank is reading order.** Foundational classics render after the current work with the ranks
  running straight through, so a 2000 paper is context rather than the headline answer.
- **Per-registrar DOI handling.** arXiv DOIs (`10.48550/`) are DataCite-registered and 404 at
  Crossref; asking anyway marked good papers `doi_unresolved`. OpenAlex is the record for those, and
  the arXiv id only joins `verified_by` when a second source independently supplied a matching one.
- **A forked skill needs a prose invocation to return structured output.** `SKILL.md` declares
  `context: fork`, so `claude -p "/research-scan …" --json-schema …` runs the whole scan inside the
  fork and returns `num_turns: 0` / `result: "Command completed"` with `structured_output: null` —
  the scan succeeds, but nothing at the top level emits the `ScanSummary` for the schema to bind to.
  Asking for the skill in prose ("use the research-scan skill … then return its ScanSummary") gives
  the session a turn of its own, and the schema attaches. Measured both ways on 2026-08-19; the
  README's headless section carries the working form.
- **A stage stamps its own timestamps.** `manifest.timestamps` uses flat `<stage>.started_at` keys
  so re-running a stage overwrites only its own pair; `emit` derives `counts.wall_clock_s` from
  `init.started_at`.
- **Caps are totals for the run, not allowances per stage.** The out-of-window budget is the one
  part of the pool every stage wants to grow; V1.1's gap round quietly took a second full
  allowance. `outside_window_spent` makes round 2 inherit what round 1 left — and round 1 counts
  nothing, so re-running it stays idempotent.
- **A second round adds; it never subtracts.** `retrieve --round 2` caps its *additions* against a
  fresh budget and leaves round 1's pool whole. Re-capping the union would silently un-screen papers
  the agent had already scored, and `shortlist` would then reject the file it was handed.
- **Each round owns its batch family, its log and its manifest section.** `NN` / `xNN` / `rNN` /
  `xrNN`; `retrieval-r2.log.jsonl`; `Manifest.retrieval_round2`. `write_batches` clears only its own
  glob and `StageLog` truncates on entry, so sharing either would have quietly destroyed round 1's
  only per-query record.
- **Coverage counts papers, not origins.** A paper three queries found is one paper covering a
  criterion; counting its origins makes the breakdown outrun the total it is breaking down.
- **A guarantee needs a floor, and an empty slot is a legitimate outcome.** "Best available review"
  is not "good enough to emit". When no review clears the floor the slot goes to the next in-window
  candidate, and on topic 1 that swapped an off-topic meta-analysis for a golden-set paper.
- **Anchors pin, filters yield.** Papers the brief names go in `queries.json.anchors`; they bypass
  the §8.3 filters and §8.4 cap (window tags them), always seed expansion, and an unresolved anchor
  is warned about, never silently dropped.
- **Per-registrar DOI handling extends to identification.** A DOI-less record is identified via
  Crossref bibliographic search, accepted only at title ratio ≥ 95 and year ±1 — verified live that
  the search returns same-author-different-paper items, so the tight gate is the feature.
- **Queries are keywords, not sentences.** Verified live in S1: S2's `/paper/search` returns
  `{"total": 0}` for a natural-language sentence, and OpenAlex's full-text search returns nothing
  for a long conjunction. Four-to-six keyword-dense words per query is the working shape — see
  `skills/research-scan/examples/queries.example.json`. This belongs in the S3 plan-rubric; until
  then, `retrieve` WARNs when a source answers every query with zero hits.

## Anti-patterns

- Putting exclusions in query text. They go in `queries.json.must_not` and are enforced by code at
  word boundaries — agents treat NOT-terms as positive keywords (§2, finding 2).
- Hand-tuned weight vectors for ranking. The rubric scores; code selects (§10.4). Weights come back
  only if the eval justifies them.
- Rewarding citation count or venue prestige as relevance. Contradicting papers are relevant.
- "Repairing" metadata from model memory. Verification either passes or the packet ships flagged.
- Registering a CLI command before its slice implements it.
- Rewriting the agent's queries in code. If a query is badly shaped, warn and record it; the plan
  rubric fixes it. The CLI never edits what the agent wrote.
- Loosening a schema constraint because a test failed. The constraint is the contract; fix the data.
- Letting a fallback hide a broken primary path. If S2's graph fails and OpenAlex covers, the counts
  still look fine — so failures are logged per call and summarised at the end of the stage.
- Repairing metadata from the live record at `verify`. A mismatch is a fact worth showing a human.
- Building a golden set out of a run's own output. It cannot then fail, and the recall number it
  produces measures nothing. Entries drawn from a run are annotated `found_in_s3e2e: true` so the
  bias stays legible. Proven on this repo: adding four independently chosen papers to
  `defaults-savings` moved recall@25 from a passing 0.75 to a failing 0.60, and the split is
  6/6 found among run-drawn entries against 0/4 among independent ones.
- Marking a golden topic `ratified`. That is the maintainer's call, on evidence, per §13.
- Writing a gap query aimed at a paper you already know is missing. The gap round is aimed by
  `coverage.json` at a thin criterion, never at a golden entry — a query written to retrieve a
  known answer measures nothing.
- Assuming a bigger pool is a *proportionally* better pool. Recall is monotone in the profile on
  both topics, but recall per 100 screened falls as the pool grows: on topic 1 `quick` returns
  0.199 against `deep`'s 0.157. Depth buys recall, and buys it at a worse rate.
- Reading a cap as a floor. Twice in V1.1 a change looked inert until the cap downstream of it was
  lifted, and once the cap turned out to *be* the whole effect. Before concluding a change does
  nothing, re-run it with the caps off.
- Building anything in §16 before its trigger fires.

## See also

- `research-scan-v1-spec.md` — the build brief: §5 layout, §6 CLI contract, §9 data contracts,
  §14 acceptance, §15 slices, §16 deferred-with-triggers.
- `skills/research-scan/references/schemas.md` — generated contract docs (S0), rubrics (S3).
- `skills/research-scan/examples/` — two worked briefs (`brief.example.md` at `Purpose: build`,
  `brief.research-example.md` at `Purpose: research`) and a hand-written `queries.json` that
  actually retrieves well; useful as the shape to imitate.
- `docs/measurements.md` — the V1 acceptance run and every measurement behind the current defaults
  (query shape, `per_query`, the derived pool cap, the expansion sort, arXiv).
- `README.md` — the user-facing install, usage, cost and troubleshooting.
- `RELEASING.md` — the release procedure, the post-release checks and the rollback rules.
