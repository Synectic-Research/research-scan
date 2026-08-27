# Evidence scan — p11-t2

Run `/Users/nabergoj/Projects/research-scan/research/experiments/phase14/runs/p11-t2/S/rep5/run` · brief `/Users/nabergoj/Projects/research-scan/research/experiments/phase14/runs/p11-t2/S/rep5/run/brief.md` · rendered 2026-08-27

| # | Paper | Year | Venue | Evidence | Verified |
|---|---|---|---|---|---|
| 1 | [Towards Recursive Self-Evolving Agentic Literature Retrieval](https://doi.org/10.48550/arxiv.2605.14306) · 10.48550/arxiv.2605.14306 | 2026 | arXiv | experimental | yes |
| 2 | [BRIGHT: A Realistic and Challenging Benchmark for Reasoning-Intensive Retrieval](https://doi.org/10.48550/arxiv.2407.12883) · 10.48550/arxiv.2407.12883 | 2024 | International Conference on Learning Representations | experimental | yes |
| 3 | [LitSearch: A Retrieval Benchmark for Scientific Literature Search](https://doi.org/10.48550/arxiv.2407.18940) · 10.48550/arxiv.2407.18940 | 2024 | Conference on Empirical Methods in Natural Language Processing | experimental | yes |
| 4 | [Diagnosing Search Behavior and Failure Modes in Long-Horizon Search Agents](https://doi.org/10.48550/arxiv.2608.01913) · 10.48550/arxiv.2608.01913 | 2026 | arXiv | experimental | yes |
| 5 | [BrowseComp-Plus: A More Fair and Transparent Evaluation Benchmark of Deep-Research Agent](https://doi.org/10.48550/arxiv.2508.06600) · 10.48550/arxiv.2508.06600 | 2025 | arXiv (Cornell University) | experimental | yes |
| 6 | [Projecting BrowseComp-Plus onto ClimbMix: Toward More Realistic Corpora for Agentic Search](https://arxiv.org/abs/2608.20317) | 2026 | — | computational | yes |
| 7 | [PaSa: An LLM Agent for Comprehensive Academic Paper Search](https://doi.org/10.48550/arxiv.2501.10120) · 10.48550/arxiv.2501.10120 | 2025 | Annual Meeting of the Association for Computational Linguistics | experimental | yes |
| 8 | [Structurally-bounded Agentic Graph Exploration for Evidence-Grounded Scholarly DeepSearch](https://doi.org/10.48550/arxiv.2608.24809) · 10.48550/arxiv.2608.24809 | 2026 | arXiv | experimental | yes |
| 9 | [Patience is all you need! An agentic system for performing scientific literature review](https://doi.org/10.48550/arxiv.2504.08752) · 10.48550/arxiv.2504.08752 | 2025 | arXiv.org | experimental | yes |
| 10 | [Deep Research Agents: A Systematic Examination And Roadmap](https://doi.org/10.48550/arxiv.2506.18096) · 10.48550/arxiv.2506.18096 | 2025 | arXiv.org | other | yes |

## 1. Towards Recursive Self-Evolving Agentic Literature Retrieval

Yuwen Du, Tian Jin, Jing Kang, Xianghe Pang et al. · 2026 · arXiv · experimental · overall 3/3

<https://doi.org/10.48550/arxiv.2605.14306>

**Key finding.** PaSaMaster achieves a 16.5x higher F1-score than Google Scholar and a 37.8% higher F1-score than GPT-5.2 at about 1% of the cost, reducing source hallucination from 32.66% to zero, across 38 disciplines in PaSaMaster-Bench.

**Why it made the cut.** design-changing · selected by score · strongest on C1 baseline recall ceiling (3/3). Gives an explicit, numeric single-query-search baseline comparison and attributes gain to a specific self-evolving retrieval mechanism — squarely answers the brief's first and second questions.

**Why it matters here.** Directly anchors the single-query database search baseline (Google Scholar) the brief needs, and quantifies how much a specific self-evolving retrieval mechanism adds on top, at a stated cost tradeoff.

**Method.** Recursive self-evolving agentic retrieval system separating intent understanding (frontier LLM) from retrieval/scoring (lightweight models); evaluated against Google Scholar and GPT-5.2 on a purpose-built 38-discipline benchmark.

**Limitations.**

- Benchmark (PaSaMaster-Bench) is newly introduced by the same authors, with limited construction detail in the abstract
- comparison partner (Google Scholar) is a product, not a controlled single-query retrieval baseline
- no independent replication reported

<sub>selected: score · criteria: C1 3/3 · C2 3/3 · C3 2/3 · C4 2/3 · C5 0/3 · flags: methods_paper · verified 2026-08-27 via openalex, arxiv</sub>

## 2. BRIGHT: A Realistic and Challenging Benchmark for Reasoning-Intensive Retrieval

Hongjin Su, Howard Yen, Mengzhou Xia, Weijia Shi et al. · 2024 · International Conference on Learning Representations · experimental · overall 3/3

<https://doi.org/10.48550/arxiv.2407.12883>

**Key finding.** State-of-the-art retrieval models perform far worse on reasoning-intensive queries than on standard benchmarks — the leading MTEB model scores 59.0 nDCG@10 generally but only 18.3 on BRIGHT — though explicit query reasoning recovers up to 12.2 points.

**Why it made the cut.** foundational · selected by score · strongest on C1 baseline recall ceiling (3/3). The most concrete, quantified baseline-ceiling result for single-query retrieval on hard queries in the batch, widely used as a reference in the agentic search literature this scan surveys.

**Why it matters here.** Establishes a concrete, widely-cited ceiling for single-query embedding search on reasoning-intensive retrieval (18.3 nDCG@10 vs. 59.0 on standard tasks) — precisely the recall-ceiling anchor the brief's first question needs, and shows reformulation-style reasoning partially recovers the gap.

**Method.** Introduces 1,384 real-world, reasoning-intensive queries across diverse domains (economics, psychology, math, coding), curated from naturally occurring human data, and evaluates state-of-the-art embedding/retrieval models.

**Limitations.**

- Domains are general (coding, math, economics), not scientific literature search specifically
- no citation-graph or iterative-crawling agent evaluated
- gap may differ for literature-specific corpora

<sub>selected: score · criteria: C1 3/3 · C2 1/3 · C3 2/3 · C4 3/3 · C5 1/3 · flags: methods_paper · verified 2026-08-27 via openalex, arxiv</sub>

## 3. LitSearch: A Retrieval Benchmark for Scientific Literature Search

Anirudh Ajith, Mengzhou Xia, Alexis Chevalier, Tanya Goyal et al. · 2024 · Conference on Empirical Methods in Natural Language Processing · experimental · overall 3/3

<https://doi.org/10.48550/arxiv.2407.18940>

**Key finding.** LitSearch, a 597-query literature-search retrieval benchmark, finds a 24.8-point recall@5 gap between BM25 and state-of-the-art dense retrievers, with LLM-based reranking adding a further 4.4% improvement, while commercial search engines like Google lag 32 points behind the best dense retriever.

**Why it made the cut.** foundational · selected by score · strongest on C1 baseline recall ceiling (3/3). The clearest, most quantified answer to the brief's first and third questions (baseline recall ceiling and benchmark construction) within the exact literature-search setting.

**Why it matters here.** Directly establishes the quantitative baseline recall ceiling (BM25 vs dense) and demonstrates a benchmark-construction methodology (GPT-4-generated plus author-written queries) — the single most load-bearing anchor for both the recall-ceiling and benchmark-construction questions in the brief.

**Method.** Benchmark of 597 realistic literature-search queries built from GPT-4-generated questions on cited paragraphs plus author-written questions about recent papers, expert-reviewed; extensive retrieval and LLM-reranking comparisons.

**Limitations.**

- Scoped to ML/NLP papers only, not broader scientific domains
- No agentic/iterative-crawling system evaluated, only static retrieval and reranking

<sub>selected: score · criteria: C1 3/3 · C2 0/3 · C3 3/3 · C4 3/3 · C5 1/3 · flags: methods_paper · verified 2026-08-27 via openalex, arxiv</sub>

## 4. Diagnosing Search Behavior and Failure Modes in Long-Horizon Search Agents

Qi Liu, Jiaxin Mao, Fengbin Zhu, Tat-Seng Chua · 2026 · arXiv · experimental · overall 3/3

<https://doi.org/10.48550/arxiv.2608.01913>

**Key finding.** Answer accuracy correlates more with cumulative retrieval recall than with number of searches or context consumed, and the best-performing agents issue far fewer redundant queries.

**Why it made the cut.** plan-influencing · selected by score · strongest on C2 agentic mechanism gain (3/3). Directly diagnoses where and why agentic search gains materialize or fail, the exact question the brief asks hardest for.

**Why it matters here.** Reframes what an 'agentic gain' should be measured against: not search effort or activity but cumulative retrieval recall and evidence utilization, which changes how our evaluation should attribute gains to specific mechanisms and when to stop searching.

**Method.** Trajectory-level diagnosis of six long-horizon search agents on BrowseComp-Plus and BrowseComp using human-annotated document-level relevance judgments to separate retrieval gaps from utilization gaps.

**Limitations.**

- Focused on general question-answering search agents rather than scholarly paper search specifically
- Findings depend on the fixed retrieval model/harness used across the six agents evaluated

<sub>selected: score · criteria: C1 1/3 · C2 3/3 · C3 1/3 · C4 2/3 · C5 2/3 · flags: contradicts · verified 2026-08-27 via openalex, arxiv</sub>

## 5. BrowseComp-Plus: A More Fair and Transparent Evaluation Benchmark of Deep-Research Agent

Zijian Chen, Xueguang Ma, Shengyao Zhuang, Ping Nie et al. · 2025 · arXiv (Cornell University) · experimental · overall 3/3

<https://doi.org/10.48550/arxiv.2508.06600>

**Key finding.** On a fixed, human-verified corpus, BM25-paired Search-R1 reaches only 3.86% accuracy while GPT-5 reaches 55.9%, and pairing GPT-5 with a Qwen3-Embedding-8B retriever raises accuracy to 70.1% with fewer search calls.

**Why it made the cut.** foundational · selected by score · strongest on C1 baseline recall ceiling (3/3). The controlled benchmark underlying baseline-versus-agent comparisons that several other papers in this set build on or challenge.

**Why it matters here.** Provides a controlled, reproducible baseline recall/accuracy ceiling for single-query retrieval (BM25) versus stronger retrievers and full agentic pipelines, the exact anchor the brief says every other reported gain must be measured against.

**Method.** Benchmark derived from BrowseComp with a fixed curated corpus, human-verified supporting documents and mined hard negatives, enabling controlled disentanglement of agent versus retriever contributions.

**Limitations.**

- Corpus and negatives were mined per-query from the benchmark's own supporting documents, which later work shows can inflate retrieval-difficulty estimates
- Web-QA style queries rather than scholarly literature search specifically

<sub>selected: score · criteria: C1 3/3 · C2 0/3 · C3 2/3 · C4 3/3 · C5 1/3 · flags: methods_paper · verified 2026-08-27 via openalex, arxiv</sub>

## 6. Projecting BrowseComp-Plus onto ClimbMix: Toward More Realistic Corpora for Agentic Search

Sahel Sharifymoghaddam, Lin Gu, Yijun Ge, Jimmy Lin · 2026 · no venue · computational · overall 3/3

<https://arxiv.org/abs/2608.20317>

**Key finding.** Relocating BrowseComp-Plus's evidence into a 553M-document corpus built without reference to the benchmark drops the strongest agent's evidence recall from 84.3% to 21.4% and answer accuracy by five points while requiring 63% more search calls.

**Why it made the cut.** contradicting · selected by score · strongest on C4 benchmark construction (3/3). The clearest demonstration in this set that a reported agentic-search gain shrinks dramatically when the benchmark's corpus-construction advantage is removed.

**Why it matters here.** Directly demonstrates that a benchmark's per-query-selected corpus inflates retrieval performance, and shows an agentic system's reported gain collapsing when the same questions are evaluated against a corpus not built around them -- the precise failure-to-replicate evidence the brief asks the scan to reach hardest for.

**Method.** A dataset-agnostic projection pipeline decomposes questions into atomic reasoning hops and re-grounds each hop in ClimbMix, retaining only questions verified by automatic checks, an independent agent, and human review; applied to 830 BrowseComp-Plus questions to yield 57 fully grounded questions.

**Limitations.**

- Yields only 57 fully grounded questions from 830, a small evaluation set
- Single benchmark projection (BrowseComp-Plus to ClimbMix), not yet generalized to other benchmarks

<sub>selected: score · criteria: C1 1/3 · C2 0/3 · C3 1/3 · C4 3/3 · C5 3/3 · flags: contradicts, methods_paper · verified 2026-08-27 via arxiv, s2</sub>

## 7. PaSa: An LLM Agent for Comprehensive Academic Paper Search

Yichen He, Guanhua Huang, Peiyuan Feng, Yuan Lin et al. · 2025 · Annual Meeting of the Association for Computational Linguistics · experimental · overall 3/3

<https://doi.org/10.48550/arxiv.2501.10120>

**Key finding.** PaSa-7B surpasses the best Google-based baseline by 37.78% in recall@20 and 39.90% in recall@50 on RealScholarQuery, and exceeds a prompted GPT-4o agent by 30.36% in recall.

**Why it made the cut.** foundational · selected by score · strongest on C1 baseline recall ceiling (3/3). Foundational scholarly-search agent paper reporting quantified recall gains over single-query search-engine baselines with an explicit benchmark construction.

**Why it matters here.** Establishes both the single-query search-engine baseline and a concrete, reproducible recall gain for an autonomous scholarly search agent, anchoring the recall-ceiling question the whole scan turns on.

**Method.** RL-trained LLM agent that invokes search tools, reads papers, and selects references, trained on synthetic AutoScholarQuery (35k queries) and evaluated on a newly built real-world benchmark, RealScholarQuery.

**Limitations.**

- Trained on synthetic queries though evaluated on a real benchmark
- Gain attributed to the system as a whole rather than to individual agentic moves

<sub>selected: score · criteria: C1 3/3 · C2 1/3 · C3 1/3 · C4 3/3 · C5 0/3 · flags: methods_paper · verified 2026-08-27 via openalex, arxiv</sub>

## 8. Structurally-bounded Agentic Graph Exploration for Evidence-Grounded Scholarly DeepSearch

Rima Hazra, Sayan Layek, Somnath Banerjee, Soumen Chakrabarti et al. · 2026 · arXiv · experimental · overall 3/3

<https://doi.org/10.48550/arxiv.2608.24809>

**Key finding.** A bounded pipeline of one seed search, 1.5-hop citation expansion, entailment-based pruning, and recency-aware random-walk ranking outperforms proprietary deep research agents by up to 3x recall@50 at roughly a third of the cost.

**Why it made the cut.** design-changing · selected by backfill · strongest on C2 agentic mechanism gain (3/3). Directly attributes a quantified retrieval gain to citation-graph traversal and pruning rather than to an undifferentiated agent system.

**Why it matters here.** Isolates citation-graph traversal as the specific mechanism carrying the gain over open-ended deep-research loops, exactly the attribution the brief's second question asks for, and suggests a cheaper, more inspectable design.

**Method.** Structurally-bounded agentic graph exploration (Crase) evaluated on LitSearch and one further benchmark over a 500K-paper arXiv corpus.

**Limitations.**

- Evaluated on a curated arXiv-only corpus of 500K papers, not the open web
- Comparison baselines are proprietary deep research agents rather than a plain single-query search baseline

<sub>selected: backfill · criteria: C1 1/3 · C2 3/3 · C3 3/3 · C4 1/3 · C5 0/3 · flags: methods_paper · verified 2026-08-27 via arxiv</sub>

## 9. Patience is all you need! An agentic system for performing scientific literature review

David W. Brett, Anniek Myatt · 2025 · arXiv.org · experimental · overall 3/3

<https://doi.org/10.48550/arxiv.2504.08752>

**Key finding.** Sparse (keyword-based) retrieval achieves results close to state-of-the-art dense retrieval for scientific literature search/distillation, and the system increases coverage of relevant documents for literature-review generation.

**Why it made the cut.** contradicting · selected by backfill · strongest on C3 retrieval/reranking method (3/3). Directly tests whether simple sparse retrieval matches more complex approaches for scientific literature review, informing the baseline-ceiling question.

**Why it matters here.** Suggests the simple sparse-retrieval baseline sits closer to the recall ceiling than assumed, weakening the case that dense retrieval or added agentic complexity is needed — directly bears on the baseline-ceiling question.

**Method.** LLM-based agentic system for literature search and distillation, evaluated on biology-related QA drawn from prior literature benchmarks; compares sparse vs dense retrieval. Abstract-only for specific numbers.

**Limitations.**

- Domain restricted to biology QA benchmarks
- No explicit precision/recall numbers reported in the abstract
- Unclear generalization to other scientific domains

<sub>selected: backfill · criteria: C1 2/3 · C2 2/3 · C3 3/3 · C4 1/3 · C5 0/3 · flags: contradicts, methods_paper · verified 2026-08-27 via openalex, arxiv</sub>

## 10. Deep Research Agents: A Systematic Examination And Roadmap

Yuxuan Huang, Yihang Chen, Haozhen Zhang, Kang Li et al. · 2025 · arXiv.org · other · overall 3/3

<https://doi.org/10.48550/arxiv.2506.18096>

**Key finding.** A systematic taxonomy of Deep Research agents by information-acquisition strategy (API-based vs browser-based), tool-use framework, and planning architecture, with a critical evaluation identifying restricted external-knowledge access, sequential execution inefficiencies, and metric-objective misalignment in current benchmarks.

**Why it made the cut.** closely-related · selected by review · strongest on C4 benchmark construction (3/3). The synthesis and benchmark critique needed to compare across the individually-scoped papers in this set.

**Why it matters here.** Gives the orientation the scan needs on how agentic literature/deep-research systems are built and evaluated, and explicitly names the benchmark-construction weaknesses the brief's third question asks the scan to surface.

**Method.** Narrative survey and taxonomy synthesis with a maintained repository of Deep Research agent research; abstract-only for specific findings.

**Limitations.**

- Narrative rather than systematic review protocol
- Abstract gives no quantitative findings
- Not specific to scholarly/scientific literature search

<sub>selected: review · criteria: C1 1/3 · C2 1/3 · C3 1/3 · C4 3/3 · C5 1/3 · flags: review · verified 2026-08-27 via arxiv</sub>

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

- [CG-RAG: Research Question Answering by Citation Graph Retrieval-Augmented LLMs](https://doi.org/10.1145/3726302.3729920) (2025) — overall 3/3
- [OpenScholar: Synthesizing Scientific Literature with Retrieval-augmented LMs](https://doi.org/10.48550/arxiv.2411.14199) (2024) — overall 3/3
- [From Inertia to Objectivity: Improving Deep Research Agents with Noise Isolation](https://doi.org/10.48550/arxiv.2608.23045) (2026) — overall 3/3
- [Multi-Turn Agentic Scientific Literature Search via Workflow Induction](https://doi.org/10.48550/arxiv.2607.00597) (2026) — overall 3/3
- [AI's Capability in Assisting Scientific Research in Physics, Astrophysics, and Cosmology I: Literature Review](https://doi.org/10.48550/arxiv.2607.25672) (2026) — overall 3/3
