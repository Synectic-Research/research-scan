# Evidence scan — p11-t2

Run `/Users/nabergoj/Projects/research-scan/research/experiments/phase12-selection/phase12b/runs/p11-t2/R20/O1/rep2/run` · brief `/Users/nabergoj/Projects/research-scan/research/experiments/phase12-selection/phase12b/runs/p11-t2/R20/O1/rep2/run/brief.md` · rendered 2026-08-26

| # | Paper | Year | Venue | Evidence | Verified |
|---|---|---|---|---|---|
| 1 | [When to use Graphs in RAG: A Comprehensive Analysis for Graph Retrieval-Augmented Generation](https://doi.org/10.48550/arxiv.2506.05690) · 10.48550/arxiv.2506.05690 | 2025 | arXiv.org | computational | yes |
| 2 | [BrowseComp-Plus: A More Fair and Transparent Evaluation Benchmark of Deep-Research Agent](https://doi.org/10.48550/arxiv.2508.06600) · 10.48550/arxiv.2508.06600 | 2025 | arXiv (Cornell University) | experimental | yes |
| 3 | [Towards Recursive Self-Evolving Agentic Literature Retrieval](https://doi.org/10.48550/arxiv.2605.14306) · 10.48550/arxiv.2605.14306 | 2026 | arXiv | experimental | yes |
| 4 | [Diagnosing Search Behavior and Failure Modes in Long-Horizon Search Agents](https://doi.org/10.48550/arxiv.2608.01913) · 10.48550/arxiv.2608.01913 | 2026 | arXiv | experimental | yes |
| 5 | [Projecting BrowseComp-Plus onto ClimbMix: Toward More Realistic Corpora for Agentic Search](https://arxiv.org/abs/2608.20317) | 2026 | — | experimental | yes |
| 6 | [LLM-guided Hierarchical Search for End-to-end Reasoning Intensive Retrieval](https://arxiv.org/abs/2510.13217) | 2025 | — | experimental | yes |
| 7 | [PaSa: An LLM Agent for Comprehensive Academic Paper Search](https://doi.org/10.48550/arxiv.2501.10120) · 10.48550/arxiv.2501.10120 | 2025 | Annual Meeting of the Association for Computational Linguistics | experimental | yes |
| 8 | [Structurally-bounded Agentic Graph Exploration for Evidence-Grounded Scholarly DeepSearch](https://doi.org/10.48550/arxiv.2608.24809) · 10.48550/arxiv.2608.24809 | 2026 | arXiv | experimental | yes |
| 9 | [Deep Research Agents: A Systematic Examination And Roadmap](https://doi.org/10.48550/arxiv.2506.18096) · 10.48550/arxiv.2506.18096 | 2025 | arXiv.org | other | yes |
| 10 | [Multi-Turn Agentic Scientific Literature Search via Workflow Induction](https://doi.org/10.48550/arxiv.2607.00597) · 10.48550/arxiv.2607.00597 | 2026 | arXiv | experimental | yes |

## 1. When to use Graphs in RAG: A Comprehensive Analysis for Graph Retrieval-Augmented Generation

Zhishang Xiang, Chuan-Yu Wu, Qinggang Zhang, Shengyuan Chen et al. · 2025 · arXiv.org · computational · overall 3/3

<https://doi.org/10.48550/arxiv.2506.05690>

**Key finding.** GraphRAG frequently underperforms vanilla RAG on many real-world tasks; GraphRAG-Bench, a benchmark spanning fact retrieval, complex reasoning, contextual summarization, and creative generation with full-pipeline evaluation, is used to identify the specific conditions under which graph structure actually helps.

**Why it made the cut.** contradicting · selected by score · strongest on C1 baseline recall ceiling (3/3). Directly tests, via the same graph-retrieval mechanism named in the brief's C2, whether the graph-traversal move actually beats a plain baseline — and finds it often does not, which is exactly the hardest evidence the brief asked the scan to surface.

**Why it matters here.** Uses the same underlying mechanism the brief's C2 names — graph-structured retrieval traversal versus plain retrieval — and shows the reported gain from graph structure often fails to beat the plain baseline, directly answering the brief's fourth question (where do reported gains fail to hold up) for the graph-traversal move specifically, and its benchmark-construction methodology (difficulty-graded tasks, full-pipeline evaluation) is a template for how a literature-search benchmark should be built.

**Method.** Introduces GraphRAG-Bench, a difficulty-graded dataset and systematic pipeline evaluation (graph construction, retrieval, generation) comparing GraphRAG variants against vanilla RAG.

**Limitations.**

- evaluated on general RAG/QA tasks rather than scientific-literature citation graphs specifically
- graph here is a concept/knowledge graph, not necessarily a citation graph
- abstract does not give the specific accuracy deltas, only the qualitative pattern

<sub>selected: score · criteria: C1 3/3 · C2 3/3 · C3 2/3 · C4 3/3 · C5 3/3 · flags: contradicts, methods_paper · verified 2026-08-26 via openalex, arxiv</sub>

## 2. BrowseComp-Plus: A More Fair and Transparent Evaluation Benchmark of Deep-Research Agent

Zijian Chen, Xueguang Ma, Shengyao Zhuang, Ping Nie et al. · 2025 · arXiv (Cornell University) · experimental · overall 3/3

<https://doi.org/10.48550/arxiv.2508.06600>

**Key finding.** On a fixed, human-verified corpus, Search-R1 with BM25 retrieval reaches only 3.86% accuracy while GPT-5 reaches 55.9%, and GPT-5 with a Qwen3-Embedding-8B retriever reaches 70.1% with fewer search calls.

**Why it made the cut.** plan-influencing · selected by score · strongest on C1 baseline recall ceiling (3/3). The field's reference benchmark for fair, reproducible retriever-vs-agent evaluation, foundational to answering how evaluation sets should be constructed and baselines measured.

**Why it matters here.** Establishes a controlled, reproducible way to separate retriever quality from agent capability — the exact anchor needed to measure whether agentic gains are real rather than artifacts of an opaque web API, directly shaping how the scan should evaluate future claims.

**Method.** Benchmark derived from BrowseComp with a fixed curated corpus, human-verified supporting documents and mined hard negatives, enabling disentangled retriever-vs-agent evaluation.

**Limitations.**

- Fixed corpus of ~100K documents assembled per-query (evidence and negatives both query-selected), a construction concern later addressed by other work
- Single benchmark family (derived from BrowseComp)

<sub>selected: score · criteria: C1 3/3 · C2 1/3 · C3 2/3 · C4 3/3 · C5 1/3 · flags: methods_paper · verified 2026-08-26 via openalex, arxiv</sub>

## 3. Towards Recursive Self-Evolving Agentic Literature Retrieval

Yuwen Du, Tian Jin, Jing Kang, Xianghe Pang et al. · 2026 · arXiv · experimental · overall 3/3

<https://doi.org/10.48550/arxiv.2605.14306>

**Key finding.** PaSaMaster achieves a 16.5x higher F1-score than Google Scholar and a 37.8% higher F1-score than GPT-5.2 at about 1% of the cost, across 38 disciplines in PaSaMaster-Bench, while reducing source hallucination from 32.66% to zero.

**Why it made the cut.** design-changing · selected by score · strongest on C1 baseline recall ceiling (3/3). A literature-search agent that explicitly benchmarks against a single-query search baseline (Google Scholar) and a non-agentic LLM baseline, directly answering the brief's C1/C2 questions.

**Why it matters here.** Directly measures the recall/precision gap between a single-query search baseline (Google Scholar) and an iterative, self-evolving agentic design, giving a concrete anchor for the brief's first question and attributing the gain to a named mechanism (self-evolving retrieval refinement).

**Method.** Recursive self-evolving retrieval architecture separating intent understanding (frontier LLM) from retrieval/scoring (lightweight models over customized corpora); evaluated on a purpose-built 38-discipline benchmark.

**Limitations.**

- benchmark construction (query source, relevance labeling, contamination controls) not detailed in the abstract
- no ablation isolating which specific move (reformulation vs. iterative refinement vs. ranking) drives the reported gain
- no evidence offered on whether the gain holds under a different benchmark or metric

<sub>selected: score · criteria: C1 3/3 · C2 3/3 · C3 2/3 · C4 1/3 · C5 0/3 · flags: methods_paper · verified 2026-08-26 via openalex, arxiv</sub>

## 4. Diagnosing Search Behavior and Failure Modes in Long-Horizon Search Agents

Qi Liu, Jiaxin Mao, Fengbin Zhu, Tat-Seng Chua · 2026 · arXiv · experimental · overall 3/3

<https://doi.org/10.48550/arxiv.2608.01913>

**Key finding.** Across six agents on BrowseComp-Plus and BrowseComp, answer accuracy correlates more with cumulative retrieval recall than with number of searches, and exploratory reformulations help while redundant queries hurt among the best-performing agents.

**Why it made the cut.** design-changing · selected by score · strongest on C2 agentic mechanism gain (3/3). Directly diagnoses which agentic search behaviors actually drive gains versus which are wasted effort, central to decisions 2 and 4.

**Why it matters here.** Directly answers which agentic moves carry the gain: retrieval quality (cumulative recall) matters more than search volume, and it names which behaviors (redundant reformulation, late low-yield search) are wasted effort — reshaping which mechanisms the scan should credit.

**Method.** Trajectory-level diagnosis using human-annotated document relevance judgments across six agents with a fixed retrieval model/harness, validated on BrowseComp-Plus and BrowseComp with an open-web search API.

**Limitations.**

- Six agents studied, may not generalize to all architectures
- Relies on document-level relevance judgments that may be incomplete

<sub>selected: score · criteria: C1 1/3 · C2 3/3 · C3 1/3 · C4 1/3 · C5 2/3 · flags: contradicts · verified 2026-08-26 via openalex, arxiv</sub>

## 5. Projecting BrowseComp-Plus onto ClimbMix: Toward More Realistic Corpora for Agentic Search

Sahel Sharifymoghaddam, Lin Gu, Yijun Ge, Jimmy Lin · 2026 · no venue · experimental · overall 3/3

<https://arxiv.org/abs/2608.20317>

**Key finding.** Relocating BrowseComp-Plus evidence into an independently-built 553M-document corpus (ClimbMix) drops the strongest agent's evidence recall from 84.3% to 21.4% and answer accuracy by five points, despite the agent issuing 63% more search calls.

**Why it made the cut.** contradicting · selected by score · strongest on C4 benchmark construction (3/3). The clearest demonstration in this set that a reported retrieval/agent gain shrinks dramatically under a different, independently-built corpus — directly answering decision 4.

**Why it matters here.** Direct, quantitative demonstration that a benchmark's own corpus construction (query-selected evidence and negatives) inflates measured retrieval performance — exactly the decision-4 evidence that reported agentic gains can collapse under a different, more realistic corpus.

**Method.** Projection pipeline decomposing benchmark questions into atomic reasoning hops, re-grounding each hop in a pre-training corpus built without reference to the benchmark, retaining only hops verified by automatic checks, an independent agent, and human review; yields 57 fully grounded questions from 830 BrowseComp-Plus questions.

**Limitations.**

- Only 57 of 830 questions survived full grounding verification, a small evaluation set
- Single benchmark family projected onto a single alternative corpus

<sub>selected: score · criteria: C1 1/3 · C2 1/3 · C3 0/3 · C4 3/3 · C5 3/3 · flags: contradicts, methods_paper · verified 2026-08-26 via arxiv, s2</sub>

## 6. LLM-guided Hierarchical Search for End-to-end Reasoning Intensive Retrieval

Nilesh Gupta, Wei-Cheng Chang, N. Bui, Cho-Jui Hsieh et al. · 2025 · no venue · experimental · overall 3/3

<https://arxiv.org/abs/2510.13217>

**Key finding.** LATTICE achieves 46.7 nDCG@10 on the reasoning-intensive BRIGHT benchmark, matching the best fine-tuned ensemble, and LATTICE++ reaches 49.1 nDCG@10, remaining competitive on NQ, SciFact and SciDocs; reranking wins at low token budgets but LATTICE reaches a higher asymptote at moderate budgets.

**Why it made the cut.** design-changing · selected by score · strongest on C3 retrieval/reranking method (3/3). A concrete retrieval-method alternative to embedding-based single-query search with quantified recall/nDCG gains and scientific-literature benchmarks, central to decisions 1 and 3.

**Why it matters here.** Shows embedding-based single-query retrieval's top-k assumption fails for reasoning-intensive queries and offers a retrieval-time alternative rather than query-side fixes — bears directly on both the recall-ceiling question and what retrieval method underlies future literature-search agents.

**Method.** LLM-guided hierarchical search index built top-down from multi-level document summaries, with calibrated path-aggregated LLM traversal replacing embedding retrieval at search time; evaluated on BRIGHT, NQ, SciFact and SciDocs with multiple LLMs.

**Limitations.**

- Not literature-search specific, though it includes scientific benchmarks (SciFact, SciDocs)
- Reranking outperforms it at low token budgets, so gains are budget-dependent

<sub>selected: score · criteria: C1 2/3 · C2 2/3 · C3 3/3 · C4 0/3 · C5 1/3 · flags: methods_paper · verified 2026-08-26 via arxiv, s2</sub>

## 7. PaSa: An LLM Agent for Comprehensive Academic Paper Search

Yichen He, Guanhua Huang, Peiyuan Feng, Yuan Lin et al. · 2025 · Annual Meeting of the Association for Computational Linguistics · experimental · overall 3/3

<https://doi.org/10.48550/arxiv.2501.10120>

**Key finding.** PaSa-7B surpasses the best Google-based baseline by 37.78% in recall@20 and 39.90% in recall@50 on RealScholarQuery, and exceeds prompted PaSa-GPT-4o by 30.36% in recall.

**Why it made the cut.** design-changing · selected by score · strongest on C4 benchmark construction (3/3). Core exemplar system directly measuring agentic search gains over single-query baselines with an explicit benchmark construction, addressing decisions 1, 2 and 3.

**Why it matters here.** Provides concrete, large recall gains over single-query search baselines with a paired synthetic/real benchmark — a reference point for how much agentic search can plausibly add over database search.

**Method.** RL-trained LLM agent that autonomously searches, reads, and follows references, trained on synthetic AutoScholarQuery (35k queries) and evaluated on a newly built real-world benchmark, RealScholarQuery.

**Limitations.**

- Trained on synthetic queries which may not transfer perfectly to all real query types
- Recall gains measured against commercial search UIs, not raw BM25/embedding API baselines

<sub>selected: score · criteria: C1 2/3 · C2 1/3 · C3 1/3 · C4 3/3 · C5 0/3 · flags: methods_paper · verified 2026-08-26 via openalex, arxiv</sub>

## 8. Structurally-bounded Agentic Graph Exploration for Evidence-Grounded Scholarly DeepSearch

Rima Hazra, Sayan Layek, Somnath Banerjee, Soumen Chakrabarti et al. · 2026 · arXiv · experimental · overall 3/3

<https://doi.org/10.48550/arxiv.2608.24809>

**Key finding.** A bounded 1.5-hop citation-graph expansion with entailment pruning and recency-aware ranking outperforms open-ended deep research agents built on proprietary models by up to 3x recall@50 at roughly a third of the cost on LitSearch and one further benchmark over a 500K-paper arXiv corpus.

**Why it made the cut.** design-changing · selected by backfill · strongest on C2 agentic mechanism gain (3/3). Isolates citation-graph traversal as the specific agentic mechanism producing measured recall gains, exactly decision 2's question.

**Why it matters here.** Isolates citation-graph traversal, structurally bounded, as the specific mechanism carrying most of the gain over open-ended agentic search, with a cost/recall tradeoff quantified — directly answering decision 2.

**Method.** Single seed search followed by 1.5-hop citation neighborhood expansion, entailment-based edge pruning, and recency-aware random-walk ranking; evaluated on LitSearch and one further benchmark.

**Limitations.**

- Single corpus (arXiv) and specific benchmarks, may not generalize to other literatures
- Comparison partner set of proprietary deep research agents may not represent all baselines

<sub>selected: backfill · criteria: C1 1/3 · C2 3/3 · C3 2/3 · C4 1/3 · C5 0/3 · flags: methods_paper · verified 2026-08-26 via arxiv</sub>

## 9. Deep Research Agents: A Systematic Examination And Roadmap

Yuxuan Huang, Yihang Chen, Haozhen Zhang, Kang Li et al. · 2025 · arXiv.org · other · overall 3/3

<https://doi.org/10.48550/arxiv.2506.18096>

**Key finding.** Provides a taxonomy of Deep Research agent architectures (static/dynamic workflows, single/multi-agent) and a critical evaluation of current benchmarks, naming restricted external-knowledge access, sequential execution inefficiencies, and metric-objective misalignment as key limitations.

**Why it made the cut.** closely-related · selected by review · strongest on C4 benchmark construction (2/3). The synthesis paper covering system designs, benchmarks, and their limitations across the whole space the brief asks about, valuable as an orientation and benchmark-critique reference.

**Why it matters here.** Gives the orienting map of the whole agentic-literature-search design space and names the specific benchmark-construction weaknesses the scan should watch for when judging any single reported gain.

**Method.** Narrative systematic review and taxonomy of Deep Research agent architectures, information-acquisition strategies, and tool-use frameworks, with a curated repository of related work.

**Limitations.**

- Narrative review, not a systematic protocol or quantitative meta-analysis
- No new empirical results of its own

<sub>selected: review · criteria: C1 1/3 · C2 1/3 · C3 1/3 · C4 2/3 · C5 1/3 · flags: review · verified 2026-08-26 via arxiv</sub>

## 10. Multi-Turn Agentic Scientific Literature Search via Workflow Induction

Jisen Li, Bingxuan Li, Nanyi Jiang, Xuying Ning et al. · 2026 · arXiv · experimental · overall 3/3

<https://doi.org/10.48550/arxiv.2607.00597>

**Key finding.** PaperPilot-9B, trained via workflow imitation and preference optimization over an executable DAG of search operators, raises Hit@5 from 58.0 to 77.0, MRR from 47.5 to 59.4, and nDCG@10 from 26.8 to 32.5 over a base toolset agent, while cutting workflow execution errors from 9.5% to 0%.

**Why it made the cut.** design-changing · selected by backfill · strongest on C2 agentic mechanism gain (2/3). A directly on-topic agentic literature-search system with an executable, inspectable workflow design and reported multi-turn gains.

**Why it matters here.** Directly instantiates the system design the brief is scanning for — an editable DAG combining keyword search, citation expansion, filtering, scoring and reranking — and gives a concrete number for what structuring the workflow buys over an undifferentiated tool-using baseline.

**Method.** Supervised workflow imitation plus preference optimization over controlled workflow corruptions; multi-turn evaluation against a Qwen3.5-9B toolset-agent baseline.

**Limitations.**

- baseline is another agent, not a single-query database search ceiling
- gain is attributed to the workflow as a whole rather than isolated per-operator ablations
- no benchmark construction detail given for the eval set

<sub>selected: backfill · criteria: C1 1/3 · C2 2/3 · C3 2/3 · C4 1/3 · C5 0/3 · flags: methods_paper · verified 2026-08-26 via openalex, arxiv</sub>

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

- [AI's Capability in Assisting Scientific Research in Physics, Astrophysics, and Cosmology I: Literature Review](https://doi.org/10.48550/arxiv.2607.25672) (2026) — overall 3/3
- [Language agents achieve superhuman synthesis of scientific knowledge](https://doi.org/10.48550/arxiv.2409.13740) (2024) — overall 3/3
- [Is Grep All You Need? How Agent Harnesses Reshape Agentic Search](https://doi.org/10.48550/arxiv.2605.15184) (2026) — overall 2/3
- [EviReform: Evidence-Guided Query Reformulation for Multi-Hop Graph Retrieval](https://doi.org/10.48550/arxiv.2608.13006) (2026) — overall 2/3
- [HySemRAG: A Hybrid Semantic Retrieval-Augmented Generation Framework for Automated Literature Synthesis and Methodological Gap Analysis](https://doi.org/10.48550/arxiv.2508.05666) (2025) — overall 2/3
