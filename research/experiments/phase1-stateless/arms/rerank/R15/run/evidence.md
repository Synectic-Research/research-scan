# Evidence scan — claim-grounding-sonnet

Run `/Users/nabergoj/Projects/research-scan/research/experiments/phase1-stateless/arms/rerank/R15/run` · brief `/Users/nabergoj/Projects/research-scan/research/experiments/phase1-stateless/arms/rerank/R15/run/brief.md` · rendered 2026-08-26

| # | Paper | Year | Venue | Evidence | Verified |
|---|---|---|---|---|---|
| 1 | [Evaluating and Guarding Citation Faithfulness in Agentic Scientific Synthesis](https://doi.org/10.48550/arxiv.2607.20527) · 10.48550/arxiv.2607.20527 | 2026 | arXiv | experimental | yes |
| 2 | [ResearchQA: Benchmarking Citation-Grounded Question-Answering on Scientific Papers](https://doi.org/10.48550/arxiv.2607.11074) · 10.48550/arxiv.2607.11074 | 2026 | arXiv | experimental | yes |
| 3 | [When Verification Fails: How Compositionally Infeasible Claims Escape Rejection](https://doi.org/10.48550/arxiv.2604.10990) · 10.48550/arxiv.2604.10990 | 2026 | arXiv | experimental | yes |
| 4 | [Can AI Validate Science? Benchmarking LLMs for Accurate Scientific Claim → Evidence Reasoning](https://doi.org/10.48550/arxiv.2506.08235) · 10.48550/arxiv.2506.08235 | 2025 | arXiv.org | experimental | yes |
| 5 | [SciClaimEval: Cross-modal Claim Verification in Scientific Papers](https://doi.org/10.48550/arxiv.2602.07621) · 10.48550/arxiv.2602.07621 | 2026 | arXiv | experimental | yes |
| 6 | [PEARL: Auditable Repair for Scientific Reasoning Graph Extraction](https://doi.org/10.48550/arxiv.2607.17917) · 10.48550/arxiv.2607.17917 | 2026 | arXiv | experimental | yes |
| 7 | [CiteME: Can Language Models Accurately Cite Scientific Claims?](https://doi.org/10.48550/arxiv.2407.12861) · 10.48550/arxiv.2407.12861 | 2024 | Neural Information Processing Systems | experimental | yes |
| 8 | [Attribution in Scientific Literature: New Benchmark and Methods](https://doi.org/10.48550/arxiv.2405.02228) · 10.48550/arxiv.2405.02228 | 2024 | arXiv (Cornell University) | experimental | yes |
| 9 | [Enabling Large Language Models to Generate Text with Citations](https://doi.org/10.18653/v1/2023.emnlp-main.398) · 10.18653/v1/2023.emnlp-main.398 | 2023 | Conference on Empirical Methods in Natural Language Processing | computational | yes |
| 10 | [Evaluating Verifiability in Generative Search Engines](https://doi.org/10.18653/v1/2023.findings-emnlp.467) · 10.18653/v1/2023.findings-emnlp.467 | 2023 | Conference on Empirical Methods in Natural Language Processing | observational | yes |

## 1. Evaluating and Guarding Citation Faithfulness in Agentic Scientific Synthesis

Taewan Goo, Junsik Kim, Kyulhee Han, G. Jo et al. · 2026 · arXiv · experimental · overall 3/3

<https://doi.org/10.48550/arxiv.2607.20527>

**Key finding.** On identical agent outputs, measured unsupported-citation rate ranges from about 3% to 18% depending purely on verifier strictness, and verifiers disagree sharply on which citations to flag (negative-specific agreement 0.27-0.30), so no single flag set is trustworthy without a named, calibrated protocol.

**Why it made the cut.** design-changing · selected by score · strongest on C2 evidence-link errors (3/3). Directly targets three of the five sub-criteria (evidence-link error characterization, benchmark legitimacy, and abstention/calibration) with quantified, cross-model, cross-pipeline results.

**Why it matters here.** Directly answers the brief's abstention/calibration question with a deployable conformal guarantee and a concrete recalibration recipe for deployment drift, while showing that citation-faithfulness numbers are themselves unreliable unless the verifier and protocol are specified — this should change how the decision engine reports and bounds trustworthiness rather than just accepting a single verifier's verdict.

**Method.** Gold-anchored evaluation protocol validating the verifier against human gold, a swappable verifier (recall 0.94 on supported class), BM25 re-attribution, and a split-conformal guard giving a distribution-free finite-sample bound on truly unsupported citations; validated across four open 27-35B models and three agentic pipelines on SciFact, QASA and PubMedQA.

**Limitations.**

- guarantee is on catch rate, not on whether the underlying conclusion is correct
- tested on open 27-35B models; frontier closed models not covered

<sub>selected: score · criteria: C1 1/3 · C2 3/3 · C3 3/3 · C4 3/3 · C5 3/3 · flags: contradicts, methods_paper · verified 2026-08-26 via openalex, arxiv</sub>

## 2. ResearchQA: Benchmarking Citation-Grounded Question-Answering on Scientific Papers

Saba Imran, Debanjum Singh Solanky · 2026 · arXiv · experimental · overall 3/3

<https://doi.org/10.48550/arxiv.2607.11074>

**Key finding.** Citation-based metrics (section coverage, citation accuracy) separate the eight evaluated models far more clearly than LLM-evaluator rubric scores, which remain tightly compressed across models; open-weight models approach closed-model citation accuracy at 3-6x lower latency.

**Why it made the cut.** plan-influencing · selected by score · strongest on C3 benchmark construction (3/3). Directly relevant to benchmark construction and abstention/calibration questions with a citation-grounded, refusal-aware evaluation design.

**Why it matters here.** Shows that citation-grounding metrics and LLM-judge scores diverge sharply — a direct caution for how the decision engine should measure trustworthiness, and its adversarial/refusal-reward design is exactly the abstention behaviour the brief asks whether it helps or just costs coverage.

**Method.** 6,211 single-paper QA pairs from 494 open-access papers across eight domains and four question types (lookup, comprehension, multi-hop, adversarial), evaluated with a deterministic citation matcher plus an LLM rubric evaluator, explicitly rewarding grounded refusal when the source does not support an answer.

**Limitations.**

- abstract does not report the coverage cost of grounded refusal quantitatively
- single-paper QA setting, not full multi-document claim extraction

<sub>selected: score · criteria: C1 1/3 · C2 2/3 · C3 3/3 · C4 2/3 · C5 2/3 · flags: methods_paper · verified 2026-08-26 via openalex, arxiv</sub>

## 3. When Verification Fails: How Compositionally Infeasible Claims Escape Rejection

Muxin Liu, Delip Rao, Grace Kim, Chris Callison-Burch · 2026 · arXiv · experimental · overall 3/3

<https://doi.org/10.48550/arxiv.2604.10990>

**Key finding.** Models that saturate existing claim-verification benchmarks consistently over-accept compositionally infeasible claims where a non-salient constraint is contradicted, revealing that existing benchmarks only test a shortcut 'salient-constraint checking' rather than genuine closed-world verification.

**Why it made the cut.** contradicting · selected by score · strongest on C2 evidence-link errors (3/3). Directly contradicts the premise that current benchmarks validate robust verification, and shows an over-generalisation-like failure mode (accepting claims despite contradicted non-salient evidence).

**Why it matters here.** This is exactly the kind of benchmark-inflation finding the brief asks us to reach for: it shows current benchmarks cannot distinguish rigorous verification from a cheap shortcut, meaning reported high accuracy on standard claim-verification benchmarks overstates true reliability and should not be trusted as evidence that extraction/verification 'works well'.

**Method.** Constructed new compositionally infeasible claims (salient constraint supported, non-salient constraint contradicted) contrasted against standard single-perturbation infeasible claims; evaluated across model families and modalities, analyzed via ROC-curve positioning under context interventions.

**Limitations.**

- focuses on constraint-level composition, not full extraction pipeline from raw papers
- abstract does not report absolute accuracy numbers, only relative shortcut prevalence

<sub>selected: score · criteria: C1 0/3 · C2 3/3 · C3 3/3 · C4 0/3 · C5 3/3 · flags: contradicts, methods_paper · verified 2026-08-26 via openalex, arxiv</sub>

## 4. Can AI Validate Science? Benchmarking LLMs for Accurate Scientific Claim → Evidence Reasoning

Shashidhar Reddy Javaji, Yupeng Cao, Haohang Li, Yangyang Yu et al. · 2025 · arXiv.org · experimental · overall 3/3

<https://doi.org/10.48550/arxiv.2506.08235>

**Key finding.** Across over 300 claim-evidence pairs and six LLMs, closed-source models (GPT-4, Claude) consistently outperform open-source models in precision and recall on claim-evidence extraction, and strategically designed multi-pass prompting significantly improves linking accuracy at higher computational cost.

**Why it made the cut.** design-changing · selected by score · strongest on C1 extraction accuracy (3/3). A dedicated benchmark for claim-evidence extraction accuracy and linking across models, directly answering the brief's first two questions.

**Why it matters here.** Directly measures claim-evidence extraction accuracy broken down by model and prompting strategy on full papers, giving concrete evidence for whether extraction accuracy (not just evidence linking) varies by model — a core input to question 1 of the brief.

**Method.** CLAIM-BENCH benchmark comparing three divide-and-conquer-inspired extraction strategies (including three-pass and one-by-one prompting) across six diverse LLMs on full-length papers across multiple research domains.

**Limitations.**

- abstract does not report accuracy broken down by paper section or claim type in detail
- cost-accuracy tradeoff of multi-pass prompting may not scale to production pipelines

<sub>selected: score · criteria: C1 3/3 · C2 2/3 · C3 2/3 · C4 0/3 · C5 2/3 · flags: methods_paper · verified 2026-08-26 via openalex, arxiv</sub>

## 5. SciClaimEval: Cross-modal Claim Verification in Scientific Papers

Xanh Ho, Yun-Ang Wu, Sunisth Kumar, Tian Cheng Xia et al. · 2026 · arXiv · experimental · overall 3/3

<https://doi.org/10.48550/arxiv.2602.07621>

**Key finding.** Across 1,664 annotated samples from 180 papers, a substantial performance gap persists between the best of 11 benchmarked multimodal foundation models and human baselines, with figure-based verification remaining especially hard.

**Why it made the cut.** closely-related · selected by score · strongest on C3 benchmark construction (3/3). Directly answers the benchmark-construction question (C3) with a construction method designed to avoid inflating accuracy, and characterizes modality-specific evidence-linking failure.

**Why it matters here.** Demonstrates a rigorous, artifact-resistant method for constructing refutation examples (perturbing evidence, not claims), directly informing what benchmark numbers can legitimately support and where figure-grounded evidence linking remains a hard, unsolved failure mode.

**Method.** New cross-modal dataset built by modifying supporting figures/tables (rather than claims or LLM-fabricated contradictions) to create authentic refuted claims; tables provided in image, LaTeX, HTML and JSON formats; benchmarked 11 open and proprietary multimodal models.

**Limitations.**

- single evaluation snapshot across only ML/NLP/medicine domains
- does not test abstention or calibrated uncertainty

<sub>selected: score · criteria: C1 1/3 · C2 2/3 · C3 3/3 · C4 0/3 · C5 2/3 · flags: methods_paper · verified 2026-08-26 via openalex, arxiv</sub>

## 6. PEARL: Auditable Repair for Scientific Reasoning Graph Extraction

Bohan Su, Pengze Li, Yuchen Lu, Xi Chen · 2026 · arXiv · experimental · overall 3/3

<https://doi.org/10.48550/arxiv.2607.17917>

**Key finding.** Raw LLM outputs for scientific reasoning graph extraction pass strict semantic validity gates 0/350 times on ARCHE; PEARL's repair layer raises this to 300/350 and improves average REA from 0.339 to 0.906.

**Why it made the cut.** contradicting · selected by score · strongest on C2 evidence-link errors (3/3). Provides concrete evidence that claim/evidence-graph extraction itself can fail almost completely before repair, directly challenging the brief's working premise.

**Why it matters here.** A near-total baseline failure rate (0/350) on raw LLM graph extraction directly contradicts the premise that frontier LLMs extract claims/evidence structure reliably; the taxonomy of failure types (malformed syntax, wrong root, weak anchors) maps closely onto the evidence-link error categories the brief asks us to characterize.

**Method.** Training-free repair framework applying a closed Peircean schema and evidence-grounded judge feedback to fix malformed edges, drifting labels, incorrect root orientation and weak source anchors in LLM-generated reasoning graphs, tested on five 70-paper archives from the ARCHE benchmark.

**Limitations.**

- single benchmark family (ARCHE), no cross-domain test outside its five archives
- repair layer is post-hoc correction, not a measure of raw model calibration or abstention behaviour

<sub>selected: score · criteria: C1 2/3 · C2 3/3 · C3 2/3 · C4 0/3 · C5 1/3 · flags: contradicts, methods_paper · verified 2026-08-26 via openalex, arxiv</sub>

## 7. CiteME: Can Language Models Accurately Cite Scientific Claims?

O. Press, Andreas Hochlehnert, Ameya Prabhu, Vishaal Udandarao et al. · 2024 · Neural Information Processing Systems · experimental · overall 3/3

<https://doi.org/10.48550/arxiv.2407.12861>

**Key finding.** On the CiteME benchmark, frontier LMs achieve only 4.2-18.5% accuracy at identifying the paper referenced by a text excerpt, versus 69.7% for humans; an autonomous search-and-read agent (CiteAgent, GPT-4o-based) raises this to 35.3%.

**Why it made the cut.** design-changing · selected by score · strongest on C3 benchmark construction (3/3). Explicitly named in the brief's known papers; provides the headline evidence that citation grounding is unreliable even in frontier models.

**Why it matters here.** A stark, direct measurement showing citation-grounding is nowhere near reliable even for frontier models, which should recalibrate the project's confidence that evidence-linking failures are a minor residual problem rather than a dominant one.

**Method.** Benchmark of text excerpts from recent ML papers each referencing a single other paper, evaluated for citation-attribution accuracy across frontier LMs and a retrieval-augmented agent system.

**Limitations.**

- citation attribution (finding the source paper) is a narrower task than full evidence-passage grounding within a paper
- confined to machine learning papers

<sub>selected: score · criteria: C1 1/3 · C2 2/3 · C3 3/3 · C4 0/3 · C5 2/3 · flags: contradicts, methods_paper · verified 2026-08-26 via openalex, arxiv</sub>

## 8. Attribution in Scientific Literature: New Benchmark and Methods

Yash Saxena, Deepa Tilwani, Ali Mohammadi, Edward Raff et al. · 2024 · arXiv (Cornell University) · experimental · overall 3/3

<https://doi.org/10.48550/arxiv.2405.02228>

**Key finding.** Top-tier LLMs achieve high sentence-attribution performance but with high hallucination rates; a metadata-augmented, RAG-based approach with Mistral reduces hallucination rates by 42% on indirect queries while maintaining competitive precision, though adversarial testing exposes fundamental limitations linking titles to abstracts.

**Why it made the cut.** plan-influencing · selected by score · strongest on C3 benchmark construction (3/3). Provides a cross-model, cross-domain benchmark quantifying hallucination in citation attribution and a mitigation strategy, relevant to evidence-link error characterization and benchmark construction.

**Why it matters here.** Quantifies hallucination as the key reliability metric for citation attribution rather than raw accuracy alone, and shows a concrete mitigation (RAG + metadata) with a measured 42% reduction — directly useful evidence for how the decision engine should measure and reduce fabricated-support errors.

**Method.** REASONS dataset with sentence-level citation annotations across 12 arXiv domains, covering indirect (sentence-to-title) and direct (author attribution) query scenarios; tested GPT-o1, GPT-4o, GPT-3.5, DeepSeek and smaller models like Perplexity AI (7B), with and without metadata/RAG augmentation.

**Limitations.**

- adversarial testing reveals persistent title-to-abstract linking failures not solved by the proposed mitigation
- no test of abstention/calibrated refusal as a trustworthiness mechanism

<sub>selected: score · criteria: C1 1/3 · C2 2/3 · C3 3/3 · C4 0/3 · C5 2/3 · flags: methods_paper · verified 2026-08-26 via openalex, arxiv</sub>

## 9. Enabling Large Language Models to Generate Text with Citations

Tianyu Gao, H. W. Yen, Jiatong Yu, Danqi Chen · 2023 · Conference on Empirical Methods in Natural Language Processing · computational · overall 2/3

<https://doi.org/10.18653/v1/2023.emnlp-main.398>

**Key finding.** On the ALCE benchmark, even the best LLM-based systems fail to fully support their citations 50% of the time on the ELI5 dataset, revealing large gaps in citation quality despite fluent-looking output.

**Why it made the cut.** foundational · selected by foundational · strongest on C3 benchmark construction (3/3). Foundational benchmark-construction work for LLM citation evaluation that the newer scientific claim-grounding benchmarks (e.g. CiteME) build on methodologically.

**Why it matters here.** This is the precursor benchmark-construction methodology (automatic + human-correlated citation-quality metrics) that CiteME-style scientific grounding benchmarks build on, so it recalibrates what 'benchmark numbers can legitimately support' for citation grounding claims — but its setting is open-domain QA, not scientific-paper claim extraction, so its accuracy figures cannot be imported directly.

**Method.** Introduces ALCE, an end-to-end benchmark requiring retrieval plus citation-annotated generation across diverse questions/corpora, with automatic metrics for fluency, correctness, and citation quality validated against human judgment.

**Limitations.**

- general open-domain QA (ELI5, etc.), not scientific literature
- citations are to retrieved passages/web sources rather than paper-internal evidence or tables
- predates the brief's 2024-01 window

<sub>selected: foundational · criteria: C1 0/3 · C2 2/3 · C3 3/3 · C4 0/3 · C5 2/3 · flags: methods_paper · verified 2026-08-26 via crossref, openalex</sub>

## 10. Evaluating Verifiability in Generative Search Engines

Nelson F. Liu, Tianyi Zhang, Percy Liang · 2023 · Conference on Empirical Methods in Natural Language Processing · observational · overall 2/3

<https://doi.org/10.18653/v1/2023.findings-emnlp.467>

**Key finding.** Human audit of four commercial generative search engines found only 51.5% of generated sentences were fully supported by citations and only 74.5% of citations actually supported their associated statement.

**Why it made the cut.** closely-related · selected by foundational · strongest on C2 evidence-link errors (3/3). Provides rigorous quantitative evidence of pervasive citation-support failures in LLM systems, directly informing the brief's C2 question on evidence-link error rates, despite being in a different domain (web search) than scientific-paper grounding.

**Why it matters here.** Directly quantifies the base rate of unsupported and inaccurate citations in LLM-generated, citation-bearing text (roughly a quarter of citations wrong), which is the closest empirical analogue to the evidence-linking error rates the paper-to-decision engine must anticipate and calibrate abstention against — but it measures web-search citation behavior, not scientific-paper claim grounding, so the numbers should inform expectations rather than be treated as transferable accuracy figures.

**Method.** Human evaluation of citation precision and recall across Bing Chat, NeevaAI, perplexity.ai, and YouChat, using a diverse query set from Google logs, Reddit, and other sources.

**Limitations.**

- domain is open-web generative search engines, not scientific papers
- citations are to web sources, not paper text/tables/figures
- predates the brief's 2024-01 window and the systems evaluated are proprietary black boxes

<sub>selected: foundational · criteria: C1 0/3 · C2 3/3 · C3 2/3 · C4 0/3 · C5 2/3 · flags: contradicts · verified 2026-08-26 via crossref, openalex</sub>

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
- [Fact or Fiction: Verifying Scientific Claims](https://doi.org/10.18653/v1/2020.emnlp-main.609) (2020) — overall 3/3
- [Encoded but Not Routed: Explaining the Table-Chart Gap in Scientific Claim Verification](https://doi.org/10.48550/arxiv.2606.01679) (2026) — overall 2/3
- [ToolSciVer: Multimodal Scientific Claim Verification with Visual Tool Augmented Reinforcement Learning](https://arxiv.org/abs/2607.16131) (2026) — overall 2/3
- [+VeriRel: Verification Feedback to Enhance Document Retrieval for Scientific Fact Checking](https://doi.org/10.1145/3746252.3760822) (2025) — overall 1/3
