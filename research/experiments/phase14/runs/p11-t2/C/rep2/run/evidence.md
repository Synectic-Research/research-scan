# Evidence scan — p11-t2

Run `/Users/nabergoj/Projects/research-scan/research/experiments/phase14/runs/p11-t2/C/rep2/run` · brief `/Users/nabergoj/Projects/research-scan/research/experiments/phase14/runs/p11-t2/C/rep2/run/brief.md` · rendered 2026-08-26

| # | Paper | Year | Venue | Evidence | Verified |
|---|---|---|---|---|---|
| 1 | [When to use Graphs in RAG: A Comprehensive Analysis for Graph Retrieval-Augmented Generation](https://doi.org/10.48550/arxiv.2506.05690) · 10.48550/arxiv.2506.05690 | 2025 | arXiv.org | experimental | yes |
| 2 | [Diagnosing Search Behavior and Failure Modes in Long-Horizon Search Agents](https://doi.org/10.48550/arxiv.2608.01913) · 10.48550/arxiv.2608.01913 | 2026 | arXiv | experimental | yes |
| 3 | [BrowseComp-Plus: A More Fair and Transparent Evaluation Benchmark of Deep-Research Agent](https://doi.org/10.48550/arxiv.2508.06600) · 10.48550/arxiv.2508.06600 | 2025 | arXiv (Cornell University) | experimental | yes |
| 4 | [BRIGHT: A Realistic and Challenging Benchmark for Reasoning-Intensive Retrieval](https://doi.org/10.48550/arxiv.2407.12883) · 10.48550/arxiv.2407.12883 | 2024 | International Conference on Learning Representations | experimental | yes |
| 5 | [LitSearch: A Retrieval Benchmark for Scientific Literature Search](https://doi.org/10.48550/arxiv.2407.18940) · 10.48550/arxiv.2407.18940 | 2024 | Conference on Empirical Methods in Natural Language Processing | experimental | yes |
| 6 | [Deep Research Agents: A Systematic Examination And Roadmap](https://doi.org/10.48550/arxiv.2506.18096) · 10.48550/arxiv.2506.18096 | 2025 | arXiv.org | other | yes |
| 7 | [Projecting BrowseComp-Plus onto ClimbMix: Toward More Realistic Corpora for Agentic Search](https://arxiv.org/abs/2608.20317) | 2026 | — | experimental | yes |
| 8 | [Towards Recursive Self-Evolving Agentic Literature Retrieval](https://doi.org/10.48550/arxiv.2605.14306) · 10.48550/arxiv.2605.14306 | 2026 | arXiv | experimental | yes |
| 9 | [PaSa: An LLM Agent for Comprehensive Academic Paper Search](https://doi.org/10.48550/arxiv.2501.10120) · 10.48550/arxiv.2501.10120 | 2025 | Annual Meeting of the Association for Computational Linguistics | experimental | yes |
| 10 | [Structurally-bounded Agentic Graph Exploration for Evidence-Grounded Scholarly DeepSearch](https://doi.org/10.48550/arxiv.2608.24809) · 10.48550/arxiv.2608.24809 | 2026 | arXiv | experimental | yes |

## 1. When to use Graphs in RAG: A Comprehensive Analysis for Graph Retrieval-Augmented Generation

Zhishang Xiang, Chuan-Yu Wu, Qinggang Zhang, Shengyuan Chen et al. · 2025 · arXiv.org · experimental · overall 3/3

<https://doi.org/10.48550/arxiv.2506.05690>

**Key finding.** GraphRAG frequently underperforms vanilla RAG on many real-world tasks; the new GraphRAG-Bench benchmark identifies the specific task and pipeline conditions under which graph structure does or does not help.

**Why it made the cut.** contradicting · selected by score · strongest on C2 agentic mechanism gain (3/3). Provides direct evidence and a benchmark precedent for when citation-graph-style traversal fails to beat baseline retrieval, the central contested premise the brief wants tested.

**Why it matters here.** Directly tests the premise that graph/citation-traversal mechanisms reliably beat baseline retrieval, showing they often do not -- exactly the hardest-case evidence decision 4 asks the scan to surface, with an explicit method/benchmark precedent.

**Method.** Comprehensive benchmark (GraphRAG-Bench) spanning fact retrieval, complex reasoning, contextual summarization, and creative generation, with systematic pipeline-wide evaluation from graph construction through generation.

**Limitations.**

- General RAG/QA setting rather than scientific literature search specifically
- Abstract gives no detail on contamination controls for the new benchmark

<sub>selected: score · criteria: C1 2/3 · C2 3/3 · C3 2/3 · C4 3/3 · C5 3/3 · flags: contradicts · verified 2026-08-26 via openalex, arxiv</sub>

## 2. Diagnosing Search Behavior and Failure Modes in Long-Horizon Search Agents

Qi Liu, Jiaxin Mao, Fengbin Zhu, Tat-Seng Chua · 2026 · arXiv · experimental · overall 3/3

<https://doi.org/10.48550/arxiv.2608.01913>

**Key finding.** Across six agents on BrowseComp-Plus and BrowseComp, answer accuracy tracks cumulative retrieval recall far better than search count or context consumed, and the best agents issue fewer redundant queries while worse agents keep searching after useful evidence is already found.

**Why it made the cut.** design-changing · selected by score · strongest on C2 agentic mechanism gain (3/3). A trajectory-level dissection of exactly which agentic behaviors (query formulation, stopping, evidence use) drive gains versus which produce low-yield search, using the field's own benchmark.

**Why it matters here.** Directly answers the brief's question 2 (which agentic moves carry the gain) and question 4 (where gains fail): search effort itself is only weakly linked to quality, undercutting the assumption that more iterative searching is inherently better.

**Method.** Trajectory-level diagnostic study with human-annotated document relevance judgments, decomposing failures into retrieval gaps and utilization gaps across six agents with retriever held fixed.

**Limitations.**

- only six agents studied
- relies on human relevance annotations that may not generalize to other corpora

<sub>selected: score · criteria: C1 2/3 · C2 3/3 · C3 1/3 · C4 2/3 · C5 3/3 · flags: contradicts · verified 2026-08-26 via openalex, arxiv</sub>

## 3. BrowseComp-Plus: A More Fair and Transparent Evaluation Benchmark of Deep-Research Agent

Zijian Chen, Xueguang Ma, Shengyao Zhuang, Ping Nie et al. · 2025 · arXiv (Cornell University) · experimental · overall 3/3

<https://doi.org/10.48550/arxiv.2508.06600>

**Key finding.** On a fixed, human-verified corpus, Search-R1 with BM25 achieves only 3.86% accuracy while GPT-5 reaches 55.9%, and pairing GPT-5 with a Qwen3-Embedding-8B retriever raises accuracy to 70.1% with fewer search calls.

**Why it made the cut.** foundational · selected by score · strongest on C1 baseline recall ceiling (3/3). The benchmark-construction and baseline-anchoring precedent for the entire deep-research-agent literature this scan is surveying.

**Why it matters here.** Directly answers the brief's questions 1 and 3: gives a concrete single-query BM25 recall/accuracy floor (3.86%) to anchor claimed agentic improvements against, and is itself the benchmark-construction precedent later work (including this scan's own dc6612fba47a) builds on and critiques.

**Method.** Benchmark construction paper: derives a fixed corpus with human-verified supporting documents and mined hard negatives from BrowseComp, enabling controlled, reproducible comparison of deep-research agents independent of live web APIs.

**Limitations.**

- fixed corpus still derived from BrowseComp's original query set, so evidence and distractors were selected per-query
- does not itself test agentic gain replication across corpora

<sub>selected: score · criteria: C1 3/3 · C2 2/3 · C3 2/3 · C4 3/3 · C5 1/3 · flags: methods_paper · verified 2026-08-26 via openalex, arxiv</sub>

## 4. BRIGHT: A Realistic and Challenging Benchmark for Reasoning-Intensive Retrieval

Hongjin Su, Howard Yen, Mengzhou Xia, Weijia Shi et al. · 2024 · International Conference on Learning Representations · experimental · overall 3/3

<https://doi.org/10.48550/arxiv.2407.12883>

**Key finding.** The leading MTEB retriever (SFR-Embedding-Mistral, 59.0 nDCG@10 on standard benchmarks) scores only 18.3 nDCG@10 on BRIGHT's reasoning-intensive queries, while explicit query reasoning recovers up to 12.2 points.

**Why it made the cut.** foundational · selected by score · strongest on C1 baseline recall ceiling (3/3). The clearest quantitative demonstration of how low single-query database/embedding search recall can fall, the anchor decision 1 needs.

**Why it matters here.** Gives a rigorous, quantified baseline recall ceiling for single-query embedding search under reasoning-intensive conditions -- exactly the anchor decision 1 requires before any agentic gain can be credited.

**Method.** New retrieval benchmark of 1,384 real-world, reasoning-intensive queries curated across diverse domains (economics, psychology, mathematics, coding), evaluated against state-of-the-art dense retrievers.

**Limitations.**

- Queries span diverse domains rather than scientific-literature-search specifically
- Evaluates retrieval alone, not a full agentic pipeline

<sub>selected: score · criteria: C1 3/3 · C2 2/3 · C3 2/3 · C4 3/3 · C5 0/3 · verified 2026-08-26 via openalex, arxiv</sub>

## 5. LitSearch: A Retrieval Benchmark for Scientific Literature Search

Anirudh Ajith, Mengzhou Xia, Alexis Chevalier, Tanya Goyal et al. · 2024 · Conference on Empirical Methods in Natural Language Processing · experimental · overall 3/3

<https://doi.org/10.48550/arxiv.2407.18940>

**Key finding.** On LitSearch (597 literature-search queries), dense retrievers beat BM25 by 24.8 points absolute recall@5, LLM-based reranking adds a further 4.4% improvement, and commercial search engines lag the best dense retriever by 32 points.

**Why it made the cut.** foundational · selected by score · strongest on C1 baseline recall ceiling (3/3). The most direct answer to the brief's baseline-ceiling question and a construction-transparent benchmark precedent that later agentic literature-search systems are compared against.

**Why it matters here.** Gives the concrete baseline recall-ceiling numbers (BM25 vs. dense vs. commercial search) the brief's first question asks for, plus a transparently constructed benchmark and a measured reranking gain, anchoring what 'improvement' should be measured against.

**Method.** Benchmark built from GPT-4-generated questions over cited paragraphs plus author-written queries about their own papers, manually expert-reviewed; benchmarked against BM25, dense retrievers, LLM rerankers, and commercial search.

**Limitations.**

- restricted to recent ML/NLP papers, not the full range of scientific disciplines
- queries are partly LLM-generated, which could introduce its own construction biases

<sub>selected: score · criteria: C1 3/3 · C2 0/3 · C3 3/3 · C4 3/3 · C5 1/3 · flags: methods_paper · verified 2026-08-26 via openalex, arxiv</sub>

## 6. Deep Research Agents: A Systematic Examination And Roadmap

Yuxuan Huang, Yihang Chen, Haozhen Zhang, Kang Li et al. · 2025 · arXiv.org · other · overall 3/3

<https://doi.org/10.48550/arxiv.2506.18096>

**Key finding.** A systematic taxonomy of Deep Research agent architectures (static/dynamic workflows, single/multi-agent, API vs browser-based retrieval) paired with a critical evaluation identifying restricted external-knowledge access, sequential execution inefficiencies, and metric-objective misalignment as key benchmark limitations.

**Why it made the cut.** plan-influencing · selected by score · strongest on C4 benchmark construction (3/3). The field-level synthesis that names the benchmark and metric weaknesses the brief specifically wants surfaced, earning its place as the review anchor for this scan.

**Why it matters here.** Synthesizes the field's architectural options and, crucially, names specific benchmark-construction and metric flaws that bear directly on the brief's question 3 and 4, shaping what to watch for when reading any single system's reported numbers.

**Method.** Narrative survey and taxonomy construction over the Deep Research agent literature, with an accompanying curated, continuously updated repository.

**Limitations.**

- narrative rather than systematic-protocol review
- synthesizes others' findings without new quantitative evidence

<sub>selected: score · criteria: C1 1/3 · C2 1/3 · C3 2/3 · C4 3/3 · C5 2/3 · flags: review · verified 2026-08-26 via arxiv</sub>

## 7. Projecting BrowseComp-Plus onto ClimbMix: Toward More Realistic Corpora for Agentic Search

Sahel Sharifymoghaddam, Lin Gu, Yijun Ge, Jimmy Lin · 2026 · no venue · experimental · overall 3/3

<https://arxiv.org/abs/2608.20317>

**Key finding.** Relocating BrowseComp-Plus's evidence into an independently-built 553M-document corpus (ClimbMix) drops the strongest agent's evidence recall from 84.3% to 21.4% and costs it five points of answer accuracy while it issues 63% more search calls, despite only 57 of 830 questions surviving full verification.

**Why it made the cut.** contradicting · selected by score · strongest on C4 benchmark construction (3/3). Directly shows a reported agentic-search gain collapsing under a corpus-construction change, the hardest-to-find evidence type the brief explicitly asked the scan to reach for.

**Why it matters here.** The clearest demonstrated case in this scan of a reported agentic gain failing to hold once the benchmark's per-query-curated corpus is replaced by an independently built one, directly answering the brief's question 4 and exposing exactly the construction artifact question 3 warns about.

**Method.** A projection pipeline that decomposes benchmark questions into atomic reasoning hops, re-grounds each hop in a corpus built without reference to any benchmark, and retains only questions verified by automatic checks, an independent agent, and human review.

**Limitations.**

- only 57 of 830 original questions survive the verification pipeline, a small resulting benchmark
- projection method is new and not yet independently validated by other groups

<sub>selected: score · criteria: C1 2/3 · C2 1/3 · C3 0/3 · C4 3/3 · C5 3/3 · flags: contradicts, methods_paper · verified 2026-08-26 via arxiv, s2</sub>

## 8. Towards Recursive Self-Evolving Agentic Literature Retrieval

Yuwen Du, Tian Jin, Jing Kang, Xianghe Pang et al. · 2026 · arXiv · experimental · overall 3/3

<https://doi.org/10.48550/arxiv.2605.14306>

**Key finding.** PaSaMaster achieves a 16.5x higher F1-score than Google Scholar and 37.8% higher F1-score than GPT-5.2 at about 1% of the cost, reducing source hallucination from 32.66% to zero across 38 disciplines.

**Why it made the cut.** design-changing · selected by score · strongest on C1 baseline recall ceiling (3/3). Central system paper quantifying agentic gains over a single-query database baseline in scientific literature retrieval, directly answering the brief's first two decisions.

**Why it matters here.** Directly quantifies the gap between a single-query search-engine baseline (Google Scholar) and an iterative, self-evolving agentic design, giving the clearest available anchor for decision 1 and 2.

**Method.** Recursive self-evolving agentic retrieval combining iterative intent refinement, hallucination-free ranking over verified papers, and planning/retrieval model separation; evaluated on PaSaMaster-Bench.

**Limitations.**

- PaSaMaster-Bench construction (query source, labeling) not detailed in the abstract
- Self-reported comparison without independent replication

<sub>selected: score · criteria: C1 3/3 · C2 3/3 · C3 2/3 · C4 1/3 · C5 0/3 · verified 2026-08-26 via openalex, arxiv</sub>

## 9. PaSa: An LLM Agent for Comprehensive Academic Paper Search

Yichen He, Guanhua Huang, Peiyuan Feng, Yuan Lin et al. · 2025 · Annual Meeting of the Association for Computational Linguistics · experimental · overall 3/3

<https://doi.org/10.48550/arxiv.2501.10120>

**Key finding.** PaSa-7B exceeds the best Google-based baseline by 37.78% in recall@20 and 39.90% in recall@50 on RealScholarQuery, and surpasses a prompted GPT-4o version of itself by 30.36% recall.

**Why it made the cut.** design-changing · selected by backfill · strongest on C1 baseline recall ceiling (3/3). Foundational system+benchmark pairing for agentic academic paper search, directly measuring recall gain over single-query search-engine baselines.

**Why it matters here.** The closest prior work to the brief's central object: a comprehensive agentic paper-search system with an explicit single-query-search baseline (Google/Google+GPT-4o) and its own purpose-built benchmark, letting us anchor how much agentic search actually adds over a search-API baseline.

**Method.** RL-trained LLM agent that invokes search tools, reads papers, and selects references; trained on synthetic AutoScholarQuery (35k queries) and evaluated on RealScholarQuery, a hand-built real-world benchmark.

**Limitations.**

- trained on synthetic queries even though evaluated on real ones
- recall numbers are self-reported against the authors' own benchmark

<sub>selected: backfill · criteria: C1 3/3 · C2 2/3 · C3 1/3 · C4 3/3 · C5 0/3 · flags: methods_paper · verified 2026-08-26 via openalex, arxiv</sub>

## 10. Structurally-bounded Agentic Graph Exploration for Evidence-Grounded Scholarly DeepSearch

Rima Hazra, Sayan Layek, Somnath Banerjee, Soumen Chakrabarti et al. · 2026 · arXiv · experimental · overall 3/3

<https://doi.org/10.48550/arxiv.2608.24809>

**Key finding.** A bounded citation-graph agent (single seed search, 1.5-hop citation expansion, entailment pruning, recency-aware random-walk ranking) outperforms deep-research agents built on proprietary models by up to 3x recall@50 at roughly a third of the cost on LitSearch and one further benchmark.

**Why it made the cut.** design-changing · selected by backfill · strongest on C2 agentic mechanism gain (3/3). Explicitly attributes a large, quantified recall gain to citation-graph traversal specifically rather than to an undifferentiated agentic system.

**Why it matters here.** Directly isolates citation-graph traversal as the mechanism carrying the gain over open-ended agentic search loops, exactly the decomposition the brief's question 2 is asking for.

**Method.** System design paper: fixed candidate set derived from one seed query, expanded via 1.5-hop citation neighborhood, pruned by entailment, ranked by random walk, evaluated over a 500K-paper arXiv corpus.

**Limitations.**

- single seed-query design may miss papers outside the 1.5-hop neighborhood
- evaluated on only two benchmarks over one corpus

<sub>selected: backfill · criteria: C1 2/3 · C2 3/3 · C3 2/3 · C4 2/3 · C5 0/3 · flags: methods_paper · verified 2026-08-26 via arxiv</sub>

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
- [OpenScholar: Synthesizing Scientific Literature with Retrieval-augmented LMs](https://doi.org/10.48550/arxiv.2411.14199) (2024) — overall 3/3
- [Deep Research: A Survey of Autonomous Research Agents](https://doi.org/10.48550/arxiv.2508.12752) (2025) — overall 3/3
- [Multi-Agent System for Scientific Literature Search and Recommendation](https://doi.org/10.1109/icssas66150.2025.11081082) (2025) — overall 3/3
- [Multi-Turn Agentic Scientific Literature Search via Workflow Induction](https://doi.org/10.48550/arxiv.2607.00597) (2026) — overall 3/3
