# Phase-1.2B — the three offline findings, established before any tokens were spent

All three are deterministic recomputations over Phase-1.1 recorded artefacts. Sources:
`results/shortlists.json` (cut identity), `results/frontier_fate.json` (stage fates).

## F1 — T1@80 is not a distinct arm at any depth this slice runs

A cap is a truncation of one order, and `rerank.cut()` takes a *prefix* of `in_window` and a
prefix of `outside_window`. So for any depth whose in-window take is <= 40, T1@40 and T1@80
hand the reranker the identical row list, in the identical order.

| topic | arm | cut (in+out) T1@40 | cut (in+out) T1@80 | identical rows |
|---|---|---|---|---|
| defaults-savings | R15 | 12+3 | 12+3 | yes |
| defaults-savings | R20 | 15+5 | 15+5 | yes |
| defaults-savings | R25 | 19+6 | 19+6 | yes |
| defaults-savings | R30 | 24+6 | 24+6 | yes |
| defaults-savings | R40 | 34+6 | 34+6 | yes |
| llm-lit-search | R15 | 15+0 | 15+0 | yes |
| llm-lit-search | R20 | 20+0 | 20+0 | yes |
| llm-lit-search | R25 | 25+0 | 25+0 | yes |
| llm-lit-search | R30 | 30+0 | 30+0 | yes |
| llm-lit-search | R40 | 40+0 | 40+0 | yes |

The two policies diverge only at `Rall`, where T1@80 adds 32 (topic 1) / 40 (topic 2) further
rows. None of those rows is a golden paper, so at `Rall` T1@80 is a distractor-load arm, not a
recall-control arm.

## F2 — the T1@40 residual loss is LitLLM, and T1@80 does not recover it

1.2A's open question, answered by name and offline.

| topic | golden | retrieved | screen | T1 in-window rank (uncapped, of 200) | in T1@40 | in T1@80 |
|---|---|---|---|---|---|---|
| llm-lit-search | LitLLM (10.48550/arXiv.2402.01788) | yes | 2 | **136** | no | **no** |

LitLLM is the single golden that T1@40 loses on the two stateless runs, and cap 80 is 56 ranks
short of it. Only an uncapped shortlist reaches it. The recall-control arm as specified cannot
answer the cap question, because the answer is already no.

## F3 — the specified depth ladder re-cuts exactly the papers T1@40 was chosen to save

T1@40's whole value in 1.2A was lifting OpenScholar to in-window rank 38 and LitSearch to 39,
inside a cap of 40. The stratified cut at k=15/20/25 takes only the first 15/20/25 in-window
rows, so it discards both again.

Goldens delivered to the reranker, T1@40:

| topic | golden | list | rank | R15 | R20 | R25 | R40 |
|---|---|---|---|---|---|---|---|
| defaults-savings | Choukhmane 2025 (Default Options and Retirement Saving Dynamics) | in | 8 | yes | yes | yes | yes |
| defaults-savings | Choi et al 2024 (Smaller than We Thought?) | in | 6 | yes | yes | yes | yes |
| defaults-savings | Beshears et al 2023 (12% Default Contribution Rate) | in | 15 | **no** | yes | yes | yes |
| defaults-savings | Berk et al 2024 (Employer-Based Short-Term Savings) | in | 12 | yes | yes | yes | yes |
| defaults-savings | Madrian & Shea 2000 (The Power of Suggestion) | in | 30 | **no** | **no** | **no** | yes |
| defaults-savings | Choi et al 2001 (For Better or For Worse) | out | 4 | **no** | yes | yes | yes |
| defaults-savings | Chetty et al 2014 (Active vs. Passive Decisions) | out | 1 | yes | yes | yes | yes |
| llm-lit-search | PaSa | in | 2 | yes | yes | yes | yes |
| llm-lit-search | OpenScholar | in | 38 | **no** | **no** | **no** | yes |
| llm-lit-search | LitSearch | in | 39 | **no** | **no** | **no** | yes |
| llm-lit-search | LitLLM | — | 136 (cut at 40) | no | no | no | no |

Maximum attainable recall@10 per cell — a cell cannot emit what the reranker never saw:

| topic | R15 | R20 | R25 | R40 | G2 baseline |
|---|---|---|---|---|---|
| defaults-savings | 4/10 | 6/10 | 6/10 | 7/10 | 5/10 |
| llm-lit-search | 1/6 | 1/6 | 1/6 | 3/6 | 3/6 |

G1 (frontier sufficiency) is therefore **unsatisfiable at k in {15, 20, 25} on both topics**, and
G2 is unreachable at R15 on topic 1 and at R15/R20/R25 on topic 2 *before a single call is made*.
The minimal G1-satisfying depth is k=36 on topic 1 and k=39 on topic 2; **R40** is the smallest
round arm that satisfies G1 on both, and it is also the shipped in-window cap.
