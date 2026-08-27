# Evidence scan — p11-t2

Run `/Users/nabergoj/Projects/research-scan/research/experiments/phase14/runs/p11-t2/C/rep1/run` · brief `/Users/nabergoj/Projects/research-scan/research/experiments/phase14/runs/p11-t2/C/rep1/run/brief.md` · rendered 2026-08-26

| # | Paper | Year | Venue | Evidence | Verified |
|---|---|---|---|---|---|
| 1 | [When to use Graphs in RAG: A Comprehensive Analysis for Graph Retrieval-Augmented Generation](https://doi.org/10.48550/arxiv.2506.05690) · 10.48550/arxiv.2506.05690 | 2025 | arXiv.org | computational | yes |
| 2 | [Diagnosing Search Behavior and Failure Modes in Long-Horizon Search Agents](https://doi.org/10.48550/arxiv.2608.01913) · 10.48550/arxiv.2608.01913 | 2026 | arXiv | experimental | yes |
| 3 | [BrowseComp-Plus: A More Fair and Transparent Evaluation Benchmark of Deep-Research Agent](https://doi.org/10.48550/arxiv.2508.06600) · 10.48550/arxiv.2508.06600 | 2025 | arXiv (Cornell University) | experimental | yes |
| 4 | [BRIGHT: A Realistic and Challenging Benchmark for Reasoning-Intensive Retrieval](https://doi.org/10.48550/arxiv.2407.12883) · 10.48550/arxiv.2407.12883 | 2024 | International Conference on Learning Representations | computational | yes |
| 5 | [Structurally-bounded Agentic Graph Exploration for Evidence-Grounded Scholarly DeepSearch](https://doi.org/10.48550/arxiv.2608.24809) · 10.48550/arxiv.2608.24809 | 2026 | arXiv | experimental | yes |
| 6 | [LitSearch: A Retrieval Benchmark for Scientific Literature Search](https://doi.org/10.48550/arxiv.2407.18940) · 10.48550/arxiv.2407.18940 | 2024 | Conference on Empirical Methods in Natural Language Processing | experimental | yes |
| 7 | [Towards Recursive Self-Evolving Agentic Literature Retrieval](https://doi.org/10.48550/arxiv.2605.14306) · 10.48550/arxiv.2605.14306 | 2026 | arXiv | computational | yes |
| 8 | [Deep Research: A Survey of Autonomous Research Agents](https://doi.org/10.48550/arxiv.2508.12752) · 10.48550/arxiv.2508.12752 | 2025 | arXiv.org | other | yes |
| 9 | [Patience is all you need! An agentic system for performing scientific literature review](https://doi.org/10.48550/arxiv.2504.08752) · 10.48550/arxiv.2504.08752 | 2025 | arXiv.org | experimental | yes |
| 10 | [OpenScholar: Synthesizing Scientific Literature with Retrieval-augmented LMs](https://doi.org/10.48550/arxiv.2411.14199) · 10.48550/arxiv.2411.14199 | 2024 | arXiv.org | experimental | yes |

## 1. When to use Graphs in RAG: A Comprehensive Analysis for Graph Retrieval-Augmented Generation

Zhishang Xiang, Chuan-Yu Wu, Qinggang Zhang, Shengyuan Chen et al. · 2025 · arXiv.org · computational · overall 3/3

<https://doi.org/10.48550/arxiv.2506.05690>

**Key finding.** GraphRAG frequently underperforms vanilla RAG on real-world tasks; GraphRAG-Bench systematically maps the conditions (fact retrieval, complex reasoning, summarization, creative generation) under which graph-structured retrieval does or does not surpass vector-only RAG.

**Why it made the cut.** contradicting · selected by score · strongest on C2 agentic mechanism gain (3/3). The clearest available evidence that graph-based retrieval — the mechanism class citation-graph traversal belongs to — does not reliably beat a vanilla single-query retrieval baseline, directly bearing on the brief's central premise.

**Why it matters here.** Directly evidences the brief's question 4: a graph-based retrieval mechanism structurally analogous to citation-graph traversal often fails to beat a plain vector-search baseline, showing exactly the kind of gain that does not survive scrutiny across settings.

**Method.** Introduces a comprehensive benchmark with tasks of increasing difficulty and evaluates the full GraphRAG pipeline (graph construction, retrieval, generation) against vanilla RAG baselines.

**Limitations.**

- General-purpose knowledge graphs rather than academic citation graphs
- not literature-search specific
- abstract-only

<sub>selected: score · criteria: C1 2/3 · C2 3/3 · C3 3/3 · C4 3/3 · C5 3/3 · flags: contradicts, methods_paper · verified 2026-08-26 via openalex, arxiv</sub>

## 2. Diagnosing Search Behavior and Failure Modes in Long-Horizon Search Agents

Qi Liu, Jiaxin Mao, Fengbin Zhu, Tat-Seng Chua · 2026 · arXiv · experimental · overall 3/3

<https://doi.org/10.48550/arxiv.2608.01913>

**Key finding.** Search effort and answer quality are only weakly correlated; answer accuracy tracks cumulative retrieval recall more than the number of searches, and the best agents issue far fewer redundant queries.

**Why it made the cut.** contradicting · selected by score · strongest on C2 agentic mechanism gain (3/3). Directly answers decision 4 (where agentic gains fail to hold) and decision 2 (which specific moves carry the gain) with trajectory-level evidence.

**Why it matters here.** Directly challenges the premise that heavier agentic search (more queries, more context) reliably improves outcomes; shows the gain often comes from early evidence rather than the loop itself, reshaping what should be measured (retrieval recall, stopping criteria) instead of raw agentic effort.

**Method.** Trajectory-level diagnosis of six deep search agents on BrowseComp-Plus and BrowseComp, using human-annotated document relevance judgments to decompose retrieval gaps from utilization gaps.

**Limitations.**

- Evaluated on only two benchmarks (BrowseComp-Plus, BrowseComp)
- Retrieval model and harness held fixed, limiting generalization to other retrieval backends

<sub>selected: score · criteria: C1 2/3 · C2 3/3 · C3 1/3 · C4 2/3 · C5 3/3 · flags: contradicts · verified 2026-08-26 via openalex, arxiv</sub>

## 3. BrowseComp-Plus: A More Fair and Transparent Evaluation Benchmark of Deep-Research Agent

Zijian Chen, Xueguang Ma, Shengyao Zhuang, Ping Nie et al. · 2025 · arXiv (Cornell University) · experimental · overall 3/3

<https://doi.org/10.48550/arxiv.2508.06600>

**Key finding.** On a fixed, human-verified corpus, Search-R1 with BM25 achieves only 3.86% accuracy versus 55.9% for GPT-5, and pairing GPT-5 with a stronger embedding retriever (Qwen3-Embedding-8B) raises accuracy to 70.1% with fewer search calls.

**Why it made the cut.** foundational · selected by score · strongest on C1 baseline recall ceiling (3/3). Foundational benchmark-construction paper providing the disentangled baseline-recall data point (C1) and the construction methodology (C4) much of this literature depends on.

**Why it matters here.** Establishes the disentangled baseline recall/accuracy ceiling (BM25 vs. stronger embedding retrievers) against which agentic gains must be measured, and is the exact benchmark-construction precedent later work (e.g., the ClimbMix projection) builds on and critiques.

**Method.** Introduces a fixed, curated corpus derived from BrowseComp with human-verified supporting documents and mined hard negatives, enabling controlled, reproducible comparison of deep-research agents and retrievers.

**Limitations.**

- Corpus derived from the benchmark's own queries, later shown to bias results (see follow-up projection work)
- ~100K documents, smaller than open-web scale

<sub>selected: score · criteria: C1 3/3 · C2 1/3 · C3 2/3 · C4 3/3 · C5 1/3 · flags: methods_paper · verified 2026-08-26 via openalex, arxiv</sub>

## 4. BRIGHT: A Realistic and Challenging Benchmark for Reasoning-Intensive Retrieval

Hongjin Su, Howard Yen, Mengzhou Xia, Weijia Shi et al. · 2024 · International Conference on Learning Representations · computational · overall 3/3

<https://doi.org/10.48550/arxiv.2407.12883>

**Key finding.** State-of-the-art dense retrievers collapse on reasoning-intensive queries: the leading MTEB model scores 59.0 nDCG@10 on standard benchmarks but only 18.3 on BRIGHT, while explicit query reasoning recovers up to 12.2 points.

**Why it made the cut.** foundational · selected by score · strongest on C1 baseline recall ceiling (3/3). Establishes the single-query dense-retrieval recall ceiling on reasoning-intensive queries using the same class of embedding retrievers agentic literature-search baselines rely on, directly answering the brief's top-priority C1 question.

**Why it matters here.** Directly measures the recall ceiling of single-query dense retrieval on the kind of reasoning-heavy queries agentic literature-search systems are meant to handle — the exact C1 baseline number the brief says everything else must be anchored against.

**Method.** Introduces a 1,384-query benchmark spanning economics, psychology, mathematics, and coding drawn from naturally occurring human data, and evaluates state-of-the-art retrieval models against it.

**Limitations.**

- Domains are general reasoning topics, not scientific literature search specifically
- does not evaluate full agentic literature-search pipelines
- dataset snapshot is from 2024

<sub>selected: score · criteria: C1 3/3 · C2 1/3 · C3 2/3 · C4 3/3 · C5 1/3 · flags: methods_paper · verified 2026-08-26 via openalex, arxiv</sub>

## 5. Structurally-bounded Agentic Graph Exploration for Evidence-Grounded Scholarly DeepSearch

Rima Hazra, Sayan Layek, Somnath Banerjee, Soumen Chakrabarti et al. · 2026 · arXiv · experimental · overall 3/3

<https://doi.org/10.48550/arxiv.2608.24809>

**Key finding.** Crase's bounded citation-graph exploration (seed search, 1.5-hop citation expansion, entailment pruning, recency-aware ranking) outperforms proprietary deep-research agents by up to 3x recall@50 at roughly a third of the cost.

**Why it made the cut.** design-changing · selected by score · strongest on C2 agentic mechanism gain (3/3). Directly evaluates a specific agentic mechanism (citation-graph traversal) against alternative agentic designs on a literature-search benchmark, core to decisions 1-3.

**Why it matters here.** Isolates citation-graph traversal as the specific mechanism carrying the reported gain over open-ended agentic search loops, directly answering decision 2 and suggesting a cheaper bounded design as the default rather than an unconstrained agent loop.

**Method.** System paper: single seed query, 1.5-hop citation-graph expansion, entailment-based edge pruning, recency-aware random-walk ranking; evaluated on LitSearch and a further benchmark over a 500K-paper arXiv corpus.

**Limitations.**

- Only two benchmarks evaluated
- Compared against 'deep research agents' as a class rather than a matched single-query baseline

<sub>selected: score · criteria: C1 1/3 · C2 3/3 · C3 3/3 · C4 2/3 · C5 1/3 · flags: methods_paper · verified 2026-08-26 via arxiv</sub>

## 6. LitSearch: A Retrieval Benchmark for Scientific Literature Search

Anirudh Ajith, Mengzhou Xia, Alexis Chevalier, Tanya Goyal et al. · 2024 · Conference on Empirical Methods in Natural Language Processing · experimental · overall 3/3

<https://doi.org/10.48550/arxiv.2407.18940>

**Key finding.** On the 597-query LitSearch benchmark, there is a 24.8% absolute recall@5 gap between BM25 and state-of-the-art dense retrievers, LLM-based reranking improves the best dense retriever by a further 4.4%, and commercial tools like Google Search lag the best dense retriever by 32 points.

**Why it made the cut.** foundational · selected by score · strongest on C1 baseline recall ceiling (3/3). The precedent literature-search retrieval benchmark giving concrete single-query baseline recall numbers and a documented construction methodology that later agentic systems and benchmarks argue against.

**Why it matters here.** Supplies the exact baseline recall-ceiling numbers (BM25 vs dense vs commercial search) decision 1 needs as the anchor point, plus a documented benchmark-construction recipe (source, labeling, expert review) for decision 3.

**Method.** New retrieval benchmark built from GPT-4-generated questions over cited paragraphs plus author-written questions about their own recent papers, expert-reviewed, benchmarking BM25, dense retrievers, LLM rerankers, and commercial search engines.

**Limitations.**

- restricted to recent ML/NLP papers, not the full scientific literature
- evaluates retrieval only, not full agentic reformulation/graph-traversal/crawling pipelines

<sub>selected: score · criteria: C1 3/3 · C2 0/3 · C3 3/3 · C4 3/3 · C5 1/3 · verified 2026-08-26 via openalex, arxiv</sub>

## 7. Towards Recursive Self-Evolving Agentic Literature Retrieval

Yuwen Du, Tian Jin, Jing Kang, Xianghe Pang et al. · 2026 · arXiv · computational · overall 3/3

<https://doi.org/10.48550/arxiv.2605.14306>

**Key finding.** PaSaMaster achieves 16.5x higher F1 than Google Scholar and 37.8% higher F1 than GPT-5.2 at about 1% of the cost, reducing source hallucination from 32.66% to zero, across 38 disciplines in PaSaMaster-Bench.

**Why it made the cut.** design-changing · selected by score · strongest on C1 baseline recall ceiling (3/3). Reports a quantified agentic-vs-single-query-baseline comparison (Google Scholar) and attributes gains to a specific self-evolving retrieval mechanism, squarely answering the brief's top two questions.

**Why it matters here.** Directly anchors the brief's C1 question by benchmarking against Google Scholar as the single-query search baseline and quantifying how much of the reported gain persists relative to it, while also isolating self-evolving retrieval as the mechanism driving improvement.

**Method.** Recursive self-evolving agentic retrieval combining LLM-based intent refinement, hallucination-free ranking over verified papers, and cost-efficient planning/retrieval separation; evaluated on a purpose-built 38-discipline benchmark against Google Scholar and GPT-5.2 baselines.

**Limitations.**

- Benchmark (PaSaMaster-Bench) is self-constructed by the same team, raising construction-bias concerns
- abstract gives no failure-mode or replication analysis
- abstract-only

<sub>selected: score · criteria: C1 3/3 · C2 3/3 · C3 2/3 · C4 1/3 · C5 0/3 · flags: methods_paper · verified 2026-08-26 via openalex, arxiv</sub>

## 8. Deep Research: A Survey of Autonomous Research Agents

Wenlin Zhang, Xiaopeng Li, Yingyi Zhang, Pengyue Jia et al. · 2025 · arXiv.org · other · overall 3/3

<https://doi.org/10.48550/arxiv.2508.12752>

**Key finding.** A systematic overview of the deep-research agent pipeline (planning, question developing, web exploration, report generation), categorizing representative methods and benchmarks for each stage and identifying open challenges.

**Why it made the cut.** closely-related · selected by score · strongest on C1 baseline recall ceiling (2/3). The synthesis paper covering the same four-stage pipeline (planning, retrieval/web exploration, synthesis, benchmarks) the brief is scanning for, providing orientation and a review flag for the scan's synthesis requirement.

**Why it matters here.** Gives a synthesized map of which agentic moves and benchmarks the field has already produced for exactly this class of system, letting the scan check decisions 2-4 against the field's own taxonomy rather than one paper's framing.

**Method.** Survey/systematic overview of the deep-research paradigm, abstract-only for methodology detail.

**Limitations.**

- abstract-only, no explicit findings on which single mechanism or benchmark generalizes best
- scope is broader autonomous research agents, not scientific-literature search exclusively

<sub>selected: score · criteria: C1 2/3 · C2 2/3 · C3 2/3 · C4 2/3 · C5 1/3 · flags: review · verified 2026-08-26 via openalex, arxiv</sub>

## 9. Patience is all you need! An agentic system for performing scientific literature review

David W. Brett, Anniek Myatt · 2025 · arXiv.org · experimental · overall 3/3

<https://doi.org/10.48550/arxiv.2504.08752>

**Key finding.** A keyword-based (sparse) retrieval system for scientific literature review achieves results close to state-of-the-art without needing dense retrieval infrastructure, evaluated on biology benchmark questions.

**Why it made the cut.** contradicting · selected by backfill · strongest on C3 retrieval/reranking method (3/3). On-domain agentic scientific-literature-search system directly comparing sparse vs dense retrieval, bearing on the baseline-recall and retrieval-method questions.

**Why it matters here.** Directly undercuts the assumption that dense retrieval or added infrastructure complexity is necessary for a working literature-search agent, which reframes what the baseline comparison in decision 1 should actually be.

**Method.** LLM-based agentic literature search and distillation system evaluated against biology-domain literature benchmarks, comparing sparse (keyword) vs dense retrieval.

**Limitations.**

- single domain (biology) benchmark
- abstract gives no precise recall/precision numbers

<sub>selected: backfill · criteria: C1 2/3 · C2 1/3 · C3 3/3 · C4 1/3 · C5 2/3 · flags: contradicts · verified 2026-08-26 via openalex, arxiv</sub>

## 10. OpenScholar: Synthesizing Scientific Literature with Retrieval-augmented LMs

Akari Asai, Jacqueline He, Rulin Shao, Weijia Shi et al. · 2024 · arXiv.org · experimental · overall 3/3

<https://doi.org/10.48550/arxiv.2411.14199>

**Key finding.** OpenScholar-8B outperforms GPT-4o by 5% and PaperQA2 by 7% in correctness on the newly built ScholarQABench (2,967 expert queries across four domains), while GPT-4o hallucinates citations 78-90% of the time versus OpenScholar's human-level citation accuracy, and experts preferred OpenScholar responses over expert-written ones 51-70% of the time.

**Why it made the cut.** design-changing · selected by backfill · strongest on C4 benchmark construction (3/3). A core scientific-literature-search agentic system with its own purpose-built, expert-labeled multi-domain benchmark and quantified comparisons against named baseline systems.

**Why it matters here.** A directly on-topic system-plus-benchmark pairing that both establishes numeric baselines against named competitor systems and constructs a large expert-labeled evaluation set, bearing on decisions 1, 3, and 4 simultaneously.

**Method.** Retrieval-augmented LM (OpenScholar) built over a 45M-paper datastore with a self-feedback inference loop, evaluated on a newly constructed multi-domain benchmark (ScholarQABench) against GPT-4o and PaperQA2, with human expert evaluation.

**Limitations.**

- citation-accuracy and correctness comparisons rely on the paper's own benchmark and self-reported baselines
- the specific contribution of the self-feedback loop versus the retriever/datastore is only partially disentangled (+12% for GPT-4o variant)

<sub>selected: backfill · criteria: C1 2/3 · C2 2/3 · C3 2/3 · C4 3/3 · C5 0/3 · verified 2026-08-26 via openalex, arxiv</sub>

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

- [Deep Research Agents: A Systematic Examination And Roadmap](https://doi.org/10.48550/arxiv.2506.18096) (2025) — overall 3/3
- [Projecting BrowseComp-Plus onto ClimbMix: Toward More Realistic Corpora for Agentic Search](https://arxiv.org/abs/2608.20317) (2026) — overall 3/3
- [PaSa: An LLM Agent for Comprehensive Academic Paper Search](https://doi.org/10.48550/arxiv.2501.10120) (2025) — overall 3/3
- [CG-RAG: Research Question Answering by Citation Graph Retrieval-Augmented LLMs](https://doi.org/10.1145/3726302.3729920) (2025) — overall 3/3
- [Multi-Agent System for Scientific Literature Search and Recommendation](https://doi.org/10.1109/icssas66150.2025.11081082) (2025) — overall 3/3
