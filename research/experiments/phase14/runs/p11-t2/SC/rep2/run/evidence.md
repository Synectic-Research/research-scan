# Evidence scan — p11-t2

Run `/Users/nabergoj/Projects/research-scan/research/experiments/phase14/runs/p11-t2/SC/rep2/run` · brief `/Users/nabergoj/Projects/research-scan/research/experiments/phase14/runs/p11-t2/SC/rep2/run/brief.md` · rendered 2026-08-26

| # | Paper | Year | Venue | Evidence | Verified |
|---|---|---|---|---|---|
| 1 | [When to use Graphs in RAG: A Comprehensive Analysis for Graph Retrieval-Augmented Generation](https://doi.org/10.48550/arxiv.2506.05690) · 10.48550/arxiv.2506.05690 | 2025 | arXiv.org | experimental | yes |
| 2 | [PaSa: An LLM Agent for Comprehensive Academic Paper Search](https://doi.org/10.48550/arxiv.2501.10120) · 10.48550/arxiv.2501.10120 | 2025 | Annual Meeting of the Association for Computational Linguistics | experimental | yes |
| 3 | [Diagnosing Search Behavior and Failure Modes in Long-Horizon Search Agents](https://doi.org/10.48550/arxiv.2608.01913) · 10.48550/arxiv.2608.01913 | 2026 | arXiv | experimental | yes |
| 4 | [BrowseComp-Plus: A More Fair and Transparent Evaluation Benchmark of Deep-Research Agent](https://doi.org/10.48550/arxiv.2508.06600) · 10.48550/arxiv.2508.06600 | 2025 | arXiv (Cornell University) | experimental | yes |
| 5 | [Deep Research Agents: A Systematic Examination And Roadmap](https://doi.org/10.48550/arxiv.2506.18096) · 10.48550/arxiv.2506.18096 | 2025 | arXiv.org | other | yes |
| 6 | [Projecting BrowseComp-Plus onto ClimbMix: Toward More Realistic Corpora for Agentic Search](https://arxiv.org/abs/2608.20317) | 2026 | — | experimental | yes |
| 7 | [Towards Recursive Self-Evolving Agentic Literature Retrieval](https://doi.org/10.48550/arxiv.2605.14306) · 10.48550/arxiv.2605.14306 | 2026 | arXiv | experimental | yes |
| 8 | [LitSearch: A Retrieval Benchmark for Scientific Literature Search](https://doi.org/10.48550/arxiv.2407.18940) · 10.48550/arxiv.2407.18940 | 2024 | Conference on Empirical Methods in Natural Language Processing | experimental | yes |
| 9 | [Structurally-bounded Agentic Graph Exploration for Evidence-Grounded Scholarly DeepSearch](https://doi.org/10.48550/arxiv.2608.24809) · 10.48550/arxiv.2608.24809 | 2026 | arXiv | experimental | yes |
| 10 | [OpenScholar: Synthesizing Scientific Literature with Retrieval-augmented LMs](https://doi.org/10.48550/arxiv.2411.14199) · 10.48550/arxiv.2411.14199 | 2024 | arXiv.org | experimental | yes |

## 1. When to use Graphs in RAG: A Comprehensive Analysis for Graph Retrieval-Augmented Generation

Zhishang Xiang, Chuan-Yu Wu, Qinggang Zhang, Shengyuan Chen et al. · 2025 · arXiv.org · experimental · overall 3/3

<https://doi.org/10.48550/arxiv.2506.05690>

**Key finding.** GraphRAG frequently underperforms vanilla RAG on real-world tasks; GraphRAG-Bench systematically maps when graph structure actually helps versus not, across fact retrieval, complex reasoning, summarization, and creative generation.

**Why it made the cut.** contradicting · selected by score · strongest on C2 agentic mechanism gain (3/3). The strongest available evidence in this batch that a core agentic mechanism (graph traversal) fails to generalize — exactly the gain-replication-failure evidence the brief prioritizes.

**Why it matters here.** Directly answers the brief's fourth question for the citation-graph-traversal mechanism specifically: the graph-based retrieval move agentic literature-search systems rely on does not reliably beat plain retrieval, and supplies a benchmark-construction template for testing when it does.

**Method.** New benchmark (GraphRAG-Bench) with tasks of increasing difficulty and full-pipeline evaluation (graph construction, retrieval, generation), used to compare GraphRAG against vanilla RAG.

**Limitations.**

- general-domain RAG tasks rather than scientific-literature corpora specifically
- graph is a constructed knowledge graph, not necessarily a citation graph

<sub>selected: score · criteria: C1 2/3 · C2 3/3 · C3 2/3 · C4 3/3 · C5 3/3 · flags: contradicts · verified 2026-08-26 via openalex, arxiv</sub>

## 2. PaSa: An LLM Agent for Comprehensive Academic Paper Search

Yichen He, Guanhua Huang, Peiyuan Feng, Yuan Lin et al. · 2025 · Annual Meeting of the Association for Computational Linguistics · experimental · overall 3/3

<https://doi.org/10.48550/arxiv.2501.10120>

**Key finding.** PaSa-7B outperforms the best Google-based baseline by 37.78% in recall@20 and 39.90% in recall@50 on RealScholarQuery, and beats PaSa-GPT-4o by 30.36% in recall and 4.25% in precision.

**Why it made the cut.** foundational · selected by score · strongest on C1 baseline recall ceiling (3/3). Closest prior work on agentic academic paper search with explicit recall gains over single-query baselines and a documented benchmark-construction methodology.

**Why it matters here.** The closest published exemplar of an agentic academic-search system with quantified gains over single-query search baselines, and the benchmark-construction template (synthetic + real query sets) other systems in this scan are measured against.

**Method.** RL-trained LLM agent that invokes search tools, reads papers, and selects citations; trained on synthetic AutoScholarQuery (35k queries) and evaluated on a newly constructed real-world benchmark, RealScholarQuery.

**Limitations.**

- Baselines rely on Google/Google Scholar rather than dedicated embedding or BM25 retrievers
- Synthetic training data may not transfer perfectly to real queries, as the paper's own comparison hints

<sub>selected: score · criteria: C1 3/3 · C2 3/3 · C3 2/3 · C4 3/3 · C5 0/3 · flags: methods_paper · verified 2026-08-26 via openalex, arxiv</sub>

## 3. Diagnosing Search Behavior and Failure Modes in Long-Horizon Search Agents

Qi Liu, Jiaxin Mao, Fengbin Zhu, Tat-Seng Chua · 2026 · arXiv · experimental · overall 3/3

<https://doi.org/10.48550/arxiv.2608.01913>

**Key finding.** Across six agents on BrowseComp-Plus (validated on BrowseComp), answer accuracy correlates with cumulative retrieval recall rather than number of searches or context consumed, and the best-performing agents issue far fewer redundant reformulated queries.

**Why it made the cut.** plan-influencing · selected by score · strongest on C2 agentic mechanism gain (3/3). Provides the clearest mechanistic account of which agentic behaviors (evidence quality vs. search volume) actually carry the reported gains, bearing directly on Q2 and Q4.

**Why it matters here.** Directly undermines the assumption that more search effort (via reformulation/iterative crawling) drives agentic gains \u2014 it is retrieved-evidence quality, not search quantity, that predicts accuracy, reshaping what the scan should measure when comparing agentic designs to baselines.

**Method.** Trajectory-level diagnostic study using human-annotated document relevance judgments to decompose agent failures into retrieval gaps vs. utilization gaps; retrieval model and evaluation harness held fixed across six deep-search agents.

**Limitations.**

- Evaluated on BrowseComp/BrowseComp-Plus web-search-style QA rather than academic-literature corpora specifically
- Only six agents studied, not exhaustive of the design space

<sub>selected: score · criteria: C1 2/3 · C2 3/3 · C3 1/3 · C4 2/3 · C5 2/3 · flags: contradicts · verified 2026-08-26 via openalex, arxiv</sub>

## 4. BrowseComp-Plus: A More Fair and Transparent Evaluation Benchmark of Deep-Research Agent

Zijian Chen, Xueguang Ma, Shengyao Zhuang, Ping Nie et al. · 2025 · arXiv (Cornell University) · experimental · overall 3/3

<https://doi.org/10.48550/arxiv.2508.06600>

**Key finding.** On a fixed, human-verified corpus, Search-R1 with BM25 achieves only 3.86% accuracy, GPT-5 alone reaches 55.9%, and GPT-5 with the Qwen3-Embedding-8B retriever reaches 70.1% with fewer search calls, showing retriever choice alone accounts for large swings in deep-research performance.

**Why it made the cut.** foundational · selected by score · strongest on C1 baseline recall ceiling (3/3). The benchmark-construction and baseline-recall precedent this literature (including three other shortlisted papers) evaluates against; without it the scan's comparisons are unanchored.

**Why it matters here.** Establishes the field's reference benchmark for disentangling retriever quality from agent reasoning quality \u2014 the baseline recall ceiling this scan needs to anchor claimed agentic gains against, and the benchmark precedent several other shortlisted papers evaluate on.

**Method.** Benchmark-construction paper: derives BrowseComp-Plus from BrowseComp with a fixed corpus, human-verified supporting documents and mined hard negatives, enabling controlled retriever/agent disentanglement.

**Limitations.**

- Corpus and negatives were both selected per query from BrowseComp's own supporting documents, a construction limitation later work in this batch (dc6612fba47a) shows inflates evidence recall

<sub>selected: score · criteria: C1 3/3 · C2 1/3 · C3 2/3 · C4 3/3 · C5 1/3 · flags: methods_paper · verified 2026-08-26 via openalex, arxiv</sub>

## 5. Deep Research Agents: A Systematic Examination And Roadmap

Yuxuan Huang, Yihang Chen, Haozhen Zhang, Kang Li et al. · 2025 · arXiv.org · other · overall 3/3

<https://doi.org/10.48550/arxiv.2506.18096>

**Key finding.** A systematic taxonomy of Deep Research agent architectures (static vs. dynamic workflows, single- vs. multi-agent) and a critical review finding current benchmarks suffer from restricted external-knowledge access, sequential execution inefficiencies, and metric-objective misalignment.

**Why it made the cut.** foundational · selected by score · strongest on C4 benchmark construction (3/3). The synthesis/roadmap paper providing the taxonomy and benchmark critique framework the rest of this batch's individual findings should be situated within.

**Why it matters here.** Supplies the field-level orientation and an explicit critique of benchmark limitations that the brief's benchmark-construction and gain-replication questions need \u2014 a synthesis against which individual system and benchmark claims in this scan should be read.

**Method.** Narrative systematic review/taxonomy of Deep Research agent literature; qualitative synthesis rather than new experiments. Abstract-only for specific evidence.

**Limitations.**

- Narrative review, not a registered systematic-review protocol
- Abstract gives no quantitative findings of its own

<sub>selected: score · criteria: C1 2/3 · C2 2/3 · C3 1/3 · C4 3/3 · C5 2/3 · flags: review · verified 2026-08-26 via arxiv</sub>

## 6. Projecting BrowseComp-Plus onto ClimbMix: Toward More Realistic Corpora for Agentic Search

Sahel Sharifymoghaddam, Lin Gu, Yijun Ge, Jimmy Lin · 2026 · no venue · experimental · overall 3/3

<https://arxiv.org/abs/2608.20317>

**Key finding.** Projecting BrowseComp-Plus's 830 questions onto the independently-built 553M-document ClimbMix corpus yields 57 fully-grounded questions on which the strongest agent's evidence recall falls from 84.3% to 21.4% (losing five points of answer accuracy) while issuing 63% more search calls.

**Why it made the cut.** contradicting · selected by score · strongest on C1 baseline recall ceiling (3/3). The most direct evidence in this batch that a widely-used benchmark's reported gains shrink dramatically under a construction change, exactly the contradiction the brief is asking the scan to surface.

**Why it matters here.** Direct, quantified demonstration that a reported deep-research recall/accuracy result does not survive relocation to a corpus not built around the benchmark's own queries \u2014 precisely the gain-replication-failure evidence the brief's Q4 asks the scan to reach hardest for.

**Method.** Introduces a dataset-agnostic 'projection' pipeline that decomposes questions into atomic reasoning hops, grounds each hop in a new corpus, and retains only hops verified by automatic checks, an independent agent, and human review; applied to BrowseComp-Plus test questions.

**Limitations.**

- Only 57 of 830 questions survive the strict grounding pipeline, a small resulting benchmark
- Single projection target (ClimbMix); generalization to other corpora not yet shown

<sub>selected: score · criteria: C1 3/3 · C2 1/3 · C3 0/3 · C4 3/3 · C5 3/3 · flags: contradicts, methods_paper · verified 2026-08-26 via arxiv, s2</sub>

## 7. Towards Recursive Self-Evolving Agentic Literature Retrieval

Yuwen Du, Tian Jin, Jing Kang, Xianghe Pang et al. · 2026 · arXiv · experimental · overall 3/3

<https://doi.org/10.48550/arxiv.2605.14306>

**Key finding.** PaSaMaster achieves a 16.5x higher F1-score than Google Scholar and 37.8% higher F1-score than GPT-5.2 at about 1% of the cost across 38 disciplines, while reducing source hallucination from 32.66% to zero.

**Why it made the cut.** design-changing · selected by score · strongest on C1 baseline recall ceiling (3/3). Gives a concrete, quantified single-query-baseline-vs-agentic comparison and isolates the mechanism responsible for the gain.

**Why it matters here.** Directly measures the single-query database baseline (Google Scholar) the brief's first question asks for, and attributes the gain to a specific mechanism (self-evolving intent refinement plus planning/retrieval separation) rather than an undifferentiated system.

**Method.** Recursive self-evolving agentic retrieval system separating intent understanding (frontier LLM) from retrieval/scoring (lightweight models); evaluated on a purpose-built 38-discipline benchmark against Google Scholar and GPT-5.2 baselines.

**Limitations.**

- comparison numbers are self-reported by the introducing team with no independent replication
- benchmark construction details (labeling, contamination controls) are only briefly described

<sub>selected: score · criteria: C1 3/3 · C2 3/3 · C3 2/3 · C4 2/3 · C5 0/3 · flags: methods_paper · verified 2026-08-26 via openalex, arxiv</sub>

## 8. LitSearch: A Retrieval Benchmark for Scientific Literature Search

Anirudh Ajith, Mengzhou Xia, Alexis Chevalier, Tanya Goyal et al. · 2024 · Conference on Empirical Methods in Natural Language Processing · experimental · overall 3/3

<https://doi.org/10.48550/arxiv.2407.18940>

**Key finding.** LitSearch finds a 24.8% absolute recall@5 gap between BM25 and state-of-the-art dense retrievers on 597 realistic literature-search queries, with LLM-based reranking improving the best dense retriever by a further 4.4%, and commercial search engines lagging the best dense retriever by 32 points.

**Why it made the cut.** foundational · selected by score · strongest on C1 baseline recall ceiling (3/3). Closest prior work to the brief itself: a purpose-built literature-search retrieval benchmark with explicit construction methodology and quantified baseline recall ceiling, answering both Q1 and Q3 directly.

**Why it matters here.** The single most direct answer to Q1 (concrete sparse-vs-dense recall ceiling numbers) and Q3 (a fully specified query-source and labeling methodology) in the whole shortlist — the benchmark construction precedent the field's later systems (including OpenScholar) are measured against.

**Method.** New retrieval benchmark of 597 literature-search queries built from GPT-4-generated questions over cited paragraphs plus author-written questions about recent papers, expert-vetted; extensive benchmarking of retrieval models, LLM rerankers, and commercial search engines.

**Limitations.**

- restricted to ML/NLP papers, not the full breadth of scientific literature
- 597 queries is a modest sample for generalization claims

<sub>selected: score · criteria: C1 3/3 · C2 0/3 · C3 3/3 · C4 3/3 · C5 1/3 · flags: methods_paper · verified 2026-08-26 via openalex, arxiv</sub>

## 9. Structurally-bounded Agentic Graph Exploration for Evidence-Grounded Scholarly DeepSearch

Rima Hazra, Sayan Layek, Somnath Banerjee, Soumen Chakrabarti et al. · 2026 · arXiv · experimental · overall 3/3

<https://doi.org/10.48550/arxiv.2608.24809>

**Key finding.** Crase, a bounded citation-graph-traversal agent (one seed query + 1.5-hop citation expansion + entailment-based pruning + recency-aware ranking), achieves up to 3x higher recall@50 than deep-research agents built on proprietary models at roughly a third of the cost on LitSearch and a further arXiv-corpus benchmark.

**Why it made the cut.** design-changing · selected by backfill · strongest on C2 agentic mechanism gain (3/3). Directly attributes a large, quantified recall gain to citation-graph traversal specifically, the exact mechanism the brief asks about in Q2, with an explicit cost/recall comparison to undifferentiated agentic search.

**Why it matters here.** Isolates citation-graph traversal as the specific agentic move producing the gain, with an explicit comparison against open-ended search-loop agents \u2014 exactly the mechanism attribution the brief's Q2 asks for, and suggests a bounded design may replace costlier open-ended agents.

**Method.** System design paper; single seed query, fixed citation-graph expansion and pruning, evaluated against open-ended deep-research agents on two literature-search benchmarks over a 500K-paper arXiv corpus.

**Limitations.**

- Compared against proprietary-model deep research agents rather than tuned open baselines
- Evaluated on a single corpus (arXiv) and two benchmarks

<sub>selected: backfill · criteria: C1 2/3 · C2 3/3 · C3 3/3 · C4 1/3 · C5 0/3 · flags: methods_paper · verified 2026-08-26 via arxiv</sub>

## 10. OpenScholar: Synthesizing Scientific Literature with Retrieval-augmented LMs

Akari Asai, Jacqueline He, Rulin Shao, Weijia Shi et al. · 2024 · arXiv.org · experimental · overall 3/3

<https://doi.org/10.48550/arxiv.2411.14199>

**Key finding.** OpenScholar-8B, using a datastore of 45 million open-access papers, outperforms GPT-4o by 5% and PaperQA2 by 7% in correctness on ScholarQABench (2,967 expert-written queries), while GPT-4o hallucinates citations 78-90% of the time versus OpenScholar's near-human citation accuracy.

**Why it made the cut.** foundational · selected by backfill · strongest on C3 retrieval/reranking method (3/3). The most central, directly on-topic system+benchmark pairing in the shortlist, giving concrete comparative numbers against GPT-4o and PaperQA2 that anchor Q1, Q3, and the brief's premise generally.

**Why it matters here.** Central system-plus-benchmark evidence for the whole brief: quantifies both the retrieval/reranking design (C3) and benchmark construction (C4), and is the closest prior work most later agentic literature-search papers will be compared against.

**Method.** Retrieval-augmented LM with self-feedback inference loop; introduces ScholarQABench, a multi-domain literature-search benchmark, and conducts human expert evaluations against GPT-4o and PaperQA2.

**Limitations.**

- datastore limited to open-access papers, missing paywalled literature
- human preference evaluation subject to rater variance
- abstract does not detail contamination controls for ScholarQABench

<sub>selected: backfill · criteria: C1 2/3 · C2 1/3 · C3 3/3 · C4 3/3 · C5 0/3 · flags: methods_paper · verified 2026-08-26 via openalex, arxiv</sub>

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

- [Fact, Fetch, and Reason: A Unified Evaluation of Retrieval-Augmented Generation](https://doi.org/10.48550/arxiv.2409.12941) (2024) — overall 3/3
- [BRIGHT: A Realistic and Challenging Benchmark for Reasoning-Intensive Retrieval](https://doi.org/10.48550/arxiv.2407.12883) (2024) — overall 3/3
- [LLM-guided Hierarchical Search for End-to-end Reasoning Intensive Retrieval](https://arxiv.org/abs/2510.13217) (2025) — overall 3/3
- [Patience is all you need! An agentic system for performing scientific literature review](https://doi.org/10.48550/arxiv.2504.08752) (2025) — overall 3/3
- [CG-RAG: Research Question Answering by Citation Graph Retrieval-Augmented LLMs](https://doi.org/10.1145/3726302.3729920) (2025) — overall 3/3
