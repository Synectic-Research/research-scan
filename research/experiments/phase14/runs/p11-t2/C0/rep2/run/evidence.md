# Evidence scan — p11-t2

Run `/Users/nabergoj/Projects/research-scan/research/experiments/phase14/runs/p11-t2/C0/rep2/run` · brief `/Users/nabergoj/Projects/research-scan/research/experiments/phase14/runs/p11-t2/C0/rep2/run/brief.md` · rendered 2026-08-26

| # | Paper | Year | Venue | Evidence | Verified |
|---|---|---|---|---|---|
| 1 | [When to use Graphs in RAG: A Comprehensive Analysis for Graph Retrieval-Augmented Generation](https://doi.org/10.48550/arxiv.2506.05690) · 10.48550/arxiv.2506.05690 | 2025 | arXiv.org | experimental | yes |
| 2 | [BrowseComp-Plus: A More Fair and Transparent Evaluation Benchmark of Deep-Research Agent](https://doi.org/10.48550/arxiv.2508.06600) · 10.48550/arxiv.2508.06600 | 2025 | arXiv (Cornell University) | experimental | yes |
| 3 | [LLM-guided Hierarchical Search for End-to-end Reasoning Intensive Retrieval](https://arxiv.org/abs/2510.13217) | 2025 | — | experimental | yes |
| 4 | [Diagnosing Search Behavior and Failure Modes in Long-Horizon Search Agents](https://doi.org/10.48550/arxiv.2608.01913) · 10.48550/arxiv.2608.01913 | 2026 | arXiv | experimental | yes |
| 5 | [Deep Research Agents: A Systematic Examination And Roadmap](https://doi.org/10.48550/arxiv.2506.18096) · 10.48550/arxiv.2506.18096 | 2025 | arXiv.org | other | yes |
| 6 | [Projecting BrowseComp-Plus onto ClimbMix: Toward More Realistic Corpora for Agentic Search](https://arxiv.org/abs/2608.20317) | 2026 | — | experimental | yes |
| 7 | [LitSearch: A Retrieval Benchmark for Scientific Literature Search](https://doi.org/10.48550/arxiv.2407.18940) · 10.48550/arxiv.2407.18940 | 2024 | Conference on Empirical Methods in Natural Language Processing | experimental | yes |
| 8 | [PaSa: An LLM Agent for Comprehensive Academic Paper Search](https://doi.org/10.48550/arxiv.2501.10120) · 10.48550/arxiv.2501.10120 | 2025 | Annual Meeting of the Association for Computational Linguistics | experimental | yes |
| 9 | [OpenScholar: Synthesizing Scientific Literature with Retrieval-augmented LMs](https://doi.org/10.48550/arxiv.2411.14199) · 10.48550/arxiv.2411.14199 | 2024 | arXiv.org | experimental | yes |
| 10 | [Towards Recursive Self-Evolving Agentic Literature Retrieval](https://doi.org/10.48550/arxiv.2605.14306) · 10.48550/arxiv.2605.14306 | 2026 | arXiv | experimental | yes |

## 1. When to use Graphs in RAG: A Comprehensive Analysis for Graph Retrieval-Augmented Generation

Zhishang Xiang, Chuan-Yu Wu, Qinggang Zhang, Shengyuan Chen et al. · 2025 · arXiv.org · experimental · overall 3/3

<https://doi.org/10.48550/arxiv.2506.05690>

**Key finding.** GraphRAG-Bench shows GraphRAG frequently underperforms vanilla RAG on real-world tasks, and systematically characterizes the conditions (task type, pipeline stage) under which graph structure actually helps.

**Why it made the cut.** contradicting · selected by score · strongest on C2 agentic mechanism gain (3/3). The clearest existing evidence that a graph-based retrieval mechanism's reported gains can shrink or vanish depending on task and benchmark, which is exactly the failure mode decision 4 asks the scan to find, and the underlying GraphRAG technique is the same one used in literature-search citation traversal.

**Why it matters here.** Directly tests the premise underlying citation-graph traversal in agentic literature search: the graph mechanism itself does not reliably beat plain retrieval, and this benchmark's task-by-task breakdown is the template for checking whether a literature-search agent's graph traversal is actually earning its keep.

**Method.** New benchmark spanning fact retrieval, complex reasoning, contextual summarization, and creative generation, with end-to-end pipeline evaluation from graph construction through generation.

**Limitations.**

- built on general-domain RAG tasks rather than scientific literature corpora
- graph retrieval technique (GraphRAG) is generic; findings are inferred to transfer to citation-graph traversal rather than tested on it directly

<sub>selected: score · criteria: C1 2/3 · C2 3/3 · C3 2/3 · C4 3/3 · C5 3/3 · flags: contradicts, methods_paper · verified 2026-08-26 via openalex, arxiv</sub>

## 2. BrowseComp-Plus: A More Fair and Transparent Evaluation Benchmark of Deep-Research Agent

Zijian Chen, Xueguang Ma, Shengyao Zhuang, Ping Nie et al. · 2025 · arXiv (Cornell University) · experimental · overall 3/3

<https://doi.org/10.48550/arxiv.2508.06600>

**Key finding.** On the fixed-corpus BrowseComp-Plus benchmark, Search-R1 with BM25 achieves only 3.86% accuracy versus GPT-5's 55.9%, and pairing GPT-5 with a Qwen3-Embedding-8B retriever raises accuracy to 70.1% with fewer search calls.

**Why it made the cut.** design-changing · selected by score · strongest on C1 baseline recall ceiling (3/3). The central controlled benchmark for measuring baseline retrieval vs agentic deep-research gains, foundational to decisions 1 and 4.

**Why it matters here.** Gives a controlled, corpus-fixed measurement of the gap between a weak baseline retriever (BM25) and a strong agentic+embedding combination, directly anchoring the size of the agentic gain over single-query search and enabling disentangled retriever-vs-agent analysis.

**Method.** A benchmark derived from BrowseComp using a fixed, curated corpus with human-verified supporting documents and mined hard negatives, enabling controlled, disentangled comparison of deep-research agents and retrievers.

**Limitations.**

- Corpus (~100K docs) assembled per-query from the benchmark's own supporting docs and mined negatives, which later work shows may inflate measured performance
- Single benchmark domain (BrowseComp-style web queries), not literature-search specific

<sub>selected: score · criteria: C1 3/3 · C2 2/3 · C3 2/3 · C4 3/3 · C5 1/3 · flags: methods_paper · verified 2026-08-26 via openalex, arxiv</sub>

## 3. LLM-guided Hierarchical Search for End-to-end Reasoning Intensive Retrieval

Nilesh Gupta, Wei-Cheng Chang, N. Bui, Cho-Jui Hsieh et al. · 2025 · no venue · experimental · overall 3/3

<https://arxiv.org/abs/2510.13217>

**Key finding.** LATTICE, an LLM-guided hierarchical search index with calibrated path-aggregated traversal, matches the best fine-tuned ensemble baseline at 46.7 nDCG@10 on BRIGHT with a single off-the-shelf LLM, and an ensemble variant (LATTICE++) reaches 49.1 nDCG@10.

**Why it made the cut.** design-changing · selected by score · strongest on C1 baseline recall ceiling (3/3). A retrieval/reranking method that measures where single-query embedding retrieval fails, directly addressing decisions 1 and 3.

**Why it matters here.** Quantifies where embedding-retriever-plus-LLM-verifier pipelines fail on reasoning-intensive queries (the recall-ceiling problem) and offers an alternative retrieval architecture removing the embedding model from the search-time loop, directly bearing on decisions 1 and 3.

**Method.** Top-down LLM-guided construction of a hierarchically navigable search index from multi-level document summaries, plus calibrated LLM-guided traversal with cross-branch reference nodes; evaluated on BRIGHT, NQ, SciFact, SciDocs.

**Limitations.**

- Primary benchmark (BRIGHT) is reasoning-intensive IR rather than literature-search-specific
- Advantage over reranking only appears after a moderate token budget

<sub>selected: score · criteria: C1 3/3 · C2 2/3 · C3 3/3 · C4 1/3 · C5 2/3 · flags: methods_paper · verified 2026-08-26 via arxiv, s2</sub>

## 4. Diagnosing Search Behavior and Failure Modes in Long-Horizon Search Agents

Qi Liu, Jiaxin Mao, Fengbin Zhu, Tat-Seng Chua · 2026 · arXiv · experimental · overall 3/3

<https://doi.org/10.48550/arxiv.2608.01913>

**Key finding.** Across six deep search agents on BrowseComp-Plus and BrowseComp, answer accuracy correlates strongly with cumulative retrieval recall but only weakly with number of search steps or context consumed, and the best-performing agents issue far fewer redundant queries.

**Why it made the cut.** design-changing · selected by score · strongest on C2 agentic mechanism gain (3/3). Directly diagnoses which agentic search behaviors carry the gain and which are low-yield, bearing on decisions 2 and 4.

**Why it matters here.** Shows that agentic search's presumed lever -- more searching -- often fails to deliver, redirecting attention from search volume to query formulation, evidence selection, and stopping criteria; directly informs how to attribute agentic gains and where they stop holding.

**Method.** Trajectory-level diagnosis of long-horizon search agents using human-annotated document-level relevance judgments, comparing six agents on BrowseComp-Plus and validating on BrowseComp with an open-web search API, retrieval model and harness held fixed.

**Limitations.**

- Six agents on two related benchmarks (BrowseComp-Plus, BrowseComp); may not generalize to literature-search-specific benchmarks
- Diagnostic/correlational analysis rather than a causal ablation of each mechanism

<sub>selected: score · criteria: C1 1/3 · C2 3/3 · C3 1/3 · C4 2/3 · C5 3/3 · flags: contradicts · verified 2026-08-26 via openalex, arxiv</sub>

## 5. Deep Research Agents: A Systematic Examination And Roadmap

Yuxuan Huang, Yihang Chen, Haozhen Zhang, Kang Li et al. · 2025 · arXiv.org · other · overall 3/3

<https://doi.org/10.48550/arxiv.2506.18096>

**Key finding.** A systematic taxonomy of Deep Research agent architectures (static/dynamic workflows, single/multi-agent) accompanies a critical review finding current benchmarks limited by restricted external-knowledge access, sequential-execution inefficiencies, and misalignment between evaluation metrics and DR agents' practical objectives.

**Why it made the cut.** foundational · selected by score · strongest on C4 benchmark construction (3/3). The field's own review of deep-research-agent design and benchmark limitations, a synthesis point against which other shortlisted findings can be checked.

**Why it matters here.** Synthesizes the field's benchmarks and architectures and flags specific evaluation misalignments, giving a map of what has and hasn't been validated and where benchmark critique should focus for decisions 3 and 4.

**Method.** Narrative survey and taxonomy of information-acquisition strategies (API vs browser-based), tool-use frameworks, and agent architectures, with critical benchmark evaluation. Abstract-only for review methodology.

**Limitations.**

- Narrative review without a stated systematic protocol
- Descriptive taxonomy rather than new empirical evidence on baseline-vs-agentic gains

<sub>selected: score · criteria: C1 1/3 · C2 2/3 · C3 2/3 · C4 3/3 · C5 2/3 · flags: review · verified 2026-08-26 via arxiv</sub>

## 6. Projecting BrowseComp-Plus onto ClimbMix: Toward More Realistic Corpora for Agentic Search

Sahel Sharifymoghaddam, Lin Gu, Yijun Ge, Jimmy Lin · 2026 · no venue · experimental · overall 3/3

<https://arxiv.org/abs/2608.20317>

**Key finding.** Relocating BrowseComp-Plus's evidence into the independently-built ClimbMix corpus (yielding 57 fully-grounded questions) drops the strongest agent's evidence recall from 84.3% to 21.4% and increases search calls by 63%, while answer accuracy falls only five points.

**Why it made the cut.** contradicting · selected by score · strongest on C4 benchmark construction (3/3). Directly demonstrates a reported agentic/retrieval gain shrinking dramatically under a construction-decoupled benchmark, the strongest evidence for decision 4.

**Why it matters here.** Shows that a widely-used deep-research benchmark's reported retrieval performance depends heavily on its query-selected corpus construction and largely evaporates once decoupled from that construction -- the clearest evidence here that reported agentic gains are partly a benchmark-construction artifact.

**Method.** A projection pipeline decomposes benchmark questions into atomic reasoning hops and re-grounds each hop in a new 553M-document corpus (ClimbMix) built without reference to the benchmark, verifying every hop via automatic checks, an independent agent, and human review.

**Limitations.**

- Only 57 of 830 original questions survive full grounding verification, a small resulting set
- Single benchmark (BrowseComp-Plus) projected onto a single alternative corpus (ClimbMix)

<sub>selected: score · criteria: C1 2/3 · C2 1/3 · C3 1/3 · C4 3/3 · C5 3/3 · flags: contradicts, methods_paper · verified 2026-08-26 via arxiv, s2</sub>

## 7. LitSearch: A Retrieval Benchmark for Scientific Literature Search

Anirudh Ajith, Mengzhou Xia, Alexis Chevalier, Tanya Goyal et al. · 2024 · Conference on Empirical Methods in Natural Language Processing · experimental · overall 3/3

<https://doi.org/10.48550/arxiv.2407.18940>

**Key finding.** On LitSearch's 597 realistic literature-search queries, there is a 24.8% absolute recall@5 gap between BM25 and state-of-the-art dense retrievers, LLM-based reranking further improves the best dense retriever by 4.4%, and commercial search engines lag the best dense retriever by 32 points.

**Why it made the cut.** foundational · selected by score · strongest on C1 baseline recall ceiling (3/3). The clearest, most directly on-topic baseline-and-benchmark paper for scientific literature search retrieval.

**Why it matters here.** Directly supplies the single-query BM25 baseline recall ceiling (Q1) the brief asks for, plus a rigorously constructed evaluation set (Q3) and a measured reranking gain (C3), making it a reference point every later agentic-gain claim should be checked against.

**Method.** Benchmark of 597 queries constructed from GPT-4-generated questions on cited paragraphs plus author-written questions about recent papers, expert-reviewed; extensively benchmarks retrieval models and two LLM reranking pipelines.

**Limitations.**

- benchmark centers on recent ML/NLP papers, so generalization to other scientific fields is untested
- does not evaluate full agentic pipelines (reformulation, graph traversal, iterative crawling), only retrieval and reranking

<sub>selected: score · criteria: C1 3/3 · C2 0/3 · C3 3/3 · C4 3/3 · C5 1/3 · flags: methods_paper · verified 2026-08-26 via openalex, arxiv</sub>

## 8. PaSa: An LLM Agent for Comprehensive Academic Paper Search

Yichen He, Guanhua Huang, Peiyuan Feng, Yuan Lin et al. · 2025 · Annual Meeting of the Association for Computational Linguistics · experimental · overall 3/3

<https://doi.org/10.48550/arxiv.2501.10120>

**Key finding.** PaSa-7B exceeds the best Google-based baseline by 37.78% in recall@20 and 39.90% in recall@50 on RealScholarQuery, and outperforms a prompted GPT-4o agent (PaSa-GPT-4o) by 30.36% in recall and 4.25% in precision.

**Why it made the cut.** design-changing · selected by score · strongest on C1 baseline recall ceiling (3/3). A leading exemplar agentic paper-search system with quantified gains over search-API baselines and its own benchmark construction, central to decisions 1-3.

**Why it matters here.** Provides both a benchmark-construction template (synthetic RL training set plus a real-world eval set) and a strong quantified anchor for how much an agentic reference-following/reading loop can gain over single-query search-API baselines like Google.

**Method.** RL-trained LLM agent that issues search queries, reads papers, and selects references, trained on a synthetic 35k-query dataset (AutoScholarQuery) and evaluated on a human-curated real-world benchmark (RealScholarQuery).

**Limitations.**

- Trained on synthetic data that may not transfer to all query types
- Baselines (Google, ChatGPT) are uncontrolled live search, unlike fixed-corpus benchmarks

<sub>selected: score · criteria: C1 3/3 · C2 2/3 · C3 1/3 · C4 3/3 · C5 0/3 · flags: methods_paper · verified 2026-08-26 via openalex, arxiv</sub>

## 9. OpenScholar: Synthesizing Scientific Literature with Retrieval-augmented LMs

Akari Asai, Jacqueline He, Rulin Shao, Weijia Shi et al. · 2024 · arXiv.org · experimental · overall 3/3

<https://doi.org/10.48550/arxiv.2411.14199>

**Key finding.** OpenScholar-8B, retrieving from 45 million open-access papers, outperforms GPT-4o by 5% and PaperQA2 by 7% in correctness on the newly built ScholarQABench (2,967 expert queries, 208 long-form answers across four domains), while GPT-4o hallucinates citations 78-90% of the time versus OpenScholar's expert-level citation accuracy.

**Why it made the cut.** design-changing · selected by backfill · strongest on C3 retrieval/reranking method (3/3). A foundational system-and-benchmark pair squarely in the brief's target setting, informing both design and evaluation decisions.

**Why it matters here.** Directly establishes both a benchmark-construction template (C4) and a baseline/gain comparison (C1/C3) for scientific-literature-search systems, the exact setting the brief targets.

**Method.** Retrieval-augmented LM with self-feedback inference loop, evaluated on a purpose-built multi-domain literature-search benchmark against strong closed and open baselines, plus human preference evaluation.

**Limitations.**

- comparisons rely on specific baseline systems (GPT-4o, PaperQA2) that may not represent all single-query search baselines
- does not test whether gains hold under a different benchmark or independent replication

<sub>selected: backfill · criteria: C1 2/3 · C2 1/3 · C3 3/3 · C4 3/3 · C5 0/3 · flags: methods_paper · verified 2026-08-26 via openalex, arxiv</sub>

## 10. Towards Recursive Self-Evolving Agentic Literature Retrieval

Yuwen Du, Tian Jin, Jing Kang, Xianghe Pang et al. · 2026 · arXiv · experimental · overall 3/3

<https://doi.org/10.48550/arxiv.2605.14306>

**Key finding.** PaSaMaster achieves 16.5x higher F1 than Google Scholar and 37.8% higher F1 than GPT-5.2 at about 1% of the cost across 38 disciplines, while reducing source hallucination from 32.66% to zero.

**Why it made the cut.** design-changing · selected by backfill · strongest on C1 baseline recall ceiling (3/3). Provides an explicit single-query database search baseline (Google Scholar) and a large measured gain over it, central to decision 1.

**Why it matters here.** Directly anchors the single-query search baseline (Google Scholar) the brief asks for and quantifies the size of an agentic gain against it, giving a concrete number to check other reported improvements against.

**Method.** Recursive self-evolving retrieval combining frontier-LLM intent understanding with lightweight-model retrieval/scoring over verified papers; evaluated on PaSaMaster-Bench (38 disciplines).

**Limitations.**

- benchmark (PaSaMaster-Bench) construction methodology not detailed in the abstract
- gain not decomposed into the contribution of individual agentic moves

<sub>selected: backfill · criteria: C1 3/3 · C2 2/3 · C3 2/3 · C4 1/3 · C5 0/3 · flags: methods_paper · verified 2026-08-26 via openalex, arxiv</sub>

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

- [Open-Source Agentic Hybrid RAG Framework for Scientific Literature Review](https://doi.org/10.48550/arxiv.2508.05660) (2025) — overall 3/3
- [Multi-Agent System for Scientific Literature Search and Recommendation](https://doi.org/10.1109/icssas66150.2025.11081082) (2025) — overall 3/3
- [Patience is all you need! An agentic system for performing scientific literature review](https://doi.org/10.48550/arxiv.2504.08752) (2025) — overall 3/3
- [Structurally-bounded Agentic Graph Exploration for Evidence-Grounded Scholarly DeepSearch](https://doi.org/10.48550/arxiv.2608.24809) (2026) — overall 3/3
- [Deep Research: A Survey of Autonomous Research Agents](https://doi.org/10.48550/arxiv.2508.12752) (2025) — overall 3/3
