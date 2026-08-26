# Evidence scan — p11-t2

Run `/Users/nabergoj/Projects/research-scan/research/experiments/phase12-selection/phase12b/runs/p11-t2/R15/O1/rep3/run` · brief `/Users/nabergoj/Projects/research-scan/research/experiments/phase12-selection/phase12b/runs/p11-t2/R15/O1/rep3/run/brief.md` · rendered 2026-08-26

| # | Paper | Year | Venue | Evidence | Verified |
|---|---|---|---|---|---|
| 1 | [Diagnosing Search Behavior and Failure Modes in Long-Horizon Search Agents](https://doi.org/10.48550/arxiv.2608.01913) · 10.48550/arxiv.2608.01913 | 2026 | arXiv | experimental | yes |
| 2 | [BrowseComp-Plus: A More Fair and Transparent Evaluation Benchmark of Deep-Research Agent](https://doi.org/10.48550/arxiv.2508.06600) · 10.48550/arxiv.2508.06600 | 2025 | arXiv (Cornell University) | experimental | yes |
| 3 | [LLM-guided Hierarchical Search for End-to-end Reasoning Intensive Retrieval](https://arxiv.org/abs/2510.13217) | 2025 | — | experimental | yes |
| 4 | [Deep Research Agents: A Systematic Examination And Roadmap](https://doi.org/10.48550/arxiv.2506.18096) · 10.48550/arxiv.2506.18096 | 2025 | arXiv.org | other | yes |
| 5 | [Projecting BrowseComp-Plus onto ClimbMix: Toward More Realistic Corpora for Agentic Search](https://arxiv.org/abs/2608.20317) | 2026 | — | experimental | yes |
| 6 | [PaSa: An LLM Agent for Comprehensive Academic Paper Search](https://doi.org/10.48550/arxiv.2501.10120) · 10.48550/arxiv.2501.10120 | 2025 | Annual Meeting of the Association for Computational Linguistics | experimental | yes |
| 7 | [Structurally-bounded Agentic Graph Exploration for Evidence-Grounded Scholarly DeepSearch](https://doi.org/10.48550/arxiv.2608.24809) · 10.48550/arxiv.2608.24809 | 2026 | arXiv | experimental | yes |
| 8 | [AI's Capability in Assisting Scientific Research in Physics, Astrophysics, and Cosmology I: Literature Review](https://doi.org/10.48550/arxiv.2607.25672) · 10.48550/arxiv.2607.25672 | 2026 | arXiv | experimental | yes |
| 9 | [Multi-Turn Agentic Scientific Literature Search via Workflow Induction](https://doi.org/10.48550/arxiv.2607.00597) · 10.48550/arxiv.2607.00597 | 2026 | arXiv | experimental | yes |
| 10 | [Do Cross-References Help LLM Agents Complete Documents? Search Cost, Robustness, and Unreachable Content on a Wiki-Style Corpus](https://mcp-data-platform.txn2.com/reference/benchmark-report-graph-completion/) | 2026 | Open MIND | experimental | yes |

## 1. Diagnosing Search Behavior and Failure Modes in Long-Horizon Search Agents

Qi Liu, Jiaxin Mao, Fengbin Zhu, Tat-Seng Chua · 2026 · arXiv · experimental · overall 3/3

<https://doi.org/10.48550/arxiv.2608.01913>

**Key finding.** Across six agents on BrowseComp-Plus and BrowseComp, answer accuracy correlates with cumulative retrieval recall far more than with number of searches or context consumed, and useful evidence typically appears early while agents keep issuing low-yield queries.

**Why it made the cut.** design-changing · selected by score · strongest on C1 baseline recall ceiling (3/3). Directly interrogates decision questions 1, 2 and 4 by decomposing where agentic search gains come from and where they stall.

**Why it matters here.** Directly answers what agentic search effort actually buys: it shows the premise that more search/reformulation reliably helps is often false, redirecting design attention to stopping criteria and evidence-selection rather than search volume.

**Method.** Trajectory-level diagnosis using human-annotated document-level relevance judgments, comparing six long-horizon search agents with retrieval model and evaluation harness held fixed, validated on two benchmarks.

**Limitations.**

- relies on existing benchmarks (BrowseComp-Plus/BrowseComp) rather than a new evaluation set
- diagnostic rather than a new retrieval method

<sub>selected: score · criteria: C1 3/3 · C2 3/3 · C3 1/3 · C4 2/3 · C5 3/3 · flags: contradicts · verified 2026-08-26 via openalex, arxiv</sub>

## 2. BrowseComp-Plus: A More Fair and Transparent Evaluation Benchmark of Deep-Research Agent

Zijian Chen, Xueguang Ma, Shengyao Zhuang, Ping Nie et al. · 2025 · arXiv (Cornell University) · experimental · overall 3/3

<https://doi.org/10.48550/arxiv.2508.06600>

**Key finding.** On a fixed, human-verified corpus, Search-R1 with BM25 achieves only 3.86% accuracy while GPT-5 reaches 55.9%, rising to 70.1% when paired with the Qwen3-Embedding-8B retriever, with fewer search calls.

**Why it made the cut.** foundational · selected by score · strongest on C1 baseline recall ceiling (3/3). The central benchmark-construction and baseline-recall paper the brief's decisions 1 and 3 are built around.

**Why it matters here.** Supplies the fixed-corpus, retriever-disentangled baseline recall/accuracy numbers (BM25 vs strong embeddings) that any claimed agentic gain in this literature must be measured against, and is the benchmark other shortlisted papers (e.g., the ClimbMix projection) build on directly.

**Method.** Benchmark derived from BrowseComp with a fixed curated corpus, human-verified supporting documents and mined hard negatives, enabling controlled, reproducible comparison of deep-research agents and retrievers.

**Limitations.**

- fixed corpus assembled from the benchmark's own queries and mined negatives, which later work shows may inflate measured gains
- focused on general deep-research QA rather than scholarly-paper discovery specifically

<sub>selected: score · criteria: C1 3/3 · C2 1/3 · C3 2/3 · C4 3/3 · C5 2/3 · flags: methods_paper · verified 2026-08-26 via openalex, arxiv</sub>

## 3. LLM-guided Hierarchical Search for End-to-end Reasoning Intensive Retrieval

Nilesh Gupta, Wei-Cheng Chang, N. Bui, Cho-Jui Hsieh et al. · 2025 · no venue · experimental · overall 3/3

<https://arxiv.org/abs/2510.13217>

**Key finding.** LATTICE, an LLM-guided hierarchical search index with no embedding model in the retrieval loop, matches the best fine-tuned ensemble at 46.7 nDCG@10 on BRIGHT and reaches 49.1 with a lightweight ensemble, while embedding-based top-k retrieval is shown to fail to place relevant documents even for SOTA embedders.

**Why it made the cut.** design-changing · selected by score · strongest on C1 baseline recall ceiling (3/3). A retrieval/reranking method contrasting embedding ceilings against LLM-guided graph-like navigation, directly under decisions 1 and 3.

**Why it matters here.** Directly quantifies where standard embedding-based single-query retrieval breaks down for reasoning-intensive queries, and proposes a corpus-navigation alternative to query reformulation/reranking pipelines — a genuine retrieval-layer design choice for agentic literature search.

**Method.** Top-down LLM-guided construction of a hierarchical document index from multi-level summaries, with calibrated path-aggregated LLM traversal, evaluated on BRIGHT plus NQ, SciFact, and SciDocs.

**Limitations.**

- primary benchmark (BRIGHT) is general reasoning-intensive retrieval, only partially scientific-literature (SciFact/SciDocs)
- reranking is shown to be competitive at low token budgets, tempering the case for hierarchical traversal in all settings

<sub>selected: score · criteria: C1 3/3 · C2 2/3 · C3 3/3 · C4 1/3 · C5 2/3 · flags: methods_paper · verified 2026-08-26 via arxiv, s2</sub>

## 4. Deep Research Agents: A Systematic Examination And Roadmap

Yuxuan Huang, Yihang Chen, Haozhen Zhang, Kang Li et al. · 2025 · arXiv.org · other · overall 3/3

<https://doi.org/10.48550/arxiv.2506.18096>

**Key finding.** Provides a taxonomy of Deep Research agent architectures (static/dynamic workflows, single/multi-agent) and a critical evaluation of current benchmarks, identifying restricted external-knowledge access, sequential execution inefficiencies, and metric-objective misalignment as key limitations.

**Why it made the cut.** closely-related · selected by score · strongest on C4 benchmark construction (3/3). A field-level synthesis flagging benchmark and evaluation weaknesses directly relevant to decisions 3 and 4.

**Why it matters here.** Synthesizes where the field's benchmarks and evaluation metrics fall short, giving a structured checklist against which the brief's own benchmark-construction question (decision 3) can be assessed.

**Method.** Narrative systematic review and taxonomy of Deep Research agent architectures, information-acquisition strategies, and evaluation benchmarks; abstract-only detail on methodology depth.

**Limitations.**

- narrative review, not a systematic-protocol review
- does not report new empirical measurements of recall or gains

<sub>selected: score · criteria: C1 2/3 · C2 1/3 · C3 1/3 · C4 3/3 · C5 2/3 · flags: review · verified 2026-08-26 via arxiv</sub>

## 5. Projecting BrowseComp-Plus onto ClimbMix: Toward More Realistic Corpora for Agentic Search

Sahel Sharifymoghaddam, Lin Gu, Yijun Ge, Jimmy Lin · 2026 · no venue · experimental · overall 3/3

<https://arxiv.org/abs/2608.20317>

**Key finding.** Relocating BrowseComp-Plus questions' evidence into a benchmark-agnostic corpus (ClimbMix) drops the strongest agent's evidence recall from 84.3% to 21.4% and costs five points of answer accuracy despite 63% more search calls.

**Why it made the cut.** contradicting · selected by score · strongest on C4 benchmark construction (3/3). The clearest demonstration in the shortlist that a reported agentic gain shrinks dramatically under a different, benchmark-independent corpus.

**Why it matters here.** Directly shows a leading benchmark's per-query-curated corpus inflates measured agentic performance, meaning gains reported on BrowseComp-Plus do not hold once the corpus is decoupled from the queries — exactly the decision-4 evidence the brief asks for.

**Method.** A projection pipeline decomposing questions into atomic reasoning hops, grounding each hop in a new 553M-document corpus (ClimbMix) with automatic, agent-based, and human verification, applied to 830 BrowseComp-Plus questions to yield 57 fully-grounded questions.

**Limitations.**

- yields only 57 fully grounded questions from 830, a small evaluation set
- single case study (one benchmark, one corpus projection) rather than a general result

<sub>selected: score · criteria: C1 2/3 · C2 0/3 · C3 0/3 · C4 3/3 · C5 3/3 · flags: contradicts, methods_paper · verified 2026-08-26 via arxiv, s2</sub>

## 6. PaSa: An LLM Agent for Comprehensive Academic Paper Search

Yichen He, Guanhua Huang, Peiyuan Feng, Yuan Lin et al. · 2025 · Annual Meeting of the Association for Computational Linguistics · experimental · overall 3/3

<https://doi.org/10.48550/arxiv.2501.10120>

**Key finding.** PaSa-7B exceeds the best Google+GPT-4o baseline by 37.78% in recall@20 and 39.90% in recall@50 on the real-world RealScholarQuery benchmark.

**Why it made the cut.** foundational · selected by score · strongest on C1 baseline recall ceiling (3/3). Establishes the baseline-vs-agent recall comparison (C1) and a widely-used benchmark construction (C4) central to the brief.

**Why it matters here.** One of the field's reference systems and benchmarks; its recall numbers versus plain search-engine baselines are the anchor other agentic-search papers measure themselves against.

**Method.** RL-trained LLM agent that invokes search, reads papers, and selects references; trained on synthetic AutoScholarQuery (35k queries) and evaluated on RealScholarQuery.

**Limitations.**

- gains attributed to the system as a whole rather than decomposed into specific mechanisms
- synthetic training data may not generalize to all query types

<sub>selected: score · criteria: C1 3/3 · C2 1/3 · C3 1/3 · C4 3/3 · C5 0/3 · flags: methods_paper · verified 2026-08-26 via openalex, arxiv</sub>

## 7. Structurally-bounded Agentic Graph Exploration for Evidence-Grounded Scholarly DeepSearch

Rima Hazra, Sayan Layek, Somnath Banerjee, Soumen Chakrabarti et al. · 2026 · arXiv · experimental · overall 3/3

<https://doi.org/10.48550/arxiv.2608.24809>

**Key finding.** A bounded pipeline of one seed search, 1.5-hop citation expansion, entailment-based pruning, and recency-aware random-walk ranking outperforms proprietary deep-research agents by up to 3x recall@50 at roughly a third of the cost.

**Why it made the cut.** design-changing · selected by score · strongest on C2 agentic mechanism gain (3/3). Isolates a specific agentic move (citation-graph traversal) and shows it beats undifferentiated deep-research loops, core to decision 2.

**Why it matters here.** Directly isolates citation-graph traversal as the mechanism carrying the gain over open-ended agentic search loops, which answers question 2 with a concrete, cheaper alternative design.

**Method.** Bounded, inspectable agentic pipeline evaluated on LitSearch and a further benchmark over a 500K-paper arXiv corpus, compared against deep-research agents built on proprietary models.

**Limitations.**

- evaluated on arXiv-only corpus and two benchmarks
- bounded design trades exploration flexibility for inspectability, which may not generalize to less citation-dense fields

<sub>selected: score · criteria: C1 1/3 · C2 3/3 · C3 3/3 · C4 1/3 · C5 0/3 · flags: methods_paper · verified 2026-08-26 via arxiv</sub>

## 8. AI's Capability in Assisting Scientific Research in Physics, Astrophysics, and Cosmology I: Literature Review

Anamaria Hell, Kateryna Vovk, Veena Krishnaraj, Jia Liu et al. · 2026 · arXiv · experimental · overall 3/3

<https://doi.org/10.48550/arxiv.2607.25672>

**Key finding.** Overlap between human-selected and mid-2025 LLM-selected references was under 6%, with 64% of AI-generated references containing at least one incorrect metadata field, though a 2026 model showed zero fabrications/mismatches in a single test.

**Why it made the cut.** contradicting · selected by score · strongest on C5 gain replication failure (3/3). Provides the sharpest evidence against the brief's premise that agentic gains are real, directly serving decision question 4.

**Why it matters here.** Directly contradicts the premise that agentic LLM literature search reliably matches expert search quality, and quantifies hallucination/metadata-error rates that any recall claim must be checked against.

**Method.** Controlled study of eight expert-conceived physics/astrophysics/cosmology research projects, with human experts and LLMs (ChatGPT-4o, Deep Research, Gemini, later ChatGPT Pro 5.5) performing identical literature review tasks in parallel.

**Limitations.**

- small sample of eight projects
- domain is physics/astro/cosmology rather than CS literature-search benchmarks
- 2026-model improvement based on a single-project test

<sub>selected: score · criteria: C1 1/3 · C2 1/3 · C3 0/3 · C4 2/3 · C5 3/3 · flags: contradicts · verified 2026-08-26 via openalex, arxiv</sub>

## 9. Multi-Turn Agentic Scientific Literature Search via Workflow Induction

Jisen Li, Bingxuan Li, Nanyi Jiang, Xuying Ning et al. · 2026 · arXiv · experimental · overall 3/3

<https://doi.org/10.48550/arxiv.2607.00597>

**Key finding.** PaperPilot-9B, which frames literature search as an executable, user-refinable DAG of search operators (keyword search, citation expansion, filtering, scoring, reranking, evidence extraction), raises Hit@5 from 58.0 to 77.0, MRR from 47.5 to 59.4, and nDCG@10 from 26.8 to 32.5 over a base toolset agent, while cutting workflow execution errors from 9.5% to 0%.

**Why it made the cut.** design-changing · selected by backfill · strongest on C2 agentic mechanism gain (2/3). A 2026 agentic literature-search system whose DAG-based workflow induction and multi-turn refinement are exactly the system design and mechanism questions (decisions 1-2) the brief asks about.

**Why it matters here.** Directly answers decision 2 — it names explicit agentic moves (citation expansion, reranking, workflow refinement from feedback) as the source of a large measured gain over an undifferentiated tool-use agent, and shows the gain is attributable to structuring the workflow itself rather than to the base model.

**Method.** Multi-turn agentic literature search system trained via supervised workflow imitation and preference optimization over controlled workflow corruptions; evaluated against a Qwen3.5-9B base toolset agent. Abstract-only.

**Limitations.**

- comparison baseline is another agentic toolset, not a single-query database search ceiling, so C1 is unaddressed
- no per-operator ablation isolating which single move (citation expansion vs reranking vs reformulation) drives the reported gain
- single model scale (9B) and no benchmark construction detail given
- abstract-only, no independent replication reported

<sub>selected: backfill · criteria: C1 1/3 · C2 2/3 · C3 2/3 · C4 0/3 · C5 0/3 · flags: methods_paper · verified 2026-08-26 via openalex, arxiv</sub>

## 10. Do Cross-References Help LLM Agents Complete Documents? Search Cost, Robustness, and Unreachable Content on a Wiki-Style Corpus

Craig Johnston · 2026 · Open MIND · experimental · overall 2/3

<https://mcp-data-platform.txn2.com/reference/benchmark-report-graph-completion/>

**Key finding.** Removing followable cross-reference links roughly doubles searches-per-grounded-fact at scale, and some facts deemed 'unreachable by search' were in fact recoverable via read-derived re-querying, invalidating naive unreachability claims.

**Why it made the cut.** closely-related · selected by backfill · strongest on C2 agentic mechanism gain (3/3). A rigorous, pre-registered study of link-traversal value and benchmark design in a neighbouring (non-scientific) setting, capped for domain mismatch.

**Why it matters here.** Demonstrates a rigorously constructed benchmark methodology for isolating the cost/benefit of link (graph) traversal versus plain search, directly informing how a literature-search benchmark could control for citation-link contamination — but the corpus is a synthetic organizational wiki, not scientific papers.

**Method.** Pre-registered two-arm contrast on a deterministic synthetic wiki-style corpus (50/500/5000 pages) with and without real hyperlinks, measured across 99 episodes of a Claude agent using search/fetch tools via an MCP server.

**Limitations.**

- synthetic organizational wiki corpus, not scientific literature
- no explicit statement of how the method transfers to citation graphs of scholarly papers

<sub>selected: backfill · criteria: C1 2/3 · C2 3/3 · C3 0/3 · C4 3/3 · C5 1/3 · flags: methods_paper · verified 2026-08-26 via openalex</sub>

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

- [ReBOL: Retrieval via Bayesian Optimization with Batched LLM Relevance Observations and Query Reformulation](https://doi.org/10.48550/arxiv.2603.20513) (2026) — overall 2/3
- [WisPaper: Your AI Scholar Search Engine](https://doi.org/10.48550/arxiv.2512.06879) (2025) — overall 2/3
- [HySemRAG: A Hybrid Semantic Retrieval-Augmented Generation Framework for Automated Literature Synthesis and Methodological Gap Analysis](https://doi.org/10.48550/arxiv.2508.05666) (2025) — overall 2/3
- [EviReform: Evidence-Guided Query Reformulation for Multi-Hop Graph Retrieval](https://doi.org/10.48550/arxiv.2608.13006) (2026) — overall 2/3
- [From Inertia to Objectivity: Improving Deep Research Agents with Noise Isolation](https://doi.org/10.48550/arxiv.2608.23045) (2026) — overall 2/3
