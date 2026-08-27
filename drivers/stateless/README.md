# Stateless screening driver

**Experimental reference cognition engine. Not part of the installed package in v0.6.0. Informs
the forthcoming provider-neutral engine protocol (see `PLUGGABLE_COGNITION_ENGINE`). Screening is
golden-validated; end-to-end quality is not yet non-inferior to the conversational path (reranker
limitation — [`docs/measurements.md`](../../docs/measurements.md)). Promotion requires end-to-end
golden non-inferiority vs a fresh multi-replicate conversational control; cost is not a promotion
criterion.**

It screens one run's `screen-batches/` through stateless provider calls — one batch per call, no
conversation, no run state, no tools — and writes the accepted judgements to that run's
`screen.json`. Everything else in the pipeline is unchanged and unaware: retrieval, expansion,
coverage, the shortlist, verification and emit run exactly as they do when a person or an agent
does the screening.

## What this is, in the architecture

Research Scan has three layers, and this driver is one replaceable instance of the middle one:

| layer | what it is | what it may do |
|---|---|---|
| **Core** | the `research-scan` package: retrieval, dedup, expansion, coverage, shortlist, verification, emit | everything deterministic; it makes no model calls of its own |
| **Cognition engine** | whatever produces the judgements — a hosting agent over the skill, or a driver like this one | score the batch it is handed, under the run's own rubric |
| **Runtime** | where an engine's work physically happens — this machine, a provider's API, something else | nothing; it is a property recorded in provenance, not a behaviour |

The core does not depend on any engine, and `engine = none` — a person or an agent screening
against the rubric — stays a first-class way to run a scan. An engine is explicit, replaceable,
opt-in, and recorded. The protocol that will make "an engine" a typed interface rather than a
driver in a repo directory is being drawn from this driver and has not shipped; until it does,
this tree is a reference, not an integration point.

## The untrusted-output doctrine

A model's response is an input to be checked, not a result to be stored. Every judgement crosses
the same chain before it becomes pipeline state, and each step can only reject:

```
engine response
  → schema validation       the decoded body has the shape the wire schema demanded
  → CID reconciliation      rows are matched against the cids the batch actually asked for
  → value/range validation  every field is inside the ScreenScore contract
  → provenance attachment   surviving rows are bound to the record of what produced them
  → accepted cognition artifact
```

No step repairs a row, invents a judgement, renames a cid or fills a missing field from context —
a repaired judgement is indistinguishable from an invented one. **The model never writes canonical
pipeline state.** It returns rows; `accept.py` decides which of them survive; a cid the run never
retrieved is refused at the last gate before `screen.json` is written; and `research-scan
shortlist` then re-validates the whole file against the package's own contract and exits 2 on
anything this driver let through. A batch that cannot be satisfied inside its bounded retries
fails **on the record**, keeping the rows it did get, and the run is short by a named list of cids
rather than quietly complete.

`contract.py` is the reconciliation itself, ported from Phase-1.2A with its tests: an unknown cid
is discarded and never buys another call, identical duplicates collapse, conflicting duplicates
invalidate the response, a missing cid is re-asked as a sub-batch, and a bad row costs its own cid
rather than the other 24.

## Provenance

Every run writes `<run>/engine/<UTC stamp>/provenance.json`:

| field | what it pins |
|---|---|
| `engine_protocol_version`, `engine_id`, `engine_version` | which contract, which engine, which build |
| `model_id`, `model_resolved` | what was asked for, and what the provider says answered |
| `rubric_hash`, `prompt_template_hash`, `brief_hash` | the three texts that steer the judgement |
| `schema_version`, `schema_hash` | the wire shape the response had to satisfy |
| `effort`, `thinking`, `sampling`, `max_concurrency` | the settings the judgements were drawn under |
| `execution_class` | `provider-api` — off this machine, in a provider's service |

It is a description of configuration, never of access: no key, token, endpoint, account or
organisation identifier reaches it, and the driver's own tests assert that. Beside it are
`accepted.json` (the artifact bound to its record), `calls.jsonl` (per-call timing and tokens) and
`summary.json`.

## Use

```bash
cd drivers/stateless
uv sync
ANTHROPIC_API_KEY=… uv run python -m stateless_driver --run ../../research/scans/<run> --dry-run
ANTHROPIC_API_KEY=… uv run python -m stateless_driver --run ../../research/scans/<run>
```

`--dry-run` writes the provenance record and the batch plan and spends nothing. Batches already
covered by `screen.json` are not re-bought unless `--all` is passed. `--model`, `--effort`,
`--max-tokens`, `--max-concurrency`, `--batches` and `--no-cache` are the knobs; every one of them
lands in the provenance record. Exit 1 means at least one batch failed on the record — the
unsatisfied cids are in `summary.json`, and `research-scan shortlist` will name them too.

```bash
uv run pytest -q      # 58 tests: the ported contract suite plus this driver's own
```

## Dependencies

`pyproject.toml` and `uv.lock` in this directory are the whole dependency contract: `anthropic`,
pinned exactly to the version the Phase-1.x arms were measured against. It is a dependency of this
driver and of nothing else — **the `research-scan` package's own dependency list is byte-unchanged
by everything in this tree**, and the package imports no module from it. This directory is
excluded from the sdist and was never in the wheel.

## What was measured, and what was not

Screening on the Phase-1.1 topic-2 run, stateless-parallel against the recorded conversational
baseline: **979 s → 73 s** and **$3.003 → $0.757**, all 572 candidates scored, schema-valid
(`552f09c:research/experiments/phase1-stateless/measurements.json`). Full-scan figures are
projections from those parts, not a demonstrated end-to-end path.

What is not measured is the part that decides whether this can ever be a default: end-to-end
quality. The reranker, not the screen, is the loss stage on the golden topics, and Phase-1.4 froze
it (Outcome C) rather than tuning it further. Until an end-to-end run beats — or matches — a fresh
multi-replicate conversational control on golden recall, this driver stays exactly what the
heading says it is. Cost does not enter that decision.

See [`docs/measurements.md`](../../docs/measurements.md) for the full record and its citations.
