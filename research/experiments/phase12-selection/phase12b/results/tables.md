## Cell table

| cell | n | reachable ceiling | recall@10 per replicate | worst | mean | mean pairwise J | reserve fills (found/contra/review) | criterion coverage | frontier tok (mean) | $ (sum) | wall s (mean) |
|---|---|---|---|---|---|---|---|---|---|---|---|
| **t1 R15** | 3 | 4/10 | 2/10, 2/10, 2/10 | **2/10** | 2 | 0.7172 | 2/2/2 · 0/0/0 · 0/0/0 | 6/6 | 28,783 | $0.7090 | 257 |
| **t1 R20** | 3 | 6/10 | 3/10, 3/10, 2/10 | **2/10** | 2.667 | 0.8788 | 2/2/2 · 0/0/0 · 0/0/0 | 6/6 | 41,401 | $1.0018 | 309 |
| **t1 R25** | 3 | 6/10 | 1/10, 2/10, 1/10 | **1/10** | 1.333 | 0.6239 | 2/2/2 · 0/0/0 · 0/0/0 | 5/6, 6/6 | 48,568 | $1.1710 | 358 |
| **t1 R40** | 3 | 7/10 | 1/10, 1/10, 1/10 | **1/10** | 1 | 0.6239 | 2/2/2 · 0/0/0 · 0/0/0 | 5/6, 6/6 | 79,938 | $1.9417 | 614 |
| **t2 R15** | 3 | 1/6 | 1/6, 1/6, 1/6 | **1/6** | 1 | 0.8182 | 0/0/0 · 0/0/0 · 0/0/0 | 5/5 | 35,571 | $0.8222 | 236 |
| **t2 R20** | 3 | 1/6 | 1/6, 1/6, 1/6 | **1/6** | 1 | 0.7677 | 0/0/0 · 0/0/0 · 0/1/0 | 5/5 | 45,407 | $1.0131 | 290 |
| **t2 R25** | 3 | 1/6 | 1/6, 1/6, 1/6 | **1/6** | 1 | 0.6317 | 0/0/0 · 0/0/0 · 0/0/0 | 5/5 | 61,698 | $1.4113 | 407 |
| **t2 R40** | 5 | 3/6 | 3/6, 2/6, 1/6, 1/6, 2/6 | **1/6** | 1.8 | 0.5276 | 0/0/0/0/0 · 0/0/0/0/0 · 0/1/1/0/1 | 5/5 | 92,671 | $3.4832 | 597 |

## Golden inclusion frequencies


**defaults-savings**

| golden | screen | reaches reranker | R15 inclusion | R20 inclusion | R25 inclusion | R40 inclusion |
|---|---|---|---|---|---|---|
| Active vs. Passive Decisions and Crowd-Out in Retirement Savings Accounts: Evidence from Denmark | 3 | R15 R20 R25 R40 | 1/3 | 0/3 | 0/3 | 0/3 |
| Automatic Enrollment with a 12% Default Contribution Rate | 2 | R20 R25 R40 | 0/3 | 2/3 | 1/3 | 0/3 |
| Default Options and Retirement Saving Dynamics | 3 | R15 R20 R25 R40 | 2/3 | 0/3 | 0/3 | 0/3 |
| Employer-Based Short-Term Savings Accounts | 3 | R15 R20 R25 R40 | 0/3 | 0/3 | 0/3 | 0/3 |
| For Better or For Worse: Default Effects and 401(k) Savings Behavior | 2 | R20 R25 R40 | 0/3 | 3/3 | 1/3 | 0/3 |
| Optimal Defaults and Active Decisions | None | — | 0/3 | 0/3 | 0/3 | 0/3 |
| Save More Tomorrow: Using Behavioral Economics to Increase Employee Saving | 1 | — | 0/3 | 0/3 | 0/3 | 0/3 |
| Smaller than We Thought? The Effect of Automatic Savings Policies | 3 | R15 R20 R25 R40 | 3/3 | 3/3 | 2/3 | 3/3 |
| The Power of Suggestion: Inertia in 401(k) Participation and Savings Behavior | 2 | R40 | 0/3 | 0/3 | 0/3 | 0/3 |
| When and why defaults influence decisions: a meta-analysis of default effects | None | — | 0/3 | 0/3 | 0/3 | 0/3 |

**llm-lit-search**

| golden | screen | reaches reranker | R15 inclusion | R20 inclusion | R25 inclusion | R40 inclusion |
|---|---|---|---|---|---|---|
| LitLLM | 2 | — | 0/3 | 0/3 | 0/3 | 0/5 |
| LitSearch | 3 | R40 | 0/3 | 0/3 | 0/3 | 5/5 |
| OpenScholar | 3 | R40 | 0/3 | 0/3 | 0/3 | 3/5 |
| PaSa | 3 | R15 R20 R25 R40 | 3/3 | 3/3 | 3/3 | 1/5 |
| Rethinking Literature Search Evaluation: Deep Research Helps, and Human Citation Lists Are Not a Ground Truth | None | — | 0/3 | 0/3 | 0/3 | 0/5 |
| ScholarQuest: A Taxonomy-Guided Benchmark for Agentic Academic Paper Search in Open Literature Environments | None | — | 0/3 | 0/3 | 0/3 | 0/5 |