# Evidence scan — p11-t2

Run `/Users/nabergoj/Projects/research-scan/research/experiments/phase14/runs/p11-t2/C0/rep1/run` · brief `/Users/nabergoj/Projects/research-scan/research/experiments/phase14/runs/p11-t2/C0/rep1/run/brief.md` · rendered 2026-08-26

| # | Paper | Year | Venue | Evidence | Verified |
|---|---|---|---|---|---|
| 1 | [Diagnosing Search Behavior and Failure Modes in Long-Horizon Search Agents](https://doi.org/10.48550/arxiv.2608.01913) · 10.48550/arxiv.2608.01913 | 2026 | arXiv | experimental | yes |
| 2 | [BrowseComp-Plus: A More Fair and Transparent Evaluation Benchmark of Deep-Research Agent](https://doi.org/10.48550/arxiv.2508.06600) · 10.48550/arxiv.2508.06600 | 2025 | arXiv (Cornell University) | experimental | yes |
| 3 | [LitSearch: A Retrieval Benchmark for Scientific Literature Search](https://doi.org/10.48550/arxiv.2407.18940) · 10.48550/arxiv.2407.18940 | 2024 | Conference on Empirical Methods in Natural Language Processing | experimental | yes |
| 4 | [OpenScholar: Synthesizing Scientific Literature with Retrieval-augmented LMs](https://doi.org/10.48550/arxiv.2411.14199) · 10.48550/arxiv.2411.14199 | 2024 | arXiv.org | experimental | yes |
| 5 | [Deep Research Agents: A Systematic Examination And Roadmap](https://doi.org/10.48550/arxiv.2506.18096) · 10.48550/arxiv.2506.18096 | 2025 | arXiv.org | other | yes |
| 6 | [Towards Recursive Self-Evolving Agentic Literature Retrieval](https://doi.org/10.48550/arxiv.2605.14306) · 10.48550/arxiv.2605.14306 | 2026 | arXiv | experimental | yes |
| 7 | [Deep Research: A Survey of Autonomous Research Agents](https://doi.org/10.48550/arxiv.2508.12752) · 10.48550/arxiv.2508.12752 | 2025 | arXiv.org | other | yes |
| 8 | [CG-RAG: Research Question Answering by Citation Graph Retrieval-Augmented LLMs](https://doi.org/10.1145/3726302.3729920) · 10.1145/3726302.3729920 | 2025 | Annual International ACM SIGIR Conference on Research and Development in Information Retrieval | experimental | yes |
| 9 | [Projecting BrowseComp-Plus onto ClimbMix: Toward More Realistic Corpora for Agentic Search](https://arxiv.org/abs/2608.20317) | 2026 | — | experimental | yes |
| 10 | [PaSa: An LLM Agent for Comprehensive Academic Paper Search](https://doi.org/10.48550/arxiv.2501.10120) · 10.48550/arxiv.2501.10120 | 2025 | Annual Meeting of the Association for Computational Linguistics | experimental | yes |

## 1. Diagnosing Search Behavior and Failure Modes in Long-Horizon Search Agents

Qi Liu, Jiaxin Mao, Fengbin Zhu, Tat-Seng Chua · 2026 · arXiv · experimental · overall 3/3

<https://doi.org/10.48550/arxiv.2608.01913>

**Key finding.** Across six agents on BrowseComp-Plus and BrowseComp, search effort and answer quality are only weakly aligned; accuracy tracks cumulative retrieval recall far better than number of searches, and the best agents issue far fewer redundant queries while useful evidence often appears early yet agents keep searching anyway.

**Why it made the cut.** contradicting · selected by score · strongest on C2 agentic mechanism gain (3/3). Provides trajectory-level evidence on exactly which agentic moves carry gains and where they fail, the core of the brief's Q2 and Q4.

**Why it matters here.** Directly answers Q2 and Q4: it decomposes agentic gains into retrieval-gap vs utilization-gap failures and shows more searching does not reliably buy more accuracy, undercutting the assumption that iterative crawling itself is the source of improvement.

**Method.** Trajectory-level diagnosis with human-annotated document relevance judgments, holding retriever and evaluation harness fixed across six long-horizon search agents on BrowseComp-Plus, validated on BrowseComp with an open-web API.

**Limitations.**

- Findings specific to BrowseComp-Plus/BrowseComp query distributions
- retrieval model and harness held fixed, so results may not generalize to different retrievers

<sub>selected: score · criteria: C1 2/3 · C2 3/3 · C3 1/3 · C4 1/3 · C5 3/3 · flags: contradicts, methods_paper · verified 2026-08-26 via openalex, arxiv</sub>

## 2. BrowseComp-Plus: A More Fair and Transparent Evaluation Benchmark of Deep-Research Agent

Zijian Chen, Xueguang Ma, Shengyao Zhuang, Ping Nie et al. · 2025 · arXiv (Cornell University) · experimental · overall 3/3

<https://doi.org/10.48550/arxiv.2508.06600>

**Key finding.** On a fixed, human-verified corpus, Search-R1 with BM25 achieves only 3.86% accuracy while GPT-5 achieves 55.9%, and pairing GPT-5 with a Qwen3-Embedding-8B retriever raises accuracy to 70.1% with fewer search calls.

**Why it made the cut.** plan-influencing · selected by score · strongest on C1 baseline recall ceiling (3/3). The controlled-corpus benchmark central to disentangling retriever from agent contribution, directly answering the brief's baseline and benchmark-construction questions.

**Why it matters here.** Establishes exactly the kind of baseline-recall/accuracy anchor Q1 requires and the corpus-construction transparency Q3 asks for; it is the benchmark other papers in this scan (e.g. the ClimbMix projection) build directly on and critique.

**Method.** Fixed-corpus benchmark derived from BrowseComp with human-verified supporting documents and mined hard negatives, enabling controlled disentangling of agent and retriever contributions.

**Limitations.**

- Corpus assembled specifically from the benchmark's own queries plus mined negatives, which later work shows may inflate results
- single benchmark domain (BrowseComp-style open-domain questions)

<sub>selected: score · criteria: C1 3/3 · C2 1/3 · C3 2/3 · C4 3/3 · C5 1/3 · flags: methods_paper · verified 2026-08-26 via openalex, arxiv</sub>

## 3. LitSearch: A Retrieval Benchmark for Scientific Literature Search

Anirudh Ajith, Mengzhou Xia, Alexis Chevalier, Tanya Goyal et al. · 2024 · Conference on Empirical Methods in Natural Language Processing · experimental · overall 3/3

<https://doi.org/10.48550/arxiv.2407.18940>

**Key finding.** On LitSearch (597 realistic literature-search queries, built from GPT-4-generated and author-written questions), there is a 24.8% absolute recall@5 gap between BM25 and state-of-the-art dense retrievers, LLM reranking adds a further 4.4%, and commercial search engines lag the best dense retriever by 32 points.

**Why it made the cut.** design-changing · selected by score · strongest on C1 baseline recall ceiling (3/3). Provides the exact baseline recall-ceiling numbers and a transparent benchmark-construction method the brief's four questions are anchored on.

**Why it matters here.** Directly establishes the single-query baseline recall ceiling (BM25 vs dense) the brief's question 1 asks for, with an exact quantified gap, and documents a transparent benchmark-construction methodology against which agentic gains can be measured.

**Method.** New retrieval benchmark constructed from GPT-4-generated questions over cited paragraphs plus author-written questions about recent papers, expert-verified, benchmarking retrievers and LLM reranking pipelines.

**Limitations.**

- restricted to recent ML/NLP papers, not the full scientific literature
- queries are partly LLM-generated, which could bias toward citation-context-style questions

<sub>selected: score · criteria: C1 3/3 · C2 1/3 · C3 2/3 · C4 3/3 · C5 1/3 · flags: methods_paper · verified 2026-08-26 via openalex, arxiv</sub>

## 4. OpenScholar: Synthesizing Scientific Literature with Retrieval-augmented LMs

Akari Asai, Jacqueline He, Rulin Shao, Weijia Shi et al. · 2024 · arXiv.org · experimental · overall 3/3

<https://doi.org/10.48550/arxiv.2411.14199>

**Key finding.** OpenScholar, retrieving from 45M open-access papers with a self-feedback inference loop, outperforms GPT-4o by 5% and PaperQA2 by 7% in correctness on the new ScholarQABench (2,967 queries), while GPT-4o hallucinates citations 78-90% of the time versus OpenScholar's human-level citation accuracy.

**Why it made the cut.** design-changing · selected by score · strongest on C2 agentic mechanism gain (3/3). A flagship agentic scientific-literature-search system with explicit per-component gain attribution and a large multi-domain benchmark, matching all three of the brief's in-scope areas.

**Why it matters here.** The clearest direct system-plus-benchmark answer to the brief's core question: it isolates the datastore/retriever/self-feedback loop's individual contribution (e.g., +12% correctness for GPT-4o) and quantifies baseline citation hallucination, giving both a mechanism attribution and a benchmark construction reference.

**Method.** Retrieval-augmented LM with dedicated datastore, retriever, and self-feedback inference loop, evaluated on a new multi-domain benchmark (ScholarQABench) with human expert comparison.

**Limitations.**

- benchmark built with the same team that built the system, raising potential construction bias
- abstract does not report failure cases or replication under an independent benchmark

<sub>selected: score · criteria: C1 2/3 · C2 3/3 · C3 2/3 · C4 2/3 · C5 0/3 · flags: methods_paper · verified 2026-08-26 via openalex, arxiv</sub>

## 5. Deep Research Agents: A Systematic Examination And Roadmap

Yuxuan Huang, Yihang Chen, Haozhen Zhang, Kang Li et al. · 2025 · arXiv.org · other · overall 3/3

<https://doi.org/10.48550/arxiv.2506.18096>

**Key finding.** A systematic taxonomy of Deep Research agents by information-acquisition strategy, planning strategy, and agent composition, paired with a critical evaluation identifying restricted external-knowledge access, sequential execution inefficiencies, and metric-objective misalignment as key benchmark limitations.

**Why it made the cut.** plan-influencing · selected by score · strongest on C4 benchmark construction (3/3). The synthesis paper mapping system designs, benchmarks, and their limitations across the exact space the brief is scanning.

**Why it matters here.** Directly answers Q3 by cataloguing how benchmarks in this space are built and where their construction misaligns with what DR agents actually need to be evaluated on, giving the project a map of the whole design and evaluation space before committing to any one system.

**Method.** Narrative systematic review and taxonomy construction over the Deep Research agent literature, with an accompanying curated repository.

**Limitations.**

- Narrative rather than systematic-protocol review
- no new empirical results of its own
- taxonomy reflects state as of survey date and will age quickly in a fast-moving field

<sub>selected: score · criteria: C1 1/3 · C2 1/3 · C3 2/3 · C4 3/3 · C5 1/3 · flags: review · verified 2026-08-26 via arxiv</sub>

## 6. Towards Recursive Self-Evolving Agentic Literature Retrieval

Yuwen Du, Tian Jin, Jing Kang, Xianghe Pang et al. · 2026 · arXiv · experimental · overall 3/3

<https://doi.org/10.48550/arxiv.2605.14306>

**Key finding.** PaSaMaster achieves a 16.5x higher F1-score than Google Scholar and 37.8% higher F1 than GPT-5.2 at about 1% of the cost, reducing source hallucination from 32.66% to zero, across 38 disciplines in PaSaMaster-Bench.

**Why it made the cut.** design-changing · selected by score · strongest on C1 baseline recall ceiling (3/3). Directly measures the gap between an agentic literature-retrieval system and a single-query search baseline, exactly the anchor decision 1 needs.

**Why it matters here.** Gives a quantified comparison against a real search baseline (Google Scholar), directly anchoring decision 1, and attributes gains to iterative self-evolving retrieval — evidence for decision 2.

**Method.** Recursive self-evolving agent combining iterative intent refinement, evidence-grounded ranking over verified papers, and planning/retrieval separation using frontier vs lightweight models, evaluated on a new 38-discipline benchmark.

**Limitations.**

- PaSaMaster-Bench construction (labeling, contamination controls) not detailed in the abstract
- Google Scholar is a black-box commercial baseline rather than a controlled BM25/embedding baseline

<sub>selected: score · criteria: C1 3/3 · C2 2/3 · C3 2/3 · C4 1/3 · C5 0/3 · flags: methods_paper · verified 2026-08-26 via openalex, arxiv</sub>

## 7. Deep Research: A Survey of Autonomous Research Agents

Wenlin Zhang, Xiaopeng Li, Yingyi Zhang, Pengyue Jia et al. · 2025 · arXiv.org · other · overall 3/3

<https://doi.org/10.48550/arxiv.2508.12752>

**Key finding.** A systematic survey decomposes 'deep research' agents into four stages -- planning, question developing, web exploration, and report generation -- and catalogs optimization techniques and benchmarks for each.

**Why it made the cut.** plan-influencing · selected by score · strongest on C2 agentic mechanism gain (2/3). The most direct synthesis of the exact system-design/benchmark space the brief is scanning, useful as an orienting map even though it is not itself new evidence.

**Why it matters here.** Gives the project a structural map of where agentic mechanisms (reformulation, retrieval, synthesis) sit in the pipeline and which benchmarks exist per stage, directly shaping how the scan's four decision questions should be organized and cross-checked.

**Method.** Narrative survey/taxonomy of agentic deep-research systems, covering technical challenges, methods, and benchmarks per pipeline stage.

**Limitations.**

- narrative overview, not a systematic-protocol review
- abstract does not quantify which techniques carry the largest gains or where they fail to replicate

<sub>selected: score · criteria: C1 1/3 · C2 2/3 · C3 2/3 · C4 2/3 · C5 1/3 · flags: review · verified 2026-08-26 via openalex, arxiv</sub>

## 8. CG-RAG: Research Question Answering by Citation Graph Retrieval-Augmented LLMs

Yuntong Hu, Zhihan Lei, Zhongjie Dai, Allen Zhang et al. · 2025 · Annual International ACM SIGIR Conference on Research and Development in Information Retrieval · experimental · overall 3/3

<https://doi.org/10.1145/3726302.3729920>

**Key finding.** CG-RAG, which integrates sparse and dense retrieval signals within a citation-graph structure (LeSeGR), significantly outperforms RAG methods paired with state-of-the-art retrievers on research question-answering benchmarks.

**Why it made the cut.** design-changing · selected by score · strongest on C2 agentic mechanism gain (3/3). Directly evaluates citation-graph traversal combined with hybrid retrieval as the mechanism carrying gains in scientific literature QA.

**Why it matters here.** Provides a concrete, isolable mechanism (citation-graph-aware hybrid retrieval) for the graph-traversal component the brief asks agentic designs to justify, with a comparison against non-graph RAG baselines.

**Method.** Graph-structured hybrid retrieval framework combining lexical and semantic signals over citation graphs, evaluated across multiple domains against RAG baselines.

**Limitations.**

- abstract does not report absolute recall numbers, only relative improvement claims
- citation graph construction and coverage details not specified in abstract

<sub>selected: score · criteria: C1 1/3 · C2 3/3 · C3 3/3 · C4 1/3 · C5 0/3 · flags: methods_paper · verified 2026-08-26 via crossref, openalex</sub>

## 9. Projecting BrowseComp-Plus onto ClimbMix: Toward More Realistic Corpora for Agentic Search

Sahel Sharifymoghaddam, Lin Gu, Yijun Ge, Jimmy Lin · 2026 · no venue · experimental · overall 3/3

<https://arxiv.org/abs/2608.20317>

**Key finding.** Relocating BrowseComp-Plus's evidence into an independently built 553M-document corpus (ClimbMix) collapses evidence recall from 84.3% to 21.4% and costs five points of answer accuracy while the agent issues 63% more search calls, even though the questions themselves are unchanged.

**Why it made the cut.** contradicting · selected by backfill · strongest on C4 benchmark construction (3/3). A direct demonstration that a widely used agentic-search benchmark's construction inflated reported gains, exactly the replication-failure evidence the brief prioritizes.

**Why it matters here.** The clearest direct evidence for Q4: it shows that a benchmark's own per-query-curated corpus construction was inflating measured retrieval performance, and that the same questions become far harder once evidence is relocated to an independently built corpus not assembled around the benchmark's queries.

**Method.** A dataset-agnostic projection pipeline that decomposes questions into atomic reasoning hops and re-grounds each hop in a new corpus, verified by automatic checks, an independent agent, and human review; applied to 830 BrowseComp-Plus questions to yield 57 fully grounded questions.

**Limitations.**

- Yields only 57 fully grounded questions from 830, a small verified subset
- single benchmark (BrowseComp-Plus) and single replacement corpus (ClimbMix) tested
- projection pipeline itself relies on LLM-based verification steps

<sub>selected: backfill · criteria: C1 1/3 · C2 0/3 · C3 0/3 · C4 3/3 · C5 3/3 · flags: contradicts, methods_paper · verified 2026-08-26 via arxiv, s2</sub>

## 10. PaSa: An LLM Agent for Comprehensive Academic Paper Search

Yichen He, Guanhua Huang, Peiyuan Feng, Yuan Lin et al. · 2025 · Annual Meeting of the Association for Computational Linguistics · experimental · overall 3/3

<https://doi.org/10.48550/arxiv.2501.10120>

**Key finding.** PaSa-7B, trained via RL on a synthetic 35k-query dataset, surpasses the best Google-based baseline by 37.78% in recall@20 and 39.90% in recall@50 on RealScholarQuery.

**Why it made the cut.** design-changing · selected by backfill · strongest on C4 benchmark construction (3/3). Archetypal agentic academic-search system reporting large recall gains over single-query baselines with an explicit benchmark construction description.

**Why it matters here.** A canonical example of the exact system class the brief studies, with paired synthetic-training and real-world benchmarks that quantify the baseline gap and the benchmark construction the brief's Q3 asks about.

**Method.** RL-trained LLM agent that invokes search tools, reads papers, and selects references; trained on synthetic AutoScholarQuery and evaluated on a held-out real-world RealScholarQuery benchmark against Google, Google Scholar, and GPT-based baselines.

**Limitations.**

- Trained on synthetic queries which may not transfer perfectly to arbitrary real queries
- gains measured against Google-based baselines rather than a controlled fixed corpus

<sub>selected: backfill · criteria: C1 2/3 · C2 1/3 · C3 1/3 · C4 3/3 · C5 0/3 · flags: methods_paper · verified 2026-08-26 via openalex, arxiv</sub>

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
- [LLM-guided Hierarchical Search for End-to-end Reasoning Intensive Retrieval](https://arxiv.org/abs/2510.13217) (2025) — overall 3/3
- [Patience is all you need! An agentic system for performing scientific literature review](https://doi.org/10.48550/arxiv.2504.08752) (2025) — overall 3/3
- [Search-Time Data Contamination](https://doi.org/10.48550/arxiv.2508.13180) (2025) — overall 3/3
- [Open-Source Agentic Hybrid RAG Framework for Scientific Literature Review](https://doi.org/10.48550/arxiv.2508.05660) (2025) — overall 3/3
