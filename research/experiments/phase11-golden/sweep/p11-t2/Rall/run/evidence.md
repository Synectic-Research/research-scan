# Evidence scan — p11-t2

Run `/Users/nabergoj/Projects/research-scan/research/experiments/phase11-golden/sweep/p11-t2/Rall/run` · brief `/Users/nabergoj/Projects/research-scan/research/experiments/phase11-golden/sweep/p11-t2/Rall/run/brief.md` · rendered 2026-08-26

| # | Paper | Year | Venue | Evidence | Verified |
|---|---|---|---|---|---|
| 1 | [Diagnosing Search Behavior and Failure Modes in Long-Horizon Search Agents](https://doi.org/10.48550/arxiv.2608.01913) · 10.48550/arxiv.2608.01913 | 2026 | arXiv | observational | yes |
| 2 | [Total Recall QA: A Verifiable Evaluation Suite for Deep Research Agents](https://doi.org/10.1145/3805712.3808629) · 10.1145/3805712.3808629 | 2026 | — | experimental | yes |
| 3 | [BrowseComp-Plus: A More Fair and Transparent Evaluation Benchmark of Deep-Research Agent](https://doi.org/10.48550/arxiv.2508.06600) · 10.48550/arxiv.2508.06600 | 2025 | arXiv (Cornell University) | experimental | yes |
| 4 | [Projecting BrowseComp-Plus onto ClimbMix: Toward More Realistic Corpora for Agentic Search](https://arxiv.org/abs/2608.20317) | 2026 | — | experimental | yes |
| 5 | [Towards Recursive Self-Evolving Agentic Literature Retrieval](https://doi.org/10.48550/arxiv.2605.14306) · 10.48550/arxiv.2605.14306 | 2026 | arXiv | experimental | yes |
| 6 | [PaSa: An LLM Agent for Comprehensive Academic Paper Search](https://doi.org/10.48550/arxiv.2501.10120) · 10.48550/arxiv.2501.10120 | 2025 | Annual Meeting of the Association for Computational Linguistics | experimental | yes |
| 7 | [Structurally-bounded Agentic Graph Exploration for Evidence-Grounded Scholarly DeepSearch](https://doi.org/10.48550/arxiv.2608.24809) · 10.48550/arxiv.2608.24809 | 2026 | arXiv | experimental | yes |
| 8 | [ReBOL: Retrieval via Bayesian Optimization with Batched LLM Relevance Observations and Query Reformulation](https://doi.org/10.48550/arxiv.2603.20513) · 10.48550/arxiv.2603.20513 | 2026 | arXiv.org | experimental | yes |
| 9 | [WisPaper: Your AI Scholar Search Engine](https://doi.org/10.48550/arxiv.2512.06879) · 10.48550/arxiv.2512.06879 | 2025 | arXiv.org | experimental | yes |
| 10 | [Deep Research Agents: A Systematic Examination And Roadmap](https://doi.org/10.48550/arxiv.2506.18096) · 10.48550/arxiv.2506.18096 | 2025 | arXiv.org | other | yes |

## 1. Diagnosing Search Behavior and Failure Modes in Long-Horizon Search Agents

Qi Liu, Jiaxin Mao, Fengbin Zhu, Tat-Seng Chua · 2026 · arXiv · observational · overall 3/3

<https://doi.org/10.48550/arxiv.2608.01913>

**Key finding.** Across six agents on BrowseComp-Plus (validated on BrowseComp), search effort is only weakly aligned with answer quality; accuracy correlates better with cumulative retrieval recall than with number of searches, and the best agents issue far fewer redundant queries.

**Why it made the cut.** contradicting · selected by score · strongest on C2 agentic mechanism gain (3/3). Directly answers the brief's core questions on what agentic moves carry the gain and where reported search-effort gains fail to materialize.

**Why it matters here.** Directly undercuts the premise that more iterative searching or reformulation reliably drives agentic gains — shows that reported improvements often trace to retrieval-recall quality and stopping discipline, not raw search volume, which should recalibrate how we attribute and measure agentic gains.

**Method.** Trajectory-level diagnosis using human-annotated document-relevance judgments, decomposing failures into retrieval gaps vs. utilization gaps, retrieval model held fixed across six agents.

**Limitations.**

- restricted to two web-search benchmarks (BrowseComp/BrowseComp-Plus), not literature-specific corpora
- six agents studied, may not generalize to all architectures

<sub>selected: score · criteria: C1 2/3 · C2 3/3 · C3 1/3 · C4 2/3 · C5 3/3 · flags: contradicts · verified 2026-08-26 via openalex, arxiv</sub>

## 2. Total Recall QA: A Verifiable Evaluation Suite for Deep Research Agents

Mahta Rafiee, Heydar Soudani, Zahra Abbasiantaeb, Mohammad Aliannejadi et al. · 2026 · no venue · experimental · overall 3/3

<https://doi.org/10.1145/3805712.3808629>

**Key finding.** Introduces Total Recall QA (TRQA), a benchmark built from Wikidata-Wikipedia plus a synthetic contamination-resistant e-commerce corpus, establishing baseline retrieval and end-to-end results for deep research agents against a formal set of evaluation requirements.

**Why it made the cut.** plan-influencing · selected by score · strongest on C1 baseline recall ceiling (3/3). Provides the recall-ceiling baseline methodology and contamination-aware benchmark-construction framework the brief's Q1 and Q3 need.

**Why it matters here.** Directly targets Q1 (what a single-query recall ceiling looks like) and Q3 (rigorous benchmark construction with contamination control), giving a concrete comparison framework rather than an ad hoc one.

**Method.** Constructs single-answer, total-recall queries with relevance judgments from a structured KB paired with a text corpus, enabling large-scale, contamination-controlled benchmark construction; benchmarks representative retrievers and deep-research models. Abstract-only for numeric baselines.

**Limitations.**

- abstract omits actual recall numbers
- corpus is Wikidata/Wikipedia and synthetic e-commerce rather than scientific literature specifically

<sub>selected: score · criteria: C1 3/3 · C2 1/3 · C3 2/3 · C4 3/3 · C5 2/3 · flags: methods_paper · verified 2026-08-26 via crossref, openalex</sub>

## 3. BrowseComp-Plus: A More Fair and Transparent Evaluation Benchmark of Deep-Research Agent

Zijian Chen, Xueguang Ma, Shengyao Zhuang, Ping Nie et al. · 2025 · arXiv (Cornell University) · experimental · overall 3/3

<https://doi.org/10.48550/arxiv.2508.06600>

**Key finding.** On a fixed, human-verified corpus, BM25+Search-R1 achieves only 3.86% accuracy while GPT-5 reaches 55.9%, and swapping in a stronger embedding retriever lifts GPT-5 to 70.1% with fewer search calls.

**Why it made the cut.** foundational · selected by score · strongest on C1 baseline recall ceiling (3/3). Foundational benchmark establishing the baseline recall ceiling and enabling controlled attribution of agentic vs. retrieval gains, referenced by multiple other shortlisted papers.

**Why it matters here.** Gives a concrete, controlled measurement of the single-query/simple-retriever recall ceiling (BM25 at 3.86%) against which agentic and retriever improvements can be anchored — exactly the baseline the brief says everything else must be measured against.

**Method.** New benchmark derived from BrowseComp with a fixed curated corpus, human-verified supporting documents and mined hard negatives, enabling disentangled agent-vs-retriever evaluation.

**Limitations.**

- 100K-document corpus is still curated per-query rather than a naturalistic large corpus (addressed by later work)
- not literature-domain specific

<sub>selected: score · criteria: C1 3/3 · C2 1/3 · C3 2/3 · C4 3/3 · C5 1/3 · flags: methods_paper · verified 2026-08-26 via openalex, arxiv</sub>

## 4. Projecting BrowseComp-Plus onto ClimbMix: Toward More Realistic Corpora for Agentic Search

Sahel Sharifymoghaddam, Lin Gu, Yijun Ge, Jimmy Lin · 2026 · no venue · experimental · overall 3/3

<https://arxiv.org/abs/2608.20317>

**Key finding.** Relocating BrowseComp-Plus's evidence into a naturalistic, benchmark-agnostic corpus (ClimbMix) causes the strongest agent's evidence recall to fall from 84.3% to 21.4% and accuracy to drop five points, while issuing 63% more search calls, on 57 fully-grounded projected questions.

**Why it made the cut.** contradicting · selected by score · strongest on C4 benchmark construction (3/3). Directly shows a reported agentic performance level collapsing under a more realistic, less benchmark-tailored corpus — the strongest evidence of gain replication failure in the set.

**Why it matters here.** Is the clearest demonstration in the shortlist that a benchmark's construction (evidence and negatives selected per-query from a small curated corpus) inflates measured performance — exactly the gain-replication-failure evidence the brief says it must reach hardest for.

**Method.** A dataset-agnostic projection pipeline decomposing questions into atomic reasoning hops, grounding each hop in a new 553M-document corpus, verified by automatic checks, an independent agent, and human review.

**Limitations.**

- yields only 57 grounded questions out of 830, a small validated subset
- single benchmark family (BrowseComp-Plus) projected, generality to other benchmarks untested

<sub>selected: score · criteria: C1 1/3 · C2 1/3 · C3 1/3 · C4 3/3 · C5 3/3 · flags: contradicts, methods_paper · verified 2026-08-26 via arxiv, s2</sub>

## 5. Towards Recursive Self-Evolving Agentic Literature Retrieval

Yuwen Du, Tian Jin, Jing Kang, Xianghe Pang et al. · 2026 · arXiv · experimental · overall 3/3

<https://doi.org/10.48550/arxiv.2605.14306>

**Key finding.** PaSaMaster achieves a 16.5x higher F1-score than Google Scholar and 37.8% higher F1 than GPT-5.2 on PaSaMaster-Bench (38 disciplines) at about 1% of the cost, reducing source hallucination from 32.66% to zero.

**Why it made the cut.** design-changing · selected by score · strongest on C2 agentic mechanism gain (3/3). A current agentic literature-retrieval system reporting a large, mechanism-attributed gain over single-query search baselines, exactly the design space the brief is scanning.

**Why it matters here.** Gives a concrete, mechanism-attributed comparison of an agentic literature search design against single-query database search (Google Scholar), directly informing decisions 1 and 2, though it confirms rather than tests the brief's premise.

**Method.** Recursive self-evolving retrieval agent separating intent-understanding (frontier LLM) from retrieval/ranking (lightweight models), evaluated on a new 38-discipline benchmark.

**Limitations.**

- self-reported new benchmark, not yet independently validated
- does not decompose how much of the gain each component (self-evolving retrieval vs verified ranking) contributes

<sub>selected: score · criteria: C1 2/3 · C2 3/3 · C3 2/3 · C4 2/3 · C5 0/3 · flags: methods_paper · verified 2026-08-26 via openalex, arxiv</sub>

## 6. PaSa: An LLM Agent for Comprehensive Academic Paper Search

Yichen He, Guanhua Huang, Peiyuan Feng, Yuan Lin et al. · 2025 · Annual Meeting of the Association for Computational Linguistics · experimental · overall 3/3

<https://doi.org/10.48550/arxiv.2501.10120>

**Key finding.** PaSa-7B surpasses the best Google-based baseline by 37.78% in recall@20 and 39.90% in recall@50 on RealScholarQuery, and exceeds a GPT-4o-prompted version of itself by 30.36% recall and 4.25% precision.

**Why it made the cut.** foundational · selected by score · strongest on C1 baseline recall ceiling (3/3). The foundational agentic academic-search system with explicit recall gains over single-query database baselines, central to the brief's decision 1.

**Why it matters here.** Establishes the anchor recall comparison of an iterative agentic search-and-crawl design against single/paraphrased-query database search that decision 1 needs, and is the base system later work (e.g. PaSaMaster) explicitly builds on and must be checked against.

**Method.** RL-trained LLM agent that autonomously searches, reads papers, and selects references; trained on synthetic AutoScholarQuery (35k queries) and evaluated on a real-world RealScholarQuery benchmark.

**Limitations.**

- trained mainly on synthetic data, real-world benchmark comparatively small
- recall gains are not decomposed by individual agentic move (search vs read vs select)

<sub>selected: score · criteria: C1 3/3 · C2 2/3 · C3 1/3 · C4 3/3 · C5 0/3 · flags: methods_paper · verified 2026-08-26 via openalex, arxiv</sub>

## 7. Structurally-bounded Agentic Graph Exploration for Evidence-Grounded Scholarly DeepSearch

Rima Hazra, Sayan Layek, Somnath Banerjee, Soumen Chakrabarti et al. · 2026 · arXiv · experimental · overall 3/3

<https://doi.org/10.48550/arxiv.2608.24809>

**Key finding.** Crase's bounded 1.5-hop citation-graph expansion with entailment-based pruning and recency-aware random-walk ranking outperforms proprietary deep research agents by up to 3x recall@50 at roughly a third of the cost on LitSearch and a further benchmark over a 500K-paper arXiv corpus.

**Why it made the cut.** design-changing · selected by score · strongest on C2 agentic mechanism gain (3/3). A system design directly attributing measured recall gains to specific, bounded agentic moves (citation-graph traversal, pruning, ranking) in scholarly search, the exact question decision 2 asks.

**Why it matters here.** Isolates exactly which agentic move (bounded citation-graph traversal plus principled pruning and ranking) drives the recall gain over less-constrained agent search loops, directly answering decision 2 with numbers in a genuine literature-search setting.

**Method.** Single seed search, fixed 1.5-hop citation-neighborhood expansion, entailment-based edge pruning, and recency-aware random-walk ranking, evaluated against open-ended deep research agents on a 500K-paper arXiv corpus.

**Limitations.**

- evaluated on LitSearch and one further benchmark only
- compared against proprietary deep research agents rather than a plain single-query baseline

<sub>selected: score · criteria: C1 2/3 · C2 3/3 · C3 3/3 · C4 1/3 · C5 0/3 · flags: methods_paper · verified 2026-08-26 via arxiv</sub>

## 8. ReBOL: Retrieval via Bayesian Optimization with Batched LLM Relevance Observations and Query Reformulation

A. Korikov, Scott Sanner · 2026 · arXiv.org · experimental · overall 3/3

<https://doi.org/10.48550/arxiv.2603.20513>

**Key finding.** ReBOL uses LLM query reformulations to seed a Bayesian Optimization posterior over document relevance, iteratively acquiring and scoring batches to beat LLM reranker baselines, e.g. 46.5% vs 35.0% recall@100 on Robust04 at comparable latency.

**Why it made the cut.** design-changing · selected by backfill · strongest on C1 baseline recall ceiling (3/3). A concrete, quantified retrieval/reranking method combining reformulation with iterative scoring — directly germane to Q1, Q2 and Q3.

**Why it matters here.** Gives a numerically anchored account of how much gain comes from query reformulation plus iterative re-scoring versus vector-similarity retrieval alone, directly informing Q1 (baseline) and Q2 (mechanism) with a technique that plugs into the retrieval/reranking stage of any agentic literature-search pipeline.

**Method.** Multimodal Bayesian Optimization over batched LLM relevance observations initialized by query reformulation; evaluated on five BEIR datasets with two LLM backbones (Gemini-2.5-Flash-Lite, GPT-5.2).

**Limitations.**

- evaluated on general BEIR IR benchmarks rather than scientific-literature-specific corpora
- no ablation isolating reformulation's contribution from the BO acquisition loop

<sub>selected: backfill · criteria: C1 3/3 · C2 3/3 · C3 3/3 · C4 0/3 · C5 0/3 · flags: methods_paper · verified 2026-08-26 via openalex, arxiv</sub>

## 9. WisPaper: Your AI Scholar Search Engine

Li Ju, Jun Zhao, Mingxu Chai, Ziyu Shen et al. · 2025 · arXiv.org · experimental · overall 3/3

<https://doi.org/10.48550/arxiv.2512.06879>

**Key finding.** WisPaper's Deep Search module (WisModel) validates candidate papers against queries via structured reasoning, reaching 22.26% recall on TaxoBench versus 20.92% for an O3 baseline, with 93.70% validation accuracy against retrieval hallucinations.

**Why it made the cut.** design-changing · selected by backfill · strongest on C1 baseline recall ceiling (2/3). Directly reports agentic vs. baseline recall numbers in academic literature search, exactly the Q1 comparison the brief needs, with a margin small enough to bear on Q4.

**Why it matters here.** Gives a concrete numeric comparison (22.26% vs 20.92%, a ~1.3-point margin) between an agentic validation step and a strong baseline in scientific literature search — exactly the Q1 anchor and a modest-gain data point supporting the scan's Q4 skepticism.

**Method.** End-to-end academic-literature agent with integrated Scholar Search, Library, and AI Feeds modules; benchmarked on TaxoBench; abstract-only for further detail.

**Limitations.**

- gain over baseline is small (~1.3 points), raising questions about how much it would replicate elsewhere
- TaxoBench construction not detailed in the abstract
- vendor system description may understate limitations

<sub>selected: backfill · criteria: C1 2/3 · C2 2/3 · C3 2/3 · C4 1/3 · C5 2/3 · flags: contradicts, methods_paper · verified 2026-08-26 via openalex, arxiv</sub>

## 10. Deep Research Agents: A Systematic Examination And Roadmap

Yuxuan Huang, Yihang Chen, Haozhen Zhang, Kang Li et al. · 2025 · arXiv.org · other · overall 3/3

<https://doi.org/10.48550/arxiv.2506.18096>

**Key finding.** A systematic taxonomy of Deep Research agent architectures (API-based vs. browser-based retrieval, static vs. dynamic workflows, single- vs. multi-agent) alongside a critical review identifying current benchmarks' limitations: restricted external knowledge access, sequential-execution inefficiency, and metric misalignment.

**Why it made the cut.** foundational · selected by review · strongest on C4 benchmark construction (2/3). Serves as the field-orienting review connecting system design taxonomy to benchmark critique, directly useful for structuring the scan's synthesis.

**Why it matters here.** Provides the orienting taxonomy and explicit critique of benchmark shortcomings that the brief's third question (how are evaluation sets constructed, and what can their numbers support) needs as a map of the field before diving into individual results.

**Method.** Narrative/systematic survey of architectures and benchmarks with an accompanying curated repository; not a systematic-review-protocol paper.

**Limitations.**

- narrative synthesis rather than quantitative meta-analysis
- covers general deep-research agents, not literature-search-specific systems exclusively

<sub>selected: review · criteria: C1 1/3 · C2 1/3 · C3 1/3 · C4 2/3 · C5 1/3 · flags: review · verified 2026-08-26 via arxiv</sub>

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

- [AstaBench: Rigorous Benchmarking of AI Agents with a Scientific Research Suite](https://doi.org/10.48550/arxiv.2510.21652) (2025) — overall 3/3
- [LLM-guided Hierarchical Search for End-to-end Reasoning Intensive Retrieval](https://arxiv.org/abs/2510.13217) (2025) — overall 3/3
- [When Deep Research Agents Stagnate: Enhancing Reasoning with Retrieval-Aware Agent Control](https://doi.org/10.48550/arxiv.2608.15191) (2026) — overall 3/3
- [Multi-Turn Agentic Scientific Literature Search via Workflow Induction](https://doi.org/10.48550/arxiv.2607.00597) (2026) — overall 3/3
- [Search-Time Contamination in Deep Research Agents: Measuring Performance Inflation in Public Benchmark Evaluation](https://doi.org/10.48550/arxiv.2606.05241) (2026) — overall 3/3
