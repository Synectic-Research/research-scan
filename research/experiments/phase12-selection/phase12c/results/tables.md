## 1. Feature inventory — `ranked.json`, over all 30 recorded runs / 840 rows

| field | rows carrying it | values observed |
|---|---|---|
| `cid` | 100.0% |  |
| `criteria` | 100.0% | per-criterion grades, ids defaults-savings: C1,C2,C3,C4,C5,C6 / llm-lit-search: C1,C2,C3,C4,C5; grade counts `0`×1420, `1`×1159, `2`×879, `3`×1042 |
| `overall` | 100.0% | `1`×38, `2`×383, `3`×419 |
| `evidence_level` | 100.0% | `computational`×49, `experimental`×495, `observational`×150, `other`×102, `prospective`×1, `rct`×35, `systematic-review`×8 |
| `relation` | 100.0% | `closely-related`×300, `contradicting`×161, `design-changing`×164, `foundational`×109, `plan-influencing`×106 |
| `flags` | 100.0% | `review` true×100, `contradicts` true×205, `methods_paper` true×451 |
| `key_finding` | 100.0% |  |
| `methodology` | 100.0% |  |
| `why_it_matters` | 100.0% |  |
| `limitations` | 100.0% |  |
| `relevance_reason` | 100.0% |  |
| `verification` | 100.0% |  |

Joinable from the 1.1 / 1.2A artefacts (recorded once per topic, identical in every replicate by construction):

| topic | shortlist rows | screen | criteria_supported | origin_count | best_retrieval_rank | date | T1 rank unique |
|---|---|---|---|---|---|---|---|
| `defaults-savings` | 46 | 46 | 46 | 46 | 46 | 45 | yes |
| `llm-lit-search` | 40 | 40 | 40 | 40 | 39 | 40 | yes |

## 2. K0 control validation

`select.select` replayed with the shipped `order_key`, over `ranked.json` order, reproduces the recorded `evidence.json` top-10 **cid-for-cid and in rank order in 30/30 runs**. Recall recomputed from the replayed sets equals Phase-1.2B's `evalrun.score` figures in 10/10 cells (`recall_validated = True`).

## 3. Per-ladder results

`ceil` is Phase-1.2B's reachable ceiling; `base` the recorded baseline. Reserve fills are `foundational / contradicting / review / backfill / diversity`, summed over the cell.

| cell | n | ceil | base | key | recall@10 per run | worst | mean | mean pairwise J | reserve fills | criterion coverage |
|---|---|---|---|---|---|---|---|---|---|---|
| defaults-savings/R15/O1 | 3 | 4 | 5 | **K0** | 2, 2, 2 | **2** | 2 | 0.7172 | 6 / 0 / 0 / 0 / 0 | 6/6 |
|  |  |  |  | **K1** | 2, 3, 3 | **2** | 2.667 | 0.8788 | 6 / 0 / 0 / 0 / 0 | 6/6 |
|  |  |  |  | **K2** | 2, 3, 3 | **2** | 2.667 | 0.8788 | 6 / 0 / 0 / 0 / 0 | 6/6 |
|  |  |  |  | **K3** | 2, 2, 3 | **2** | 2.333 | 0.7677 | 6 / 0 / 0 / 0 / 0 | 6/6 |
| defaults-savings/R20/O1 | 3 | 6 | 5 | **K0** | 3, 3, 2 | **2** | 2.667 | 0.8788 | 6 / 0 / 0 / 0 / 0 | 6/6 |
|  |  |  |  | **K1** | 3, 3, 2 | **2** | 2.667 | 0.8788 | 6 / 0 / 0 / 0 / 0 | 6/6 |
|  |  |  |  | **K2** | 3, 3, 2 | **2** | 2.667 | 0.8788 | 6 / 0 / 0 / 0 / 0 | 6/6 |
|  |  |  |  | **K3** | 1, 2, 1 | **1** | 1.333 | 0.8788 | 6 / 0 / 0 / 0 / 0 | 6/6 |
| defaults-savings/R25/O1 | 3 | 6 | 5 | **K0** | 1, 2, 1 | **1** | 1.333 | 0.6239 | 6 / 0 / 0 / 0 / 0 | 5/6, 6/6 |
|  |  |  |  | **K1** | 1, 1, 1 | **1** | 1 | 0.6667 | 6 / 0 / 0 / 0 / 0 | 5/6, 6/6 |
|  |  |  |  | **K2** | 1, 1, 1 | **1** | 1 | 0.6667 | 6 / 0 / 0 / 0 / 0 | 5/6, 6/6 |
|  |  |  |  | **K3** | 1, 1, 1 | **1** | 1 | 0.8788 | 6 / 0 / 0 / 0 / 0 | 5/6, 6/6 |
| defaults-savings/R40/O1 | 3 | 7 | 5 | **K0** | 1, 1, 1 | **1** | 1 | 0.6239 | 6 / 0 / 0 / 0 / 0 | 5/6, 6/6 |
|  |  |  |  | **K1** | 1, 1, 1 | **1** | 1 | 0.7172 | 6 / 0 / 0 / 0 / 0 | 6/6 |
|  |  |  |  | **K2** | 1, 1, 1 | **1** | 1 | 0.7172 | 6 / 0 / 0 / 0 / 0 | 6/6 |
|  |  |  |  | **K3** | 1, 1, 1 | **1** | 1 | 0.6239 | 6 / 0 / 0 / 0 / 0 | 5/6, 6/6 |
| llm-lit-search/R15/O1 | 3 | 1 | 3 | **K0** | 1, 1, 1 | **1** | 1 | 0.8182 | 0 / 0 / 0 / 6 / 0 | 5/5 |
|  |  |  |  | **K1** | 1, 1, 1 | **1** | 1 | 0.8788 | 0 / 0 / 1 / 6 / 0 | 5/5 |
|  |  |  |  | **K2** | 1, 1, 1 | **1** | 1 | 0.8788 | 0 / 0 / 1 / 6 / 0 | 5/5 |
|  |  |  |  | **K3** | 1, 1, 1 | **1** | 1 | 0.8788 | 0 / 0 / 0 / 6 / 0 | 5/5 |
| llm-lit-search/R20/O1 | 3 | 1 | 3 | **K0** | 1, 1, 1 | **1** | 1 | 0.7677 | 0 / 0 / 1 / 6 / 0 | 5/5 |
|  |  |  |  | **K1** | 1, 1, 1 | **1** | 1 | 0.7677 | 0 / 0 / 1 / 6 / 0 | 5/5 |
|  |  |  |  | **K2** | 1, 1, 1 | **1** | 1 | 0.7677 | 0 / 0 / 1 / 6 / 0 | 5/5 |
|  |  |  |  | **K3** | 1, 1, 1 | **1** | 1 | 0.7677 | 0 / 0 / 0 / 6 / 0 | 5/5 |
| llm-lit-search/R25/O1 | 3 | 1 | 3 | **K0** | 1, 1, 1 | **1** | 1 | 0.6317 | 0 / 0 / 0 / 6 / 0 | 5/5 |
|  |  |  |  | **K1** | 0, 1, 1 | **0** | 0.667 | 0.6744 | 0 / 0 / 1 / 6 / 0 | 5/5 |
|  |  |  |  | **K2** | 0, 1, 1 | **0** | 0.667 | 0.6744 | 0 / 0 / 1 / 6 / 0 | 5/5 |
|  |  |  |  | **K3** | 0, 1, 1 | **0** | 0.667 | 0.6744 | 0 / 0 / 0 / 6 / 0 | 5/5 |
| llm-lit-search/R40/O1 | 5 | 3 | 3 | **K0** | 3, 2, 1, 1, 2 | **1** | 1.8 | 0.5276 | 0 / 0 / 3 / 10 / 0 | 5/5 |
|  |  |  |  | **K1** | 2, 2, 1, 2, 2 | **1** | 1.8 | 0.4663 | 0 / 0 / 5 / 10 / 0 | 5/5 |
|  |  |  |  | **K2** | 2, 2, 1, 2, 2 | **1** | 1.8 | 0.4663 | 0 / 0 / 5 / 10 / 0 | 5/5 |
|  |  |  |  | **K3** | 1, 1, 1, 1, 2 | **1** | 1.2 | 0.6713 | 0 / 0 / 0 / 10 / 0 | 5/5 |
| llm-lit-search/R40/O2 | 2 | 3 | 3 | **K0** | 2, 2 | **2** | 2 | 0.3333 | 0 / 0 / 1 / 4 / 0 | 5/5 |
|  |  |  |  | **K1** | 2, 2 | **2** | 2 | 0.1765 | 0 / 0 / 2 / 4 / 0 | 5/5 |
|  |  |  |  | **K2** | 2, 2 | **2** | 2 | 0.1765 | 0 / 0 / 2 / 4 / 0 | 5/5 |
|  |  |  |  | **K3** | 1, 0 | **0** | 0.5 | 0.4286 | 0 / 0 / 0 / 4 / 0 | 5/5 |
| llm-lit-search/R40/O3 | 2 | 3 | 3 | **K0** | 3, 2 | **2** | 2.5 | 0.5385 | 0 / 1 / 0 / 4 / 0 | 5/5 |
|  |  |  |  | **K1** | 2, 2 | **2** | 2 | 0.5385 | 0 / 0 / 1 / 4 / 0 | 5/5 |
|  |  |  |  | **K2** | 2, 2 | **2** | 2 | 0.5385 | 0 / 0 / 1 / 4 / 0 | 5/5 |
|  |  |  |  | **K3** | 1, 2 | **1** | 1.5 | 0.4286 | 0 / 0 / 0 / 4 / 0 | 5/5 |

### Per-golden inclusion frequency, by ladder — the two G1-passing R40 cells

**`defaults-savings/R40/O1`** — n = 3, reachable ceiling 7

| golden | K0 | K1 | K2 | K3 |
|---|---|---|---|---|
| Active vs. Passive Decisions and Crowd-Out in Retirement Savin | 0/3 | 0/3 | 0/3 | 0/3 |
| Automatic Enrollment with a 12% Default Contribution Rate | 0/3 | 0/3 | 0/3 | 0/3 |
| Default Options and Retirement Saving Dynamics | 0/3 | 0/3 | 0/3 | 0/3 |
| Employer-Based Short-Term Savings Accounts | 0/3 | 0/3 | 0/3 | 0/3 |
| For Better or For Worse: Default Effects and 401(k) Savings Be | 0/3 | 0/3 | 0/3 | 0/3 |
| Save More Tomorrow: Using Behavioral Economics to Increase Emp | 0/3 | 0/3 | 0/3 | 0/3 |
| Smaller than We Thought? The Effect of Automatic Savings Polic | 3/3 | 3/3 | 3/3 | 3/3 |
| The Power of Suggestion: Inertia in 401(k) Participation and S | 0/3 | 0/3 | 0/3 | 0/3 |

**`llm-lit-search/R40/O1`** — n = 5, reachable ceiling 3

| golden | K0 | K1 | K2 | K3 |
|---|---|---|---|---|
| LitLLM | 0/5 | 0/5 | 0/5 | 0/5 |
| LitSearch | 5/5 | 5/5 | 5/5 | 5/5 |
| OpenScholar | 3/5 | 3/5 | 3/5 | 1/5 |
| PaSa | 1/5 | 1/5 | 1/5 | 0/5 |

## 4. Tie depth at the cut boundary

Per run, the two in-window rows straddling the last filled main slot are compared and the first key tier at which they differ is recorded. "terminal" means the ladder fell through to its last tier — T1 rank for K1–K3, and for K0 the stable sort over `ranked.json` order, i.e. the reranker's own emitted order. Determinism by fiat: reproducible, and carrying no signal.

| key | tiers | resolved at each tier (of 30 runs) | fell through to terminal | mean tie band (full prefix) | mean `overall` band |
|---|---|---|---|---|---|
| **K0** | 5 | `overall` 1, `criteria_sum` 13, `origin_count` 13, `date` 3 | **0/30** | 1.30 | 13.9 |
| **K1** | 5 | `overall` 1, `n3` 9, `n2` 9, `n1` 8, `T1 rank` 3 | **3/30** | 1.40 | 13.9 |
| **K2** | 7 | `overall` 1, `n3` 9, `n2` 9, `n1` 8, `screen` 1, `T1 rank` 2 | **2/30** | 1.17 | 13.9 |
| **K3** | 9 | `overall` 1, `review_slot` 3, `counter_slot` 2, `n3` 11, `n2` 2, `n1` 4, `criteria_supported` 4, `T1 rank` 3 | **3/30** | 1.17 | 13.9 |

### The saturation band, per run — K0, `overall` band at the boundary

Column `1.2B tie` is the count Phase-1.2B reported as "rows tied on the exact key deciding tenth place"; reproduced here as the K0 prefix `(overall, criteria_sum)`.

| run | in-window rows | cut at | boundary `overall` | rows sharing it | 1.2B tie |
|---|---|---|---|---|---|
| `defaults-savings/R15/O1/rep1` | 12 | 8 | 2 | **7** | 1 |
| `defaults-savings/R15/O1/rep2` | 12 | 8 | 2 | **7** | 4 |
| `defaults-savings/R15/O1/rep3` | 12 | 8 | 2 | **7** | 2 |
| `defaults-savings/R20/O1/rep1` | 15 | 8 | 2 | **9** | 1 |
| `defaults-savings/R20/O1/rep2` | 15 | 8 | 2 | **8** | 2 |
| `defaults-savings/R20/O1/rep3` | 15 | 8 | 2 | **9** | 2 |
| `defaults-savings/R25/O1/rep1` | 19 | 8 | 2 | **12** | 1 |
| `defaults-savings/R25/O1/rep2` | 19 | 8 | 2 | **12** | 3 |
| `defaults-savings/R25/O1/rep3` | 19 | 8 | 2 | **10** | 2 |
| `defaults-savings/R40/O1/rep1` | 34 | 8 | 3 | **11** | 2 |
| `defaults-savings/R40/O1/rep2` | 34 | 8 | 3 | **9** | 1 |
| `defaults-savings/R40/O1/rep3` | 34 | 8 | 3 | **10** | 2 |
| `llm-lit-search/R15/O1/rep1` | 15 | 10 | 2 | **6** | 1 |
| `llm-lit-search/R15/O1/rep2` | 15 | 10 | 2 | **6** | 1 |
| `llm-lit-search/R15/O1/rep3` | 15 | 10 | 2 | **6** | 1 |
| `llm-lit-search/R20/O1/rep1` | 20 | 10 | 3 | **11** | 2 |
| `llm-lit-search/R20/O1/rep2` | 20 | 10 | 3 | **12** | 3 |
| `llm-lit-search/R20/O1/rep3` | 20 | 10 | 3 | **10** | 1 |
| `llm-lit-search/R25/O1/rep1` | 25 | 10 | 3 | **16** | 1 |
| `llm-lit-search/R25/O1/rep2` | 25 | 10 | 3 | **14** | 4 |
| `llm-lit-search/R25/O1/rep3` | 25 | 10 | 3 | **15** | 2 |
| `llm-lit-search/R40/O1/rep1` | 40 | 10 | 3 | **23** | 5 |
| `llm-lit-search/R40/O1/rep2` | 40 | 10 | 3 | **25** | 3 |
| `llm-lit-search/R40/O1/rep3` | 40 | 10 | 3 | **27** | 3 |
| `llm-lit-search/R40/O1/rep4` | 40 | 10 | 3 | **26** | 6 |
| `llm-lit-search/R40/O1/rep5` | 40 | 10 | 3 | **23** | 6 |
| `llm-lit-search/R40/O2/rep1` | 40 | 10 | 3 | **24** | 4 |
| `llm-lit-search/R40/O2/rep2` | 40 | 10 | 3 | **23** | 4 |
| `llm-lit-search/R40/O3/rep1` | 40 | 10 | 3 | **21** | 2 |
| `llm-lit-search/R40/O3/rep2` | 40 | 10 | 3 | **19** | 5 |

## 5. TIE-LOSS vs SCORE-LOSS decomposition

One row per (run, golden) where the golden **reached the reranker** and was not emitted under K0. The boundary row is the weakest in-window pick the run actually emitted. `SCORE_LOSS` = the golden's `overall` is strictly below the boundary row's, so **no ladder beginning with `overall DESC` can recover it, by construction**. `TIE_LOSS_BAND` = equal `overall`, so a richer key *could* in principle recover it — whether one *does* is the replay's own answer, in the last two columns.

| topic | arm | verdict counts | K1 rescues | K2 rescues | K3 rescues |
|---|---|---|---|---|---|
| `defaults-savings` | R15 | 6 TIE-LOSS-BAND | 2/6 | 2/6 | 1/6 |
| `defaults-savings` | R20 | 10 TIE-LOSS-BAND | 0/10 | 0/10 | 1/10 |
| `defaults-savings` | R25 | 14 TIE-LOSS-BAND | 0/14 | 0/14 | 1/14 |
| `defaults-savings` | R40 | 18 SCORE-LOSS | 0/18 | 0/18 | 0/18 |
| `llm-lit-search` | R40 | 9 TIE-LOSS-BAND | 2/9 | 2/9 | 0/9 |

### Per golden, on the two G1-passing R40 cells

| topic | golden | runs reached | emitted (K0) | TIE-LOSS | SCORE-LOSS | golden `overall` | boundary `overall` |
|---|---|---|---|---|---|---|---|
| `defaults-savings` | Default Options and Retirement Saving Dynamics | 3 | 0 | 0 | 3 | [2] | [3] |
| `defaults-savings` | Smaller than We Thought? The Effect of Automatic Sav | 3 | 3 | 0 | 0 | [3] | [3] |
| `defaults-savings` | Automatic Enrollment with a 12% Default Contribution | 3 | 0 | 0 | 3 | [2] | [3] |
| `defaults-savings` | Employer-Based Short-Term Savings Accounts | 3 | 0 | 0 | 3 | [2] | [3] |
| `defaults-savings` | The Power of Suggestion: Inertia in 401(k) Participa | 3 | 0 | 0 | 3 | [2] | [3] |
| `defaults-savings` | For Better or For Worse: Default Effects and 401(k)  | 3 | 0 | 0 | 3 | [2] | [3] |
| `defaults-savings` | Active vs. Passive Decisions and Crowd-Out in Retire | 3 | 0 | 0 | 3 | [2] | [3] |
| `llm-lit-search` | PaSa | 9 | 5 | 4 | 0 | [3] | [3] |
| `llm-lit-search` | LitSearch | 9 | 9 | 0 | 0 | [3] | [3] |
| `llm-lit-search` | OpenScholar | 9 | 4 | 5 | 0 | [3] | [3] |

### Net golden delta of each ladder, whole slice

| ladder | tie-band losses rescued | goldens K0 emitted that the ladder loses | net |
|---|---|---|---|
| **K1** | 4/39 | 5/48 | **-1** |
| **K2** | 4/39 | 5/48 | **-1** |
| **K3** | 3/39 | 16/48 | **-13** |

## 6. Is the tie-break key itself run-stable?

Percentage of candidate rows whose value for that tier is **identical across every replicate of the cell**. Upstream-joined tiers (screen, `criteria_supported`, `origin_count`, `best_retrieval_rank`, date, T1 rank) are 100% by construction — they are recorded once and never re-asked.

| cell | n | rows | `overall` | grade histogram | `overall`+histogram | `relation` | `flags.review` | `flags.contradicts` |
|---|---|---|---|---|---|---|---|---|
| `defaults-savings/R15/O1` | 3 | 15 | 86.7% | 0.0% | 0.0% | 66.7% | 100.0% | 93.3% |
| `defaults-savings/R20/O1` | 3 | 20 | 95.0% | 5.0% | 5.0% | 80.0% | 100.0% | 70.0% |
| `defaults-savings/R25/O1` | 3 | 25 | 80.0% | 8.0% | 8.0% | 72.0% | 96.0% | 68.0% |
| `defaults-savings/R40/O1` | 3 | 40 | 87.5% | 15.0% | 15.0% | 52.5% | 97.5% | 77.5% |
| `llm-lit-search/R15/O1` | 3 | 15 | 100.0% | 0.0% | 0.0% | 53.3% | 100.0% | 93.3% |
| `llm-lit-search/R20/O1` | 3 | 20 | 80.0% | 5.0% | 0.0% | 60.0% | 100.0% | 90.0% |
| `llm-lit-search/R25/O1` | 3 | 25 | 76.0% | 12.0% | 4.0% | 68.0% | 100.0% | 80.0% |
| `llm-lit-search/R40/O1` | 5 | 40 | 67.5% | 2.5% | 2.5% | 52.5% | 100.0% | 90.0% |
| `llm-lit-search/R40/O2` | 2 | 40 | 60.0% | 17.5% | 12.5% | 72.5% | 100.0% | 97.5% |
| `llm-lit-search/R40/O3` | 2 | 40 | 80.0% | 30.0% | 22.5% | 75.0% | 100.0% | 92.5% |

## 7. Decision rule

| ladder | key tiers | worst recall@10 t1 R40 (base 5) | worst recall@10 t2 R40 (base 3) | mean J t1 R40 | mean J t2 R40 | mean of the two |
|---|---|---|---|---|---|---|
| **K0** | 5 | 1/10 | 1/6 | 0.6239 | 0.5276 | 0.5757 |
| **K1** | 5 | 1/10 | 1/6 | 0.7172 | 0.4663 | 0.5917 |
| **K2** | 7 | 1/10 | 1/6 | 0.7172 | 0.4663 | 0.5917 |
| **K3** | 9 | 1/10 | 1/6 | 0.6239 | 0.6713 | 0.6476 |

Step 1 (worst-run recall@10 per topic) separates nothing: survivors ['K0', 'K1', 'K2', 'K3']. Step 2 (mean Jaccard) conflicts across topics — {'defaults-savings/R40/O1': 'K1', 'llm-lit-search/R40/O1': 'K3'} — and averaging the two topics selects **K3**.

**Winner restores stability AND worst-run recall at R40 on both topics: `False`.**

**RULING: PHASE 1.4 NECESSARY.**
