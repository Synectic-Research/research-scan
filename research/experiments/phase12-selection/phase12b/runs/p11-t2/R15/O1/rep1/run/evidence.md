# Evidence scan — p11-t2

Run `/Users/nabergoj/Projects/research-scan/research/experiments/phase12-selection/phase12b/runs/p11-t2/R15/O1/rep1/run` · brief `/Users/nabergoj/Projects/research-scan/research/experiments/phase12-selection/phase12b/runs/p11-t2/R15/O1/rep1/run/brief.md` · rendered 2026-08-26

| # | Paper | Year | Venue | Evidence | Verified |
|---|---|---|---|---|---|
| 1 | [Diagnosing Search Behavior and Failure Modes in Long-Horizon Search Agents](https://doi.org/10.48550/arxiv.2608.01913) · 10.48550/arxiv.2608.01913 | 2026 | arXiv | observational | yes |
| 2 | [BrowseComp-Plus: A More Fair and Transparent Evaluation Benchmark of Deep-Research Agent](https://doi.org/10.48550/arxiv.2508.06600) · 10.48550/arxiv.2508.06600 | 2025 | arXiv (Cornell University) | experimental | yes |
| 3 | [Projecting BrowseComp-Plus onto ClimbMix: Toward More Realistic Corpora for Agentic Search](https://arxiv.org/abs/2608.20317) | 2026 | — | experimental | yes |
| 4 | [PaSa: An LLM Agent for Comprehensive Academic Paper Search](https://doi.org/10.48550/arxiv.2501.10120) · 10.48550/arxiv.2501.10120 | 2025 | Annual Meeting of the Association for Computational Linguistics | experimental | yes |
| 5 | [Structurally-bounded Agentic Graph Exploration for Evidence-Grounded Scholarly DeepSearch](https://doi.org/10.48550/arxiv.2608.24809) · 10.48550/arxiv.2608.24809 | 2026 | arXiv | experimental | yes |
| 6 | [AI's Capability in Assisting Scientific Research in Physics, Astrophysics, and Cosmology I: Literature Review](https://doi.org/10.48550/arxiv.2607.25672) · 10.48550/arxiv.2607.25672 | 2026 | arXiv | observational | yes |
| 7 | [LLM-guided Hierarchical Search for End-to-end Reasoning Intensive Retrieval](https://arxiv.org/abs/2510.13217) | 2025 | — | experimental | yes |
| 8 | [Deep Research Agents: A Systematic Examination And Roadmap](https://doi.org/10.48550/arxiv.2506.18096) · 10.48550/arxiv.2506.18096 | 2025 | arXiv.org | other | yes |
| 9 | [Multi-Turn Agentic Scientific Literature Search via Workflow Induction](https://doi.org/10.48550/arxiv.2607.00597) · 10.48550/arxiv.2607.00597 | 2026 | arXiv | experimental | yes |
| 10 | [From Inertia to Objectivity: Improving Deep Research Agents with Noise Isolation](https://doi.org/10.48550/arxiv.2608.23045) · 10.48550/arxiv.2608.23045 | 2026 | arXiv | experimental | yes |

## 1. Diagnosing Search Behavior and Failure Modes in Long-Horizon Search Agents

Qi Liu, Jiaxin Mao, Fengbin Zhu, Tat-Seng Chua · 2026 · arXiv · observational · overall 3/3

<https://doi.org/10.48550/arxiv.2608.01913>

**Key finding.** Across six agents on BrowseComp-Plus and BrowseComp, answer accuracy correlates far more with cumulative retrieval recall of evidence than with the number of search steps or context consumed, and useful evidence usually appears early while agents keep issuing low-yield queries.

**Why it made the cut.** design-changing · selected by score · strongest on C2 agentic mechanism gain (3/3). Directly decomposes which agentic mechanisms carry the measured gain and where search effort fails to translate into better answers, central to decisions 2 and 4.

**Why it matters here.** Directly answers what carries the agentic gain: it's retrieved-evidence quality, not search volume, undercutting the assumption that more iterative searching or reformulation automatically helps, and it argues for stopping criteria based on evidence sufficiency rather than search budget.

**Method.** Trajectory-level diagnosis with human-annotated document relevance judgments, decomposing agent failures into retrieval gaps vs. utilization gaps; retrieval model and harness held fixed across six agents on BrowseComp-Plus, validated on BrowseComp with an open-web API.

**Limitations.**

- Evaluated on BrowseComp-family QA benchmarks rather than dedicated academic paper search tasks
- Six agents studied, may not generalize to all agent architectures

<sub>selected: score · criteria: C1 2/3 · C2 3/3 · C3 1/3 · C4 1/3 · C5 3/3 · verified 2026-08-26 via openalex, arxiv</sub>

## 2. BrowseComp-Plus: A More Fair and Transparent Evaluation Benchmark of Deep-Research Agent

Zijian Chen, Xueguang Ma, Shengyao Zhuang, Ping Nie et al. · 2025 · arXiv (Cornell University) · experimental · overall 3/3

<https://doi.org/10.48550/arxiv.2508.06600>

**Key finding.** On the fixed-corpus BrowseComp-Plus benchmark, Search-R1 with BM25 retrieval reaches only 3.86% accuracy while GPT-5 reaches 55.9%, and pairing GPT-5 with a stronger embedding retriever raises accuracy to 70.1% with fewer search calls.

**Why it made the cut.** design-changing · selected by score · strongest on C1 baseline recall ceiling (3/3). The benchmark most directly answering decision 1 (single-query baseline recall ceiling) and decision 3 (benchmark construction), used as the anchor by several other shortlisted papers.

**Why it matters here.** Gives a controlled, reproducible baseline for single-query retrieval (BM25) versus stronger retrieval and reasoning, directly setting the recall/accuracy ceiling that agentic gains must be measured against, and is explicitly designed for retriever/agent disentanglement.

**Method.** Benchmark construction: queries derived from BrowseComp with a fixed, curated corpus, human-verified supporting documents, and mined hard negatives, enabling disentangled evaluation of agent vs. retriever contributions.

**Limitations.**

- Corpus limited to ~100K documents assembled per-query, later criticized for evidence and distractors both being selected per query
- Focused on deep-research QA rather than literature discovery specifically

<sub>selected: score · criteria: C1 3/3 · C2 1/3 · C3 2/3 · C4 3/3 · C5 1/3 · flags: methods_paper · verified 2026-08-26 via openalex, arxiv</sub>

## 3. Projecting BrowseComp-Plus onto ClimbMix: Toward More Realistic Corpora for Agentic Search

Sahel Sharifymoghaddam, Lin Gu, Yijun Ge, Jimmy Lin · 2026 · no venue · experimental · overall 3/3

<https://arxiv.org/abs/2608.20317>

**Key finding.** Relocating BrowseComp-Plus questions' evidence into the independently-built ClimbMix corpus drops the strongest agent's evidence recall from 84.3% to 21.4% and answer accuracy by five points, while search calls rise 63%, yielding only 57 fully-grounded questions from 830 candidates.

**Why it made the cut.** contradicting · selected by score · strongest on C4 benchmark construction (3/3). The clearest demonstration in the shortlist of a reported agentic gain failing to hold under a harder, independently-built corpus — central to decision 4 and the brief's explicit ask for disconfirming evidence.

**Why it matters here.** Directly shows a reported agentic/retrieval gain shrinking sharply once the benchmark's own per-query-curated corpus is replaced with an independently-built one, exactly the replication-failure evidence decision 4 is looking for, and it exposes a specific contamination mechanism in benchmark construction.

**Method.** A projection pipeline decomposing questions into atomic reasoning hops, re-grounding each hop in a 553M-document pretraining corpus (ClimbMix) built without reference to the benchmark, verified by automatic checks, an independent agent, and human review.

**Limitations.**

- Only 57 of 830 questions survive the grounding pipeline, a small evaluation set
- Single benchmark family (BrowseComp-Plus) projected so far

<sub>selected: score · criteria: C1 2/3 · C2 1/3 · C3 1/3 · C4 3/3 · C5 3/3 · flags: contradicts, methods_paper · verified 2026-08-26 via arxiv, s2</sub>

## 4. PaSa: An LLM Agent for Comprehensive Academic Paper Search

Yichen He, Guanhua Huang, Peiyuan Feng, Yuan Lin et al. · 2025 · Annual Meeting of the Association for Computational Linguistics · experimental · overall 3/3

<https://doi.org/10.48550/arxiv.2501.10120>

**Key finding.** PaSa-7B, trained with RL on a synthetic 35k-query dataset, surpasses the best Google-based baseline by 37.78% in recall@20 and 39.90% in recall@50 on RealScholarQuery.

**Why it made the cut.** design-changing · selected by score · strongest on C4 benchmark construction (3/3). A foundational agentic paper-search system reporting the specific recall gain over single-query baselines that decisions 1 and 2 need.

**Why it matters here.** Establishes a concrete, large recall gain of an agentic academic search system over single-query search-engine baselines (Google, Google Scholar), giving a quantified answer to how much agentic design adds over single-query search.

**Method.** RL-trained LLM agent that invokes search tools, reads papers, and selects references; trained on synthetic AutoScholarQuery (35k queries) and evaluated on a newly built real-world benchmark, RealScholarQuery.

**Limitations.**

- Baselines are search engines with GPT-4o paraphrasing rather than a controlled BM25/embedding ceiling
- Training data is synthetic, may not transfer to all query types

<sub>selected: score · criteria: C1 2/3 · C2 2/3 · C3 1/3 · C4 3/3 · C5 0/3 · flags: methods_paper · verified 2026-08-26 via openalex, arxiv</sub>

## 5. Structurally-bounded Agentic Graph Exploration for Evidence-Grounded Scholarly DeepSearch

Rima Hazra, Sayan Layek, Somnath Banerjee, Soumen Chakrabarti et al. · 2026 · arXiv · experimental · overall 3/3

<https://doi.org/10.48550/arxiv.2608.24809>

**Key finding.** Crase, using a single seed search plus 1.5-hop citation-graph expansion and entailment-based pruning, outperforms deep research agents built on proprietary models by up to 3x recall@50 at roughly a third of the cost on LitSearch and a further benchmark.

**Why it made the cut.** design-changing · selected by score · strongest on C2 agentic mechanism gain (3/3). Attributes measured gains specifically to citation-graph traversal, exactly what decision 2 asks for.

**Why it matters here.** Isolates citation-graph traversal as the specific mechanism carrying the gain over open-ended agentic search loops, and shows a bounded, inspectable design can beat costlier deep-research agents — directly informs which agentic move to build.

**Method.** Bounded pipeline: one search-engine query for seed papers, citation-neighborhood expansion, entailment-based edge pruning, and recency-aware random-walk ranking, evaluated over a 500K-paper arXiv corpus.

**Limitations.**

- Compares against proprietary deep-research agents rather than a plain single-query baseline directly
- Restricted to arXiv corpus, may not generalize to broader literature

<sub>selected: score · criteria: C1 2/3 · C2 3/3 · C3 2/3 · C4 1/3 · C5 0/3 · flags: methods_paper · verified 2026-08-26 via arxiv</sub>

## 6. AI's Capability in Assisting Scientific Research in Physics, Astrophysics, and Cosmology I: Literature Review

Anamaria Hell, Kateryna Vovk, Veena Krishnaraj, Jia Liu et al. · 2026 · arXiv · observational · overall 3/3

<https://doi.org/10.48550/arxiv.2607.25672>

**Key finding.** Overlap between human- and AI-selected references in literature reviews is under 6%, and 64% of AI-generated references from mid-2025 models (ChatGPT-4o, ChatGPT Deep Research, Gemini) contain at least one incorrect metadata field, though a 2026 model showed zero errors in a single test.

**Why it made the cut.** contradicting · selected by score · strongest on C1 baseline recall ceiling (3/3). Provides direct evidence that agentic/AI literature search does not yet match human search quality, addressing decision 4 and contradicting the stated premise.

**Why it matters here.** Directly contradicts the premise that agentic literature-search gains are already real: current systems barely reproduce expert search coverage and generate substantial reference errors, exactly the failure-to-replicate evidence the brief asks the scan to prioritize.

**Method.** Controlled comparison of eight expert-conceived research projects, human experts vs. mid-2025 and 2026 LLMs performing identical literature review tasks in physics, astrophysics, and cosmology.

**Limitations.**

- Small sample of eight projects
- Domain-specific to physics/astro/cosmology rather than general scientific literature
- Uses black-box commercial tools rather than instrumented agent architectures

<sub>selected: score · criteria: C1 3/3 · C2 0/3 · C3 0/3 · C4 2/3 · C5 3/3 · flags: contradicts · verified 2026-08-26 via openalex, arxiv</sub>

## 7. LLM-guided Hierarchical Search for End-to-end Reasoning Intensive Retrieval

Nilesh Gupta, Wei-Cheng Chang, N. Bui, Cho-Jui Hsieh et al. · 2025 · no venue · experimental · overall 3/3

<https://arxiv.org/abs/2510.13217>

**Key finding.** LATTICE, which lets an LLM traverse a hierarchically-built search index directly instead of relying on embedding-based top-k retrieval, matches the best fine-tuned ensemble on BRIGHT (46.7 nDCG@10) and reaches 49.1 with a lightweight ensemble, while remaining competitive on SciFact and SciDocs.

**Why it made the cut.** plan-influencing · selected by score · strongest on C3 retrieval/reranking method (3/3). A retrieval method directly targeting the failure of embedding-based single-pass retrieval underlying many agentic search systems, tested partly on scientific-literature IR benchmarks.

**Why it matters here.** Directly challenges the standard 'cheap embedding retriever + LLM verifier' recipe used underneath most agentic search systems, showing embedding-based recall ceilings can be bypassed by LLM-guided graph traversal — relevant to both the recall-ceiling question and retrieval-method choice.

**Method.** LLM-guided top-down construction of a hierarchical document index from multi-level summaries, plus calibrated path-aggregated LLM traversal with cross-branch reference nodes; evaluated on BRIGHT and traditional IR benchmarks including SciFact and SciDocs.

**Limitations.**

- Reasoning-intensive benchmark (BRIGHT) is general, not literature-search specific, though SciFact/SciDocs are scientific
- Reranking has a better tradeoff at low token budgets, so gains depend on budget regime

<sub>selected: score · criteria: C1 2/3 · C2 1/3 · C3 3/3 · C4 0/3 · C5 1/3 · flags: methods_paper · verified 2026-08-26 via arxiv, s2</sub>

## 8. Deep Research Agents: A Systematic Examination And Roadmap

Yuxuan Huang, Yihang Chen, Haozhen Zhang, Kang Li et al. · 2025 · arXiv.org · other · overall 3/3

<https://doi.org/10.48550/arxiv.2506.18096>

**Key finding.** A systematic taxonomy of Deep Research agents identifies static vs. dynamic workflows and single- vs. multi-agent architectures, and critically finds current benchmarks limited by restricted external-knowledge access, sequential-execution inefficiency, and metric misalignment with DR agents' actual objectives.

**Why it made the cut.** plan-influencing · selected by score · strongest on C4 benchmark construction (2/3). The field-level synthesis of architectures and benchmark limitations, useful as the review anchor for decisions 2 and 3.

**Why it matters here.** Synthesizes the field's benchmark weaknesses directly relevant to decision 3 — it names specific construction flaws (restricted knowledge access, metric misalignment) that make cross-system comparisons unreliable, which should shape how this scan interprets any single benchmark's numbers.

**Method.** abstract-only; narrative systematic review and taxonomy of architectural components (information acquisition, tool-use frameworks, planning strategies) plus a critical benchmark evaluation, with a maintained repository.

**Limitations.**

- Narrative survey rather than systematic-protocol review, abstract gives no quantitative synthesis
- Covers deep research agents broadly rather than literature search specifically

<sub>selected: score · criteria: C1 1/3 · C2 1/3 · C3 1/3 · C4 2/3 · C5 1/3 · flags: review · verified 2026-08-26 via arxiv</sub>

## 9. Multi-Turn Agentic Scientific Literature Search via Workflow Induction

Jisen Li, Bingxuan Li, Nanyi Jiang, Xuying Ning et al. · 2026 · arXiv · experimental · overall 3/3

<https://doi.org/10.48550/arxiv.2607.00597>

**Key finding.** PaperPilot-9B, a multi-turn agentic search system built as an executable, editable DAG of paper-search operators (keyword search, citation expansion, filtering, scoring, reranking, evidence extraction), improves Hit@5 from 58.0 to 77.0, MRR from 47.5 to 59.4, and nDCG@10 from 26.8 to 32.5 over a base toolset agent, while cutting workflow execution errors from 9.5% to 0%.

**Why it made the cut.** design-changing · selected by backfill · strongest on C2 agentic mechanism gain (2/3). A 2026 agentic literature-search system explicitly combining citation-graph traversal, query reformulation via workflow refinement, and reranking, with reported quantitative gains — squarely the system design the brief is scanning for.

**Why it matters here.** Directly instantiates the system design the brief is orienting on — combining query reformulation, citation-graph traversal and reranking as explicit, inspectable workflow steps — with concrete effect sizes against a non-agentic toolset baseline, though gains are reported for the whole workflow rather than isolated per-mechanism via ablation.

**Method.** Supervised workflow imitation plus preference optimization over controlled workflow corruptions; evaluated on multi-turn literature search interactions comparing PaperPilot-9B to a base Qwen3.5-9B toolset agent.

**Limitations.**

- gains reported for the composite system, not decomposed by individual operator (reformulation vs. citation expansion vs. reranking)
- no comparison to a single-query database search ceiling
- no benchmark construction detail (query source, relevance labeling, contamination) given
- no replication or cross-benchmark stress test reported

<sub>selected: backfill · criteria: C1 1/3 · C2 2/3 · C3 2/3 · C4 1/3 · C5 0/3 · flags: methods_paper · verified 2026-08-26 via openalex, arxiv</sub>

## 10. From Inertia to Objectivity: Improving Deep Research Agents with Noise Isolation

Xiangxin Zhang, Zhanwei Zhang, Zhihang Fu, Binbin Lin et al. · 2026 · arXiv · experimental · overall 2/3

<https://doi.org/10.48550/arxiv.2608.23045>

**Key finding.** Deep research agents exhibit an 'inertia bias' — worse judgment when evaluating outcomes of their own prior search actions — and the proposed NIS-Agent, which isolates context at webpage-triage and answer-validation points, reduces token cost by 33% while maintaining competitive performance across GAIA, WebWalkerQA, BrowseComp, and BrowseComp-zh.

**Why it made the cut.** closely-related · selected by backfill · strongest on C2 agentic mechanism gain (2/3). Surfaces a mechanism-level failure mode inside agentic search that could explain inflated or fragile reported gains, relevant to decision 4.

**Why it matters here.** Identifies a specific, previously undocumented failure mode inside agentic search loops that can silently erode the reliability of reported gains — relevant to where agentic gains fail to hold under self-referential judgment conditions.

**Method.** Introduces the IBIS benchmark controlling search observations while varying self-authorship of prior actions; proposes NIS-Agent with context isolation, and trains an 8B model for intrinsic resistance to the bias.

**Limitations.**

- Evaluated on general deep-research QA benchmarks rather than academic literature search specifically
- Bias measured via a purpose-built benchmark (IBIS), generalization to other agent designs untested

<sub>selected: backfill · criteria: C1 0/3 · C2 2/3 · C3 1/3 · C4 2/3 · C5 2/3 · verified 2026-08-26 via arxiv</sub>

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

- [EviReform: Evidence-Guided Query Reformulation for Multi-Hop Graph Retrieval](https://doi.org/10.48550/arxiv.2608.13006) (2026) — overall 2/3
- [ReBOL: Retrieval via Bayesian Optimization with Batched LLM Relevance Observations and Query Reformulation](https://doi.org/10.48550/arxiv.2603.20513) (2026) — overall 2/3
- [Do Cross-References Help LLM Agents Complete Documents? Search Cost, Robustness, and Unreachable Content on a Wiki-Style Corpus](https://mcp-data-platform.txn2.com/reference/benchmark-report-graph-completion/) (2026) — overall 2/3
- [HySemRAG: A Hybrid Semantic Retrieval-Augmented Generation Framework for Automated Literature Synthesis and Methodological Gap Analysis](https://doi.org/10.48550/arxiv.2508.05666) (2025) — overall 2/3
- [WisPaper: Your AI Scholar Search Engine](https://doi.org/10.48550/arxiv.2512.06879) (2025) — overall 2/3
