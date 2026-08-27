# Evidence scan — p11-t2

Run `/Users/nabergoj/Projects/research-scan/research/experiments/phase14/runs/p11-t2/S/rep2/run` · brief `/Users/nabergoj/Projects/research-scan/research/experiments/phase14/runs/p11-t2/S/rep2/run/brief.md` · rendered 2026-08-26

| # | Paper | Year | Venue | Evidence | Verified |
|---|---|---|---|---|---|
| 1 | [When to use Graphs in RAG: A Comprehensive Analysis for Graph Retrieval-Augmented Generation](https://doi.org/10.48550/arxiv.2506.05690) · 10.48550/arxiv.2506.05690 | 2025 | arXiv.org | experimental | yes |
| 2 | [Towards Recursive Self-Evolving Agentic Literature Retrieval](https://doi.org/10.48550/arxiv.2605.14306) · 10.48550/arxiv.2605.14306 | 2026 | arXiv | experimental | yes |
| 3 | [LLM-guided Hierarchical Search for End-to-end Reasoning Intensive Retrieval](https://arxiv.org/abs/2510.13217) | 2025 | — | experimental | yes |
| 4 | [Diagnosing Search Behavior and Failure Modes in Long-Horizon Search Agents](https://doi.org/10.48550/arxiv.2608.01913) · 10.48550/arxiv.2608.01913 | 2026 | arXiv | experimental | yes |
| 5 | [Deep Research Agents: A Systematic Examination And Roadmap](https://doi.org/10.48550/arxiv.2506.18096) · 10.48550/arxiv.2506.18096 | 2025 | arXiv.org | other | yes |
| 6 | [BrowseComp-Plus: A More Fair and Transparent Evaluation Benchmark of Deep-Research Agent](https://doi.org/10.48550/arxiv.2508.06600) · 10.48550/arxiv.2508.06600 | 2025 | arXiv (Cornell University) | experimental | yes |
| 7 | [BRIGHT: A Realistic and Challenging Benchmark for Reasoning-Intensive Retrieval](https://doi.org/10.48550/arxiv.2407.12883) · 10.48550/arxiv.2407.12883 | 2024 | International Conference on Learning Representations | experimental | yes |
| 8 | [Structurally-bounded Agentic Graph Exploration for Evidence-Grounded Scholarly DeepSearch](https://doi.org/10.48550/arxiv.2608.24809) · 10.48550/arxiv.2608.24809 | 2026 | arXiv | experimental | yes |
| 9 | [OpenScholar: Synthesizing Scientific Literature with Retrieval-augmented LMs](https://doi.org/10.48550/arxiv.2411.14199) · 10.48550/arxiv.2411.14199 | 2024 | arXiv.org | experimental | yes |
| 10 | [Projecting BrowseComp-Plus onto ClimbMix: Toward More Realistic Corpora for Agentic Search](https://arxiv.org/abs/2608.20317) | 2026 | — | experimental | yes |

## 1. When to use Graphs in RAG: A Comprehensive Analysis for Graph Retrieval-Augmented Generation

Zhishang Xiang, Chuan-Yu Wu, Qinggang Zhang, Shengyuan Chen et al. · 2025 · arXiv.org · experimental · overall 3/3

<https://doi.org/10.48550/arxiv.2506.05690>

**Key finding.** GraphRAG frequently underperforms vanilla RAG on many real-world tasks; GraphRAG-Bench's systematic pipeline evaluation identifies the specific conditions under which graph structure actually helps.

**Why it made the cut.** contradicting · selected by score · strongest on C2 agentic mechanism gain (3/3). The single strongest piece of evidence in this batch that a core agentic mechanism (graph traversal) does not reliably outperform the plain baseline, which the brief explicitly asks the scan to look for.

**Why it matters here.** Directly contradicts the premise that graph-structured retrieval (the mechanism underlying citation-graph traversal) reliably beats simpler retrieval, and supplies the benchmark needed to say when it does and doesn't -- central to the brief's Q2 and Q4.

**Method.** New benchmark spanning fact retrieval, complex reasoning, contextual summarization, and creative generation, with end-to-end evaluation from graph construction through retrieval to generation.

**Limitations.**

- Domain is general knowledge-graph RAG, not citation graphs over scientific literature specifically.
- Benchmark tasks are synthetic/curated rather than drawn from real literature-search queries.

<sub>selected: score · criteria: C1 1/3 · C2 3/3 · C3 2/3 · C4 3/3 · C5 3/3 · flags: contradicts, methods_paper · verified 2026-08-26 via openalex, arxiv</sub>

## 2. Towards Recursive Self-Evolving Agentic Literature Retrieval

Yuwen Du, Tian Jin, Jing Kang, Xianghe Pang et al. · 2026 · arXiv · experimental · overall 3/3

<https://doi.org/10.48550/arxiv.2605.14306>

**Key finding.** PaSaMaster achieves a 16.5x higher F1-score than Google Scholar and 37.8% higher F1 than GPT-5.2 at about 1% of the cost, reducing source hallucination from 32.66% to zero, across 38 disciplines in PaSaMaster-Bench.

**Why it made the cut.** design-changing · selected by score · strongest on C1 baseline recall ceiling (3/3). One of the clearest in-window systems directly reporting the single-query-search baseline comparison the brief's first question asks for, plus an explicit mechanism attribution.

**Why it matters here.** Provides a quantified comparison against a real single-query search baseline (Google Scholar), directly anchoring how large an agentic gain can be and which mechanism (iterative intent refinement) is credited with it.

**Method.** Recursive self-evolving agentic retrieval combining iterative intent refinement, hallucination-free ranking over verified papers, and planning/retrieval separation across cheap vs. frontier models; new 38-discipline benchmark.

**Limitations.**

- Benchmark (PaSaMaster-Bench) is introduced by the same team, raising a construction/self-serving-evaluation concern.
- Abstract gives no detail on relevance-labeling methodology or contamination controls for the new benchmark.

<sub>selected: score · criteria: C1 3/3 · C2 3/3 · C3 3/3 · C4 2/3 · C5 0/3 · flags: methods_paper · verified 2026-08-26 via openalex, arxiv</sub>

## 3. LLM-guided Hierarchical Search for End-to-end Reasoning Intensive Retrieval

Nilesh Gupta, Wei-Cheng Chang, N. Bui, Cho-Jui Hsieh et al. · 2025 · no venue · experimental · overall 3/3

<https://arxiv.org/abs/2510.13217>

**Key finding.** LATTICE, an LLM-guided hierarchical search index with no embedding model in the loop, reaches 46.7 nDCG@10 on BRIGHT (matching the best fine-tuned ensemble) and 49.1 with a lightweight ensemble variant, remaining competitive on SciFact and SciDocs.

**Why it made the cut.** design-changing · selected by score · strongest on C1 baseline recall ceiling (3/3). Directly evidences the recall ceiling of embedding retrieval (C1) and proposes a retrieval-stage mechanism (C3) that bears on which underlying method an agentic literature-search system should use.

**Why it matters here.** Directly demonstrates that embedding-based single-query retrieval hits a recall ceiling on reasoning-intensive queries that query rewriting and agentic loops fail to overcome, and offers a retrieval-stage alternative that changes what underlying retrieval method a literature-search agent should use.

**Method.** Constructs a hierarchically navigable index via LLM judgments over multi-level document summaries, then performs calibrated path-aggregated LLM traversal; evaluated on BRIGHT, NQ, SciFact, SciDocs against embedding+reranker baselines.

**Limitations.**

- core evaluation is general reasoning-intensive IR (BRIGHT), scientific benchmarks are secondary
- index construction cost and scalability to very large scholarly corpora not addressed

<sub>selected: score · criteria: C1 3/3 · C2 2/3 · C3 3/3 · C4 1/3 · C5 2/3 · flags: methods_paper · verified 2026-08-26 via arxiv, s2</sub>

## 4. Diagnosing Search Behavior and Failure Modes in Long-Horizon Search Agents

Qi Liu, Jiaxin Mao, Fengbin Zhu, Tat-Seng Chua · 2026 · arXiv · experimental · overall 3/3

<https://doi.org/10.48550/arxiv.2608.01913>

**Key finding.** Across six agents on BrowseComp-Plus and BrowseComp, answer accuracy tracks cumulative retrieval recall far more than search-step count or context consumed, and top agents issue far fewer redundant queries despite useful evidence often surfacing early.

**Why it made the cut.** plan-influencing · selected by score · strongest on C2 agentic mechanism gain (3/3). Provides the clearest mechanistic evidence for which agentic moves carry gains and where reported search effort fails to translate into quality, addressing Q2 and Q4 head-on.

**Why it matters here.** Directly answers what agentic effort actually buys: search volume is only weakly related to output quality, so any claimed agentic gain must be checked against retrieved-evidence quality, not step count — reshaping how we'd measure and attribute gains in Q2/Q4.

**Method.** Trajectory-level diagnostic study using human-annotated document-level relevance judgments, decomposing failures into retrieval gaps vs utilization gaps; held retriever and harness fixed across six long-horizon search agents on two benchmarks.

**Limitations.**

- single retrieval model/harness held fixed, may not generalize to other retrievers
- focused on two benchmark families (BrowseComp variants)

<sub>selected: score · criteria: C1 1/3 · C2 3/3 · C3 1/3 · C4 2/3 · C5 3/3 · verified 2026-08-26 via openalex, arxiv</sub>

## 5. Deep Research Agents: A Systematic Examination And Roadmap

Yuxuan Huang, Yihang Chen, Haozhen Zhang, Kang Li et al. · 2025 · arXiv.org · other · overall 3/3

<https://doi.org/10.48550/arxiv.2506.18096>

**Key finding.** A systematic taxonomy of Deep Research agent architectures (static vs dynamic workflows, single- vs multi-agent) that identifies restricted external-knowledge access, sequential execution inefficiencies, and metric-objective misalignment as key benchmark limitations.

**Why it made the cut.** foundational · selected by score · strongest on C4 benchmark construction (3/3). The most comprehensive review-level synthesis of DR agent architectures and benchmark limitations in the shortlist, guaranteeing a synthesis view alongside the empirical papers.

**Why it matters here.** Provides the field-level map of which architectural components and benchmark weaknesses matter, directly informing how to sequence and interpret evidence for Q2 (mechanism taxonomy) and Q3 (benchmark critique) across the rest of the portfolio.

**Method.** Narrative survey/taxonomy paper reviewing information-acquisition strategies, tool-use frameworks, and existing benchmarks for Deep Research agents; abstract-only detail beyond taxonomy structure.

**Limitations.**

- narrative synthesis, not a systematic-review protocol
- abstract-only, no quantitative findings of its own

<sub>selected: score · criteria: C1 1/3 · C2 2/3 · C3 2/3 · C4 3/3 · C5 2/3 · flags: review · verified 2026-08-26 via arxiv</sub>

## 6. BrowseComp-Plus: A More Fair and Transparent Evaluation Benchmark of Deep-Research Agent

Zijian Chen, Xueguang Ma, Shengyao Zhuang, Ping Nie et al. · 2025 · arXiv (Cornell University) · experimental · overall 3/3

<https://doi.org/10.48550/arxiv.2508.06600>

**Key finding.** On a fixed, human-verified corpus, Search-R1 with BM25 achieves only 3.86% accuracy while GPT-5 reaches 55.9%, rising to 70.1% when paired with the Qwen3-Embedding-8B retriever and fewer search calls.

**Why it made the cut.** foundational · selected by score · strongest on C1 baseline recall ceiling (3/3). The foundational, most-cited benchmark-construction paper in this exact space, underlying multiple other shortlisted works' evaluations.

**Why it matters here.** Supplies the fixed-corpus, controlled-baseline benchmark this whole subfield now measures itself against, giving a concrete, reproducible number for the BM25 recall ceiling question (Q1) and a template for benchmark construction (Q3).

**Method.** Benchmark construction paper: replaces BrowseComp's opaque live web search with a fixed, curated corpus, human-verified supporting documents, and mined hard negatives, enabling controlled disentanglement of agent vs retriever contributions.

**Limitations.**

- single benchmark family (BrowseComp-derived queries)
- corpus assembled per-query from the benchmark's own supporting documents, later shown (elsewhere) to potentially inflate results

<sub>selected: score · criteria: C1 3/3 · C2 0/3 · C3 2/3 · C4 3/3 · C5 1/3 · flags: methods_paper · verified 2026-08-26 via openalex, arxiv</sub>

## 7. BRIGHT: A Realistic and Challenging Benchmark for Reasoning-Intensive Retrieval

Hongjin Su, Howard Yen, Mengzhou Xia, Weijia Shi et al. · 2024 · International Conference on Learning Representations · experimental · overall 3/3

<https://doi.org/10.48550/arxiv.2407.12883>

**Key finding.** The leading MTEB retriever (59.0 nDCG@10 on standard benchmarks) scores only 18.3 nDCG@10 on BRIGHT's reasoning-intensive queries; incorporating explicit query reasoning improves retrieval by up to 12.2 points.

**Why it made the cut.** foundational · selected by score · strongest on C1 baseline recall ceiling (3/3). The clearest available quantification of the single-query recall ceiling under hard queries, foundational for judging whether any agentic gain is real or just recovering an easy baseline.

**Why it matters here.** Establishes just how low the single-query dense-retrieval ceiling actually is once queries require reasoning rather than surface matching -- the exact baseline number (Q1) that any agentic literature-search gain needs to be measured against.

**Method.** 1,384 real-world, curated reasoning-intensive queries across economics, psychology, mathematics, and coding; evaluates state-of-the-art dense and sparse retrievers.

**Limitations.**

- Domain is general reasoning-intensive retrieval (economics, coding, etc.), not scientific literature search specifically.
- Does not evaluate agentic, multi-step retrieval systems, only single-query retrievers.

<sub>selected: score · criteria: C1 3/3 · C2 0/3 · C3 2/3 · C4 3/3 · C5 1/3 · flags: methods_paper · verified 2026-08-26 via openalex, arxiv</sub>

## 8. Structurally-bounded Agentic Graph Exploration for Evidence-Grounded Scholarly DeepSearch

Rima Hazra, Sayan Layek, Somnath Banerjee, Soumen Chakrabarti et al. · 2026 · arXiv · experimental · overall 3/3

<https://doi.org/10.48550/arxiv.2608.24809>

**Key finding.** Crase, a bounded 1.5-hop citation-graph expansion with entailment-pruned edges and recency-aware random-walk ranking, outperforms deep research agents built on proprietary models by up to 3x recall@50 at roughly a third of the cost on LitSearch and a second benchmark over a 500K-paper arXiv corpus.

**Why it made the cut.** design-changing · selected by score · strongest on C2 agentic mechanism gain (3/3). A concrete, evaluated alternative design that isolates citation-graph traversal as the mechanism carrying the gain — exactly what Q2 asks for.

**Why it matters here.** Shows that a fixed, inspectable citation-traversal design beats open-ended agentic search loops on both recall and cost, directly informing which agentic mechanism (bounded graph traversal vs. unconstrained iteration) to prefer.

**Method.** System paper: single seed search, fixed-depth citation-graph expansion, entailment-based pruning, random-walk reranking; evaluated on LitSearch and one further scholarly-search benchmark.

**Limitations.**

- compared against proprietary deep-research baselines with limited transparency into their configuration
- tested on two benchmarks only, generalization to other corpora untested

<sub>selected: score · criteria: C1 2/3 · C2 3/3 · C3 2/3 · C4 2/3 · C5 0/3 · flags: methods_paper · verified 2026-08-26 via arxiv</sub>

## 9. OpenScholar: Synthesizing Scientific Literature with Retrieval-augmented LMs

Akari Asai, Jacqueline He, Rulin Shao, Weijia Shi et al. · 2024 · arXiv.org · experimental · overall 3/3

<https://doi.org/10.48550/arxiv.2411.14199>

**Key finding.** OpenScholar-8B outperforms GPT-4o by 5% and PaperQA2 by 7% in correctness on the new ScholarQABench benchmark (2,967 expert queries), while GPT-4o hallucinates citations 78-90% of the time versus expert-level citation accuracy for OpenScholar.

**Why it made the cut.** design-changing · selected by backfill · strongest on C3 retrieval/reranking method (3/3). The most comprehensive system-plus-benchmark paper directly on the brief's target setting, combining retrieval design, agentic self-feedback, and rigorous multi-domain evaluation.

**Why it matters here.** Sets a concrete, multi-domain benchmark and system baseline for literature synthesis quality and citation accuracy, the standard against which any agentic literature-search claim in this scan should be measured.

**Method.** Retrieval-augmented LM over a 45-million-paper open-access datastore with a self-feedback inference loop; evaluated on the newly constructed multi-domain ScholarQABench benchmark and via human preference studies.

**Limitations.**

- Comparisons are against general-purpose LLMs and PaperQA2 rather than a plain single-query search baseline
- Benchmark and datastore restricted to open-access papers, limiting corpus coverage

<sub>selected: backfill · criteria: C1 2/3 · C2 1/3 · C3 3/3 · C4 3/3 · C5 0/3 · flags: methods_paper · verified 2026-08-26 via openalex, arxiv</sub>

## 10. Projecting BrowseComp-Plus onto ClimbMix: Toward More Realistic Corpora for Agentic Search

Sahel Sharifymoghaddam, Lin Gu, Yijun Ge, Jimmy Lin · 2026 · no venue · experimental · overall 3/3

<https://arxiv.org/abs/2608.20317>

**Key finding.** Relocating BrowseComp-Plus's 57 fully-grounded questions onto the independently built ClimbMix corpus drops the strongest agent's evidence recall from 84.3% to 21.4% and answer accuracy by five points, while search calls rise 63%.

**Why it made the cut.** contradicting · selected by backfill · strongest on C4 benchmark construction (3/3). Directly answers Q3 and Q4 together: shows how benchmark construction inflates reported agentic gains and how those gains shrink dramatically under an independently built corpus — exactly the hardest evidence the brief asked the scan to find.

**Why it matters here.** The single clearest demonstration in this set that a benchmark's own corpus construction (per-query selected evidence and negatives) inflates measured agentic performance, and that the gain collapses once the evidence is relocated to an independently built corpus.

**Method.** Projection pipeline decomposing benchmark questions into atomic reasoning hops and re-grounding each hop in a 400B-token, 553M-document corpus (ClimbMix) built without reference to the benchmark, validated by automatic verification, an independent agent, and human review.

**Limitations.**

- yields only 57 fully grounded questions after strict verification, a small evaluation set
- projection pipeline itself introduces its own selection and verification assumptions

<sub>selected: backfill · criteria: C1 1/3 · C2 0/3 · C3 1/3 · C4 3/3 · C5 3/3 · flags: review, contradicts, methods_paper · verified 2026-08-26 via arxiv, s2</sub>

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

- [PaSa: An LLM Agent for Comprehensive Academic Paper Search](https://doi.org/10.48550/arxiv.2501.10120) (2025) — overall 3/3
- [Patience is all you need! An agentic system for performing scientific literature review](https://doi.org/10.48550/arxiv.2504.08752) (2025) — overall 3/3
- [CG-RAG: Research Question Answering by Citation Graph Retrieval-Augmented LLMs](https://doi.org/10.1145/3726302.3729920) (2025) — overall 3/3
- [LitSearch: A Retrieval Benchmark for Scientific Literature Search](https://doi.org/10.48550/arxiv.2407.18940) (2024) — overall 3/3
- [Multi-Turn Agentic Scientific Literature Search via Workflow Induction](https://doi.org/10.48550/arxiv.2607.00597) (2026) — overall 3/3
