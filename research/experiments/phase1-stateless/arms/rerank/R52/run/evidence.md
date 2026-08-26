# Evidence scan — claim-grounding-sonnet

Run `/Users/nabergoj/Projects/research-scan/research/experiments/phase1-stateless/arms/rerank/R52/run` · brief `/Users/nabergoj/Projects/research-scan/research/experiments/phase1-stateless/arms/rerank/R52/run/brief.md` · rendered 2026-08-26

| # | Paper | Year | Venue | Evidence | Verified |
|---|---|---|---|---|---|
| 1 | [Evaluating and Guarding Citation Faithfulness in Agentic Scientific Synthesis](https://doi.org/10.48550/arxiv.2607.20527) · 10.48550/arxiv.2607.20527 | 2026 | arXiv | experimental | yes |
| 2 | [ResearchQA: Benchmarking Citation-Grounded Question-Answering on Scientific Papers](https://doi.org/10.48550/arxiv.2607.11074) · 10.48550/arxiv.2607.11074 | 2026 | arXiv | computational | yes |
| 3 | [When Retrieval Helps and Distracts: Evaluating Evidence-Generating LLMs for Biomedical Claim Verification](https://doi.org/10.48550/arxiv.2608.01409) · 10.48550/arxiv.2608.01409 | 2026 | arXiv | computational | yes |
| 4 | [Can AI Validate Science? Benchmarking LLMs for Accurate Scientific Claim → Evidence Reasoning](https://doi.org/10.48550/arxiv.2506.08235) · 10.48550/arxiv.2506.08235 | 2025 | arXiv.org | computational | yes |
| 5 | [Attribution in Scientific Literature: New Benchmark and Methods](https://doi.org/10.48550/arxiv.2405.02228) · 10.48550/arxiv.2405.02228 | 2024 | arXiv (Cornell University) | computational | yes |
| 6 | [Evidence Absence Is Not Evidence Insufficiency: Diagnosing NEI Construction Artifacts in Fact Verification](https://doi.org/10.48550/arxiv.2605.26663) · 10.48550/arxiv.2605.26663 | 2026 | arXiv.org | computational | yes |
| 7 | [An automated framework for assessing how well LLMs cite relevant medical references](https://doi.org/10.1038/s41467-025-58551-6) · 10.1038/s41467-025-58551-6 | 2025 | Nature Communications | experimental | yes |
| 8 | [Attribution, Citation, and Quotation: A Survey of Evidence-based Text Generation with Large Language Models](https://doi.org/10.18653/v1/2026.acl-long.1430) · 10.18653/v1/2026.acl-long.1430 | 2025 | Annual Meeting of the Association for Computational Linguistics | other | yes |
| 9 | [Enabling Large Language Models to Generate Text with Citations](https://doi.org/10.18653/v1/2023.emnlp-main.398) · 10.18653/v1/2023.emnlp-main.398 | 2023 | Conference on Empirical Methods in Natural Language Processing | experimental | yes |
| 10 | [Evaluating Verifiability in Generative Search Engines](https://doi.org/10.18653/v1/2023.findings-emnlp.467) · 10.18653/v1/2023.findings-emnlp.467 | 2023 | Conference on Empirical Methods in Natural Language Processing | observational | yes |

## 1. Evaluating and Guarding Citation Faithfulness in Agentic Scientific Synthesis

Taewan Goo, Junsik Kim, Kyulhee Han, G. Jo et al. · 2026 · arXiv · experimental · overall 3/3

<https://doi.org/10.48550/arxiv.2607.20527>

**Key finding.** On identical agent outputs, measured unsupported-citation rate ranges from ~3% to ~18% depending only on the citation verifier's strictness, and verifiers disagree sharply on which citations to flag (negative-specific agreement 0.27-0.30), so a gold-anchored protocol plus a split-conformal guard is needed to bound the true unsupported-citation rate.

**Why it made the cut.** design-changing · selected by score · strongest on C2 evidence-link errors (3/3). Answers the evidence-link error question (C2), benchmark legitimacy question (C3), and the abstention/calibration question (C4) all at once, directly informing how the paper-to-decision engine should report trustworthiness.

**Why it matters here.** Directly demonstrates that citation-verification checks themselves are unreliable unless calibrated against gold, and provides a concrete, transferable mechanism (conformal bound + recalibration recipe) for our engine to report a bounded trustworthiness guarantee rather than a bare confidence score.

**Method.** Gold-anchored evaluation protocol comparing multiple citation-faithfulness verifiers against human-graded gold, plus a deployable split-conformal guard giving distribution-free, finite-sample bounds on unsupported citations; validated across four open 27-35B models and three agentic pipelines on SciFact, QASA, and PubMedQA.

**Limitations.**

- verifier models limited to 27-35B open-weight range, may not reflect frontier proprietary models
- calibration-negative difficulty condition requires recalibration recipe that adds deployment complexity
- abstract gives ranges rather than a single definitive verifier

<sub>selected: score · criteria: C1 1/3 · C2 3/3 · C3 3/3 · C4 3/3 · C5 3/3 · flags: methods_paper · verified 2026-08-26 via openalex, arxiv</sub>

## 2. ResearchQA: Benchmarking Citation-Grounded Question-Answering on Scientific Papers

Saba Imran, Debanjum Singh Solanky · 2026 · arXiv · computational · overall 3/3

<https://doi.org/10.48550/arxiv.2607.11074>

**Key finding.** On ResearchQA's 6,211 citation-grounded QA pairs from 494 papers, citation-based metrics (section coverage, citation accuracy) separate eight leading models far more clearly than LLM-evaluator rubric scores, which remain tightly compressed; open-weight models approach closed-model citation accuracy at 3-6x lower latency.

**Why it made the cut.** design-changing · selected by score · strongest on C3 benchmark construction (3/3). Directly built around citation grounding and grounded refusal, the two core mechanisms (C2/C4) the decision engine needs to report trustworthiness and abstain.

**Why it matters here.** Directly tests grounded refusal (abstention) as a first-class benchmark dimension and shows that citation-grounded metrics, not generic LLM-judge scores, are what actually discriminate model trustworthiness — a design lesson for how our engine should evaluate itself.

**Method.** New benchmark spanning eight domains and four question types (lookup, comprehension, multi-hop, adversarial) permitting multiple valid supporting passages and explicitly rewarding grounded refusal; evaluated with a deterministic citation matcher and LLM rubric across eight closed/open models.

**Limitations.**

- single-paper QA setting may not capture cross-paper claim extraction
- abstract does not report absolute citation-accuracy numbers, only relative separation
- adversarial question type performance not broken out in abstract

<sub>selected: score · criteria: C1 1/3 · C2 2/3 · C3 3/3 · C4 3/3 · C5 3/3 · flags: methods_paper · verified 2026-08-26 via openalex, arxiv</sub>

## 3. When Retrieval Helps and Distracts: Evaluating Evidence-Generating LLMs for Biomedical Claim Verification

Pritam Deka, Prabhjot Singh · 2026 · arXiv · computational · overall 3/3

<https://doi.org/10.48550/arxiv.2608.01409>

**Key finding.** PubMed retrieval-augmentation helps evidence generation on PubMed-aligned sources like PubMedQA and SciFact but distracts models on broader public-health claims, and fine-tuned LLMs -- not retrieval-augmented ones -- are the strongest evidence generators.

**Why it made the cut.** design-changing · selected by score · strongest on C2 evidence-link errors (3/3). Rigorous biomedical evaluation showing retrieval augmentation can distract rather than help evidence-evidence linking, a premise-challenging finding squarely in the brief's allowed biomedicine scope.

**Why it matters here.** Directly contradicts the assumption that adding retrieved evidence uniformly improves grounding; shows retrieval utility is source-dependent, which should change the engine's default of 'always retrieve more evidence' into a selective-retrieval policy.

**Method.** Unified evaluation across five biomedical/health fact-checking sources (CARE-XAI) comparing base LLMs, PubMed-RAG LLMs, fine-tuned LLMs, label-only LLMs, and biomedical encoder classifiers, plus a new Bio-GRACE diagnostic for retrieval-evidence utility.

**Limitations.**

- Biomedicine-specific, may not generalize to other scientific domains
- Bio-GRACE diagnostic is newly introduced and not independently validated elsewhere

<sub>selected: score · criteria: C1 1/3 · C2 3/3 · C3 2/3 · C4 1/3 · C5 3/3 · flags: contradicts · verified 2026-08-26 via openalex, arxiv</sub>

## 4. Can AI Validate Science? Benchmarking LLMs for Accurate Scientific Claim → Evidence Reasoning

Shashidhar Reddy Javaji, Yupeng Cao, Haohang Li, Yangyang Yu et al. · 2025 · arXiv.org · computational · overall 3/3

<https://doi.org/10.48550/arxiv.2506.08235>

**Key finding.** CLAIM-BENCH, evaluated over 300+ claim-evidence pairs, shows closed-source models (GPT-4, Claude) consistently outperform open-source counterparts on claim-evidence extraction and validation, and that three-pass/one-by-one prompting strategies improve linking dispersed evidence to claims at increased compute cost.

**Why it made the cut.** design-changing · selected by score · strongest on C1 extraction accuracy (3/3). A benchmark specifically evaluating LLM claim-evidence extraction and validation across full papers with six models, directly answering Q1 and Q5.

**Why it matters here.** Directly measures the extraction-accuracy question the brief's premise rests on (Q1) and shows meaningful cross-model gaps and prompting-strategy tradeoffs (accuracy vs cost) our engine's extraction module should be benchmarked against.

**Method.** New benchmark and three divide-and-conquer-inspired prompting strategies compared across six diverse LLMs for claim-evidence identification and validation over full-length papers.

**Limitations.**

- only ~300 claim-evidence pairs, modest scale for a full-paper extraction benchmark
- abstract does not break results down by paper section as the brief's C1 asks for
- compute-cost tradeoff of improved prompting strategies not quantified

<sub>selected: score · criteria: C1 3/3 · C2 2/3 · C3 2/3 · C4 0/3 · C5 3/3 · flags: methods_paper · verified 2026-08-26 via openalex, arxiv</sub>

## 5. Attribution in Scientific Literature: New Benchmark and Methods

Yash Saxena, Deepa Tilwani, Ali Mohammadi, Edward Raff et al. · 2024 · arXiv (Cornell University) · computational · overall 3/3

<https://doi.org/10.48550/arxiv.2405.02228>

**Key finding.** On the REASONS benchmark (sentence-level annotations across 12 arXiv domains), top LLMs (GPT-o1, GPT-4o, GPT-3.5, DeepSeek) attribute sentences well but show high hallucination rates, and a retrieval-augmented Mistral setup reduces hallucination by 42% on indirect queries while adversarial title-to-abstract linking remains a fundamental weakness.

**Why it made the cut.** plan-influencing · selected by score · strongest on C2 evidence-link errors (3/3). Directly characterizes citation-grounding hallucination as a dominant evidence-linking error type and tests mitigations across many models and domains.

**Why it matters here.** Quantifies hallucination in citation attribution as a distinct, measurable failure mode and shows metadata augmentation and RAG meaningfully reduce it, giving our engine a concrete lever (metadata-augmented grounding) and a metric (hallucination rate) to track alongside accuracy.

**Method.** New dataset with sentence-level citation annotations across 12 domains, covering indirect (sentence-to-title) and direct (author attribution) query scenarios enhanced with contextual metadata; extensive experiments across multiple LLM families plus adversarial testing.

**Limitations.**

- hallucination-rate reduction figures are task-specific (indirect queries) and may not transfer to direct attribution
- adversarial title-to-abstract failures suggest even improved methods have a ceiling not fully characterized
- abstract-only, no per-domain breakdown given

<sub>selected: score · criteria: C1 1/3 · C2 3/3 · C3 3/3 · C4 0/3 · C5 3/3 · flags: methods_paper · verified 2026-08-26 via openalex, arxiv</sub>

## 6. Evidence Absence Is Not Evidence Insufficiency: Diagnosing NEI Construction Artifacts in Fact Verification

Jing Qiu, Zeyu Han, Chen Huang · 2026 · arXiv.org · computational · overall 3/3

<https://doi.org/10.48550/arxiv.2605.26663>

**Key finding.** NEI competence does not transfer reliably across construction families in SciFact-style, FEVER, and HoVer benchmarks: models trained on shortcut-prone NEI constructions fail on semantically related insufficient-evidence cases, and the evidence condition used to build NEI examples silently shifts confidence in the reference Support/Refute label itself.

**Why it made the cut.** contradicting · selected by score · strongest on C3 benchmark construction (3/3). Precisely the kind of benchmark-artifact critique the brief asked us to reach hardest for, in the SciFact lineage named as a known-paper anchor.

**Why it matters here.** Directly targets the brief's hardest ask — a benchmark whose construction inflates reported accuracy — and shows an aggregate NEI/abstention score can hide which problem a model actually solved, which is exactly the calibration/abstention question our engine must get right before trusting an 'insufficient evidence' verdict.

**Method.** NEI-CAP, a construction-aware diagnostic protocol that tags each Not-Enough-Information example by the construction method that produced it, audits shortcut cues, validates hard cases via human adjudication, and tests cross-construction transfer, instantiated on SciFact-style verification with FEVER/HoVer as controls.

**Limitations.**

- abstract-only
- focused on NEI/insufficiency labeling rather than full claim extraction pipelines
- SciFact-style setting may not generalize to full-paper multi-modal evidence (tables, figures)

<sub>selected: score · criteria: C1 0/3 · C2 2/3 · C3 3/3 · C4 2/3 · C5 3/3 · flags: contradicts, methods_paper · verified 2026-08-26 via openalex, arxiv</sub>

## 7. An automated framework for assessing how well LLMs cite relevant medical references

Kevin Wu, Eric Wu, Kevin Wei, Angela Zhang et al. · 2025 · Nature Communications · experimental · overall 3/3

<https://doi.org/10.1038/s41467-025-58551-6>

**Key finding.** Across seven LLMs on 800 medical questions and 58,000 statement-source pairs, 50-90% of LLM responses are not fully supported (and sometimes contradicted) by their cited sources; even GPT-4o with Web Search leaves ~30% of individual statements unsupported and nearly half its responses not fully supported, confirmed by independent doctor review.

**Why it made the cut.** contradicting · selected by score · strongest on C2 evidence-link errors (3/3). The strongest quantitative evidence found on how often LLM claim-evidence citation links fail, directly answering Q2 at scale in a biomedical setting the brief explicitly permits.

**Why it matters here.** Large-scale, doctor-validated quantitative evidence that evidence-linking failure (unsupported or contradicted citations) is the dominant and severe error mode even in frontier models with web search, directly contradicting any assumption that citation grounding is largely solved.

**Method.** SourceCheckup, an automated agent-based pipeline, evaluates relevance and supportiveness of cited sources for LLM-generated medical statements at scale, cross-validated against independent physician assessment.

**Limitations.**

- medical query domain rather than full scientific-paper reading
- focuses on citation support for generated statements rather than claim extraction from a single source paper
- does not test abstention/calibration interventions

<sub>selected: score · criteria: C1 1/3 · C2 3/3 · C3 3/3 · C4 0/3 · C5 3/3 · flags: contradicts · verified 2026-08-26 via crossref, openalex</sub>

## 8. Attribution, Citation, and Quotation: A Survey of Evidence-based Text Generation with Large Language Models

Tobias Schreieder, Tim Schopf, Michael Farber · 2025 · Annual Meeting of the Association for Computational Linguistics · other · overall 3/3

<https://doi.org/10.18653/v1/2026.acl-long.1430>

**Key finding.** A systematic analysis of 134 papers on evidence-based (attribution/citation/quotation) text generation with LLMs finds the field fragmented by inconsistent terminology, isolated evaluation practices, and 300 distinct evaluation metrics across seven dimensions, with no unified benchmark.

**Why it made the cut.** closely-related · selected by review · strongest on C3 benchmark construction (3/3). The comprehensive survey of the benchmark and evaluation landscape the project needs to map (Q3), with 134 papers and 300 metrics catalogued.

**Why it matters here.** Provides the map of existing claim-evidence grounding benchmarks and metrics the project needs before choosing which to adopt, and its finding of fragmented, inconsistent evaluation practice is itself evidence that reported numbers across papers are not directly comparable.

**Method.** Literature survey and taxonomy-building over 134 papers; catalogues methods and 300 evaluation metrics across seven key dimensions of evidence-based generation.

**Limitations.**

- abstract-only
- survey rather than new empirical evidence
- does not itself measure extraction or grounding accuracy

<sub>selected: review · criteria: C1 1/3 · C2 2/3 · C3 3/3 · C4 1/3 · C5 2/3 · flags: review · verified 2026-08-26 via crossref, openalex</sub>

## 9. Enabling Large Language Models to Generate Text with Citations

Tianyu Gao, H. W. Yen, Jiatong Yu, Danqi Chen · 2023 · Conference on Empirical Methods in Natural Language Processing · experimental · overall 2/3

<https://doi.org/10.18653/v1/2023.emnlp-main.398>

**Key finding.** On ALCE, the first benchmark for automatic LLM citation evaluation, even the best state-of-the-art models lack complete citation support 50% of the time on the ELI5 dataset.

**Why it made the cut.** foundational · selected by foundational · strongest on C3 benchmark construction (3/3). Foundational benchmark-construction work for citation grounding that the CiteME line (named in the brief) builds on; its automatic-metric methodology for citation correctness/quality is the explicit technique transferable to scientific claim-evidence grounding benchmarks.

**Why it matters here.** Establishes the benchmark-construction template (automatic metrics correlated with human judgement, end-to-end retrieve-then-cite systems) that later scientific-grounding benchmarks like CiteME build on, and its headline number — 50% incomplete citation support even in top models — is a baseline the project should not assume is beaten by frontier LLMs on scientific text without checking.

**Method.** Benchmark construction across diverse questions and retrieval corpora, with automatic metrics for fluency, correctness and citation quality validated against human judgements; evaluated with multiple LLMs and prompting strategies.

**Limitations.**

- setting is general information-seeking QA (e.g. ELI5) with open web/retrieval corpora, not scientific-paper claim extraction
- citation quality measured for generated answers, not extraction/verification of claims already stated in a source paper
- out-of-window (2023) so does not reflect current frontier models

<sub>selected: foundational · criteria: C1 0/3 · C2 2/3 · C3 3/3 · C4 0/3 · C5 2/3 · flags: methods_paper · verified 2026-08-26 via crossref, openalex</sub>

## 10. Evaluating Verifiability in Generative Search Engines

Nelson F. Liu, Tianyi Zhang, Percy Liang · 2023 · Conference on Empirical Methods in Natural Language Processing · observational · overall 2/3

<https://doi.org/10.18653/v1/2023.findings-emnlp.467>

**Key finding.** Across four commercial generative search engines (Bing Chat, NeevaAI, perplexity.ai, YouChat), only 51.5% of generated sentences were fully supported by citations and only 74.5% of citations actually supported their associated sentence.

**Why it made the cut.** closely-related · selected by foundational · strongest on C2 evidence-link errors (3/3). Rigorous human-evaluation methodology for citation verifiability (recall/precision) directly relevant to characterizing evidence-link errors, though in a neighbouring (web search) rather than scientific-paper setting.

**Why it matters here.** Gives a concrete, human-annotated quantification of how often citation links fail even in citation-quality dimensions (unsupported statements ~48%, unsupported citations ~25%) that supports the brief's working premise that evidence-linking is the dominant failure mode, and offers a directly transferable audit methodology (citation recall/precision via human annotation) for scoring the project's own claim-evidence links.

**Method.** Human evaluation audit of citation recall and precision across a diverse query set (historical Google queries, Reddit questions, etc.) for four production generative search systems.

**Limitations.**

- setting is open-web generative search engines answering general queries, not scientific-paper claim extraction
- no scientific literature or paper-specific structure (tables, sections) involved
- out-of-window (2023), commercial systems since updated
- does not break down errors by fabricated support vs wrong-direction vs over-generalisation

<sub>selected: foundational · criteria: C1 0/3 · C2 3/3 · C3 1/3 · C4 0/3 · C5 2/3 · verified 2026-08-26 via crossref, openalex</sub>

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

- [SciClaimEval: Cross-modal Claim Verification in Scientific Papers](https://doi.org/10.48550/arxiv.2602.07621) (2026) — overall 3/3
- [MiniCheck: Efficient Fact-Checking of LLMs on Grounding Documents](https://doi.org/10.18653/v1/2024.emnlp-main.499) (2024) — overall 3/3
- [Do You Need a Frontier Model as a Citation Verifier? Benchmarking Rubric LLMs for Deep-Research Source Attribution](https://arxiv.org/abs/2607.08700) (2026) — overall 3/3
- [When Verification Fails: How Compositionally Infeasible Claims Escape Rejection](https://doi.org/10.48550/arxiv.2604.10990) (2026) — overall 3/3
- [HiEviDR-Bench: A Benchmark for Hierarchical Evidence Aggregation in Deep Research](https://doi.org/10.48550/arxiv.2607.25151) (2026) — overall 3/3
