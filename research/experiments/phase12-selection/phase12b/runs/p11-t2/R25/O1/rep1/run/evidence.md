# Evidence scan — p11-t2

Run `/Users/nabergoj/Projects/research-scan/research/experiments/phase12-selection/phase12b/runs/p11-t2/R25/O1/rep1/run` · brief `/Users/nabergoj/Projects/research-scan/research/experiments/phase12-selection/phase12b/runs/p11-t2/R25/O1/rep1/run/brief.md` · rendered 2026-08-26

| # | Paper | Year | Venue | Evidence | Verified |
|---|---|---|---|---|---|
| 1 | [When to use Graphs in RAG: A Comprehensive Analysis for Graph Retrieval-Augmented Generation](https://doi.org/10.48550/arxiv.2506.05690) · 10.48550/arxiv.2506.05690 | 2025 | arXiv.org | experimental | yes |
| 2 | [BrowseComp-Plus: A More Fair and Transparent Evaluation Benchmark of Deep-Research Agent](https://doi.org/10.48550/arxiv.2508.06600) · 10.48550/arxiv.2508.06600 | 2025 | arXiv (Cornell University) | experimental | yes |
| 3 | [Deep Research Agents: A Systematic Examination And Roadmap](https://doi.org/10.48550/arxiv.2506.18096) · 10.48550/arxiv.2506.18096 | 2025 | arXiv.org | other | yes |
| 4 | [BRIGHT: A Realistic and Challenging Benchmark for Reasoning-Intensive Retrieval](https://doi.org/10.48550/arxiv.2407.12883) · 10.48550/arxiv.2407.12883 | 2024 | International Conference on Learning Representations | experimental | yes |
| 5 | [Diagnosing Search Behavior and Failure Modes in Long-Horizon Search Agents](https://doi.org/10.48550/arxiv.2608.01913) · 10.48550/arxiv.2608.01913 | 2026 | arXiv | experimental | yes |
| 6 | [Projecting BrowseComp-Plus onto ClimbMix: Toward More Realistic Corpora for Agentic Search](https://arxiv.org/abs/2608.20317) | 2026 | — | experimental | yes |
| 7 | [Structurally-bounded Agentic Graph Exploration for Evidence-Grounded Scholarly DeepSearch](https://doi.org/10.48550/arxiv.2608.24809) · 10.48550/arxiv.2608.24809 | 2026 | arXiv | experimental | yes |
| 8 | [Towards Recursive Self-Evolving Agentic Literature Retrieval](https://doi.org/10.48550/arxiv.2605.14306) · 10.48550/arxiv.2605.14306 | 2026 | arXiv | experimental | yes |
| 9 | [LLM-guided Hierarchical Search for End-to-end Reasoning Intensive Retrieval](https://arxiv.org/abs/2510.13217) | 2025 | — | experimental | yes |
| 10 | [PaSa: An LLM Agent for Comprehensive Academic Paper Search](https://doi.org/10.48550/arxiv.2501.10120) · 10.48550/arxiv.2501.10120 | 2025 | Annual Meeting of the Association for Computational Linguistics | experimental | yes |

## 1. When to use Graphs in RAG: A Comprehensive Analysis for Graph Retrieval-Augmented Generation

Zhishang Xiang, Chuan-Yu Wu, Qinggang Zhang, Shengyuan Chen et al. · 2025 · arXiv.org · experimental · overall 3/3

<https://doi.org/10.48550/arxiv.2506.05690>

**Key finding.** GraphRAG frequently underperforms vanilla RAG on real-world tasks, and the proposed GraphRAG-Bench (fact retrieval, complex reasoning, contextual summarization, creative generation, full-pipeline evaluation) is used to identify the specific conditions under which graph structure actually helps.

**Why it made the cut.** contradicting · selected by score · strongest on C2 agentic mechanism gain (3/3). A benchmark-driven finding that graph-based retrieval frequently fails to beat vanilla RAG, directly contradicting the brief's premise about agentic (graph-traversal) gains being real.

**Why it matters here.** Directly tests the premise that graph-structure retrieval (the CS analogue of citation-graph traversal) reliably beats simpler retrieval, and finds it often does not -- exactly the kind of gain-does-not-hold-up evidence the brief's decision 4 is asking for.

**Method.** New benchmark spanning tasks of increasing difficulty with systematic pipeline evaluation from graph construction through retrieval to generation, comparing GraphRAG variants against vanilla RAG.

**Limitations.**

- General knowledge-graph RAG tasks rather than citation-graph traversal over scientific literature specifically
- Findings are about conceptual/entity graphs, which may not generalize to citation graphs

<sub>selected: score · criteria: C1 1/3 · C2 3/3 · C3 2/3 · C4 3/3 · C5 3/3 · flags: contradicts, methods_paper · verified 2026-08-26 via openalex, arxiv</sub>

## 2. BrowseComp-Plus: A More Fair and Transparent Evaluation Benchmark of Deep-Research Agent

Zijian Chen, Xueguang Ma, Shengyao Zhuang, Ping Nie et al. · 2025 · arXiv (Cornell University) · experimental · overall 3/3

<https://doi.org/10.48550/arxiv.2508.06600>

**Key finding.** On a fixed, human-verified corpus, Search-R1 with BM25 retrieval achieves only 3.86% accuracy while GPT-5 with BM25 reaches 55.9%, and GPT-5 paired with a Qwen3-Embedding-8B dense retriever reaches 70.1% accuracy with fewer search calls.

**Why it made the cut.** foundational · selected by score · strongest on C1 baseline recall ceiling (3/3). The central controlled benchmark disentangling retriever from agent for deep-research evaluation, directly serving the baseline-ceiling, retrieval-method, and benchmark-construction questions.

**Why it matters here.** Gives the field's clearest controlled anchor for the baseline recall/accuracy ceiling of single-query retrieval (BM25 vs dense) versus agent capability, exactly the reference point questions 1 and 3 need, and later work shows its curated corpus can itself inflate apparent recall.

**Method.** Benchmark derived from BrowseComp using a fixed, curated corpus with human-verified supporting documents and mined hard negatives, enabling controlled disentanglement of agent capability from retriever quality across multiple deep-research systems.

**Limitations.**

- Corpus is curated from the benchmark's own queries plus mined negatives, which a follow-up projection study shows may inflate measured recall relative to a more realistic corpus
- Focused on BrowseComp-style multi-hop questions, may not generalize to broader literature-search tasks

<sub>selected: score · criteria: C1 3/3 · C2 1/3 · C3 2/3 · C4 3/3 · C5 2/3 · flags: methods_paper · verified 2026-08-26 via openalex, arxiv</sub>

## 3. Deep Research Agents: A Systematic Examination And Roadmap

Yuxuan Huang, Yihang Chen, Haozhen Zhang, Kang Li et al. · 2025 · arXiv.org · other · overall 3/3

<https://doi.org/10.48550/arxiv.2506.18096>

**Key finding.** Proposes a taxonomy of Deep Research agent architectures (static vs dynamic workflows, single- vs multi-agent) and identifies key benchmark limitations: restricted access to external knowledge, sequential execution inefficiencies, and misalignment between evaluation metrics and practical objectives.

**Why it made the cut.** foundational · selected by score · strongest on C4 benchmark construction (3/3). A comprehensive survey covering system design, benchmark critique, and mechanism taxonomy that maps directly onto the brief's four ordered questions.

**Why it matters here.** Maps the design space (which agentic moves and architectures exist) and names specific ways current benchmarks fail to support fair comparison, directly structuring how the project should sequence its own evaluation of mechanisms and benchmark choices.

**Method.** Abstract-only; narrative/systematic review of information-acquisition strategies (API vs browser-based), tool-use frameworks, and planning-strategy taxonomies for Deep Research agents, with a maintained repository of related work.

**Limitations.**

- Abstract-only, breadth over empirical depth
- No new quantitative findings validated within this abstract, primarily taxonomic

<sub>selected: score · criteria: C1 1/3 · C2 2/3 · C3 2/3 · C4 3/3 · C5 2/3 · flags: review · verified 2026-08-26 via arxiv</sub>

## 4. BRIGHT: A Realistic and Challenging Benchmark for Reasoning-Intensive Retrieval

Hongjin Su, Howard Yen, Mengzhou Xia, Weijia Shi et al. · 2024 · International Conference on Learning Representations · experimental · overall 3/3

<https://doi.org/10.48550/arxiv.2407.12883>

**Key finding.** The leading MTEB retriever (SFR-Embedding-Mistral, 59.0 nDCG@10 on MTEB) scores only 18.3 nDCG@10 on BRIGHT's 1,384 reasoning-intensive real-world queries, while adding explicit query reasoning improves retrieval by up to 12.2 points.

**Why it made the cut.** foundational · selected by score · strongest on C1 baseline recall ceiling (3/3). The widely-cited benchmark quantifying how badly standard single-query retrieval fails on reasoning-heavy queries, directly setting the baseline decision 1 asks for.

**Why it matters here.** Gives the sharpest quantified evidence for decision 1: the recall ceiling of standard single-query embedding search collapses (59.0 -> 18.3 nDCG@10) once queries require reasoning, the exact baseline number against which agentic gains must be measured.

**Method.** New retrieval benchmark of naturally-occurring, reasoning-intensive queries across economics, psychology, mathematics, and coding, evaluated against state-of-the-art embedding and retrieval models.

**Limitations.**

- Domains are economics/psychology/math/coding rather than scientific-literature search specifically
- Does not evaluate agentic (multi-step) retrieval systems directly, only single-query retrievers

<sub>selected: score · criteria: C1 3/3 · C2 1/3 · C3 2/3 · C4 3/3 · C5 1/3 · flags: methods_paper · verified 2026-08-26 via openalex, arxiv</sub>

## 5. Diagnosing Search Behavior and Failure Modes in Long-Horizon Search Agents

Qi Liu, Jiaxin Mao, Fengbin Zhu, Tat-Seng Chua · 2026 · arXiv · experimental · overall 3/3

<https://doi.org/10.48550/arxiv.2608.01913>

**Key finding.** Across six agents on BrowseComp-Plus and BrowseComp, answer accuracy correlates more with cumulative retrieval recall and evidence quality than with the number of searches, and the best agents issue far fewer redundant reformulated queries.

**Why it made the cut.** plan-influencing · selected by score · strongest on C2 agentic mechanism gain (3/3). Directly diagnoses which agentic behaviors (reformulation, continued searching) carry measured gains and where extra search effort fails to pay off, central to the brief's second and fourth questions.

**Why it matters here.** Shows that 'more agentic search' is not what drives quality — retrieval recall and evidence use are — which reframes how the project should attribute gains to specific agentic moves and design stopping criteria rather than assuming effort itself is the mechanism.

**Method.** Trajectory-level diagnosis using human-annotated document relevance judgments, comparing six long-horizon search agents on BrowseComp-Plus with retrieval model/harness held fixed, validated on BrowseComp with an open-web API.

**Limitations.**

- Evaluated on two closely related benchmarks (BrowseComp-Plus, BrowseComp)
- Retrieval model and harness held fixed, so findings may not transfer to other retrievers or search APIs

<sub>selected: score · criteria: C1 1/3 · C2 3/3 · C3 1/3 · C4 1/3 · C5 3/3 · flags: contradicts · verified 2026-08-26 via openalex, arxiv</sub>

## 6. Projecting BrowseComp-Plus onto ClimbMix: Toward More Realistic Corpora for Agentic Search

Sahel Sharifymoghaddam, Lin Gu, Yijun Ge, Jimmy Lin · 2026 · no venue · experimental · overall 3/3

<https://arxiv.org/abs/2608.20317>

**Key finding.** Relocating BrowseComp-Plus evidence to the independently-built ClimbMix corpus drops evidence recall from 84.3% to 21.4% and answer accuracy by five points despite the agent issuing 63% more search calls, across 57 fully grounded projected questions.

**Why it made the cut.** contradicting · selected by score · strongest on C4 benchmark construction (3/3). The clearest demonstration in the shortlist that a reported agentic-search gain shrinks sharply under a different, less curated corpus, directly answering the brief's fourth question.

**Why it matters here.** Directly demonstrates that agentic search gains measured on a benchmark-specific curated corpus do not hold when evidence is relocated to an independently-built, more realistic corpus — exactly the replication failure the brief asks the scan to surface, and a caution on how benchmark construction inflates reported recall.

**Method.** Dataset-agnostic projection pipeline that decomposes benchmark questions into atomic reasoning hops and grounds each hop in a new corpus (ClimbMix, 553M documents), retaining only questions verified by automatic checks, an independent agent, and human review.

**Limitations.**

- Resulting benchmark is small, only 57 fully grounded questions after strict verification
- Limited to BrowseComp-Plus-derived questions projected onto a single substitute corpus (ClimbMix)

<sub>selected: score · criteria: C1 1/3 · C2 1/3 · C3 1/3 · C4 3/3 · C5 3/3 · flags: contradicts, methods_paper · verified 2026-08-26 via arxiv, s2</sub>

## 7. Structurally-bounded Agentic Graph Exploration for Evidence-Grounded Scholarly DeepSearch

Rima Hazra, Sayan Layek, Somnath Banerjee, Soumen Chakrabarti et al. · 2026 · arXiv · experimental · overall 3/3

<https://doi.org/10.48550/arxiv.2608.24809>

**Key finding.** Crase, using a single seed query, bounded 1.5-hop citation-graph expansion, entailment-based edge pruning, and recency-aware random-walk ranking, outperforms deep research agents built on proprietary models by up to 3x recall@50 at roughly a third of the cost on LitSearch and a second benchmark over a 500K-paper arXiv corpus.

**Why it made the cut.** design-changing · selected by score · strongest on C2 agentic mechanism gain (3/3). Directly answers which agentic mechanism (citation-graph traversal) carries the gain and shows unbounded agentic search is not necessary to beat it, core to questions 2 and 4.

**Why it matters here.** Directly tests the premise that open-ended agentic search loops are needed: a bounded citation-graph-traversal design beats them on recall at lower cost, isolating graph traversal as the mechanism that carries the gain rather than unrestricted iteration.

**Method.** Bounded, inspectable pipeline: one search-engine query for seed papers, 1.5-hop citation expansion, entailment-filtered pruning, recency-aware random-walk reranking; compared against open-ended deep research agents on a 500K-document arXiv corpus.

**Limitations.**

- Evaluated on LitSearch and only one further benchmark, generalization elsewhere untested
- Comparison to proprietary deep-research agents may not fully control for prompting/tool differences

<sub>selected: score · criteria: C1 1/3 · C2 3/3 · C3 3/3 · C4 0/3 · C5 2/3 · flags: contradicts, methods_paper · verified 2026-08-26 via arxiv</sub>

## 8. Towards Recursive Self-Evolving Agentic Literature Retrieval

Yuwen Du, Tian Jin, Jing Kang, Xianghe Pang et al. · 2026 · arXiv · experimental · overall 3/3

<https://doi.org/10.48550/arxiv.2605.14306>

**Key finding.** PaSaMaster achieves a 16.5x higher F1-score than Google Scholar and a 37.8% higher F1-score than GPT-5.2 at about 1% of the cost, reducing citation hallucination from 32.66% to zero, across 38 disciplines in PaSaMaster-Bench.

**Why it made the cut.** design-changing · selected by score · strongest on C1 baseline recall ceiling (3/3). Directly reports a baseline-vs-agentic-system recall/F1 comparison and attributes gains to a specific iterative retrieval mechanism, hitting decisions 1 and 2 head-on.

**Why it matters here.** Directly anchors decision 1 with a quantified baseline comparison (Google Scholar) and attributes the gain to self-evolving retrieval refinement, giving a concrete recall-ceiling and mechanism data point the rest of the scan can be measured against.

**Method.** Recursive self-evolving retrieval agent separating intent-understanding (frontier LLM) from retrieval/scoring (lightweight models over verified corpora), benchmarked against Google Scholar and GPT-5.2 on a 38-discipline benchmark.

**Limitations.**

- Benchmark (PaSaMaster-Bench) construction, relevance labeling, and contamination controls not detailed in the abstract
- Comparator (Google Scholar F1) may not be a like-for-like single-query database/embedding baseline

<sub>selected: score · criteria: C1 3/3 · C2 2/3 · C3 2/3 · C4 1/3 · C5 0/3 · flags: methods_paper · verified 2026-08-26 via openalex, arxiv</sub>

## 9. LLM-guided Hierarchical Search for End-to-end Reasoning Intensive Retrieval

Nilesh Gupta, Wei-Cheng Chang, N. Bui, Cho-Jui Hsieh et al. · 2025 · no venue · experimental · overall 3/3

<https://arxiv.org/abs/2510.13217>

**Key finding.** LATTICE, an LLM-guided hierarchical search index requiring no embedding model at search time, achieves 46.7 nDCG@10 on the reasoning-intensive BRIGHT benchmark — matching the best fine-tuned ensemble — and 49.1 with a lightweight ensemble variant.

**Why it made the cut.** plan-influencing · selected by backfill · strongest on C3 retrieval/reranking method (3/3). A retrieval architecture directly addressing the underlying retrieval/reranking question and critiquing the brittleness of query-reformulation-based agentic fixes.

**Why it matters here.** Shows that both standard embedding-based top-k retrieval and query-side agentic fixes (rewriting, agentic loops) remain brittle for reasoning-intensive queries, and that a different retrieval architecture (LLM-guided graph/hierarchical traversal) can match or beat them, directly bearing on which retrieval technique should underlie an agentic literature-search system.

**Method.** Top-down LLM-guided construction of a hierarchical index from multi-level document summaries, plus calibrated path-aggregated LLM traversal with cross-branch reference nodes; evaluated on BRIGHT, NQ, SciFact, and SciDocs.

**Limitations.**

- Primary evaluation is on BRIGHT (general reasoning-intensive IR), only secondarily on scientific corpora (SciFact, SciDocs)
- Traversal is compute/token-intensive and the tradeoff against reranking is only partially characterized

<sub>selected: backfill · criteria: C1 2/3 · C2 2/3 · C3 3/3 · C4 0/3 · C5 1/3 · flags: contradicts, methods_paper · verified 2026-08-26 via arxiv, s2</sub>

## 10. PaSa: An LLM Agent for Comprehensive Academic Paper Search

Yichen He, Guanhua Huang, Peiyuan Feng, Yuan Lin et al. · 2025 · Annual Meeting of the Association for Computational Linguistics · experimental · overall 3/3

<https://doi.org/10.48550/arxiv.2501.10120>

**Key finding.** PaSa-7B surpasses the best Google-based baseline (Google with GPT-4o paraphrasing) by 37.78% in recall@20 and 39.90% in recall@50 on the real-world RealScholarQuery benchmark.

**Why it made the cut.** foundational · selected by backfill · strongest on C4 benchmark construction (3/3). A foundational agentic academic-search system with an explicit dual-benchmark construction, widely cited and central to how the field frames the recall-ceiling question.

**Why it matters here.** One of the earliest strong reference points for how much an agentic paper-search loop can beat conventional search baselines, and its dual synthetic/real benchmark construction is a template the project should compare newer benchmark designs against.

**Method.** RL-trained LLM agent that searches, reads, and selects references, trained on a synthetic 35k-query AutoScholarQuery dataset and evaluated on a new real-world RealScholarQuery benchmark against several search-engine and LLM baselines.

**Limitations.**

- Baselines conflate different underlying LLMs (GPT-4o, o1) with the search mechanism, so the source of the gain is not isolated
- Trained mainly on synthetic queries, which may not reflect the true distribution of real scholarly queries

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

- [Multi-Turn Agentic Scientific Literature Search via Workflow Induction](https://doi.org/10.48550/arxiv.2607.00597) (2026) — overall 3/3
- [Search-Time Contamination in Deep Research Agents: Measuring Performance Inflation in Public Benchmark Evaluation](https://doi.org/10.48550/arxiv.2606.05241) (2026) — overall 3/3
- [Agents-K1: Towards Agent-native Knowledge Orchestration](https://doi.org/10.48550/arxiv.2606.13669) (2026) — overall 3/3
- [Deep Research Bench: Evaluating AI Web Research Agents](https://doi.org/10.48550/arxiv.2506.06287) (2025) — overall 3/3
- [AI's Capability in Assisting Scientific Research in Physics, Astrophysics, and Cosmology I: Literature Review](https://doi.org/10.48550/arxiv.2607.25672) (2026) — overall 3/3
