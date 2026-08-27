# Evidence scan — p11-t2

Run `/Users/nabergoj/Projects/research-scan/research/experiments/phase14/runs/p11-t2/C/rep4/run` · brief `/Users/nabergoj/Projects/research-scan/research/experiments/phase14/runs/p11-t2/C/rep4/run/brief.md` · rendered 2026-08-27

| # | Paper | Year | Venue | Evidence | Verified |
|---|---|---|---|---|---|
| 1 | [When to use Graphs in RAG: A Comprehensive Analysis for Graph Retrieval-Augmented Generation](https://doi.org/10.48550/arxiv.2506.05690) · 10.48550/arxiv.2506.05690 | 2025 | arXiv.org | experimental | yes |
| 2 | [Diagnosing Search Behavior and Failure Modes in Long-Horizon Search Agents](https://doi.org/10.48550/arxiv.2608.01913) · 10.48550/arxiv.2608.01913 | 2026 | arXiv | experimental | yes |
| 3 | [BrowseComp-Plus: A More Fair and Transparent Evaluation Benchmark of Deep-Research Agent](https://doi.org/10.48550/arxiv.2508.06600) · 10.48550/arxiv.2508.06600 | 2025 | arXiv (Cornell University) | experimental | yes |
| 4 | [Projecting BrowseComp-Plus onto ClimbMix: Toward More Realistic Corpora for Agentic Search](https://arxiv.org/abs/2608.20317) | 2026 | — | experimental | yes |
| 5 | [Fact, Fetch, and Reason: A Unified Evaluation of Retrieval-Augmented Generation](https://doi.org/10.48550/arxiv.2409.12941) · 10.48550/arxiv.2409.12941 | 2024 | North American Chapter of the Association for Computational Linguistics | experimental | yes |
| 6 | [LitSearch: A Retrieval Benchmark for Scientific Literature Search](https://doi.org/10.48550/arxiv.2407.18940) · 10.48550/arxiv.2407.18940 | 2024 | Conference on Empirical Methods in Natural Language Processing | experimental | yes |
| 7 | [Towards Recursive Self-Evolving Agentic Literature Retrieval](https://doi.org/10.48550/arxiv.2605.14306) · 10.48550/arxiv.2605.14306 | 2026 | arXiv | experimental | yes |
| 8 | [LLM-guided Hierarchical Search for End-to-end Reasoning Intensive Retrieval](https://arxiv.org/abs/2510.13217) | 2025 | — | experimental | yes |
| 9 | [OpenScholar: Synthesizing Scientific Literature with Retrieval-augmented LMs](https://doi.org/10.48550/arxiv.2411.14199) · 10.48550/arxiv.2411.14199 | 2024 | arXiv.org | experimental | yes |
| 10 | [Deep Research Agents: A Systematic Examination And Roadmap](https://doi.org/10.48550/arxiv.2506.18096) · 10.48550/arxiv.2506.18096 | 2025 | arXiv.org | other | yes |

## 1. When to use Graphs in RAG: A Comprehensive Analysis for Graph Retrieval-Augmented Generation

Zhishang Xiang, Chuan-Yu Wu, Qinggang Zhang, Shengyuan Chen et al. · 2025 · arXiv.org · experimental · overall 3/3

<https://doi.org/10.48550/arxiv.2506.05690>

**Key finding.** GraphRAG frequently underperforms vanilla RAG on many real-world tasks; GraphRAG-Bench systematically identifies the specific conditions under which graph-based retrieval does and does not surpass traditional RAG.

**Why it made the cut.** contradicting · selected by score · strongest on C4 benchmark construction (3/3). Directly contradicts the premise that graph-structured retrieval reliably improves over baseline retrieval, and its benchmark-construction approach transfers as a precedent for evaluating agentic literature-search systems on the same question.

**Why it matters here.** Provides direct, benchmarked evidence that graph-based retrieval — the mechanism underlying citation-graph traversal in agentic literature search — does not reliably beat a simple baseline, exactly the failure-to-replicate evidence the brief's question 4 asks the scan to find; its benchmark-construction methodology for isolating when graph structure helps is a transferable precedent for literature-search evaluation sets.

**Method.** Introduces GraphRAG-Bench, a benchmark spanning fact retrieval, complex reasoning, contextual summarization, and creative generation, with systematic pipeline evaluation from graph construction through generation.

**Limitations.**

- general-domain RAG tasks rather than scientific-literature corpora
- GraphRAG vs. vanilla RAG findings may not map exactly onto citation-graph traversal for paper retrieval

<sub>selected: score · criteria: C1 2/3 · C2 2/3 · C3 2/3 · C4 3/3 · C5 3/3 · flags: contradicts, methods_paper · verified 2026-08-27 via openalex, arxiv</sub>

## 2. Diagnosing Search Behavior and Failure Modes in Long-Horizon Search Agents

Qi Liu, Jiaxin Mao, Fengbin Zhu, Tat-Seng Chua · 2026 · arXiv · experimental · overall 3/3

<https://doi.org/10.48550/arxiv.2608.01913>

**Key finding.** Across six agents on BrowseComp-Plus and BrowseComp, search effort and answer quality are only weakly aligned; accuracy tracks cumulative retrieval recall far better than number of searches, and top agents issue far fewer redundant queries.

**Why it made the cut.** design-changing · selected by score · strongest on C2 agentic mechanism gain (3/3). Decomposes agentic search behavior into retrieval vs utilization gaps, the exact mechanism-attribution question the brief prioritizes.

**Why it matters here.** Directly answers decision 2 and 4: shows which agentic behaviors (early useful evidence, low-yield search tails) actually carry the gain and where more searching does not help, undercutting the premise that more agentic search always wins.

**Method.** Trajectory-level diagnosis with human-annotated document relevance judgments, retrieval model and evaluation harness held fixed across six agents; validated on two benchmarks.

**Limitations.**

- diagnostic/observational, not a new system
- relies on existing benchmarks' relevance judgments
- six-agent sample may not generalize to all designs

<sub>selected: score · criteria: C1 2/3 · C2 3/3 · C3 2/3 · C4 1/3 · C5 3/3 · flags: contradicts · verified 2026-08-27 via openalex, arxiv</sub>

## 3. BrowseComp-Plus: A More Fair and Transparent Evaluation Benchmark of Deep-Research Agent

Zijian Chen, Xueguang Ma, Shengyao Zhuang, Ping Nie et al. · 2025 · arXiv (Cornell University) · experimental · overall 3/3

<https://doi.org/10.48550/arxiv.2508.06600>

**Key finding.** On a fixed, human-verified corpus, Search-R1 with BM25 achieves only 3.86% accuracy while GPT-5 reaches 55.9%, and pairing GPT-5 with a Qwen3-Embedding-8B retriever raises accuracy to 70.1% with fewer search calls.

**Why it made the cut.** foundational · selected by score · strongest on C1 baseline recall ceiling (3/3). The benchmark-construction and baseline-recall precedent multiple other shortlisted papers build on or critique.

**Why it matters here.** Supplies the exact BM25/single-retriever recall ceiling the brief needs as an anchor and a template for constructing contamination-controlled benchmarks, directly answering decisions 1 and 3.

**Method.** Benchmark derived from BrowseComp with a fixed curated corpus, human-verified supporting documents, and mined hard negatives, enabling controlled comparison of retrievers and agent LLMs.

**Limitations.**

- corpus assembled per-query from the benchmark's own supporting documents and negatives, a contamination risk later work (this shortlist's dc6612fba47a) directly challenges

<sub>selected: score · criteria: C1 3/3 · C2 1/3 · C3 2/3 · C4 3/3 · C5 1/3 · flags: methods_paper · verified 2026-08-27 via openalex, arxiv</sub>

## 4. Projecting BrowseComp-Plus onto ClimbMix: Toward More Realistic Corpora for Agentic Search

Sahel Sharifymoghaddam, Lin Gu, Yijun Ge, Jimmy Lin · 2026 · no venue · experimental · overall 3/3

<https://arxiv.org/abs/2608.20317>

**Key finding.** Relocating BrowseComp-Plus's evidence to an independently built corpus (ClimbMix) drops the strongest agent's evidence recall from 84.3% to 21.4% and costs five points of answer accuracy while issuing 63% more search calls, despite only 57 of 830 questions surviving full grounding verification.

**Why it made the cut.** contradicting · selected by score · strongest on C4 benchmark construction (3/3). Shows a widely-used benchmark's own construction inflates the reported agentic gain, the clearest example in this shortlist of decision 4's target finding.

**Why it matters here.** Directly demonstrates decision 4: a benchmark's per-query-constructed corpus (BrowseComp-Plus) inflates reported agentic evidence recall relative to a corpus built independently of the benchmark, exactly the replication-failure the brief is hunting for.

**Method.** A dataset-agnostic projection pipeline that decomposes questions into atomic reasoning hops, grounds each hop in a new 553M-document corpus (ClimbMix) not built from the benchmark, verified by automatic checks, an independent agent, and human review.

**Limitations.**

- only 57 of 830 original questions survive full grounding, a large reduction in coverage
- single benchmark (BrowseComp-Plus) and single alternative corpus (ClimbMix) tested so far

<sub>selected: score · criteria: C1 2/3 · C2 1/3 · C3 1/3 · C4 3/3 · C5 3/3 · flags: contradicts, methods_paper · verified 2026-08-27 via arxiv, s2</sub>

## 5. Fact, Fetch, and Reason: A Unified Evaluation of Retrieval-Augmented Generation

Satyapriya Krishna, Kalpesh Krishna, Anhad Mohananey, S. Schwarcz et al. · 2024 · North American Chapter of the Association for Computational Linguistics · experimental · overall 3/3

<https://doi.org/10.48550/arxiv.2409.12941>

**Key finding.** State-of-the-art LLMs achieve only 0.40 accuracy on FRAMES multi-hop questions with no retrieval, rising to 0.66 with a multi-step retrieval pipeline (>50% relative improvement).

**Why it made the cut.** plan-influencing · selected by score · strongest on C1 baseline recall ceiling (3/3). Provides an explicit no-retrieval vs multi-step-retrieval baseline comparison and a benchmark construction precedent (C1, C4).

**Why it matters here.** Gives a concrete, quantified no-retrieval baseline and shows the specific gain size attributable to multi-step (iterative) retrieval, directly anchoring the recall-ceiling and mechanism-attribution questions.

**Method.** New unified RAG evaluation benchmark (FRAMES) of multi-hop questions requiring multi-source integration; baseline no-retrieval and multi-step retrieval pipeline results reported.

**Limitations.**

- general RAG/QA setting, not specific to scientific literature
- multi-step retrieval pipeline is not decomposed into reformulation vs iteration vs reranking contributions

<sub>selected: score · criteria: C1 3/3 · C2 2/3 · C3 2/3 · C4 3/3 · C5 0/3 · flags: methods_paper · verified 2026-08-27 via openalex, arxiv</sub>

## 6. LitSearch: A Retrieval Benchmark for Scientific Literature Search

Anirudh Ajith, Mengzhou Xia, Alexis Chevalier, Tanya Goyal et al. · 2024 · Conference on Empirical Methods in Natural Language Processing · experimental · overall 3/3

<https://doi.org/10.48550/arxiv.2407.18940>

**Key finding.** On the 597-query LitSearch benchmark, BM25 trails state-of-the-art dense retrievers by 24.8% absolute recall@5, LLM-based reranking further improves the best dense retriever by 4.4%, and commercial search engines lag the best dense retriever by 32 points.

**Why it made the cut.** design-changing · selected by score · strongest on C1 baseline recall ceiling (3/3). The most direct evidence available on the brief's first question (baseline recall ceiling of single-query search) and a template for benchmark construction (C1, C4), making it foundational to the whole scan.

**Why it matters here.** Gives the exact quantified recall ceiling of single-query search (BM25 vs dense vs commercial engines) that the brief names as the anchor everything else must be measured against, plus the benchmark-construction template for literature-search retrieval evaluation.

**Method.** New retrieval benchmark combining GPT-4-generated queries from inline-citation contexts and author-written questions about recent papers, expert-verified; extensive benchmarking of retrievers, LLM rerankers, and commercial search engines.

**Limitations.**

- focused on ML/NLP literature specifically, generalization to other scientific fields untested
- does not evaluate full agentic (multi-step) systems, only single-shot retrieval and reranking

<sub>selected: score · criteria: C1 3/3 · C2 0/3 · C3 3/3 · C4 3/3 · C5 1/3 · flags: methods_paper · verified 2026-08-27 via openalex, arxiv</sub>

## 7. Towards Recursive Self-Evolving Agentic Literature Retrieval

Yuwen Du, Tian Jin, Jing Kang, Xianghe Pang et al. · 2026 · arXiv · experimental · overall 3/3

<https://doi.org/10.48550/arxiv.2605.14306>

**Key finding.** PaSaMaster achieves a 16.5x higher F1-score than Google Scholar and a 37.8% higher F1-score than GPT-5.2 at about 1% of the cost across 38 disciplines, while reducing source hallucination from 32.66% to zero.

**Why it made the cut.** design-changing · selected by score · strongest on C1 baseline recall ceiling (3/3). A direct agentic literature-retrieval system with quantified gains over a database-style baseline and a frontier LLM, squarely answering the brief's core comparison questions.

**Why it matters here.** Directly anchors an agentic system's gain against a real database-style baseline (Google Scholar), giving the recall/F1 ceiling comparison the brief's C1 asks for, plus a named mechanism (self-evolving intent refinement) driving it.

**Method.** Recursive self-evolving retrieval agent that iteratively refines search intent from ranked evidence, ranks verified (non-generated) papers, and separates frontier-LLM planning from lightweight retrieval/scoring; evaluated on PaSaMaster-Bench.

**Limitations.**

- PaSaMaster-Bench's construction, labeling, and contamination controls are not described in the abstract
- F1 gains over Google Scholar are not decomposed by mechanism

<sub>selected: score · criteria: C1 3/3 · C2 2/3 · C3 3/3 · C4 1/3 · C5 0/3 · flags: methods_paper · verified 2026-08-27 via openalex, arxiv</sub>

## 8. LLM-guided Hierarchical Search for End-to-end Reasoning Intensive Retrieval

Nilesh Gupta, Wei-Cheng Chang, N. Bui, Cho-Jui Hsieh et al. · 2025 · no venue · experimental · overall 3/3

<https://arxiv.org/abs/2510.13217>

**Key finding.** LATTICE matches the best fine-tuned ensemble baseline on BRIGHT (46.7 nDCG@10) using a single off-the-shelf LLM with no embedding model in the loop, and an ensemble variant reaches 49.1 nDCG@10.

**Why it made the cut.** closely-related · selected by backfill · strongest on C3 retrieval/reranking method (3/3). A retrieval-method contribution explicitly targeting the failure mode of embedding-based top-k retrieval that agentic query-side fixes cannot solve, core to the brief's retrieval-layer question.

**Why it matters here.** Directly addresses the embedding-retriever recall ceiling and demonstrates a specific retrieval mechanism (LLM-guided hierarchical traversal replacing embedding search) as an alternative underlying technique for agentic search systems.

**Method.** LLM-guided hierarchical search index built top-down from multi-level document summaries, with calibrated path-aggregated LLM traversal; evaluated on BRIGHT plus NQ, SciFact, SciDocs.

**Limitations.**

- evaluated on general reasoning-intensive IR benchmarks rather than a literature-search-specific benchmark
- reranking outperforms at low token budgets, so gains are budget-dependent

<sub>selected: backfill · criteria: C1 2/3 · C2 2/3 · C3 3/3 · C4 1/3 · C5 1/3 · flags: methods_paper · verified 2026-08-27 via arxiv, s2</sub>

## 9. OpenScholar: Synthesizing Scientific Literature with Retrieval-augmented LMs

Akari Asai, Jacqueline He, Rulin Shao, Weijia Shi et al. · 2024 · arXiv.org · experimental · overall 3/3

<https://doi.org/10.48550/arxiv.2411.14199>

**Key finding.** OpenScholar, retrieving from 45M open-access papers, outperforms GPT-4o by 5% and PaperQA2 by 7% in correctness on the new ScholarQABench (2,967 expert queries), while GPT-4o hallucinates citations 78-90% of the time versus OpenScholar's expert-level citation accuracy.

**Why it made the cut.** design-changing · selected by backfill · strongest on C3 retrieval/reranking method (3/3). Directly on-brief: an agentic literature-synthesis system plus its own purpose-built benchmark, bearing on C1, C3, and C4 simultaneously.

**Why it matters here.** The closest prior work to the brief's exact system design (retrieval + synthesis for scientific literature), giving both a quantified system-level gain over strong baselines and a benchmark construction precedent that later comparisons should be checked against.

**Method.** Retrieval-augmented LM with a self-feedback inference loop over a purpose-built datastore; evaluated on a new large-scale multi-domain literature-search benchmark (ScholarQABench) with human expert comparison.

**Limitations.**

- gain attributed to the system as a whole rather than isolated to a specific agentic move (reformulation vs iterative retrieval vs self-feedback)
- correctness/citation-accuracy metrics may not directly measure recall ceiling of underlying single-query search

<sub>selected: backfill · criteria: C1 2/3 · C2 1/3 · C3 3/3 · C4 3/3 · C5 0/3 · flags: methods_paper · verified 2026-08-27 via openalex, arxiv</sub>

## 10. Deep Research Agents: A Systematic Examination And Roadmap

Yuxuan Huang, Yihang Chen, Haozhen Zhang, Kang Li et al. · 2025 · arXiv.org · other · overall 3/3

<https://doi.org/10.48550/arxiv.2506.18096>

**Key finding.** A systematic taxonomy of Deep Research agent architectures (static/dynamic workflows, single/multi-agent, API-based vs browser-based retrieval) with a critical evaluation identifying benchmark limitations including restricted external-knowledge access and metric-objective misalignment.

**Why it made the cut.** foundational · selected by review · strongest on C2 agentic mechanism gain (2/3). Foundational survey covering system designs, tool-use, and benchmark critique across the whole space the brief scans.

**Why it matters here.** The orientation piece the whole scan can be read against: it names the exact axes (information-acquisition strategy, planning strategy, benchmark misalignment) the brief's four decisions require, and its benchmark critique bears directly on decision 3.

**Method.** Narrative/taxonomic survey of Deep Research agent architectures, tool-use frameworks, and benchmarks, with a curated repository of related work.

**Limitations.**

- narrative review, not a systematic-review protocol
- no new empirical measurements or effect sizes

<sub>selected: review · criteria: C1 1/3 · C2 2/3 · C3 2/3 · C4 2/3 · C5 1/3 · flags: review · verified 2026-08-27 via arxiv</sub>

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

- [CG-RAG: Research Question Answering by Citation Graph Retrieval-Augmented LLMs](https://doi.org/10.1145/3726302.3729920) (2025) — overall 3/3
- [PaSa: An LLM Agent for Comprehensive Academic Paper Search](https://doi.org/10.48550/arxiv.2501.10120) (2025) — overall 3/3
- [BRIGHT: A Realistic and Challenging Benchmark for Reasoning-Intensive Retrieval](https://doi.org/10.48550/arxiv.2407.12883) (2024) — overall 3/3
- [Structurally-bounded Agentic Graph Exploration for Evidence-Grounded Scholarly DeepSearch](https://doi.org/10.48550/arxiv.2608.24809) (2026) — overall 3/3
- [Deep Research: A Survey of Autonomous Research Agents](https://doi.org/10.48550/arxiv.2508.12752) (2025) — overall 3/3
