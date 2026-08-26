## 5. Gates G1–G5

No favourable rounding anywhere. Thresholds are read as written.

### G1 — frontier sufficiency: **FAIL at R15/R20/R25 on both topics, PASS at R40**

"All screened-≥2 goldens that fit under the policy reach the reranker." Under `T1@40` the
qualifying set is 7 goldens on topic 1 and 3 on topic 2 (LitLLM is an upstream shortlist loss —
see F2, documented, not charged to the reranker).

| topic | R15 | R20 | R25 | R40 |
|---|---|---|---|---|
| `defaults-savings` | 4/7 — **fail** | 6/7 — **fail** | 6/7 — **fail** | 7/7 — **pass** |
| `llm-lit-search` | 1/3 — **fail** | 1/3 — **fail** | 1/3 — **fail** | 3/3 — **pass** |

Upstream losses, documented and not charged to the reranker: topic 1 — Save More Tomorrow
(screen 1), the Jachimowicz meta-analysis and Carroll et al 2009 (never retrieved); topic 2 —
RollingEval and ScholarQuest (never retrieved), LitLLM (shortlist, T1 rank 136).

**Only the two R40 cells survive G1.** Everything else is eliminated here, lexicographically,
before any recall number is read.

### G2 — worst-run recall@10 ≥ recorded baseline: **FAIL in every cell**

Baselines re-verified against `eval/results/2026-08-19-{defaults-savings,llm-lit-search}.json`:
**5/10** (topic 1, `2026-08-19-s3-e2e`) and **3/6** (topic 2, `2026-08-19-topic2b`). Confirmed, and
identical to Phase 1.1's re-derivation.

| cell | worst-run | baseline | verdict |
|---|---|---|---|
| t1 R40 (G1 passer) | **1/10** | 5/10 | **fail** |
| t2 R40 (G1 passer) | **1/6** | 3/6 | **fail** |
| best worst-run anywhere (t1 R20) | 2/10 | 5/10 | fail |

The extension rule ("any replicate below the baseline gate → extend to 5") is triggered by every
replicate in the slice. It could not be honoured for every cell inside the $18 cap; it was spent on
the decisive cell only (§ deviations).

### G3 — no regression in contradicting recovery, foundational recovery, criterion coverage

| measure | topic 1 baseline | t1 R40 | topic 2 baseline | t2 R40 | verdict |
|---|---|---|---|---|---|
| foundational slots filled | 2 | **2, 2, 2** | 2 | **0, 0, 0** | t1 pass · t2 fail-upstream |
| `selection_reason: contradicting` | 0 | 0, 0, 0 | 0 | 0, 0, 0 | pass |
| emitted `relation: contradicting` | 0 | **5, 2, 4** | 2 | 1, 2, 3 | pass |
| criterion coverage | — | 5/6, 6/6, 6/6 | — | **5/5** ×3 | pass |

**Foundational recovery is reported conditional on frontier availability, as the slice requires.**
Topic 2's `shortlist.outside_window` is empty: the stateless screener scored all 16 out-of-window
candidates 0 or 1, so no foundational paper was available to any cell at any depth. That is a
Phase-1.3 screening matter and is *not* a rerank regression. Conditional on availability, topic 1
fills 2/2 in every replicate of every cell and topic 2 is not assessable.

Contradicting recovery is ahead of baseline on topic 1 in every replicate and varies 1–3 against a
baseline of 2 on topic 2 — itself a further instance of replicate variance, not a regression.

### G4 — stability: **FAIL**

Two clauses. The threshold is the slice's own diagnostic 0.65, not doctrine.

| cell | mean pairwise Jaccard | ≥ 0.65? |
|---|---|---|
| t1 R15 | 0.717 | yes |
| t1 R20 | 0.879 | yes |
| t1 R25 | 0.624 | **no** |
| t1 R40 (G1 passer) | 0.624 | **no** |
| t2 R15 | 0.818 | yes |
| t2 R20 | 0.768 | yes |
| t2 R25 | 0.632 | **no** |
| **t2 R40** (G1 passer) | **0.502** | **no** |

**Both G1-passing cells fail the Jaccard clause.** Stability falls monotonically with depth on
topic 2 (0.818 → 0.768 → 0.632 → 0.502) — the arms that satisfy frontier sufficiency are exactly
the arms that fail stability.

Second clause — no golden flipping 3/3 ↔ 0/3 across orderings: **pass**. LitSearch is emitted in
7 of 7 probe runs; PaSa 5/7; OpenScholar 3/7. OpenScholar's 2/3 → 0/2 → 1/2 swing is the widest
and does not reach a 3/3 ↔ 0/3 flip.

**G4 fails on clause one.**

### G5 — minimality among passers: **not reached**

G5 discriminates only among configurations that passed G1–G4. None did. Recorded for the file: at
equal policy, R40 costs 79.9k (t1) / 95.3k (t2) mean frontier tokens against R15's 28.8k / 35.6k,
and ~2.4× the wall clock — so the arms that satisfy G1 are also the most expensive, and the
cheapest arms are the ones that cannot see the evidence.
