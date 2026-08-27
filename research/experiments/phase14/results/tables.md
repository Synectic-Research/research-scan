## 1. Per-cell results

`Δ vs C0` is the difference in mean recall@10 against the fresh control in the same topic. `reachable ceiling` is how many goldens the frozen R40 frontier delivers to the reranker; no cell can exceed it.

| cell | n | reachable ceiling | recall@10 per run | min | mean | Δ vs C0 | top-tier share | mean pairwise J | criterion coverage | cost |
|---|---|---|---|---|---|---|---|---|---|---|
| **defaults-savings** | | | | | | | | | | |
| **C0** | 5 | 7/10 | 0, 1, 1, 1, 1 | **0** | 0.8 | — | 0.325 | 0.8273 | 6/6 | $3.48 |
| **S** | 5 | 7/10 | 0, 1, 1, 2, 1 | **0** | 1 | +0.200 | 0.345 | 0.5972 | 6/6 | $3.30 |
| **C** | 5 | 7/10 | 3, 1, 4, 1, 2 | **1** | 2.2 | +1.400 | 0.415 | 0.4741 | 6/6 | $3.13 |
| **SC** | 5 | 7/10 | 4, 4, 2, 2, 3 | **2** | 3 | +2.200 | 0.475 | 0.5549 | 6/6 | $3.35 |
| **llm-lit-search** | | | | | | | | | | |
| **C0** | 5 | 3/6 | 3, 3, 2, 2, 2 | **2** | 2.4 | — | 0.595 | 0.6434 | 5/5 | $3.91 |
| **S** | 4 | 3/6 | 2, 2, 2, 2 | **2** | 2 | -0.400 | 0.588 | 0.5951 | 5/5 | $3.28 |
| **C** | 5 | 3/6 | 2, 2, 2, 2, 1 | **1** | 1.8 | -0.600 | 0.650 | 0.5573 | 5/5 | $3.46 |
| **SC** | 5 | 3/6 | 2, 2, 2, 2, 2 | **2** | 2 | -0.400 | 0.670 | 0.5752 | 5/5 | $4.15 |


## 2. Per-golden inclusion frequency `f_g`

**`defaults-savings`** — every golden named, C0 vs each cell. `reached` is how many replicates delivered the paper to the reranker at all; a golden the frontier never carries cannot be emitted by any cell.

| golden | reached (C0) | C0 | S | C | SC |
|---|---|---|---|---|---|
| Choukhmane — Default Options & Retirement Saving Dynamics | 5/5 | 0/5 | 0/5 | 1/5 | 4/5 |
| Choi — Smaller than We Thought? | 5/5 | 4/5 | 4/5 | 5/5 | 5/5 |
| Beshears — 12% Default Contribution Rate | 5/5 | 0/5 | 0/5 | 0/5 | 0/5 |
| Berk — Employer-Based Short-Term Savings | 5/5 | 0/5 | 1/5 | 1/5 | 3/5 |
| Madrian & Shea — The Power of Suggestion | 5/5 | 0/5 | 0/5 | 0/5 | 0/5 |
| Thaler & Benartzi — Save More Tomorrow | 0/5 | 0/5 | 0/5 | 0/5 | 0/5 |
| Choi — For Better or For Worse | 5/5 | 0/5 | 0/5 | 2/5 | 1/5 |
| Jachimowicz — Default-effects meta-analysis | 0/5 | 0/5 | 0/5 | 0/5 | 0/5 |
| Carroll — Optimal Defaults & Active Decisions | 0/5 | 0/5 | 0/5 | 0/5 | 0/5 |
| Chetty — Active vs Passive & Crowd-Out | 5/5 | 0/5 | 0/5 | 2/5 | 2/5 |


**`llm-lit-search`** — every golden named, C0 vs each cell. `reached` is how many replicates delivered the paper to the reranker at all; a golden the frontier never carries cannot be emitted by any cell.

| golden | reached (C0) | C0 | S | C | SC |
|---|---|---|---|---|---|
| PaSa | 5/5 | 4/5 | 0/4 | 2/5 | 1/5 |
| RollingEval | 0/5 | 0/5 | 0/4 | 0/5 | 0/5 |
| ScholarQuest | 0/5 | 0/5 | 0/4 | 0/5 | 0/5 |
| LitSearch | 5/5 | 4/5 | 4/4 | 5/5 | 5/5 |
| OpenScholar | 5/5 | 4/5 | 4/4 | 2/5 | 4/5 |
| LitLLM | 0/5 | 0/5 | 0/4 | 0/5 | 0/5 |


## 3. Top-tier population share — the saturation metric

| topic | cell | n | rows | `overall` histogram 0/1/2/3 | top-tier rows per run | top-tier share | relative cut vs C0 |
|---|---|---|---|---|---|---|---|
| defaults-savings | **C0** | 5 | 40 | 0/36/99/65 | 12, 14, 14, 12, 13 | 0.325 | — |
| defaults-savings | **S** | 5 | 40 | 0/37/94/69 | 14, 13, 12, 15, 15 | 0.345 | -6.2% |
| defaults-savings | **C** | 5 | 40 | 0/33/84/83 | 18, 12, 20, 18, 15 | 0.415 | -27.7% |
| defaults-savings | **SC** | 5 | 40 | 0/36/69/95 | 19, 19, 17, 22, 18 | 0.475 | -46.2% |
| llm-lit-search | **C0** | 5 | 40 | 0/4/77/119 | 24, 23, 24, 24, 24 | 0.595 | — |
| llm-lit-search | **S** | 4 | 40 | 0/2/64/94 | 23, 24, 24, 23 | 0.588 | +1.3% |
| llm-lit-search | **C** | 5 | 40 | 0/5/65/130 | 24, 26, 27, 27, 26 | 0.650 | -9.2% |
| llm-lit-search | **SC** | 5 | 40 | 0/1/65/134 | 26, 28, 28, 27, 25 | 0.670 | -12.6% |


## 4. Guaranteed slots and special-slot inclusion

| topic | cell | review | contradicting | foundational | backfill | contradiction incl. freq | foundational incl. freq |
|---|---|---|---|---|---|---|---|
| defaults-savings | **C0** | 0.00 | 0.00 | 2.00 | 0.00 | 1.0 | 1.0 |
| defaults-savings | **S** | 0.00 | 0.00 | 2.00 | 0.00 | 1.0 | 1.0 |
| defaults-savings | **C** | 0.00 | 0.00 | 2.00 | 0.00 | 1.0 | 1.0 |
| defaults-savings | **SC** | 0.80 | 0.00 | 2.00 | 0.00 | 1.0 | 1.0 |
| llm-lit-search | **C0** | 0.60 | 0.00 | 0.00 | 2.00 | 1.0 | 0.0 |
| llm-lit-search | **S** | 0.75 | 0.00 | 0.00 | 2.00 | 1.0 | 0.0 |
| llm-lit-search | **C** | 0.20 | 0.00 | 0.00 | 2.00 | 1.0 | 0.0 |
| llm-lit-search | **SC** | 1.00 | 0.00 | 0.00 | 2.00 | 1.0 | 0.0 |


## 5. Where an S-cell change came from

The same `ranked.json`, selected twice: once under the cell's own ordering key, once under the shipped key. The gap is what `priority_rank` did; the rest is the rubric moving the judgements.

| topic | cell | recall@10 under the cell's key | under the shipped key | attributable to `priority_rank` |
|---|---|---|---|---|
| defaults-savings | **S** | 1 ([0, 1, 1, 2, 1]) | 0.8 ([0, 1, 1, 1, 1]) | +0.200 |
| defaults-savings | **SC** | 3 ([4, 4, 2, 2, 3]) | 2.8 ([2, 4, 2, 3, 3]) | +0.200 |
| llm-lit-search | **S** | 2 ([2, 2, 2, 2]) | 2.25 ([3, 1, 3, 2]) | -0.250 |
| llm-lit-search | **SC** | 2 ([2, 2, 2, 2, 2]) | 2.8 ([2, 3, 3, 3, 3]) | -0.800 |


## 6. The pre-registered outcome rule

Thresholds fixed before the first replicate: {"material_recall_gain": 1.0, "non_inferiority": 0.0, "saturation_relative_cut": 0.25, "stable_in_c0": 0.8, "stable_floor": 0.6}

| cell | materially better | non-inferior both topics | no stable golden lost | no special-slot regression | less saturated | **adopt** |
|---|---|---|---|---|---|---|
| **S** | **FAIL** | **FAIL** | **FAIL** | PASS | **FAIL** | no |
| **C** | PASS | **FAIL** | **FAIL** | **FAIL** | n/a | no |
| **SC** | PASS | **FAIL** | **FAIL** | PASS | **FAIL** | no |


**Main effects (mean recall@10):** `{"S": {"defaults-savings": {"contrasts": {"S-C0": 0.2, "SC-C": 0.8}, "main_effect": 0.5, "interaction": -0.6}, "llm-lit-search": {"contrasts": {"S-C0": -0.4, "SC-C": 0.2}, "main_effect": -0.1, "interaction": -0.6}}, "C": {"defaults-savings": {"contrasts": {"C-C0": 1.4, "SC-S": 2}, "main_effect": 1.7, "interaction": -0.6}, "llm-lit-search": {"contrasts": {"C-C0": -0.6, "SC-S": 0}, "main_effect": -0.3, "interaction": -0.6}}}`


**OUTCOME: OUTCOME C — freeze the current reranker**



## 7. Spend

`$29.5287` over 168 recorded calls.
