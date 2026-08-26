# Evidence scan — p11-t2

Run `/Users/nabergoj/Projects/research-scan/research/experiments/phase12-selection/phase12b/runs/p11-t2/R40/O1/rep5/run` · brief `/Users/nabergoj/Projects/research-scan/research/experiments/phase12-selection/phase12b/runs/p11-t2/R40/O1/rep5/run/brief.md` · rendered 2026-08-26

| # | Paper | Year | Venue | Evidence | Verified |
|---|---|---|---|---|---|
| 1 | [Patience is all you need! An agentic system for performing scientific literature review](https://doi.org/10.48550/arxiv.2504.08752) · 10.48550/arxiv.2504.08752 | 2025 | arXiv.org | experimental | yes |
| 2 | [BrowseComp-Plus: A More Fair and Transparent Evaluation Benchmark of Deep-Research Agent](https://doi.org/10.48550/arxiv.2508.06600) · 10.48550/arxiv.2508.06600 | 2025 | arXiv (Cornell University) | experimental | yes |
| 3 | [Projecting BrowseComp-Plus onto ClimbMix: Toward More Realistic Corpora for Agentic Search](https://arxiv.org/abs/2608.20317) | 2026 | — | experimental | yes |
| 4 | [OpenScholar: Synthesizing Scientific Literature with Retrieval-augmented LMs](https://doi.org/10.48550/arxiv.2411.14199) · 10.48550/arxiv.2411.14199 | 2024 | arXiv.org | experimental | yes |
| 5 | [LitSearch: A Retrieval Benchmark for Scientific Literature Search](https://doi.org/10.48550/arxiv.2407.18940) · 10.48550/arxiv.2407.18940 | 2024 | Conference on Empirical Methods in Natural Language Processing | experimental | yes |
| 6 | [Diagnosing Search Behavior and Failure Modes in Long-Horizon Search Agents](https://doi.org/10.48550/arxiv.2608.01913) · 10.48550/arxiv.2608.01913 | 2026 | arXiv | experimental | yes |
| 7 | [Towards Recursive Self-Evolving Agentic Literature Retrieval](https://doi.org/10.48550/arxiv.2605.14306) · 10.48550/arxiv.2605.14306 | 2026 | arXiv | experimental | yes |
| 8 | [Structurally-bounded Agentic Graph Exploration for Evidence-Grounded Scholarly DeepSearch](https://doi.org/10.48550/arxiv.2608.24809) · 10.48550/arxiv.2608.24809 | 2026 | arXiv | experimental | yes |
| 9 | [LLM-guided Hierarchical Search for End-to-end Reasoning Intensive Retrieval](https://arxiv.org/abs/2510.13217) | 2025 | — | computational | yes |
| 10 | [Deep Research Agents: A Systematic Examination And Roadmap](https://doi.org/10.48550/arxiv.2506.18096) · 10.48550/arxiv.2506.18096 | 2025 | arXiv.org | other | yes |

## 1. Patience is all you need! An agentic system for performing scientific literature review

David W. Brett, Anniek Myatt · 2025 · arXiv.org · experimental · overall 3/3

<https://doi.org/10.48550/arxiv.2504.08752>

**Key finding.** Sparse (keyword-based) retrieval achieves results close to state-of-the-art without requiring dense retrieval infrastructure, while a method for increasing coverage of relevant documents improves literature review generation.

**Why it made the cut.** design-changing · selected by score · strongest on C1 baseline recall ceiling (3/3). Directly tests decision 1 (recall ceiling of single-query search) and questions whether dense/agentic complexity adds real value.

**Why it matters here.** Directly challenges the premise that dense retrieval or agentic complexity is needed to approach SOTA, suggesting the plain single-query sparse baseline may already sit close to the ceiling agentic gains are measured against.

**Method.** LLM-based agentic system for scientific literature search and distillation, evaluated against biology-related questions from existing literature benchmarks; abstract-only for further detail.

**Limitations.**

- Evaluated only on biology-related questions
- Relies on existing benchmarks rather than constructing a new evaluation set
- Abstract gives no absolute performance numbers

<sub>selected: score · criteria: C1 3/3 · C2 2/3 · C3 3/3 · C4 1/3 · C5 2/3 · flags: contradicts, methods_paper · verified 2026-08-26 via openalex, arxiv</sub>

## 2. BrowseComp-Plus: A More Fair and Transparent Evaluation Benchmark of Deep-Research Agent

Zijian Chen, Xueguang Ma, Shengyao Zhuang, Ping Nie et al. · 2025 · arXiv (Cornell University) · experimental · overall 3/3

<https://doi.org/10.48550/arxiv.2508.06600>

**Key finding.** On a fixed, human-verified corpus, Search-R1 with BM25 achieves only 3.86% accuracy while GPT-5 reaches 55.9%, and GPT-5 with a Qwen3-Embedding-8B retriever reaches 70.1% with fewer search calls.

**Why it made the cut.** foundational · selected by score · strongest on C1 baseline recall ceiling (3/3). The central benchmark-construction paper explicitly built to disentangle retriever quality from agent capability with reported baseline accuracies, foundational to nearly every other agentic literature/deep-research search evaluation in this set.

**Why it matters here.** Establishes exactly the kind of controlled baseline-recall and retriever-disentanglement evidence the brief's first question calls for, and is the foundational benchmark that later replication/projection work (e.g., ClimbMix projection) builds on and stress-tests.

**Method.** Benchmark derived from BrowseComp with a fixed curated corpus, human-verified supporting documents, and mined hard negatives, enabling controlled disentanglement of agent and retriever contributions.

**Limitations.**

- corpus is fixed and derived from BrowseComp's own query-supporting documents, which later work shows may inflate apparent retrieval performance
- results reflect one snapshot of models (Search-R1, GPT-5) that will date quickly

<sub>selected: score · criteria: C1 3/3 · C2 1/3 · C3 2/3 · C4 3/3 · C5 1/3 · flags: methods_paper · verified 2026-08-26 via openalex, arxiv</sub>

## 3. Projecting BrowseComp-Plus onto ClimbMix: Toward More Realistic Corpora for Agentic Search

Sahel Sharifymoghaddam, Lin Gu, Yijun Ge, Jimmy Lin · 2026 · no venue · experimental · overall 3/3

<https://arxiv.org/abs/2608.20317>

**Key finding.** Relocating BrowseComp-Plus's evidence into a 553M-document corpus built independently of the benchmark drops evidence recall from 84.3% to 21.4% and costs the strongest agent five points of answer accuracy while issuing 63% more search calls, despite only 57 of 830 questions being fully re-groundable.

**Why it made the cut.** contradicting · selected by score · strongest on C4 benchmark construction (3/3). The clearest available demonstration that a widely-used agentic-search benchmark's construction inflates reported recall/accuracy, and that gains shrink substantially when evidence is relocated to an independently built corpus — exactly the replication-failure evidence the brief asks the scan to reach hardest for.

**Why it matters here.** Directly demonstrates the brief's fourth question in action: a benchmark's own construction (query-derived corpus and negatives) inflates measured retrieval performance, and reported agentic gains shrink sharply once the same questions are projected onto a corpus built without reference to the benchmark.

**Method.** A dataset-agnostic projection pipeline that decomposes benchmark questions into atomic reasoning hops, re-grounds each hop in the ClimbMix corpus, and retains only questions verified by automatic checks, an independent agent, and human review.

**Limitations.**

- only 57 of 830 original questions survive the strict verification pipeline, a small and possibly non-representative subset
- single projection target (ClimbMix); generality of the finding across other corpora is not yet established

<sub>selected: score · criteria: C1 2/3 · C2 1/3 · C3 1/3 · C4 3/3 · C5 3/3 · flags: contradicts, methods_paper · verified 2026-08-26 via arxiv, s2</sub>

## 4. OpenScholar: Synthesizing Scientific Literature with Retrieval-augmented LMs

Akari Asai, Jacqueline He, Rulin Shao, Weijia Shi et al. · 2024 · arXiv.org · experimental · overall 3/3

<https://doi.org/10.48550/arxiv.2411.14199>

**Key finding.** OpenScholar-8B outperforms GPT-4o by 5% and PaperQA2 by 7% in correctness on the new ScholarQABench benchmark (2,967 expert queries across four domains), and its self-feedback inference loop improves GPT-4o's correctness by 12%, while GPT-4o hallucinates citations 78-90% of the time versus OpenScholar's expert-level citation accuracy.

**Why it made the cut.** design-changing · selected by score · strongest on C2 agentic mechanism gain (3/3). One of the most central papers to the brief: an agentic literature-search system, its benchmark, and a quantified mechanism-level gain, all in one.

**Why it matters here.** Attributes a measured gain to a specific mechanism (self-feedback retrieval loop, +12% correctness) and introduces a large expert-constructed literature-search benchmark, giving concrete numbers for decisions 1, 2 and 3 simultaneously.

**Method.** Retrieval-augmented LM over a 45-million-paper open-access datastore with a self-feedback inference loop, evaluated on the new multi-domain ScholarQABench benchmark and via human expert preference studies.

**Limitations.**

- Comparison baseline is another agentic system (PaperQA2) rather than a plain single-query database search
- Datastore limited to open-access papers

<sub>selected: score · criteria: C1 2/3 · C2 3/3 · C3 2/3 · C4 3/3 · C5 0/3 · flags: methods_paper · verified 2026-08-26 via openalex, arxiv</sub>

## 5. LitSearch: A Retrieval Benchmark for Scientific Literature Search

Anirudh Ajith, Mengzhou Xia, Alexis Chevalier, Tanya Goyal et al. · 2024 · Conference on Empirical Methods in Natural Language Processing · experimental · overall 3/3

<https://doi.org/10.48550/arxiv.2407.18940>

**Key finding.** LitSearch finds a 24.8-point absolute recall@5 gap between BM25 and state-of-the-art dense retrievers, LLM-based reranking further improves the best dense retriever by 4.4%, and commercial search engines like Google Search lag the best dense retriever by 32 points.

**Why it made the cut.** design-changing · selected by score · strongest on C1 baseline recall ceiling (3/3). Directly answers decisions 1 and 3 with concrete numbers, on a benchmark built specifically for scientific literature search — core evidence for the brief.

**Why it matters here.** Gives the clearest quantified answer to decision 1 (single-query sparse-search recall ceiling versus dense/reranking alternatives) and a rigorously documented benchmark-construction methodology for decision 3, in exactly the brief's target setting.

**Method.** New 597-query literature-search retrieval benchmark built from GPT-4-generated and author-written questions, expert-verified, benchmarked against numerous retrieval and reranking systems.

**Limitations.**

- Focused on ML/NLP papers rather than science broadly
- Evaluates single-pass retrieval and reranking, not full agentic multi-step systems

<sub>selected: score · criteria: C1 3/3 · C2 0/3 · C3 3/3 · C4 3/3 · C5 1/3 · flags: methods_paper · verified 2026-08-26 via openalex, arxiv</sub>

## 6. Diagnosing Search Behavior and Failure Modes in Long-Horizon Search Agents

Qi Liu, Jiaxin Mao, Fengbin Zhu, Tat-Seng Chua · 2026 · arXiv · experimental · overall 3/3

<https://doi.org/10.48550/arxiv.2608.01913>

**Key finding.** Across six agents on BrowseComp-Plus and BrowseComp, search effort and answer quality are only weakly aligned; accuracy tracks cumulative retrieval recall far better than number of searches, and the best agents issue far fewer redundant queries.

**Why it made the cut.** design-changing · selected by score · strongest on C2 agentic mechanism gain (3/3). Directly decomposes agentic search gains into retrieval vs. utilization components and shows where search effort fails to translate into quality, exactly the mechanism-attribution and failure-mode questions the brief asks.

**Why it matters here.** Directly answers the brief's question of which specific agentic moves carry the gain: query reformulation helps but redundant searching does not, and evidence quality (not search volume) is what predicts answer quality — this should reshape how we measure and stop agentic search rather than count query iterations as a proxy for improvement.

**Method.** Trajectory-level diagnosis with human-annotated document-relevance judgments, decomposing failures into retrieval gaps vs. utilization gaps across six agents on two existing benchmarks.

**Limitations.**

- retrieval model and evaluation harness held fixed across agents, so findings may not generalize to other retrievers
- diagnostic rather than causal manipulation of agent design

<sub>selected: score · criteria: C1 1/3 · C2 3/3 · C3 1/3 · C4 1/3 · C5 3/3 · flags: methods_paper · verified 2026-08-26 via openalex, arxiv</sub>

## 7. Towards Recursive Self-Evolving Agentic Literature Retrieval

Yuwen Du, Tian Jin, Jing Kang, Xianghe Pang et al. · 2026 · arXiv · experimental · overall 3/3

<https://doi.org/10.48550/arxiv.2605.14306>

**Key finding.** PaSaMaster achieves a 16.5x higher F1-score than Google Scholar and a 37.8% higher F1-score than GPT-5.2 at about 1% of the cost, while cutting source hallucination from 32.66% to zero, across 38 disciplines in PaSaMaster-Bench.

**Why it made the cut.** design-changing · selected by score · strongest on C2 agentic mechanism gain (3/3). Directly answers the brief's core question of what agentic self-evolving retrieval adds over single-query search, with an explicit baseline comparison.

**Why it matters here.** Explicitly anchors an agentic system's gain against a plain database-search baseline (Google Scholar) with a quantified multiple, giving the scan a concrete C1/C2 data point on how much iterative self-evolving retrieval adds over single-query search.

**Method.** Recursive self-evolving agentic retrieval system separating intent planning (frontier LLM) from retrieval/scoring (lightweight models), evaluated against Google Scholar and GPT-5.2 baselines on a custom 38-discipline benchmark.

**Limitations.**

- benchmark (PaSaMaster-Bench) construction details not given in the abstract
- comparison baseline (Google Scholar) is not a controlled BM25/embedding search implementation
- no replication or alternate-metric check of the reported gains

<sub>selected: score · criteria: C1 2/3 · C2 3/3 · C3 3/3 · C4 1/3 · C5 0/3 · flags: methods_paper · verified 2026-08-26 via openalex, arxiv</sub>

## 8. Structurally-bounded Agentic Graph Exploration for Evidence-Grounded Scholarly DeepSearch

Rima Hazra, Sayan Layek, Somnath Banerjee, Soumen Chakrabarti et al. · 2026 · arXiv · experimental · overall 3/3

<https://doi.org/10.48550/arxiv.2608.24809>

**Key finding.** Crase, a bounded citation-graph exploration method (one seed search, 1.5-hop expansion, entailment-based pruning, recency-aware random-walk ranking), outperforms deep research agents built on proprietary models by up to 3x recall@50 at roughly a third of the cost on LitSearch and a further benchmark.

**Why it made the cut.** design-changing · selected by backfill · strongest on C2 agentic mechanism gain (3/3). A structurally bounded citation-graph traversal system that explicitly attributes its recall gains to specific mechanisms (graph expansion, pruning, ranking) rather than to an undifferentiated agent, directly on scholarly literature search.

**Why it matters here.** Isolates which specific agentic moves (bounded citation-graph traversal + entailment pruning + ranking) actually carry the recall gain versus an unbounded, opaque search loop, directly answering the brief's second decision question with a mechanism-level ablation-style design.

**Method.** Bounded, inspectable pipeline over a 500K-paper arXiv corpus: single seed query, fixed citation-graph expansion, entailment pruning, and random-walk ranking, benchmarked against open-ended deep research agents.

**Limitations.**

- evaluated on a fixed 500K-paper arXiv corpus, so generalization to full open-web literature search is untested
- comparison partly favors Crase's cost efficiency which may trade off against coverage on other corpora

<sub>selected: backfill · criteria: C1 2/3 · C2 3/3 · C3 3/3 · C4 1/3 · C5 0/3 · flags: methods_paper · verified 2026-08-26 via arxiv</sub>

## 9. LLM-guided Hierarchical Search for End-to-end Reasoning Intensive Retrieval

Nilesh Gupta, Wei-Cheng Chang, N. Bui, Cho-Jui Hsieh et al. · 2025 · no venue · computational · overall 3/3

<https://arxiv.org/abs/2510.13217>

**Key finding.** LATTICE, an LLM-guided hierarchical search index with no embedding model in the retrieval loop, matches the best fine-tuned ensemble baseline on BRIGHT (46.7 nDCG@10) and reaches 49.1 with a lightweight ensemble, while remaining competitive on SciFact/SciDocs.

**Why it made the cut.** design-changing · selected by backfill · strongest on C3 retrieval/reranking method (3/3). A retrieval-architecture paper that explicitly shows where embedding-based single-query retrieval and query-reformulation fixes both fail, directly relevant to the brief's baseline-ceiling and mechanism-attribution questions, with tests on scientific benchmarks (SciFact, SciDocs).

**Why it matters here.** Shows that the standard embedding-retriever-plus-LLM-verifier recipe (the single-query database search baseline) fails when top-k misses the right documents on reasoning-intensive queries, and that query-side fixes like reformulation and agentic loops remain brittle to that failure — directly bears on the brief's baseline-ceiling and mechanism-gain questions.

**Method.** Top-down LLM-guided construction of a hierarchical document index from multi-level summaries, with calibrated path-aggregated LLM traversal, evaluated against embedding-retriever and reranking baselines on BRIGHT, NQ, SciFact, SciDocs.

**Limitations.**

- primary evaluation is on BRIGHT, a general reasoning-intensive IR benchmark, not a literature-search-specific one
- index construction cost and scalability to very large corpora not detailed in the abstract

<sub>selected: backfill · criteria: C1 2/3 · C2 1/3 · C3 3/3 · C4 1/3 · C5 2/3 · flags: methods_paper · verified 2026-08-26 via arxiv, s2</sub>

## 10. Deep Research Agents: A Systematic Examination And Roadmap

Yuxuan Huang, Yihang Chen, Haozhen Zhang, Kang Li et al. · 2025 · arXiv.org · other · overall 3/3

<https://doi.org/10.48550/arxiv.2506.18096>

**Key finding.** A systematic taxonomy of Deep Research agent architectures (static vs. dynamic workflows, single- vs. multi-agent) that critically evaluates current benchmarks, flagging restricted external-knowledge access, sequential execution inefficiencies, and metric-objective misalignment as key limitations.

**Why it made the cut.** foundational · selected by review · strongest on C4 benchmark construction (3/3). The main synthesis/roadmap paper for the entire deep-research-agent literature, with an explicit critique of benchmark validity that anchors the brief's benchmark-construction and gain-scrutiny questions.

**Why it matters here.** Gives an explicit, structured critique of benchmark limitations and metric-objective misalignment, directly informing the brief's third and fourth questions about benchmark construction and where reported gains may not be trustworthy, and orients the whole scan's taxonomy of agentic mechanisms.

**Method.** Narrative survey and taxonomy synthesizing architectural components (information acquisition, tool use, MCP integration) and benchmark critique across the Deep Research agent literature.

**Limitations.**

- narrative review rather than a systematic review with a stated protocol
- does not itself provide new empirical measurements of gains or failures

<sub>selected: review · criteria: C1 1/3 · C2 2/3 · C3 1/3 · C4 3/3 · C5 1/3 · flags: review · verified 2026-08-26 via arxiv</sub>

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

- [Multi-Turn Agentic Scientific Literature Search via Workflow Induction](https://doi.org/10.48550/arxiv.2607.00597) (2026) — overall 3/3
- [PaSa: An LLM Agent for Comprehensive Academic Paper Search](https://doi.org/10.48550/arxiv.2501.10120) (2025) — overall 3/3
- [Deep Research: A Survey of Autonomous Research Agents](https://doi.org/10.48550/arxiv.2508.12752) (2025) — overall 3/3
- [Multi-Agent System for Scientific Literature Search and Recommendation](https://doi.org/10.1109/icssas66150.2025.11081082) (2025) — overall 3/3
- [CG-RAG: Research Question Answering by Citation Graph Retrieval-Augmented LLMs](https://doi.org/10.1145/3726302.3729920) (2025) — overall 3/3
