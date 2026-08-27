# Evidence scan — p11-t2

Run `/Users/nabergoj/Projects/research-scan/research/experiments/phase14/runs/p11-t2/SC/rep3/run` · brief `/Users/nabergoj/Projects/research-scan/research/experiments/phase14/runs/p11-t2/SC/rep3/run/brief.md` · rendered 2026-08-26

| # | Paper | Year | Venue | Evidence | Verified |
|---|---|---|---|---|---|
| 1 | [When to use Graphs in RAG: A Comprehensive Analysis for Graph Retrieval-Augmented Generation](https://doi.org/10.48550/arxiv.2506.05690) · 10.48550/arxiv.2506.05690 | 2025 | arXiv.org | experimental | yes |
| 2 | [BrowseComp-Plus: A More Fair and Transparent Evaluation Benchmark of Deep-Research Agent](https://doi.org/10.48550/arxiv.2508.06600) · 10.48550/arxiv.2508.06600 | 2025 | arXiv (Cornell University) | computational | yes |
| 3 | [Diagnosing Search Behavior and Failure Modes in Long-Horizon Search Agents](https://doi.org/10.48550/arxiv.2608.01913) · 10.48550/arxiv.2608.01913 | 2026 | arXiv | computational | yes |
| 4 | [LLM-guided Hierarchical Search for End-to-end Reasoning Intensive Retrieval](https://arxiv.org/abs/2510.13217) | 2025 | — | computational | yes |
| 5 | [Projecting BrowseComp-Plus onto ClimbMix: Toward More Realistic Corpora for Agentic Search](https://arxiv.org/abs/2608.20317) | 2026 | — | computational | yes |
| 6 | [BRIGHT: A Realistic and Challenging Benchmark for Reasoning-Intensive Retrieval](https://doi.org/10.48550/arxiv.2407.12883) · 10.48550/arxiv.2407.12883 | 2024 | International Conference on Learning Representations | experimental | yes |
| 7 | [OpenScholar: Synthesizing Scientific Literature with Retrieval-augmented LMs](https://doi.org/10.48550/arxiv.2411.14199) · 10.48550/arxiv.2411.14199 | 2024 | arXiv.org | experimental | yes |
| 8 | [LitSearch: A Retrieval Benchmark for Scientific Literature Search](https://doi.org/10.48550/arxiv.2407.18940) · 10.48550/arxiv.2407.18940 | 2024 | Conference on Empirical Methods in Natural Language Processing | experimental | yes |
| 9 | [PaSa: An LLM Agent for Comprehensive Academic Paper Search](https://doi.org/10.48550/arxiv.2501.10120) · 10.48550/arxiv.2501.10120 | 2025 | Annual Meeting of the Association for Computational Linguistics | computational | yes |
| 10 | [Deep Research Agents: A Systematic Examination And Roadmap](https://doi.org/10.48550/arxiv.2506.18096) · 10.48550/arxiv.2506.18096 | 2025 | arXiv.org | other | yes |

## 1. When to use Graphs in RAG: A Comprehensive Analysis for Graph Retrieval-Augmented Generation

Zhishang Xiang, Chuan-Yu Wu, Qinggang Zhang, Shengyuan Chen et al. · 2025 · arXiv.org · experimental · overall 3/3

<https://doi.org/10.48550/arxiv.2506.05690>

**Key finding.** GraphRAG frequently underperforms vanilla RAG on many real-world tasks; GraphRAG-Bench systematically maps the conditions (fact retrieval vs. complex reasoning vs. summarization vs. creative generation) under which graph structure actually helps.

**Why it made the cut.** contradicting · selected by score · strongest on C2 agentic mechanism gain (3/3). The single strongest piece of evidence in this batch that a core agentic mechanism (graph traversal) fails to reliably beat single-query-style baseline RAG, directly serving question 4.

**Why it matters here.** Directly answers question 4 for the graph-traversal mechanism specifically: the citation/graph-traversal 'agentic move' does not reliably beat plain retrieval, and the paper gives task-level conditions for when it does \u2014 exactly the evidence the brief says it should reach hardest for.

**Method.** Comprehensive benchmark with tasks of increasing difficulty, evaluating the full GraphRAG pipeline from graph construction and retrieval through generation, compared against vanilla RAG. Abstract-only for detailed numbers.

**Limitations.**

- General-purpose RAG benchmark, not scientific-literature-search specific
- Abstract does not give the numeric size of the underperformance
- Findings tied to the specific GraphRAG implementations tested

<sub>selected: score · criteria: C1 2/3 · C2 3/3 · C3 2/3 · C4 3/3 · C5 3/3 · flags: contradicts, methods_paper · verified 2026-08-26 via openalex, arxiv</sub>

## 2. BrowseComp-Plus: A More Fair and Transparent Evaluation Benchmark of Deep-Research Agent

Zijian Chen, Xueguang Ma, Shengyao Zhuang, Ping Nie et al. · 2025 · arXiv (Cornell University) · computational · overall 3/3

<https://doi.org/10.48550/arxiv.2508.06600>

**Key finding.** With a fixed, human-verified corpus, Search-R1 with BM25 reaches only 3.86% accuracy while GPT-5 reaches 55.9%, and GPT-5 with the Qwen3-Embedding-8B retriever reaches 70.1% with fewer search calls.

**Why it made the cut.** foundational · selected by score · strongest on C1 baseline recall ceiling (3/3). The necessary foundational benchmark for anchoring baseline-vs-agentic gains, central to Q1, Q3, and Q4.

**Why it matters here.** Gives the field's clearest anchored baseline recall ceiling and the benchmark-construction template that later replication-failure studies are measured against.

**Method.** Benchmark derived from BrowseComp using a fixed curated corpus with human-verified supporting documents and mined hard negatives, enabling controlled disentanglement of retriever versus agent contribution.

**Limitations.**

- Corpus assembled per-query from the benchmark's own supporting documents, later shown to be potentially non-representative
- Single snapshot of models tested

<sub>selected: score · criteria: C1 3/3 · C2 2/3 · C3 2/3 · C4 3/3 · C5 2/3 · flags: methods_paper · verified 2026-08-26 via openalex, arxiv</sub>

## 3. Diagnosing Search Behavior and Failure Modes in Long-Horizon Search Agents

Qi Liu, Jiaxin Mao, Fengbin Zhu, Tat-Seng Chua · 2026 · arXiv · computational · overall 3/3

<https://doi.org/10.48550/arxiv.2608.01913>

**Key finding.** Search effort and answer quality are only weakly aligned; answer accuracy correlates more with cumulative retrieval recall than with number of searches, and top agents issue far fewer redundant queries.

**Why it made the cut.** plan-influencing · selected by score · strongest on C2 agentic mechanism gain (3/3). Directly decomposes what drives agentic gains (retrieval vs utilization) and shows where search effort fails to help, bearing on both Q2 and Q4.

**Why it matters here.** Shows that more agentic search effort does not reliably translate into better answers, undermining the assumption that agentic mechanisms automatically outperform simpler search, and points to recall-based stopping criteria as the metric worth measuring.

**Method.** Trajectory-level diagnosis with human-annotated document relevance judgments, retrieval model held fixed, comparing six agents on BrowseComp-Plus and validating on BrowseComp with an open-web search API.

**Limitations.**

- Evaluated on only two benchmark families (BrowseComp-Plus/BrowseComp)
- Six agents may not represent the full design space of agentic systems

<sub>selected: score · criteria: C1 2/3 · C2 3/3 · C3 1/3 · C4 2/3 · C5 3/3 · flags: contradicts · verified 2026-08-26 via openalex, arxiv</sub>

## 4. LLM-guided Hierarchical Search for End-to-end Reasoning Intensive Retrieval

Nilesh Gupta, Wei-Cheng Chang, N. Bui, Cho-Jui Hsieh et al. · 2025 · no venue · computational · overall 3/3

<https://arxiv.org/abs/2510.13217>

**Key finding.** LATTICE, an LLM-guided hierarchical search index with no embedding retriever in the loop, matches the best fine-tuned ensemble on BRIGHT (46.7 nDCG@10) and its ensemble variant reaches 49.1 nDCG@10.

**Why it made the cut.** design-changing · selected by score · strongest on C1 baseline recall ceiling (3/3). Provides both the recall-ceiling failure of standard embedding retrieval and an alternative retrieval/reranking method directly underlying agentic search systems.

**Why it matters here.** Demonstrates that single-query embedding retrieval fails on reasoning-intensive queries even for SOTA embedders, motivating a retrieval architecture that bypasses the vector-search baseline the brief asks us to anchor against.

**Method.** Top-down LLM-guided construction of a hierarchical corpus index over multi-level summaries plus calibrated, path-aggregated LLM traversal; evaluated on BRIGHT, NQ, SciFact, SciDocs.

**Limitations.**

- Evaluated mainly on general reasoning-IR benchmarks, not literature-search-specific corpora
- Needs a moderate token budget before its asymptotic advantage over reranking appears

<sub>selected: score · criteria: C1 3/3 · C2 2/3 · C3 3/3 · C4 1/3 · C5 2/3 · flags: methods_paper · verified 2026-08-26 via arxiv, s2</sub>

## 5. Projecting BrowseComp-Plus onto ClimbMix: Toward More Realistic Corpora for Agentic Search

Sahel Sharifymoghaddam, Lin Gu, Yijun Ge, Jimmy Lin · 2026 · no venue · computational · overall 3/3

<https://arxiv.org/abs/2608.20317>

**Key finding.** Relocating BrowseComp-Plus questions onto the independently-built ClimbMix corpus drops the strongest agent's evidence recall from 84.3% to 21.4% while answer accuracy falls only five points and search calls rise 63%.

**Why it made the cut.** contradicting · selected by score · strongest on C1 baseline recall ceiling (3/3). The clearest demonstration that a benchmark's construction inflates agentic gains and that those gains fail to hold under an independently-built corpus.

**Why it matters here.** Shows a widely-used benchmark's reported recall inflates because its corpus was assembled per-query, and that agentic evidence-recall gains shrink dramatically once relocated to a corpus built without benchmark awareness — the replication-failure evidence the brief is looking for.

**Method.** Projection pipeline decomposing questions into atomic reasoning hops, grounding each hop in a new 553M-document corpus (ClimbMix) via automatic verification, independent-agent check, and human review; applied to 830 BrowseComp-Plus questions, yielding 57 fully grounded questions.

**Limitations.**

- Pipeline yields only 57 grounded questions out of 830, a small evaluated subset
- Only a single projection target (ClimbMix) tested so far

<sub>selected: score · criteria: C1 3/3 · C2 0/3 · C3 1/3 · C4 3/3 · C5 3/3 · flags: contradicts, methods_paper · verified 2026-08-26 via arxiv, s2</sub>

## 6. BRIGHT: A Realistic and Challenging Benchmark for Reasoning-Intensive Retrieval

Hongjin Su, Howard Yen, Mengzhou Xia, Weijia Shi et al. · 2024 · International Conference on Learning Representations · experimental · overall 3/3

<https://doi.org/10.48550/arxiv.2407.12883>

**Key finding.** The leading MTEB embedding retriever (SFR-Embedding-Mistral, 59.0 nDCG@10 on standard benchmarks) scores only 18.3 nDCG@10 on BRIGHT's reasoning-intensive queries, though explicit query reasoning recovers up to 12.2 points.

**Why it made the cut.** foundational · selected by score · strongest on C1 baseline recall ceiling (3/3). Foundational baseline-ceiling result establishing how badly plain embedding search fails on reasoning-heavy queries, the anchor question 1 requires.

**Why it matters here.** Sets the single clearest, most quantified ceiling for single-query embedding-search recall under reasoning-intensive queries \u2014 the exact anchor question 1 needs before any agentic literature-search gain can be judged credible or inflated.

**Method.** 1,384 real-world, reasoning-intensive queries curated across economics, psychology, mathematics, and coding domains; extensive evaluation of state-of-the-art retrieval models. Abstract-only.

**Limitations.**

- Domains are economics/psychology/math/coding, not scientific-literature retrieval directly
- Predates most 2025-2026 agentic literature-search systems
- Gain from explicit reasoning (12.2 points) still leaves a large residual gap unexplained

<sub>selected: score · criteria: C1 3/3 · C2 1/3 · C3 2/3 · C4 3/3 · C5 1/3 · flags: methods_paper · verified 2026-08-26 via openalex, arxiv</sub>

## 7. OpenScholar: Synthesizing Scientific Literature with Retrieval-augmented LMs

Akari Asai, Jacqueline He, Rulin Shao, Weijia Shi et al. · 2024 · arXiv.org · experimental · overall 3/3

<https://doi.org/10.48550/arxiv.2411.14199>

**Key finding.** OpenScholar-8B, retrieving from 45 million open-access papers, outperforms GPT-4o by 5% and PaperQA2 by 7% in correctness on the new ScholarQABench benchmark (2,967 queries), while GPT-4o hallucinates citations 78-90% of the time versus OpenScholar's expert-level citation accuracy.

**Why it made the cut.** design-changing · selected by score · strongest on C3 retrieval/reranking method (3/3). Closest prior work to the system the brief is scoping, with its own purpose-built benchmark and quantified gains over strong baselines.

**Why it matters here.** The closest existing system to what the brief is scoping \u2014 a full literature-search-and-synthesis agent with its own purpose-built benchmark and quantified baseline comparisons \u2014 making it the primary comparison point for design and evaluation decisions.

**Method.** Retrieval-augmented LM with a dedicated 45M-paper datastore, retriever, and self-feedback inference loop, evaluated on a newly built multi-domain benchmark (ScholarQABench) plus human preference studies.

**Limitations.**

- domain coverage limited to CS/physics/neuroscience/biomedicine
- self-feedback loop's specific contribution not isolated from the rest of the system

<sub>selected: score · criteria: C1 2/3 · C2 2/3 · C3 3/3 · C4 3/3 · C5 0/3 · verified 2026-08-26 via openalex, arxiv</sub>

## 8. LitSearch: A Retrieval Benchmark for Scientific Literature Search

Anirudh Ajith, Mengzhou Xia, Alexis Chevalier, Tanya Goyal et al. · 2024 · Conference on Empirical Methods in Natural Language Processing · experimental · overall 3/3

<https://doi.org/10.48550/arxiv.2407.18940>

**Key finding.** On 597 realistic literature-search queries, BM25 trails state-of-the-art dense retrievers by 24.8 points of absolute recall@5, LLM-based reranking further improves the best dense retriever by 4.4%, and commercial search engines/Google lag the best dense retriever by 32 points.

**Why it made the cut.** foundational · selected by backfill · strongest on C1 baseline recall ceiling (3/3). The foundational quantified baseline and benchmark-construction template anchoring the brief's recall-ceiling and benchmark-construction questions.

**Why it matters here.** Gives the single clearest, quantified statement of the baseline recall ceiling (BM25 vs. dense vs. commercial search) that every later agentic-search claim in this space should be measured against.

**Method.** New retrieval benchmark (LitSearch) built from GPT-4-generated questions over cited paragraphs plus author-written questions about their own recent papers, all expert-verified; extensive benchmarking of retrievers, rerankers, and commercial search engines.

**Limitations.**

- restricted to ML/NLP papers
- queries partly LLM-generated rather than naturally occurring
- does not test full multi-step agentic search pipelines

<sub>selected: backfill · criteria: C1 3/3 · C2 1/3 · C3 3/3 · C4 3/3 · C5 0/3 · verified 2026-08-26 via openalex, arxiv</sub>

## 9. PaSa: An LLM Agent for Comprehensive Academic Paper Search

Yichen He, Guanhua Huang, Peiyuan Feng, Yuan Lin et al. · 2025 · Annual Meeting of the Association for Computational Linguistics · computational · overall 3/3

<https://doi.org/10.48550/arxiv.2501.10120>

**Key finding.** PaSa-7B surpasses the best Google+GPT-4o baseline by 37.78% in recall@20 and 39.90% in recall@50 on the real-world RealScholarQuery benchmark.

**Why it made the cut.** foundational · selected by backfill · strongest on C1 baseline recall ceiling (3/3). Closest prior work establishing the quantified agentic-vs-single-query-search gain and the benchmark-construction template underlying it.

**Why it matters here.** Establishes the quantified baseline-vs-agent recall gap for academic paper search and the benchmark construction (AutoScholarQuery/RealScholarQuery) much later work is measured against.

**Method.** RL-trained LLM agent that invokes search tools, reads papers, and selects references; trained on the synthetic AutoScholarQuery dataset (35k queries) and evaluated on RealScholarQuery against Google/Scholar/ChatGPT baselines.

**Limitations.**

- Training data drawn from top-tier AI conference papers may not generalize to other fields
- Comparisons against live Google baselines are hard to reproduce as APIs change

<sub>selected: backfill · criteria: C1 3/3 · C2 2/3 · C3 1/3 · C4 3/3 · C5 0/3 · flags: methods_paper · verified 2026-08-26 via openalex, arxiv</sub>

## 10. Deep Research Agents: A Systematic Examination And Roadmap

Yuxuan Huang, Yihang Chen, Haozhen Zhang, Kang Li et al. · 2025 · arXiv.org · other · overall 3/3

<https://doi.org/10.48550/arxiv.2506.18096>

**Key finding.** Provides a taxonomy of Deep Research agent architectures (static/dynamic workflows, single/multi-agent) and a critical evaluation identifying benchmark limitations including restricted external-knowledge access and metric-objective misalignment.

**Why it made the cut.** foundational · selected by review · strongest on C4 benchmark construction (3/3). The field's synthesis and critique of benchmark limitations, providing review-level orientation before weighing individual studies.

**Why it matters here.** Orients the scan to the field's existing critique of benchmark construction and agent architecture taxonomy, flagging exactly the benchmark-construction weaknesses (Q3) and evaluation-metric misalignment (Q4) the brief asks about.

**Method.** Abstract-only narrative synthesis and taxonomy across Deep Research agent literature, with a critical review of current benchmarks.

**Limitations.**

- Narrative review with no explicit systematic protocol
- Abstract gives no quantified findings

<sub>selected: review · criteria: C1 2/3 · C2 1/3 · C3 1/3 · C4 3/3 · C5 1/3 · flags: review · verified 2026-08-26 via arxiv</sub>

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

- [Towards Recursive Self-Evolving Agentic Literature Retrieval](https://doi.org/10.48550/arxiv.2605.14306) (2026) — overall 3/3
- [Is Grep All You Need? How Agent Harnesses Reshape Agentic Search](https://doi.org/10.48550/arxiv.2605.15184) (2026) — overall 3/3
- [Structurally-bounded Agentic Graph Exploration for Evidence-Grounded Scholarly DeepSearch](https://doi.org/10.48550/arxiv.2608.24809) (2026) — overall 3/3
- [Deep Research: A Survey of Autonomous Research Agents](https://doi.org/10.48550/arxiv.2508.12752) (2025) — overall 3/3
- [Fact, Fetch, and Reason: A Unified Evaluation of Retrieval-Augmented Generation](https://doi.org/10.48550/arxiv.2409.12941) (2024) — overall 3/3
