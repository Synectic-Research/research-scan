# Evidence scan — claim-grounding-sonnet

Run `/Users/nabergoj/Projects/research-scan/research/experiments/phase1-stateless/arms/rerank/R25/run` · brief `/Users/nabergoj/Projects/research-scan/research/experiments/phase1-stateless/arms/rerank/R25/run/brief.md` · rendered 2026-08-26

| # | Paper | Year | Venue | Evidence | Verified |
|---|---|---|---|---|---|
| 1 | [Evaluating and Guarding Citation Faithfulness in Agentic Scientific Synthesis](https://doi.org/10.48550/arxiv.2607.20527) · 10.48550/arxiv.2607.20527 | 2026 | arXiv | experimental | yes |
| 2 | [When Verification Fails: How Compositionally Infeasible Claims Escape Rejection](https://doi.org/10.48550/arxiv.2604.10990) · 10.48550/arxiv.2604.10990 | 2026 | arXiv | experimental | yes |
| 3 | [ResearchQA: Benchmarking Citation-Grounded Question-Answering on Scientific Papers](https://doi.org/10.48550/arxiv.2607.11074) · 10.48550/arxiv.2607.11074 | 2026 | arXiv | computational | yes |
| 4 | [Can AI Validate Science? Benchmarking LLMs for Accurate Scientific Claim → Evidence Reasoning](https://doi.org/10.48550/arxiv.2506.08235) · 10.48550/arxiv.2506.08235 | 2025 | arXiv.org | computational | yes |
| 5 | [Evidence Absence Is Not Evidence Insufficiency: Diagnosing NEI Construction Artifacts in Fact Verification](https://doi.org/10.48550/arxiv.2605.26663) · 10.48550/arxiv.2605.26663 | 2026 | arXiv.org | computational | yes |
| 6 | [Generalization bias in large language model summarization of scientific research](https://doi.org/10.1098/rsos.241776) · 10.1098/rsos.241776 | 2025 | Royal Society Open Science | experimental | yes |
| 7 | [SciClaimEval: Cross-modal Claim Verification in Scientific Papers](https://doi.org/10.48550/arxiv.2602.07621) · 10.48550/arxiv.2602.07621 | 2026 | arXiv | computational | yes |
| 8 | [Attribution, Citation, and Quotation: A Survey of Evidence-based Text Generation with Large Language Models](https://doi.org/10.18653/v1/2026.acl-long.1430) · 10.18653/v1/2026.acl-long.1430 | 2025 | Annual Meeting of the Association for Computational Linguistics | other | yes |
| 9 | [Enabling Large Language Models to Generate Text with Citations](https://doi.org/10.18653/v1/2023.emnlp-main.398) · 10.18653/v1/2023.emnlp-main.398 | 2023 | Conference on Empirical Methods in Natural Language Processing | experimental | yes |
| 10 | [Evaluating Verifiability in Generative Search Engines](https://doi.org/10.18653/v1/2023.findings-emnlp.467) · 10.18653/v1/2023.findings-emnlp.467 | 2023 | Conference on Empirical Methods in Natural Language Processing | observational | yes |

## 1. Evaluating and Guarding Citation Faithfulness in Agentic Scientific Synthesis

Taewan Goo, Junsik Kim, Kyulhee Han, G. Jo et al. · 2026 · arXiv · experimental · overall 3/3

<https://doi.org/10.48550/arxiv.2607.20527>

**Key finding.** On identical agent outputs, measured unsupported-citation rates range from ~3% to ~18% depending solely on verifier strictness, and verifiers disagree substantially on which citations to flag (negative-specific agreement only 0.27-0.30), while a gold-anchored protocol plus split-conformal guard bounds the true unsupported-citation rate.

**Why it made the cut.** design-changing · selected by score · strongest on C2 evidence-link errors (3/3). Central to the brief's exact questions: quantifies evidence-link error variability, benchmark/verifier validity, and calibrated abstention trade-offs.

**Why it matters here.** Directly answers the brief's core Q2-Q4: shows evidence-linking error rates are themselves unreliable to measure without a named verifier/protocol, and demonstrates a concrete, bounded abstention mechanism (conformal guard) trading catch-rate guarantees for coverage.

**Method.** Gold-anchored evaluation protocol validating verifiers against human gold labels, re-attribution via deterministic BM25, and a split-conformal distribution-free bound; validated across four open 27-35B models and three agentic pipelines on SciFact, QASA, and PubMedQA.

**Limitations.**

- guard's bound is on catch-rate, not conclusion correctness
- tested on 27-35B open models, not necessarily frontier proprietary models
- calibration-negative difficulty transfer condition requires recalibration recipe to hold

<sub>selected: score · criteria: C1 1/3 · C2 3/3 · C3 3/3 · C4 3/3 · C5 3/3 · flags: contradicts, methods_paper · verified 2026-08-26 via openalex, arxiv</sub>

## 2. When Verification Fails: How Compositionally Infeasible Claims Escape Rejection

Muxin Liu, Delip Rao, Grace Kim, Chris Callison-Burch · 2026 · arXiv · experimental · overall 3/3

<https://doi.org/10.48550/arxiv.2604.10990>

**Key finding.** Models that saturate existing claim-verification benchmarks consistently over-accept compositionally infeasible claims (where a non-salient constraint is contradicted while the salient one is supported), revealing that benchmarks cannot distinguish rigorous verification from salient-constraint shortcut reasoning.

**Why it made the cut.** design-changing · selected by score · strongest on C2 evidence-link errors (3/3). Directly answers the brief's call for benchmarks whose construction inflates reported accuracy and models' verification failure modes.

**Why it matters here.** Directly falsifies the premise that existing grounding benchmarks' high accuracy numbers reflect genuine claim-verification competence—showing they are inflated by shortcut reasoning, exactly the artifact the brief asked us to hunt for.

**Method.** Constructs compositionally infeasible claims contrasting with existing single-element perturbation benchmarks; tests across model families and modalities, analyzes results via ROC-curve framing of verification thresholds.

**Limitations.**

- abstract-only detail on exact dataset size
- focuses on compositional/CWA violations, not all error types (e.g., fabrication)
- newly proposed test, not yet independently replicated

<sub>selected: score · criteria: C1 1/3 · C2 3/3 · C3 3/3 · C4 1/3 · C5 3/3 · flags: contradicts · verified 2026-08-26 via openalex, arxiv</sub>

## 3. ResearchQA: Benchmarking Citation-Grounded Question-Answering on Scientific Papers

Saba Imran, Debanjum Singh Solanky · 2026 · arXiv · computational · overall 3/3

<https://doi.org/10.48550/arxiv.2607.11074>

**Key finding.** ResearchQA (6,211 QA pairs over 494 papers, 8 domains, 4 question types) shows citation-based metrics (section coverage, citation accuracy) separate model quality far more clearly than LLM-evaluator scores, which stay tightly compressed, and open-weight models approach closed-model citation accuracy at 3-6x lower latency.

**Why it made the cut.** design-changing · selected by score · strongest on C3 benchmark construction (3/3). Directly relevant to C3 (benchmark construction) and C4 (grounded refusal/abstention) for citation-grounded evaluation.

**Why it matters here.** Directly tests whether rewarding grounded refusal (abstention) improves trustworthiness, and shows citation-grounded metrics reveal model differences that generic LLM-judge scores obscure — a methodological lesson for how the decision engine should be evaluated.

**Method.** New benchmark with multiple valid supporting passages per claim and a grounded-refusal design, evaluated with a deterministic citation matcher plus LLM rubric evaluator across eight closed- and open-weight models.

**Limitations.**

- single-paper QA setting, not multi-document claim extraction
- LLM-based rubric evaluator itself unaudited for reliability
- abstract does not report coverage cost of grounded refusal quantitatively

<sub>selected: score · criteria: C1 1/3 · C2 2/3 · C3 3/3 · C4 2/3 · C5 2/3 · verified 2026-08-26 via openalex, arxiv</sub>

## 4. Can AI Validate Science? Benchmarking LLMs for Accurate Scientific Claim → Evidence Reasoning

Shashidhar Reddy Javaji, Yupeng Cao, Haohang Li, Yangyang Yu et al. · 2025 · arXiv.org · computational · overall 3/3

<https://doi.org/10.48550/arxiv.2506.08235>

**Key finding.** CLAIM-BENCH, evaluated over 300+ claim-evidence pairs across domains and six LLMs, finds closed-source models (GPT-4, Claude) consistently outperform open-source counterparts in claim-evidence identification precision/recall, and multi-pass prompting strategies improve accuracy at higher computational cost.

**Why it made the cut.** design-changing · selected by score · strongest on C1 extraction accuracy (3/3). Core benchmark measuring exactly what the brief's Q1 and Q2 ask about: claim-evidence extraction and linking accuracy across models.

**Why it matters here.** Directly measures claim-evidence extraction accuracy across models and prompting strategies, providing exactly the cross-model comparison the brief needs to test whether extraction itself is a bottleneck versus evidence linking.

**Method.** New benchmark comparing three divide-and-conquer-inspired prompting strategies (including three-pass and one-by-one) across six diverse LLMs for claim-evidence extraction and validation from full-length papers.

**Limitations.**

- relatively small evaluation set (~300 pairs)
- benchmark construction methodology not deeply detailed in the abstract
- no calibration/abstention analysis

<sub>selected: score · criteria: C1 3/3 · C2 2/3 · C3 2/3 · C4 0/3 · C5 3/3 · verified 2026-08-26 via openalex, arxiv</sub>

## 5. Evidence Absence Is Not Evidence Insufficiency: Diagnosing NEI Construction Artifacts in Fact Verification

Jing Qiu, Zeyu Han, Chen Huang · 2026 · arXiv.org · computational · overall 3/3

<https://doi.org/10.48550/arxiv.2605.26663>

**Key finding.** In SciFact-style verification (with FEVER/HoVer as controls), NEI competence does not transfer across the different ways 'not enough information' examples are constructed; models trained on shortcut-prone constructions fail on semantically related insufficient-evidence cases, and mixed-construction training only narrows, not closes, the gap.

**Why it made the cut.** contradicting · selected by score · strongest on C3 benchmark construction (3/3). Exactly the kind of benchmark-construction-artifact finding the brief asks us to reach for, targeting SciFact directly.

**Why it matters here.** Directly shows a claim-evidence grounding benchmark (SciFact) can hide which problem a model actually solved, meaning reported NEI/abstention accuracy on these benchmarks may not indicate real insufficient-evidence detection ability — a core risk for our abstention design.

**Method.** NEI-CAP diagnostic protocol: tags each NEI example by construction family, audits shortcut cues, runs human adjudication of hard cases, and tests cross-construction transfer on SciFact/FEVER/HoVer.

**Limitations.**

- focused on NEI/insufficient-evidence label rather than full claim extraction pipeline
- SciFact-style setting only, generalisation to full-paper multi-claim extraction untested

<sub>selected: score · criteria: C1 0/3 · C2 2/3 · C3 3/3 · C4 2/3 · C5 3/3 · flags: contradicts, methods_paper · verified 2026-08-26 via openalex, arxiv</sub>

## 6. Generalization bias in large language model summarization of scientific research

Uwe Peters, Benjamin Chin‐Yee · 2025 · Royal Society Open Science · experimental · overall 3/3

<https://doi.org/10.1098/rsos.241776>

**Key finding.** Across 4900 LLM-generated summaries from 10 models (ChatGPT-4o/4.5, DeepSeek, LLaMA 3.3 70B, Claude 3.7 Sonnet, etc.), most LLMs generalise scientific conclusions more broadly than the original text even when explicitly prompted for accuracy, with 26-73% overgeneralization rates for some models, LLM summaries ~5x more likely than human summaries to overgeneralize (OR=4.85), and newer models performing worse than earlier ones.

**Why it made the cut.** contradicting · selected by score · strongest on C2 evidence-link errors (3/3). The strongest evidence in this shortlist that extraction/summarization itself, not just evidence linking, is a major failure mode — exactly the hardest-to-find result the brief asked for.

**Why it matters here.** Directly falsifies the premise that most extraction/summarization errors are confined to evidence linking — overgeneralisation (claim scope distortion) is itself a widespread and, alarmingly, worsening extraction-level failure, which must be built into our trustworthiness scoring even for 'well-extracted' claims.

**Method.** Comparative evaluation of 4900 LLM-generated summaries against original scientific texts and human-authored summaries across 10 prominent LLMs, with statistical comparison (odds ratios).

**Limitations.**

- measures summarization overgeneralisation rather than structured claim-evidence extraction pipelines specifically
- abstract does not report per-section or per-claim-type breakdown
- mechanism behind 'newer models worse' not explained

<sub>selected: score · criteria: C1 2/3 · C2 3/3 · C3 1/3 · C4 1/3 · C5 3/3 · flags: contradicts · verified 2026-08-26 via crossref, openalex</sub>

## 7. SciClaimEval: Cross-modal Claim Verification in Scientific Papers

Xanh Ho, Yun-Ang Wu, Sunisth Kumar, Tian Cheng Xia et al. · 2026 · arXiv · computational · overall 3/3

<https://doi.org/10.48550/arxiv.2602.07621>

**Key finding.** A new cross-modal claim-verification dataset (1,664 samples, 180 papers, 3 domains) built by perturbing actual figures/tables rather than LLM-fabricated claims shows figure-based verification remains far below human performance across 11 multimodal models.

**Why it made the cut.** plan-influencing · selected by score · strongest on C3 benchmark construction (3/3). Directly tackles benchmark-construction artifacts and cross-modal evidence-link reliability, core to the brief's C2/C3 questions.

**Why it matters here.** Directly addresses the benchmark-construction question (C3): shows how avoiding LLM-generated negatives changes what a grounding benchmark can support, and quantifies a large, robust figure-vs-table performance gap relevant to which evidence types a decision engine can trust.

**Method.** Novel refutation-construction method that modifies supporting evidence (not the claim) using authentic figures/tables in multiple formats; benchmarked against 11 open and proprietary multimodal LLMs with expert validation.

**Limitations.**

- small sample per domain (1,664 total)
- 3 domains only
- newly released, unreplicated construction methodology

<sub>selected: score · criteria: C1 1/3 · C2 2/3 · C3 3/3 · C4 0/3 · C5 3/3 · verified 2026-08-26 via openalex, arxiv</sub>

## 8. Attribution, Citation, and Quotation: A Survey of Evidence-based Text Generation with Large Language Models

Tobias Schreieder, Tim Schopf, Michael Farber · 2025 · Annual Meeting of the Association for Computational Linguistics · other · overall 3/3

<https://doi.org/10.18653/v1/2026.acl-long.1430>

**Key finding.** A systematic analysis of 134 papers on evidence-based text generation (citation, attribution, quotation) yields a unified taxonomy and catalogs 300 evaluation metrics across seven dimensions, revealing the field is fragmented by inconsistent terminology and isolated evaluation practices.

**Why it made the cut.** plan-influencing · selected by review · strongest on C3 benchmark construction (3/3). The synthesis paper mapping the benchmark and metric landscape the brief explicitly asks us to characterize.

**Why it matters here.** Gives the field-wide map of which claim-evidence grounding benchmarks and metrics exist and how fragmented/incomparable they are, which is exactly what the brief's benchmark-mapping question (C3) needs before we pick or build an evaluation.

**Method.** Systematic literature survey and taxonomy construction over 134 papers; abstract-only detail on selection/synthesis methodology beyond the taxonomy itself.

**Limitations.**

- abstract-only, no primary experimental results of its own
- narrative/taxonomic synthesis rather than a systematic-review protocol with quantitative pooling

<sub>selected: review · criteria: C1 1/3 · C2 2/3 · C3 3/3 · C4 1/3 · C5 1/3 · flags: review · verified 2026-08-26 via crossref, openalex</sub>

## 9. Enabling Large Language Models to Generate Text with Citations

Tianyu Gao, H. W. Yen, Jiatong Yu, Danqi Chen · 2023 · Conference on Empirical Methods in Natural Language Processing · experimental · overall 2/3

<https://doi.org/10.18653/v1/2023.emnlp-main.398>

**Key finding.** ALCE, the first benchmark for automatic LLM citation evaluation, shows current end-to-end retrieve-and-cite systems have substantial room for improvement — on ELI5, even the best models lack complete citation support 50% of the time.

**Why it made the cut.** foundational · selected by foundational · strongest on C3 benchmark construction (3/3). Foundational citation-evaluation benchmark methodology that current scientific claim-grounding benchmarks reference and build on.

**Why it matters here.** Establishes the foundational citation-evaluation metric design (fluency/correctness/citation quality) that later scientific claim-grounding benchmarks build on, useful for designing our own automatic metrics even though its setting is general QA, not scientific papers.

**Method.** New benchmark (ALCE) combining diverse questions and retrieval corpora, with automatic metrics for fluency, correctness, and citation quality validated against human judgments; evaluated against SOTA LLMs and prompting strategies.

**Limitations.**

- general open-domain QA setting, not scientific-paper claim extraction
- predates most frontier models used in later benchmarks
- no scientific-paper-specific claim types tested

<sub>selected: foundational · criteria: C1 0/3 · C2 2/3 · C3 3/3 · C4 0/3 · C5 1/3 · flags: methods_paper · verified 2026-08-26 via crossref, openalex</sub>

## 10. Evaluating Verifiability in Generative Search Engines

Nelson F. Liu, Tianyi Zhang, Percy Liang · 2023 · Conference on Empirical Methods in Natural Language Processing · observational · overall 2/3

<https://doi.org/10.18653/v1/2023.findings-emnlp.467>

**Key finding.** Human evaluation of four commercial generative search engines finds only 51.5% of generated sentences are fully supported by their citations and only 74.5% of citations actually support their associated sentence.

**Why it made the cut.** foundational · selected by foundational · strongest on C2 evidence-link errors (3/3). The foundational human-evaluation study establishing the citation-verifiability framing (recall/precision of support) that scientific claim-grounding benchmarks build on.

**Why it matters here.** Foundational quantification of citation-support failure rates and the verifiability (recall/precision) framing that later scientific claim-grounding work, including the brief's own evidence-link-error question, directly inherits.

**Method.** Human evaluation audit of citation recall and precision across Bing Chat, NeevaAI, perplexity.ai, and YouChat on a diverse query set from Google logs and Reddit.

**Limitations.**

- general web search engines, not scientific-paper claim extraction
- commercial systems from 2023, likely outdated relative to current frontier models
- no per-claim-type or per-section breakdown

<sub>selected: foundational · criteria: C1 0/3 · C2 3/3 · C3 2/3 · C4 0/3 · C5 1/3 · flags: methods_paper · verified 2026-08-26 via crossref, openalex</sub>

## Coverage

| Criterion | Papers kept |
|---|---|
| C1 extraction accuracy | 55 |
| C2 evidence-link errors | 113 |
| C3 benchmark construction | 77 |
| C4 abstention and calibration | 36 |
| C5 cross-model or cross-domain generalisation | 28 |

## Alternates

Next in order, not selected:

- [SciVer: Evaluating Foundation Models for Multimodal Scientific Claim Verification](https://doi.org/10.48550/arxiv.2506.15569) (2025) — overall 3/3
- [Attribution in Scientific Literature: New Benchmark and Methods](https://doi.org/10.48550/arxiv.2405.02228) (2024) — overall 3/3
- [AttributionBench: How Hard is Automatic Attribution Evaluation?](https://doi.org/10.48550/arxiv.2402.15089) (2024) — overall 3/3
- [FactReview: Evidence-Grounded Peer Review with Execution-Based Claim Verification](https://doi.org/10.48550/arxiv.2604.04074) (2026) — overall 3/3
- [CiteME: Can Language Models Accurately Cite Scientific Claims?](https://doi.org/10.48550/arxiv.2407.12861) (2024) — overall 3/3
