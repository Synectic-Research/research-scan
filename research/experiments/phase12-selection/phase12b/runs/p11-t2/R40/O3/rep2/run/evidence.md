# Evidence scan — p11-t2

Run `/Users/nabergoj/Projects/research-scan/research/experiments/phase12-selection/phase12b/runs/p11-t2/R40/O3/rep2/run` · brief `/Users/nabergoj/Projects/research-scan/research/experiments/phase12-selection/phase12b/runs/p11-t2/R40/O3/rep2/run/brief.md` · rendered 2026-08-26

| # | Paper | Year | Venue | Evidence | Verified |
|---|---|---|---|---|---|
| 1 | [Diagnosing Search Behavior and Failure Modes in Long-Horizon Search Agents](https://doi.org/10.48550/arxiv.2608.01913) · 10.48550/arxiv.2608.01913 | 2026 | arXiv | observational | yes |
| 2 | [BrowseComp-Plus: A More Fair and Transparent Evaluation Benchmark of Deep-Research Agent](https://doi.org/10.48550/arxiv.2508.06600) · 10.48550/arxiv.2508.06600 | 2025 | arXiv (Cornell University) | experimental | yes |
| 3 | [Structurally-bounded Agentic Graph Exploration for Evidence-Grounded Scholarly DeepSearch](https://doi.org/10.48550/arxiv.2608.24809) · 10.48550/arxiv.2608.24809 | 2026 | arXiv | experimental | yes |
| 4 | [Deep Research Agents: A Systematic Examination And Roadmap](https://doi.org/10.48550/arxiv.2506.18096) · 10.48550/arxiv.2506.18096 | 2025 | arXiv.org | other | yes |
| 5 | [PaSa: An LLM Agent for Comprehensive Academic Paper Search](https://doi.org/10.48550/arxiv.2501.10120) · 10.48550/arxiv.2501.10120 | 2025 | Annual Meeting of the Association for Computational Linguistics | experimental | yes |
| 6 | [LitSearch: A Retrieval Benchmark for Scientific Literature Search](https://doi.org/10.48550/arxiv.2407.18940) · 10.48550/arxiv.2407.18940 | 2024 | Conference on Empirical Methods in Natural Language Processing | experimental | yes |
| 7 | [Towards Recursive Self-Evolving Agentic Literature Retrieval](https://doi.org/10.48550/arxiv.2605.14306) · 10.48550/arxiv.2605.14306 | 2026 | arXiv | experimental | yes |
| 8 | [LLM-guided Hierarchical Search for End-to-end Reasoning Intensive Retrieval](https://arxiv.org/abs/2510.13217) | 2025 | — | experimental | yes |
| 9 | [Multi-Turn Agentic Scientific Literature Search via Workflow Induction](https://doi.org/10.48550/arxiv.2607.00597) · 10.48550/arxiv.2607.00597 | 2026 | arXiv | experimental | yes |
| 10 | [AI's Capability in Assisting Scientific Research in Physics, Astrophysics, and Cosmology I: Literature Review](https://doi.org/10.48550/arxiv.2607.25672) · 10.48550/arxiv.2607.25672 | 2026 | arXiv | experimental | yes |

## 1. Diagnosing Search Behavior and Failure Modes in Long-Horizon Search Agents

Qi Liu, Jiaxin Mao, Fengbin Zhu, Tat-Seng Chua · 2026 · arXiv · observational · overall 3/3

<https://doi.org/10.48550/arxiv.2608.01913>

**Key finding.** Across six agents on BrowseComp-Plus (validated on BrowseComp), answer accuracy correlates with cumulative retrieval recall, not with number of searches or context consumed, and the best-performing agents issue far fewer redundant queries.

**Why it made the cut.** plan-influencing · selected by score · strongest on C2 agentic mechanism gain (3/3). Directly diagnoses which agentic moves (reformulation, crawling volume) do and do not carry measured gains, with explicit benchmark methodology — central to questions 2 and 4.

**Why it matters here.** Directly targets question 2 and 4: it shows that more search effort and more reformulation do not reliably translate into gains, redirecting what should be measured (cumulative recall, stopping criteria) rather than search volume.

**Method.** Trajectory-level diagnosis using human-annotated document-level relevance judgments, decomposing failures into retrieval gaps versus evidence-utilization gaps, with retrieval model and harness held fixed across six agents.

**Limitations.**

- scoped to two closely related benchmarks (BrowseComp-Plus/BrowseComp)
- retrieval model held fixed, so findings may not generalize across retrieval backends

<sub>selected: score · criteria: C1 2/3 · C2 3/3 · C3 1/3 · C4 3/3 · C5 3/3 · flags: contradicts · verified 2026-08-26 via openalex, arxiv</sub>

## 2. BrowseComp-Plus: A More Fair and Transparent Evaluation Benchmark of Deep-Research Agent

Zijian Chen, Xueguang Ma, Shengyao Zhuang, Ping Nie et al. · 2025 · arXiv (Cornell University) · experimental · overall 3/3

<https://doi.org/10.48550/arxiv.2508.06600>

**Key finding.** On BrowseComp-Plus's fixed, human-verified corpus, Search-R1 with BM25 achieves only 3.86% accuracy versus GPT-5's 55.9%, rising to 70.1% when GPT-5 is paired with a Qwen3-Embedding retriever using fewer search calls.

**Why it made the cut.** design-changing · selected by score · strongest on C1 baseline recall ceiling (3/3). Central to C1, C3, and C4: quantifies the baseline BM25 ceiling, evaluates retrieval methods, and demonstrates rigorous, contamination-resistant benchmark construction.

**Why it matters here.** Gives a controlled, corpus-fixed measurement of the accuracy/recall ceiling of a plain retriever (BM25) versus stronger retrievers and reasoning models — exactly the anchor decision 1 needs — and shows how uncontrolled live-web benchmarks can misattribute gains.

**Method.** Benchmark derived from BrowseComp using a fixed curated corpus with human-verified supporting documents and mined hard negatives, enabling controlled disentanglement of retriever vs. reasoning-model contributions.

**Limitations.**

- Domain is general web deep-research (BrowseComp-derived), not scientific literature databases specifically
- Corpus curation choices could still bias which documents count as 'hard negatives'

<sub>selected: score · criteria: C1 3/3 · C2 1/3 · C3 3/3 · C4 3/3 · C5 2/3 · flags: methods_paper · verified 2026-08-26 via openalex, arxiv</sub>

## 3. Structurally-bounded Agentic Graph Exploration for Evidence-Grounded Scholarly DeepSearch

Rima Hazra, Sayan Layek, Somnath Banerjee, Soumen Chakrabarti et al. · 2026 · arXiv · experimental · overall 3/3

<https://doi.org/10.48550/arxiv.2608.24809>

**Key finding.** A bounded pipeline (single seed query, 1.5-hop citation expansion, entailment-based pruning, recency-aware random-walk ranking) outperforms open-ended deep-research agents on proprietary models by up to 3x recall@50 at roughly a third of the cost on LitSearch and a 500K-paper arXiv corpus.

**Why it made the cut.** design-changing · selected by score · strongest on C2 agentic mechanism gain (3/3). A bounded citation-graph-traversal design beating full deep-research agents is exactly the kind of evidence the brief asks the scan to hunt for on premise question 2 and 4.

**Why it matters here.** Directly answers what agentic move carries the gain (citation-graph traversal + pruning, not open-ended iteration) and challenges the premise that more elaborate agentic loops necessarily beat simpler bounded designs, at lower cost.

**Method.** Structural, inspectable alternative to open-ended agentic search loops; evaluated on LitSearch plus one further benchmark over a fixed arXiv corpus, compared against proprietary deep-research agents.

**Limitations.**

- single corpus/domain (arXiv) and two benchmarks
- comparison against 'deep research agents' as a class may not cover every agentic design variant

<sub>selected: score · criteria: C1 2/3 · C2 3/3 · C3 2/3 · C4 2/3 · C5 3/3 · flags: contradicts, methods_paper · verified 2026-08-26 via arxiv</sub>

## 4. Deep Research Agents: A Systematic Examination And Roadmap

Yuxuan Huang, Yihang Chen, Haozhen Zhang, Kang Li et al. · 2025 · arXiv.org · other · overall 3/3

<https://doi.org/10.48550/arxiv.2506.18096>

**Key finding.** A taxonomy of Deep Research agent architectures (static vs. dynamic workflows, single- vs. multi-agent) with a critical evaluation of current benchmarks identifying restricted external-knowledge access, sequential-execution inefficiencies, and metric-objective misalignment.

**Why it made the cut.** closely-related · selected by score · strongest on C4 benchmark construction (3/3). Synthesizes the field's own benchmark critique, which the brief explicitly wants surfaced (question 3), and provides the taxonomy needed to compare agentic designs on like terms.

**Why it matters here.** Its critique of benchmark-metric misalignment directly bears on question 3 — how evaluation sets are built and what their numbers can and cannot support — and should reshape how this scan reads any single benchmark's headline number.

**Method.** Systematic examination and roadmap paper reviewing information-acquisition strategies, tool-use frameworks (code execution, multimodal input, MCP), and existing benchmarks; abstract-only for methodological detail.

**Limitations.**

- narrative/taxonomic review rather than new empirical evidence
- abstract does not give quantitative findings to weigh against specific systems

<sub>selected: score · criteria: C1 1/3 · C2 2/3 · C3 1/3 · C4 3/3 · C5 2/3 · flags: review · verified 2026-08-26 via arxiv</sub>

## 5. PaSa: An LLM Agent for Comprehensive Academic Paper Search

Yichen He, Guanhua Huang, Peiyuan Feng, Yuan Lin et al. · 2025 · Annual Meeting of the Association for Computational Linguistics · experimental · overall 3/3

<https://doi.org/10.48550/arxiv.2501.10120>

**Key finding.** PaSa-7B surpasses the best Google-based baseline by 37.78% in recall@20 and 39.90% in recall@50 on RealScholarQuery, and beats PaSa-GPT-4o by 30.36% in recall and 4.25% in precision.

**Why it made the cut.** design-changing · selected by score · strongest on C1 baseline recall ceiling (3/3). A landmark system paper directly measuring the baseline-vs-agent recall gap the brief's first two questions are built around, with detailed benchmark construction.

**Why it matters here.** Establishes the single-query database (Google/Google Scholar) recall ceiling explicitly and quantifies the gap an agentic crawl-and-select design closes, anchoring question 1 and 2 with real numbers.

**Method.** RL-trained autonomous paper-search agent that invokes search tools, reads papers, and selects references; trained on synthetic AutoScholarQuery (35k queries) and evaluated on newly built RealScholarQuery.

**Limitations.**

- trained on synthetic queries sourced from top-tier AI conference papers, so generalization to other scientific fields is untested
- gain is reported for the system as a whole rather than cleanly isolating which agentic move (crawling vs. reference selection) drives it

<sub>selected: score · criteria: C1 3/3 · C2 2/3 · C3 1/3 · C4 3/3 · C5 0/3 · flags: methods_paper · verified 2026-08-26 via openalex, arxiv</sub>

## 6. LitSearch: A Retrieval Benchmark for Scientific Literature Search

Anirudh Ajith, Mengzhou Xia, Alexis Chevalier, Tanya Goyal et al. · 2024 · Conference on Empirical Methods in Natural Language Processing · experimental · overall 3/3

<https://doi.org/10.48550/arxiv.2407.18940>

**Key finding.** LitSearch finds a 24.8-point absolute recall@5 gap between BM25 and state-of-the-art dense retrievers, LLM-based reranking adds a further 4.4% over the best dense retriever, and commercial search engines lag the best dense retriever by 32 points.

**Why it made the cut.** foundational · selected by score · strongest on C1 baseline recall ceiling (3/3). Answers decision 1 (recall ceiling) and decision 3 (benchmark construction) directly with numbers, making it foundational to the scan's core questions.

**Why it matters here.** Directly establishes the baseline recall ceiling (BM25 vs dense) the scan needs to anchor any reported agentic improvement against, and its construction methodology is a template for benchmark quality (C4).

**Method.** 597 realistic literature-search queries built from GPT-4-generated questions on inline-citation paragraphs plus author-written queries about their own recent papers, expert-reviewed; benchmarks retrieval and reranking models.

**Limitations.**

- Restricted to ML/NLP literature
- Queries are partly LLM-generated, which may not fully capture real researcher intents

<sub>selected: score · criteria: C1 3/3 · C2 0/3 · C3 3/3 · C4 3/3 · C5 0/3 · verified 2026-08-26 via openalex, arxiv</sub>

## 7. Towards Recursive Self-Evolving Agentic Literature Retrieval

Yuwen Du, Tian Jin, Jing Kang, Xianghe Pang et al. · 2026 · arXiv · experimental · overall 3/3

<https://doi.org/10.48550/arxiv.2605.14306>

**Key finding.** PaSaMaster achieves a 16.5x higher F1-score than Google Scholar and a 37.8% higher F1-score than GPT-5.2 at about 1% of the cost, reducing source hallucination from 32.66% to zero, across 38 disciplines in PaSaMaster-Bench.

**Why it made the cut.** design-changing · selected by score · strongest on C2 agentic mechanism gain (3/3). Provides the sharpest example of an agentic literature-retrieval system quantifying gain over baseline database search and attributing it to specific mechanisms.

**Why it matters here.** Directly quantifies the agentic gain over baseline single-query search (Google Scholar) attributable to specific mechanisms (self-evolving retrieval, verified-paper ranking), exactly the comparison decisions 1 and 2 need.

**Method.** Recursive self-evolving agentic retrieval system with self-evolving intent refinement, hallucination-free ranking over verified papers, and planning/retrieval separation between frontier and lightweight LLMs; evaluated on PaSaMaster-Bench.

**Limitations.**

- Preprint with 0 citations; gains not yet independently verified
- Benchmark (PaSaMaster-Bench) construction details not given in the abstract

<sub>selected: score · criteria: C1 2/3 · C2 3/3 · C3 2/3 · C4 1/3 · C5 0/3 · flags: methods_paper · verified 2026-08-26 via openalex, arxiv</sub>

## 8. LLM-guided Hierarchical Search for End-to-end Reasoning Intensive Retrieval

Nilesh Gupta, Wei-Cheng Chang, N. Bui, Cho-Jui Hsieh et al. · 2025 · no venue · experimental · overall 3/3

<https://arxiv.org/abs/2510.13217>

**Key finding.** LATTICE, an LLM-guided hierarchical search index with no embedding model at search time, matches the best fine-tuned ensemble baseline (46.7 nDCG@10) on the reasoning-intensive BRIGHT benchmark, and a lightweight ensemble reaches 49.1.

**Why it made the cut.** plan-influencing · selected by backfill · strongest on C3 retrieval/reranking method (3/3). Directly informs C3 (retrieval/reranking method underlying literature-search agents) and the recall-ceiling question by quantifying where embedding retrieval fails.

**Why it matters here.** Shows embedding-based top-k retrieval genuinely caps recall on reasoning-intensive queries and that removing the embedder in favor of direct LLM-guided traversal recovers it, directly bearing on what retrieval/reranking substrate an agentic literature-search system should use.

**Method.** Proposes top-down LLM-guided index construction over multi-level document summaries plus calibrated path-aggregated traversal; evaluated on BRIGHT, NQ, SciFact, SciDocs against embedding+rerank baselines.

**Limitations.**

- evaluated on general reasoning-intensive IR benchmarks (BRIGHT) rather than agentic scientific-literature-search benchmarks specifically
- sliding-window reranking beats it at low token budgets, so the advantage is budget-dependent

<sub>selected: backfill · criteria: C1 2/3 · C2 1/3 · C3 3/3 · C4 0/3 · C5 2/3 · flags: methods_paper · verified 2026-08-26 via arxiv, s2</sub>

## 9. Multi-Turn Agentic Scientific Literature Search via Workflow Induction

Jisen Li, Bingxuan Li, Nanyi Jiang, Xuying Ning et al. · 2026 · arXiv · experimental · overall 3/3

<https://doi.org/10.48550/arxiv.2607.00597>

**Key finding.** PaperPilot-9B raises Hit@5 from 58.0 to 77.0, MRR from 47.5 to 59.4, and nDCG@10 from 26.8 to 32.5 over a base toolset agent, while cutting workflow execution errors from 9.5% to 0%, by framing literature search as an executable, user-refinable DAG of operators (keyword search, citation expansion, filtering, reranking, evidence extraction).

**Why it made the cut.** design-changing · selected by backfill · strongest on C1 baseline recall ceiling (2/3). A scientific-literature-search agent with an explicit, editable workflow (including citation expansion) and concrete quantitative gains over a baseline toolset agent — squarely the system design and mechanism-attribution the brief is built around.

**Why it matters here.** A directly on-domain system with a clean baseline-to-agentic-workflow delta (Hit@5 +19, MRR +11.9, nDCG@10 +5.7) that decomposes the workflow into named operators including citation expansion — giving Q2 a concrete, attributable mechanism rather than an undifferentiated system-level gain.

**Method.** Supervised workflow imitation plus preference optimization over controlled workflow corruptions, trained on Qwen3.5-9B; evaluated in multi-turn interaction against a base toolset agent.

**Limitations.**

- Abstract does not report how the evaluation queries/relevance labels were constructed
- gains are for one base model family (Qwen3.5-9B) and may not generalize to other backbones

<sub>selected: backfill · criteria: C1 2/3 · C2 2/3 · C3 2/3 · C4 1/3 · C5 0/3 · flags: methods_paper · verified 2026-08-26 via openalex, arxiv</sub>

## 10. AI's Capability in Assisting Scientific Research in Physics, Astrophysics, and Cosmology I: Literature Review

Anamaria Hell, Kateryna Vovk, Veena Krishnaraj, Jia Liu et al. · 2026 · arXiv · experimental · overall 3/3

<https://doi.org/10.48550/arxiv.2607.25672>

**Key finding.** Across eight expert-designed literature-review projects in physics/astro/cosmology, overlap between human- and AI-selected references was under 6%, and 64% of mid-2025 AI-generated real-paper citations had at least one incorrect metadata field.

**Why it made the cut.** contradicting · selected by contradicting · strongest on C5 gain replication failure (3/3). The clearest evidence in the shortlist that agentic literature-search gains do not yet hold up against expert human search, which is exactly what question 4 asks the scan to find.

**Why it matters here.** Directly contradicts the premise that current agentic literature-search systems reliably match expert search, quantifying both a low overlap ceiling and a high metadata-error rate that any reported 'gain' claim must be checked against.

**Method.** Controlled human-AI comparison study across eight research projects, comparing expert literature selections against ChatGPT-4o, ChatGPT Deep Research, and Gemini outputs, with a follow-up single-project test of a 2026 model.

**Limitations.**

- applied domain (astrophysics/cosmology) rather than a CS benchmark of agent design itself
- small sample (eight projects, one project for the 2026-model follow-up)

<sub>selected: contradicting · criteria: C1 1/3 · C2 0/3 · C3 0/3 · C4 2/3 · C5 3/3 · flags: contradicts · verified 2026-08-26 via openalex, arxiv</sub>

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

- [Language agents achieve superhuman synthesis of scientific knowledge](https://doi.org/10.48550/arxiv.2409.13740) (2024) — overall 3/3
- [Deep Research: A Survey of Autonomous Research Agents](https://doi.org/10.48550/arxiv.2508.12752) (2025) — overall 3/3
- [Open-Source Agentic Hybrid RAG Framework for Scientific Literature Review](https://doi.org/10.48550/arxiv.2508.05660) (2025) — overall 3/3
- [OpenScholar: Synthesizing Scientific Literature with Retrieval-augmented LMs](https://doi.org/10.48550/arxiv.2411.14199) (2024) — overall 3/3
- [Search-Time Data Contamination](https://doi.org/10.48550/arxiv.2508.13180) (2025) — overall 3/3
