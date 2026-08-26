## 1. What was run, and what changed before anything was run

Three deterministic recomputations over Phase-1.1 recorded artefacts, made **before any tokens
were spent**, changed the design. Each is a file-level fact, not a judgement.

**F1 — `T1@80` is not a distinct arm at any depth this slice specifies.** A cap is a truncation of
one order, and the frozen `rerank.cut()` takes a *prefix* of `in_window` and a prefix of
`outside_window`. For any depth whose in-window take is ≤ 40, `T1@40` and `T1@80` hand the
reranker the identical rows in the identical order.

| topic | R15 | R20 | R25 | R30 | R40 |
|---|---|---|---|---|---|
| `defaults-savings` — cut (in+out), both policies | 12+3 | 15+5 | 19+6 | 24+6 | 34+6 |
| `llm-lit-search` — cut (in+out), both policies | 15+0 | 20+0 | 25+0 | 30+0 | 40+0 |
| rows byte-identical between `T1@40` and `T1@80` | yes | yes | yes | yes | yes |

The two diverge only at `Rall`, where `T1@80` adds 32 (topic 1) / 40 (topic 2) further rows, none
of them a golden paper. At `Rall`, `T1@80` is a **distractor-load** arm, not a recall-control arm.

**F2 — the residual `T1@40` loss is LitLLM, and `T1@80` does not recover it.** This is 1.2A's open
question, answered by name and offline.

| topic | golden | retrieved | screen | T1 in-window rank (uncapped, of 200) | in `T1@40` | in `T1@80` |
|---|---|---|---|---|---|---|
| `llm-lit-search` | **LitLLM** (`10.48550/arXiv.2402.01788`) | yes | 2 | **136** | no | **no** |

Cap 80 is 56 ranks short of LitLLM. Only an uncapped shortlist reaches it. The recall-control arm
as specified could not have answered the cap question, because the answer was already no.

**F3 — the specified depth ladder re-cuts exactly the papers `T1@40` was chosen to save.** T1@40's
entire value in 1.2A was lifting OpenScholar to in-window rank 38 and LitSearch to 39, inside a cap
of 40. The stratified cut at k = 15/20/25 takes only the first 15/20/25 in-window rows and
discards both again.

Maximum attainable recall@10 — a cell cannot emit a paper the reranker was never shown:

| topic | R15 | R20 | R25 | R40 | G2 baseline |
|---|---|---|---|---|---|
| `defaults-savings` | 4/10 | 6/10 | 6/10 | 7/10 | 5/10 |
| `llm-lit-search` | 1/6 | 1/6 | 1/6 | 3/6 | 3/6 |

**G1 is unsatisfiable at k ∈ {15, 20, 25} on both topics, and G2 is unreachable at R15 on topic 1
and at R15/R20/R25 on topic 2, before a single call is made.** The minimal G1-satisfying depth is
k = 36 on topic 1 and k = 39 on topic 2. **R40** is the smallest round arm satisfying G1 on both,
and it is also the shipped `DEFAULT_MAX_IN_WINDOW`.

**The reallocation.** The 18 runs the slice assigned to `T1@80` would have measured an identical
input distribution twice. They were spent instead on an **R40 arm at `T1@40`** — the only depth in
reach that can satisfy the slice's own first gate. Design as run: 2 topics × {R15, R20, R25, R40}
× 3 replicates = **24 runs**, all at `T1@40`, ordering O1.
