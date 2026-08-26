### Per-topic run record

| | topic 1 `defaults-savings` | topic 2 `llm-lit-search` |
|---|---|---|
| run dir | `research/experiments/phase11-golden/runs/p11-t1` | `research/experiments/phase11-golden/runs/p11-t2` |
| profile / domain / window | standard · behavioral · from 2023-08 | standard · cs · from 2024-01 |
| purpose inferred by the planning call | `build` | `research` |
| routed sources (hits, failed) | openalex 320/0, s2 247/0 | openalex 320/0, s2 280/0, arxiv 272/0 |
| pool screened | 905 | 1009 |
| out-of-window in pool | 19 | 16 |
| screened ≥2 | 78 | 200 |
| shortlist (in+out) | 40+6 | 40+0 |
| gap round | ran, 4 queries | ran, 4 queries |

### defaults-savings — golden fate

| golden paper | retrieved | screen | ≥2 | shortlist pos | in R15 cut | in R15 top-10 |
|---|---|---|---|---|---|---|
| `10.1257/aer.20210881` Default Options and Retirement Saving Dynami | yes | 3 | yes | 5 (in) | yes | yes |
| `10.3386/w32828` Smaller than We Thought? The Effect of Autom | yes | 3 | yes | 2 (in) | yes | yes |
| `10.3386/w31601` Automatic Enrollment with a 12% Default Cont | yes | 2 | yes | 15 (in) | no | no |
| `10.3386/w32074` Employer-Based Short-Term Savings Accounts | yes | 3 | yes | 12 (in) | yes | yes |
| `10.3386/w7682` The Power of Suggestion: Inertia in 401(k) P | yes | 2 | yes | 16 (in) | no | no |
| `10.1086/380085` Save More Tomorrow™: Using Behavioral Econom | yes | 1 | **no** | — | no | no |
| `10.3386/w8651` For Better or For Worse: Default Effects and | yes | 2 | yes | 46 (out) | no | no |
| `10.1017/bpp.2018.43` When and why defaults influence decisions: a | **no** | — | **no** | — | no | no |
| `10.1162/qjec.2009.124.4.1639` Optimal Defaults and Active Decisions | **no** | — | **no** | — | no | no |
| `10.1093/qje/qju013` Active vs. Passive Decisions and Crowd-Out i | yes | 3 | yes | 41 (out) | yes | no |

### llm-lit-search — golden fate

| golden paper | retrieved | screen | ≥2 | shortlist pos | in R15 cut | in R15 top-10 |
|---|---|---|---|---|---|---|
| `10.48550/arXiv.2501.10120` PaSa: An LLM Agent for Comprehensive Academi | yes | 3 | yes | 20 (in) | no | no |
| `10.48550/arXiv.2605.29234` Rethinking Literature Search Evaluation: Dee | **no** | — | **no** | — | no | no |
| `10.48550/arXiv.2606.20235` ScholarQuest: A Taxonomy-Guided Benchmark fo | **no** | — | **no** | — | no | no |
| `10.48550/arXiv.2407.18940` LitSearch: A Retrieval Benchmark for Scienti | yes | 3 | yes | — | no | no |
| `10.48550/arXiv.2411.14199` OpenScholar: Synthesizing Scientific Literat | yes | 3 | yes | — | no | no |
| `10.48550/arXiv.2402.01788` LitLLM: A Toolkit for Scientific Literature  | yes | 2 | yes | — | no | no |

### Rerank-depth sweep

| topic | arm | reranked (in+out) | recall@10 | recall@25 | foundational | contradicting (reason / relation) | review | criterion coverage | frontier tok | tok/item | cost | wall s | judged precision | judged mean |
|---|---|---|---|---|---|---|---|---|---|---|---|---|---|---|
| defaults-savings | R10 | 10 (8+2) | 3/10 | 3/10 | 2/2 | 0 / 4 | 0 | 6/6 | 18137 | 1813 | $0.1567 | 124 | 0.875 | 2.5 |
| defaults-savings | R15 | 15 (12+3) | 3/10 | 4/10 | 2/2 | 0 / 4 | 0 | 6/6 | 28775 | 2877 | $0.2453 | 219 | 1.0 | 2.625 |
| defaults-savings | R20 | 20 (15+5) | 2/10 | 5/10 | 2/2 | 0 / 3 | 0 | 5/6 | 33458 | 3345 | $0.2568 | 246 | 1.0 | 2.625 |
| defaults-savings | R25 | 25 (19+6) | 1/10 | 7/10 | 2/2 | 0 / 2 | 0 | 6/6 | 36098 | 3609 | $0.2656 | 245 | 1.0 | 2.5 |
| defaults-savings | Rall | 46 (40+6) | 1/10 | 6/10 | 2/2 | 0 / 3 | 0 | 5/6 | 86033 | 8603 | $0.6733 | 617 | 0.875 | 2.5 |
| llm-lit-search | R10 | 10 (10+0) | 0/6 | 0/6 | 0/2 | 0 / 3 | 0 | 5/5 | 27949 | 2794 | $0.2353 | 193 | 0.9 | 2.3 |
| llm-lit-search | R15 | 15 (15+0) | 0/6 | 0/6 | 0/2 | 0 / 3 | 0 | 5/5 | 38087 | 3808 | $0.3094 | 246 | 1.0 | 2.6 |
| llm-lit-search | R20 | 20 (20+0) | 1/6 | 1/6 | 0/2 | 0 / 4 | 0 | 5/5 | 59462 | 5946 | $0.4793 | 416 | 0.9 | 2.6 |
| llm-lit-search | R25 | 25 (25+0) | 1/6 | 1/6 | 0/2 | 0 / 2 | 0 | 5/5 | 69854 | 6985 | $0.5545 | 499 | 0.9 | 2.6 |
| llm-lit-search | Rall | 40 (40+0) | 1/6 | 1/6 | 0/2 | 0 / 2 | 1 | 5/5 | 105379 | 10537 | $0.8230 | 744 | 1.0 | 2.5 |

### P(golden | screen score), pooled over both topics

| score | pool | golden | P(golden \| score) |
|---|---|---|---|
| 0 | 1283 | 0 | 0.00000 |
| 1 | 353 | 1 | 0.00283 |
| 2 | 208 | 4 | 0.01923 |
| 3 | 70 | 7 | 0.10000 |
| **all** | **1914** | **12** | **0.00627** |

### Model spend and wall clock, per topic

| stage | t1 calls | t1 cost | t1 wall s | t2 calls | t2 cost | t2 wall s |
|---|---|---|---|---|---|---|
| plan (1 stateless call) | 1 | $0.0262 | 14.1 | 1 | $0.0464 | 31.5 |
| screen · per-family breakdown | see `screen_wall_measured` in measurements.json | | | | | |
| gap queries (1 stateless call) | 1 | $0.0298 | 11.5 | 1 | $0.0327 | 12.5 |
| rerank R15 | 2 | $0.2453 | 219.3 | 2 | $0.3094 | 246.1 |
| **screening total** (ledger: every attempt) | 39 | $1.1756 | 194.6 | 49 | $1.5133 | 305.7 |
| **scan total (plan + screen + gap + R15 + CLI)** | 42 | $1.4769 | 717.6 | 52 | $1.9018 | 809.9 |

### CLI stage seconds (no model spend)

| stage | t1 | t2 |
|---|---|---|
| coverage | 0.0 | 0.0 |
| expand | 100.0 | 92.0 |
| expand-r2 | 37.0 | 38.0 |
| init | 0.0 | 0.0 |
| retrieve | 116.0 | 11.0 |
| retrieve-r2 | 25.0 | 73.0 |
| shortlist | 0.0 | 0.0 |
