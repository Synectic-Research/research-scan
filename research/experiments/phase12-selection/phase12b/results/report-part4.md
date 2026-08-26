## 7. Deviations, surprises, recommendation

### Deviations

1. **The `T1@80` arm was not run as an arm.** It is byte-identical to `T1@40` as a rerank input at
   every depth this slice specifies (F1, `results/shortlists.json`). Its 18 runs were reallocated to
   an **R40 arm at `T1@40`** — the only depth in reach that satisfies G1. The question `T1@80`
   existed to answer was settled offline instead (F2: the residual loss is LitLLM at T1 rank 136;
   cap 80 does not reach it).
2. **R40 was added to the depth ladder.** G1 is the slice's lexicographically first gate and is
   unsatisfiable at k ∈ {15, 20, 25}. Running only the specified ladder would have produced
   "every cell fails G1" and no answer to the slice's headline question. R40 is the smallest round
   arm satisfying G1 on both topics (the exact minima are k = 36 and k = 39) and is the shipped
   `DEFAULT_MAX_IN_WINDOW`.
3. **Replicate count.** 3 per cell as specified; the extension rule is triggered by *every*
   replicate (all fall below the G2 baseline) and could not be honoured everywhere inside $18. The
   extension was spent on `t2 R40 O1` alone — the cell carrying the recall answer and the branch
   ruling — taking it to 5. `t1 R40` was left at 3 and its inclusion frequencies are reported as
   frequencies only, with no interval, as the slice requires.
4. **Probe replicate accounting.** O1's replicates come from the primary run rather than being
   re-issued (identical configuration), so the probe cost 4 new runs rather than 6. The
   within-cell variance the probe tests against is therefore measured on 3–5 O1 replicates, not 2 —
   a stronger comparison than specified, not a weaker one.
5. **`verify` was run on every replicate, not only winner and runner-up.** `emit` raises
   `select.NotVerified` without it, so it is not optional. It spends no model tokens.
6. **Two topic streams ran concurrently.** Wall-clock per run is therefore measured under 2-way
   contention and is not directly comparable to Phase 1.1's sequential figures; per-call API seconds
   and token counts are unaffected. The shared ledger is `flock`-protected so the single cap holds
   across both streams.
7. **Own ledger.** Phase 1.1's `spend.json` is a measurement of record and was not appended to;
   this slice writes `phase12b/results/spend.json` with its own $18 cap.

### Surprises

1. **The frontier fix works and costs stability.** `t1 R40` and `t2 R40` are the only cells that
   satisfy G1, and they are the two least stable cells measured. The papers 1.2A recovered into the
   shortlist do reach the output — LitSearch **5/5** and OpenScholar **3/5** on the extended cell —
   but PaSa, a 3/3 lock at every shallower depth, is displaced.
2. **Recall@10 as a scalar hides golden-level churn.** `t1 R15` scores 2/10 in all three replicates
   with two different pairs of papers; `t1 R25` reps 1 and 3 emit only Choi 2024 while rep 2 emits a
   **disjoint** pair. Phase 1.1 read single-shot arms differing by one paper as a depth trend. At
   n = 3 the within-cell spread is the same size as the between-depth differences k\* = 15 rested on.
3. **Order does not matter; resampling does.** The probe was built to find listwise position
   instability and found none — between-ordering dispersion (J 0.445) is *smaller* than
   within-ordering dispersion (0.476), with 38 of 40 rows moved and chunk membership changed.
4. **The reranker is the loss stage, and it is not `emit`.** Under the shipped `select.order_key`
   merit order, 18 of 21 golden-replicate slots at `t1 R40` are `L_rerank` — the reranker saw the
   paper and scored it out of the top ten — and **zero** are `L_select`. The selection rules are
   not displacing golden evidence; the scoring is.
5. **Berk et al 2024 is rejected every time it is seen.** `Employer-Based Short-Term Savings
   Accounts`, screen score 3, which the golden file calls the closest published setting to the
   brief, reaches the reranker at every depth and is emitted **0/12** across all topic-1 replicates.
   That is not variance — it is a stable disagreement between the screening rubric and the rerank
   rubric about the same paper.
6. **Choukhmane 2025 gets worse with more context.** Emitted 2/3 at R15, then `L_rerank` 3/3 at
   R20, R25 and R40. More candidates in the same call moved a golden paper out of the top ten.
7. **The x02 failure family recurred, on the rerank path.** One call in 60 returned
   `extra=['5716814f6adf_placeholder']` while dropping four wanted cids — the same
   structured-output padding defect Phase 1.1 hit six times on screening, now with real cids
   missing as well as a ghost added. Recovered on retry (1.7% of calls, under the 3% bar Phase 1.1
   missed). Independent in-slice evidence that 1.2A's reconciling contract addresses a live defect,
   and that its sub-batch re-ask path — not just ghost-discarding — is the one that matters.
8. **The judge is blind to instability as well as to recall.** `t1 R40 rep1` earns judged precision
   **1.00** and mean relevance **2.375** while emitting one of the seven goldens the reranker was
   shown. Because the judge grades one list at a time, three mutually disagreeing replicates would
   each be graded excellent.
