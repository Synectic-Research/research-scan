# phase14 — rerank judgment contract, 2×2 factorial with a fresh control

The final optimisation experiment in the stateless-processing programme. Its outcome selects a
rubric variant or freezes the current reranker; failure does not authorise another tuning slice.

Phase-1.2C exhausted deterministic selection: no tie-break ladder over the recorded features
recovers the missing goldens, because on `defaults-savings/R40` every loss is a **SCORE-LOSS** — the
golden's `overall` is strictly below the boundary row's, so no ladder beginning with `overall DESC`
can reach it. Two defects remain, and they are properties of the judgement, not of the ordering:

* **a saturated scale** — `overall == 3` on 419 of 840 recorded rows, `0` never used once, and 23–27
  of 40 in-window rows tied at the top on `llm-lit-search/R40`;
* **a stable content disagreement** — 6 of the 7 `defaults-savings` goldens that reach the reranker
  sit at `overall 2` in every replicate against a boundary of 3.

## The factorial

| cell | FACTOR S — discrimination contract | FACTOR C — content correction |
|---|---|---|
| **C0** | off | off | ← the fresh control; every comparison is against this |
| **S** | on | off |
| **C** | off | on |
| **SC** | on | on |

Nothing under `skills/` or `src/` is touched. `variants.py` reads the shipped rubric and applies
each factor's patches from `patches/*.md`; `C0` is asserted byte-identical to the shipped file, and
the C0 *system prompt* is asserted byte-identical to `phase11-golden/rerank.py`'s at the top of
every run. The generated texts and their diffs are in `rubrics/`.

Each factor has two edit sites, because the current rubric decides `overall` in two places and
patching one of them leaves a rubric that contradicts itself — see `variants.py`'s module docstring
for why, including the pre-registration interpretation behind `C2`.

Frozen and imported, never re-implemented: model, effort, thinking, `record_payload`, the user turn,
the stratified cut, `RERANK_CHUNK`, the attempt policy, the cost model, the T1@40 shortlist and its
canonical ordering, `verify`, `emit`, and every slot rule in `research_scan.select`. Phase-1.2C's
reconcile-and-re-ask is active on every chunk.

## Layout

| path | what it is |
|---|---|
| `patches/` | the eight patch texts, as markdown. The ratification artefact |
| `rubrics/` | the four generated variant texts and the three diffs against C0 |
| `variants.py` | patch application, digests, the contamination check |
| `schema14.py` | the wire schema per cell; `priority_rank` in the S cells only |
| `contract14.py` | the `priority_rank` contract and its exit-2 class |
| `select14.py` | the ordering key each cell's result is read under, and the merge rule |
| `driver14.py` | the call path: frozen mechanics, one rubric substitution, one schema field |
| `run14.py` | one replicate, end to end |
| `analyze14.py` | the metric layer |
| `rule14.py` | the pre-registered outcome rule, with its thresholds fixed in advance |
| `deviation14.py` | the one protocol deviation, and an exact bound on what it could have changed |
| `tables14.py` | the report's tables |
| `selfcheck14.py` | $0 proof that the metric and ruling layers work, before any spend |
| `test_phase14.py` | the offline suite, including the 30-run shipped-key control replay |
| `runs/`, `results/`, `logs/` | recordings, derived numbers, per-replicate logs |

## Running it

```sh
export ANTHROPIC_API_KEY=...
./phase14.sh 1 3 C0 S C SC     # stage 1 — 3 replicates of every cell, both topics
./phase14.sh 4 5 C0            # stage 2 — extend the control and any contender to 5
.venv/bin/python analyze14.py && .venv/bin/python rule14.py && .venv/bin/python tables14.py
```

Both topic streams run in parallel against one flock'd ledger and a \$33 cap (raised from
\$30 for stage 2, in `run14.py`; a budget guard, not a pre-registered threshold); ~10 minutes a
replicate. Every replicate is skipped if its `summary.json` exists, so the script resumes rather
than repeats.

## Rules

The arc rules in `../README.md` bind here: append-only, the report cites the file, nothing is
imported by `src/`, and `.venv/` stays out of git.

One more, specific to this slice. **The ruling is mechanical.** `rule14.py` was written and
committed before the first replicate ran, with numbers in place of the slice's qualitative words,
so the outcome is read out of the data rather than argued from it.

## Outcome

**OUTCOME C — freeze the current reranker.** No cell cleared the control. Every candidate lost
ground on `llm-lit-search` (non-inferiority has no tolerance band) and every candidate dropped
`PaSa` — stable at 4/5 in C0 — below the 0.6 floor. `results/ruling.json` is the ruling;
`results/tables.md` is what the report cites. Per the slice's exit rule, failure does not authorise
another tuning slice, and the programme closes here.

## Deviations

One, recorded rather than repaired.

`llm-lit-search/S/rep4` does not exist. It was attempted twice and died both times inside
`contract14.check_batch` on chunk 3 with `PriorityContractViolation`, the slice's own pre-registered
exit-2 class — `1 overall==3 row(s) carry no rank … ranks not unique: [4]`, then `ranks not unique:
[3]` (`logs/p11-t2-S-rep4.log`). The violation is raised after reconciliation has accepted the
chunk, by design, so reconcile-and-re-ask cannot recover it and the replicate has no emitted set.
That cell is analysed at n=4; every other cell is n=5. The re-ask path did fire: each attempt
logged `c1, c2, c3, c3/a2`, so chunk 3 was re-asked, reconciliation accepted the second response,
and `check_batch` rejected it anyway — four generations of the same chunk, none conforming.

The absence is not at random — the cell that failed to produce it is the cell whose contract
failed — so it is treated as evidence both ways. It is the only contract failure in all 40 attempted
runs of the slice, and it is a robustness fact about FACTOR S, which introduces that contract.
It is also not permitted to become a loophole: `deviation14.py` bounds it exactly, and
`results/deviation_s_r4.json` records that no value the missing replicate could have taken flips
any clause. Non-inferiority would have needed it to score 4 and materially-better 9, against a
reachable ceiling of 3; `PaSa` is 0/4, so even a best-case fifth hit leaves it at 1/5, below the
0.6 floor; and the saturation clause was already lost on `defaults-savings`, which is complete.
