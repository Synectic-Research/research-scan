# Evidence scan — p11-t2

Run `/Users/nabergoj/Projects/research-scan/research/experiments/phase14/runs/p11-t2/SC/rep4/run` · brief `/Users/nabergoj/Projects/research-scan/research/experiments/phase14/runs/p11-t2/SC/rep4/run/brief.md` · rendered 2026-08-27

| # | Paper | Year | Venue | Evidence | Verified |
|---|---|---|---|---|---|
| 1 | [When to use Graphs in RAG: A Comprehensive Analysis for Graph Retrieval-Augmented Generation](https://doi.org/10.48550/arxiv.2506.05690) · 10.48550/arxiv.2506.05690 | 2025 | arXiv.org | experimental | yes |
| 2 | [BrowseComp-Plus: A More Fair and Transparent Evaluation Benchmark of Deep-Research Agent](https://doi.org/10.48550/arxiv.2508.06600) · 10.48550/arxiv.2508.06600 | 2025 | arXiv (Cornell University) | experimental | yes |
| 3 | [Towards Recursive Self-Evolving Agentic Literature Retrieval](https://doi.org/10.48550/arxiv.2605.14306) · 10.48550/arxiv.2605.14306 | 2026 | arXiv | experimental | yes |
| 4 | [PaSa: An LLM Agent for Comprehensive Academic Paper Search](https://doi.org/10.48550/arxiv.2501.10120) · 10.48550/arxiv.2501.10120 | 2025 | Annual Meeting of the Association for Computational Linguistics | experimental | yes |
| 5 | [Structurally-bounded Agentic Graph Exploration for Evidence-Grounded Scholarly DeepSearch](https://doi.org/10.48550/arxiv.2608.24809) · 10.48550/arxiv.2608.24809 | 2026 | arXiv | experimental | yes |
| 6 | [Patience is all you need! An agentic system for performing scientific literature review](https://doi.org/10.48550/arxiv.2504.08752) · 10.48550/arxiv.2504.08752 | 2025 | arXiv.org | experimental | yes |
| 7 | [OpenScholar: Synthesizing Scientific Literature with Retrieval-augmented LMs](https://doi.org/10.48550/arxiv.2411.14199) · 10.48550/arxiv.2411.14199 | 2024 | arXiv.org | experimental | yes |
| 8 | [Fact, Fetch, and Reason: A Unified Evaluation of Retrieval-Augmented Generation](https://doi.org/10.48550/arxiv.2409.12941) · 10.48550/arxiv.2409.12941 | 2024 | North American Chapter of the Association for Computational Linguistics | experimental | yes |
| 9 | [LitSearch: A Retrieval Benchmark for Scientific Literature Search](https://doi.org/10.48550/arxiv.2407.18940) · 10.48550/arxiv.2407.18940 | 2024 | Conference on Empirical Methods in Natural Language Processing | experimental | yes |
| 10 | [Deep Research Agents: A Systematic Examination And Roadmap](https://doi.org/10.48550/arxiv.2506.18096) · 10.48550/arxiv.2506.18096 | 2025 | arXiv.org | other | yes |

## 1. When to use Graphs in RAG: A Comprehensive Analysis for Graph Retrieval-Augmented Generation

Zhishang Xiang, Chuan-Yu Wu, Qinggang Zhang, Shengyuan Chen et al. · 2025 · arXiv.org · experimental · overall 3/3

<https://doi.org/10.48550/arxiv.2506.05690>

**Key finding.** GraphRAG-Bench, a comprehensive benchmark spanning fact retrieval, complex reasoning, contextual summarization and creative generation, finds that GraphRAG frequently underperforms vanilla RAG and systematically characterizes the conditions under which graph structure actually helps.

**Why it made the cut.** contradicting · selected by score · strongest on C3 retrieval/reranking method (3/3). Names the exact agentic mechanism (graph traversal) in C2 and shows, via a purpose-built benchmark, that its gain over vanilla retrieval frequently fails to hold -- an explicit method-level contradiction the brief asked the scan to reach hardest for.

**Why it matters here.** Directly interrogates the specific agentic mechanism the brief names (citation-graph traversal) and shows the reported gain from graph structure does not generalize across tasks, which is precisely the Q2/Q4 evidence the brief wants prioritized over confirming results.

**Method.** New benchmark with a full-pipeline evaluation protocol (graph construction, retrieval, generation) across tasks of increasing difficulty, used to compare GraphRAG variants against vanilla RAG.

**Limitations.**

- evaluates general RAG/QA tasks, not literature-search agents specifically, though the mechanism (graph vs. vector retrieval) is the same one named in the brief's C2
- does not include a citation-graph-traversal literature agent as such

<sub>selected: score · criteria: C1 1/3 · C2 2/3 · C3 3/3 · C4 3/3 · C5 3/3 · flags: contradicts, methods_paper · verified 2026-08-27 via openalex, arxiv</sub>

## 2. BrowseComp-Plus: A More Fair and Transparent Evaluation Benchmark of Deep-Research Agent

Zijian Chen, Xueguang Ma, Shengyao Zhuang, Ping Nie et al. · 2025 · arXiv (Cornell University) · experimental · overall 3/3

<https://doi.org/10.48550/arxiv.2508.06600>

**Key finding.** Search-R1 with a BM25 retriever achieves only 3.86% accuracy on BrowseComp-Plus, while GPT-5 alone reaches 55.9%, and GPT-5 with a Qwen3-Embedding-8B retriever reaches 70.1% with fewer search calls.

**Why it made the cut.** foundational · selected by score · strongest on C1 baseline recall ceiling (3/3). The controlled, fixed-corpus benchmark giving explicit single-query-retriever baseline numbers and disentangling agent vs. retriever contribution — foundational to the brief's Q1 and Q3.

**Why it matters here.** Gives explicit, quantified baseline numbers for a weak single-query retriever (BM25) versus stronger retrievers and agents, directly anchoring the recall-ceiling question (Q1), and is the fixed-corpus benchmark-construction precedent later work (e.g., the ClimbMix projection) builds on and stress-tests.

**Method.** A fixed, curated corpus with human-verified supporting documents and mined hard negatives, derived from BrowseComp, enabling controlled disentanglement of agent versus retriever contributions.

**Limitations.**

- Corpus assembled specifically from the benchmark's own queries and mined negatives, which later work shows may inflate apparent performance
- Limited to the BrowseComp query distribution

<sub>selected: score · criteria: C1 3/3 · C2 1/3 · C3 2/3 · C4 3/3 · C5 2/3 · flags: methods_paper · verified 2026-08-27 via openalex, arxiv</sub>

## 3. Towards Recursive Self-Evolving Agentic Literature Retrieval

Yuwen Du, Tian Jin, Jing Kang, Xianghe Pang et al. · 2026 · arXiv · experimental · overall 3/3

<https://doi.org/10.48550/arxiv.2605.14306>

**Key finding.** PaSaMaster, a recursive self-evolving literature retrieval agent separating intent-planning from retrieval/ranking, achieves a 16.5x higher F1 than Google Scholar and 37.8% higher F1 than GPT-5.2 at ~1% of the cost across 38 disciplines in PaSaMaster-Bench, cutting source hallucination from 32.66% to zero.

**Why it made the cut.** design-changing · selected by score · strongest on C1 baseline recall ceiling (3/3). One of the few papers in the batch that both measures a single-query baseline ceiling (Google Scholar) and attributes the gain to a named agentic mechanism, making it central evidence for the brief's first two questions.

**Why it matters here.** Directly anchors the single-query search baseline (Google Scholar) against an agentic system and attributes the gain to a specific mechanism (self-evolving intent refinement plus verified-only ranking), answering both the brief's Q1 and Q2 in one study.

**Method.** Recursive self-evolving retrieval with planning-retrieval separation (frontier LLM for intent, lightweight models for retrieval/scoring), evaluated on the purpose-built PaSaMaster-Bench spanning 38 disciplines against Google Scholar and GPT-5.2 baselines.

**Limitations.**

- benchmark (PaSaMaster-Bench) is newly introduced by the same team, raising construction/contamination questions
- no independent replication of the reported margins
- abstract does not give benchmark labeling/query-source methodology in detail

<sub>selected: score · criteria: C1 3/3 · C2 3/3 · C3 3/3 · C4 2/3 · C5 0/3 · flags: methods_paper · verified 2026-08-27 via openalex, arxiv</sub>

## 4. PaSa: An LLM Agent for Comprehensive Academic Paper Search

Yichen He, Guanhua Huang, Peiyuan Feng, Yuan Lin et al. · 2025 · Annual Meeting of the Association for Computational Linguistics · experimental · overall 3/3

<https://doi.org/10.48550/arxiv.2501.10120>

**Key finding.** PaSa-7B surpasses the best Google-based baseline (Google + GPT-4o paraphrasing) by 37.78% in recall@20 and 39.90% in recall@50 on RealScholarQuery, and exceeds a prompted GPT-4o agent by 30.36% in recall.

**Why it made the cut.** foundational · selected by score · strongest on C1 baseline recall ceiling (3/3). Seminal agentic academic paper-search system with explicit baseline comparisons and transparent benchmark construction — the closest prior work to the brief's core question.

**Why it matters here.** Establishes an explicit baseline recall ceiling for single-query search-engine approaches against which agentic gains are measured, and is the closest prior work defining the benchmark-construction pattern (synthetic + real query sets) this literature repeatedly reuses.

**Method.** RL-trained LLM agent that iteratively invokes search tools, reads papers, and selects references; trained on synthetic AutoScholarQuery (35k queries) and evaluated on the real-world RealScholarQuery benchmark.

**Limitations.**

- Trained on synthetic data which may not fully represent real query distributions
- Recall@k gains measured against specific baselines that may not generalize to other retrieval backends

<sub>selected: score · criteria: C1 3/3 · C2 2/3 · C3 2/3 · C4 3/3 · C5 1/3 · flags: methods_paper · verified 2026-08-27 via openalex, arxiv</sub>

## 5. Structurally-bounded Agentic Graph Exploration for Evidence-Grounded Scholarly DeepSearch

Rima Hazra, Sayan Layek, Somnath Banerjee, Soumen Chakrabarti et al. · 2026 · arXiv · experimental · overall 3/3

<https://doi.org/10.48550/arxiv.2608.24809>

**Key finding.** Crase, a bounded citation-graph-expansion agent with entailment-based edge pruning and recency-aware random-walk ranking, outperforms deep research agents built on proprietary models by up to 3x recall@50 at roughly a third of the cost on LitSearch and one further benchmark.

**Why it made the cut.** design-changing · selected by score · strongest on C2 agentic mechanism gain (3/3). A concrete, bounded agentic design attributing gains specifically to citation-graph traversal rather than to open-ended search as an undifferentiated whole.

**Why it matters here.** Isolates citation-graph traversal, with an explicit stopping condition, as the mechanism producing a large quantified recall gain over open-ended agentic search — direct, well-decomposed evidence for which agentic move carries the improvement (Q2).

**Method.** Single seed search, 1.5-hop citation-neighborhood expansion, entailment-based pruning, and random-walk ranking over a 500K-paper arXiv corpus.

**Limitations.**

- Evaluated on a fixed 500K-paper arXiv corpus, may not generalize to broader multi-source corpora
- Comparison baselines are proprietary deep research agents, not single-query database search directly

<sub>selected: score · criteria: C1 2/3 · C2 3/3 · C3 3/3 · C4 1/3 · C5 1/3 · flags: methods_paper · verified 2026-08-27 via arxiv</sub>

## 6. Patience is all you need! An agentic system for performing scientific literature review

David W. Brett, Anniek Myatt · 2025 · arXiv.org · experimental · overall 3/3

<https://doi.org/10.48550/arxiv.2504.08752>

**Key finding.** A keyword-based (sparse) search-and-distillation system achieves results close to state-of-the-art on biology literature-review benchmarks without dense retrieval, and also increases coverage of relevant documents.

**Why it made the cut.** contradicting · selected by score · strongest on C1 baseline recall ceiling (3/3). Directly challenges the assumption that dense retrieval (and its agentic scaffolding) is required to reach strong recall, bearing on the recall-ceiling question.

**Why it matters here.** Pushes against the premise that dense/agentic retrieval infrastructure is needed for strong literature-review coverage, informing both the recall-ceiling question and where reported agentic gains may not hold up.

**Method.** LLM-based search-and-distillation system evaluated against biology-related questions drawn from existing literature benchmarks; sparse vs dense retrieval compared directly.

**Limitations.**

- biology domain only
- abstract gives no explicit numeric recall/precision figures, only relative comparison to 'state of the art'

<sub>selected: score · criteria: C1 3/3 · C2 1/3 · C3 3/3 · C4 1/3 · C5 2/3 · flags: contradicts · verified 2026-08-27 via openalex, arxiv</sub>

## 7. OpenScholar: Synthesizing Scientific Literature with Retrieval-augmented LMs

Akari Asai, Jacqueline He, Rulin Shao, Weijia Shi et al. · 2024 · arXiv.org · experimental · overall 3/3

<https://doi.org/10.48550/arxiv.2411.14199>

**Key finding.** OpenScholar-8B outperforms GPT-4o by 5% and PaperQA2 by 7% in correctness on ScholarQABench, while GPT-4o hallucinates citations 78-90% of the time versus near-human citation accuracy for OpenScholar.

**Why it made the cut.** closely-related · selected by score · strongest on C3 retrieval/reranking method (3/3). Closest prior work to the exact system-plus-benchmark question the brief is asking, with concrete comparison numbers against a leading closed model and a literature-QA competitor.

**Why it matters here.** The flagship system-plus-benchmark pairing the brief is scanning for: shows what a specific retrieval+self-feedback design adds over a closed-book LLM and over a competing literature-QA agent, with a multi-domain benchmark-construction template.

**Method.** Retrieval-augmented LM over a 45-million open-access-paper datastore with a self-feedback inference loop; evaluated on ScholarQABench (2,967 expert-written queries, 208 long-form answers across CS, physics, neuroscience, biomedicine) plus human preference studies.

**Limitations.**

- benchmark self-constructed by the same group that built the system, risking favorable framing
- abstract does not isolate which component (retriever vs self-feedback loop) drives the measured gain

<sub>selected: score · criteria: C1 2/3 · C2 2/3 · C3 3/3 · C4 3/3 · C5 0/3 · flags: methods_paper · verified 2026-08-27 via openalex, arxiv</sub>

## 8. Fact, Fetch, and Reason: A Unified Evaluation of Retrieval-Augmented Generation

Satyapriya Krishna, Kalpesh Krishna, Anhad Mohananey, S. Schwarcz et al. · 2024 · North American Chapter of the Association for Computational Linguistics · experimental · overall 3/3

<https://doi.org/10.48550/arxiv.2409.12941>

**Key finding.** State-of-the-art LLMs achieve only 0.40 accuracy on FRAMES's multi-hop questions with no retrieval, rising to 0.66 (>50% relative improvement) with a proposed multi-step retrieval pipeline.

**Why it made the cut.** closely-related · selected by backfill · strongest on C1 baseline recall ceiling (3/3). One of the few sources with an explicit no-retrieval baseline number set directly against a multi-step retrieval gain.

**Why it matters here.** Provides a clean no-retrieval baseline and quantifies exactly how much a multi-step retrieval approach adds over it, the recall-ceiling-versus-gain comparison the brief's first two questions need.

**Method.** FRAMES benchmark of challenging multi-hop, multi-source questions; baseline no-retrieval performance compared against a multi-step retrieval pipeline.

**Limitations.**

- the multi-step pipeline is not decomposed into reformulation vs graph traversal vs crawling, so the specific carrying mechanism is not isolated
- abstract does not detail query-source or relevance-labeling methodology

<sub>selected: backfill · criteria: C1 3/3 · C2 2/3 · C3 2/3 · C4 3/3 · C5 0/3 · flags: methods_paper · verified 2026-08-27 via openalex, arxiv</sub>

## 9. LitSearch: A Retrieval Benchmark for Scientific Literature Search

Anirudh Ajith, Mengzhou Xia, Alexis Chevalier, Tanya Goyal et al. · 2024 · Conference on Empirical Methods in Natural Language Processing · experimental · overall 3/3

<https://doi.org/10.48550/arxiv.2407.18940>

**Key finding.** LitSearch shows a 24.8% absolute recall@5 gap between BM25 and state-of-the-art dense retrievers, with LLM-based reranking adding a further 4.4% improvement, while commercial search engines lag the best dense retriever by 32 points.

**Why it made the cut.** foundational · selected by backfill · strongest on C1 baseline recall ceiling (3/3). The clearest existing measurement of the single-query recall ceiling and a precedent for constructing literature-search benchmarks with expert-verified queries.

**Why it matters here.** Directly sets the single-query baseline recall ceiling (BM25 vs dense) that any agentic gain must be measured against, and shows current commercial search performing far below dense retrieval, the anchor comparison for the brief's first question.

**Method.** 597 literature-search queries built from GPT-4-generated questions on citation-context paragraphs plus author-written questions about their own papers, expert-verified; benchmarks dense/sparse retrievers, rerankers, and commercial search engines.

**Limitations.**

- restricted to ML/NLP papers
- evaluates static retrieval only, not agentic iteration or graph traversal

<sub>selected: backfill · criteria: C1 3/3 · C2 0/3 · C3 3/3 · C4 3/3 · C5 1/3 · flags: methods_paper · verified 2026-08-27 via openalex, arxiv</sub>

## 10. Deep Research Agents: A Systematic Examination And Roadmap

Yuxuan Huang, Yihang Chen, Haozhen Zhang, Kang Li et al. · 2025 · arXiv.org · other · overall 3/3

<https://doi.org/10.48550/arxiv.2506.18096>

**Key finding.** The survey's taxonomy differentiates static vs. dynamic Deep Research workflows and single- vs. multi-agent architectures, and critically identifies benchmark limitations including restricted external-knowledge access, sequential-execution inefficiencies, and misalignment between evaluation metrics and practical DR objectives.

**Why it made the cut.** closely-related · selected by review · strongest on C4 benchmark construction (3/3). The synthesis/roadmap paper mapping DR-agent architectures and critically evaluating benchmark limitations, useful orientation across all four of the brief's questions and the guaranteed review-slot candidate.

**Why it matters here.** Provides the field-level map of architectural components (retrieval strategy, tool use, planning) and a structured critique of current benchmarks' limitations — directly bearing on the benchmark-construction question (Q3) and flagging where reported gains may be measured against misaligned metrics.

**Method.** Narrative/systematic examination of Deep Research agent architectures, information-acquisition strategies, tool-use frameworks, and benchmarks. Abstract-only for full methodology detail.

**Limitations.**

- Narrative review rather than a systematic-protocol review; abstract does not detail inclusion criteria
- Descriptive taxonomy without new empirical evidence of its own

<sub>selected: review · criteria: C1 1/3 · C2 2/3 · C3 1/3 · C4 3/3 · C5 2/3 · flags: review · verified 2026-08-27 via arxiv</sub>

## Coverage

| Criterion | Papers kept | Gap round added |
|---|---|---|
| C1 baseline recall ceiling | 26 | +4 |
| C2 agentic mechanism gain | 89 | +5 |
| C3 retrieval/reranking method | 89 | +12 |
| C4 benchmark construction | 69 | +11 |
| C5 gain replication failure | 9 | +3 |

## Alternates

Next in order, not selected:

- [Diagnosing Search Behavior and Failure Modes in Long-Horizon Search Agents](https://doi.org/10.48550/arxiv.2608.01913) (2026) — overall 3/3
- [BRIGHT: A Realistic and Challenging Benchmark for Reasoning-Intensive Retrieval](https://doi.org/10.48550/arxiv.2407.12883) (2024) — overall 3/3
- [Multi-Agent System for Scientific Literature Search and Recommendation](https://doi.org/10.1109/icssas66150.2025.11081082) (2025) — overall 3/3
- [LLM-guided Hierarchical Search for End-to-end Reasoning Intensive Retrieval](https://arxiv.org/abs/2510.13217) (2025) — overall 3/3
- [Deep Research: A Survey of Autonomous Research Agents](https://doi.org/10.48550/arxiv.2508.12752) (2025) — overall 3/3
