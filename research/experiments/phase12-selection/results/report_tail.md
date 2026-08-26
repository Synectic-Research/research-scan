
---

## 4. The latent-defect answer, stated plainly

**Yes — cap 40 + T0 loses golden evidence on the old conversational artefacts too. It is a latent
v0.4-era defect, not something the flatter stateless score distribution created.**

On `2026-08-19-topic2b`, the recorded V1-acceptance run for topic 2, **OpenScholar sits at T0 rank
90 of a 289-strong in-window ≥2 population and is cut by the shipped cap of 40.** It is cut at 60
and at 80 as well, and only re-enters at cap 120. That run scored OpenScholar **3** — it is not a
marginal paper being correctly filtered; it is a central one dying at a cap. The same run's own
`evidence.json` never emitted it, and until now that miss was attributed downstream.

The other three inputs qualify the finding without weakening it:

* `2026-08-19-s3-e2e` (topic 1 control): **no golden loss at any cap under any policy**. All 8
  retrieved-and-kept goldens survive T0@40. The 87-candidate in-window population is barely twice
  the cap, and five of the eight goldens are out-of-window and so sit in the separate reserved list.
* `p11-t1` (topic 1 stateless): likewise **no loss at any cap**. All 7 goldens ≥ 2 survive T0@40.
  Topic 1's recall problem is entirely downstream of the shortlist — which is what Phase 1.1 found.
* `p11-t2` (topic 2 stateless): T0@40 keeps **1 of 4**. This is the severe case, and the stateless
  screen makes it worse rather than causing it — the ≥2 population is 200 instead of 289, but 54 of
  those are 3s against a 40-row cap, so the cut now falls *inside the score-3 band*.

**The mechanism is the same on both eras, and it is the tie-break, not the cap.** T0's key is
`(score, origin_count, publication_date)`. On `p11-t2` the 54 score-3 candidates split 7/16/31 by
origin count, so for the 31 papers with a single origin the only remaining discriminator is
**publication date, descending** — a pure recency filter. OpenScholar (2024-11-21) lands at rank
52 and LitSearch (2024-07-10) at rank 54: they are the two oldest score-3 single-origin papers in
the pool. The dates at T0 ranks 36–56 run monotonically 2026-01 → 2024-07. Nothing about relevance
distinguishes them from the papers above; only their age does.

So the defect has two separable halves, and the sweep separates them:

| | topic 2 stateless, T0@40 | mechanism |
|---|---|---|
| lost **to ordering** | OpenScholar, LitSearch | recoverable at the same cap by a better tie-break |
| lost **to the cap** | LitLLM (score 2, T0 rank 188) | unreachable at cap 40 by any swept policy |

*Definitions used throughout:* a golden ≥ 2 excluded by a configuration is **lost to ordering** if
some other swept policy admits it **at the same cap**, and **lost to the cap** if no swept policy
admits it at that cap.

---

## 5. OpenScholar / LitSearch fate

Named in every configuration in §3's fate table. The summary:

| input run | T0@40 | T1@40 = T2@40 | first config that recovers both |
|---|---|---|---|
| `p11-t2` (stateless) | OpenScholar **out** (52), LitSearch **out** (54) | OpenScholar **in** (38), LitSearch **in** (39) | **T1@40 / T2@40** — no cap increase |
| `topic2b` (control, as recorded) | OpenScholar **out** (90), LitSearch in (36) | OpenScholar **out** (62), LitSearch in (9) | T1@80 / T2@80 (T0 needs cap 120) |
| `topic2b` + attribution overlay | OpenScholar **out** (90), LitSearch in (36) | OpenScholar **in** (4), LitSearch **out** (56) | T1@60 / T2@60 (T0 needs cap 120) |

Two things worth naming rather than smoothing over. First, on the control, **T1 at cap 40 does not
save OpenScholar** — it lifts it from rank 90 to 62, which is a large improvement that a 40-row cap
still cuts. Second, on the overlay variant T1@40 **costs** LitSearch, moving it from rank 36 to 56:
LitSearch carries one criterion in that attribution against competitors carrying two, so demoting
date and promoting `criteria_supported` demotes it. T1 is not a free improvement at every cap; it
is a decisive one at cap 40 on the input the architecture will actually run.

PaSa and LitLLM, for completeness: PaSa is retained in every configuration on every input (T1 lifts
it from rank 20 to 2 on `p11-t2`). LitLLM is retrieved only by the stateless run, scores 2, and is
cut at every finite cap by every policy — T1 lifts it from rank 188 to 136, which changes nothing
that matters.

---

## 6. Winner and runner-up

Applied over the two Phase-1.1 golden scans — the inputs the frontier policy will actually run on —
with `cap = ∞` excluded, as the slice specifies it is diagnostic only.

**1. Maximise retrievable-golden survival into the rerank frontier.** Pooled over both stateless
topics (7 + 4 = 11 goldens scored ≥ 2):

| | @40 | @60 | @80 | @120 | @∞ *(diag)* |
|---|---|---|---|---|---|
| T0 | **8/11** | 10/11 | 10/11 | 10/11 | 11/11 |
| T1 | **10/11** | 10/11 | 10/11 | 10/11 | 11/11 |
| T2 | **10/11** | 10/11 | 10/11 | 10/11 | 11/11 |

10/11 is the finite maximum; every configuration except T0@40 reaches it. T0@40 — what ships today
— is the unique loser at step 1.

**2. Preserve all criterion / relation / foundational reserves.** Every surviving configuration
holds full criterion coverage (6/6 on topic 1, 5/5 on topic 2), retains all 6 out-of-window
foundational candidates on topic 1 (topic 2 has none to retain, unchanged from Phase 1.1), and none
can be scored on the contradicting reserve, which is not expressible pre-rerank. **No
discrimination at this step.**

**3. Minimise shortlist size.** Cap 40 gives 46 + 40 = 86 rows across the two topics, against 126 at
cap 60 and 158 at cap 80. **Only T1@40 and T2@40 survive.**

**4. Prefer the simpler policy.** T2 is a **pure no-op on all six input runs at every cap**: its
per-criterion reserve admits 13–16 candidates on the stateless runs, and every one of them is
already inside the T1 order's own top 40. Membership is identical to T1 in 30 of 30 comparisons.

> ### Winner — **T1 @ cap 40**
> `score DESC, criteria_supported DESC, origin_count DESC, best_retrieval_rank ASC, date DESC`, at
> the shipped `DEFAULT_MAX_IN_WINDOW = 40`. It is the only step-3 survivor that is also the simpler
> of the two, it recovers both OpenScholar and LitSearch on `p11-t2`, and it changes **no cap, no
> weight, and no rerank cost** — the frontier stays 40 rows wide.

> ### Runner-up — **T1 @ cap 80**
> By strict lexicographic reading the second place is T2@40, but it is byte-identical to the winner
> on every input, so carrying it forward tests nothing. The useful second recommendation is the
> smallest configuration that maximises golden survival on **all six** input runs, controls
> included: T1@80 is 5/5 on `topic2b` and on its overlay variant, 8/8 on `s3-e2e`, and matches the
> winner on both stateless runs. It costs a 158-row frontier against 86 — roughly double the rerank
> input — and is the arm to run if 1.2B wants the control-era regression closed too.

**The claim this sweep does not make.** These configurations determine which papers reach the
rerank frontier. Nothing here says what the reranker or `emit` would do with them: every paper
beyond the original cap of 40 was never reranked, so **no simulated recall@10 is reported for any
configuration, and none was computed**. T1@40 puts OpenScholar and LitSearch in front of the
reranker; whether the reranker then selects them is Phase-1.2B's measurement to make.

---

## 7. Deviations, surprises, and the recommendation

**Deviations.**

1. Part 1's code lives in `phase12-selection/contract.py` rather than editing
   `phase11-golden/lib/common.py`. Editing the Phase-1.1 driver would have changed the artefact set
   that report measured. The integration point is documented in the module docstring.
2. Six input runs were swept instead of four (90 configurations, not 60): the two control runs are
   swept both as recorded and with the `p-standard` attribution overlay, because T1's key feature is
   absent from the recorded controls.
3. Three of the six recorded x02 attempt bodies were not preserved verbatim by the Phase-1.1 driver.
   Fixtures are rebuilt to the recorded error signature, and the fixture file states this per entry.
4. `max_outside_window` was held at 12 in all 90 configurations. The slice swept the in-window cap;
   the out-of-window list has its own cap and was not in scope.

**Surprises.**

1. **The shortlist defect is an ordering defect first.** The Phase-1.1 report framed OpenScholar and
   LitSearch as cap losses at ranks 52 and 54 against a cap of 40. They are, but a tie-break change
   moves them to 38 and 39 — inside the existing cap. The cap was never the binding constraint for
   those two papers.
2. **T0's date tie-break is a recency filter exactly where it hurts most.** It only becomes the
   discriminator when score and origin count are tied, which is precisely the dense score-3
   single-origin band a large pool produces — 31 of 54 score-3 papers on `p11-t2`.
3. **The defect predates the stateless architecture.** OpenScholar dies at rank 90 in the recorded
   V1-acceptance run for topic 2, at a screen score of 3.
4. **T2 bought nothing, anywhere.** A stratified per-criterion reserve is a no-op on all six inputs
   at all five caps, because T1's own ordering already surfaces each criterion's top five. The
   reserve machinery would only start to matter if a criterion's papers were systematically low on
   the other keys.
5. **T1 is not monotonically good.** On the overlay control it costs LitSearch 20 rank positions at
   cap 40. Worth watching in 1.2B rather than assuming away.

**Recommendation for Phase 1.2B.** Carry **T1@40** as the primary and **T1@80** as the robustness
arm; T1@40 is the change to implement first, because it recovers the two named papers into the
rerank frontier at zero cap cost and zero added rerank tokens, and 1.2B's job is then the one
question this slice is forbidden to answer — whether the reranker keeps them.

---

## Artefacts

```
research/experiments/phase12-selection/
  contract.py                       the reconciling CID contract + bounded retry driver
  test_contract.py                  25 tests, all passing
  fixtures/x02-batch.json           the real 25-item batch
  fixtures/x02-response-salvage.json          the byte-recoverable 27-row response
  fixtures/x02-attempts-recorded.json         six attempts, rebuilt to their recorded signatures
  sweep.py                          the offline sweep + the T0@40-reproduces-shipped check
  tables.py                         table rendering
  results/sweep.json                every measurement, 6 runs × 15 configurations
  results/tables.md                 the rendered tables
  results/pytest.txt                the test run
```
