# Evidence scan — p11-t2

Run `/Users/nabergoj/Projects/research-scan/research/experiments/phase12-selection/phase12b/runs/p11-t2/R40/O1/rep3/run` · brief `/Users/nabergoj/Projects/research-scan/research/experiments/phase12-selection/phase12b/runs/p11-t2/R40/O1/rep3/run/brief.md` · rendered 2026-08-26

| # | Paper | Year | Venue | Evidence | Verified |
|---|---|---|---|---|---|
| 1 | [BrowseComp-Plus: A More Fair and Transparent Evaluation Benchmark of Deep-Research Agent](https://doi.org/10.48550/arxiv.2508.06600) · 10.48550/arxiv.2508.06600 | 2025 | arXiv (Cornell University) | experimental | yes |
| 2 | [Structurally-bounded Agentic Graph Exploration for Evidence-Grounded Scholarly DeepSearch](https://doi.org/10.48550/arxiv.2608.24809) · 10.48550/arxiv.2608.24809 | 2026 | arXiv | experimental | yes |
| 3 | [Diagnosing Search Behavior and Failure Modes in Long-Horizon Search Agents](https://doi.org/10.48550/arxiv.2608.01913) · 10.48550/arxiv.2608.01913 | 2026 | arXiv | experimental | yes |
| 4 | [Projecting BrowseComp-Plus onto ClimbMix: Toward More Realistic Corpora for Agentic Search](https://arxiv.org/abs/2608.20317) | 2026 | — | experimental | yes |
| 5 | [LLM-guided Hierarchical Search for End-to-end Reasoning Intensive Retrieval](https://arxiv.org/abs/2510.13217) | 2025 | — | experimental | yes |
| 6 | [Patience is all you need! An agentic system for performing scientific literature review](https://doi.org/10.48550/arxiv.2504.08752) · 10.48550/arxiv.2504.08752 | 2025 | arXiv.org | computational | yes |
| 7 | [Fact, Fetch, and Reason: A Unified Evaluation of Retrieval-Augmented Generation](https://doi.org/10.48550/arxiv.2409.12941) · 10.48550/arxiv.2409.12941 | 2024 | North American Chapter of the Association for Computational Linguistics | computational | yes |
| 8 | [LitSearch: A Retrieval Benchmark for Scientific Literature Search](https://doi.org/10.48550/arxiv.2407.18940) · 10.48550/arxiv.2407.18940 | 2024 | Conference on Empirical Methods in Natural Language Processing | computational | yes |
| 9 | [Towards Recursive Self-Evolving Agentic Literature Retrieval](https://doi.org/10.48550/arxiv.2605.14306) · 10.48550/arxiv.2605.14306 | 2026 | arXiv | experimental | yes |
| 10 | [Deep Research: A Survey of Autonomous Research Agents](https://doi.org/10.48550/arxiv.2508.12752) · 10.48550/arxiv.2508.12752 | 2025 | arXiv.org | other | yes |

## 1. BrowseComp-Plus: A More Fair and Transparent Evaluation Benchmark of Deep-Research Agent

Zijian Chen, Xueguang Ma, Shengyao Zhuang, Ping Nie et al. · 2025 · arXiv (Cornell University) · experimental · overall 3/3

<https://doi.org/10.48550/arxiv.2508.06600>

**Key finding.** On BrowseComp-Plus's fixed, human-verified corpus, Search-R1 with BM25 achieves only 3.86% accuracy, GPT-5 alone reaches 55.9%, and GPT-5 with a Qwen3-Embedding-8B retriever reaches 70.1% while issuing fewer search calls.

**Why it made the cut.** design-changing · selected by score · strongest on C1 baseline recall ceiling (3/3). The field's reference benchmark for isolating retriever effect from agent reasoning, essential to the baseline-ceiling and benchmark-construction questions.

**Why it matters here.** The central artifact for Q1/Q3: gives a controlled way to disentangle retriever from agent contribution and shows the enormous swing (3.86%→70.1%) retriever choice alone produces, a figure any claimed agentic gain must be measured against.

**Method.** Introduces a fixed-corpus benchmark derived from BrowseComp with human-verified supporting documents and mined hard negatives, enabling controlled, reproducible separation of retriever quality from agent reasoning.

**Limitations.**

- Corpus, though fixed, is derived from BrowseComp and inherits any construction biases of the original benchmark
- exact corpus size and negative-mining details not given in this abstract

<sub>selected: score · criteria: C1 3/3 · C2 2/3 · C3 2/3 · C4 3/3 · C5 1/3 · verified 2026-08-26 via openalex, arxiv</sub>

## 2. Structurally-bounded Agentic Graph Exploration for Evidence-Grounded Scholarly DeepSearch

Rima Hazra, Sayan Layek, Somnath Banerjee, Soumen Chakrabarti et al. · 2026 · arXiv · experimental · overall 3/3

<https://doi.org/10.48550/arxiv.2608.24809>

**Key finding.** Crase, a bounded citation-graph exploration agent (single seed query, 1.5-hop citation expansion, entailment-based pruning, recency-aware random-walk ranking), outperforms proprietary-model deep research agents by up to 3x recall@50 at roughly a third of the cost on LitSearch and a second benchmark over a 500K-paper arXiv corpus.

**Why it made the cut.** design-changing · selected by score · strongest on C2 agentic mechanism gain (3/3). Directly attributes a measured recall gain to citation-graph traversal specifically, versus open-ended agentic search as a whole.

**Why it matters here.** Isolates citation-graph traversal as the specific mechanism carrying the gain (Q2), and shows a bounded, inspectable design beats open-ended agentic search loops at lower cost — directly actionable for which agentic move to build.

**Method.** Bounded graph-traversal pipeline (seed retrieval + citation-graph expansion + entailment-based edge pruning + recency-aware ranking) benchmarked against open-ended deep-research agents on two scholarly search benchmarks.

**Limitations.**

- Evaluated only on LitSearch and one further arXiv-restricted benchmark, may not generalize beyond CS/physics preprints
- comparison against proprietary deep-research agents whose exact configuration is opaque

<sub>selected: score · criteria: C1 2/3 · C2 3/3 · C3 3/3 · C4 1/3 · C5 2/3 · flags: methods_paper · verified 2026-08-26 via arxiv</sub>

## 3. Diagnosing Search Behavior and Failure Modes in Long-Horizon Search Agents

Qi Liu, Jiaxin Mao, Fengbin Zhu, Tat-Seng Chua · 2026 · arXiv · experimental · overall 3/3

<https://doi.org/10.48550/arxiv.2608.01913>

**Key finding.** Across six long-horizon search agents on BrowseComp-Plus and BrowseComp, answer accuracy correlates more with cumulative retrieval recall than with number of searches, and the best-performing agents issue far fewer redundant reformulated queries.

**Why it made the cut.** contradicting · selected by score · strongest on C2 agentic mechanism gain (3/3). Diagnoses which specific agentic behaviors (search volume, reformulation, evidence use) actually carry measured gains, the core mechanism-attribution question.

**Why it matters here.** Directly targets Q2/Q4: search effort (query count, context consumed) is only weakly tied to gains, while retrieval-evidence quality drives accuracy — undercutting the assumption that more agentic searching itself produces the improvement, and pointing to stopping-criteria design instead.

**Method.** Trajectory-level diagnosis using human-annotated document-level relevance judgments, comparing six agents on BrowseComp-Plus and validating on BrowseComp, with retrieval model and evaluation harness held fixed.

**Limitations.**

- Evaluated on curated deep-research benchmarks (BrowseComp-Plus/BrowseComp) rather than open scientific-literature corpora
- only six agents sampled, may not cover the full design space

<sub>selected: score · criteria: C1 2/3 · C2 3/3 · C3 1/3 · C4 1/3 · C5 3/3 · flags: contradicts · verified 2026-08-26 via openalex, arxiv</sub>

## 4. Projecting BrowseComp-Plus onto ClimbMix: Toward More Realistic Corpora for Agentic Search

Sahel Sharifymoghaddam, Lin Gu, Yijun Ge, Jimmy Lin · 2026 · no venue · experimental · overall 3/3

<https://arxiv.org/abs/2608.20317>

**Key finding.** Relocating BrowseComp-Plus's evidence into an independently-built 553M-document corpus (ClimbMix) drops the strongest agent's evidence recall from 84.3% to 21.4% and answer accuracy by five points, while requiring 63% more search calls.

**Why it made the cut.** contradicting · selected by score · strongest on C1 baseline recall ceiling (3/3). Directly demonstrates a reported agentic-search benchmark result shrinking under an independently constructed corpus — precisely the gain-replication-failure question.

**Why it matters here.** Directly answers Q4 for the field's flagship controlled benchmark: BrowseComp-Plus's per-query-curated corpus inflates evidence recall relative to an independently constructed corpus, meaning reported agentic gains on it likely overstate real-world retrieval difficulty.

**Method.** A projection pipeline decomposes benchmark questions into atomic reasoning hops and re-grounds each hop in a new corpus, validated by automatic verification, an independent agent, and human review; applied to 830 BrowseComp-Plus questions, yielding 57 fully-grounded questions.

**Limitations.**

- Yields only 57 grounded questions from an original 830, a large reduction in evaluable set size
- tested against a single projection target (ClimbMix); generalization to other corpora is untested

<sub>selected: score · criteria: C1 3/3 · C2 1/3 · C3 0/3 · C4 3/3 · C5 3/3 · flags: contradicts, methods_paper · verified 2026-08-26 via arxiv, s2</sub>

## 5. LLM-guided Hierarchical Search for End-to-end Reasoning Intensive Retrieval

Nilesh Gupta, Wei-Cheng Chang, N. Bui, Cho-Jui Hsieh et al. · 2025 · no venue · experimental · overall 3/3

<https://arxiv.org/abs/2510.13217>

**Key finding.** LATTICE achieves 46.7 nDCG@10 on the reasoning-intensive BRIGHT benchmark — matching the best fine-tuned ensemble baseline — while an ensemble variant, LATTICE++, reaches 49.1 nDCG@10, using LLM-guided hierarchical corpus traversal instead of an embedding retriever.

**Why it made the cut.** plan-influencing · selected by score · strongest on C1 baseline recall ceiling (3/3). Direct evidence on retrieval/reranking method design and on where embedding-based baselines break down for reasoning-heavy queries.

**Why it matters here.** Demonstrates that standard embedding-based top-k retrieval is a real recall bottleneck for reasoning-intensive queries and that LLM-guided traversal can match fine-tuned ensembles without an embedder in the loop — a concrete alternative retrieval layer for agentic literature-search systems (Q1/Q3).

**Method.** LLM-guided hierarchical search index built via top-down LLM judgments over multi-level document summaries, with calibrated path-aggregated traversal at query time; evaluated on BRIGHT, NQ, SciFact, and SciDocs.

**Limitations.**

- BRIGHT is a reasoning-intensive IR benchmark, not itself a literature-search benchmark
- index-construction cost and scalability to large scientific corpora are not detailed

<sub>selected: score · criteria: C1 3/3 · C2 2/3 · C3 3/3 · C4 0/3 · C5 2/3 · flags: methods_paper · verified 2026-08-26 via arxiv, s2</sub>

## 6. Patience is all you need! An agentic system for performing scientific literature review

David W. Brett, Anniek Myatt · 2025 · arXiv.org · computational · overall 3/3

<https://doi.org/10.48550/arxiv.2504.08752>

**Key finding.** Sparse (keyword-based) retrieval achieves results close to state-of-the-art dense retrieval on biology literature-review QA benchmarks, while also increasing coverage of relevant documents.

**Why it made the cut.** contradicting · selected by score · strongest on C1 baseline recall ceiling (3/3). Directly tests C1 (baseline recall ceiling) by comparing sparse vs dense retrieval for scientific literature agents.

**Why it matters here.** Directly tests whether the recall ceiling of simple single-query sparse search rivals dense retrieval, recalibrating how much credit is due to complex retrieval infrastructure in agentic systems.

**Method.** LLM-based agentic system for literature search and distillation, evaluated against biology-related questions from previously released literature benchmarks using sparse (keyword) retrieval; abstract-only for further scale details.

**Limitations.**

- Evaluated only on biology-domain benchmarks
- abstract does not report exact recall/precision numbers

<sub>selected: score · criteria: C1 3/3 · C2 1/3 · C3 3/3 · C4 1/3 · C5 2/3 · flags: contradicts, methods_paper · verified 2026-08-26 via openalex, arxiv</sub>

## 7. Fact, Fetch, and Reason: A Unified Evaluation of Retrieval-Augmented Generation

Satyapriya Krishna, Kalpesh Krishna, Anhad Mohananey, S. Schwarcz et al. · 2024 · North American Chapter of the Association for Computational Linguistics · computational · overall 3/3

<https://doi.org/10.48550/arxiv.2409.12941>

**Key finding.** State-of-the-art LLMs achieve only 0.40 accuracy on FRAMES multi-hop questions with no retrieval, rising to 0.66 (>50% relative improvement) with a proposed multi-step retrieval pipeline.

**Why it made the cut.** plan-influencing · selected by score · strongest on C1 baseline recall ceiling (3/3). Directly supplies the C1 baseline-ceiling number the brief calls the anchor against which agentic gains must be measured.

**Why it matters here.** Establishes a quantified no-retrieval baseline (0.40) against a multi-step retrieval gain (0.66), giving a concrete anchor for what fraction of an agentic system's improvement should be attributed to iterative retrieval versus the base model.

**Method.** New FRAMES benchmark of multi-hop questions requiring multi-source integration; baseline LLM-only performance compared against a multi-step retrieval pipeline.

**Limitations.**

- General RAG/QA benchmark, not specific to scientific literature
- Multi-step pipeline is not decomposed into individual agentic moves (reformulation vs. iteration)

<sub>selected: score · criteria: C1 3/3 · C2 2/3 · C3 2/3 · C4 3/3 · C5 0/3 · flags: methods_paper · verified 2026-08-26 via openalex, arxiv</sub>

## 8. LitSearch: A Retrieval Benchmark for Scientific Literature Search

Anirudh Ajith, Mengzhou Xia, Alexis Chevalier, Tanya Goyal et al. · 2024 · Conference on Empirical Methods in Natural Language Processing · computational · overall 3/3

<https://doi.org/10.48550/arxiv.2407.18940>

**Key finding.** LitSearch reveals a 24.8-point absolute recall@5 gap between BM25 and state-of-the-art dense retrievers on 597 realistic literature-search queries, with LLM-based reranking adding a further 4.4% improvement, while commercial search engines lag the best dense retriever by 32 points.

**Why it made the cut.** foundational · selected by backfill · strongest on C1 baseline recall ceiling (3/3). The foundational baseline-and-benchmark paper directly answering C1 and C4 for scientific literature search.

**Why it matters here.** Supplies the exact single-query database-search recall ceiling (BM25 vs. dense, vs. commercial search) the brief calls the anchor everything else must be measured against, plus a transparent benchmark-construction recipe.

**Method.** 597-query benchmark built from GPT-4-generated questions (from inline-citation contexts) plus author-written questions about recent papers, expert-vetted; extensive benchmarking of retrievers, rerankers, and commercial search engines.

**Limitations.**

- Restricted to recent ML/NLP papers, not broader scientific domains
- Recall@5 metric may not capture iterative/agentic retrieval's advantages over one-shot dense search

<sub>selected: backfill · criteria: C1 3/3 · C2 0/3 · C3 3/3 · C4 3/3 · C5 1/3 · flags: methods_paper · verified 2026-08-26 via openalex, arxiv</sub>

## 9. Towards Recursive Self-Evolving Agentic Literature Retrieval

Yuwen Du, Tian Jin, Jing Kang, Xianghe Pang et al. · 2026 · arXiv · experimental · overall 3/3

<https://doi.org/10.48550/arxiv.2605.14306>

**Key finding.** PaSaMaster achieves 16.5x higher F1 than Google Scholar and 37.8% higher F1 than GPT-5.2 at about 1% of the cost, while reducing citation hallucination from 32.66% to zero across 38 disciplines in PaSaMaster-Bench.

**Why it made the cut.** design-changing · selected by backfill · strongest on C3 retrieval/reranking method (3/3). Provides a quantified agentic-vs-baseline comparison plus a hallucination-reduction claim central to the brief's core questions.

**Why it matters here.** Directly anchors the recall/precision gap between plain search-engine baselines (Google Scholar) and an agentic, self-evolving retrieval loop, giving concrete magnitude for question 1 and 2.

**Method.** Recursive self-evolving retrieval agent separating frontier-LLM intent understanding from lightweight-model retrieval/scoring over verified papers; evaluated on a custom 38-discipline benchmark against Google Scholar and GPT-5.2.

**Limitations.**

- benchmark (PaSaMaster-Bench) construction details (labeling, contamination control) not given in the abstract
- comparison baseline is Google Scholar rather than a controlled single-query BM25/embedding search

<sub>selected: backfill · criteria: C1 2/3 · C2 2/3 · C3 3/3 · C4 2/3 · C5 0/3 · flags: methods_paper · verified 2026-08-26 via openalex, arxiv</sub>

## 10. Deep Research: A Survey of Autonomous Research Agents

Wenlin Zhang, Xiaopeng Li, Yingyi Zhang, Pengyue Jia et al. · 2025 · arXiv.org · other · overall 3/3

<https://doi.org/10.48550/arxiv.2508.12752>

**Key finding.** The survey decomposes deep-research agent pipelines into four stages (planning, question developing, web exploration, report generation) and categorizes representative methods, optimization techniques, and benchmarks for each.

**Why it made the cut.** plan-influencing · selected by review · strongest on C2 agentic mechanism gain (2/3). A recent systematic overview mapping directly onto the brief's four decision questions; the natural review anchor for the scan.

**Why it matters here.** Gives a structured taxonomy of exactly the agentic moves (query reformulation as 'question developing', crawling as 'web exploration') the brief needs to disentangle, and surveys the benchmark landscape in one place.

**Method.** Systematic literature survey covering agentic deep-research systems, their technical challenges, optimization techniques, and benchmarks.

**Limitations.**

- Survey synthesis rather than new empirical evidence
- May reflect optimistic framing typical of surveys advocating the paradigm they describe

<sub>selected: review · criteria: C1 1/3 · C2 2/3 · C3 2/3 · C4 2/3 · C5 1/3 · flags: review · verified 2026-08-26 via openalex, arxiv</sub>

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

- [ReBOL: Retrieval via Bayesian Optimization with Batched LLM Relevance Observations and Query Reformulation](https://doi.org/10.48550/arxiv.2603.20513) (2026) — overall 3/3
- [OpenScholar: Synthesizing Scientific Literature with Retrieval-augmented LMs](https://doi.org/10.48550/arxiv.2411.14199) (2024) — overall 3/3
- [PaSa: An LLM Agent for Comprehensive Academic Paper Search](https://doi.org/10.48550/arxiv.2501.10120) (2025) — overall 3/3
- [Multi-Agent System for Scientific Literature Search and Recommendation](https://doi.org/10.1109/icssas66150.2025.11081082) (2025) — overall 3/3
- [CG-RAG: Research Question Answering by Citation Graph Retrieval-Augmented LLMs](https://doi.org/10.1145/3726302.3729920) (2025) — overall 3/3
