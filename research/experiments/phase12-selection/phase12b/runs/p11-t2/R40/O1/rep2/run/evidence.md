# Evidence scan — p11-t2

Run `/Users/nabergoj/Projects/research-scan/research/experiments/phase12-selection/phase12b/runs/p11-t2/R40/O1/rep2/run` · brief `/Users/nabergoj/Projects/research-scan/research/experiments/phase12-selection/phase12b/runs/p11-t2/R40/O1/rep2/run/brief.md` · rendered 2026-08-26

| # | Paper | Year | Venue | Evidence | Verified |
|---|---|---|---|---|---|
| 1 | [LitSearch: A Retrieval Benchmark for Scientific Literature Search](https://doi.org/10.48550/arxiv.2407.18940) · 10.48550/arxiv.2407.18940 | 2024 | Conference on Empirical Methods in Natural Language Processing | experimental | yes |
| 2 | [LLM-guided Hierarchical Search for End-to-end Reasoning Intensive Retrieval](https://arxiv.org/abs/2510.13217) | 2025 | — | experimental | yes |
| 3 | [Patience is all you need! An agentic system for performing scientific literature review](https://doi.org/10.48550/arxiv.2504.08752) · 10.48550/arxiv.2504.08752 | 2025 | arXiv.org | experimental | yes |
| 4 | [OpenScholar: Synthesizing Scientific Literature with Retrieval-augmented LMs](https://doi.org/10.48550/arxiv.2411.14199) · 10.48550/arxiv.2411.14199 | 2024 | arXiv.org | experimental | yes |
| 5 | [Diagnosing Search Behavior and Failure Modes in Long-Horizon Search Agents](https://doi.org/10.48550/arxiv.2608.01913) · 10.48550/arxiv.2608.01913 | 2026 | arXiv | experimental | yes |
| 6 | [BrowseComp-Plus: A More Fair and Transparent Evaluation Benchmark of Deep-Research Agent](https://doi.org/10.48550/arxiv.2508.06600) · 10.48550/arxiv.2508.06600 | 2025 | arXiv (Cornell University) | experimental | yes |
| 7 | [ReBOL: Retrieval via Bayesian Optimization with Batched LLM Relevance Observations and Query Reformulation](https://doi.org/10.48550/arxiv.2603.20513) · 10.48550/arxiv.2603.20513 | 2026 | arXiv.org | experimental | yes |
| 8 | [Multi-Agent System for Scientific Literature Search and Recommendation](https://doi.org/10.1109/icssas66150.2025.11081082) · 10.1109/icssas66150.2025.11081082 | 2025 | — | experimental | yes |
| 9 | [Deep Research Agents: A Systematic Examination And Roadmap](https://doi.org/10.48550/arxiv.2506.18096) · 10.48550/arxiv.2506.18096 | 2025 | arXiv.org | other | yes |
| 10 | [Projecting BrowseComp-Plus onto ClimbMix: Toward More Realistic Corpora for Agentic Search](https://arxiv.org/abs/2608.20317) | 2026 | — | experimental | yes |

## 1. LitSearch: A Retrieval Benchmark for Scientific Literature Search

Anirudh Ajith, Mengzhou Xia, Alexis Chevalier, Tanya Goyal et al. · 2024 · Conference on Empirical Methods in Natural Language Processing · experimental · overall 3/3

<https://doi.org/10.48550/arxiv.2407.18940>

**Key finding.** On the 597-query LitSearch benchmark, dense retrievers outperform BM25 by 24.8 absolute points in recall@5, LLM reranking adds a further 4.4% over the best dense retriever, and commercial search engines like Google Search lag the best dense retriever by 32 points.

**Why it made the cut.** design-changing · selected by score · strongest on C1 baseline recall ceiling (3/3). Directly quantifies the BM25 recall ceiling versus dense retrieval and reranking on a well-documented literature-search benchmark — the anchor baseline the brief's decision 1 asks for.

**Why it matters here.** Gives an explicit, quantified single-query BM25 baseline and its gap to dense retrieval and reranking — precisely the recall-ceiling number decision 1 says every other claimed improvement must be measured against — plus a transparent benchmark-construction recipe for decision 3.

**Method.** New retrieval benchmark built from GPT-4-generated questions drawn from citation contexts plus author-written questions about recent papers, expert-verified; benchmarks BM25, dense retrievers, and LLM reranking pipelines.

**Limitations.**

- ML/NLP-paper domain only, unclear generalization to other sciences
- does not evaluate full agentic (multi-turn/crawling) systems, only single-shot retrieval and reranking

<sub>selected: score · criteria: C1 3/3 · C2 1/3 · C3 3/3 · C4 3/3 · C5 2/3 · flags: methods_paper · verified 2026-08-26 via openalex, arxiv</sub>

## 2. LLM-guided Hierarchical Search for End-to-end Reasoning Intensive Retrieval

Nilesh Gupta, Wei-Cheng Chang, N. Bui, Cho-Jui Hsieh et al. · 2025 · no venue · experimental · overall 3/3

<https://arxiv.org/abs/2510.13217>

**Key finding.** LATTICE, an LLM-guided hierarchical search index with no embedding model at query time, matches the best fine-tuned ensemble on BRIGHT (46.7 nDCG@10) and reaches 49.1 with a lightweight ensemble, while showing standard embedding-retriever-plus-LLM-verifier pipelines fail when the right documents are not in the embedding top-k.

**Why it made the cut.** design-changing · selected by score · strongest on C1 baseline recall ceiling (3/3). Empirically shows where embedding-based single-query retrieval breaks down and proposes an alternative retrieval mechanism, directly answering decisions 1 and 2 with numbers.

**Why it matters here.** Directly demonstrates a failure mode of the single-query embedding retrieval baseline for reasoning-intensive queries and offers a retrieval architecture that avoids depending on embedding top-k recall, bearing on both the baseline ceiling question and the retrieval-layer design decision.

**Method.** Top-down LLM-guided construction of a hierarchical document index from multi-level summaries, with calibrated path-aggregated LLM traversal; evaluated on BRIGHT (reasoning-intensive IR) plus NQ, SciFact, SciDocs.

**Limitations.**

- reasoning-intensive setting (BRIGHT) may not represent typical literature-search queries
- convergence to higher asymptote requires moderate token budget, worse than reranking at low budgets
- abstract does not report benchmark construction details for BRIGHT itself

<sub>selected: score · criteria: C1 3/3 · C2 2/3 · C3 3/3 · C4 1/3 · C5 2/3 · flags: methods_paper · verified 2026-08-26 via arxiv, s2</sub>

## 3. Patience is all you need! An agentic system for performing scientific literature review

David W. Brett, Anniek Myatt · 2025 · arXiv.org · experimental · overall 3/3

<https://doi.org/10.48550/arxiv.2504.08752>

**Key finding.** Sparse (keyword-based) retrieval achieves results close to state-of-the-art dense retrieval for LLM-based literature search over biology benchmarks, while also increasing coverage of relevant documents for review generation.

**Why it made the cut.** contradicting · selected by score · strongest on C1 baseline recall ceiling (3/3). Tests whether the baseline sparse/keyword retrieval ceiling is actually much lower than agentic systems, directly informing decision 1.

**Why it matters here.** Directly challenges the premise that sophisticated dense/agentic retrieval infrastructure is necessary — suggests the single-query sparse-search ceiling is already close to SOTA, which changes the baseline improvement claims must be measured against.

**Method.** LLM-based literature review system evaluated on biology-focused literature benchmarks; compares sparse (keyword-based) vs dense retrieval approaches.

**Limitations.**

- biology-specific benchmarks, may not generalize across domains
- abstract does not quantify the 'close to SOTA' gap numerically

<sub>selected: score · criteria: C1 3/3 · C2 2/3 · C3 3/3 · C4 1/3 · C5 2/3 · flags: contradicts · verified 2026-08-26 via openalex, arxiv</sub>

## 4. OpenScholar: Synthesizing Scientific Literature with Retrieval-augmented LMs

Akari Asai, Jacqueline He, Rulin Shao, Weijia Shi et al. · 2024 · arXiv.org · experimental · overall 3/3

<https://doi.org/10.48550/arxiv.2411.14199>

**Key finding.** OpenScholar-8B, retrieving from 45 million open-access papers with a self-feedback inference loop, outperforms GPT-4o by 5% and PaperQA2 by 7% in correctness on the 2,967-query ScholarQABench benchmark, while GPT-4o hallucinates citations 78-90% of the time versus near-human citation accuracy for OpenScholar.

**Why it made the cut.** design-changing · selected by score · strongest on C3 retrieval/reranking method (3/3). A flagship literature-search system with a purpose-built benchmark and quantified gains over closed-book LLMs and a competing literature-search tool, central to nearly every decision in the brief.

**Why it matters here.** Directly quantifies the gain from retrieval-plus-self-feedback over closed-book LLMs and a prior literature-search tool (PaperQA2), and introduces a large expert-curated benchmark — bears on decisions 1, 2, and 3 simultaneously.

**Method.** Retrieval-augmented LM with a purpose-built datastore and retriever, evaluated on the newly constructed multi-domain ScholarQABench benchmark plus human preference evaluation.

**Limitations.**

- benchmark queries are expert-written but largely single-shot rather than testing iterative/multi-turn agentic behavior explicitly
- comparison baselines (GPT-4o, PaperQA2) may have shifted since publication

<sub>selected: score · criteria: C1 2/3 · C2 2/3 · C3 3/3 · C4 3/3 · C5 1/3 · flags: methods_paper · verified 2026-08-26 via openalex, arxiv</sub>

## 5. Diagnosing Search Behavior and Failure Modes in Long-Horizon Search Agents

Qi Liu, Jiaxin Mao, Fengbin Zhu, Tat-Seng Chua · 2026 · arXiv · experimental · overall 3/3

<https://doi.org/10.48550/arxiv.2608.01913>

**Key finding.** Across six deep-search agents on BrowseComp-Plus and BrowseComp, answer accuracy tracks cumulative retrieval recall far more than search effort, and the best agents issue far fewer redundant queries despite useful evidence typically surfacing early.

**Why it made the cut.** design-changing · selected by score · strongest on C2 agentic mechanism gain (3/3). Directly decomposes agentic search behavior into retrieval vs. utilization, the causal attribution the brief asks for in C2 and a caution against the premise in C5.

**Why it matters here.** Directly answers what agentic effort actually buys: it shows more searching is not the mechanism of improvement, redirecting the design question toward evidence selection, context management, and stopping criteria rather than iteration volume.

**Method.** Trajectory-level diagnosis with human-annotated document relevance judgments, decomposing failures into retrieval gaps vs. utilization gaps; retrieval model and evaluation harness held fixed across six agents, validated on two benchmarks.

**Limitations.**

- only six agents compared
- relies on document-level relevance judgments that may not generalize across corpora
- does not isolate which specific reformulation strategies work

<sub>selected: score · criteria: C1 1/3 · C2 3/3 · C3 1/3 · C4 2/3 · C5 3/3 · verified 2026-08-26 via openalex, arxiv</sub>

## 6. BrowseComp-Plus: A More Fair and Transparent Evaluation Benchmark of Deep-Research Agent

Zijian Chen, Xueguang Ma, Shengyao Zhuang, Ping Nie et al. · 2025 · arXiv (Cornell University) · experimental · overall 3/3

<https://doi.org/10.48550/arxiv.2508.06600>

**Key finding.** On a fixed, human-verified corpus, Search-R1 with BM25 reaches only 3.86% accuracy while GPT-5 reaches 55.9%, and pairing GPT-5 with a Qwen3-Embedding retriever raises accuracy to 70.1% with fewer search calls.

**Why it made the cut.** foundational · selected by score · strongest on C1 baseline recall ceiling (3/3). The core benchmark-construction paper for controlled deep-research evaluation, giving explicit single-query baseline numbers the brief's decision 1 needs and the reference point for later replication/generalization checks.

**Why it matters here.** Provides the concrete, numeric baseline recall/accuracy ceiling for single-query retrieval (BM25 vs. dense) that other agentic gains must be measured against, and is the benchmark other shortlisted papers (the diagnosis paper, the ClimbMix projection) build directly on.

**Method.** Benchmark derived from BrowseComp using a fixed curated corpus with human-verified supporting documents and mined hard negatives, enabling disentangled evaluation of agent reasoning versus retriever quality.

**Limitations.**

- corpus is derived per-query from the benchmark's own supporting documents and negatives, a construction concern later work (ClimbMix projection) explicitly raises
- fixed corpus may not reflect open-web search difficulty
- accuracy metric conflates retrieval and reasoning contributions somewhat despite disentanglement design

<sub>selected: score · criteria: C1 3/3 · C2 1/3 · C3 2/3 · C4 3/3 · C5 1/3 · flags: methods_paper · verified 2026-08-26 via openalex, arxiv</sub>

## 7. ReBOL: Retrieval via Bayesian Optimization with Batched LLM Relevance Observations and Query Reformulation

A. Korikov, Scott Sanner · 2026 · arXiv.org · experimental · overall 3/3

<https://doi.org/10.48550/arxiv.2603.20513>

**Key finding.** ReBOL, which uses LLM query reformulations to seed a Bayesian-optimization posterior over relevance and iteratively acquires document batches for LLM scoring, beats the best LLM reranker baseline on Robust04 (46.5% vs. 35.0% recall@100) at comparable latency.

**Why it made the cut.** plan-influencing · selected by score · strongest on C2 agentic mechanism gain (3/3). A retrieval/reranking method paper isolating query reformulation's contribution to recall gains, squarely in scope of C3 and useful evidence for C2's mechanism-attribution question.

**Why it matters here.** Gives a concrete retrieval/reranking mechanism that separates the contribution of query reformulation from downstream vector search, directly informing how the retrieval layer under an agentic literature-search system should be built and measured.

**Method.** Bayesian optimization over document relevance seeded by LLM query reformulation and updated via iterative LLM batch scoring, evaluated on five BEIR datasets with two LLMs against LLM-reranker baselines.

**Limitations.**

- evaluated on general BEIR datasets, not a literature-search-specific benchmark
- gains vary by dataset (competitive rather than dominant on NDCG@10)
- adds Bayesian-optimization overhead requiring latency management

<sub>selected: score · criteria: C1 2/3 · C2 3/3 · C3 3/3 · C4 1/3 · C5 1/3 · flags: methods_paper · verified 2026-08-26 via openalex, arxiv</sub>

## 8. Multi-Agent System for Scientific Literature Search and Recommendation

Aswathy K Cherian, Naman Srivastava, Samyak Varia · 2025 · no venue · experimental · overall 3/3

<https://doi.org/10.1109/icssas66150.2025.11081082>

**Key finding.** A three-agent (Query, Retrieval, Learning) hybrid BM25+FAISS literature search system achieves 8.5% precision improvement, 7.3% recall improvement, and about 210ms lower response latency versus PaperQA and Semantic Scholar.

**Why it made the cut.** design-changing · selected by backfill · strongest on C1 baseline recall ceiling (3/3). A literature-search-specific multi-agent system with quantified precision/recall gains attributable to a query-reformulation agent, exactly the system design and mechanism the brief investigates.

**Why it matters here.** Directly quantifies the gain from a query-reformulation agent plus hybrid retrieval over existing literature-search baselines, giving concrete numbers for decisions 1 and 2.

**Method.** FastAPI-based multi-agent hybrid sparse/dense retrieval system, experimentally compared against PaperQA and Semantic Scholar on precision, recall, and latency.

**Limitations.**

- small, non-peer-reviewed venue with limited detail on evaluation set construction
- only one citation reported, unclear evaluation rigor and reproducibility

<sub>selected: backfill · criteria: C1 3/3 · C2 3/3 · C3 3/3 · C4 1/3 · C5 0/3 · flags: methods_paper · verified 2026-08-26 via crossref, openalex</sub>

## 9. Deep Research Agents: A Systematic Examination And Roadmap

Yuxuan Huang, Yihang Chen, Haozhen Zhang, Kang Li et al. · 2025 · arXiv.org · other · overall 3/3

<https://doi.org/10.48550/arxiv.2506.18096>

**Key finding.** A systematic taxonomy of Deep Research agents finds that current benchmarks suffer from restricted external-knowledge access, sequential execution inefficiencies, and misalignment between evaluation metrics and agents' practical objectives.

**Why it made the cut.** closely-related · selected by review · strongest on C4 benchmark construction (3/3). The field-level review that names the same benchmark-construction and evaluation-metric weaknesses the brief's decisions 3 and 4 are built around, earning its guaranteed review slot.

**Why it matters here.** Synthesizes exactly the construction flaws in current benchmarks that the brief's decision 3 and 4 ask about, giving a structured map of where reported gains and evaluation numbers may be unreliable across the field rather than in a single system.

**Method.** Narrative/systematic review and taxonomy of Deep Research agent architectures (static vs. dynamic workflows, single- vs. multi-agent), information-acquisition strategies, tool-use frameworks, and a critical evaluation of existing benchmarks.

**Limitations.**

- narrative synthesis rather than new empirical results
- taxonomy may already be dated given the pace of 2025-2026 releases
- does not quantify how much benchmark misalignment inflates specific reported gains

<sub>selected: review · criteria: C1 1/3 · C2 2/3 · C3 1/3 · C4 3/3 · C5 2/3 · flags: review · verified 2026-08-26 via arxiv</sub>

## 10. Projecting BrowseComp-Plus onto ClimbMix: Toward More Realistic Corpora for Agentic Search

Sahel Sharifymoghaddam, Lin Gu, Yijun Ge, Jimmy Lin · 2026 · no venue · experimental · overall 3/3

<https://arxiv.org/abs/2608.20317>

**Key finding.** Relocating BrowseComp-Plus's evidence into a benchmark-agnostic 400B-token corpus (ClimbMix) drops the strongest agent's evidence recall from 84.3% to 21.4% and answer accuracy by five points, despite 63% more search calls.

**Why it made the cut.** contradicting · selected by backfill · strongest on C4 benchmark construction (3/3). The clearest evidence in the shortlist that a widely-used agentic benchmark's reported gains shrink dramatically under a more realistic, independently-built corpus, directly serving decision 4.

**Why it matters here.** Directly shows that a headline agentic-search benchmark's reported performance was inflated by a corpus built per-query from the benchmark's own evidence and negatives -- exactly the gain-replication failure the brief's decision 4 is looking for.

**Method.** A projection pipeline decomposes benchmark questions into atomic reasoning hops and re-grounds each hop in an independently-built 553M-document corpus, retaining only fully-verified questions (57 of 830 BrowseComp-Plus questions survived), then re-evaluates agents on the harder corpus.

**Limitations.**

- only 57 of 830 original questions survive the grounding pipeline, a small resulting benchmark
- single benchmark (BrowseComp-Plus) projected so far, described as the first of a planned series
- projection pipeline's own verification (automatic + agent + human) could itself introduce selection effects

<sub>selected: backfill · criteria: C1 1/3 · C2 1/3 · C3 1/3 · C4 3/3 · C5 3/3 · flags: contradicts, methods_paper · verified 2026-08-26 via arxiv, s2</sub>

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

- [Structurally-bounded Agentic Graph Exploration for Evidence-Grounded Scholarly DeepSearch](https://doi.org/10.48550/arxiv.2608.24809) (2026) — overall 3/3
- [Towards Recursive Self-Evolving Agentic Literature Retrieval](https://doi.org/10.48550/arxiv.2605.14306) (2026) — overall 3/3
- [CG-RAG: Research Question Answering by Citation Graph Retrieval-Augmented LLMs](https://doi.org/10.1145/3726302.3729920) (2025) — overall 3/3
- [PaSa: An LLM Agent for Comprehensive Academic Paper Search](https://doi.org/10.48550/arxiv.2501.10120) (2025) — overall 3/3
- [Deep Research: A Survey of Autonomous Research Agents](https://doi.org/10.48550/arxiv.2508.12752) (2025) — overall 3/3
