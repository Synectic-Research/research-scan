# Phase-1.1 — golden-topic validation of the stateless architecture

Two live end-to-end scans of the ratified golden topics through the Phase-1 stateless driver, with
**nothing changed to fix anything**. Both runs are complete: plan → retrieve → screen → expand →
screen → coverage → gap round → screen → expand → screen → coverage → shortlist → stratified
rerank → verify → emit, followed by a five-point rerank-depth sweep on each topic's fixed
shortlist and an independent Fable-5 judge over all ten emitted lists.

Nothing under `src/`, `skills/`, `eval/` or `pyproject.toml` was touched. `git status` is clean;
every artefact lives under the gitignored `research/experiments/phase11-golden/`. Total API spend
**$9.57** of the $20 cap.

**Headline: the golden set does not ratify the stateless screen's strictness — but it does not
convict it either. Screening is where almost nothing is lost. Of the 13 golden papers the two runs
failed to emit, 1 was lost at screening, 4 were never retrieved, and 8 were lost downstream at the
shortlist cap, the rerank cut, or the reranker's own ordering.** G1 passes at its bar; G2, G3 and
G4 fail. Per the slice's third stop condition — losses at shortlist/rerank stages — this report
proposes nothing.

---

## 1. Frozen-configuration record

Screening carries Phase-1 arm C verbatim; rerank carries R15's mechanics generalised over k.

| knob | value | source |
|---|---|---|
| model, every screening / planning / rerank call | `claude-sonnet-5` | Phase-1 arm C / R15 |
| effort | `high` (`output_config.effort`) | Phase 1 |
| thinking — screening | **off** (`{"type": "disabled"}`) | arm C |
| thinking — planning, gap queries, rerank | **on** (`{"type": "adaptive"}`) | R15 / plan step |
| batch size | 25 | `retrieve.BATCH_SIZE`, the CLI's own |
| max_concurrency (screening) | 8 | arm C |
| retry policy | 3 attempts, backoff 2ⁿ | arm C |
| max_tokens | 24 000 screening · 48 000 rerank | Phase 1 |
| rerank chunk | 13 records | Phase 1 |
| prompt cache | one ephemeral breakpoint on the stable `system` prefix; first call warms it | arm C |
| output format | structured outputs (`json_schema`), then re-validated against `research-scan schema` | Phase 1 |
| stratified cut | `n_in = round(k · 40/52)`, `n_out = k − n_in`, each capped by availability | Phase 1's ratio rule, generalised; no new weights |
| judge | `claude-fable-5`, effort high, thinking implicit, `eval/judge-prompt.md`, packet projection from `eval/judge.sh` | Phase 1 |
| profile / top / foundational / contradicting | `standard` / 10 / 2 / 1 (defaults) | — |

### Per-topic run record

| | topic 1 `defaults-savings` | topic 2 `llm-lit-search` |
|---|---|---|
| run dir | `runs/p11-t1` | `runs/p11-t2` |
| brief (anchor-free) | `research/scans/2026-08-19-p-standard-t1/brief.md` | `eval/briefs/llm-lit-search.md` |
| profile · domain · window | standard · behavioral · from 2023-08 | standard · cs · from 2024-01 |
| purpose inferred by the planning call | `build` | `research` |
| **per-source hits / failures** | openalex 320 / **0**, s2 247 / **0** | openalex 320 / **0**, s2 280 / **0**, arxiv 272 / **0** |
| pool screened | 905 | 1009 |
| out-of-window in pool | 19 | 16 |
| screened ≥2 | 78 | 200 |
| shortlist (in + out) | 40 + 6 | 40 + **0** |
| gap round | fired on the relative rule (C6, 4 vs median 12); 4 queries | fired on both rules (C5, 6 papers, median 58); 4 queries |

Both topics are **quotable**: every routed source reports `failed: 0`. Topic 2's first retrieval
did not — s2 returned HTTP 429 on `Q7` (`failed: 1`) — so per `docs/measurements.md`'s
measurement-hygiene rule that run was quarantined under `quarantine/p11-t2-retrieval-429/` and
retrieval was re-run against the same query plan with a warm cache. Nothing else was re-run.

---

## 2. Per-topic golden fate

`shortlist pos` is the position in the cut order (`in_window` list, then `outside_window`).
`in cut` / `in top-10` are shown for the frozen R15 arm; the full per-arm matrix is in §4.

### topic 1 — `defaults-savings` (10 golden papers)

| golden paper | retrieved | screen | ≥2 | shortlist pos | in R15 cut | in R15 top-10 | lost at |
|---|---|---|---|---|---|---|---|
| `10.3386/w32828` Smaller than We Thought? | yes | 3 | yes | 2 (in) | yes | **yes** | — |
| `10.1257/aer.20210881` Default Options and Retirement Saving Dynamics | yes | 3 | yes | 5 (in) | yes | **yes** | — |
| `10.3386/w32074` Employer-Based Short-Term Savings Accounts | yes | 3 | yes | 12 (in) | yes | **yes** | — |
| `10.1093/qje/qju013` Chetty et al 2014 | yes | 3 | yes | 41 (out #1) | yes | no | rerank / emit ordering |
| `10.3386/w31601` Beshears et al 2023, 12% default | yes | 2 | yes | 15 (in) | no | no | R15 cut |
| `10.3386/w7682` Madrian & Shea | yes | 2 | yes | 16 (in) | no | no | R15 cut |
| `10.3386/w8651` Choi et al 2001 | yes | 2 | yes | 46 (out #6) | no | no | R15 cut |
| `10.1086/380085` Save More Tomorrow | yes | **1** | **no** | — | no | no | **screening** |
| `10.1017/bpp.2018.43` defaults meta-analysis | **no** | — | — | — | — | — | retrieval |
| `10.1162/qjec.2009.124.4.1639` Carroll et al 2009 | **no** | — | — | — | — | — | retrieval |

### topic 2 — `llm-lit-search` (6 golden papers)

| golden paper | retrieved | screen | ≥2 | shortlist pos | in R15 cut | in R15 top-10 | lost at |
|---|---|---|---|---|---|---|---|
| `10.48550/arXiv.2501.10120` PaSa | yes | 3 | yes | 20 (in) | no | no | R15 cut (in top-10 from R20 on) |
| `10.48550/arXiv.2407.18940` LitSearch | yes | 3 | yes | — (rank 54 of 200) | no | no | **shortlist cap** |
| `10.48550/arXiv.2411.14199` OpenScholar | yes | 3 | yes | — (rank 52 of 200) | no | no | **shortlist cap** |
| `10.48550/arXiv.2402.01788` LitLLM | yes | 2 | yes | — (rank 188 of 200) | no | no | **shortlist cap** |
| `10.48550/arXiv.2605.29234` RollingEval | **no** | — | — | — | — | — | retrieval |
| `10.48550/arXiv.2606.20235` ScholarQuest | **no** | — | — | — | — | — | retrieval |

### Stage-loss summary, pooled over 16 golden papers

| arm | emitted | rerank / emit ordering | cut at k | shortlist cap | screening (<2) | not retrieved |
|---|---|---|---|---|---|---|
| R10 | 3 | 0 | 5 | 3 | 1 | 4 |
| **R15** | **3** | **1** | **4** | **3** | **1** | **4** |
| R20 | 3 | 3 | 2 | 3 | 1 | 4 |
| R25 | 2 | 6 | 0 | 3 | 1 | 4 |
| Rall | 2 | 6 | 0 | 3 | 1 | 4 |

Read the bottom two rows first. At `Rall` **nothing is cut at all** — the whole shortlist is
reranked — and the emitted count *falls* to 2. Depth is not the binding constraint. Six golden
papers reach the reranker and are then not selected.

### The one screening miss, in full

`10.1086/380085` Save More Tomorrow, scored **1**, reason as written:

> *"Save More Tomorrow employer savings program, not consumer self-directed nor default enrolment
> comparison."*

The same screener gave `10.3386/w7682` (also an employer 401(k) study) a **2**, reasoning
*"Classic 401k auto-enrollment default effect; employer setting but foundational C1 evidence."* So
this is not a blanket employer penalty. It is the brief's own setting constraint — "Consumer
financial product, not an employer-sponsored plan" — applied literally to a paper that is an
*escalation* design rather than a default-enrolment comparison. That is defensible reasoning; the
golden set disagrees with it.

### Stateless vs the recorded conversational scores, on the same golden papers

`eval --stage candidates` on the recorded `standard` runs carries their conversational screen
scores. Every golden paper those runs retrieved scored **3**. Ours:

| golden paper | conversational | stateless |
|---|---|---|
| `10.1257/aer.20210881` | 3 | 3 |
| `10.3386/w32828` | 3 | 3 |
| `10.3386/w32074` | 3 | 3 |
| `10.1093/qje/qju013` | 3 | 3 |
| `10.3386/w31601` | 3 | **2** |
| `10.3386/w7682` | 3 | **2** |
| `10.1086/380085` | 3 | **1** |
| `10.48550/arXiv.2501.10120` PaSa | 3 | 3 |
| `10.48550/arXiv.2407.18940` LitSearch | 3 | 3 |
| `10.48550/arXiv.2411.14199` OpenScholar | 3 | 3 |
| `10.48550/arXiv.2402.01788` LitLLM | not retrieved | **2** |
| `10.3386/w8651` Choi 2001 | not retrieved | **2** |

Phase 1's "strictly more conservative" finding reproduces on the golden set: four golden papers
land a notch below the conversational score, none above. It costs one paper the ≥2 threshold — and
it costs three more their place in the shortlist ordering, because `shortlist.order_key` is
`(score, origin_count, publication_date)` and a 2 sorts behind every 3.

---

## 3. Gates

### G1 — screening retention, conditional on retrieval: **PASS, exactly at the bar**

| | value |
|---|---|
| golden papers retrieved (pooled) | **12** of 16 |
| of those, scored ≥2 | **11** |
| bar (retrieved − 1, since fewer than 16 were retrieved) | 11 |
| conditional retention | **11/12 — PASS** |
| raw, unconditional | **11/16** |
| itemised miss | `10.1086/380085` Save More Tomorrow, score **1** (topic 1) |

The bar is met with nothing to spare, and it is a bar that moved down with retrieval: had all 16
been retrieved the requirement would have been 15/16.

### G2 — final emit: **FAIL on both topics**

The slice prompt quotes "≥8/10 and ≥5/6" as the recall@10 baseline. **Re-verified against the
repo, those are not recall@10 numbers.** They are *candidates* recall at the `standard` profile
(`docs/measurements.md`, v0.2.2 corrected profile table). The recorded recall@10 values are in the
V1 acceptance table and in `eval/results/`, and neither acceptance run was at `standard`
(topic 1's was `quick`-depth, topic 2's was `deep`). Both readings are reported.

| topic | our recall@10 (R15) | recorded recall@10 | verdict | our recall@25 | recorded recall@25 |
|---|---|---|---|---|---|
| `defaults-savings` | **3/10** | 5/10 (`2026-08-19-s3-e2e`, quick-depth) | **FAIL** | 4/10 | 8/10 |
| `llm-lit-search` | **0/6** | 3/6 (`2026-08-19-topic2b`, deep) | **FAIL** | 0/6 | 4/6 |

Against the number the prompt actually quoted — candidates recall at `standard` — the picture is
different and worth recording, because it separates retrieval from everything after it:

| topic | our candidates recall | recorded candidates recall at `standard` | verdict |
|---|---|---|---|
| `defaults-savings` | 8/10 | 8/10 | **matched** (a different 8: we gain Choi 2001, lose the meta-analysis) |
| `llm-lit-search` | 4/6 | 5/6 | **−1** (we gain LitLLM, lose RollingEval and ScholarQuest) |

Best arm on each topic is still short: topic 1 peaks at 3/10 (R10, R15), topic 2 at 1/6 (R20 on).

### G3 — contradiction and foundational recovery: **PASS on topic 1, FAIL on topic 2**

| | topic 1 (baseline `s3-e2e`) | topic 2 (baseline `topic2b`) |
|---|---|---|
| foundational slots filled | **2/2** vs baseline 2 — ok | **0/2** vs baseline 2 — **regression** |
| `selection_reason: contradicting` | 0 vs 0 — ok | 0 vs 0 — ok |
| emitted `relation: contradicting` | **4** vs 0 — ahead | **3** vs 2 — ahead |
| `selection_reason: review` | 0 vs 1 — down | 0 vs 1 — down |
| verdict | **pass** | **fail** |

Topic 2's foundational slots cannot be filled at any rerank depth: the pool holds 16 out-of-window
candidates and the stateless screener scored **all 16 at 0 or 1**, so `shortlist.outside_window` is
empty and `emit` backfills both slots with in-window papers. Counter-evidence is not the problem —
both topics emit *more* `relation: contradicting` papers than their baselines. The review slot goes
unfilled on both topics, in every arm except topic 2's `Rall`.

### G4 — schema failures and retry rate: **FAIL on both clauses**

| | value |
|---|---|
| API calls (all) | 125 |
| pipeline calls (excl. judge) | 115 over 107 logical units |
| schema-driven retries | **7** |
| retry rate | **6.5%** of logical units · 6.1% of attempts — **over the 3% bar** |
| unrecovered schema failures under the frozen 3-attempt policy | **1** — `screen/llm-lit-search/x02` |
| `verify` / `emit` non-zero exits | 0 / 0 across all ten arms |
| `ranked.json` / `screen.json` / `queries.json` schema validation | valid, every file, every arm |

One repeat attempt is excluded from the retry rate and named here because it is an operator
artefact rather than a model or API failure: the shell running topic 1's sweep was killed at a
10-minute timeout part-way through `R25/c1`, and that arm was re-run from the start. Its orphaned
call is in the ledger.

**The one hard failure, in detail.** Topic 2's expansion batch `x02` (25 items) failed the
`ScreenScore` contract on **six consecutive identical stateless calls** — the frozen 3 attempts,
then 3 more from a re-invocation. Every time the model returned all 25 wanted cids correctly scored
*plus* one or two extra rows carrying a mangled 13-character variant of a real cid
(`2ad9d99f0b79b`, `2ad9d99f0b79dup`, `2ad9d99f0b79-dup`, `4a1808a68e2a2`). On the seventh call the
extras came with their own reason line: **`"reason": "duplicate placeholder"`**. The
structured-output decoder is padding the array and labelling the padding. The judgement was never
wrong; the wire shape was.

To let the topic finish, `salvage.py` re-issued the identical frozen call, dropped rows whose cid
is not in the batch, and validated the remainder against the same unrelaxed contract (a missing
cid, a duplicate of a real cid, or a bad score would still have failed). What was dropped is
recorded in `stages/salvage-llm-lit-search-x02.json`. The underlying failure is still counted
against G4.

---

## 4. Rerank-depth sweep, and k\*

Same fixed shortlist per topic; screening was not regenerated. Every arm is stratified by the
40:12 ratio, so the out-of-window rows `emit` needs survive every depth (topic 2 has none to
carry). "criterion coverage" = sub-criteria for which at least one emitted packet scored ≥2 on
that criterion in `ranked.json`. Judge is `claude-fable-5` over each arm's own top-10.

| topic | arm | reranked (in+out) | recall@10 | recall@25 | foundational | contradicting (reason / relation) | review | criterion coverage | frontier tok | tok / accepted item | cost | wall s | judged precision | judged mean |
|---|---|---|---|---|---|---|---|---|---|---|---|---|---|---|
| defaults-savings | R10 | 10 (8+2) | **3/10** | 3/10 | 2/2 | 0 / 4 | 0 | 6/6 | 18 137 | 1 813 | $0.1567 | 124 | 0.875 | 2.50 |
| defaults-savings | **R15** | 15 (12+3) | **3/10** | 4/10 | 2/2 | 0 / 4 | 0 | 6/6 | 28 775 | 2 877 | $0.2453 | 219 | **1.00** | **2.625** |
| defaults-savings | R20 | 20 (15+5) | 2/10 | 5/10 | 2/2 | 0 / 3 | 0 | 5/6 | 33 458 | 3 345 | $0.2568 | 246 | 1.00 | 2.625 |
| defaults-savings | R25 | 25 (19+6) | 1/10 | **7/10** | 2/2 | 0 / 2 | 0 | 6/6 | 36 098 | 3 609 | $0.2656 | 245 | 1.00 | 2.50 |
| defaults-savings | Rall | 46 (40+6) | 1/10 | 6/10 | 2/2 | 0 / 3 | 0 | 5/6 | 86 033 | 8 603 | $0.6733 | 617 | 0.875 | 2.50 |
| llm-lit-search | R10 | 10 (10+0) | 0/6 | 0/6 | 0/2 | 0 / 3 | 0 | 5/5 | 27 949 | 2 794 | $0.2353 | 193 | 0.90 | 2.30 |
| llm-lit-search | **R15** | 15 (15+0) | 0/6 | 0/6 | 0/2 | 0 / 3 | 0 | 5/5 | 38 087 | 3 808 | $0.3094 | 246 | **1.00** | 2.60 |
| llm-lit-search | R20 | 20 (20+0) | **1/6** | 1/6 | 0/2 | 0 / 4 | 0 | 5/5 | 59 462 | 5 946 | $0.4793 | 416 | 0.90 | 2.60 |
| llm-lit-search | R25 | 25 (25+0) | **1/6** | 1/6 | 0/2 | 0 / 2 | 0 | 5/5 | 69 854 | 6 985 | $0.5545 | 499 | 0.90 | 2.60 |
| llm-lit-search | Rall | 40 (40+0) | **1/6** | 1/6 | 0/2 | 0 / 2 | 1 | 5/5 | 105 379 | 10 537 | $0.8230 | 744 | 1.00 | 2.50 |

**k\* = 15, and the determination is weaker than the number looks.** No depth is best on both
topics: topic 1's recall@10 *falls* monotonically with depth (3 → 3 → 2 → 1 → 1) while topic 2's
*rises* (0 → 0 → 1 → 1 → 1). Pooled recall@10 is 3/16 at R10, R15 and R20 and 2/16 beyond. R15 is
the minimum depth that is non-inferior on every measured axis simultaneously — top-equal pooled
recall, **1.00** judged in-window precision on *both* topics (the only depth that manages this),
full criterion coverage on both, both foundational slots on topic 1 — at 2 877 / 3 808 tokens per
accepted item against `Rall`'s 8 603 / 10 537 and a third of the cost. R10 ties on recall and loses
on judged precision (0.875 / 0.90); R20 and beyond buy topic 2 one paper and cost topic 1 one to
two.

**The judge does not see the recall collapse.** Judged in-window precision is 0.875–1.00 in every
arm on both topics, and mean relevance 2.30–2.625 — comparable to the recorded acceptance runs'
0.875. An independent stronger model reads all ten of these lists as good. The golden set says two
of them contain three of ten expected papers and eight contain fewer. Both statements are true:
the lists are full of relevant papers that are not the ones the golden set names.

---

## 5. Escalation calibration data

Diagnostic only. Nothing in this slice is built on it.

### P(golden | screen score), pooled over both topics

| score | pool | golden | P(golden \| score) |
|---|---|---|---|
| 0 | 1283 | 0 | 0.00000 |
| 1 | 353 | 1 | 0.00283 |
| 2 | 208 | 4 | 0.01923 |
| 3 | 70 | 7 | **0.10000** |
| **all** | **1914** | **12** | **0.00627** |

Monotone, and steeply so: a 3 is ~35× more likely to be a golden paper than a 1, and no golden
paper anywhere in either pool was scored 0. The 12 in the numerator are the golden papers that were
retrieved; the 4 that were not retrieved are outside this table by construction.

### Pool score distribution

| topic | 0 | 1 | 2 | 3 | ≥2 | pool |
|---|---|---|---|---|---|---|
| `defaults-savings` | 680 | 147 | 62 | 16 | 78 (8.6%) | 905 |
| `llm-lit-search` | 603 | 206 | 146 | 54 | 200 (19.8%) | 1009 |
| pooled | 1283 | 353 | 208 | 70 | 278 (14.5%) | 1914 |

The two topics calibrate very differently under the same absolute rubric — 8.6% vs 19.8% at ≥2,
and 1.8% vs 5.4% at 3. Topic 2's 200-strong ≥2 set against a 40-row in-window shortlist cap is the
mechanism behind its three shortlist-cap losses, and it is a pool-size effect the fixed cap does
not track.

---

## 6. Cost and wall clock

Baseline is Phase 1's decomposition of `2026-08-26-claim-grounding-sonnet`: screening share
$3.003 / 979 s, whole scan $6.448 / 1689 s, over a 572-candidate pool. **Our pools are 1.6–1.8×
that**, so absolute and per-candidate ratios are both reported; the per-candidate column is the
like-for-like one. These are measurements, not gates.

| stage | t1 calls | t1 cost | t1 wall s | t2 calls | t2 cost | t2 wall s |
|---|---|---|---|---|---|---|
| plan — 1 stateless call, thinking on | 1 | $0.0262 | 14.1 | 1 | $0.0464 | 31.5 |
| gap queries — 1 stateless call, thinking on | 1 | $0.0298 | 11.5 | 1 | $0.0327 | 12.5 |
| screening, all four batch families (every attempt) | 39 | $1.1756 | 194.6 | 49 | $1.5133 | 305.7 |
| rerank R15 | 2 | $0.2453 | 219.3 | 2 | $0.3094 | 246.1 |
| CLI stages (retrieve, expand ×2, coverage, shortlist) | — | ~$0.008 | 278 | — | ~$0.008 | 214\* |
| **scan total** | 43 | **$1.4769** | **717.6** | 53 | **$1.9018** | **809.9** |

| measure | target | t1 absolute | t1 per candidate | t2 absolute | t2 per candidate |
|---|---|---|---|---|---|
| screening cost vs baseline screening share | ≤30% | 39.1% | **24.7%** | 50.4% | **28.6%** |
| screening wall vs baseline screening wall | ≤10% | 19.9% | **12.6%** | 31.2% | **17.7%** |
| full scan cost vs baseline whole scan | ≤25% | **22.9%** | 14.5% | 29.5% | **16.7%** |
| full scan wall vs baseline whole scan | — | 42.5% | 26.9% | 47.9% | 27.2% |

\* Topic 2's `retrieve` reads 11 s because it is the cached re-run after the 429 quarantine; the
first, uncached pass took 90 s. Its scan-total wall is understated by roughly that much.

Per candidate, screening cost meets the 30% target on both topics and full-scan cost meets 25% on
both. The **screening-wall target of 10% is missed** (12.6% / 17.7% per candidate): the per-pass
throughput is unchanged from Phase 1 — topic 1's 450-candidate first pass took 72.7 s against arm
C's 72.6 s for 572 — but a real scan runs *four* screening passes, each a separate serialised
fan-out, and the gap round doubles the pool. Concurrency within a pass is not the whole latency
story once the pipeline has four of them.

The judge is not part of a scan and is excluded above: 10 lists, $2.53, 41 s each.

---

## 7. Proposed calibration deck — **not produced**

Two stop conditions are live. G2 fails and there is a golden paper missed at score 1, which points
at the calibration-deck condition. But the third condition — "losses at shortlist/R15/rerank
stages" — is also live, and on the evidence it dominates by a wide margin:

- 1 of 16 golden papers lost at screening.
- 8 of 16 lost after screening: 3 at the shortlist cap, 4 at the R15 cut, 1 at the reranker's
  ordering. At `Rall`, where nothing is cut, 6 are lost at ordering alone.
- 4 of 16 never retrieved.

A calibration deck addresses the smallest of those three buckets. Building one now would be
optimising the stage that is working. Per the slice's instruction for that condition: the
stage-loss table is in §2, the analysis is below, and **nothing is proposed**.

### Where the losses actually are

**Topic 2, the shortlist cap.** 200 candidates scored ≥2, all in-window; `DEFAULT_MAX_IN_WINDOW`
is 40. `shortlist.order_key` is `(score, origin_count, publication_date)`, so within a 54-strong
score-3 tier the tie-break is recency. The last row admitted is a 1-origin paper dated 2025-10-15.
OpenScholar (score 3, 1 origin, 2024-11-21) lands at rank **52**; LitSearch (3, 1 origin,
2024-07-10) at **54**; LitLLM (score 2) at **188**. All three are cut by a rule that is, on this
pool, a recency filter — on a topic whose window opens in 2024 and whose golden set is 2024–2026.
PaSa survives at rank 20 only because it has two origins.

**Both topics, the reranker's ordering.** Deeper reranking converts cut-losses into ordering-losses
one for one, and does not convert them into emissions. On topic 1, `10.1257/aer.20210881` is
emitted at R10 and R15 and drops out at R20, R25 and Rall; `10.3386/w32074` is emitted only at R15;
`10.1093/qje/qju013` only at R10. Each time the frontier widens, non-golden papers the reranker
prefers displace golden ones. `Rall` reranks all 46 / 40 shortlisted records and emits 2 of 16.

**Both topics, retrieval.** Four golden papers never entered a pool. Neither `10.1017/bpp.2018.43`
nor `10.1162/qjec.2009.124.4.1639` is present under any identifier or near-title on topic 1 (best
title ratios 48.9 and 70.0), and neither RollingEval nor ScholarQuest is present on topic 2. This
is the query-plan variance the golden file already documents; a fresh plan finds a different eight.

---

## 8. Deviations, surprises, recommendation

### Deviations

- **Topic 2's retrieval was run twice.** The first run recorded `s2 failed: 1` (HTTP 429 on Q7).
  Quarantined under `quarantine/p11-t2-retrieval-429/`; re-run against the same plan, warm cache,
  clean manifest. Reason: `docs/measurements.md`'s rule that a run is not quotable until every
  routed source reports `failed: 0`.
- **Batch `llm-lit-search/x02` was salvaged after six failed attempts** (§3, G4). The frozen
  3-attempt policy was exhausted, re-invoked once more, and exhausted again; the salvage dropped
  only rows whose cid was not in the batch and re-validated the rest unrelaxed. Without it the
  topic could not reach `shortlist`.
- **`--from` was taken from each golden topic's `window`, not from `init`'s 36-month default.** The
  recorded `standard` profile run for topic 2 used the default 2023-08 at `init` and 2024-01 in its
  `queries.json`; ours is 2024-01 at both. Same effective window.
- **G2's baseline had to be re-derived.** The prompt's "8/10 and 5/6" are candidates recall at
  `standard`, not recall@10. Both readings reported (§3).
- **The gap round's queries were written with thinking on**, like planning. The frozen "thinking
  off" applies to screening; a gap query is a planning judgement. Its cost is reported separately
  ($0.030 / $0.033).
- **The two golden briefs carry no `Purpose:` line**, so the judge prompt's own fallback rule
  applies and it scored both topics as `build` — while the planning call inferred `research` for
  topic 2 and the whole pipeline ranked under that purpose. `eval/judge.sh` passes `brief.md`
  verbatim and injects nothing, so this is the shipped behaviour; it was not corrected here.
  It means topic 2's judged precision is measured against a purpose the run did not use.
- One orphaned API call (`rerank/defaults-savings/R25/c1`, $0.2255) from a shell killed at a
  10-minute timeout is in the ledger and excluded from the retry rate.

### Surprises

**Deeper reranking makes topic 1 worse.** recall@10 falls 3 → 3 → 2 → 1 → 1 as k goes 10 → 46,
while recall@25 rises 3 → 7. The reranker is not failing to *see* the golden papers at depth; it is
seeing them and ranking other papers above them. This is the single most consequential result here,
and it says the frontier-size lever is not the one that moves final quality.

**The judge and the golden set disagree completely, and neither is obviously wrong.** Ten lists,
judged in-window precision 0.875–1.00, mean relevance up to 2.625 — against golden recall@10 of
0/6 to 3/10. Phase 1 saw a milder version of this ("top-10 overlap is a bad quality proxy"); at
golden-set scale it is total. A gate resting on either metric alone would reach the opposite
conclusion from a gate resting on the other.

**Topic 2 cannot fill a foundational slot at any depth.** Sixteen out-of-window candidates in a
1009-paper pool, every one scored 0 or 1. `emit` backfills. The foundational reservation assumes
the citation graph delivers pre-window canon worth ≥2; on a two-year-old CS literature it does not.

**Madrian & Shea sits in the in-window shortlist.** `4d7c9fdb0fab`, DOI `10.1162/003355301753265543`,
`publication_date` 2001-11-01, six merged `openalex:references` origins — and
`outside_window: false`. The tag and the date disagree on a merged record, so a 2001 classic
competes for an in-window slot rather than an out-of-window one. Recorded as an observation for the
maintainer, not diagnosed and not touched.

**The structured-output decoder pads arrays and says so.** `x02`'s spurious rows arrived carrying
`"reason": "duplicate placeholder"`. Six identical calls produced the same defect with three
different mangled cids. This is a reproducible failure mode of schema-constrained decoding on a
25-item batch, not a transient.

**Screening throughput is unchanged; screening wall is not.** 450 candidates in 72.7 s matches
Phase 1's 572 in 72.6 s. But a real scan screens four families across two rounds, and the gap
round doubled both pools — so the 10% wall target is missed at 12.6% / 17.7% per candidate despite
identical per-pass speed.

### Recommendation

**Investigate the shortlist cap and the rerank ordering — in that order — before any further work
on screening calibration:** screening loses 1 of 16 golden papers while the shortlist cap and the
reranker's own ordering together lose 8, and at `Rall`, where nothing is cut at all, six golden
papers are reranked and then not selected.
