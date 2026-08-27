# Changelog

All notable changes to this project are documented here.

The format is based on [Keep a Changelog](https://keepachangelog.com/en/1.1.0/), and this project
adheres to [Semantic Versioning](https://semver.org/spec/v2.0.0.html).

Every release below was gated on measurement. Where an entry says a change was reverted, the
measurement that killed it is in [`docs/measurements.md`](docs/measurements.md), kept so the same
idea is not retried blind.

## [0.6.0] — 2026-08-27

### Fixed

- **The shortlist tie-break was acting as a recency filter inside large equal-score bands.** The
  ordered cut handed to the reranker keyed on `score DESC, origin_count DESC, date DESC`, and in a
  real pool the first two tiers tie across dozens of papers — so date decided, and the cap dropped
  central papers for being older than their band. On the recorded topic-2 acceptance run a paper
  screened 3 sat at rank 90 of a 289-strong in-window population and never reached the reranker; on
  the golden-topic run the cut fell inside the score-3 band and lost two. Latent since v0.4 and
  present on both eras of artefact — the evidence is in
  [`docs/measurements.md`](docs/measurements.md),
  `552f09c462dce07a7c20fa3f30e85c3264f42346:research/experiments/phase12-selection/results/report_tail.md`
  §4, and the audit record in
  [#1](https://github.com/Synectic-Research/research-scan/issues/1). Fixed in
  `1fd1465f413c21104d7af3710ed219ce595ca49a`, with
  the replay that proves it in
  `1fd1465f413c21104d7af3710ed219ce595ca49a:research/experiments/phase12-selection/results/src-t1-replay.json`.
  Pooled golden
  survival into the rerank frontier at the shipped cap goes from 8/11 to 10/11, which is the finite
  maximum, with no cap change and no new weights.

### Added

- A **runtime deployment fingerprint**: the server logs it at startup and `/health` reports it, so
  a running deployment can be matched to the commit it was built from. `RELEASING.md` gained the
  post-release step that exercises it — restart, then verify the fingerprint against the release
  SHA — and a release receipt.
- An **experimental reference cognition driver** in `drivers/stateless/`, repo-only. It screens a
  run's batches through stateless provider calls behind a reconciling CID contract, and every run
  writes a machine-readable engine provenance record. It is **not part of the installed package**:
  it lives outside `src/`, is excluded from the sdist, was never in the wheel, carries its own
  pinned dependency contract, and the package's own dependency list is unchanged. It informs the
  provider-neutral engine protocol that has not shipped
  ([#4](https://github.com/Synectic-Research/research-scan/issues/4)); promotion to a documented
  path requires
  end-to-end golden non-inferiority against a fresh multi-replicate conversational control, and
  cost is not a promotion criterion.

### Changed

- **Shortlist ordering is now a total order**: `score DESC, criteria_supported DESC,
  origin_count DESC, best_retrieval_rank ASC, date DESC, cid ASC`. `criteria_supported` counts the
  distinct sub-criteria screening attributed to a paper (restricted to the ids `queries.json`
  defines, when the run has that file); `best_retrieval_rank` is the best position any source gave
  it. Both are evidence the pipeline already produced. The final `cid` tier removes the last
  dependence on `candidates.json` order — on the six frozen inputs it moves four rows, all inside
  fully tied bands, with membership at the shipped caps unchanged. **No other selection semantics
  change**: same caps, same threshold, same two windows, same slot rules at emit.
- **The fields that order reads now have domains narrow enough to trust.** `score` and
  `Origin.rank` are strict integers: Pydantic's lax coercion turned `true` into `1` and `"3"` into
  `3`, so a malformed `screen.json` bought a place in the order instead of exiting 2. A run whose
  artefacts carry a score or a rank as a string or a boolean now fails at the stage that reads it,
  with the field named. `rank` keeps its `≥ 0` floor — ranks are zero-based, and the top hit is
  rank 0. `publication_date` is unchanged at the schema, where partial dates are legitimate
  metadata, but the date tier resolves through a calendar check, so `"2024-13-01"` sorts with the
  unknowns instead of outranking `"2025-01-01"` as a raw string. And `shortlist.build` refuses a
  screen file that scores one cid twice, which both shipped call paths already refused upstream.

## [0.5.2] — 2026-08-21

### Added

- A documentation site at <https://researchscan.synectic.org>, built from
  [`research-scan-docs`](https://github.com/Synectic-Research/research-scan-docs). The README and
  the package metadata link to it; `server.json` carries it as `websiteUrl`.
- `[project.urls]` in `pyproject.toml` — homepage, documentation, repository, changelog and
  issues — so the PyPI sidebar points somewhere.
- `websiteUrl` in `server.json`, which the MCP registry shows on the server's record. It reaches
  the registry only through the manual publish step; `RELEASING.md` now says so.
- CI on every push and pull request: lint, tests, the version guard, and a wheel smoke test that
  installs the built artifact into a clean venv and makes it state its own version. Python 3.11
  and 3.13, since `requires-python` is `>=3.11`.
- `scripts/check_versions.py`, the five-way version guard as a script instead of Python embedded
  in a workflow. `ci.yml` and `release.yml` both call it, and it runs locally the same way.

### Changed

- The README opens on what the tool does and for whom, and one description now runs across the
  package, the plugin, the marketplace entry and the skill, rather than four variants of it. The
  registry record carries that sentence's first clause: the MCP registry caps `description` at
  100 characters, and the full sentence is 119.
- `SKILL.md`'s command-not-found hint installs from PyPI (`uv tool install research-scan`) instead
  of from a git URL. The package has been on PyPI since 0.5.0.
- The `AGENTS.md` anti-pattern about pool size now cites the corrected per-100-screened figures.
  It had rested on a topic-2 `quick` 6/6 that was withdrawn at v0.2.2, when the run behind it
  turned out to have arXiv failing all eight queries.

### Removed

- `ok` and `tool_version` from `doctor --json`. Read `ready` and `version`, identical in value.
  `doctor --json` is a stable interface from 0.5.2 onward: keys are added, never removed or
  repurposed. The two removed keys existed in 0.5.0 and 0.5.1 as undocumented duplicates of
  `ready` and `version`; the README has always named `ready` as the boolean.

## [0.5.1] — 2026-08-21

### Changed

- Packaging only: PyPI long description (`readme` metadata) and MCP registry ownership marker; no
  code changes.

## [0.5.0] — 2026-08-20 — Open Source Developer Release

### Added

- Apache-2.0 licensing: `LICENSE`, SPDX headers on every source file, and PEP 639 license metadata
  in `pyproject.toml`.
- Governance files for a public project: `SECURITY.md`, `CONTRIBUTING.md`, `CODE_OF_CONDUCT.md`,
  `CITATION.cff`, and this changelog.
- An ORCID on the `CITATION.cff` author, so the attribution resolves to a person rather than to a
  name string.
- `research-scan version`, with `--json` reporting the version, the Python and platform it is
  running on, and whether the optional `mcp` extra is installed. `--version` keeps its bare output.
- `doctor --json` gained five summary keys — `version`, `ready`, `providers`, `config`,
  `run_store` — as the documented CI/agent interface. A strict superset: every key the skill's
  preflight already parses, `checks` included, is unchanged.
- `doctor --verbose`, which prints the per-check table that used to be the default.
- `research-scan configure` (alias `setup`): interactive credential setup that writes
  `~/.config/research-scan/.env` at 0600 in a 0700 directory, reads keys without echo, and ends by
  running `doctor`. Re-running is safe — it merges, so comments and variables it does not ask
  about (the MCP adapter's token among them) are left byte-identical. Without a terminal on stdin
  it prints the file to write and exits 2 instead of hanging.
- `research-scan completion bash|zsh|fish`, printing the eval-able script from Typer's own
  generator. `add_completion=False` stays, so the root gains no `--install-completion` /
  `--show-completion` flags; the per-shell classes are registered at import instead, which is
  what makes the printed script actually answer.
- `research-scan mcp`: the MCP server as a first-class command. Default transport is stdio, for
  Claude Desktop, Claude Code and other local agent runners; `--http` is the existing
  Streamable HTTP mode. Both serve the same server object and the same four tools — nothing is
  duplicated. `research-scan-mcp` still exists and is unchanged.
- `config.write_env()`, the first writer in `config.py`. The module already owned reading the
  credential file; it now owns writing it too, so there is still exactly one component that knows
  where that file lives.
- `THIRD_PARTY_LICENSES.md`, recording that the dependency set is predominantly MIT/BSD/Apache/
  ISC/PSF and that one dependency, `certifi`, is MPL-2.0, consumed unmodified as a transitive
  dependency of `httpx`/`httpcore`.
- A tag-triggered release workflow publishing to PyPI through Trusted Publishing (OIDC, no API
  token), gated on the tag matching the packaged version and on a smoke test of the built wheel.

### Changed

- Distribution is local-first. The tool is a CLI plus an agent skill that runs on your own machine
  against your own API keys; the previously documented remote MCP surface is not part of the public
  project. Installation is `uvx research-scan` or `uv tool install research-scan`, from PyPI.
- `fastmcp` and `uvicorn` moved from the optional `mcp` extra into core dependencies, exact pins
  unchanged, so the MCP server ships by default and the documented client config needs no
  `--from 'research-scan[mcp]'` incantation. `mcp = []` remains as an empty compatibility extra so
  existing invocations keep resolving.
- The project is developed in a public repository under the Apache-2.0 licence.
- With no `RESEARCH_SCAN_MCP_TOKEN` configured, the token-authenticated HTTP transport now starts
  and answers 401 to every request instead of refusing to boot. The posture is identical — no
  request is ever served, and the alternate mount that carries the token in the URL path is not
  created at all — but a dead port could not be health-checked and gave an operator nothing to
  look at but the logs. With a token configured, behaviour is unchanged.
- `doctor` now prints a four-line summary by default instead of the full table: one line for
  configuration, one for the providers, one for the run store, and a verdict. Failures carry one
  actionable sentence. Presentation only — the checks, their statuses and the exit codes are
  untouched in all three modes, and a test pins that. A missing *optional* key no longer demotes
  the configuration line; it is a warning, which is what it always meant.
- `pyproject.toml` is now the only place the version is written. `__version__` resolves from the
  installed distribution through `importlib.metadata`, so the CLI, `manifest.json`'s
  `tool_version`, the User-Agent and the MCP handshake cannot disagree with it. One consequence
  worth knowing: after a bump, an editable install reports the old number until `uv sync` runs.

### Fixed

- The MCP handshake advertised FastMCP's version (`3.4.7`) as `serverInfo.version`. FastMCP falls
  back to its own version when none is passed, and none was. It now reports the package version,
  from the same single source as everything else.
- The README's credential table called `S2_API_KEY` required and said a missing one was a `FAIL`.
  `doctor` has always treated it as a warning — the scan runs without it, throttled — and
  `.env.example` said so. The docs were wrong, not the code.

### Note

This release resolves a three-way version drift: the package said `0.2.5`, `.claude-plugin/
plugin.json` said `0.2.4`, and the most recent tag said `v0.4.0`. All three now say `0.5.0`, moved
in one commit. A test asserts that the reported version equals the one written in `pyproject.toml`,
and the release workflow fails a build whose tag disagrees with it, so the drift cannot recur
silently.

Releases before this one were made in a private repository, and their tags are not present here.
The comparison links below therefore resolve only for releases cut in the public repository.

## [0.4.0] — 2026-08-20

### Added

- MCP adapter (`research-scan-mcp`, optional `mcp` extra) exposing the four decision boundaries —
  write queries, screen a batch, write gap queries, rank a page — over Streamable HTTP, so an agent
  that is not on the same machine can drive the pipeline. The adapter shells out to the CLI and
  holds no judgement about papers.
- `scan_start` accepts a client-supplied scan id, making a retried call resume the existing scan
  instead of starting a second one.

### Verified

- Two end-to-end scans driven from a claude.ai client: 23 and 36 tool calls, zero timeouts, zero
  retries, 47/47 and 49/49 DOIs verified. The second forced the gap round and reached the
  `write_gap_queries` boundary. Transport evidence only — no golden-set eval was run.

There is no `v0.3.x` tag. The MCP dependencies were added under a `0.3` working label that was
never released; the adapter shipped in `v0.4.0`.

## [0.2.5] — 2026-08-20

### Changed

- The counter-evidence guarantee reserves N slots (`emit --contradicting N`, default 1) instead of
  exactly one, capped at half the main slots.
- Satisfaction is keyed on `relation: contradicting` rather than the additive `flags.contradicts`.
  The flag was being set 3–9× as often as the relation, so most runs arrived already "satisfied" by
  papers that answer the brief and only incidentally push back — the reserved slot had effectively
  never fired.

### Fixed

- A guarantee could displace its own earlier pick. Displacement is now two-tier: a pick the
  ordering made, else another guarantee's, never its own.

Re-running selection over all 21 committed runs that still have their pool produced zero diffs, so
no top-10 moved and the precision gate passed vacuously.

## [0.2.4] — 2026-08-19

### Changed

- Reframed from "papers that change a design" to the 5–10 recent papers with the highest impact on
  a research question, topic, or project — judged through a `purpose` (`build`, `research`,
  `orient`) the brief declares or the planner infers. Each purpose derives its own sub-criteria and
  changes what `why_it_matters` has to argue.
- Skill description rewritten without angle-bracket placeholders, which the claude.ai uploader
  rejects as XML tags.

Documentation and rubrics only — no default, cap, selection rule or eval metric changed. A 12-prompt
trigger check scored 12/12: every should-trigger prompt invoked the skill, every should-not left it
alone.

## [0.2.3] — 2026-08-19

### Reverted

- Per-seed round-robin admission for out-of-window candidates, after measurement. It cost topic 1
  three golden papers at every profile (7/10 → 4/10, 8/10 → 5/10, 9/10 → 6/10) at an identical pool
  size and gained nothing on topic 2, because round-robin admits every seed's rank-0 item before any
  seed's rank-3 item — and the paper it dropped was the most central one, cited by 4 of 15 seeds.

Global sorting stays. The durable lesson: fair-share admission helps when producers are
interchangeable and hurts when agreement between them is the signal.

## [0.2.2] — 2026-08-19

### Changed

- Defaults frozen. A proposed collapse from three profiles to two was measured and rejected: the
  candidate `standard` missed the decision rule on both topics and both terms — recall 7/10 and 4/6
  against a bar of 8/10 and 5/6, at pools of 521 and 619 against a bar of 420.

### Fixed

- Corrected a wrong number in the v0.2.1 profile table, caught by the same measurement.

## [0.2.1] — 2026-08-19

### Added

- Three profiles — `quick`, `standard`, `deep` — chosen at `init` and recorded in
  `manifest.defaults`, setting per-query depth, the pool cap, the out-of-window total for the run,
  and whether the gap round runs. Flags still override them.
- `recall_per_100_screened` on `EvalResult`, so a recall number carries its screening cost.

### Changed

- The out-of-window admission is now a bounded total for the run rather than a per-stage cap, and
  the gap round is conditional on the coverage trigger.

Measuring the profiles revealed that the V1 acceptance table had never been one setting: topic 1's
run was `quick`-depth and topic 2's was `deep`.

### Reverted

- The proposed out-of-window ranking key (in-window seeds, then log velocity) measured as an exact
  no-op — `log1p` is monotone — and was reverted.

## [0.2.0] — 2026-08-19

### Added

- Coverage-driven gap round: `screen.json` entries carry `criteria_hit`, a new `coverage` command
  reports per-sub-criterion coverage and the gap-round verdict, and `retrieve --round 2` /
  `expand --round 2` run one extra round aimed at the thinnest criteria. Topic 1 candidates recall
  8/10 → 9/10; topic 2 unchanged at 5/6.
- Two rerank guards: an off-domain cap in the rubric (a paper whose setting is not the brief's caps
  at `overall` 2 unless it names an explicit method transfer) and a relevance floor on the `review`
  guarantee. Both papers the acceptance judge scored 1 leave the top 10, each replaced by a
  golden-set paper, and every paper judged 3 stays — but only both guards together do it.

### Measured, not shipped

- Full-bibliography expansion for anchor papers: could not move either topic.

## [0.1.1] — 2026-08-19

### Fixed

- `research-scan --version` exited 2. Typer required a subcommand before the root callback ran, so
  the flag `--help` advertised failed with "Missing command". Two regression tests.

## [0.1.0] — 2026-08-19

First release: the whole V1 pipeline.

### Added

- The stage chain — `init`, `retrieve`, `expand`, `coverage`, `shortlist`, `verify`, `emit`, `eval`,
  `doctor`, `schema` — with pydantic contracts for every file, and `doctor` proving each source live
  rather than reporting what it thinks is configured.
- Sources: OpenAlex, Semantic Scholar, arXiv, Crossref verification, with routing by domain.
- The Claude Code skill and its rubrics: the CLI carries no LLM SDK, so query planning, screening
  and reranking belong to whatever agent hosts it.
- Golden-set eval with an independent judge, and `precision_ge2_in_window` split out from raw
  precision — the raw number mixed in slots reserved for out-of-window classics, scored on a scale a
  classic cannot win, so it measured the selection policy rather than the reranker.

### Measured before shipping

- Query shape rewritten to 2–4 core terms and `per_query` 20 → 40 took topic 2 candidates recall
  from 1/6 to 6/6, with no loss on topic 1. Pool cap scaled by built-source count (450 × n/2).
- Acceptance run: recall@10 0.50 on both topics, recall@25 0.80 and 0.67,
  `precision_ge2_in_window` 0.875 on both.
