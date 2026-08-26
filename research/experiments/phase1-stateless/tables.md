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
