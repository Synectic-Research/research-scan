# Evidence scan — p11-t2

Run `/Users/nabergoj/Projects/research-scan/research/experiments/phase14/runs/p11-t2/S/rep3/run` · brief `/Users/nabergoj/Projects/research-scan/research/experiments/phase14/runs/p11-t2/S/rep3/run/brief.md` · rendered 2026-08-26

| # | Paper | Year | Venue | Evidence | Verified |
|---|---|---|---|---|---|
| 1 | [Diagnosing Search Behavior and Failure Modes in Long-Horizon Search Agents](https://doi.org/10.48550/arxiv.2608.01913) · 10.48550/arxiv.2608.01913 | 2026 | arXiv | experimental | yes |
| 2 | [BrowseComp-Plus: A More Fair and Transparent Evaluation Benchmark of Deep-Research Agent](https://doi.org/10.48550/arxiv.2508.06600) · 10.48550/arxiv.2508.06600 | 2025 | arXiv (Cornell University) | experimental | yes |
| 3 | [Deep Research Agents: A Systematic Examination And Roadmap](https://doi.org/10.48550/arxiv.2506.18096) · 10.48550/arxiv.2506.18096 | 2025 | arXiv.org | other | yes |
| 4 | [OpenScholar: Synthesizing Scientific Literature with Retrieval-augmented LMs](https://doi.org/10.48550/arxiv.2411.14199) · 10.48550/arxiv.2411.14199 | 2024 | arXiv.org | experimental | yes |
| 5 | [PaSa: An LLM Agent for Comprehensive Academic Paper Search](https://doi.org/10.48550/arxiv.2501.10120) · 10.48550/arxiv.2501.10120 | 2025 | Annual Meeting of the Association for Computational Linguistics | experimental | yes |
| 6 | [LLM-guided Hierarchical Search for End-to-end Reasoning Intensive Retrieval](https://arxiv.org/abs/2510.13217) | 2025 | — | experimental | yes |
| 7 | [LitSearch: A Retrieval Benchmark for Scientific Literature Search](https://doi.org/10.48550/arxiv.2407.18940) · 10.48550/arxiv.2407.18940 | 2024 | Conference on Empirical Methods in Natural Language Processing | experimental | yes |
| 8 | [Towards Recursive Self-Evolving Agentic Literature Retrieval](https://doi.org/10.48550/arxiv.2605.14306) · 10.48550/arxiv.2605.14306 | 2026 | arXiv | experimental | yes |
| 9 | [Structurally-bounded Agentic Graph Exploration for Evidence-Grounded Scholarly DeepSearch](https://doi.org/10.48550/arxiv.2608.24809) · 10.48550/arxiv.2608.24809 | 2026 | arXiv | experimental | yes |
| 10 | [Multi-Agent System for Scientific Literature Search and Recommendation](https://doi.org/10.1109/icssas66150.2025.11081082) · 10.1109/icssas66150.2025.11081082 | 2025 | — | experimental | yes |

## 1. Diagnosing Search Behavior and Failure Modes in Long-Horizon Search Agents

Qi Liu, Jiaxin Mao, Fengbin Zhu, Tat-Seng Chua · 2026 · arXiv · experimental · overall 3/3

<https://doi.org/10.48550/arxiv.2608.01913>

**Key finding.** Answer accuracy correlates more strongly with cumulative retrieval recall than with number of searches or context consumed, and the best-performing agents issue far fewer redundant queries.

**Why it made the cut.** contradicting · selected by score · strongest on C2 agentic mechanism gain (3/3). Directly answers which agentic mechanisms carry the gain and where long-horizon search effort fails to pay off, central to Q2 and Q4.

**Why it matters here.** Directly tests whether more agentic search effort produces better answers, finding a weak link and locating the real gain in retrieval quality and non-redundant querying rather than search volume — this reframes what an 'agentic gain' should actually be attributed to.

**Method.** Trajectory-level diagnosis of six long-horizon search agents on BrowseComp-Plus and BrowseComp, using human-annotated document-level relevance judgments with retrieval model and evaluation harness held fixed.

**Limitations.**

- Focused on two related benchmark families (BrowseComp/BrowseComp-Plus), which may not generalize to other literature-search settings
- Diagnostic/observational analysis rather than a causal manipulation of agent design

<sub>selected: score · criteria: C1 1/3 · C2 3/3 · C3 1/3 · C4 2/3 · C5 3/3 · flags: contradicts · verified 2026-08-26 via openalex, arxiv</sub>

## 2. BrowseComp-Plus: A More Fair and Transparent Evaluation Benchmark of Deep-Research Agent

Zijian Chen, Xueguang Ma, Shengyao Zhuang, Ping Nie et al. · 2025 · arXiv (Cornell University) · experimental · overall 3/3

<https://doi.org/10.48550/arxiv.2508.06600>

**Key finding.** On a fixed, human-verified corpus, BM25-paired Search-R1 reaches only 3.86% accuracy versus GPT-5's 55.9%, and pairing GPT-5 with a Qwen3-Embedding-8B retriever raises accuracy to 70.1% with fewer search calls.

**Why it made the cut.** foundational · selected by score · strongest on C1 baseline recall ceiling (3/3). The controlled benchmark underlying most other agentic-search evaluations in this batch; essential for interpreting any reported recall gain.

**Why it matters here.** Supplies the field's controlled recall/accuracy ceiling numbers separating retriever quality from agent capability, exactly the anchor the brief requires before any agentic improvement can be judged real.

**Method.** Benchmark derived from BrowseComp using a fixed, curated document corpus with human-verified supporting documents and mined hard negatives, enabling controlled, reproducible comparison of retrievers and agent LLMs.

**Limitations.**

- Corpus and hard negatives were constructed from the benchmark's own queries, a contamination-adjacent design later shown to inflate results
- Single benchmark family (BrowseComp-derived), not scientific-literature-specific queries

<sub>selected: score · criteria: C1 3/3 · C2 1/3 · C3 2/3 · C4 3/3 · C5 1/3 · flags: methods_paper · verified 2026-08-26 via openalex, arxiv</sub>

## 3. Deep Research Agents: A Systematic Examination And Roadmap

Yuxuan Huang, Yihang Chen, Haozhen Zhang, Kang Li et al. · 2025 · arXiv.org · other · overall 3/3

<https://doi.org/10.48550/arxiv.2506.18096>

**Key finding.** A systematic taxonomy of Deep Research agent architectures (static/dynamic workflows, single/multi-agent) alongside a critical evaluation identifying restricted external-knowledge access, sequential-execution inefficiency, and metric-objective misalignment as key current benchmark limitations.

**Why it made the cut.** foundational · selected by score · strongest on C4 benchmark construction (3/3). The field's synthesis and benchmark critique, directly informing how to interpret benchmark construction and where reported gains are likely inflated.

**Why it matters here.** Gives the field's organizing taxonomy and names exactly the benchmark-construction failure modes (misaligned metrics, restricted knowledge access) that Q3/Q4 ask us to watch for, orienting how to read every other paper's reported numbers.

**Method.** Narrative systematic review and taxonomy of Deep Research agent architectures, information-acquisition strategies, and tool-use frameworks, plus a critique of existing benchmarks. Abstract-only detail beyond that.

**Limitations.**

- Narrative/roadmap review rather than new empirical evidence
- Does not itself quantify any of the failure modes it names

<sub>selected: score · criteria: C1 2/3 · C2 2/3 · C3 1/3 · C4 3/3 · C5 2/3 · flags: review · verified 2026-08-26 via arxiv</sub>

## 4. OpenScholar: Synthesizing Scientific Literature with Retrieval-augmented LMs

Akari Asai, Jacqueline He, Rulin Shao, Weijia Shi et al. · 2024 · arXiv.org · experimental · overall 3/3

<https://doi.org/10.48550/arxiv.2411.14199>

**Key finding.** OpenScholar-8B outperforms GPT-4o by 5% and PaperQA2 by 7% in correctness on ScholarQABench (2,967 expert queries across CS, physics, neuroscience, biomedicine), while GPT-4o hallucinates citations 78-90% of the time versus OpenScholar's expert-level citation accuracy.

**Why it made the cut.** design-changing · selected by score · strongest on C1 baseline recall ceiling (3/3). The strongest, most directly comparable evidence in the batch for baseline recall/correctness ceiling and benchmark construction in scientific literature search.

**Why it matters here.** Sets the strongest current baseline and benchmark for scientific literature synthesis, giving concrete numbers (recall/correctness/citation-hallucination rates) against which any new agentic design's claimed gain must be measured, and directly shows where undifferentiated 'agentic' systems (GPT-4o) fail.

**Method.** Retrieval-augmented LM over a 45-million-paper open-access datastore with self-feedback inference loop; new multi-domain benchmark (ScholarQABench) with human expert evaluation comparing to GPT-4o and PaperQA2.

**Limitations.**

- comparisons are correctness/citation-accuracy based rather than pure retrieval recall
- self-feedback loop's contribution vs retriever/datastore not fully decomposed

<sub>selected: score · criteria: C1 3/3 · C2 1/3 · C3 3/3 · C4 3/3 · C5 0/3 · flags: methods_paper · verified 2026-08-26 via openalex, arxiv</sub>

## 5. PaSa: An LLM Agent for Comprehensive Academic Paper Search

Yichen He, Guanhua Huang, Peiyuan Feng, Yuan Lin et al. · 2025 · Annual Meeting of the Association for Computational Linguistics · experimental · overall 3/3

<https://doi.org/10.48550/arxiv.2501.10120>

**Key finding.** PaSa-7B surpasses the best Google-based baseline by 37.78% in recall@20 and 39.90% in recall@50 on the real-world RealScholarQuery benchmark.

**Why it made the cut.** foundational · selected by score · strongest on C1 baseline recall ceiling (3/3). A landmark agentic academic-search system with explicit baseline comparisons and benchmark construction, central to Q1 and Q4.

**Why it matters here.** Establishes that keyword/Google-based single-query search substantially underperforms an agentic read-and-select loop, and supplies one of the field's core benchmark-construction templates (synthetic training set plus real-world evaluation set).

**Method.** RL-trained LLM agent that invokes search tools, reads papers, and selects references; trained on synthetic AutoScholarQuery (35k queries from top-tier AI venues) and evaluated on RealScholarQuery.

**Limitations.**

- Synthetic training data (AutoScholarQuery) may not transfer perfectly to open-ended real queries
- Baseline comparisons are against Google-based systems rather than a systematically constructed database-search recall ceiling

<sub>selected: score · criteria: C1 3/3 · C2 2/3 · C3 1/3 · C4 3/3 · C5 0/3 · flags: methods_paper · verified 2026-08-26 via openalex, arxiv</sub>

## 6. LLM-guided Hierarchical Search for End-to-end Reasoning Intensive Retrieval

Nilesh Gupta, Wei-Cheng Chang, N. Bui, Cho-Jui Hsieh et al. · 2025 · no venue · experimental · overall 3/3

<https://arxiv.org/abs/2510.13217>

**Key finding.** LATTICE, an LLM-guided hierarchical search index with no embedding model in the retrieval loop, matches the best fine-tuned reranking ensemble at 46.7 nDCG@10 on BRIGHT and reaches 49.1 with a lightweight ensemble.

**Why it made the cut.** plan-influencing · selected by score · strongest on C1 baseline recall ceiling (3/3). Direct evidence bounding the recall ceiling of standard embedding retrieval and a concrete alternative retrieval/reranking mechanism (C1, C3).

**Why it matters here.** Shows that the standard embedding-retriever-then-LLM-verifier pipeline — the implicit baseline for many agentic systems — fails to place relevant documents in top-k for reasoning-intensive queries, motivating retrieval architectures beyond single-query embedding search.

**Method.** Top-down LLM-guided construction of a hierarchically navigable search index over multi-level document summaries with calibrated, path-aggregated LLM traversal; evaluated on BRIGHT, NQ, SciFact, and SciDocs.

**Limitations.**

- Primary evaluation benchmark (BRIGHT) is general reasoning-intensive retrieval, not specifically scientific-literature search
- Sliding-window reranking is shown to be better at low token budgets, so LATTICE's advantage is budget-conditional

<sub>selected: score · criteria: C1 3/3 · C2 1/3 · C3 3/3 · C4 1/3 · C5 1/3 · flags: methods_paper · verified 2026-08-26 via arxiv, s2</sub>

## 7. LitSearch: A Retrieval Benchmark for Scientific Literature Search

Anirudh Ajith, Mengzhou Xia, Alexis Chevalier, Tanya Goyal et al. · 2024 · Conference on Empirical Methods in Natural Language Processing · experimental · overall 3/3

<https://doi.org/10.48550/arxiv.2407.18940>

**Key finding.** On 597 realistic literature-search queries, LitSearch finds a 24.8% absolute recall@5 gap between BM25 and state-of-the-art dense retrievers, with LLM reranking adding a further 4.4% improvement, while commercial search engines lag the best dense retriever by 32 points.

**Why it made the cut.** foundational · selected by score · strongest on C1 baseline recall ceiling (3/3). The clearest anchor for the baseline recall ceiling and a template for benchmark construction, both central to the brief's decision questions.

**Why it matters here.** Directly answers the brief's first-priority question by quantifying the single-query BM25 recall ceiling and the size of the dense-retrieval and reranking gains on top of it, and documents exactly how a literature-search benchmark should be built (query source, expert vetting).

**Method.** New retrieval benchmark constructed from GPT-4-generated questions (from cited paragraphs) plus author-written questions about recent papers, expert-vetted; extensive benchmarking of retrievers, rerankers, and commercial search engines.

**Limitations.**

- restricted to recent ML/NLP papers, not broader scientific domains
- queries partly GPT-4-generated, raising a construction-validity question the brief itself flags

<sub>selected: score · criteria: C1 3/3 · C2 0/3 · C3 2/3 · C4 3/3 · C5 1/3 · flags: methods_paper · verified 2026-08-26 via openalex, arxiv</sub>

## 8. Towards Recursive Self-Evolving Agentic Literature Retrieval

Yuwen Du, Tian Jin, Jing Kang, Xianghe Pang et al. · 2026 · arXiv · experimental · overall 3/3

<https://doi.org/10.48550/arxiv.2605.14306>

**Key finding.** PaSaMaster achieves a 16.5x higher F1-score than Google Scholar and a 37.8% higher F1-score than GPT-5.2 at about 1% of the cost across 38 disciplines, while reducing source hallucination from 32.66% to zero.

**Why it made the cut.** design-changing · selected by score · strongest on C3 retrieval/reranking method (3/3). Directly reports a baseline-anchored, mechanism-attributed gain for an agentic literature retrieval system, the exact evidence shape the brief's first two questions ask for.

**Why it matters here.** Provides one of the few direct, numeric comparisons against a real single-query search baseline (Google Scholar), anchoring the brief's Q1 recall-ceiling question, and attributes gains to self-evolving intent refinement, speaking to Q2.

**Method.** Recursive self-evolving agentic retrieval system separating frontier-LLM intent understanding from lightweight-model retrieval/scoring; evaluated against Google Scholar and GPT-5.2 baselines on a 38-discipline benchmark (PaSaMaster-Bench).

**Limitations.**

- PaSaMaster-Bench construction (query source, relevance labeling) not detailed in the abstract
- Comparison baseline (Google Scholar) is a commercial search engine, not a controlled single-query database-search ablation

<sub>selected: score · criteria: C1 2/3 · C2 2/3 · C3 3/3 · C4 1/3 · C5 0/3 · flags: methods_paper · verified 2026-08-26 via openalex, arxiv</sub>

## 9. Structurally-bounded Agentic Graph Exploration for Evidence-Grounded Scholarly DeepSearch

Rima Hazra, Sayan Layek, Somnath Banerjee, Soumen Chakrabarti et al. · 2026 · arXiv · experimental · overall 3/3

<https://doi.org/10.48550/arxiv.2608.24809>

**Key finding.** Crase's bounded citation-graph pipeline (seed search, 1.5-hop citation expansion, entailment pruning, recency-aware random walk) outperforms proprietary deep research agents by up to 3x recall@50 at roughly a third of the cost.

**Why it made the cut.** design-changing · selected by backfill · strongest on C2 agentic mechanism gain (3/3). Directly isolates and quantifies the contribution of citation-graph traversal, a central agentic-mechanism question in the brief.

**Why it matters here.** Isolates citation-graph traversal as the specific mechanism carrying the measured gain over open-ended agentic search loops, directly answering which agentic move matters and by how much.

**Method.** Structured, inspectable retrieval pipeline evaluated on LitSearch and a further benchmark over a 500K-paper arXiv corpus, compared against deep-research agent baselines built on proprietary models.

**Limitations.**

- Evaluated on a fixed arXiv corpus that may not capture the full difficulty of live search
- Comparison baselines are proprietary deep-research agents rather than a plain single-query search baseline

<sub>selected: backfill · criteria: C1 2/3 · C2 3/3 · C3 2/3 · C4 1/3 · C5 0/3 · flags: methods_paper · verified 2026-08-26 via arxiv</sub>

## 10. Multi-Agent System for Scientific Literature Search and Recommendation

Aswathy K Cherian, Naman Srivastava, Samyak Varia · 2025 · no venue · experimental · overall 3/3

<https://doi.org/10.1109/icssas66150.2025.11081082>

**Key finding.** A multi-agent system with a query-expansion agent and hybrid BM25+FAISS retrieval achieves an 8.5% precision improvement, 7.3% recall improvement, and ~210ms lower latency than PaperQA and Semantic Scholar.

**Why it made the cut.** design-changing · selected by backfill · strongest on C3 retrieval/reranking method (3/3). A scientific-literature-search-specific system that isolates query reformulation and hybrid retrieval against named baselines, matching C1-C3 directly.

**Why it matters here.** Gives a directly comparable, quantified case of query reformulation plus hybrid retrieval beating named literature-search baselines (PaperQA, Semantic Scholar), which is exactly the kind of gain-attribution evidence the brief wants isolated by mechanism.

**Method.** FastAPI-based multi-agent architecture (Query, Retrieval, Learning agents) with hybrid sparse/dense retrieval and Sentence-Transformers for semantic similarity; compared against published retrieval systems.

**Limitations.**

- unclear peer-review status/venue (listed as 'other' type)
- evaluation details (dataset, statistical significance) not given beyond abstract
- small citation count, unreplicated

<sub>selected: backfill · criteria: C1 2/3 · C2 2/3 · C3 3/3 · C4 1/3 · C5 0/3 · flags: methods_paper · verified 2026-08-26 via crossref, openalex</sub>

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

- [Projecting BrowseComp-Plus onto ClimbMix: Toward More Realistic Corpora for Agentic Search](https://arxiv.org/abs/2608.20317) (2026) — overall 3/3
- [Multi-Turn Agentic Scientific Literature Search via Workflow Induction](https://doi.org/10.48550/arxiv.2607.00597) (2026) — overall 3/3
- [Deep Research: A Survey of Autonomous Research Agents](https://doi.org/10.48550/arxiv.2508.12752) (2025) — overall 3/3
- [Patience is all you need! An agentic system for performing scientific literature review](https://doi.org/10.48550/arxiv.2504.08752) (2025) — overall 3/3
- [CG-RAG: Research Question Answering by Citation Graph Retrieval-Augmented LLMs](https://doi.org/10.1145/3726302.3729920) (2025) — overall 3/3
