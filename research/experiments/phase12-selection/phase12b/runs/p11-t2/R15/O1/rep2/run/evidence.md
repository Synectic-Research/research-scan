# Evidence scan — p11-t2

Run `/Users/nabergoj/Projects/research-scan/research/experiments/phase12-selection/phase12b/runs/p11-t2/R15/O1/rep2/run` · brief `/Users/nabergoj/Projects/research-scan/research/experiments/phase12-selection/phase12b/runs/p11-t2/R15/O1/rep2/run/brief.md` · rendered 2026-08-26

| # | Paper | Year | Venue | Evidence | Verified |
|---|---|---|---|---|---|
| 1 | [BrowseComp-Plus: A More Fair and Transparent Evaluation Benchmark of Deep-Research Agent](https://doi.org/10.48550/arxiv.2508.06600) · 10.48550/arxiv.2508.06600 | 2025 | arXiv (Cornell University) | experimental | yes |
| 2 | [Projecting BrowseComp-Plus onto ClimbMix: Toward More Realistic Corpora for Agentic Search](https://arxiv.org/abs/2608.20317) | 2026 | — | experimental | yes |
| 3 | [Diagnosing Search Behavior and Failure Modes in Long-Horizon Search Agents](https://doi.org/10.48550/arxiv.2608.01913) · 10.48550/arxiv.2608.01913 | 2026 | arXiv | experimental | yes |
| 4 | [PaSa: An LLM Agent for Comprehensive Academic Paper Search](https://doi.org/10.48550/arxiv.2501.10120) · 10.48550/arxiv.2501.10120 | 2025 | Annual Meeting of the Association for Computational Linguistics | experimental | yes |
| 5 | [Structurally-bounded Agentic Graph Exploration for Evidence-Grounded Scholarly DeepSearch](https://doi.org/10.48550/arxiv.2608.24809) · 10.48550/arxiv.2608.24809 | 2026 | arXiv | experimental | yes |
| 6 | [AI's Capability in Assisting Scientific Research in Physics, Astrophysics, and Cosmology I: Literature Review](https://doi.org/10.48550/arxiv.2607.25672) · 10.48550/arxiv.2607.25672 | 2026 | arXiv | observational | yes |
| 7 | [Deep Research Agents: A Systematic Examination And Roadmap](https://doi.org/10.48550/arxiv.2506.18096) · 10.48550/arxiv.2506.18096 | 2025 | arXiv.org | other | yes |
| 8 | [LLM-guided Hierarchical Search for End-to-end Reasoning Intensive Retrieval](https://arxiv.org/abs/2510.13217) | 2025 | — | experimental | yes |
| 9 | [Multi-Turn Agentic Scientific Literature Search via Workflow Induction](https://doi.org/10.48550/arxiv.2607.00597) · 10.48550/arxiv.2607.00597 | 2026 | arXiv | experimental | yes |
| 10 | [EviReform: Evidence-Guided Query Reformulation for Multi-Hop Graph Retrieval](https://doi.org/10.48550/arxiv.2608.13006) · 10.48550/arxiv.2608.13006 | 2026 | arXiv | experimental | yes |

## 1. BrowseComp-Plus: A More Fair and Transparent Evaluation Benchmark of Deep-Research Agent

Zijian Chen, Xueguang Ma, Shengyao Zhuang, Ping Nie et al. · 2025 · arXiv (Cornell University) · experimental · overall 3/3

<https://doi.org/10.48550/arxiv.2508.06600>

**Key finding.** On a fixed, human-verified corpus, Search-R1 with BM25 achieves only 3.86% accuracy versus GPT-5's 55.9%, and pairing GPT-5 with a Qwen3-Embedding-8B retriever raises accuracy to 70.1% with fewer search calls.

**Why it made the cut.** foundational · selected by score · strongest on C1 baseline recall ceiling (3/3). The canonical fair/transparent benchmark for deep-research/search agents that underlies several other shortlisted papers' evaluations, central to the brief's benchmark-construction question.

**Why it matters here.** The controlled-corpus benchmark other candidates in this scan build directly on (evaluation substrate, projection studies); it sets a concrete, reproducible baseline separating retriever quality from agent reasoning, which the brief's question 1 and 3 both need.

**Method.** Introduces a fixed-corpus derivative of BrowseComp with human-verified supporting documents and mined hard negatives, enabling controlled disentanglement of agent and retriever contributions.

**Limitations.**

- queries are general knowledge-intensive questions, not academic-paper-finding queries specifically
- corpus was assembled per-query from supporting docs plus mined negatives, a construction choice later shown to bias results (see companion projection study)

<sub>selected: score · criteria: C1 3/3 · C2 1/3 · C3 2/3 · C4 3/3 · C5 2/3 · flags: methods_paper · verified 2026-08-26 via openalex, arxiv</sub>

## 2. Projecting BrowseComp-Plus onto ClimbMix: Toward More Realistic Corpora for Agentic Search

Sahel Sharifymoghaddam, Lin Gu, Yijun Ge, Jimmy Lin · 2026 · no venue · experimental · overall 3/3

<https://arxiv.org/abs/2608.20317>

**Key finding.** Relocating BrowseComp-Plus's evidence into the independently-built ClimbMix corpus drops the strongest agent's evidence recall from 84.3% to 21.4% and answer accuracy by five points while it issues 63% more search calls, despite the questions being unchanged.

**Why it made the cut.** contradicting · selected by score · strongest on C1 baseline recall ceiling (3/3). The clearest available demonstration that an agentic search benchmark's construction inflates reported gains, directly answering the brief's hardest question.

**Why it matters here.** Direct, quantified evidence that a reported agentic-search benchmark result is substantially inflated by the original corpus's per-query construction, exactly the question-4 evidence the brief prioritizes finding.

**Method.** A projection pipeline that decomposes each question into atomic reasoning hops and re-grounds them in a new 553M-document corpus, retaining only hops verified by automatic checking, an independent agent, and human review; applied to 830 BrowseComp-Plus questions, yielding 57 fully grounded questions.

**Limitations.**

- pipeline yields only 57 grounded questions from 830, a small evaluation set
- first of a planned series, so generalization to other benchmarks beyond BrowseComp-Plus is not yet demonstrated

<sub>selected: score · criteria: C1 3/3 · C2 1/3 · C3 1/3 · C4 3/3 · C5 3/3 · flags: contradicts, methods_paper · verified 2026-08-26 via arxiv, s2</sub>

## 3. Diagnosing Search Behavior and Failure Modes in Long-Horizon Search Agents

Qi Liu, Jiaxin Mao, Fengbin Zhu, Tat-Seng Chua · 2026 · arXiv · experimental · overall 3/3

<https://doi.org/10.48550/arxiv.2608.01913>

**Key finding.** Across six agents on BrowseComp-Plus and BrowseComp, answer accuracy tracks cumulative retrieval recall far more than the number of searches or context consumed, and the best agents issue far fewer redundant reformulations.

**Why it made the cut.** contradicting · selected by score · strongest on C2 agentic mechanism gain (3/3). Decomposes what part of agentic search effort actually produces gains, the exact mechanism-attribution question the brief prioritizes.

**Why it matters here.** Directly answers the brief's question 2 and undercuts the premise that more agentic search effort is what carries the gain — useful evidence often appears early and agents overshoot, which redirects design attention from 'more iteration' to stopping criteria and evidence selection.

**Method.** Trajectory-level diagnosis using human-annotated document relevance judgments, holding the retrieval model fixed while comparing six long-horizon search agents.

**Limitations.**

- evaluates existing agents rather than proposing a new system
- findings tied to BrowseComp-Plus/BrowseComp corpora, not literature-specific benchmarks

<sub>selected: score · criteria: C1 1/3 · C2 3/3 · C3 1/3 · C4 1/3 · C5 3/3 · flags: contradicts · verified 2026-08-26 via openalex, arxiv</sub>

## 4. PaSa: An LLM Agent for Comprehensive Academic Paper Search

Yichen He, Guanhua Huang, Peiyuan Feng, Yuan Lin et al. · 2025 · Annual Meeting of the Association for Computational Linguistics · experimental · overall 3/3

<https://doi.org/10.48550/arxiv.2501.10120>

**Key finding.** PaSa-7B beats the best Google+GPT-4o baseline by 37.78% in recall@20 and 39.90% in recall@50 on RealScholarQuery, and exceeds prompted PaSa-GPT-4o by 30.36% recall and 4.25% precision.

**Why it made the cut.** design-changing · selected by score · strongest on C1 baseline recall ceiling (3/3). Foundational agentic academic-paper-search system with explicit baseline comparison and benchmark construction, core to the brief's setting.

**Why it matters here.** Gives concrete, large recall gaps over single-query search-engine baselines (Google, Google Scholar) for the exact academic-paper-search task the brief is scanning, anchoring question 1 and offering a benchmark-construction template for question 3.

**Method.** RL-trained LLM agent that invokes search tools, reads papers, and selects references; trained on synthetic AutoScholarQuery (35k queries) and evaluated on a new RealScholarQuery benchmark.

**Limitations.**

- trained on synthetic queries derived from top-tier AI conference papers, may not generalize across fields
- recall gains not decomposed by which agentic move (search vs. reading vs. citation-following) drives them

<sub>selected: score · criteria: C1 3/3 · C2 2/3 · C3 1/3 · C4 3/3 · C5 0/3 · flags: methods_paper · verified 2026-08-26 via openalex, arxiv</sub>

## 5. Structurally-bounded Agentic Graph Exploration for Evidence-Grounded Scholarly DeepSearch

Rima Hazra, Sayan Layek, Somnath Banerjee, Soumen Chakrabarti et al. · 2026 · arXiv · experimental · overall 3/3

<https://doi.org/10.48550/arxiv.2608.24809>

**Key finding.** A bounded pipeline of one seed search, 1.5-hop citation expansion, entailment-based pruning, and recency-aware random-walk ranking outperforms proprietary deep-research agents by up to 3x recall@50 at roughly a third of the cost on LitSearch.

**Why it made the cut.** design-changing · selected by score · strongest on C2 agentic mechanism gain (3/3). A structurally-bounded alternative to open-loop deep research agents that explicitly attributes gains to citation-graph traversal, exactly the mechanism decomposition the brief wants.

**Why it matters here.** Isolates citation-graph traversal and pruning as the specific mechanisms carrying the gain over open-ended agentic search, directly answering the brief's question 2 with an inspectable, bounded design.

**Method.** System design paper evaluated on LitSearch and one further benchmark over a 500K-paper arXiv corpus; compares against open-ended deep-research agents built on proprietary LLMs.

**Limitations.**

- corpus limited to arXiv (500K papers)
- benchmark construction for the 'one further benchmark' not detailed in the abstract

<sub>selected: score · criteria: C1 2/3 · C2 3/3 · C3 2/3 · C4 1/3 · C5 0/3 · flags: methods_paper · verified 2026-08-26 via arxiv</sub>

## 6. AI's Capability in Assisting Scientific Research in Physics, Astrophysics, and Cosmology I: Literature Review

Anamaria Hell, Kateryna Vovk, Veena Krishnaraj, Jia Liu et al. · 2026 · arXiv · observational · overall 3/3

<https://doi.org/10.48550/arxiv.2607.25672>

**Key finding.** Overlap between human-selected and mid-2025 LLM-selected references across eight expert physics/astrophysics/cosmology projects is under 6%, with 3% fabricated references and 64% carrying at least one incorrect metadata field, though a 2026 model showed zero errors on one test project.

**Why it made the cut.** contradicting · selected by score · strongest on C1 baseline recall ceiling (3/3). The sharpest available evidence that current agentic literature search does not reproduce expert recall, which is exactly the hardest-case evidence the brief asks the scan to surface.

**Why it matters here.** Directly tests and largely rejects the brief's premise that agentic literature search reliably matches expert search, giving a concrete low-overlap number to anchor question 1 and a hallucination rate that qualifies any reported agentic gain.

**Method.** Controlled parallel comparison of human experts vs. LLM systems (ChatGPT-4o, ChatGPT Deep Research, Gemini) performing identical literature-review tasks on eight defined research projects.

**Limitations.**

- only eight projects, all in physics/astrophysics/cosmology
- improved 2026 model result is a single-project anecdote, not systematically tested

<sub>selected: score · criteria: C1 3/3 · C2 0/3 · C3 0/3 · C4 2/3 · C5 3/3 · flags: contradicts · verified 2026-08-26 via openalex, arxiv</sub>

## 7. Deep Research Agents: A Systematic Examination And Roadmap

Yuxuan Huang, Yihang Chen, Haozhen Zhang, Kang Li et al. · 2025 · arXiv.org · other · overall 3/3

<https://doi.org/10.48550/arxiv.2506.18096>

**Key finding.** A taxonomy of Deep Research agent architectures (static/dynamic workflows, single/multi-agent, API vs. browser retrieval) alongside a critical assessment finding current benchmarks limited by restricted external-knowledge access, sequential-execution inefficiency, and metrics misaligned with agents' practical objectives.

**Why it made the cut.** plan-influencing · selected by score · strongest on C2 agentic mechanism gain (2/3). The field-level synthesis a research scan needs to place individual system and benchmark papers in context, and the required review-flagged entry.

**Why it matters here.** Gives an orienting map of the mechanisms and benchmark weaknesses across the field, directly informing which specific agentic moves and which benchmark flaws the scan should watch for in questions 2 through 4.

**Method.** Narrative systematic review and taxonomy synthesis, no abstract-stated protocol; includes a maintained repository of DR agent research.

**Limitations.**

- abstract-only, narrative rather than systematic-protocol review
- does not itself measure baseline recall or replication failure, only synthesizes others' findings

<sub>selected: score · criteria: C1 1/3 · C2 2/3 · C3 1/3 · C4 2/3 · C5 1/3 · flags: review · verified 2026-08-26 via arxiv</sub>

## 8. LLM-guided Hierarchical Search for End-to-end Reasoning Intensive Retrieval

Nilesh Gupta, Wei-Cheng Chang, N. Bui, Cho-Jui Hsieh et al. · 2025 · no venue · experimental · overall 3/3

<https://arxiv.org/abs/2510.13217>

**Key finding.** LATTICE, an LLM-guided hierarchical search index with no embedding model in the retrieval loop, reaches 46.7 nDCG@10 on BRIGHT (matching the best fine-tuned ensemble) and 49.1 with a lightweight ensemble, while remaining competitive on SciFact and SciDocs.

**Why it made the cut.** design-changing · selected by score · strongest on C3 retrieval/reranking method (3/3). A core retrieval/reranking method directly evaluated on scientific-literature benchmarks, bearing on the brief's retrieval-layer and baseline-ceiling questions.

**Why it matters here.** Shows the standard embedding-retriever-plus-LLM-verifier pipeline fails when embeddings miss top-k, and offers a retrieval architecture that removes that failure mode — directly relevant to the retrieval/reranking layer underlying literature-search agents, with explicit evaluation on scientific-literature benchmarks (SciFact, SciDocs).

**Method.** Top-down LLM-guided construction of a hierarchical document index from multi-level summaries, plus calibrated path-aggregated LLM traversal at query time; evaluated on BRIGHT, NQ, SciFact, SciDocs.

**Limitations.**

- reasoning-intensive benchmark focus (BRIGHT) is broader than academic paper search specifically
- sliding-window reranking beats it at low token budgets, limiting when the advantage holds

<sub>selected: score · criteria: C1 2/3 · C2 1/3 · C3 3/3 · C4 0/3 · C5 1/3 · flags: methods_paper · verified 2026-08-26 via arxiv, s2</sub>

## 9. Multi-Turn Agentic Scientific Literature Search via Workflow Induction

Jisen Li, Bingxuan Li, Nanyi Jiang, Xuying Ning et al. · 2026 · arXiv · experimental · overall 3/3

<https://doi.org/10.48550/arxiv.2607.00597>

**Key finding.** PaperPilot-9B, a multi-turn literature-search agent that induces an executable DAG of search operators (keyword search, citation expansion, filtering, scoring, reranking, evidence extraction), raises Hit@5 from 58.0 to 77.0, MRR from 47.5 to 59.4, and nDCG@10 from 26.8 to 32.5 over a base toolset agent, while cutting workflow execution errors from 9.5% to 0%.

**Why it made the cut.** design-changing · selected by backfill · strongest on C2 agentic mechanism gain (2/3). A literature-search agent that explicitly attributes measured gains to named agentic operators (citation expansion, reranking, workflow refinement), squarely in the brief's setting.

**Why it matters here.** Directly tests what agentic moves add over an undifferentiated toolset agent by making the workflow explicit and editable — the closest evidence in this shortlist to decision 2 (which specific moves carry the gain), though the baseline compared against is another agent rather than a clean single-query database search ceiling, so it cannot answer decision 1.

**Method.** Supervised workflow imitation plus preference optimization over controlled workflow corruptions; evaluated against a Qwen3.5-9B toolset agent baseline under multi-turn interaction. Abstract-only for full experimental detail.

**Limitations.**

- baseline is a toolset agent, not a single-query BM25/embedding/API baseline, so the recall ceiling question (C1) is not addressed
- no discussion of how the evaluation query/relevance set was constructed
- gains reported on one model family (Qwen3.5-9B) with no cross-benchmark or replication check

<sub>selected: backfill · criteria: C1 1/3 · C2 2/3 · C3 2/3 · C4 0/3 · C5 0/3 · flags: methods_paper · verified 2026-08-26 via openalex, arxiv</sub>

## 10. EviReform: Evidence-Guided Query Reformulation for Multi-Hop Graph Retrieval

Xin Xu, Yoshua Y. Li · 2026 · arXiv · experimental · overall 2/3

<https://doi.org/10.48550/arxiv.2608.13006>

**Key finding.** EviReform, which forms residual queries from retrieved passages to guide graph-based multi-hop retrieval toward evidence left underspecified by the original question, exceeds the strongest baseline by up to 5.59 Recall@5 points and 4.50 F1 points on 2WikiMultiHopQA, HotpotQA, and MuSiQue.

**Why it made the cut.** closely-related · selected by backfill · strongest on C2 agentic mechanism gain (3/3). Describes a query-reformulation-plus-graph-retrieval mechanism structurally close to citation-graph traversal, but demonstrated only in multi-hop QA, not literature search — a technique to note, not a direct answer to the brief's questions.

**Why it matters here.** Isolates exactly the kind of mechanism the brief's C2/C3 criteria ask about — query reformulation combined with graph-structured retrieval — with a quantified, ablatable gain, but the evidence is built and evaluated entirely on multi-hop QA retrieval rather than scientific literature search agents, so it can sharpen technique choices without answering the brief's recall-ceiling or benchmark-construction questions in its own setting.

**Method.** Retrieval architecture separating query revision from graph-based evidence aggregation, normalizing and combining original and residual retrieval signals, propagated across propositions sharing entities; evaluated on three multi-hop QA benchmarks. Abstract-only.

**Limitations.**

- evaluated on general multi-hop QA datasets, not literature-search corpora or agentic search benchmarks
- no discussion of benchmark construction, contamination, or labeling
- baseline compared against is the 'strongest baseline' in QA retrieval literature, not a single-query database search ceiling as the brief defines it

<sub>selected: backfill · criteria: C1 1/3 · C2 3/3 · C3 3/3 · C4 0/3 · C5 0/3 · flags: methods_paper · verified 2026-08-26 via openalex, arxiv</sub>

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

- [From Inertia to Objectivity: Improving Deep Research Agents with Noise Isolation](https://doi.org/10.48550/arxiv.2608.23045) (2026) — overall 2/3
- [ReBOL: Retrieval via Bayesian Optimization with Batched LLM Relevance Observations and Query Reformulation](https://doi.org/10.48550/arxiv.2603.20513) (2026) — overall 2/3
- [Do Cross-References Help LLM Agents Complete Documents? Search Cost, Robustness, and Unreachable Content on a Wiki-Style Corpus](https://mcp-data-platform.txn2.com/reference/benchmark-report-graph-completion/) (2026) — overall 2/3
- [WisPaper: Your AI Scholar Search Engine](https://doi.org/10.48550/arxiv.2512.06879) (2025) — overall 2/3
- [HySemRAG: A Hybrid Semantic Retrieval-Augmented Generation Framework for Automated Literature Synthesis and Methodological Gap Analysis](https://doi.org/10.48550/arxiv.2508.05666) (2025) — overall 2/3
