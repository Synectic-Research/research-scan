# Evidence scan — p11-t2

Run `/Users/nabergoj/Projects/research-scan/research/experiments/phase12-selection/phase12b/runs/p11-t2/R40/O2/rep2/run` · brief `/Users/nabergoj/Projects/research-scan/research/experiments/phase12-selection/phase12b/runs/p11-t2/R40/O2/rep2/run/brief.md` · rendered 2026-08-26

| # | Paper | Year | Venue | Evidence | Verified |
|---|---|---|---|---|---|
| 1 | [Projecting BrowseComp-Plus onto ClimbMix: Toward More Realistic Corpora for Agentic Search](https://arxiv.org/abs/2608.20317) | 2026 | — | other | yes |
| 2 | [Patience is all you need! An agentic system for performing scientific literature review](https://doi.org/10.48550/arxiv.2504.08752) · 10.48550/arxiv.2504.08752 | 2025 | arXiv.org | experimental | yes |
| 3 | [Towards Recursive Self-Evolving Agentic Literature Retrieval](https://doi.org/10.48550/arxiv.2605.14306) · 10.48550/arxiv.2605.14306 | 2026 | arXiv | experimental | yes |
| 4 | [PaSa: An LLM Agent for Comprehensive Academic Paper Search](https://doi.org/10.48550/arxiv.2501.10120) · 10.48550/arxiv.2501.10120 | 2025 | Annual Meeting of the Association for Computational Linguistics | computational | yes |
| 5 | [Structurally-bounded Agentic Graph Exploration for Evidence-Grounded Scholarly DeepSearch](https://doi.org/10.48550/arxiv.2608.24809) · 10.48550/arxiv.2608.24809 | 2026 | arXiv | computational | yes |
| 6 | [ReBOL: Retrieval via Bayesian Optimization with Batched LLM Relevance Observations and Query Reformulation](https://doi.org/10.48550/arxiv.2603.20513) · 10.48550/arxiv.2603.20513 | 2026 | arXiv.org | computational | yes |
| 7 | [Open-Source Agentic Hybrid RAG Framework for Scientific Literature Review](https://doi.org/10.48550/arxiv.2508.05660) · 10.48550/arxiv.2508.05660 | 2025 | arXiv.org | experimental | yes |
| 8 | [CG-RAG: Research Question Answering by Citation Graph Retrieval-Augmented LLMs](https://doi.org/10.1145/3726302.3729920) · 10.1145/3726302.3729920 | 2025 | Annual International ACM SIGIR Conference on Research and Development in Information Retrieval | experimental | yes |
| 9 | [LitSearch: A Retrieval Benchmark for Scientific Literature Search](https://doi.org/10.48550/arxiv.2407.18940) · 10.48550/arxiv.2407.18940 | 2024 | Conference on Empirical Methods in Natural Language Processing | computational | yes |
| 10 | [Deep Research: A Survey of Autonomous Research Agents](https://doi.org/10.48550/arxiv.2508.12752) · 10.48550/arxiv.2508.12752 | 2025 | arXiv.org | other | yes |

## 1. Projecting BrowseComp-Plus onto ClimbMix: Toward More Realistic Corpora for Agentic Search

Sahel Sharifymoghaddam, Lin Gu, Yijun Ge, Jimmy Lin · 2026 · no venue · other · overall 3/3

<https://arxiv.org/abs/2608.20317>

**Key finding.** Relocating BrowseComp-Plus's evidence into a realistic 553M-document web corpus (ClimbMix) collapses the strongest agent's evidence recall from 84.3% to 21.4% (while issuing 63% more search calls) even though answer accuracy drops only five points, across 57 fully-grounded projected questions.

**Why it made the cut.** contradicting · selected by score · strongest on C4 benchmark construction (3/3). The strongest evidence that benchmark construction choices inflate reported agentic retrieval performance, with an explicitly stated method transfer to any decomposable benchmark, directly answering decision 4.

**Why it matters here.** Directly demonstrates that a benchmark's curated, query-specific corpus -- not genuine agent capability -- can be responsible for much of a reported evidence-recall figure, exactly the construction-inflates-gains failure mode decisions 3 and 4 ask the scan to surface, and its explicitly dataset-agnostic pipeline is stated to generalize to any decomposable benchmark.

**Method.** Dataset-agnostic projection pipeline decomposing questions into atomic reasoning hops and grounding each hop in a new corpus, retaining questions only when automatic verification, an independent agent, and human review all agree; applied to 830 BrowseComp-Plus questions to yield 57 validated ones.

**Limitations.**

- Small final validated set (57 questions) after strict verification
- corpus and queries are general web-search style, not scientific-literature search, though the pipeline claims domain-general applicability

<sub>selected: score · criteria: C1 2/3 · C2 1/3 · C3 1/3 · C4 3/3 · C5 3/3 · flags: contradicts, methods_paper · verified 2026-08-26 via arxiv, s2</sub>

## 2. Patience is all you need! An agentic system for performing scientific literature review

David W. Brett, Anniek Myatt · 2025 · arXiv.org · experimental · overall 3/3

<https://doi.org/10.48550/arxiv.2504.08752>

**Key finding.** A keyword-based (sparse) search-and-distillation system for scientific literature review achieves results close to state-of-the-art on biology literature benchmarks without needing dense retrieval infrastructure.

**Why it made the cut.** contradicting · selected by score · strongest on C1 baseline recall ceiling (3/3). A direct scientific-literature-review system showing simple sparse retrieval nearly matches more complex methods, evidence against the brief's premise that agentic/dense sophistication is necessary.

**Why it matters here.** Directly challenges the assumption that literature-search agents need complex dense or heavily agentic retrieval infrastructure to perform well, since sparse retrieval nearly matches the state of the art — exactly the premise-challenging evidence the brief's Q1/Q4 ask us to look for.

**Method.** LLM-based full-text search-and-distillation system evaluated against biology-related questions from existing literature benchmarks; compares sparse vs dense retrieval and shows a way to increase document coverage.

**Limitations.**

- evaluated only on biology-related questions
- abstract gives no numeric accuracy figures
- unclear how 'close to state of the art' is measured or which system is the comparator

<sub>selected: score · criteria: C1 3/3 · C2 1/3 · C3 2/3 · C4 1/3 · C5 2/3 · flags: contradicts, methods_paper · verified 2026-08-26 via openalex, arxiv</sub>

## 3. Towards Recursive Self-Evolving Agentic Literature Retrieval

Yuwen Du, Tian Jin, Jing Kang, Xianghe Pang et al. · 2026 · arXiv · experimental · overall 3/3

<https://doi.org/10.48550/arxiv.2605.14306>

**Key finding.** PaSaMaster achieves 16.5x higher F1 than Google Scholar and 37.8% higher F1 than GPT-5.2 at about 1% of the cost across 38 disciplines, reducing source hallucination from 32.66% in generative LLMs to zero.

**Why it made the cut.** design-changing · selected by score · strongest on C1 baseline recall ceiling (3/3). Provides the sharpest quantitative agentic-vs-single-query-search comparison in the shortlist, central to brief decisions 1 and 2.

**Why it matters here.** Directly measures agentic literature search against a real single-query search baseline (Google Scholar) with a large reported margin, giving a concrete number for decisions 1 and 2 -- though the premise-testing brief wants this margin checked against other benchmarks before it is trusted.

**Method.** Recursive self-evolving agentic retrieval combining self-evolving intent refinement, hallucination-free ranking over verified papers, and planning/retrieval cost separation, evaluated on PaSaMaster-Bench (38 disciplines) against Google Scholar and GPT-5.2.

**Limitations.**

- Comparator (Google Scholar) is a specific commercial search engine, not a controlled BM25/embedding baseline
- PaSaMaster-Bench construction details not given in the abstract
- self-reported gains with no independent replication

<sub>selected: score · criteria: C1 3/3 · C2 2/3 · C3 2/3 · C4 1/3 · C5 0/3 · verified 2026-08-26 via openalex, arxiv</sub>

## 4. PaSa: An LLM Agent for Comprehensive Academic Paper Search

Yichen He, Guanhua Huang, Peiyuan Feng, Yuan Lin et al. · 2025 · Annual Meeting of the Association for Computational Linguistics · computational · overall 3/3

<https://doi.org/10.48550/arxiv.2501.10120>

**Key finding.** PaSa-7B surpasses the best Google-based baseline by 37.78% in recall@20 and 39.90% in recall@50 on RealScholarQuery, and exceeds a GPT-4o-prompted version of itself by 30.36% in recall and 4.25% in precision.

**Why it made the cut.** foundational · selected by score · strongest on C4 benchmark construction (3/3). Foundational agentic paper-search system with an explicit benchmark-construction methodology and large reported recall gains over single-query search baselines.

**Why it matters here.** A reference agentic paper-search system giving concrete baseline-vs-agent recall numbers (C1/C2) and a worked benchmark-construction methodology from citation-derived synthetic queries plus real-world validation (C4), against which other benchmark-construction choices in this scan should be measured.

**Method.** RL-trained LLM agent that invokes search, reads papers, and selects references; trained on a synthetic 35k-query dataset (AutoScholarQuery) built from citations in top-tier AI conference papers, evaluated on a separate real-world query benchmark (RealScholarQuery).

**Limitations.**

- Training data (AutoScholarQuery) is synthetic and citation-derived, which could inflate performance on citation-adjacent queries relative to organic search tasks
- Abstract does not decompose the gain by individual agent action type (search vs. read vs. select)

<sub>selected: score · criteria: C1 2/3 · C2 2/3 · C3 1/3 · C4 3/3 · C5 0/3 · flags: methods_paper · verified 2026-08-26 via openalex, arxiv</sub>

## 5. Structurally-bounded Agentic Graph Exploration for Evidence-Grounded Scholarly DeepSearch

Rima Hazra, Sayan Layek, Somnath Banerjee, Soumen Chakrabarti et al. · 2026 · arXiv · computational · overall 3/3

<https://doi.org/10.48550/arxiv.2608.24809>

**Key finding.** Crase — one seed search, 1.5-hop citation-neighborhood expansion, entailment-based edge pruning, and recency-aware random-walk ranking — outperforms proprietary deep-research agents by up to 3x recall@50 at roughly a third of the cost on LitSearch and one further benchmark over a 500K-paper arXiv corpus.

**Why it made the cut.** design-changing · selected by score · strongest on C2 agentic mechanism gain (3/3). A citation-graph-traversal system with an explicit, bounded design reporting a specific multiplier gain over agentic baselines on the field's standard benchmark (LitSearch).

**Why it matters here.** Directly isolates citation-graph traversal with explicit stopping/pruning rules as the mechanism carrying the recall gain over both single-query search and open-ended agent loops, with a specific 3x recall@50 figure — exactly the C2 attribution the brief asks for, and argues bounded design beats unconstrained agentic search.

**Method.** Fixed, inspectable graph-exploration pipeline (no open-ended agent loop) evaluated against proprietary-model deep-research agents on LitSearch and one additional benchmark.

**Limitations.**

- Compares against proprietary deep-research agents rather than the plain single-query baseline directly, leaving C1 implicit
- Evaluated on only two benchmarks (LitSearch plus one more)

<sub>selected: score · criteria: C1 1/3 · C2 3/3 · C3 2/3 · C4 1/3 · C5 1/3 · flags: methods_paper · verified 2026-08-26 via arxiv</sub>

## 6. ReBOL: Retrieval via Bayesian Optimization with Batched LLM Relevance Observations and Query Reformulation

A. Korikov, Scott Sanner · 2026 · arXiv.org · computational · overall 3/3

<https://doi.org/10.48550/arxiv.2603.20513>

**Key finding.** ReBOL, which seeds a Bayesian-optimization posterior from LLM query reformulations and iteratively scores document batches, achieves 46.5% vs. 35.0% recall@100 and 63.6% vs. 61.2% NDCG@10 against the best LLM reranker baseline on Robust04.

**Why it made the cut.** design-changing · selected by score · strongest on C2 agentic mechanism gain (3/3). A retrieval/reranking method explicitly attributing a measured recall gain to query reformulation plus iterative optimization, directly answering what agentic moves add on top of top-k retrieval.

**Why it matters here.** Isolates query reformulation plus iterative batch acquisition as the mechanism recovering recall lost by top-k vector retrieval, giving a concrete, comparable recall gain (C2) for the retrieval/reranking layer underneath agentic literature search.

**Method.** Combines LLM query reformulation with multimodal Bayesian Optimization over document batches for iterative relevance scoring; evaluated on five BEIR datasets with two LLMs against LLM-reranker baselines.

**Limitations.**

- Evaluated on general BEIR retrieval datasets rather than a literature-search-specific benchmark
- Abstract does not report results on scientific literature corpora specifically

<sub>selected: score · criteria: C1 2/3 · C2 3/3 · C3 3/3 · C4 0/3 · C5 0/3 · flags: methods_paper · verified 2026-08-26 via openalex, arxiv</sub>

## 7. Open-Source Agentic Hybrid RAG Framework for Scientific Literature Review

Aditya Nagori, Ricardo Accorsi Casonatto, Ayush Gautam, Abhinav Manikantha Sai Cheruvu et al. · 2025 · arXiv.org · experimental · overall 3/3

<https://doi.org/10.48550/arxiv.2508.05660>

**Key finding.** An agent that dynamically selects between GraphRAG and VectorRAG per query, with DPO instruction tuning, achieves a 0.63 gain in Context Recall and a 0.56 gain in Context Precision on synthetic literature-review benchmarks, among smaller gains on other metrics.

**Why it made the cut.** design-changing · selected by score · strongest on C2 agentic mechanism gain (3/3). Directly attributes quantified gains to specific agentic retrieval-selection choices in a scientific-literature-review system, exactly the mechanism-attribution question the brief asks.

**Why it matters here.** Attributes a large, quantified gain to a specific agentic design choice — dynamic GraphRAG-vs-VectorRAG selection plus instruction tuning — directly answering the brief's Q2 for the exact scientific-literature-review setting it cares about.

**Method.** Autonomous agent orchestrating a Neo4j citation-graph KG and a FAISS vector store over PubMed/arXiv/Google Scholar data, with bootstrapped evaluation on synthetic query benchmarks against a baseline agent.

**Limitations.**

- evaluated on synthetic benchmarks 'mimicking' real queries rather than real user queries
- self-reported RAGAS-style metrics rather than an independent gold-labeled benchmark
- no comparison against a plain single-query database-search baseline

<sub>selected: score · criteria: C1 1/3 · C2 3/3 · C3 3/3 · C4 1/3 · C5 0/3 · flags: methods_paper · verified 2026-08-26 via openalex, arxiv</sub>

## 8. CG-RAG: Research Question Answering by Citation Graph Retrieval-Augmented LLMs

Yuntong Hu, Zhihan Lei, Zhongjie Dai, Allen Zhang et al. · 2025 · Annual International ACM SIGIR Conference on Research and Development in Information Retrieval · experimental · overall 3/3

<https://doi.org/10.1145/3726302.3729920>

**Key finding.** CG-RAG's contextual citation-graph representation plus Lexical-Semantic Graph Retrieval (LeSeGR), combining sparse and dense signals within the graph, significantly outperforms RAG methods paired with various state-of-the-art retrievers on research question-answering benchmarks.

**Why it made the cut.** design-changing · selected by backfill · strongest on C2 agentic mechanism gain (3/3). Directly evaluates the citation-graph-traversal mechanism for research-literature QA that the brief names as a specific agentic move to isolate.

**Why it matters here.** Directly attributes a measured gain to the citation-graph-traversal mechanism itself (via LeSeGR) rather than the system as a whole, answering the brief's Q2 for the exact mechanism it names, in the exact setting (research-literature QA) it cares about.

**Method.** New graph-based RAG framework built on citation graphs; hybrid sparse+dense retrieval encoded into the graph, evaluated across multiple research-QA benchmarks and domains.

**Limitations.**

- abstract gives no numeric effect sizes
- benchmark construction and baseline recall ceiling not described
- citation-graph coverage/quality dependencies not discussed

<sub>selected: backfill · criteria: C1 1/3 · C2 3/3 · C3 3/3 · C4 1/3 · C5 0/3 · flags: methods_paper · verified 2026-08-26 via crossref, openalex</sub>

## 9. LitSearch: A Retrieval Benchmark for Scientific Literature Search

Anirudh Ajith, Mengzhou Xia, Alexis Chevalier, Tanya Goyal et al. · 2024 · Conference on Empirical Methods in Natural Language Processing · computational · overall 3/3

<https://doi.org/10.48550/arxiv.2407.18940>

**Key finding.** LitSearch documents a 24.8 percentage-point absolute recall@5 gap between BM25 and the best dense retriever, LLM-based reranking further improves the best dense retriever by 4.4%, and commercial search engines including Google lag the best dense retriever by 32 points.

**Why it made the cut.** foundational · selected by backfill · strongest on C1 baseline recall ceiling (3/3). The benchmark other papers in this scan repeatedly reference; gives explicit baseline recall-ceiling numbers and a documented construction methodology.

**Why it matters here.** The field's standard literature-search retrieval benchmark and the clearest quantified statement of the single-query baseline ceiling (BM25 vs. dense vs. commercial search) that any agentic system's reported gain must be measured against, with an explicit, replicable construction recipe (C4).

**Method.** Constructs 597 realistic literature-search queries via GPT-4-generated questions from inline-citation paragraphs plus author-written questions about recent papers, expert-reviewed for quality; benchmarks state-of-the-art retrievers, LLM rerankers, and commercial search engines.

**Limitations.**

- Queries are ML/NLP-specific, so recall-ceiling numbers may not transfer to other scientific fields
- GPT-4-generated questions could carry construction artifacts absent from fully organic search queries

<sub>selected: backfill · criteria: C1 3/3 · C2 0/3 · C3 1/3 · C4 3/3 · C5 1/3 · flags: methods_paper · verified 2026-08-26 via openalex, arxiv</sub>

## 10. Deep Research: A Survey of Autonomous Research Agents

Wenlin Zhang, Xiaopeng Li, Yingyi Zhang, Pengyue Jia et al. · 2025 · arXiv.org · other · overall 3/3

<https://doi.org/10.48550/arxiv.2508.12752>

**Key finding.** The survey organizes the deep-research agent pipeline into four stages — planning, question developing, web exploration, and report generation — and catalogs representative methods, optimization techniques, and benchmarks for each.

**Why it made the cut.** foundational · selected by review · strongest on C1 baseline recall ceiling (1/3). The field's own synthesis of system designs and benchmarks for deep-research/literature-search agents, useful as an orienting map for this scan's other findings.

**Why it matters here.** Provides the taxonomy this scan can use to sort every other paper into the pipeline stage its agentic mechanism belongs to, and its benchmark summary is the reference point for checking whether the benchmarks found elsewhere are standard or fringe in the field.

**Method.** Systematic narrative survey of the deep-research agent literature; abstract-only, no primary experiments.

**Limitations.**

- A survey reflects the literature at time of writing and does not itself measure or replicate any gain
- Abstract does not state which specific benchmarks or failure modes it covers

<sub>selected: review · criteria: C1 1/3 · C2 1/3 · C3 1/3 · C4 1/3 · C5 1/3 · flags: review · verified 2026-08-26 via openalex, arxiv</sub>

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
- [Multi-Turn Agentic Scientific Literature Search via Workflow Induction](https://doi.org/10.48550/arxiv.2607.00597) (2026) — overall 3/3
- [LLM-guided Hierarchical Search for End-to-end Reasoning Intensive Retrieval](https://arxiv.org/abs/2510.13217) (2025) — overall 3/3
- [OpenScholar: Synthesizing Scientific Literature with Retrieval-augmented LMs](https://doi.org/10.48550/arxiv.2411.14199) (2024) — overall 3/3
- [HySemRAG: A Hybrid Semantic Retrieval-Augmented Generation Framework for Automated Literature Synthesis and Methodological Gap Analysis](https://doi.org/10.48550/arxiv.2508.05666) (2025) — overall 3/3
