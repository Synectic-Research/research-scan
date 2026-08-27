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

`contract.py` is the reconciliation itself, ported from Phase-1.2A with its tests. Batches are the
package's own — 25 items each by default — and every rule is about the wire shape, never about the
judgement:

| the response does this | the contract does this |
|---|---|
| names a cid the batch never asked for | discard the row, log it, never retry for it |
| names a cid that cannot be read at all | log it unassignable; the expected cids stay owed |
| answers one cid twice, agreeing on score **and** `criteria_hit` | keep one, log the collapse |
| answers one cid twice, disagreeing on either | that cid is unresolved and is re-asked; the rest of the response stands |
| leaves a cid unanswered | re-ask the owed cids only, as a minimal sub-batch |
| returns a row that fails the field contract | that cid is unresolved; the other 24 are kept |

Retries are bounded at `contract.MAX_RETRIES = 2` — one call plus at most two retries, per batch,
never a loop. When those are spent the batch fails **on the record**: the accepted rows are kept,
the unresolved cids are named in `summary.json` and in the provenance record, the process exits
non-zero, and what it wrote is never presented as a complete `screen.json`.

## Provenance

Every run writes `<run>/engine/<UTC stamp>/provenance.json`:

| field | what it pins |
|---|---|
| `provenance_schema_version` | which record shape this is, so a reader knows which keys to expect |
| `run_id`, `started_at`, `completed_at` | which run, and when — ISO-8601 UTC with the offset written out |
| `engine_protocol_version`, `engine_id`, `engine_version` | which contract, which engine, which build |
| `model_id`, `model_revision_or_hash` | what was asked for, and what the provider says answered |
| `rubric_hash`, `prompt_template_hash`, `brief_hash` | the three texts that steer the judgement, as `sha256:…` |
| `response_schema_version`, `response_schema_hash` | the wire shape the response had to satisfy |
| `effort_or_thinking_configuration`, `sampling_parameters` | the settings the judgements were drawn under |
| `batch_size`, `max_concurrency` | how the work was cut up and how much of it ran at once |
| `execution_class` | `provider-api` — this run went off this machine, into a provider's service |
| `attempt_count`, `retry_summary` | how many calls it actually took, and which batches needed more than one |
| `input_record_count`, `accepted_record_count`, `unresolved_cids` | what went in, what survived the chain, what is still owed |
| `usage`, `token_unit`, `cost`, `currency` | tokens and money, summed over initial calls **and** their retries |
| `completion_status` | `complete` only when no cid is unresolved |

Every key is present in every record, including the ones a run cannot fill: an absent field cannot
be told from a forgotten one six months later, so unfilled fields serialise as `null`. `cost` is
one of them by default — no price table ships with the driver, because a stale one baked into a
record reads as measured — while `currency` is stated regardless, so the number is never read in
the wrong one.

It is a description of configuration and outcome, never of access: no key, token, endpoint,
account or organisation identifier reaches it. The driver's tests plant an API key, a bearer
token, a credentialed URL, a `base_url` and an environment dump, then scan the whole serialised
record for each. Beside it are `accepted.json` (the artifact bound to its record), `calls.jsonl`
(per-call timing and tokens) and `summary.json`.

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
uv run pytest -q      # 76 tests: the ported contract suite plus this driver's own
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
(`552f09c462dce07a7c20fa3f30e85c3264f42346:research/experiments/phase1-stateless/measurements.json`).
Full-scan figures are
projections from those parts, not a demonstrated end-to-end path.

What is not measured is the part that decides whether this can ever be a default: end-to-end
quality. The reranker, not the screen, is the loss stage on the golden topics, and Phase-1.4 froze
it (Outcome C) rather than tuning it further. Until an end-to-end run beats — or matches — a fresh
multi-replicate conversational control on golden recall, this driver stays exactly what the
heading says it is. Cost does not enter that decision.

See [`docs/measurements.md`](../../docs/measurements.md) for the full record and its citations.
