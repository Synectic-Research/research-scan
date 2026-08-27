# Evidence scan — p11-t2

Run `/Users/nabergoj/Projects/research-scan/research/experiments/phase14/runs/p11-t2/SC/rep5/run` · brief `/Users/nabergoj/Projects/research-scan/research/experiments/phase14/runs/p11-t2/SC/rep5/run/brief.md` · rendered 2026-08-27

| # | Paper | Year | Venue | Evidence | Verified |
|---|---|---|---|---|---|
| 1 | [When to use Graphs in RAG: A Comprehensive Analysis for Graph Retrieval-Augmented Generation](https://doi.org/10.48550/arxiv.2506.05690) · 10.48550/arxiv.2506.05690 | 2025 | arXiv.org | experimental | yes |
| 2 | [Diagnosing Search Behavior and Failure Modes in Long-Horizon Search Agents](https://doi.org/10.48550/arxiv.2608.01913) · 10.48550/arxiv.2608.01913 | 2026 | arXiv | experimental | yes |
| 3 | [Deep Research Agents: A Systematic Examination And Roadmap](https://doi.org/10.48550/arxiv.2506.18096) · 10.48550/arxiv.2506.18096 | 2025 | arXiv.org | other | yes |
| 4 | [BRIGHT: A Realistic and Challenging Benchmark for Reasoning-Intensive Retrieval](https://doi.org/10.48550/arxiv.2407.12883) · 10.48550/arxiv.2407.12883 | 2024 | International Conference on Learning Representations | experimental | yes |
| 5 | [OpenScholar: Synthesizing Scientific Literature with Retrieval-augmented LMs](https://doi.org/10.48550/arxiv.2411.14199) · 10.48550/arxiv.2411.14199 | 2024 | arXiv.org | experimental | yes |
| 6 | [BrowseComp-Plus: A More Fair and Transparent Evaluation Benchmark of Deep-Research Agent](https://doi.org/10.48550/arxiv.2508.06600) · 10.48550/arxiv.2508.06600 | 2025 | arXiv (Cornell University) | experimental | yes |
| 7 | [Towards Recursive Self-Evolving Agentic Literature Retrieval](https://doi.org/10.48550/arxiv.2605.14306) · 10.48550/arxiv.2605.14306 | 2026 | arXiv | experimental | yes |
| 8 | [Projecting BrowseComp-Plus onto ClimbMix: Toward More Realistic Corpora for Agentic Search](https://arxiv.org/abs/2608.20317) | 2026 | — | experimental | yes |
| 9 | [LitSearch: A Retrieval Benchmark for Scientific Literature Search](https://doi.org/10.48550/arxiv.2407.18940) · 10.48550/arxiv.2407.18940 | 2024 | Conference on Empirical Methods in Natural Language Processing | experimental | yes |
| 10 | [PaSa: An LLM Agent for Comprehensive Academic Paper Search](https://doi.org/10.48550/arxiv.2501.10120) · 10.48550/arxiv.2501.10120 | 2025 | Annual Meeting of the Association for Computational Linguistics | experimental | yes |

## 1. When to use Graphs in RAG: A Comprehensive Analysis for Graph Retrieval-Augmented Generation

Zhishang Xiang, Chuan-Yu Wu, Qinggang Zhang, Shengyuan Chen et al. · 2025 · arXiv.org · experimental · overall 3/3

<https://doi.org/10.48550/arxiv.2506.05690>

**Key finding.** GraphRAG frequently underperforms vanilla RAG on many real-world tasks; the newly introduced GraphRAG-Bench (fact retrieval, complex reasoning, contextual summarization, creative generation) is used to systematically identify when graph structure actually helps.

**Why it made the cut.** contradicting · selected by score · strongest on C2 agentic mechanism gain (3/3). Contradicts the premise that graph-based (citation-graph-like) retrieval reliably improves on vanilla retrieval, and supplies benchmark-construction precedent for testing when it does — the same graph-retrieval mechanism underlies citation-graph traversal in agentic literature search.

**Why it matters here.** Directly tests the premise that graph-structured retrieval — the mechanism underlying citation-graph traversal in agentic literature-search systems — reliably beats plain retrieval, and finds it frequently does not; this is exactly the gain-replication-failure evidence the brief asks the scan to reach hardest for.

**Method.** New benchmark with a full-pipeline evaluation protocol (graph construction, retrieval, generation) across tasks of increasing difficulty, used to compare GraphRAG against traditional RAG systematically.

**Limitations.**

- Tasks are general-knowledge RAG benchmarks, not scientific literature search specifically
- findings concern graph-augmented generation broadly, not literature-search agents in particular
- abstract gives no specific effect sizes for the underperformance

<sub>selected: score · criteria: C1 2/3 · C2 3/3 · C3 2/3 · C4 3/3 · C5 3/3 · flags: contradicts, methods_paper · verified 2026-08-27 via openalex, arxiv</sub>

## 2. Diagnosing Search Behavior and Failure Modes in Long-Horizon Search Agents

Qi Liu, Jiaxin Mao, Fengbin Zhu, Tat-Seng Chua · 2026 · arXiv · experimental · overall 3/3

<https://doi.org/10.48550/arxiv.2608.01913>

**Key finding.** Across six agents on BrowseComp-Plus and BrowseComp, answer accuracy tracks cumulative retrieval recall far more than the number of searches issued, and the best agents issue far fewer redundant queries while useful evidence typically appears early in the trajectory.

**Why it made the cut.** plan-influencing · selected by score · strongest on C2 agentic mechanism gain (3/3). Directly answers where agentic gains fail to hold (redundant search, weak effort-quality link) and what actually drives quality (retrieval recall), core to Q2 and Q4.

**Why it matters here.** Directly undercuts the premise that more agentic search effort produces proportional gains, and reframes the measurement question toward cumulative recall and stopping criteria rather than search count.

**Method.** Trajectory-level diagnosis using human-annotated document relevance judgments, decomposing failures into retrieval gaps vs utilization gaps; retrieval model and evaluation harness held fixed across six agents on BrowseComp-Plus, validated on BrowseComp with a live web API.

**Limitations.**

- single retrieval model/harness held fixed, limiting generalization across retrievers
- focuses on six specific agents, not a representative sample of all architectures

<sub>selected: score · criteria: C1 2/3 · C2 3/3 · C3 1/3 · C4 2/3 · C5 3/3 · flags: contradicts · verified 2026-08-27 via openalex, arxiv</sub>

## 3. Deep Research Agents: A Systematic Examination And Roadmap

Yuxuan Huang, Yihang Chen, Haozhen Zhang, Kang Li et al. · 2025 · arXiv.org · other · overall 3/3

<https://doi.org/10.48550/arxiv.2506.18096>

**Key finding.** A systematic taxonomy of Deep Research agent architectures (static vs dynamic workflows, single- vs multi-agent, API-based vs browser-based retrieval) coupled with a critical evaluation identifying restricted external-knowledge access, sequential execution inefficiencies, and metric-objective misalignment as key benchmark limitations.

**Why it made the cut.** foundational · selected by score · strongest on C4 benchmark construction (3/3). The synthesis paper most directly structured around the brief's own four questions (baseline ceiling, mechanism attribution, benchmark construction, evaluation misalignment), serving as an orienting map for the rest of the evidence.

**Why it matters here.** Provides the field-level map of architectural moves (reformulation, tool use, planning strategies) and explicitly critiques current benchmarks' construction and metric validity, directly informing all four of the brief's questions in one place.

**Method.** Narrative survey and taxonomy of Deep Research agent architectures, tool-use frameworks, and benchmarks, with a maintained repository of DR agent research.

**Limitations.**

- narrative/non-systematic review methodology, not a quantitative meta-analysis
- abstract gives no effect sizes or comparative numbers of its own

<sub>selected: score · criteria: C1 2/3 · C2 2/3 · C3 2/3 · C4 3/3 · C5 2/3 · flags: review · verified 2026-08-27 via arxiv</sub>

## 4. BRIGHT: A Realistic and Challenging Benchmark for Reasoning-Intensive Retrieval

Hongjin Su, Howard Yen, Mengzhou Xia, Weijia Shi et al. · 2024 · International Conference on Learning Representations · experimental · overall 3/3

<https://doi.org/10.48550/arxiv.2407.12883>

**Key finding.** The leading MTEB retrieval model (SFR-Embedding-Mistral, 59.0 nDCG@10 on MTEB) scores only 18.3 nDCG@10 on BRIGHT's 1,384 reasoning-intensive real-world queries, and adding explicit reasoning about the query improves retrieval by up to 12.2 points.

**Why it made the cut.** foundational · selected by score · strongest on C1 baseline recall ceiling (3/3). Foundational benchmark precedent quantifying the recall/ranking ceiling of single-query embedding search on reasoning-intensive queries, exactly the baseline the brief's first question asks to anchor against.

**Why it matters here.** Quantifies exactly how far a single-query embedding-search ceiling can fall for reasoning-intensive queries (59.0 to 18.3 nDCG@10), giving the clearest numeric anchor for the brief's first question and a benchmark-construction precedent widely used to test whether reformulation or agentic reasoning recovers the gap.

**Method.** New retrieval benchmark of 1,384 naturally-occurring, curated queries spanning economics, psychology, mathematics, and coding, requiring reasoning beyond surface-form matching; extensive evaluation of state-of-the-art retrieval models.

**Limitations.**

- Domains are economics, psychology, mathematics, and coding, not scientific literature search specifically
- does not test full agentic pipelines, only retrieval models plus a reasoning-augmented query step
- no citation-graph or iterative-crawling mechanism evaluated

<sub>selected: score · criteria: C1 3/3 · C2 1/3 · C3 3/3 · C4 3/3 · C5 1/3 · flags: methods_paper · verified 2026-08-27 via openalex, arxiv</sub>

## 5. OpenScholar: Synthesizing Scientific Literature with Retrieval-augmented LMs

Akari Asai, Jacqueline He, Rulin Shao, Weijia Shi et al. · 2024 · arXiv.org · experimental · overall 3/3

<https://doi.org/10.48550/arxiv.2411.14199>

**Key finding.** OpenScholar-8B outperforms GPT-4o by 5% and PaperQA2 by 7% in correctness on the new ScholarQABench (2,967 expert queries across CS, physics, neuroscience, and biomedicine), while GPT-4o hallucinates citations 78-90% of the time versus OpenScholar's expert-level citation accuracy.

**Why it made the cut.** design-changing · selected by score · strongest on C3 retrieval/reranking method (3/3). The closest prior work to the brief's exact object of study — a literature-search agentic system with its own large-scale multi-domain benchmark and explicit baseline comparisons.

**Why it matters here.** The strongest, most directly comparable system-and-benchmark pairing for agentic scientific literature synthesis available, giving concrete baseline numbers and a benchmark-construction template the rest of the evidence portfolio should be measured against.

**Method.** Retrieval-augmented LM over a 45-million-paper open-access datastore with a self-feedback inference loop; evaluated on the newly built multi-domain ScholarQABench against GPT-4o, PaperQA2, and human experts.

**Limitations.**

- benchmark built and evaluated by the same team as the system
- correctness judging protocol only summarized in the abstract

<sub>selected: score · criteria: C1 2/3 · C2 2/3 · C3 3/3 · C4 3/3 · C5 1/3 · flags: methods_paper · verified 2026-08-27 via openalex, arxiv</sub>

## 6. BrowseComp-Plus: A More Fair and Transparent Evaluation Benchmark of Deep-Research Agent

Zijian Chen, Xueguang Ma, Shengyao Zhuang, Ping Nie et al. · 2025 · arXiv (Cornell University) · experimental · overall 3/3

<https://doi.org/10.48550/arxiv.2508.06600>

**Key finding.** On a fixed, human-verified corpus, Search-R1 with BM25 retrieval achieves only 3.86% accuracy while GPT-5 achieves 55.9%, and pairing GPT-5 with a Qwen3-Embedding-8B retriever raises accuracy to 70.1% with fewer search calls.

**Why it made the cut.** foundational · selected by score · strongest on C1 baseline recall ceiling (3/3). The foundational, controlled benchmark that anchors the recall-ceiling comparison (Q1) and benchmark-construction question (Q3) for this literature, and that other shortlisted papers directly build on.

**Why it matters here.** Establishes the clearest quantified baseline recall ceiling for single-query retrieval (BM25) against agentic performance on a controlled corpus, and is the benchmark precedent that later work in this set builds on and stress-tests.

**Method.** Introduces a fixed, curated corpus with human-verified supporting documents and mined hard negatives derived from BrowseComp, enabling controlled comparison of deep-research agents and retrievers.

**Limitations.**

- fixed corpus assembled specifically to support and challenge BrowseComp queries, so difficulty is calibrated to that query set
- does not itself test whether agentic gains generalize to other corpora (addressed by later projection work)

<sub>selected: score · criteria: C1 3/3 · C2 1/3 · C3 2/3 · C4 3/3 · C5 1/3 · flags: methods_paper · verified 2026-08-27 via openalex, arxiv</sub>

## 7. Towards Recursive Self-Evolving Agentic Literature Retrieval

Yuwen Du, Tian Jin, Jing Kang, Xianghe Pang et al. · 2026 · arXiv · experimental · overall 3/3

<https://doi.org/10.48550/arxiv.2605.14306>

**Key finding.** PaSaMaster achieves a 16.5x higher F1-score than Google Scholar and a 37.8% higher F1-score than GPT-5.2 at about 1% of the cost across 38 disciplines in PaSaMaster-Bench, while cutting source hallucination from 32.66% to zero.

**Why it made the cut.** closely-related · selected by score · strongest on C1 baseline recall ceiling (3/3). Most direct current evidence on the brief's central baseline-vs-agentic-gain question, in the exact scientific-literature-search setting.

**Why it matters here.** Directly anchors the brief's first question with an explicit single-query baseline (Google Scholar) and attributes the gain to a specific mechanism (self-evolving retrieval refining intent), giving the clearest quantified agentic-vs-baseline comparison in the set.

**Method.** Recursive self-evolving agentic retrieval system separating intent-understanding (frontier LLM) from retrieval/scoring (lightweight models), evaluated against Google Scholar and GPT-5.2 baselines on a new 38-discipline benchmark. Abstract-only for benchmark construction detail.

**Limitations.**

- Extremely large reported multiplier (16.5x) invites scrutiny for benchmark or baseline-selection artifacts
- benchmark introduced by the same team with construction detail not given in the abstract
- no replication against an independent benchmark

<sub>selected: score · criteria: C1 3/3 · C2 3/3 · C3 2/3 · C4 2/3 · C5 0/3 · flags: methods_paper · verified 2026-08-27 via openalex, arxiv</sub>

## 8. Projecting BrowseComp-Plus onto ClimbMix: Toward More Realistic Corpora for Agentic Search

Sahel Sharifymoghaddam, Lin Gu, Yijun Ge, Jimmy Lin · 2026 · no venue · experimental · overall 3/3

<https://arxiv.org/abs/2608.20317>

**Key finding.** Relocating BrowseComp-Plus's evidence into a benchmark-agnostic corpus (ClimbMix) drops the strongest agent's evidence recall from 84.3% to 21.4% and answer accuracy by five points, while search calls rise 63%.

**Why it made the cut.** contradicting · selected by score · strongest on C4 benchmark construction (3/3). The single clearest demonstration in this batch that a reported agentic gain shrinks dramatically under a different, less benchmark-selected corpus, squarely answering Q4.

**Why it matters here.** Directly demonstrates that a reported agentic gain, measured on a benchmark whose corpus was assembled from the queries' own supporting evidence, collapses once the same questions are re-grounded in an independently built corpus — the clearest replication-failure evidence in this set.

**Method.** A dataset-agnostic projection pipeline that decomposes benchmark questions into atomic reasoning hops, grounds each hop in a new 553M-document corpus not built with reference to the benchmark, and retains only hops verified by automated checks, an independent agent, and human review; applied to the 830 BrowseComp-Plus questions to yield 57 fully grounded questions.

**Limitations.**

- yields only 57 fully grounded questions out of 830, a small resulting evaluation set
- projection pipeline itself relies on automated and agent-based verification whose own error rate is not fully characterized

<sub>selected: score · criteria: C1 2/3 · C2 1/3 · C3 0/3 · C4 3/3 · C5 3/3 · flags: contradicts, methods_paper · verified 2026-08-27 via arxiv, s2</sub>

## 9. LitSearch: A Retrieval Benchmark for Scientific Literature Search

Anirudh Ajith, Mengzhou Xia, Alexis Chevalier, Tanya Goyal et al. · 2024 · Conference on Empirical Methods in Natural Language Processing · experimental · overall 3/3

<https://doi.org/10.48550/arxiv.2407.18940>

**Key finding.** On 597 realistic literature-search queries, LitSearch finds a 24.8-point absolute recall@5 gap between BM25 and the best dense retriever, with LLM-based reranking adding a further 4.4-point improvement, while commercial search engines lag the best dense retriever by 32 points.

**Why it made the cut.** foundational · selected by backfill · strongest on C1 baseline recall ceiling (3/3). The foundational retrieval benchmark for scientific literature search that directly answers the baseline recall ceiling question and sets the benchmark-construction precedent.

**Why it matters here.** Directly quantifies the single-query baseline recall ceiling (BM25) against dense and reranked retrieval for scientific literature search, and documents exactly how its queries were sourced and validated — the precedent every benchmark-construction claim in this space should be measured against.

**Method.** Benchmark built from GPT-4-generated questions over cited paragraphs plus author-written questions about their own recent papers, all expert-verified; extensive benchmarking of retrieval and reranking models.

**Limitations.**

- ML/NLP papers only, not multi-domain science
- does not itself evaluate agentic/iterative systems

<sub>selected: backfill · criteria: C1 3/3 · C2 0/3 · C3 2/3 · C4 3/3 · C5 1/3 · flags: methods_paper · verified 2026-08-27 via openalex, arxiv</sub>

## 10. PaSa: An LLM Agent for Comprehensive Academic Paper Search

Yichen He, Guanhua Huang, Peiyuan Feng, Yuan Lin et al. · 2025 · Annual Meeting of the Association for Computational Linguistics · experimental · overall 3/3

<https://doi.org/10.48550/arxiv.2501.10120>

**Key finding.** PaSa-7B surpasses the best Google-based baseline by 37.78% in recall@20 and 39.90% in recall@50 on RealScholarQuery, and exceeds a prompted PaSa-GPT-4o variant by 30.36% in recall.

**Why it made the cut.** foundational · selected by backfill · strongest on C1 baseline recall ceiling (3/3). Closest prior work to the brief's exact target system (an LLM agent for academic paper search) with the clearest baseline-vs-agent recall numbers and benchmark construction detail.

**Why it matters here.** The clearest quantified anchor for how far agentic academic search exceeds single-query search-engine baselines, and a template for benchmark construction (synthetic training set plus held-out real-world eval) that later systems are measured against.

**Method.** RL-trained LLM agent that issues searches, reads papers, and selects references; trained on a synthetic 35k-query dataset (AutoScholarQuery) and evaluated on a new real-world benchmark (RealScholarQuery) against search-engine and LLM-augmented-search baselines.

**Limitations.**

- trained on synthetic queries derived from top-tier AI conference papers, may not generalize to other fields
- comparison baselines are search engines rather than a controlled fixed-corpus retriever

<sub>selected: backfill · criteria: C1 3/3 · C2 1/3 · C3 1/3 · C4 3/3 · C5 0/3 · flags: methods_paper · verified 2026-08-27 via openalex, arxiv</sub>

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

- [Deep Research: A Survey of Autonomous Research Agents](https://doi.org/10.48550/arxiv.2508.12752) (2025) — overall 3/3
- [Multi-Agent System for Scientific Literature Search and Recommendation](https://doi.org/10.1109/icssas66150.2025.11081082) (2025) — overall 3/3
- [Patience is all you need! An agentic system for performing scientific literature review](https://doi.org/10.48550/arxiv.2504.08752) (2025) — overall 3/3
- [CG-RAG: Research Question Answering by Citation Graph Retrieval-Augmented LLMs](https://doi.org/10.1145/3726302.3729920) (2025) — overall 3/3
- [Structurally-bounded Agentic Graph Exploration for Evidence-Grounded Scholarly DeepSearch](https://doi.org/10.48550/arxiv.2608.24809) (2026) — overall 3/3
