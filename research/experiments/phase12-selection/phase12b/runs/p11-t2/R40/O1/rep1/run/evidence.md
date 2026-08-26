# Evidence scan — p11-t2

Run `/Users/nabergoj/Projects/research-scan/research/experiments/phase12-selection/phase12b/runs/p11-t2/R40/O1/rep1/run` · brief `/Users/nabergoj/Projects/research-scan/research/experiments/phase12-selection/phase12b/runs/p11-t2/R40/O1/rep1/run/brief.md` · rendered 2026-08-26

| # | Paper | Year | Venue | Evidence | Verified |
|---|---|---|---|---|---|
| 1 | [Diagnosing Search Behavior and Failure Modes in Long-Horizon Search Agents](https://doi.org/10.48550/arxiv.2608.01913) · 10.48550/arxiv.2608.01913 | 2026 | arXiv | experimental | yes |
| 2 | [LitSearch: A Retrieval Benchmark for Scientific Literature Search](https://doi.org/10.48550/arxiv.2407.18940) · 10.48550/arxiv.2407.18940 | 2024 | Conference on Empirical Methods in Natural Language Processing | experimental | yes |
| 3 | [BrowseComp-Plus: A More Fair and Transparent Evaluation Benchmark of Deep-Research Agent](https://doi.org/10.48550/arxiv.2508.06600) · 10.48550/arxiv.2508.06600 | 2025 | arXiv (Cornell University) | experimental | yes |
| 4 | [Deep Research Agents: A Systematic Examination And Roadmap](https://doi.org/10.48550/arxiv.2506.18096) · 10.48550/arxiv.2506.18096 | 2025 | arXiv.org | other | yes |
| 5 | [Projecting BrowseComp-Plus onto ClimbMix: Toward More Realistic Corpora for Agentic Search](https://arxiv.org/abs/2608.20317) | 2026 | — | experimental | yes |
| 6 | [OpenScholar: Synthesizing Scientific Literature with Retrieval-augmented LMs](https://doi.org/10.48550/arxiv.2411.14199) · 10.48550/arxiv.2411.14199 | 2024 | arXiv.org | experimental | yes |
| 7 | [Towards Recursive Self-Evolving Agentic Literature Retrieval](https://doi.org/10.48550/arxiv.2605.14306) · 10.48550/arxiv.2605.14306 | 2026 | arXiv | experimental | yes |
| 8 | [Structurally-bounded Agentic Graph Exploration for Evidence-Grounded Scholarly DeepSearch](https://doi.org/10.48550/arxiv.2608.24809) · 10.48550/arxiv.2608.24809 | 2026 | arXiv | experimental | yes |
| 9 | [PaSa: An LLM Agent for Comprehensive Academic Paper Search](https://doi.org/10.48550/arxiv.2501.10120) · 10.48550/arxiv.2501.10120 | 2025 | Annual Meeting of the Association for Computational Linguistics | experimental | yes |
| 10 | [LLM-guided Hierarchical Search for End-to-end Reasoning Intensive Retrieval](https://arxiv.org/abs/2510.13217) | 2025 | — | experimental | yes |

## 1. Diagnosing Search Behavior and Failure Modes in Long-Horizon Search Agents

Qi Liu, Jiaxin Mao, Fengbin Zhu, Tat-Seng Chua · 2026 · arXiv · experimental · overall 3/3

<https://doi.org/10.48550/arxiv.2608.01913>

**Key finding.** Across six agents on BrowseComp-Plus and BrowseComp, answer accuracy correlates more with cumulative retrieval recall than with the number of searches, and the best agents issue far fewer redundant queries.

**Why it made the cut.** design-changing · selected by score · strongest on C2 agentic mechanism gain (3/3). Empirically decomposes where agentic search gains and losses come from, directly targeting the brief's second and fourth questions.

**Why it matters here.** Directly answers the brief's second question: search effort itself does not carry the gain, evidence quality and stopping discipline do — reformulation helps but redundant re-querying does not, which should reshape what 'agentic gain' is measured against.

**Method.** Trajectory-level diagnosis using human-annotated document relevance judgments, holding retriever and harness fixed across six agents on BrowseComp-Plus, validated on BrowseComp with an open-web API.

**Limitations.**

- Only six agents studied
- retrieval model held fixed so findings may not generalize across retrievers

<sub>selected: score · criteria: C1 2/3 · C2 3/3 · C3 1/3 · C4 2/3 · C5 3/3 · flags: contradicts · verified 2026-08-26 via openalex, arxiv</sub>

## 2. LitSearch: A Retrieval Benchmark for Scientific Literature Search

Anirudh Ajith, Mengzhou Xia, Alexis Chevalier, Tanya Goyal et al. · 2024 · Conference on Empirical Methods in Natural Language Processing · experimental · overall 3/3

<https://doi.org/10.48550/arxiv.2407.18940>

**Key finding.** LitSearch's 597 realistic literature-search queries reveal a 24.8% absolute recall@5 gap between BM25 and state-of-the-art dense retrievers, with LLM-based reranking adding a further 4.4%, while commercial search engines lag the best dense retriever by 32 points.

**Why it made the cut.** foundational · selected by score · strongest on C1 baseline recall ceiling (3/3). The clearest, most directly on-topic benchmark quantifying the BM25-vs-dense recall ceiling and detailing its own construction methodology — foundational evidence for the brief's first and third decision questions.

**Why it matters here.** Directly answers the brief's first decision question with numbers: single-query BM25 search is far below the recall ceiling of dense retrieval on real literature-search queries, giving a concrete anchor against which any agentic system's reported improvement must be measured, and its query-construction/expert-review method is a template for benchmark-construction quality.

**Method.** Benchmark constructed from GPT-4-generated questions on inline-citation paragraphs plus author-written questions about recent papers, all manually reviewed; extensively benchmarks retrieval and LLM-reranking pipelines.

**Limitations.**

- restricted to recent ML/NLP papers, not the full breadth of scientific literature
- queries are GPT-4-generated or author-written, which may not fully represent naturalistic researcher search behavior

<sub>selected: score · criteria: C1 3/3 · C2 1/3 · C3 3/3 · C4 3/3 · C5 1/3 · verified 2026-08-26 via openalex, arxiv</sub>

## 3. BrowseComp-Plus: A More Fair and Transparent Evaluation Benchmark of Deep-Research Agent

Zijian Chen, Xueguang Ma, Shengyao Zhuang, Ping Nie et al. · 2025 · arXiv (Cornell University) · experimental · overall 3/3

<https://doi.org/10.48550/arxiv.2508.06600>

**Key finding.** On BrowseComp-Plus's fixed, human-verified corpus, Search-R1 with BM25 retrieval reaches only 3.86% accuracy, GPT-5 alone reaches 55.9%, and GPT-5 with a Qwen3-Embedding retriever reaches 70.1%.

**Why it made the cut.** foundational · selected by score · strongest on C1 baseline recall ceiling (3/3). The controlled benchmark against which multiple other shortlisted papers evaluate, providing the explicit baseline recall/accuracy numbers the brief's first question asks for.

**Why it matters here.** Gives an explicit, quantified single-query retriever baseline (BM25 at 3.86%) to anchor claimed agentic gains against, and shows retriever choice alone accounts for a large share of reported system-level improvement — central to the brief's first and second questions.

**Method.** Introduces a fixed, curated corpus derived from BrowseComp with human-verified supporting documents and mined hard negatives, enabling controlled, retriever-disentangled evaluation of deep-research agents.

**Limitations.**

- Corpus curated specifically around benchmark queries, which a follow-up projection study shows may inflate measured recall
- focused on open-domain QA-style deep research rather than literature search specifically

<sub>selected: score · criteria: C1 3/3 · C2 1/3 · C3 2/3 · C4 3/3 · C5 1/3 · flags: methods_paper · verified 2026-08-26 via openalex, arxiv</sub>

## 4. Deep Research Agents: A Systematic Examination And Roadmap

Yuxuan Huang, Yihang Chen, Haozhen Zhang, Kang Li et al. · 2025 · arXiv.org · other · overall 3/3

<https://doi.org/10.48550/arxiv.2506.18096>

**Key finding.** A systematic taxonomy of Deep Research agent architectures and information-acquisition strategies that also identifies key benchmark limitations — restricted external-knowledge access, sequential execution inefficiencies, and misalignment between evaluation metrics and DR agents' practical objectives.

**Why it made the cut.** foundational · selected by score · strongest on C4 benchmark construction (3/3). The orienting review that frames the whole space of agentic literature/deep-research systems and their evaluation problems.

**Why it matters here.** Provides the field-level map against which specific papers in this scan should be read, and explicitly names the benchmark-construction problems (metric misalignment, restricted knowledge access) the brief's third and fourth questions are asking about.

**Method.** abstract-only — narrative/taxonomic review of DR agent architectures, tool-use frameworks, and existing benchmarks, with a maintained repository of related work.

**Limitations.**

- Narrative synthesis rather than a systematic-review protocol or quantitative meta-analysis
- does not itself report new empirical measurements of recall or gain

<sub>selected: score · criteria: C1 1/3 · C2 2/3 · C3 1/3 · C4 3/3 · C5 2/3 · flags: review · verified 2026-08-26 via arxiv</sub>

## 5. Projecting BrowseComp-Plus onto ClimbMix: Toward More Realistic Corpora for Agentic Search

Sahel Sharifymoghaddam, Lin Gu, Yijun Ge, Jimmy Lin · 2026 · no venue · experimental · overall 3/3

<https://arxiv.org/abs/2608.20317>

**Key finding.** Relocating BrowseComp-Plus's evidence into the much larger, benchmark-agnostic ClimbMix corpus drops the strongest agent's evidence recall from 84.3% to 21.4% and answer accuracy by five points, while search calls rise 63%.

**Why it made the cut.** contradicting · selected by score · strongest on C4 benchmark construction (3/3). The clearest demonstration in this shortlist that a reported agentic gain does not survive a change in benchmark corpus construction, exactly the failure mode the brief is looking hardest for.

**Why it matters here.** Direct evidence for the brief's fourth question: a benchmark whose corpus was assembled per-query (evidence and negatives both selected relative to the questions) substantially inflates measured agentic performance, and the gain shrinks sharply once evaluated on an uncurated corpus.

**Method.** Projection pipeline decomposes each BrowseComp-Plus question into atomic reasoning hops, grounds each hop in ClimbMix (400B tokens, 553M documents), and retains only questions verified by automatic checks, an independent agent, and human review; yields 57 fully grounded questions.

**Limitations.**

- Only 57 questions survive the grounding pipeline, a small evaluation set
- single agent evaluated in the reported comparison

<sub>selected: score · criteria: C1 1/3 · C2 1/3 · C3 1/3 · C4 3/3 · C5 3/3 · flags: contradicts, methods_paper · verified 2026-08-26 via arxiv, s2</sub>

## 6. OpenScholar: Synthesizing Scientific Literature with Retrieval-augmented LMs

Akari Asai, Jacqueline He, Rulin Shao, Weijia Shi et al. · 2024 · arXiv.org · experimental · overall 3/3

<https://doi.org/10.48550/arxiv.2411.14199>

**Key finding.** OpenScholar, retrieving from 45 million open-access papers with a self-feedback inference loop, outperforms GPT-4o by 5% and PaperQA2 by 7% in correctness on the new ScholarQABench benchmark (2,967 expert queries), while GPT-4o hallucinates citations 78-90% of the time versus OpenScholar's expert-level citation accuracy.

**Why it made the cut.** design-changing · selected by score · strongest on C3 retrieval/reranking method (3/3). A central, in-domain system-and-benchmark paper for scientific literature synthesis with detailed benchmark construction and quantified system-vs-baseline gains.

**Why it matters here.** Directly in the brief's setting: gives a detailed, expert-labeled benchmark-construction example and quantified numbers showing where a retrieval-augmented literature-synthesis system beats and falls short of general-purpose LLMs, informing both the benchmark-construction and gain-attribution decision questions.

**Method.** Specialized retrieval-augmented LM plus purpose-built multi-domain benchmark (ScholarQABench) with expert-written queries and long-form answers; human-evaluation preference study included.

**Limitations.**

- gains attributed to the overall system (datastore + retriever + self-feedback loop) rather than decomposed into individual agentic moves
- correctness and citation-accuracy metrics may not generalize beyond the four domains studied

<sub>selected: score · criteria: C1 2/3 · C2 1/3 · C3 3/3 · C4 3/3 · C5 0/3 · flags: methods_paper · verified 2026-08-26 via openalex, arxiv</sub>

## 7. Towards Recursive Self-Evolving Agentic Literature Retrieval

Yuwen Du, Tian Jin, Jing Kang, Xianghe Pang et al. · 2026 · arXiv · experimental · overall 3/3

<https://doi.org/10.48550/arxiv.2605.14306>

**Key finding.** PaSaMaster achieves a 16.5x higher F1-score than Google Scholar and 37.8% higher F1 than GPT-5.2 at about 1% of the cost across 38 disciplines in PaSaMaster-Bench, while cutting source hallucination from 32.66% to zero.

**Why it made the cut.** design-changing · selected by score · strongest on C1 baseline recall ceiling (3/3). The clearest quantified baseline-vs-agent comparison for scientific literature retrieval found in the shortlist, directly answering Q1 and Q2.

**Why it matters here.** Directly anchors the recall-ceiling comparison the brief asks for (Q1) by benchmarking against Google Scholar as a single-query-style baseline, and attributes the gain to a specific mechanism (self-evolving intent refinement), giving a concrete number the project's own claimed improvements should be measured against.

**Method.** Recursive self-evolving agentic retrieval system with planning/retrieval separation, evaluated against Google Scholar and GPT-5.2 baselines on PaSaMaster-Bench.

**Limitations.**

- PaSaMaster-Bench construction (query source, relevance labeling) is not detailed in the abstract
- comparison baseline is Google Scholar's UI search, not a controlled single-query embedding/BM25 baseline
- no ablation isolating the self-evolving mechanism from the verification and cost-efficiency components

<sub>selected: score · criteria: C1 3/3 · C2 2/3 · C3 2/3 · C4 1/3 · C5 0/3 · flags: methods_paper · verified 2026-08-26 via openalex, arxiv</sub>

## 8. Structurally-bounded Agentic Graph Exploration for Evidence-Grounded Scholarly DeepSearch

Rima Hazra, Sayan Layek, Somnath Banerjee, Soumen Chakrabarti et al. · 2026 · arXiv · experimental · overall 3/3

<https://doi.org/10.48550/arxiv.2608.24809>

**Key finding.** Crase, using a single seed search plus 1.5-hop citation-graph expansion and entailment pruning, outperforms proprietary deep-research agents by up to 3x recall@50 on LitSearch at roughly a third of the cost.

**Why it made the cut.** design-changing · selected by score · strongest on C2 agentic mechanism gain (3/3). Directly demonstrates which agentic move (bounded citation-graph traversal) carries the reported gain, and at what cost.

**Why it matters here.** Isolates citation-graph traversal as the specific mechanism carrying the gain over open-ended agentic search loops, directly answering the brief's second question with an ablated, inspectable design.

**Method.** Bounded pipeline: one search-engine query for seed papers, citation-neighborhood expansion, entailment-based pruning, and recency-aware random-walk ranking; evaluated on a 500K-paper arXiv corpus across LitSearch and one further benchmark.

**Limitations.**

- Compared against proprietary deep-research agents rather than a plain single-query baseline explicitly
- benchmark construction not detailed in the abstract

<sub>selected: score · criteria: C1 1/3 · C2 3/3 · C3 3/3 · C4 1/3 · C5 0/3 · flags: methods_paper · verified 2026-08-26 via arxiv</sub>

## 9. PaSa: An LLM Agent for Comprehensive Academic Paper Search

Yichen He, Guanhua Huang, Peiyuan Feng, Yuan Lin et al. · 2025 · Annual Meeting of the Association for Computational Linguistics · experimental · overall 3/3

<https://doi.org/10.48550/arxiv.2501.10120>

**Key finding.** PaSa-7B beats the best Google-based baseline (Google+GPT-4o paraphrasing) by 37.78% in recall@20 and 39.90% in recall@50 on RealScholarQuery.

**Why it made the cut.** foundational · selected by backfill · strongest on C1 baseline recall ceiling (2/3). A foundational agentic paper-search system reporting a large, quantified gain over single-query search baselines.

**Why it matters here.** Anchors the magnitude of agentic gain over single-query database/search-engine baselines with concrete recall numbers, and shows reference-following contributes to comprehensive retrieval — central evidence for the brief's first two questions.

**Method.** RL-trained LLM agent that issues search queries, reads papers, and follows references; trained on synthetic AutoScholarQuery (35k queries) and evaluated on real-world RealScholarQuery.

**Limitations.**

- Trained on synthetic data which may not transfer perfectly to RealScholarQuery's real-world distribution
- gains not decomposed by individual agentic move (search vs reading vs reference-following)

<sub>selected: backfill · criteria: C1 2/3 · C2 1/3 · C3 2/3 · C4 2/3 · C5 0/3 · verified 2026-08-26 via openalex, arxiv</sub>

## 10. LLM-guided Hierarchical Search for End-to-end Reasoning Intensive Retrieval

Nilesh Gupta, Wei-Cheng Chang, N. Bui, Cho-Jui Hsieh et al. · 2025 · no venue · experimental · overall 3/3

<https://arxiv.org/abs/2510.13217>

**Key finding.** LATTICE, an LLM-guided hierarchical search index built without any embedding model in the retrieval loop, achieves 46.7 nDCG@10 on BRIGHT, matching the best fine-tuned ensemble baseline, and 49.1 with a lightweight ensemble.

**Why it made the cut.** design-changing · selected by backfill · strongest on C3 retrieval/reranking method (3/3). A retrieval-architecture paper directly relevant to the brief's third question, quantifying where embedding-based single-query retrieval and agentic query rewriting both fail on reasoning-intensive queries.

**Why it matters here.** Shows the standard embedding-retriever-plus-LLM-verifier pipeline caps recall on reasoning-intensive queries even after query rewriting or agentic loops, motivating retrieval architectures that could replace the embedding-search baseline this brief needs anchored.

**Method.** abstract-only — top-down LLM-guided construction of a hierarchical index over multi-level document summaries, with calibrated path-aggregated LLM traversal; evaluated on BRIGHT plus NQ, SciFact, SciDocs.

**Limitations.**

- Not evaluated on a scientific-literature-search-specific benchmark beyond SciFact/SciDocs
- traversal cost/latency tradeoff only partially characterized against reranking at low budgets

<sub>selected: backfill · criteria: C1 2/3 · C2 1/3 · C3 3/3 · C4 0/3 · C5 1/3 · flags: methods_paper · verified 2026-08-26 via arxiv, s2</sub>

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

- [Multi-Agent System for Scientific Literature Search and Recommendation](https://doi.org/10.1109/icssas66150.2025.11081082) (2025) — overall 3/3
- [Patience is all you need! An agentic system for performing scientific literature review](https://doi.org/10.48550/arxiv.2504.08752) (2025) — overall 3/3
- [CG-RAG: Research Question Answering by Citation Graph Retrieval-Augmented LLMs](https://doi.org/10.1145/3726302.3729920) (2025) — overall 3/3
- [Search-Time Contamination in Deep Research Agents: Measuring Performance Inflation in Public Benchmark Evaluation](https://doi.org/10.48550/arxiv.2606.05241) (2026) — overall 3/3
- [AI's Capability in Assisting Scientific Research in Physics, Astrophysics, and Cosmology I: Literature Review](https://doi.org/10.48550/arxiv.2607.25672) (2026) — overall 3/3
