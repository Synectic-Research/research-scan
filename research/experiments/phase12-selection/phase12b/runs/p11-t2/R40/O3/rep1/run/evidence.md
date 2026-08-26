# Evidence scan — p11-t2

Run `/Users/nabergoj/Projects/research-scan/research/experiments/phase12-selection/phase12b/runs/p11-t2/R40/O3/rep1/run` · brief `/Users/nabergoj/Projects/research-scan/research/experiments/phase12-selection/phase12b/runs/p11-t2/R40/O3/rep1/run/brief.md` · rendered 2026-08-26

| # | Paper | Year | Venue | Evidence | Verified |
|---|---|---|---|---|---|
| 1 | [BrowseComp-Plus: A More Fair and Transparent Evaluation Benchmark of Deep-Research Agent](https://doi.org/10.48550/arxiv.2508.06600) · 10.48550/arxiv.2508.06600 | 2025 | arXiv (Cornell University) | experimental | yes |
| 2 | [Towards Recursive Self-Evolving Agentic Literature Retrieval](https://doi.org/10.48550/arxiv.2605.14306) · 10.48550/arxiv.2605.14306 | 2026 | arXiv | experimental | yes |
| 3 | [Deep Research Agents: A Systematic Examination And Roadmap](https://doi.org/10.48550/arxiv.2506.18096) · 10.48550/arxiv.2506.18096 | 2025 | arXiv.org | other | yes |
| 4 | [Projecting BrowseComp-Plus onto ClimbMix: Toward More Realistic Corpora for Agentic Search](https://arxiv.org/abs/2608.20317) | 2026 | — | experimental | yes |
| 5 | [LLM-guided Hierarchical Search for End-to-end Reasoning Intensive Retrieval](https://arxiv.org/abs/2510.13217) | 2025 | — | experimental | yes |
| 6 | [LitSearch: A Retrieval Benchmark for Scientific Literature Search](https://doi.org/10.48550/arxiv.2407.18940) · 10.48550/arxiv.2407.18940 | 2024 | Conference on Empirical Methods in Natural Language Processing | experimental | yes |
| 7 | [Diagnosing Search Behavior and Failure Modes in Long-Horizon Search Agents](https://doi.org/10.48550/arxiv.2608.01913) · 10.48550/arxiv.2608.01913 | 2026 | arXiv | observational | yes |
| 8 | [Patience is all you need! An agentic system for performing scientific literature review](https://doi.org/10.48550/arxiv.2504.08752) · 10.48550/arxiv.2504.08752 | 2025 | arXiv.org | experimental | yes |
| 9 | [PaSa: An LLM Agent for Comprehensive Academic Paper Search](https://doi.org/10.48550/arxiv.2501.10120) · 10.48550/arxiv.2501.10120 | 2025 | Annual Meeting of the Association for Computational Linguistics | experimental | yes |
| 10 | [OpenScholar: Synthesizing Scientific Literature with Retrieval-augmented LMs](https://doi.org/10.48550/arxiv.2411.14199) · 10.48550/arxiv.2411.14199 | 2024 | arXiv.org | experimental | yes |

## 1. BrowseComp-Plus: A More Fair and Transparent Evaluation Benchmark of Deep-Research Agent

Zijian Chen, Xueguang Ma, Shengyao Zhuang, Ping Nie et al. · 2025 · arXiv (Cornell University) · experimental · overall 3/3

<https://doi.org/10.48550/arxiv.2508.06600>

**Key finding.** On BrowseComp-Plus's fixed, human-verified corpus, Search-R1 with BM25 achieves only 3.86% accuracy while GPT-5 reaches 55.9%, and pairing GPT-5 with a stronger embedding retriever (Qwen3-Embedding-8B) raises accuracy to 70.1% with fewer search calls.

**Why it made the cut.** plan-influencing · selected by score · strongest on C1 baseline recall ceiling (3/3). Its benchmark-construction method directly transfers to building rigorous literature-search benchmarks, and its findings undercut naive attribution of 'deep research' gains to agentic reasoning.

**Why it matters here.** Its fixed-corpus, human-verified-relevance, mined-hard-negative construction method directly transfers to building contamination-controlled, retriever-disentangled literature-search benchmarks (decision 3), and its results show reported 'deep research' gains partly reduce to retriever choice, bearing on decision 4.

**Method.** Benchmark derived from BrowseComp using a fixed curated corpus with human-verified supporting documents and mined hard negatives, enabling controlled, disentangled comparison of retriever and LLM contributions across deep-research systems.

**Limitations.**

- Derived from BrowseComp's general knowledge-seeking queries, not scientific-literature queries
- Does not test citation-graph traversal or literature-specific relevance judgments

<sub>selected: score · criteria: C1 3/3 · C2 1/3 · C3 3/3 · C4 3/3 · C5 2/3 · flags: contradicts, methods_paper · verified 2026-08-26 via openalex, arxiv</sub>

## 2. Towards Recursive Self-Evolving Agentic Literature Retrieval

Yuwen Du, Tian Jin, Jing Kang, Xianghe Pang et al. · 2026 · arXiv · experimental · overall 3/3

<https://doi.org/10.48550/arxiv.2605.14306>

**Key finding.** PaSaMaster achieves a 16.5x higher F1-score than Google Scholar and 37.8% higher F1 than GPT-5.2 at about 1% of the cost across 38 disciplines, reducing source hallucination from 32.66% to zero.

**Why it made the cut.** design-changing · selected by score · strongest on C1 baseline recall ceiling (3/3). The clearest quantified case of an agentic mechanism reportedly beating a single-query search baseline, exactly the claim decisions 1/2 need scrutinized.

**Why it matters here.** Directly answers decisions 1 and 2 together: quantifies gain over a real single-query search baseline (Google Scholar) and attributes it to a specific mechanism (self-evolving intent refinement plus verified-source ranking), a concrete design pattern to scrutinize.

**Method.** Recursive self-evolving agentic retrieval system that iteratively refines search intent from ranked evidence, ranks only verified papers, and separates planning (frontier LLM) from retrieval/scoring (lightweight models); evaluated on PaSaMaster-Bench across 38 disciplines.

**Limitations.**

- Benchmark (PaSaMaster-Bench) built by the same team proposing the system, raising conflict-of-interest concerns
- No independent replication reported

<sub>selected: score · criteria: C1 3/3 · C2 3/3 · C3 3/3 · C4 2/3 · C5 0/3 · flags: methods_paper · verified 2026-08-26 via openalex, arxiv</sub>

## 3. Deep Research Agents: A Systematic Examination And Roadmap

Yuxuan Huang, Yihang Chen, Haozhen Zhang, Kang Li et al. · 2025 · arXiv.org · other · overall 3/3

<https://doi.org/10.48550/arxiv.2506.18096>

**Key finding.** Proposes a taxonomy of Deep Research agent architectures (static/dynamic workflows, single/multi-agent) and identifies benchmark limitations including restricted external-knowledge access, sequential execution inefficiencies, and misalignment between evaluation metrics and DR objectives.

**Why it made the cut.** plan-influencing · selected by score · strongest on C4 benchmark construction (3/3). A critical survey of Deep Research agent designs and benchmarks directly informing benchmark-construction judgment (Q3) and taxonomizing the agentic mechanisms in play (Q2).

**Why it matters here.** Names the specific benchmark-construction failure modes (metric/objective misalignment, restricted knowledge access) that determine whether reported agentic gains across systems are even comparable, directly shaping how we should read and construct evaluation sets.

**Method.** Narrative systematic review and taxonomy of Deep Research agent information-acquisition strategies, tool-use frameworks, and benchmarks. Abstract-only.

**Limitations.**

- Narrative review rather than a systematic-protocol review despite critical benchmark coverage
- abstract gives no quantitative findings of its own

<sub>selected: score · criteria: C1 1/3 · C2 2/3 · C3 2/3 · C4 3/3 · C5 2/3 · flags: review · verified 2026-08-26 via arxiv</sub>

## 4. Projecting BrowseComp-Plus onto ClimbMix: Toward More Realistic Corpora for Agentic Search

Sahel Sharifymoghaddam, Lin Gu, Yijun Ge, Jimmy Lin · 2026 · no venue · experimental · overall 3/3

<https://arxiv.org/abs/2608.20317>

**Key finding.** Relocating BrowseComp-Plus's evidence into an independently-built 553M-document corpus (ClimbMix) drops the strongest agent's evidence recall from 84.3% to 21.4% (and answer accuracy by five points) while it issues 63% more search calls, retaining only 57 of the original 830 questions as fully grounded.

**Why it made the cut.** contradicting · selected by score · strongest on C4 benchmark construction (3/3). Directly demonstrates a reported agentic-search gain shrinking dramatically once benchmark corpus construction is decontaminated of query-specific selection — the strongest available evidence for Q4.

**Why it matters here.** Shows precisely how per-query-selected corpora inflate measured agentic-search performance — a benchmark-construction artifact (Q3) that directly explains where reported agentic gains fail to replicate (Q4) once distractors and evidence are not curated per query.

**Method.** A dataset-agnostic projection pipeline decomposes benchmark questions into atomic reasoning hops and re-grounds each hop in a corpus not built around the benchmark's own queries, verified by automated and human review.

**Limitations.**

- Yields only 57 grounded questions from the original 830, a small evaluation slice
- focused on general web-browsing agents (BrowseComp), not literature-search agents specifically, though the pipeline is explicitly stated to generalize to any decomposable benchmark

<sub>selected: score · criteria: C1 2/3 · C2 1/3 · C3 1/3 · C4 3/3 · C5 3/3 · flags: contradicts, methods_paper · verified 2026-08-26 via arxiv, s2</sub>

## 5. LLM-guided Hierarchical Search for End-to-end Reasoning Intensive Retrieval

Nilesh Gupta, Wei-Cheng Chang, N. Bui, Cho-Jui Hsieh et al. · 2025 · no venue · experimental · overall 3/3

<https://arxiv.org/abs/2510.13217>

**Key finding.** LATTICE achieves 46.7 nDCG@10 on BRIGHT with a single off-the-shelf LLM (matching the best fine-tuned ensemble baseline), and LATTICE++ reaches 49.1 nDCG@10; reranking wins at low token budgets but LATTICE converges to a higher asymptote at moderate budgets.

**Why it made the cut.** design-changing · selected by score · strongest on C2 agentic mechanism gain (3/3). Proposes and rigorously benchmarks a retrieval/reranking alternative directly relevant to the retrieval methods underlying agentic literature search (C3), with an explicit baseline-failure argument (C1).

**Why it matters here.** Directly challenges the standard 'cheap embedding retriever + LLM verifier' recipe by showing embedding models often fail to place the right documents in top-k, and offers a retrieval backbone with no embedding model in the loop — a real alternative to weigh against reranking-based designs.

**Method.** LLM-guided top-down construction of a hierarchically navigable search index from multi-level document summaries, plus calibrated path-aggregated LLM traversal; evaluated on BRIGHT, NQ, SciFact, SciDocs.

**Limitations.**

- Reasoning-intensive IR benchmarks only partly overlap with scholarly citation-search tasks
- single-LLM budget comparison against reranking may not generalize across models

<sub>selected: score · criteria: C1 2/3 · C2 3/3 · C3 3/3 · C4 1/3 · C5 1/3 · flags: methods_paper · verified 2026-08-26 via arxiv, s2</sub>

## 6. LitSearch: A Retrieval Benchmark for Scientific Literature Search

Anirudh Ajith, Mengzhou Xia, Alexis Chevalier, Tanya Goyal et al. · 2024 · Conference on Empirical Methods in Natural Language Processing · experimental · overall 3/3

<https://doi.org/10.48550/arxiv.2407.18940>

**Key finding.** LitSearch finds a 24.8-point absolute recall@5 gap between BM25 and state-of-the-art dense retrievers on 597 realistic literature-search queries; LLM-based reranking adds a further 4.4% improvement, and commercial search engines lag the best dense retriever by 32 points.

**Why it made the cut.** foundational · selected by score · strongest on C1 baseline recall ceiling (3/3). The core retrieval-benchmark result decisions 1 and 3 need: an expertly constructed literature-search benchmark quantifying the sparse/dense/rerank gap.

**Why it matters here.** Directly sets the single-query recall ceiling (decision 1) with hard numbers and shows which component (dense embedding, then reranking) contributes gains — the anchor baseline agentic-system claims in this space should be measured against.

**Method.** 597 literature-search queries built from GPT-4-generated questions over inline-citation paragraphs plus author-written questions about their own recent papers, all expert-verified; benchmarks retrieval and reranking models against them.

**Limitations.**

- Restricted to recent ML/NLP papers, not broader scientific literature
- Queries partly LLM-generated, which could bias question style

<sub>selected: score · criteria: C1 3/3 · C2 0/3 · C3 3/3 · C4 3/3 · C5 1/3 · flags: methods_paper · verified 2026-08-26 via openalex, arxiv</sub>

## 7. Diagnosing Search Behavior and Failure Modes in Long-Horizon Search Agents

Qi Liu, Jiaxin Mao, Fengbin Zhu, Tat-Seng Chua · 2026 · arXiv · observational · overall 3/3

<https://doi.org/10.48550/arxiv.2608.01913>

**Key finding.** Across six agents on BrowseComp-Plus (validated on BrowseComp), search effort and answer quality are only weakly aligned; accuracy correlates more strongly with cumulative retrieval recall than with number of searches or context consumed, and the best-performing agents issue far fewer redundant queries.

**Why it made the cut.** contradicting · selected by score · strongest on C5 gain replication failure (3/3). A trajectory-level diagnostic study directly answering which agentic moves carry the gain and where iterative search stops paying off, central to Q2 and Q4.

**Why it matters here.** Undercuts the premise that more iterative crawling drives agentic gains — shows evidence quality and disciplined query reformulation do the work, not search volume, which should redirect what we optimize and measure rather than assuming iteration itself helps.

**Method.** Trajectory-level diagnosis using human-annotated document relevance judgments, decomposing agent failures into retrieval gaps versus utilization gaps, with retrieval model and evaluation harness held fixed across six long-horizon search agents.

**Limitations.**

- Retrieval model and harness held fixed, so findings may not transfer to agents using different retrievers
- focused on open-web BrowseComp-style tasks rather than scholarly-corpus search specifically

<sub>selected: score · criteria: C1 1/3 · C2 2/3 · C3 1/3 · C4 2/3 · C5 3/3 · flags: contradicts · verified 2026-08-26 via openalex, arxiv</sub>

## 8. Patience is all you need! An agentic system for performing scientific literature review

David W. Brett, Anniek Myatt · 2025 · arXiv.org · experimental · overall 3/3

<https://doi.org/10.48550/arxiv.2504.08752>

**Key finding.** Keyword-based (sparse) retrieval achieves results close to state-of-the-art dense retrieval for literature-review question answering, without dense-retrieval infrastructure overhead, and coverage of relevant documents can be increased further.

**Why it made the cut.** design-changing · selected by score · strongest on C1 baseline recall ceiling (3/3). Directly measures the sparse vs. dense single-query retrieval ceiling the brief's decision 1 asks about, in the exact scientific-literature setting.

**Why it matters here.** Directly answers the recall-ceiling question for decision 1: sparse single-query search can match dense retrieval in this setting, so claimed agentic gains must be benchmarked against a strong sparse baseline rather than an assumed-weak one.

**Method.** LLM-based literature search-and-distillation system evaluated on biology-related questions from existing literature QA benchmarks, comparing sparse vs. dense retrieval and document-coverage strategies. Abstract-only for exact numbers.

**Limitations.**

- Evaluated only on biology-domain benchmark questions
- Abstract gives no absolute recall numbers
- System report rather than controlled ablation study

<sub>selected: score · criteria: C1 3/3 · C2 1/3 · C3 3/3 · C4 1/3 · C5 1/3 · flags: methods_paper · verified 2026-08-26 via openalex, arxiv</sub>

## 9. PaSa: An LLM Agent for Comprehensive Academic Paper Search

Yichen He, Guanhua Huang, Peiyuan Feng, Yuan Lin et al. · 2025 · Annual Meeting of the Association for Computational Linguistics · experimental · overall 3/3

<https://doi.org/10.48550/arxiv.2501.10120>

**Key finding.** PaSa-7B surpasses the best Google-based baseline (Google with GPT-4o) by 37.78% in recall@20 and 39.90% in recall@50 on the real-world RealScholarQuery benchmark, and exceeds PaSa-GPT-4o by 30.36% recall and 4.25% precision.

**Why it made the cut.** design-changing · selected by backfill · strongest on C1 baseline recall ceiling (3/3). A widely-cited, dedicated agentic academic paper-search system with quantified recall gains over database baselines and a purpose-built benchmark.

**Why it matters here.** Quantifies both the database-search recall ceiling (Google/Google Scholar) and the size of the agentic gain over it with a purpose-built real-world benchmark — the clearest single data point for Q1 and Q2, though it does not decompose which agentic action drives the improvement.

**Method.** RL-trained autonomous academic paper search agent invoking search tools, reading papers, and selecting references; trained on the synthetic AutoScholarQuery dataset (35k queries) and evaluated on RealScholarQuery against search-engine and LLM baselines.

**Limitations.**

- End-to-end RL training conflates the contribution of search, reading, and reference-selection actions
- benchmark queries sourced from top-tier AI conference papers may not generalize across scientific fields

<sub>selected: backfill · criteria: C1 3/3 · C2 1/3 · C3 1/3 · C4 3/3 · C5 0/3 · flags: methods_paper · verified 2026-08-26 via openalex, arxiv</sub>

## 10. OpenScholar: Synthesizing Scientific Literature with Retrieval-augmented LMs

Akari Asai, Jacqueline He, Rulin Shao, Weijia Shi et al. · 2024 · arXiv.org · experimental · overall 3/3

<https://doi.org/10.48550/arxiv.2411.14199>

**Key finding.** OpenScholar-8B, retrieving from 45M open-access papers, outperforms GPT-4o by 5% and PaperQA2 by 7% in correctness on the new ScholarQABench (2,967 expert queries), while GPT-4o hallucinates citations 78\u201390% of the time versus OpenScholar's expert-level citation accuracy; adding OpenScholar's datastore/retriever/feedback loop to GPT-4o improves its correctness by 12%.

**Why it made the cut.** design-changing · selected by backfill · strongest on C4 benchmark construction (3/3). One of the most directly relevant systems in scope — an agentic literature-search LM with its own purpose-built benchmark and quantified baseline comparisons.

**Why it matters here.** A directly on-topic, heavily cited system that both builds a literature-search-specific benchmark (Q3) and quantifies what retrieval-plus-feedback adds over a closed-book/API baseline (Q1, Q2), making it a central reference point for what agentic designs can realistically deliver.

**Method.** Retrieval-augmented LM with a dedicated scientific datastore, retriever, and self-feedback inference loop; evaluated on the newly built multi-domain ScholarQABench and via human preference studies (experts preferred OpenScholar 51\u201370% of the time vs. GPT-4o's 32%).

**Limitations.**

- Comparisons are against GPT-4o and PaperQA2 as whole systems, not against a decomposed single-query database-search ceiling
- no discussion of whether gains replicate on an independent benchmark

<sub>selected: backfill · criteria: C1 1/3 · C2 2/3 · C3 2/3 · C4 3/3 · C5 0/3 · flags: methods_paper · verified 2026-08-26 via openalex, arxiv</sub>

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
- [Multi-Agent System for Scientific Literature Search and Recommendation](https://doi.org/10.1109/icssas66150.2025.11081082) (2025) — overall 3/3
- [Multi-Turn Agentic Scientific Literature Search via Workflow Induction](https://doi.org/10.48550/arxiv.2607.00597) (2026) — overall 3/3
- [Search-Time Contamination in Deep Research Agents: Measuring Performance Inflation in Public Benchmark Evaluation](https://doi.org/10.48550/arxiv.2606.05241) (2026) — overall 3/3
- [Search-Time Data Contamination](https://doi.org/10.48550/arxiv.2508.13180) (2025) — overall 3/3
