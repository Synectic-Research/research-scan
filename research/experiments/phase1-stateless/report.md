# Phase-1 stateless-screening replay — report

Replay of `research/scans/2026-08-26-claim-grounding-sonnet` (the $6.45 / 28-min / 60-turn
Sonnet-5 forked-skill run) through stateless API calls. No pipeline change: nothing under
`src/`, `skills/` or `pyproject.toml` was touched, and the saved run directory was read and
never written. `git status` is clean; everything new lives under the gitignored
`research/experiments/phase1-stateless/`.

Model for every screening and rerank call: `claude-sonnet-5` at `effort: high` — the model the
session json records (`modelUsage`) and the effort every one of the baseline's 59 assistant
turns ran at (`effort` field in the transcript). No substitution was needed.

## 1. Files created

```
research/experiments/phase1-stateless/
├── lib/common.py            pricing, spend ledger + $12 cap, prompt assembly, ScreenScore
│                            validation, `research-scan schema` shape checks
├── arm_a.py                 ARM A — baseline bookkeeping and stage cost attribution
├── screen_arms.py           ARMS B / C / D — stateless screening replay
├── rerank_arms.py           RERANK-CUT R52 / R25 / R15
├── judge.py                 independent judge (Fable 5) over the top-10 lists
├── analyze.py               measurements, recovery curves, gate verdict
├── measurements.json        every number in this report, machine-readable
├── tables.md                rendered tables (sections 2-4 below)
├── spend.json               per-call ledger, $5.09 total
├── .venv/                   anthropic 1.0.0 + jsonschema (pyproject.toml untouched)
└── arms/
    ├── A/baseline.json          scores, ≥2 set, shortlist ids, top-10 DOIs, stage attribution
    ├── {B,C,D}/                 batches/*.json, screen.json, calls.json, summary.json, run/
    ├── D/priority-order.json    the deterministic screening order
    ├── rerank/{R52,R25,R15}/    run/ (full pipeline copy), calls.json, summary.json
    └── judge/                   baseline.json, R52.json, R25.json, R15.json, summary.json
```

### How the baseline's screening+rerank share was estimated

The whole-scan $6.45 / 28 min covers plan, retrieval, expansion, verification and reporting too,
so the gate needs like-for-like. Two independent decompositions, both reported:

- **Stage clock** — `manifest.json` timestamps bracket every CLI stage exactly. The gaps between
  one CLI stage finishing and the next starting *are* the agent's screening and rerank work.
- **Turn cost** — each assistant turn in the session transcript is billed at the verified Sonnet-5
  rates and attributed to the stage window its timestamp falls in. One API request appears as up
  to three transcript rows carrying the same usage block, so rows are deduped by `requestId`;
  doing so reproduces the session json's totals exactly (output 146,359 · cache-read 13,340,895 ·
  thinking 77,635), which is what makes the split trustworthy. Attributed turns sum to $6.371 of
  the billed $6.448 (98.8%); the 1.2% residual is turns outside every stage window.

The four Sonnet-5 rates used throughout ($2.00 / $10.00 / $2.50 / $0.20 per MTok for
input / output / cache-write / cache-read) reproduce the session's `total_cost_usd` of
$6.4480633 to the cent from its own token counts, so pricing is not an assumption here.

| baseline stage | wall | cost | turns |
|---|---|---|---|
| plan | 62 s | $0.179 | 5 |
| retrieve (CLI) | 39 s | $0 | 0 |
| **screen round 1** | **767 s** | **$2.063** | 23 |
| expand (CLI) | 76 s | $0 | 0 |
| **screen expansion** | **212 s** | **$0.940** | 9 |
| coverage + shortlist (CLI) | 10 s | $0.077 | 1 |
| **rerank** | **449 s** | **$2.417** | 8 |
| verify (CLI) | 63 s | $0 | 0 |
| emit + report | 11 s | $0.112 | 1 |

**Screening share: $3.003 / 979 s. Rerank share: $2.417 / 449 s. Together $5.420 — 84% of the
whole-scan cost.** The ≤20% gate target is therefore **$0.601** for screening.

## 2. Measurements

| arm | calls | input tok | cache-read tok | output tok | (thinking) | cost USD | stage wall s | exact agr | binary ≥2 | ≥2 Jaccard | shortlist ∩ base | top-10 ∩ base |
|---|---|---|---|---|---|---|---|---|---|---|---|---|
| A (baseline, screening share) | 32 turns | 64 | 7,115,537 | 85,123 | 46,314 | 3.003 | 979.0 | 1.000 | 1.000 | 1.000 | 47/47 | 10/10 |
| B | 24 | 184,512 | 88,251 | 90,419 | 54,732 | 1.3005 | 961 | 0.731 | 0.895 | 0.686 | 29/47 | — |
| C | 24 | 184,512 | 88,251 | 36,053 | 0 | 0.7568 | 73 | 0.603 | 0.830 | 0.481 | 31/47 | — |
| D | 23 | 184,018 | 88,251 | 35,947 | 0 | 0.7452 | 74 | 0.598 | 0.830 | 0.481 | 25/47 | — |
| A (baseline, rerank share) | 8 turns | 16 | 2,729,367 | 48,420 | 24,657 | 2.4174 | 449.0 | — | — | — | — | 10/10 |
| R52 (rerank 42) | 4 | 28,344 | 17,550 | 55,893 | 33,058 | 0.6338 | 552 | — | — | — | — | 5/10 |
| R25 (rerank 25) | 2 | 15,812 | 11,700 | 26,993 | 14,118 | 0.3039 | 262 | — | — | — | — | 5/10 |
| R15 (rerank 15) | 2 | 9,775 | 11,700 | 15,903 | 7,860 | 0.1809 | 204 | — | — | — | — | 5/10 |

Frontier tokens per accepted evidence item (rerank tokens ÷ 10):

| sub-arm | reranked | rerank tokens | tokens / accepted item |
|---|---|---|---|
| R52 | 42 | 101,787 | 10179 |
| R25 | 25 | 54,505 | 5450 |
| R15 | 15 | 37,378 | 3738 |

## 3. Arm D recovery curves

`found` = arm D screened it *and* scored it ≥2. `enc` = it had been reached in the queue at all.

| % screened | items | ≥2 set found | ≥2 set enc | top-10 found | top-10 enc | contradicting found | contradicting enc |
|---|---|---|---|---|---|---|---|
| 10% | 57 | 9.1% | 16.6% | 40.0% | 50.0% | 14.3% | 14.3% |
| 20% | 114 | 14.4% | 25.7% | 60.0% | 70.0% | 42.9% | 42.9% |
| 30% | 172 | 19.8% | 35.3% | 80.0% | 90.0% | 71.4% | 71.4% |
| 40% | 229 | 21.9% | 43.3% | 80.0% | 100.0% | 71.4% | 71.4% |
| 50% | 286 | 24.6% | 48.7% | 80.0% | 100.0% | 100.0% | 100.0% |
| 60% | 343 | 27.8% | 56.7% | 80.0% | 100.0% | 100.0% | 100.0% |
| 70% | 400 | 32.1% | 66.3% | 80.0% | 100.0% | 100.0% | 100.0% |
| 80% | 458 | 37.4% | 78.6% | 80.0% | 100.0% | 100.0% | 100.0% |
| 90% | 515 | 41.7% | 87.2% | 80.0% | 100.0% | 100.0% | 100.0% |
| 100% | 572 | 48.1% | 100.0% | 80.0% | 100.0% | 100.0% | 100.0% |

## 4. Gate

| criterion | threshold | arm | value | verdict |
|---|---|---|---|---|
| screening cost vs baseline screening share | ≤ 20% | C | $0.7568 / $3.0030 = 25.2% | FAIL |
| binary ≥2 agreement | ≥ 95% | C | 83.04% | FAIL |
| exact score agreement | ≥ 80% | C | 60.31% | FAIL |
| screening cost vs baseline screening share | ≤ 20% | D | $0.7452 / $3.0030 = 24.8% | FAIL |
| binary ≥2 agreement | ≥ 95% | D | 83.04% | FAIL |
| exact score agreement | ≥ 80% | D | 59.79% | FAIL |
| rerank top-10 overlap | ≥ 8/10 | R52 | 5/10 | FAIL |
| rerank top-10 overlap | ≥ 8/10 | R25 | 5/10 | FAIL |
| rerank top-10 overlap | ≥ 8/10 | R15 | 5/10 | FAIL |
| — fallback: judged precision vs baseline | within 0.1 | R52 | 1.00 vs 1.00 (Δ 0.00) | PASS |
| — fallback: judged precision vs baseline | within 0.1 | R25 | 1.00 vs 1.00 (Δ 0.00) | PASS |
| — fallback: judged precision vs baseline | within 0.1 | R15 | 1.00 vs 1.00 (Δ 0.00) | PASS |
| **rerank criterion overall** (≥8/10 **or** judged within 0.1) | — | any sub-arm | R52, R25, R15 | PASS |

### Judge detail (claude-fable-5, eval/judge-prompt.md)

| list | in-window packets | precision ≥2 | mean score | foundational scores |
|---|---|---|---|---|
| baseline | 8 | 1.00 | 2.625 | [3, 2] |
| R52 | 8 | 1.00 | 2.625 | [3, 3] |
| R25 | 8 | 1.00 | 2.75 | [3, 2] |
| R15 | 8 | 1.00 | 2.75 | [3, 2] |

### Extrapolated full scan

Replay cannot reproduce retrieval. Plan, the CLI stages and the report turn are carried from the baseline at their measured values ($0.368, 261s); only screening and rerank are replaced.

| configuration | full-scan cost | full-scan wall | screen+rerank vs baseline share |
|---|---|---|---|
| baseline (measured) | $6.45 | 1689s (28.1 min) | 100% |
| C+R52 | $1.76 (27% of baseline) | 886s (14.8 min) | 25.7% |
| C+R25 | $1.43 (22% of baseline) | 596s (9.9 min) | 19.6% |
| C+R15 | $1.31 (20% of baseline) | 537s (9.0 min) | 17.3% |

Total API spend this slice: **$5.09** of the $12 cap.

## 5. Deviations from the prompt

- **`R52` reranked 42 records, not 52.** Arm C's shortlist is 42 (40 in-window + 2 out-of-window);
  R52 is defined as the whole shortlist, which is the parity condition the baseline ran under
  (it reranked all 47 of its own shortlist). Nothing was cut at R52.
- **`R25`/`R15` keep the shortlist's 40:12 in/out-of-window proportion** (19+6 and 12+3) rather
  than taking a flat prefix. A flat prefix would take 25 in-window rows and zero out-of-window
  ones, leaving `emit` unable to fill its 2 foundational slots — that would measure the cut rule,
  not the reranker.
- **One ephemeral cache breakpoint on the stable prefix.** Brief + rubric + purpose + schema are
  byte-identical across all 24 calls, so they sit in `system` behind one `cache_control` marker.
  This changes billing, not content. Arms C/D issue the first call alone to warm it, then fan out.
  Without caching, arm C would cost $0.914 instead of $0.757 (21% higher).
- **Structured outputs instead of free-form JSON.** `output_config.format` guarantees parseable
  output; the shape is still validated afterwards against `research-scan schema --name ScreenFile`.
  The wire schema bounds `score` with `enum: [0,1,2,3]` because the API rejects `minimum`/`maximum`
  on integers ("For 'integer' type, properties maximum, minimum are not supported").
- **All calls stream.** At `max_tokens: 24000` the API refuses non-streaming outright ("Streaming
  is required for operations that may take longer than 10 minutes").
- **Judge run on Fable 5, not via `eval/judge.sh`.** The prompt, packet projection and `JudgeFile`
  schema are `judge.sh`'s; the transport is the same stateless driver so the cost lands in the
  tracked ledger against the $12 cap. `judge.sh` shells out to `claude -p`, which would not.
- **Arm D reranking was not run.** The slice specifies the rerank sub-arms run on arm C's scores;
  arm D's shortlist contains 0 out-of-window rows, so it could not fill the foundational slots.
- **`doctor` exits 0**, with one warning (arXiv unreachable — a retrieval-only source, and this is
  a replay that issues no retrieval). Not exit 3, so `verify` ran; it exited 0 in all three
  sub-arms, as did `emit`.
- **No batch failed schema validation.** 0 failures across 71 screening calls; 2 transient API
  retries in arm B, 0 in C and D. Nothing was hand-patched.

## 6. Surprises

**The stateless screener is strictly more conservative, not noisier.** Arm C's ≥2 set has **zero
false positives and 97 false negatives** against the baseline: it is a strict *subset* — 90 of the
baseline's 187. Arm B (thinking on) is nearly so: 135 ≥2 with 4 false positives, 56 false
negatives. The disagreement is not two models diverging; it is one model applying the same rubric
with a higher bar. The baseline awarded 46 threes in the first 225 candidates where arm B awarded
28. The prompt's hypothesis was that harness cost is pure tax; part of it is calibration — the
in-context agent sees the accumulating `screen.json` and grades on a curve the stateless call
cannot see.

**Low agreement did not cost recall where it matters.** Nine of the baseline's ten emitted papers
survived arm C's screening into the shortlist. Only one (`7c75cad1f848`, WiCE) was lost at
screening. The other four top-10 differences are rerank *ordering* churn among papers that were
all present in the pool — so the 5/10 overlap is mostly a rerank tie-breaking artifact, not a
screening recall failure.

**Top-10 overlap is a bad quality proxy, and the judge says so.** All three sub-arms score 5/10 on
DOI overlap, yet an independent Fable 5 judge gives **1.00 in-window precision to all four lists**,
with R25 and R15 scoring a *higher* mean relevance (2.75) than the baseline (2.625). The judge
scored 3s to papers unique to the stateless lists ("Directly demonstrates a benchmark-construction
artifact", "Large-scale, doctor-validated quantification of unsupported and contradicted
citations") and 2s to several unique to the baseline. Both lists are good; they are different
draws from a pool of near-equivalent 3s. Had the gate rested on overlap alone it would have
rejected an output the judge rates as equal-or-better.

**Cutting the reranker deeper did not degrade the result.** R15 reads 15 records instead of 42,
costs $0.18 instead of $0.63, and produces a list the judge scores *higher*. Frontier tokens per
accepted evidence item fall from 10,179 (R52) to 3,738 (R15).

**Thinking is the whole cost difference in screening, and buys ~7 points of binary agreement.**
Arms B and C send byte-identical input (184,512 tokens). Arm B emits 90,419 output tokens (54,732
thinking) for $1.30; arm C emits 36,053 with none for $0.757. That 72% extra spend buys binary ≥2
agreement of 89.5% against 83.0% — real, but not enough to reach the 95% bar.

**Wall-clock is where stateless wins outright.** Arm C screens all 572 candidates in **72.6 s**
against the baseline's 979 s — 13.5×. Arm B, sequential with thinking, takes 961 s: essentially
the baseline's own wall time, which confirms the baseline's screening latency was serialised model
work, not harness overhead. Concurrency, not statelessness, is the speed lever.

**Arm D's priority order concentrates the *output*, not the ≥2 set.** After 30% of the queue it has
encountered 90% of the baseline's emitted top-10 and 71% of the contradicting papers, but only 35%
of the broad ≥2 set — barely above the 30% a random order would give. The ordering is a good
predictor of what finally gets emitted and a weak predictor of bulk relevance. (Because arm D
screens every candidate, this curve is diagnostic only; nothing was skipped.)

## 7. Recommendation

**Iterate** — the stateless driver is the right transport (13.5× faster screening, 73-80% cheaper end-to-end,
judged output quality equal or better) but must not ship as the documented headless path until the
screening-calibration gap is closed, because the ≥2 set it produces is less than half the
baseline's and the gate's agreement criteria fail on the numbers as measured.
