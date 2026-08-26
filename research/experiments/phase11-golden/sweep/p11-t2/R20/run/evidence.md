# Evidence scan — p11-t2

Run `/Users/nabergoj/Projects/research-scan/research/experiments/phase11-golden/sweep/p11-t2/R20/run` · brief `/Users/nabergoj/Projects/research-scan/research/experiments/phase11-golden/sweep/p11-t2/R20/run/brief.md` · rendered 2026-08-26

| # | Paper | Year | Venue | Evidence | Verified |
|---|---|---|---|---|---|
| 1 | [BrowseComp-Plus: A More Fair and Transparent Evaluation Benchmark of Deep-Research Agent](https://doi.org/10.48550/arxiv.2508.06600) · 10.48550/arxiv.2508.06600 | 2025 | arXiv (Cornell University) | experimental | yes |
| 2 | [When to use Graphs in RAG: A Comprehensive Analysis for Graph Retrieval-Augmented Generation](https://doi.org/10.48550/arxiv.2506.05690) · 10.48550/arxiv.2506.05690 | 2025 | arXiv.org | experimental | yes |
| 3 | [Diagnosing Search Behavior and Failure Modes in Long-Horizon Search Agents](https://doi.org/10.48550/arxiv.2608.01913) · 10.48550/arxiv.2608.01913 | 2026 | arXiv | observational | yes |
| 4 | [Projecting BrowseComp-Plus onto ClimbMix: Toward More Realistic Corpora for Agentic Search](https://arxiv.org/abs/2608.20317) | 2026 | — | experimental | yes |
| 5 | [PaSa: An LLM Agent for Comprehensive Academic Paper Search](https://doi.org/10.48550/arxiv.2501.10120) · 10.48550/arxiv.2501.10120 | 2025 | Annual Meeting of the Association for Computational Linguistics | experimental | yes |
| 6 | [Towards Recursive Self-Evolving Agentic Literature Retrieval](https://doi.org/10.48550/arxiv.2605.14306) · 10.48550/arxiv.2605.14306 | 2026 | arXiv | experimental | yes |
| 7 | [When Deep Research Agents Stagnate: Enhancing Reasoning with Retrieval-Aware Agent Control](https://doi.org/10.48550/arxiv.2608.15191) · 10.48550/arxiv.2608.15191 | 2026 | arXiv | experimental | yes |
| 8 | [Deep Research Agents: A Systematic Examination And Roadmap](https://doi.org/10.48550/arxiv.2506.18096) · 10.48550/arxiv.2506.18096 | 2025 | arXiv.org | other | yes |
| 9 | [Search-Time Contamination in Deep Research Agents: Measuring Performance Inflation in Public Benchmark Evaluation](https://doi.org/10.48550/arxiv.2606.05241) · 10.48550/arxiv.2606.05241 | 2026 | arXiv.org | experimental | yes |
| 10 | [Multi-Turn Agentic Scientific Literature Search via Workflow Induction](https://doi.org/10.48550/arxiv.2607.00597) · 10.48550/arxiv.2607.00597 | 2026 | arXiv | experimental | yes |

## 1. BrowseComp-Plus: A More Fair and Transparent Evaluation Benchmark of Deep-Research Agent

Zijian Chen, Xueguang Ma, Shengyao Zhuang, Ping Nie et al. · 2025 · arXiv (Cornell University) · experimental · overall 3/3

<https://doi.org/10.48550/arxiv.2508.06600>

**Key finding.** On a fixed, human-verified corpus, Search-R1 with BM25 achieves only 3.86% accuracy while GPT-5 reaches 55.9%, and pairing GPT-5 with the Qwen3-Embedding-8B retriever raises accuracy to 70.1% with fewer search calls.

**Why it made the cut.** foundational · selected by score · strongest on C1 baseline recall ceiling (3/3). Provides the fixed-corpus baseline recall ceiling and retriever comparison the brief's decision 1 needs, and underlies several other shortlisted papers' experiments.

**Why it matters here.** Gives an explicit, reproducible baseline recall/accuracy ceiling for single retriever plus LLM combinations, exactly the anchor decision 1 asks for, and disentangles retriever quality from agent reasoning quality.

**Method.** Introduces BrowseComp-Plus, a fixed corpus derived from BrowseComp with human-verified supporting documents and mined hard negatives, enabling controlled comparison of retrievers and agent LLMs independent of live web search APIs.

**Limitations.**

- Corpus limited to ~100K documents assembled per-query from the benchmark's own evidence and negatives, which later work shows can inflate scores
- Domain is general web search QA, not scientific literature specifically

<sub>selected: score · criteria: C1 3/3 · C2 1/3 · C3 3/3 · C4 3/3 · C5 1/3 · flags: methods_paper · verified 2026-08-26 via openalex, arxiv</sub>

## 2. When to use Graphs in RAG: A Comprehensive Analysis for Graph Retrieval-Augmented Generation

Zhishang Xiang, Chuan-Yu Wu, Qinggang Zhang, Shengyuan Chen et al. · 2025 · arXiv.org · experimental · overall 3/3

<https://doi.org/10.48550/arxiv.2506.05690>

**Key finding.** GraphRAG frequently underperforms vanilla RAG on many real-world tasks; GraphRAG-Bench systematically maps the conditions (fact retrieval, complex reasoning, summarization, creative generation) under which graph structure actually helps.

**Why it made the cut.** contradicting · selected by score · strongest on C4 benchmark construction (3/3). Shows a graph-based agentic mechanism failing to consistently beat baseline RAG, directly bearing on whether graph-traversal gains hold up.

**Why it matters here.** Directly undercuts the premise that a graph-traversal agentic mechanism reliably beats simpler retrieval, giving the scan a concrete case of a named agentic move (graph structure) failing to generalize — exactly the C5 evidence the brief asks us to reach for.

**Method.** Introduces GraphRAG-Bench, a benchmark with tasks of increasing difficulty and pipeline-wide evaluation from graph construction and retrieval through generation; abstract-only for exact scale and labeling details.

**Limitations.**

- Studied as general GraphRAG/RAG rather than citation-graph traversal over an academic-paper corpus specifically
- Abstract does not give an explicit magnitude for the reported underperformance

<sub>selected: score · criteria: C1 2/3 · C2 1/3 · C3 2/3 · C4 3/3 · C5 3/3 · flags: contradicts, methods_paper · verified 2026-08-26 via openalex, arxiv</sub>

## 3. Diagnosing Search Behavior and Failure Modes in Long-Horizon Search Agents

Qi Liu, Jiaxin Mao, Fengbin Zhu, Tat-Seng Chua · 2026 · arXiv · observational · overall 3/3

<https://doi.org/10.48550/arxiv.2608.01913>

**Key finding.** Across six agents on BrowseComp-Plus (validated on BrowseComp), search effort and answer quality are only weakly aligned; answer accuracy tracks cumulative retrieval recall far more than the number of searches, and top agents issue far fewer redundant queries.

**Why it made the cut.** contradicting · selected by score · strongest on C5 gain replication failure (3/3). Directly answers decisions 2 and 4: it isolates which behaviors (evidence quality, non-redundant reformulation) carry the gain and shows raw search effort does not reliably predict it.

**Why it matters here.** Undercuts the assumption that more iterative searching itself produces the agentic gain	ing discipline, not search volume, predicts outcomes, which should change what we measure when attributing gains to agentic mechanisms.

**Method.** Trajectory-level diagnosis using human-annotated document-level relevance judgments, holding retrieval model and evaluation harness fixed while comparing six long-horizon search agents; failures decomposed into retrieval gaps vs. utilization gaps.

**Limitations.**

- Focused on general web/long-horizon search agents rather than scientific-literature agents specifically
- Findings tied to BrowseComp-Plus/BrowseComp corpora and may not generalize to other retrieval domains

<sub>selected: score · criteria: C1 1/3 · C2 2/3 · C3 2/3 · C4 2/3 · C5 3/3 · flags: contradicts · verified 2026-08-26 via openalex, arxiv</sub>

## 4. Projecting BrowseComp-Plus onto ClimbMix: Toward More Realistic Corpora for Agentic Search

Sahel Sharifymoghaddam, Lin Gu, Yijun Ge, Jimmy Lin · 2026 · no venue · experimental · overall 3/3

<https://arxiv.org/abs/2608.20317>

**Key finding.** Relocating BrowseComp-Plus evidence into ClimbMix, a 553M-document corpus built without reference to the benchmark, drops the strongest agent's evidence recall from 84.3% to 21.4% and costs it 5 points of answer accuracy despite 63% more search calls, on 57 fully-grounded projected questions.

**Why it made the cut.** contradicting · selected by score · strongest on C4 benchmark construction (3/3). The clearest evidence in the shortlist that a widely-used agentic benchmark's construction inflates reported gains, exactly what the brief's decision 4 asks the scan to find.

**Why it matters here.** Directly demonstrates decision 4's core worry: a benchmark whose corpus was assembled per-query from its own evidence and negatives inflates reported agentic performance, and the same agent looks dramatically worse once evidence is relocated to an independently-built corpus.

**Method.** A dataset-agnostic projection pipeline decomposes benchmark questions into atomic reasoning hops and re-grounds each hop in a new, benchmark-independent corpus, retaining only hops confirmed by automatic verification, an independent agent, and human review.

**Limitations.**

- Only 57 of 830 original questions survive the strict grounding pipeline, a large reduction in coverage
- Tests general web-agent retrieval rather than scientific literature search specifically

<sub>selected: score · criteria: C1 1/3 · C2 0/3 · C3 2/3 · C4 3/3 · C5 3/3 · flags: contradicts, methods_paper · verified 2026-08-26 via arxiv, s2</sub>

## 5. PaSa: An LLM Agent for Comprehensive Academic Paper Search

Yichen He, Guanhua Huang, Peiyuan Feng, Yuan Lin et al. · 2025 · Annual Meeting of the Association for Computational Linguistics · experimental · overall 3/3

<https://doi.org/10.48550/arxiv.2501.10120>

**Key finding.** PaSa-7B surpasses the best Google-based baseline (Google with GPT-4o paraphrasing) by 37.78% in recall@20 and 39.90% in recall@50 on RealScholarQuery, and exceeds a prompted-GPT-4o version of itself by 30.36% in recall and 4.25% in precision.

**Why it made the cut.** foundational · selected by score · strongest on C1 baseline recall ceiling (3/3). The foundational agentic academic-paper-search system against which the field's baseline-recall and benchmark-construction claims are argued.

**Why it matters here.** The reference point for the whole scan: it quantifies the recall gap between single-query database/search-engine baselines and an agentic literature-search system, and its two-benchmark design (synthetic training set vs. real-world eval set) is the template other papers in this space (e.g. PaSaMaster) build on or must be measured against.

**Method.** RL-trained LLM agent that autonomously invokes search tools, reads papers, and selects references; trained on synthetic AutoScholarQuery (35k queries from top-tier AI conference papers) and evaluated on the real-world RealScholarQuery benchmark.

**Limitations.**

- Recall gains are measured against Google/Google Scholar baselines that may differ in query formulation from the agent's own reformulated queries
- AutoScholarQuery is synthetic and drawn only from top-tier AI conference papers, limiting corpus coverage
- No replication or failure-mode analysis of the reported gains is presented

<sub>selected: score · criteria: C1 3/3 · C2 2/3 · C3 1/3 · C4 3/3 · C5 0/3 · flags: methods_paper · verified 2026-08-26 via openalex, arxiv</sub>

## 6. Towards Recursive Self-Evolving Agentic Literature Retrieval

Yuwen Du, Tian Jin, Jing Kang, Xianghe Pang et al. · 2026 · arXiv · experimental · overall 3/3

<https://doi.org/10.48550/arxiv.2605.14306>

**Key finding.** PaSaMaster, a recursive self-evolving agentic literature retrieval system, achieves a 16.5x higher F1-score than Google Scholar and 37.8% higher F1 than GPT-5.2 at about 1% of the cost, reducing source hallucination from 32.66% to zero across 38 disciplines.

**Why it made the cut.** design-changing · selected by score · strongest on C3 retrieval/reranking method (3/3). A directly on-topic agentic literature-search system quantifying gains over a single-query baseline with a described retrieval/reranking mechanism.

**Why it matters here.** Gives a quantified, mechanism-attributed comparison against a single-query database baseline (Google Scholar) and a general-purpose LLM, directly answering the brief's first two questions and offering a concrete design (planning/retrieval separation) worth adopting or testing against.

**Method.** Iterative-intent-refinement agent combining hallucination-free ranking over verified papers with planning/retrieval separation (frontier LLM for intent, lightweight models for retrieval and scoring); evaluated on the newly introduced PaSaMaster-Bench across 38 disciplines.

**Limitations.**

- Benchmark (PaSaMaster-Bench) construction and relevance-labeling methodology not detailed in the abstract
- Comparisons across Google Scholar/GPT-5.2/PaSaMaster may not control for prompting or tooling differences
- Self-reported evaluation by the system's own authors

<sub>selected: score · criteria: C1 2/3 · C2 2/3 · C3 3/3 · C4 1/3 · C5 0/3 · flags: methods_paper · verified 2026-08-26 via openalex, arxiv</sub>

## 7. When Deep Research Agents Stagnate: Enhancing Reasoning with Retrieval-Aware Agent Control

Heydar Soudani, Elizabeth Lingg, Faegheh Hasibi, Navid Rekabsaz · 2026 · arXiv · experimental · overall 3/3

<https://doi.org/10.48550/arxiv.2608.15191>

**Key finding.** Most iterations of deep-research agents contribute little or no improvement to final performance; adding a Retrieval-Aware Agent Controller (RAAC), built on search-novelty and information-coverage signals, cuts search calls by an average of 14 and improves accuracy by up to 10% (3% on average) on BrowseComp-Plus.

**Why it made the cut.** plan-influencing · selected by score · strongest on C2 agentic mechanism gain (3/3). Speaks to decisions 2 and 4 together: names a specific control mechanism that carries the gain, and documents that most agentic search iterations are wasted effort, undercutting the reflexive premise that more agentic action is better.

**Why it matters here.** Shows directly that the naive premise 'more iterative search = more gain' does not hold 
 most iterations are wasted 
 and that a specific, measurable control signal recovers most of the benefit, which should reshape how we attribute and measure agentic gains.

**Method.** Analyzes reasoning trajectories of multiple Deep Research Agents for stagnation, then introduces unsupervised novelty/coverage signals and a controller that selects actions at each research step, evaluated across many DRAs on BrowseComp-Plus.

**Limitations.**

- Evaluated on BrowseComp-Plus, a general web-search benchmark, not a scientific-literature corpus
- Reported accuracy gain averages only 3%, with the 10% figure representing a best case

<sub>selected: score · criteria: C1 0/3 · C2 3/3 · C3 2/3 · C4 0/3 · C5 2/3 · flags: contradicts, methods_paper · verified 2026-08-26 via arxiv</sub>

## 8. Deep Research Agents: A Systematic Examination And Roadmap

Yuxuan Huang, Yihang Chen, Haozhen Zhang, Kang Li et al. · 2025 · arXiv.org · other · overall 3/3

<https://doi.org/10.48550/arxiv.2506.18096>

**Key finding.** Proposes a taxonomy distinguishing static vs. dynamic Deep Research agent workflows and single- vs. multi-agent architectures, and identifies restricted external-knowledge access, sequential execution inefficiency, and metric misalignment as key benchmark limitations.

**Why it made the cut.** foundational · selected by score · strongest on C4 benchmark construction (2/3). The field's orientation piece: a taxonomy and benchmark critique that frames how the other shortlisted system and benchmark papers relate to each other.

**Why it matters here.** Gives the orienting taxonomy (information acquisition strategy, workflow dynamism, agent composition) needed to categorize every other system-design paper in this scan and explicitly flags the benchmark-metric misalignment the brief's decision 4 is looking for.

**Method.** Narrative systematic review and taxonomy of Deep Research agent architectures, tool-use frameworks, and evaluation benchmarks; abstract-only detail.

**Limitations.**

- Narrative rather than systematic-protocol review
- Covers general Deep Research agents rather than literature-search agents specifically

<sub>selected: score · criteria: C1 1/3 · C2 1/3 · C3 1/3 · C4 2/3 · C5 1/3 · flags: review · verified 2026-08-26 via arxiv</sub>

## 9. Search-Time Contamination in Deep Research Agents: Measuring Performance Inflation in Public Benchmark Evaluation

Yongjie Wang, Xinyu Crystina Zhang, Kunhong Yao, Zhiwei Zeng et al. · 2026 · arXiv.org · experimental · overall 3/3

<https://doi.org/10.48550/arxiv.2606.05241>

**Key finding.** Search-Time Contamination (metadata, context, and answer leakage via web search) inflates deep research agent performance by up to 4% across six public benchmarks.

**Why it made the cut.** contradicting · selected by backfill · strongest on C4 benchmark construction (3/3). The clearest evidence in this shortlist that reported agentic gains can fail to hold up once contamination is accounted for.

**Why it matters here.** Directly targets the scan's fourth and hardest question: it shows a concrete, measured mechanism by which reported agentic gains are inflated rather than real, so any 'agentic beats single-query' claim on a public benchmark needs to be checked for search-time contamination first.

**Method.** Defines three contamination severity types (Benchmark Metadata Leakage, Question-Context Leakage, Explicit Answer Leakage), builds detection algorithms, and evaluates modern deep research agents on six public benchmarks.

**Limitations.**

- Focused on web-search contamination in general deep-research benchmarks rather than academic-literature corpora specifically
- 4% inflation figure is an aggregate across six benchmarks and may not generalize to every agent/benchmark pair

<sub>selected: backfill · criteria: C1 0/3 · C2 0/3 · C3 0/3 · C4 3/3 · C5 3/3 · flags: contradicts, methods_paper · verified 2026-08-26 via openalex, arxiv</sub>

## 10. Multi-Turn Agentic Scientific Literature Search via Workflow Induction

Jisen Li, Bingxuan Li, Nanyi Jiang, Xuying Ning et al. · 2026 · arXiv · experimental · overall 3/3

<https://doi.org/10.48550/arxiv.2607.00597>

**Key finding.** PaperPilot, which frames multi-turn scientific literature search as workflow induction over an executable DAG of paper-search operators (keyword search, citation expansion, filtering, scoring, reranking, evidence extraction), raises Hit@5 from 58.0 to 77.0, MRR from 47.5 to 59.4, and nDCG@10 from 26.8 to 32.5 over a base toolset agent, while cutting workflow execution errors from 9.5% to 0%.

**Why it made the cut.** design-changing · selected by backfill · strongest on C3 retrieval/reranking method (3/3). Directly on-brief: an agentic scientific-literature-search system with explicit citation-expansion and reranking operators and a measured, decomposable performance gain.

**Why it matters here.** This is the one paper in the shortlist that is literally an agentic scientific-literature-search system combining citation expansion and reranking as explicit, editable operators 
 its retrieval-pipeline design is the concrete alternative our own system design should weigh.

**Method.** Trains a 9B-parameter agent via supervised workflow imitation and preference optimization over controlled workflow corruptions, given an anchor paper and user query; evaluated under multi-turn interaction.

**Limitations.**

- Gains measured against a base toolset agent, not a single-query database search baseline
- No benchmark-construction detail on how the multi-turn evaluation queries/labels were built

<sub>selected: backfill · criteria: C1 0/3 · C2 2/3 · C3 3/3 · C4 0/3 · C5 0/3 · flags: methods_paper · verified 2026-08-26 via openalex, arxiv</sub>

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

- [Deep Research Bench: Evaluating AI Web Research Agents](https://doi.org/10.48550/arxiv.2506.06287) (2025) — overall 3/3
- [ResearchRubrics: A Benchmark of Prompts and Rubrics For Evaluating Deep Research Agents](https://doi.org/10.48550/arxiv.2511.07685) (2025) — overall 3/3
- [DeepResearch Bench: A Comprehensive Benchmark for Deep Research Agents](https://doi.org/10.48550/arxiv.2506.11763) (2025) — overall 3/3
- [Is Grep All You Need? How Agent Harnesses Reshape Agentic Search](https://doi.org/10.48550/arxiv.2605.15184) (2026) — overall 2/3
- [EviReform: Evidence-Guided Query Reformulation for Multi-Hop Graph Retrieval](https://doi.org/10.48550/arxiv.2608.13006) (2026) — overall 2/3
