# Evidence scan — p11-t2

Run `/Users/nabergoj/Projects/research-scan/research/experiments/phase12-selection/phase12b/runs/p11-t2/R25/O1/rep3/run` · brief `/Users/nabergoj/Projects/research-scan/research/experiments/phase12-selection/phase12b/runs/p11-t2/R25/O1/rep3/run/brief.md` · rendered 2026-08-26

| # | Paper | Year | Venue | Evidence | Verified |
|---|---|---|---|---|---|
| 1 | [When to use Graphs in RAG: A Comprehensive Analysis for Graph Retrieval-Augmented Generation](https://doi.org/10.48550/arxiv.2506.05690) · 10.48550/arxiv.2506.05690 | 2025 | arXiv.org | computational | yes |
| 2 | [Diagnosing Search Behavior and Failure Modes in Long-Horizon Search Agents](https://doi.org/10.48550/arxiv.2608.01913) · 10.48550/arxiv.2608.01913 | 2026 | arXiv | experimental | yes |
| 3 | [BrowseComp-Plus: A More Fair and Transparent Evaluation Benchmark of Deep-Research Agent](https://doi.org/10.48550/arxiv.2508.06600) · 10.48550/arxiv.2508.06600 | 2025 | arXiv (Cornell University) | experimental | yes |
| 4 | [Projecting BrowseComp-Plus onto ClimbMix: Toward More Realistic Corpora for Agentic Search](https://arxiv.org/abs/2608.20317) | 2026 | — | experimental | yes |
| 5 | [Towards Recursive Self-Evolving Agentic Literature Retrieval](https://doi.org/10.48550/arxiv.2605.14306) · 10.48550/arxiv.2605.14306 | 2026 | arXiv | experimental | yes |
| 6 | [PaSa: An LLM Agent for Comprehensive Academic Paper Search](https://doi.org/10.48550/arxiv.2501.10120) · 10.48550/arxiv.2501.10120 | 2025 | Annual Meeting of the Association for Computational Linguistics | experimental | yes |
| 7 | [Deep Research Agents: A Systematic Examination And Roadmap](https://doi.org/10.48550/arxiv.2506.18096) · 10.48550/arxiv.2506.18096 | 2025 | arXiv.org | other | yes |
| 8 | [Structurally-bounded Agentic Graph Exploration for Evidence-Grounded Scholarly DeepSearch](https://doi.org/10.48550/arxiv.2608.24809) · 10.48550/arxiv.2608.24809 | 2026 | arXiv | experimental | yes |
| 9 | [LLM-guided Hierarchical Search for End-to-end Reasoning Intensive Retrieval](https://arxiv.org/abs/2510.13217) | 2025 | — | experimental | yes |
| 10 | [Language agents achieve superhuman synthesis of scientific knowledge](https://doi.org/10.48550/arxiv.2409.13740) · 10.48550/arxiv.2409.13740 | 2024 | arXiv (Cornell University) | experimental | yes |

## 1. When to use Graphs in RAG: A Comprehensive Analysis for Graph Retrieval-Augmented Generation

Zhishang Xiang, Chuan-Yu Wu, Qinggang Zhang, Shengyuan Chen et al. · 2025 · arXiv.org · computational · overall 3/3

<https://doi.org/10.48550/arxiv.2506.05690>

**Key finding.** GraphRAG frequently underperforms vanilla RAG on many real-world tasks; GraphRAG-Bench systematically identifies the conditions under which graph structure does and does not provide measurable benefit across fact retrieval, complex reasoning, summarization, and creative generation.

**Why it made the cut.** contradicting · selected by score · strongest on C2 agentic mechanism gain (3/3). Empirically shows the graph-traversal mechanism named in the brief's decision 2 often fails to beat vanilla retrieval, via the same underlying operation (stored-graph neighbor retrieval) that citation-graph traversal in literature search relies on — the clearest available evidence against the premise that agentic graph mechanisms reliably add gain.

**Why it matters here.** Citation-graph traversal in literature-search agents is mechanistically the same operation as knowledge-graph traversal in GraphRAG — both retrieve neighboring nodes via stored graph relations rather than re-querying — so this benchmark's finding that graph traversal often fails to beat vanilla retrieval transfers directly to decision 2's mechanism question and decision 4's replication-failure search.

**Method.** Introduces GraphRAG-Bench, a benchmark spanning the full GraphRAG pipeline (construction, retrieval, generation) with tasks of increasing difficulty; systematically compares GraphRAG against vanilla RAG.

**Limitations.**

- evaluated on general RAG tasks, not scientific-literature corpora specifically
- graph construction quality may vary by domain, limiting how directly the failure transfers to citation graphs built from papers

<sub>selected: score · criteria: C1 2/3 · C2 3/3 · C3 2/3 · C4 3/3 · C5 3/3 · flags: contradicts, methods_paper · verified 2026-08-26 via openalex, arxiv</sub>

## 2. Diagnosing Search Behavior and Failure Modes in Long-Horizon Search Agents

Qi Liu, Jiaxin Mao, Fengbin Zhu, Tat-Seng Chua · 2026 · arXiv · experimental · overall 3/3

<https://doi.org/10.48550/arxiv.2608.01913>

**Key finding.** Across six agents on BrowseComp-Plus and BrowseComp, answer accuracy correlates with cumulative retrieval recall far more than with number of searches or context consumed, and top agents issue fewer redundant queries despite useful evidence often appearing early.

**Why it made the cut.** plan-influencing · selected by score · strongest on C2 agentic mechanism gain (3/3). A trajectory-level diagnosis that separates retrieval from utilization failure and shows search effort is only weakly tied to quality, exactly the kind of gain-scrutiny the brief's question 4 asks for.

**Why it matters here.** Directly undercuts the assumption that more search effort drives agentic gains: it shows the gain tracks evidence quality, not search volume, which reframes what our C2 mechanism analysis should measure (stopping criteria and evidence selection, not query count).

**Method.** Trajectory-level diagnosis using human-annotated document-level relevance judgments, decomposing failures into retrieval gaps vs utilization gaps, retrieval model and harness held fixed across six agents.

**Limitations.**

- evaluated on two benchmarks only (BrowseComp-Plus, BrowseComp)
- diagnostic study, not a new system or benchmark

<sub>selected: score · criteria: C1 2/3 · C2 3/3 · C3 1/3 · C4 1/3 · C5 3/3 · flags: contradicts · verified 2026-08-26 via openalex, arxiv</sub>

## 3. BrowseComp-Plus: A More Fair and Transparent Evaluation Benchmark of Deep-Research Agent

Zijian Chen, Xueguang Ma, Shengyao Zhuang, Ping Nie et al. · 2025 · arXiv (Cornell University) · experimental · overall 3/3

<https://doi.org/10.48550/arxiv.2508.06600>

**Key finding.** On a fixed, human-verified corpus, Search-R1 with BM25 achieves only 3.86% accuracy while GPT-5 reaches 55.9%, and pairing GPT-5 with a stronger embedding retriever raises accuracy to 70.1% with fewer search calls.

**Why it made the cut.** foundational · selected by score · strongest on C1 baseline recall ceiling (3/3). The reference benchmark for disentangling retrieval-method contribution from agent design in deep research systems, directly answering the brief's baseline-ceiling and benchmark-construction questions.

**Why it matters here.** Sets the canonical fair baseline for comparing retriever choice against agentic reasoning improvements, and its corpus/labeling method is the construction standard against which other benchmarks in this space (and their contamination controls) should be judged.

**Method.** New benchmark derived from BrowseComp using a fixed curated corpus with human-verified supporting documents and mined hard negatives, enabling controlled disentanglement of retriever from agent.

**Limitations.**

- corpus assembled per-query from supporting docs plus mined negatives, which later work shows may inflate ease relative to a realistic corpus
- single benchmark family (BrowseComp derivative)

<sub>selected: score · criteria: C1 3/3 · C2 1/3 · C3 2/3 · C4 3/3 · C5 1/3 · flags: methods_paper · verified 2026-08-26 via openalex, arxiv</sub>

## 4. Projecting BrowseComp-Plus onto ClimbMix: Toward More Realistic Corpora for Agentic Search

Sahel Sharifymoghaddam, Lin Gu, Yijun Ge, Jimmy Lin · 2026 · no venue · experimental · overall 3/3

<https://arxiv.org/abs/2608.20317>

**Key finding.** Relocating BrowseComp-Plus's evidence into a 553M-document corpus not built from benchmark queries drops the strongest agent's evidence recall from 84.3% to 21.4% (with a 63% increase in search calls) while answer accuracy falls by only five points, on 57 fully-verified projected questions.

**Why it made the cut.** contradicting · selected by score · strongest on C4 benchmark construction (3/3). The clearest evidence in this set that reported agentic-search gains can shrink dramatically once benchmark construction artifacts (query-conditioned corpora) are removed.

**Why it matters here.** A direct demonstration that a benchmark's own construction (query-conditioned corpus and negatives) inflates measured retrieval performance; the same agent's evidence recall collapses on a corpus not assembled per-query, exactly the replication failure the brief's question 4 is looking for.

**Method.** Projection pipeline decomposing questions into atomic reasoning hops, grounding each hop in a new corpus (ClimbMix) built independent of the benchmark, retaining only questions verified by automatic checks, an independent agent, and human review.

**Limitations.**

- only 57 questions survive the strict grounding-verification pipeline
- single projection target (ClimbMix); generality to other corpora untested

<sub>selected: score · criteria: C1 2/3 · C2 1/3 · C3 1/3 · C4 3/3 · C5 3/3 · flags: contradicts, methods_paper · verified 2026-08-26 via arxiv, s2</sub>

## 5. Towards Recursive Self-Evolving Agentic Literature Retrieval

Yuwen Du, Tian Jin, Jing Kang, Xianghe Pang et al. · 2026 · arXiv · experimental · overall 3/3

<https://doi.org/10.48550/arxiv.2605.14306>

**Key finding.** PaSaMaster achieves 16.5x higher F1 than Google Scholar and 37.8% higher F1 than GPT-5.2 at about 1% of the cost, reducing source hallucination from 32.66% to zero across 38 disciplines in PaSaMaster-Bench.

**Why it made the cut.** design-changing · selected by score · strongest on C1 baseline recall ceiling (3/3). Explicitly measures against a single-query baseline (Google Scholar) and reports a large agentic gain — central to decisions 1 and 2, though its self-reported magnitude is exactly the kind of number decision 4 asks us to interrogate.

**Why it matters here.** Directly anchors the recall/precision ceiling of a single-query search baseline (Google Scholar) against an agentic system, giving a concrete comparison point for decision 1, though the huge margin invites scrutiny of benchmark construction (decision 3).

**Method.** Recursive self-evolving agentic retrieval system separating LLM-based intent understanding from lightweight-model retrieval/scoring over verified papers; evaluated on a custom 38-discipline benchmark against Google Scholar and GPT-5.2 baselines.

**Limitations.**

- benchmark (PaSaMaster-Bench) is self-constructed, raising possible construction bias
- no ablation isolating self-evolving retrieval's contribution from other components' contribution to the reported gain

<sub>selected: score · criteria: C1 3/3 · C2 2/3 · C3 3/3 · C4 2/3 · C5 0/3 · flags: methods_paper · verified 2026-08-26 via openalex, arxiv</sub>

## 6. PaSa: An LLM Agent for Comprehensive Academic Paper Search

Yichen He, Guanhua Huang, Peiyuan Feng, Yuan Lin et al. · 2025 · Annual Meeting of the Association for Computational Linguistics · experimental · overall 3/3

<https://doi.org/10.48550/arxiv.2501.10120>

**Key finding.** PaSa-7B, an RL-trained autonomous paper-search agent, beats the best Google+GPT-4o baseline by 37.78% in recall@20 and 39.90% in recall@50 on a real-world academic query benchmark.

**Why it made the cut.** foundational · selected by score · strongest on C1 baseline recall ceiling (3/3). One of the founding agentic-paper-search systems, defining both the recall-ceiling baseline (C1) and a widely cited benchmark construction (C4).

**Why it matters here.** Establishes the single-query search-engine baseline (Google, Google Scholar) this whole literature repeatedly measures against, and its two benchmarks are the construction template later papers critique or reuse.

**Method.** RL-trained LLM agent that issues searches, reads papers, and selects references; trained on synthetic AutoScholarQuery (35k queries) and evaluated on a new real-world RealScholarQuery benchmark.

**Limitations.**

- trained on synthetic data with only limited real-world validation
- benchmark scope is AI conference papers, not broader science

<sub>selected: score · criteria: C1 3/3 · C2 2/3 · C3 1/3 · C4 3/3 · C5 0/3 · flags: methods_paper · verified 2026-08-26 via openalex, arxiv</sub>

## 7. Deep Research Agents: A Systematic Examination And Roadmap

Yuxuan Huang, Yihang Chen, Haozhen Zhang, Kang Li et al. · 2025 · arXiv.org · other · overall 3/3

<https://doi.org/10.48550/arxiv.2506.18096>

**Key finding.** A systematic taxonomy of Deep Research agents along information-acquisition strategy (API vs browser), tool-use modularity, and planning/composition architecture, paired with a critical evaluation identifying restricted external-knowledge access, sequential-execution inefficiency, and metric-objective misalignment as key current benchmark limitations.

**Why it made the cut.** foundational · selected by score · strongest on C4 benchmark construction (3/3). The field's own synthesis of architecture types and benchmark weaknesses, providing the orientation and critique the brief's decisions 2 and 3 depend on.

**Why it matters here.** Names the exact benchmark-construction failure modes (restricted knowledge access, misaligned metrics) the brief's question 3 and 4 are asking about, giving a map of where existing evaluations are already known to be shaky.

**Method.** Narrative systematic review and taxonomy construction over the Deep Research agent literature, with a maintained repository of surveyed systems.

**Limitations.**

- narrative synthesis, not a systematic-protocol review
- no new empirical results of its own

<sub>selected: score · criteria: C1 1/3 · C2 1/3 · C3 1/3 · C4 3/3 · C5 2/3 · flags: review · verified 2026-08-26 via arxiv</sub>

## 8. Structurally-bounded Agentic Graph Exploration for Evidence-Grounded Scholarly DeepSearch

Rima Hazra, Sayan Layek, Somnath Banerjee, Soumen Chakrabarti et al. · 2026 · arXiv · experimental · overall 3/3

<https://doi.org/10.48550/arxiv.2608.24809>

**Key finding.** A bounded pipeline of single seed search, 1.5-hop citation expansion, entailment-based edge pruning, and recency-aware random-walk ranking outperforms open-ended deep research agents by up to 3x recall@50 at roughly a third of the cost on LitSearch-style benchmarks.

**Why it made the cut.** design-changing · selected by score · strongest on C2 agentic mechanism gain (3/3). Precisely answers the brief's question 2: attributes measured gains to a specific mechanism (bounded citation-graph traversal) rather than treating the agent as a black box.

**Why it matters here.** Directly isolates which agentic move (citation-graph traversal with explicit pruning) carries the gain over an undifferentiated agent loop, and shows a bounded design can beat open-ended search decisively cheaper.

**Method.** Structured, inspectable graph-exploration system (Crase) evaluated on LitSearch and a second benchmark over a 500K-paper arXiv corpus, compared against deep research agents built on proprietary models.

**Limitations.**

- only two benchmarks tested
- relies on entailment model quality for edge pruning, itself unvalidated against ground truth

<sub>selected: score · criteria: C1 2/3 · C2 3/3 · C3 2/3 · C4 1/3 · C5 0/3 · flags: methods_paper · verified 2026-08-26 via arxiv</sub>

## 9. LLM-guided Hierarchical Search for End-to-end Reasoning Intensive Retrieval

Nilesh Gupta, Wei-Cheng Chang, N. Bui, Cho-Jui Hsieh et al. · 2025 · no venue · experimental · overall 3/3

<https://arxiv.org/abs/2510.13217>

**Key finding.** LATTICE, an LLM-guided hierarchical search index with no embedding model at search time, matches the best fine-tuned ensemble on BRIGHT (46.7 nDCG@10) and reaches 49.1 with a lightweight ensemble, while remaining competitive on SciFact and SciDocs.

**Why it made the cut.** plan-influencing · selected by backfill · strongest on C3 retrieval/reranking method (3/3). A retrieval/reranking method explicitly targeting the standard embedding-retriever-then-verify recipe's failure mode, tested partly on scientific IR benchmarks (SciFact, SciDocs).

**Why it matters here.** Shows that bypassing the embedding-retriever bottleneck entirely via LLM-guided hierarchical traversal can match or beat query-side reformulation fixes on reasoning-intensive retrieval, directly informing which retrieval architecture underlies a literature-search agent's evidence-gathering stage.

**Method.** Top-down LLM-guided construction of a hierarchical search index from multi-level document summaries plus calibrated path-aggregated LLM traversal, evaluated on BRIGHT, NQ, SciFact, SciDocs.

**Limitations.**

- BRIGHT is a general reasoning-intensive benchmark, not literature-search specific
- token-budget tradeoffs mean reranking still wins at low budgets

<sub>selected: backfill · criteria: C1 2/3 · C2 2/3 · C3 3/3 · C4 0/3 · C5 1/3 · flags: methods_paper · verified 2026-08-26 via arxiv, s2</sub>

## 10. Language agents achieve superhuman synthesis of scientific knowledge

Michael Skarlinski, Sam Cox, Jon M. Laurent, James D. Braza et al. · 2024 · arXiv (Cornell University) · experimental · overall 3/3

<https://doi.org/10.48550/arxiv.2409.13740>

**Key finding.** PaperQA2 matches or exceeds subject-matter-expert performance on literature search, summarization, and contradiction-detection tasks, and identifies 2.34 ± 1.99 contradictions per paper in biology literature, 70% validated by human experts.

**Why it made the cut.** foundational · selected by backfill · strongest on C4 benchmark construction (3/3). The most cited, most direct prior claim that agentic literature-search systems beat human/baseline performance — the paper decision 4 is specifically asking us to stress-test.

**Why it matters here.** The foundational claim the whole 'agentic beats baseline' premise rests on; any replication-failure evidence found later has to be read against this specific benchmark (LitQA2) and comparison protocol.

**Method.** Human-AI comparison methodology on real-world literature research tasks; introduces the LitQA2 benchmark used to guide PaperQA2's design; humans given unrestricted internet/tool access for a fair comparison.

**Limitations.**

- benchmark (LitQA2) co-developed with the system it evaluates, raising circularity concerns
- biology-heavy evaluation domain limits generality

<sub>selected: backfill · criteria: C1 1/3 · C2 1/3 · C3 2/3 · C4 3/3 · C5 0/3 · flags: methods_paper · verified 2026-08-26 via openalex, arxiv</sub>

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
- [Search-Time Contamination in Deep Research Agents: Measuring Performance Inflation in Public Benchmark Evaluation](https://doi.org/10.48550/arxiv.2606.05241) (2026) — overall 3/3
- [Agents-K1: Towards Agent-native Knowledge Orchestration](https://doi.org/10.48550/arxiv.2606.13669) (2026) — overall 3/3
- [From Inertia to Objectivity: Improving Deep Research Agents with Noise Isolation](https://doi.org/10.48550/arxiv.2608.23045) (2026) — overall 3/3
- [Multi-Turn Agentic Scientific Literature Search via Workflow Induction](https://doi.org/10.48550/arxiv.2607.00597) (2026) — overall 3/3
