# Evidence scan — p11-t2

Run `/Users/nabergoj/Projects/research-scan/research/experiments/phase12-selection/phase12b/runs/p11-t2/R20/O1/rep1/run` · brief `/Users/nabergoj/Projects/research-scan/research/experiments/phase12-selection/phase12b/runs/p11-t2/R20/O1/rep1/run/brief.md` · rendered 2026-08-26

| # | Paper | Year | Venue | Evidence | Verified |
|---|---|---|---|---|---|
| 1 | [BrowseComp-Plus: A More Fair and Transparent Evaluation Benchmark of Deep-Research Agent](https://doi.org/10.48550/arxiv.2508.06600) · 10.48550/arxiv.2508.06600 | 2025 | arXiv (Cornell University) | experimental | yes |
| 2 | [Diagnosing Search Behavior and Failure Modes in Long-Horizon Search Agents](https://doi.org/10.48550/arxiv.2608.01913) · 10.48550/arxiv.2608.01913 | 2026 | arXiv | experimental | yes |
| 3 | [Towards Recursive Self-Evolving Agentic Literature Retrieval](https://doi.org/10.48550/arxiv.2605.14306) · 10.48550/arxiv.2605.14306 | 2026 | arXiv | experimental | yes |
| 4 | [Deep Research Agents: A Systematic Examination And Roadmap](https://doi.org/10.48550/arxiv.2506.18096) · 10.48550/arxiv.2506.18096 | 2025 | arXiv.org | other | yes |
| 5 | [PaSa: An LLM Agent for Comprehensive Academic Paper Search](https://doi.org/10.48550/arxiv.2501.10120) · 10.48550/arxiv.2501.10120 | 2025 | Annual Meeting of the Association for Computational Linguistics | experimental | yes |
| 6 | [Structurally-bounded Agentic Graph Exploration for Evidence-Grounded Scholarly DeepSearch](https://doi.org/10.48550/arxiv.2608.24809) · 10.48550/arxiv.2608.24809 | 2026 | arXiv | experimental | yes |
| 7 | [LLM-guided Hierarchical Search for End-to-end Reasoning Intensive Retrieval](https://arxiv.org/abs/2510.13217) | 2025 | — | experimental | yes |
| 8 | [Projecting BrowseComp-Plus onto ClimbMix: Toward More Realistic Corpora for Agentic Search](https://arxiv.org/abs/2608.20317) | 2026 | — | experimental | yes |
| 9 | [Multi-Turn Agentic Scientific Literature Search via Workflow Induction](https://doi.org/10.48550/arxiv.2607.00597) · 10.48550/arxiv.2607.00597 | 2026 | arXiv | experimental | yes |
| 10 | [Language agents achieve superhuman synthesis of scientific knowledge](https://doi.org/10.48550/arxiv.2409.13740) · 10.48550/arxiv.2409.13740 | 2024 | arXiv (Cornell University) | experimental | yes |

## 1. BrowseComp-Plus: A More Fair and Transparent Evaluation Benchmark of Deep-Research Agent

Zijian Chen, Xueguang Ma, Shengyao Zhuang, Ping Nie et al. · 2025 · arXiv (Cornell University) · experimental · overall 3/3

<https://doi.org/10.48550/arxiv.2508.06600>

**Key finding.** On a fixed, human-verified corpus, Search-R1 with BM25 achieves only 3.86% accuracy while GPT-5 reaches 55.9%, and adding a dense retriever (Qwen3-Embedding-8B) pushes GPT-5 to 70.1% with fewer search calls.

**Why it made the cut.** foundational · selected by score · strongest on C1 baseline recall ceiling (3/3). The central controlled benchmark enabling fair comparison of database baselines against agentic deep-research systems, referenced by several other shortlisted papers.

**Why it matters here.** Supplies the exact baseline-vs-agentic-gain numbers question 1 and 2 need, and is the corpus multiple other shortlisted papers (diagnosis paper, ClimbMix projection) build directly on, making its construction choices load-bearing for the whole scan.

**Method.** Benchmark derived from BrowseComp with a fixed curated corpus, human-verified supporting documents, and mined hard negatives, enabling disentangled retriever-vs-agent evaluation.

**Limitations.**

- fixed corpus built from the benchmark's own queries plus mined negatives, which the ClimbMix projection paper shows inflates apparent retrieval difficulty realism
- single benchmark family (BrowseComp lineage)

<sub>selected: score · criteria: C1 3/3 · C2 2/3 · C3 2/3 · C4 3/3 · C5 2/3 · flags: methods_paper · verified 2026-08-26 via openalex, arxiv</sub>

## 2. Diagnosing Search Behavior and Failure Modes in Long-Horizon Search Agents

Qi Liu, Jiaxin Mao, Fengbin Zhu, Tat-Seng Chua · 2026 · arXiv · experimental · overall 3/3

<https://doi.org/10.48550/arxiv.2608.01913>

**Key finding.** Answer accuracy correlates with cumulative retrieval recall much more than with number of searches or context consumed, and the best agents issue far fewer redundant queries than weaker ones.

**Why it made the cut.** plan-influencing · selected by score · strongest on C2 agentic mechanism gain (3/3). Decomposes agentic search into retrieval-gap vs utilization-gap failures, exactly the mechanism-attribution question the brief prioritizes.

**Why it matters here.** Directly answers what agentic effort should be measured against: not search count but cumulative evidence recall, meaning our evaluation plan should track retrieval quality and stopping criteria rather than iteration counts as proxies for the gain.

**Method.** Trajectory-level diagnosis with human-annotated document-level relevance judgments across six agents on BrowseComp-Plus, validated on BrowseComp with an open-web search API.

**Limitations.**

- fixed retrieval model/harness across compared agents limits generalization to other retrievers
- diagnostic rather than causal (does not intervene to prove which fix works)

<sub>selected: score · criteria: C1 2/3 · C2 3/3 · C3 1/3 · C4 1/3 · C5 3/3 · flags: contradicts · verified 2026-08-26 via openalex, arxiv</sub>

## 3. Towards Recursive Self-Evolving Agentic Literature Retrieval

Yuwen Du, Tian Jin, Jing Kang, Xianghe Pang et al. · 2026 · arXiv · experimental · overall 3/3

<https://doi.org/10.48550/arxiv.2605.14306>

**Key finding.** PaSaMaster achieves a 16.5x higher F1-score than Google Scholar and a 37.8% higher F1-score than GPT-5.2 at about 1% of the cost across 38 disciplines, while reducing source hallucination from 32.66% to zero.

**Why it made the cut.** design-changing · selected by score · strongest on C1 baseline recall ceiling (3/3). Provides an explicit baseline-vs-agentic comparison plus mechanism attribution squarely on the brief's decisions 1 and 2.

**Why it matters here.** Directly quantifies the single-query search-engine ceiling (Google Scholar) against an agentic system and attributes the gain to named mechanisms (self-evolving intent refinement, planning/retrieval separation), giving concrete anchors for decisions 1 and 2.

**Method.** Recursive self-evolving retrieval architecture separating frontier-LLM intent understanding from lightweight-model retrieval/scoring, evaluated on PaSaMaster-Bench (38 disciplines) against Google Scholar and GPT-5.2 baselines.

**Limitations.**

- Baseline and benchmark (PaSaMaster-Bench) are the paper's own construction, inviting builder's-bias in labeling
- No independent replication reported
- Cost/efficiency claims not independently verified

<sub>selected: score · criteria: C1 3/3 · C2 3/3 · C3 2/3 · C4 2/3 · C5 0/3 · flags: methods_paper · verified 2026-08-26 via openalex, arxiv</sub>

## 4. Deep Research Agents: A Systematic Examination And Roadmap

Yuxuan Huang, Yihang Chen, Haozhen Zhang, Kang Li et al. · 2025 · arXiv.org · other · overall 3/3

<https://doi.org/10.48550/arxiv.2506.18096>

**Key finding.** Provides a taxonomy of Deep Research agent architectures (static vs dynamic workflows, single- vs multi-agent) and a critical evaluation identifying benchmark limitations including restricted external knowledge access and metric-objective misalignment.

**Why it made the cut.** foundational · selected by score · strongest on C4 benchmark construction (3/3). The synthesis/roadmap paper that ties together system design, benchmark critique, and open challenges across the exact space the brief scans.

**Why it matters here.** Synthesizes and names exactly the benchmark-construction weaknesses (restricted knowledge access, misaligned metrics) that question 3 and 4 ask us to scrutinize, giving a map of where the field's evaluation is weakest.

**Method.** Narrative systematic review and taxonomy synthesis of Deep Research agent literature, with an accompanying curated repository. Abstract-only for specific claims.

**Limitations.**

- narrative rather than systematic-protocol review
- abstract gives no quantitative findings, only qualitative taxonomy and critique

<sub>selected: score · criteria: C1 1/3 · C2 1/3 · C3 1/3 · C4 3/3 · C5 2/3 · flags: review · verified 2026-08-26 via arxiv</sub>

## 5. PaSa: An LLM Agent for Comprehensive Academic Paper Search

Yichen He, Guanhua Huang, Peiyuan Feng, Yuan Lin et al. · 2025 · Annual Meeting of the Association for Computational Linguistics · experimental · overall 3/3

<https://doi.org/10.48550/arxiv.2501.10120>

**Key finding.** PaSa-7B beats the best Google+GPT-4o baseline by 37.78% recall@20 and 39.90% recall@50 on RealScholarQuery, a real-world academic query benchmark.

**Why it made the cut.** foundational · selected by score · strongest on C1 baseline recall ceiling (3/3). One of the field's reference agentic paper-search systems, with an explicit baseline comparison and benchmark construction detail central to the brief.

**Why it matters here.** Anchors the single-query database baseline (Google, Google Scholar, GPT-4o-paraphrased search) that the whole scan's question 1 is measured against, and shows a concrete construction recipe for a scholarly-search benchmark.

**Method.** RL-trained autonomous paper-search agent; synthetic AutoScholarQuery (35k queries) for training, RealScholarQuery for evaluation.

**Limitations.**

- evaluated only against Google-family baselines, not BM25/dense retrievers directly
- trained mainly on synthetic data despite real-world test set

<sub>selected: score · criteria: C1 3/3 · C2 1/3 · C3 1/3 · C4 3/3 · C5 0/3 · flags: methods_paper · verified 2026-08-26 via openalex, arxiv</sub>

## 6. Structurally-bounded Agentic Graph Exploration for Evidence-Grounded Scholarly DeepSearch

Rima Hazra, Sayan Layek, Somnath Banerjee, Soumen Chakrabarti et al. · 2026 · arXiv · experimental · overall 3/3

<https://doi.org/10.48550/arxiv.2608.24809>

**Key finding.** A bounded 1.5-hop citation-graph expansion with entailment-based pruning and recency-aware ranking outperforms open-ended deep-research agents by up to 3x recall@50 at roughly a third of the cost.

**Why it made the cut.** design-changing · selected by score · strongest on C2 agentic mechanism gain (3/3). Directly isolates and quantifies the contribution of citation-graph traversal versus an undifferentiated agentic loop.

**Why it matters here.** Isolates citation-graph traversal as the specific mechanism carrying the gain over open-ended agentic search loops, directly answering question 2 with a bounded alternative design.

**Method.** Fixed-pipeline agent (seed search, citation-graph expansion, entailment pruning, random-walk ranking) evaluated on LitSearch and one further benchmark over a 500K-paper arXiv corpus.

**Limitations.**

- evaluated on only two benchmarks over a single arXiv corpus
- bounded 1.5-hop design may not generalize to queries needing deeper multi-hop traversal

<sub>selected: score · criteria: C1 1/3 · C2 3/3 · C3 2/3 · C4 1/3 · C5 1/3 · flags: methods_paper · verified 2026-08-26 via arxiv</sub>

## 7. LLM-guided Hierarchical Search for End-to-end Reasoning Intensive Retrieval

Nilesh Gupta, Wei-Cheng Chang, N. Bui, Cho-Jui Hsieh et al. · 2025 · no venue · experimental · overall 3/3

<https://arxiv.org/abs/2510.13217>

**Key finding.** LATTICE matches the best fine-tuned ensemble baseline on BRIGHT with 46.7 nDCG@10 using a single off-the-shelf LLM and no embedding model at search time, reaching 49.1 with a lightweight ensemble.

**Why it made the cut.** design-changing · selected by score · strongest on C1 baseline recall ceiling (3/3). Directly evidences where single embedding-based retrieval fails and proposes a retrieval/reranking alternative underlying agentic search.

**Why it matters here.** Empirically shows the standard embed-then-verify pipeline fails to surface relevant documents for reasoning-intensive queries, directly setting the recall ceiling question 1 asks about and offering a retrieval architecture that avoids the embedding bottleneck.

**Method.** LLM-guided hierarchical search index built top-down from multi-level document summaries, with calibrated path-aggregated traversal at query time; evaluated on BRIGHT, NQ, SciFact, SciDocs.

**Limitations.**

- index construction cost scales with corpus size and LLM calls, not quantified against BM25/dense baselines directly on scientific corpora
- SciFact/SciDocs results are secondary, not the main evaluation focus

<sub>selected: score · criteria: C1 3/3 · C2 1/3 · C3 3/3 · C4 0/3 · C5 1/3 · flags: methods_paper · verified 2026-08-26 via arxiv, s2</sub>

## 8. Projecting BrowseComp-Plus onto ClimbMix: Toward More Realistic Corpora for Agentic Search

Sahel Sharifymoghaddam, Lin Gu, Yijun Ge, Jimmy Lin · 2026 · no venue · experimental · overall 3/3

<https://arxiv.org/abs/2608.20317>

**Key finding.** Projecting BrowseComp-Plus questions onto a pretraining-scale corpus (ClimbMix) not built from the benchmark's own queries drops the strongest agent's evidence recall from 84.3% to 21.4% while accuracy falls five points and search calls rise 63%.

**Why it made the cut.** contradicting · selected by score · strongest on C4 benchmark construction (3/3). The clearest demonstration in the shortlist of a reported agentic/retrieval gain shrinking dramatically under a more realistic corpus, exactly the failure-to-replicate evidence the brief asks us to seek.

**Why it matters here.** Directly demonstrates question 4's concern: a benchmark's per-query-curated corpus inflates apparent retrieval performance, so gains measured on BrowseComp-Plus do not transfer to a more realistic, benchmark-independent corpus.

**Method.** Projection pipeline decomposing each question into atomic reasoning hops, grounding each hop in ClimbMix (400B-token, 553M-document corpus) with automatic, agent, and human verification; applied to 830 BrowseComp-Plus questions yielding 57 fully grounded ones.

**Limitations.**

- yields only 57 fully grounded questions from 830, a large reduction in evaluation set size
- single benchmark family projected onto a single alternative corpus so far

<sub>selected: score · criteria: C1 1/3 · C2 0/3 · C3 0/3 · C4 3/3 · C5 3/3 · flags: contradicts, methods_paper · verified 2026-08-26 via arxiv, s2</sub>

## 9. Multi-Turn Agentic Scientific Literature Search via Workflow Induction

Jisen Li, Bingxuan Li, Nanyi Jiang, Xuying Ning et al. · 2026 · arXiv · experimental · overall 3/3

<https://doi.org/10.48550/arxiv.2607.00597>

**Key finding.** PaperPilot-9B improves over the base Qwen3.5-9B toolset agent under multi-turn interaction, raising Hit@5 from 58.0 to 77.0, MRR from 47.5 to 59.4, and nDCG@10 from 26.8 to 32.5, while cutting workflow execution errors from 9.5% to 0%.

**Why it made the cut.** design-changing · selected by backfill · strongest on C2 agentic mechanism gain (3/3). Directly targets decision 2 (which agentic moves carry the gain) with an explicit, controllable workflow decomposition in the literature-search setting itself.

**Why it matters here.** Decomposes the agentic gain into named, editable operators (citation expansion, filtering, reranking, evidence extraction) inside an inspectable DAG, giving direct evidence for which specific moves carry the improvement rather than crediting the system as an undifferentiated whole.

**Method.** Trains a 9B-parameter agent via supervised workflow imitation and preference optimization over controlled workflow corruptions; evaluates multi-turn literature search against a base toolset agent.

**Limitations.**

- Compares to a base toolset agent rather than a plain single-query database search baseline
- No citation count / not yet peer reviewed
- Gains measured on the authors' own evaluation setup

<sub>selected: backfill · criteria: C1 1/3 · C2 3/3 · C3 2/3 · C4 0/3 · C5 0/3 · verified 2026-08-26 via openalex, arxiv</sub>

## 10. Language agents achieve superhuman synthesis of scientific knowledge

Michael Skarlinski, Sam Cox, Jon M. Laurent, James D. Braza et al. · 2024 · arXiv (Cornell University) · experimental · overall 3/3

<https://doi.org/10.48550/arxiv.2409.13740>

**Key finding.** PaperQA2 matches or exceeds subject-matter-expert performance on literature retrieval, summarization, and contradiction-detection tasks, identifying 2.34 ± 1.99 contradictions per paper with 70% validated by human experts.

**Why it made the cut.** foundational · selected by backfill · strongest on C4 benchmark construction (2/3). Foundational, highly-cited claim of agentic systems beating expert literature search that the current literature, including this scan's premise, responds to and tests.

**Why it matters here.** The widely-cited (152 citations) foundational claim of superhuman agentic literature search that much of the later work in this scan is measured against or pushes back on; anchors how strong the field believes the baseline 'agentic beats human/database' result to be.

**Method.** Human-AI comparison methodology on three literature-research tasks; introduces the LitQA2 benchmark used to guide PaperQA2's design; humans given full internet and tool access.

**Limitations.**

- No single-query database search recall ceiling reported for direct comparison
- LitQA2 benchmark was built to guide the same system's design, raising circularity concerns
- Human comparison group size and task scope not detailed in the abstract

<sub>selected: backfill · criteria: C1 1/3 · C2 1/3 · C3 1/3 · C4 2/3 · C5 0/3 · flags: methods_paper · verified 2026-08-26 via openalex, arxiv</sub>

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
- [When to use Graphs in RAG: A Comprehensive Analysis for Graph Retrieval-Augmented Generation](https://doi.org/10.48550/arxiv.2506.05690) (2025) — overall 2/3
- [Is Grep All You Need? How Agent Harnesses Reshape Agentic Search](https://doi.org/10.48550/arxiv.2605.15184) (2026) — overall 2/3
- [ReBOL: Retrieval via Bayesian Optimization with Batched LLM Relevance Observations and Query Reformulation](https://doi.org/10.48550/arxiv.2603.20513) (2026) — overall 2/3
- [HySemRAG: A Hybrid Semantic Retrieval-Augmented Generation Framework for Automated Literature Synthesis and Methodological Gap Analysis](https://doi.org/10.48550/arxiv.2508.05666) (2025) — overall 2/3
