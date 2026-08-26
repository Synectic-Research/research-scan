# Phase-1.2A — x02 driver-contract fix + offline shortlist-policy sweep

Zero model calls, $0.00 API spend, no repo changes. `git status` clean; every artefact lives under
the gitignored `research/experiments/phase12-selection/`. Nothing under `src/`, `skills/` or
`eval/` was touched, and the Phase-1.1 driver in `research/experiments/phase11-golden/` was read
but not edited, so its measured artefacts stay exactly as Phase 1.1 reported them.

**Headline, in two sentences.** The x02 failure was an all-or-nothing predicate, not a judgement
failure: a reconciling contract lands all six recorded attempts that the frozen policy threw away,
and 25 correct rows can no longer be destroyed by a 26th spurious one. The shortlist defect is
real, it is an *ordering* defect before it is a *cap* defect, and the smallest fix that recovers
both OpenScholar and LitSearch is **a tie-break change at the shipped cap of 40** — no cap
increase, no new weights, no extra rerank tokens.

---

## 1. x02 CID-contract fix

### What broke

`lib/common.validate_batch_scores` opens with `sorted(got) != sorted(want) -> raise`. Batch
membership is checked as an all-or-nothing equality, so a single extra row invalidates the whole
response. On `llm-lit-search/x02` the structured-output decoder padded the array with a mangled
13-character variant of a real cid — `2ad9d99f0b79b`, `2ad9d99f0b79dup`, `2ad9d99f0b79-dup`,
`4a1808a68e2a2` — deterministically, on six consecutive calls. Every one of those calls carried
all 25 wanted cids, correctly scored. All six were discarded.

### What replaces it

`contract.py` — `reconcile(batch, payload)` partitions a response against the cids its batch asked
for, and `screen_batch(batch, call)` drives the bounded retry. The judgement layer is untouched:
every field rule from the frozen contract survives verbatim, applied per row instead of per array.

| case | behaviour | retry? | provenance event |
|---|---|---|---|
| unknown cid returned | row discarded, judgement kept for the rest | **no** | `unknown_cid_discarded` (cid, whether well-formed, its reason string) |
| same unknown cid repeated | each row discarded the same way | **no** | one `unknown_cid_discarded` per row |
| expected cid twice, identical score | first row kept, copies dropped | **no** | `duplicate_identical_collapsed` (cid, copies, score) |
| expected cid twice, conflicting scores | whole response rejected — it contradicts itself about a judgement | **yes**, bounded | `duplicate_conflicting` (cid, the scores), then `batch_invalid` |
| expected cid missing | the owed cids are re-asked as a **sub-batch** (`sub_batch()`), whole batch when the driver cannot sub-call | **yes**, bounded | `retry` (owed count, mode) |
| row fails a field rule (bad score, empty reason, unknown criterion id, score ≥ 2 with empty `criteria_hit`) | that cid alone becomes unsatisfied; the other 24 stand | **yes**, bounded | `row_rejected` (cid, why) |
| no `scores` array at all | response rejected | **yes**, bounded | `no_scores_array` |
| the call itself raises | recorded, counts as an attempt | **yes**, bounded | `call_failed` (attempt, error) |
| retries exhausted | batch fails **with the rows it did get**, and a recorded reason | never loops | `batch_failed` (attempts, reason, kept, missing) |

Retry ceiling is `MAX_RETRIES = 2` — one call plus at most two retries, then the batch fails on the
record. Rows banked by an earlier attempt are never given back, so a late transport failure cannot
undo an earlier partial success.

### Fixtures and test results

Fixtures are recorded Phase-1.1 artefacts, not inventions:

* `fixtures/x02-batch.json` — `runs/p11-t2/screen-batches/x02.json`, the real 25-item batch.
* `fixtures/x02-response-salvage.json` — the salvage call's 27 rows, byte-recoverable: the 25
  recorded judgements from `screen-batches/p11-t2/x02.json` plus the two rows
  `stages/salvage-llm-lit-search-x02.json` records as dropped.
* `fixtures/x02-attempts-recorded.json` — the six frozen-policy attempts. **Fidelity caveat, stated
  in the file itself:** the six raw bodies were not kept, only their error signatures
  (`stages/screen-calls-llm-lit-search-expand.json`, `logs/screen-t2-expand*.log`). Each is rebuilt
  to its recorded signature — `missing=[] extra=['<the recorded mangled cid>']` over the 25
  recorded rows — which is exactly what `missing=[]` licenses and no more.

**25 tests, 25 passed** (`uv`'s repo venv, pytest 9.1.1; full run in `results/pytest.txt`).

| test group | n | what it pins |
|---|---|---|
| `test_every_recorded_x02_attempt_now_lands` | 6 | all six thrown-away attempts reconcile to `COMPLETE` with the 25 wanted cids in batch order, and name the discarded ghost |
| `test_salvage_response_needs_no_salvage_script` + `..._matches_the_recorded_salvage_output_exactly` | 2 | the 27-row body reconciles to **exactly** the 25 rows `salvage.py` wrote — no Phase-1.1 measurement moves |
| `test_clean_response_is_unchanged` | 1 | a clean response reconciles to itself, with an empty provenance log |
| unknown-cid cases | 2 | discarded, logged, and **never buy another call** (asserted on call count) |
| duplicate-expected-cid cases | 4 | identical → keep one; conflicting → invalid, retry, land on attempt 2, or fail after exactly 3 calls |
| missing-cid cases | 3 | sub-batch re-asks only the owed cids; whole-batch fallback; persistent miss keeps 23 good rows and fails on the record |
| per-row field contract | 5 | a bad row costs its own cid, not the batch — 24 rows survive each mutation |
| driver safety | 2 | no `scores` array is retryable; a raising call cannot loop (exactly 3 attempts) |

The property the slice asked for is asserted directly:
`test_persistently_missing_cids_fail_the_batch_but_keep_the_good_rows` ends with
`assert len(out.scores) == 23`, and every unknown-cid test ends with `len(out.scores) == 25`.

**Integration point, not integrated.** `contract.py` is a drop-in for `screen.py::_one`'s
`C.validate_batch_scores(batch, payload)` call — the retry decision moves from "did it raise" to
`Reconciliation.verdict`. It was deliberately *not* wired into `phase11-golden/`, because that
driver's outputs are the Phase-1.1 measurement of record. Wiring it in belongs to the slice that
next spends tokens on screening.

---

## 2. Feature availability for T1

**`criteria_supported` is available on the Phase-1.1 stateless runs and absent from the recorded
conversational controls.**

`ScreenScore.criteria_hit` (a list of sub-criterion ids, required on any score ≥ 2, consumed by
`coverage.py`) is the per-candidate criteria-supported count T1 needs. It is populated on both
Phase-1.1 runs, on every kept candidate, with no gaps:

| run | screened | score 2 with `criteria_hit` | score 3 with `criteria_hit` | mean hits at 2 / at 3 |
|---|---|---|---|---|
| `p11-t1` | 905 | 62/62 | 16/16 | 1.27 / 2.31 |
| `p11-t2` | 1009 | 146/146 | 54/54 | 1.24 / 1.87 |
| `2026-08-19-s3-e2e` (control) | 359 | **0/68** | **0/36** | — |
| `2026-08-19-topic2b` (control) | 713 | **0/197** | **0/104** | — |

The two V1-acceptance control runs predate v0.2: their `screen.json` carries `criteria_hit: []` on
every row. Per the slice's instruction, **T1 is run on those controls without that key** (it
degenerates to score → origin_count → best_retrieval_rank → date, which still differs from T0 by
the rank tie-break and the demotion of date), and no substitute heuristic is derived.

**One recorded alternative, reported rather than substituted.** `2026-08-19-p-standard-t1` and
`-t2` carry `screen.json` files whose cid sets are **identical** to the two control runs (359 and
713 cids), with **zero score differences**, over the **same brief and the same five sub-criteria
(id, name and text all byte-identical)** — but with `criteria_hit` populated on all 104 / 301 kept
rows. Their own `candidates.json` is a different, larger pool (565 / 570), so they are not a
drop-in control; the attribution alone joins 1:1 onto the control cids. Both control runs are
therefore swept **twice**: once as recorded (`t1-control`, `t2-control` — T1 without the key), and
once with the attribution overlay (`t1-control+attr`, `t2-control+attr`), clearly labelled. Six
input runs × 15 configurations = 90 recomputations.

**The reserve T2 could not implement.** `relation: contradicting` is a `RankedEntry` field written
by the rerank step. It does not exist anywhere in the pre-shortlist inputs, so a contradicting
reserve is **not deterministically expressible at shortlist time**. T2 therefore reserves per
sub-criterion only, and the contradicting column below is a *retrospective* count — how many of
each configuration's members the original run's own `ranked.json` later marked contradicting, which
covers only the subset that run reranked. It is a diagnostic, not a measurement of the policy.

The foundational reserve needs no new machinery: `outside_window` is already a **separate list with
its own cap** (`DEFAULT_MAX_OUTSIDE_WINDOW = 12`), so out-of-window classics never compete with
in-window papers for the swept cap. It is held at 12 in every configuration.

T2's reserve depth is `THIN_CRITERION_HITS = 5` — the repo's own count for "this criterion has
enough kept papers" (`coverage.py`). No number was invented.

### Validation of the recomputation

Before any policy was swept, **T0@40 was checked against each run's recorded `shortlist.json`**.
All six input runs reproduce **identically, cid for cid, in order**, in both the `in_window` and
`outside_window` lists (`sweep.check_control_reproduces_shipped()`). The sweep's control arm is the
shipped code's own output, not a re-implementation that resembles it.

---
