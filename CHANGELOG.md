# Changelog

All notable changes to this project are documented here.

The format is based on [Keep a Changelog](https://keepachangelog.com/en/1.1.0/), and this project
adheres to [Semantic Versioning](https://semver.org/spec/v2.0.0.html).

Every release below was gated on measurement. Where an entry says a change was reverted, the
measurement that killed it is in [`docs/measurements.md`](docs/measurements.md), kept so the same
idea is not retried blind.

## [Unreleased]

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

### Changed

- Distribution is moving to local-first. The tool is a CLI plus an agent skill that runs on your
  own machine against your own API keys; the previously documented remote MCP surface is not part
  of the public project.
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
  `tool_version`, the User-Agent and the MCP handshake cannot disagree with it. The number itself
  did not move. One consequence worth knowing: after a bump, an editable install reports the old
  number until `uv sync` runs.

### Fixed

- The MCP handshake advertised FastMCP's version (`3.4.7`) as `serverInfo.version`. FastMCP falls
  back to its own version when none is passed, and none was. It now reports the package version,
  from the same single source as everything else.
- The README's credential table called `S2_API_KEY` required and said a missing one was a `FAIL`.
  `doctor` has always treated it as a warning — the scan runs without it, throttled — and
  `.env.example` said so. The docs were wrong, not the code.

### Note

The package version is still `0.2.5` while the most recent tag is `v0.4.0` — `__version__` was not
bumped when that tag was cut. The next release resolves the two. There is now a test asserting that
the reported version equals the one written in `pyproject.toml`, so the same drift cannot recur
silently; `.claude-plugin/plugin.json` stays out of it deliberately, as release-automation's job.

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

[Unreleased]: https://github.com/Synectic-Research/research-scan/compare/v0.4.0...HEAD
[0.4.0]: https://github.com/Synectic-Research/research-scan/compare/v0.2.5...v0.4.0
[0.2.5]: https://github.com/Synectic-Research/research-scan/compare/v0.2.4...v0.2.5
[0.2.4]: https://github.com/Synectic-Research/research-scan/compare/v0.2.3...v0.2.4
[0.2.3]: https://github.com/Synectic-Research/research-scan/compare/v0.2.2...v0.2.3
[0.2.2]: https://github.com/Synectic-Research/research-scan/compare/v0.2.1...v0.2.2
[0.2.1]: https://github.com/Synectic-Research/research-scan/compare/v0.2.0...v0.2.1
[0.2.0]: https://github.com/Synectic-Research/research-scan/compare/v0.1.1...v0.2.0
[0.1.1]: https://github.com/Synectic-Research/research-scan/compare/v0.1.0...v0.1.1
[0.1.0]: https://github.com/Synectic-Research/research-scan/releases/tag/v0.1.0
