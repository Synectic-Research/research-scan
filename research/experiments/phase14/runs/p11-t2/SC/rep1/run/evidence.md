# Evidence scan — p11-t2

Run `/Users/nabergoj/Projects/research-scan/research/experiments/phase14/runs/p11-t2/SC/rep1/run` · brief `/Users/nabergoj/Projects/research-scan/research/experiments/phase14/runs/p11-t2/SC/rep1/run/brief.md` · rendered 2026-08-26

| # | Paper | Year | Venue | Evidence | Verified |
|---|---|---|---|---|---|
| 1 | [When to use Graphs in RAG: A Comprehensive Analysis for Graph Retrieval-Augmented Generation](https://doi.org/10.48550/arxiv.2506.05690) · 10.48550/arxiv.2506.05690 | 2025 | arXiv.org | computational | yes |
| 2 | [BrowseComp-Plus: A More Fair and Transparent Evaluation Benchmark of Deep-Research Agent](https://doi.org/10.48550/arxiv.2508.06600) · 10.48550/arxiv.2508.06600 | 2025 | arXiv (Cornell University) | experimental | yes |
| 3 | [BRIGHT: A Realistic and Challenging Benchmark for Reasoning-Intensive Retrieval](https://doi.org/10.48550/arxiv.2407.12883) · 10.48550/arxiv.2407.12883 | 2024 | International Conference on Learning Representations | computational | yes |
| 4 | [OpenScholar: Synthesizing Scientific Literature with Retrieval-augmented LMs](https://doi.org/10.48550/arxiv.2411.14199) · 10.48550/arxiv.2411.14199 | 2024 | arXiv.org | experimental | yes |
| 5 | [Towards Recursive Self-Evolving Agentic Literature Retrieval](https://doi.org/10.48550/arxiv.2605.14306) · 10.48550/arxiv.2605.14306 | 2026 | arXiv | experimental | yes |
| 6 | [LitSearch: A Retrieval Benchmark for Scientific Literature Search](https://doi.org/10.48550/arxiv.2407.18940) · 10.48550/arxiv.2407.18940 | 2024 | Conference on Empirical Methods in Natural Language Processing | experimental | yes |
| 7 | [Diagnosing Search Behavior and Failure Modes in Long-Horizon Search Agents](https://doi.org/10.48550/arxiv.2608.01913) · 10.48550/arxiv.2608.01913 | 2026 | arXiv | experimental | yes |
| 8 | [LLM-guided Hierarchical Search for End-to-end Reasoning Intensive Retrieval](https://arxiv.org/abs/2510.13217) | 2025 | — | experimental | yes |
| 9 | [Multi-Agent System for Scientific Literature Search and Recommendation](https://doi.org/10.1109/icssas66150.2025.11081082) · 10.1109/icssas66150.2025.11081082 | 2025 | — | experimental | yes |
| 10 | [Deep Research Agents: A Systematic Examination And Roadmap](https://doi.org/10.48550/arxiv.2506.18096) · 10.48550/arxiv.2506.18096 | 2025 | arXiv.org | other | yes |

## 1. When to use Graphs in RAG: A Comprehensive Analysis for Graph Retrieval-Augmented Generation

Zhishang Xiang, Chuan-Yu Wu, Qinggang Zhang, Shengyuan Chen et al. · 2025 · arXiv.org · computational · overall 3/3

<https://doi.org/10.48550/arxiv.2506.05690>

**Key finding.** GraphRAG frequently underperforms vanilla RAG on many real-world tasks; GraphRAG-Bench systematically characterizes when graph structure does and does not provide measurable benefit across fact retrieval, complex reasoning, summarization, and creative generation.

**Why it made the cut.** contradicting · selected by score · strongest on C2 agentic mechanism gain (3/3). The most direct contradicting evidence in this batch for whether the graph-traversal agentic move actually beats a plain retrieval baseline, exactly the premise the brief wants tested hardest.

**Why it matters here.** Directly answers the brief's fourth decision question for the citation-graph-traversal mechanism specifically: graph-based retrieval, the analogue of citation-graph traversal in literature-search agents, often fails to beat plain retrieval, undermining the premise that this agentic move reliably carries a gain.

**Method.** New benchmark spanning tasks of increasing difficulty, with systematic evaluation across the full GraphRAG pipeline (construction, retrieval, generation) against vanilla RAG. Abstract-only.

**Limitations.**

- Benchmark targets general knowledge-graph RAG tasks, not scientific literature corpora specifically
- Findings are architecture- and task-dependent, so generalization to literature-search-specific graphs needs separate validation

<sub>selected: score · criteria: C1 2/3 · C2 3/3 · C3 2/3 · C4 3/3 · C5 3/3 · flags: contradicts, methods_paper · verified 2026-08-26 via openalex, arxiv</sub>

## 2. BrowseComp-Plus: A More Fair and Transparent Evaluation Benchmark of Deep-Research Agent

Zijian Chen, Xueguang Ma, Shengyao Zhuang, Ping Nie et al. · 2025 · arXiv (Cornell University) · experimental · overall 3/3

<https://doi.org/10.48550/arxiv.2508.06600>

**Key finding.** On the fixed-corpus BrowseComp-Plus benchmark, Search-R1 with a BM25 retriever reaches only 3.86% accuracy while GPT-5 reaches 55.9%, and pairing GPT-5 with a Qwen3-Embedding retriever raises accuracy to 70.1% with fewer search calls.

**Why it made the cut.** foundational · selected by score · strongest on C1 baseline recall ceiling (3/3). The construction precedent and baseline-recall anchor for deep-research agent evaluation that most later work (including other shortlisted papers) builds on or contests.

**Why it matters here.** The controlled benchmark and baseline numbers (BM25 at under 4% accuracy) this scan needs to anchor any claim of agentic improvement -- without it, reported deep-research gains are measured against opaque, non-reproducible web APIs.

**Method.** Benchmark construction: fixed, curated corpus derived from BrowseComp with human-verified supporting documents and mined hard negatives, enabling disentangled retriever-vs-agent evaluation.

**Limitations.**

- Corpus and negatives are both selected per query from the benchmark's own questions (addressed by later projection work)
- reported baseline is a full deep-research system rather than a pure single-query search step in isolation

<sub>selected: score · criteria: C1 3/3 · C2 2/3 · C3 3/3 · C4 3/3 · C5 1/3 · flags: methods_paper · verified 2026-08-26 via openalex, arxiv</sub>

## 3. BRIGHT: A Realistic and Challenging Benchmark for Reasoning-Intensive Retrieval

Hongjin Su, Howard Yen, Mengzhou Xia, Weijia Shi et al. · 2024 · International Conference on Learning Representations · computational · overall 3/3

<https://doi.org/10.48550/arxiv.2407.12883>

**Key finding.** The leading MTEB retriever (SFR-Embedding-Mistral, 59.0 nDCG@10 on MTEB) scores only 18.3 nDCG@10 on BRIGHT's 1,384 reasoning-intensive real-world queries, while incorporating explicit reasoning about the query improves retrieval performance by up to 12.2 points.

**Why it made the cut.** foundational · selected by score · strongest on C1 baseline recall ceiling (3/3). The clearest quantified demonstration that single-query embedding search collapses on complex queries, a benchmark precedent much reasoning-augmented retrieval work (including literature-search agents) is measured against.

**Why it matters here.** Provides a concrete, widely-cited (182) measurement of how far a strong single-query embedding search baseline falls short on reasoning-intensive queries, and shows explicit reasoning recovers some of that gap -- directly relevant to the brief's first and second decision questions even though the domains tested are not scientific literature.

**Method.** New retrieval benchmark of naturally-occurring, curated reasoning-intensive queries across economics, psychology, mathematics, and coding; evaluates state-of-the-art retrievers and reasoning-augmented retrieval. Abstract-only.

**Limitations.**

- Domains covered (economics, psychology, math, coding) do not include scientific literature search directly
- Gains from added reasoning remain far below the un-degraded MTEB ceiling

<sub>selected: score · criteria: C1 3/3 · C2 2/3 · C3 2/3 · C4 3/3 · C5 1/3 · flags: methods_paper · verified 2026-08-26 via openalex, arxiv</sub>

## 4. OpenScholar: Synthesizing Scientific Literature with Retrieval-augmented LMs

Akari Asai, Jacqueline He, Rulin Shao, Weijia Shi et al. · 2024 · arXiv.org · experimental · overall 3/3

<https://doi.org/10.48550/arxiv.2411.14199>

**Key finding.** OpenScholar-8B outperforms GPT-4o by 5% and PaperQA2 by 7% in correctness on ScholarQABench (2,967 expert queries across four domains), while GPT-4o hallucinates citations 78-90% of the time versus OpenScholar's human-comparable citation accuracy.

**Why it made the cut.** foundational · selected by score · strongest on C1 baseline recall ceiling (3/3). The nearest published system-and-benchmark pairing to the brief's core question, anchoring both the baseline-comparison and benchmark-construction criteria.

**Why it matters here.** The closest prior full system-plus-benchmark combination in the set, giving concrete baseline comparisons (against GPT-4o and PaperQA2) and a detailed benchmark-construction precedent that later literature-search-agent work is measured against.

**Method.** Retrieval-augmented LM over a 45M-paper open-access datastore with a self-feedback inference loop, evaluated on a newly built multi-domain benchmark (ScholarQABench) against expert answers and human preference judgments.

**Limitations.**

- citation numbers are from the abstract only, no independent replication reported here
- benchmark restricted to four domains (CS, physics, neuroscience, biomedicine)

<sub>selected: score · criteria: C1 3/3 · C2 2/3 · C3 3/3 · C4 3/3 · C5 0/3 · flags: methods_paper · verified 2026-08-26 via openalex, arxiv</sub>

## 5. Towards Recursive Self-Evolving Agentic Literature Retrieval

Yuwen Du, Tian Jin, Jing Kang, Xianghe Pang et al. · 2026 · arXiv · experimental · overall 3/3

<https://doi.org/10.48550/arxiv.2605.14306>

**Key finding.** PaSaMaster achieves a 16.5x higher F1-score than Google Scholar and a 37.8% higher F1-score than GPT-5.2 at about 1% of the cost across 38 disciplines in PaSaMaster-Bench, while reducing source hallucination from 32.66% to zero.

**Why it made the cut.** design-changing · selected by score · strongest on C1 baseline recall ceiling (3/3). One of the few systems in this batch reporting a direct, quantified comparison to a single-query database search baseline, the exact anchor the brief's first decision question needs.

**Why it matters here.** Directly anchors the brief's first decision question by benchmarking against Google Scholar as the single-query search baseline, and attributes the measured gain to a specific mechanism — self-evolving retrieval that refines intent from ranked evidence over time.

**Method.** Recursive self-evolving agentic retrieval system combining self-evolving retrieval, hallucination-free ranking over verified papers, and planning/retrieval separation across lightweight and frontier LLMs; evaluated on a purpose-built 38-discipline benchmark against Google Scholar and GPT-5.2. Abstract-only.

**Limitations.**

- Benchmark (PaSaMaster-Bench) is self-constructed; abstract gives no detail on relevance labeling or contamination controls
- Comparison to Google Scholar does not isolate which sub-mechanism drives the gain

<sub>selected: score · criteria: C1 3/3 · C2 3/3 · C3 2/3 · C4 2/3 · C5 0/3 · flags: methods_paper · verified 2026-08-26 via openalex, arxiv</sub>

## 6. LitSearch: A Retrieval Benchmark for Scientific Literature Search

Anirudh Ajith, Mengzhou Xia, Alexis Chevalier, Tanya Goyal et al. · 2024 · Conference on Empirical Methods in Natural Language Processing · experimental · overall 3/3

<https://doi.org/10.48550/arxiv.2407.18940>

**Key finding.** On 597 realistic literature-search queries, state-of-the-art dense retrievers outperform BM25 by 24.8 absolute points in recall@5, LLM reranking adds a further 4.4% over the best dense retriever, and commercial search engines lag the best dense retriever by 32 points.

**Why it made the cut.** foundational · selected by score · strongest on C1 baseline recall ceiling (3/3). The most direct, numerically explicit answer in the set to the baseline recall-ceiling question and a benchmark-construction precedent the field argues from.

**Why it matters here.** Directly establishes the single-query database search recall ceiling (BM25 vs. dense) that the brief's first question asks for, and is the closest thing to a construction precedent for literature-search retrieval benchmarks.

**Method.** New retrieval benchmark (LitSearch) built from GPT-4-generated questions over cited paragraphs plus author-written questions, expert-verified, benchmarked across retrieval models and LLM reranking pipelines.

**Limitations.**

- restricted to recent ML/NLP papers, not broader scientific literature
- abstract-only numbers, no independent replication reported here

<sub>selected: score · criteria: C1 3/3 · C2 1/3 · C3 2/3 · C4 3/3 · C5 1/3 · flags: methods_paper · verified 2026-08-26 via openalex, arxiv</sub>

## 7. Diagnosing Search Behavior and Failure Modes in Long-Horizon Search Agents

Qi Liu, Jiaxin Mao, Fengbin Zhu, Tat-Seng Chua · 2026 · arXiv · experimental · overall 3/3

<https://doi.org/10.48550/arxiv.2608.01913>

**Key finding.** Across six agents on BrowseComp-Plus and BrowseComp, answer accuracy correlates with cumulative retrieval recall far more than with number of searches or context consumed, and the best agents issue far fewer redundant queries.

**Why it made the cut.** plan-influencing · selected by score · strongest on C2 agentic mechanism gain (3/3). Directly answers what agentic moves carry the gain and shows where more searching stops helping -- core to questions 2 and 4.

**Why it matters here.** Directly undercuts the assumption that more search effort (crawling, reformulation volume) drives agentic gains -- the evidence says retrieved-evidence quality, not search quantity, is what matters, redirecting where to look for the agentic 'gain'.

**Method.** Trajectory-level diagnosis using human-annotated document relevance judgments, decomposing failures into retrieval gaps vs. utilization gaps across six deep-search agents on BrowseComp-Plus (validated on BrowseComp with a live web API).

**Limitations.**

- Evaluates existing agents rather than proposing a new mechanism
- relies on human relevance judgments that may not generalize across corpora

<sub>selected: score · criteria: C1 1/3 · C2 3/3 · C3 1/3 · C4 1/3 · C5 3/3 · flags: contradicts · verified 2026-08-26 via openalex, arxiv</sub>

## 8. LLM-guided Hierarchical Search for End-to-end Reasoning Intensive Retrieval

Nilesh Gupta, Wei-Cheng Chang, N. Bui, Cho-Jui Hsieh et al. · 2025 · no venue · experimental · overall 3/3

<https://arxiv.org/abs/2510.13217>

**Key finding.** LATTICE, an LLM-guided hierarchical search index with no embedding model at search time, reaches 46.7 nDCG@10 on the reasoning-intensive BRIGHT benchmark -- matching the best fine-tuned ensemble baseline -- and 49.1 with a lightweight ensemble, while remaining competitive on SciFact and SciDocs.

**Why it made the cut.** closely-related · selected by backfill · strongest on C1 baseline recall ceiling (3/3). Quantifies the recall ceiling of embedding-based single-query retrieval and proposes a hierarchical-traversal alternative -- bears directly on questions 1 and the retrieval-method layer (C3).

**Why it matters here.** Directly quantifies where standard embedding-based top-k retrieval fails for reasoning-intensive queries and offers an alternative retrieval architecture -- bears on both the baseline-ceiling question and the retrieval-method question underneath agentic search.

**Method.** Method paper: top-down LLM-guided construction of a hierarchical document-summary index plus calibrated path-aggregated LLM traversal; evaluated on BRIGHT, NQ, SciFact, SciDocs against fine-tuned and sliding-window-reranking baselines.

**Limitations.**

- Primary benchmark (BRIGHT) is general reasoning-intensive retrieval, not literature-search-specific, though SciFact/SciDocs partially overlap
- reranking baseline is competitive at low token budgets, so LATTICE's advantage is budget-dependent

<sub>selected: backfill · criteria: C1 3/3 · C2 2/3 · C3 3/3 · C4 0/3 · C5 1/3 · flags: methods_paper · verified 2026-08-26 via arxiv, s2</sub>

## 9. Multi-Agent System for Scientific Literature Search and Recommendation

Aswathy K Cherian, Naman Srivastava, Samyak Varia · 2025 · no venue · experimental · overall 3/3

<https://doi.org/10.1109/icssas66150.2025.11081082>

**Key finding.** A multi-agent system with a hybrid BM25+FAISS retrieval strategy achieves an 8.5% precision improvement, 7.3% recall improvement, and ~210ms latency reduction over systems such as PaperQA and Semantic Scholar.

**Why it made the cut.** design-changing · selected by backfill · strongest on C1 baseline recall ceiling (3/3). Quantifies the precision/recall/latency gain attributable to specific agentic components against named literature-search baselines.

**Why it matters here.** Gives concrete, attributable numbers for what a query-reformulation agent plus hybrid retrieval adds over established literature-search baselines, directly answering the brief's first two questions.

**Method.** Three-agent architecture (Query, Retrieval, Learning agents) built on FastAPI with hybrid sparse/dense retrieval, benchmarked against published retrieval systems.

**Limitations.**

- venue unclear/likely non-peer-reviewed, low citation count
- comparison baselines and evaluation set construction not detailed

<sub>selected: backfill · criteria: C1 3/3 · C2 2/3 · C3 3/3 · C4 1/3 · C5 0/3 · flags: methods_paper · verified 2026-08-26 via crossref, openalex</sub>

## 10. Deep Research Agents: A Systematic Examination And Roadmap

Yuxuan Huang, Yihang Chen, Haozhen Zhang, Kang Li et al. · 2025 · arXiv.org · other · overall 3/3

<https://doi.org/10.48550/arxiv.2506.18096>

**Key finding.** A systematic taxonomy of Deep Research agents finds that current benchmarks are limited by restricted external-knowledge access, sequential execution inefficiencies, and misalignment between evaluation metrics and agents' practical objectives.

**Why it made the cut.** foundational · selected by review · strongest on C4 benchmark construction (3/3). The synthesis paper surveying system designs, benchmarks and their limitations across the field -- the review the brief's evidence portfolio needs.

**Why it matters here.** Supplies the field-wide orientation and the explicit critique of benchmark construction (question 3) that individual system papers do not provide, and flags exactly the metric-misalignment problem the brief's question 4 is chasing.

**Method.** Narrative survey/roadmap covering information-acquisition strategies, tool-use frameworks, architecture taxonomy (static/dynamic, single/multi-agent), and critical benchmark evaluation; abstract-only detail on specific numbers.

**Limitations.**

- Narrative review, not a systematic-review protocol
- abstract gives no quantitative results of its own

<sub>selected: review · criteria: C1 1/3 · C2 1/3 · C3 1/3 · C4 3/3 · C5 1/3 · flags: review · verified 2026-08-26 via arxiv</sub>

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

- [Patience is all you need! An agentic system for performing scientific literature review](https://doi.org/10.48550/arxiv.2504.08752) (2025) — overall 3/3
- [Projecting BrowseComp-Plus onto ClimbMix: Toward More Realistic Corpora for Agentic Search](https://arxiv.org/abs/2608.20317) (2026) — overall 3/3
- [PaSa: An LLM Agent for Comprehensive Academic Paper Search](https://doi.org/10.48550/arxiv.2501.10120) (2025) — overall 3/3
- [CG-RAG: Research Question Answering by Citation Graph Retrieval-Augmented LLMs](https://doi.org/10.1145/3726302.3729920) (2025) — overall 3/3
- [Structurally-bounded Agentic Graph Exploration for Evidence-Grounded Scholarly DeepSearch](https://doi.org/10.48550/arxiv.2608.24809) (2026) — overall 3/3
