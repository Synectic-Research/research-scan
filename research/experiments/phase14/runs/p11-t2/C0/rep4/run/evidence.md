# Evidence scan — p11-t2

Run `/Users/nabergoj/Projects/research-scan/research/experiments/phase14/runs/p11-t2/C0/rep4/run` · brief `/Users/nabergoj/Projects/research-scan/research/experiments/phase14/runs/p11-t2/C0/rep4/run/brief.md` · rendered 2026-08-27

| # | Paper | Year | Venue | Evidence | Verified |
|---|---|---|---|---|---|
| 1 | [BrowseComp-Plus: A More Fair and Transparent Evaluation Benchmark of Deep-Research Agent](https://doi.org/10.48550/arxiv.2508.06600) · 10.48550/arxiv.2508.06600 | 2025 | arXiv (Cornell University) | computational | yes |
| 2 | [Structurally-bounded Agentic Graph Exploration for Evidence-Grounded Scholarly DeepSearch](https://doi.org/10.48550/arxiv.2608.24809) · 10.48550/arxiv.2608.24809 | 2026 | arXiv | experimental | yes |
| 3 | [LLM-guided Hierarchical Search for End-to-end Reasoning Intensive Retrieval](https://arxiv.org/abs/2510.13217) | 2025 | — | experimental | yes |
| 4 | [Diagnosing Search Behavior and Failure Modes in Long-Horizon Search Agents](https://doi.org/10.48550/arxiv.2608.01913) · 10.48550/arxiv.2608.01913 | 2026 | arXiv | experimental | yes |
| 5 | [Patience is all you need! An agentic system for performing scientific literature review](https://doi.org/10.48550/arxiv.2504.08752) · 10.48550/arxiv.2504.08752 | 2025 | arXiv.org | experimental | yes |
| 6 | [LitSearch: A Retrieval Benchmark for Scientific Literature Search](https://doi.org/10.48550/arxiv.2407.18940) · 10.48550/arxiv.2407.18940 | 2024 | Conference on Empirical Methods in Natural Language Processing | experimental | yes |
| 7 | [PaSa: An LLM Agent for Comprehensive Academic Paper Search](https://doi.org/10.48550/arxiv.2501.10120) · 10.48550/arxiv.2501.10120 | 2025 | Annual Meeting of the Association for Computational Linguistics | experimental | yes |
| 8 | [Projecting BrowseComp-Plus onto ClimbMix: Toward More Realistic Corpora for Agentic Search](https://arxiv.org/abs/2608.20317) | 2026 | — | experimental | yes |
| 9 | [Towards Recursive Self-Evolving Agentic Literature Retrieval](https://doi.org/10.48550/arxiv.2605.14306) · 10.48550/arxiv.2605.14306 | 2026 | arXiv | experimental | yes |
| 10 | [Deep Research Agents: A Systematic Examination And Roadmap](https://doi.org/10.48550/arxiv.2506.18096) · 10.48550/arxiv.2506.18096 | 2025 | arXiv.org | other | yes |

## 1. BrowseComp-Plus: A More Fair and Transparent Evaluation Benchmark of Deep-Research Agent

Zijian Chen, Xueguang Ma, Shengyao Zhuang, Ping Nie et al. · 2025 · arXiv (Cornell University) · computational · overall 3/3

<https://doi.org/10.48550/arxiv.2508.06600>

**Key finding.** On a fixed, human-verified corpus, Search-R1 with BM25 reaches only 3.86% accuracy while GPT-5 reaches 55.9%, rising to 70.1% when paired with a Qwen3-Embedding-8B retriever.

**Why it made the cut.** foundational · selected by score · strongest on C1 baseline recall ceiling (3/3). The field's reference benchmark for disentangling agent and retriever contributions, providing baseline numbers and a construction template other papers here build on.

**Why it matters here.** Gives the field's clearest baseline accuracy/recall numbers under a controlled corpus (decision 1) and a reusable benchmark-construction methodology (decision 3) that other shortlisted work builds on directly.

**Method.** Introduces BrowseComp-Plus: a fixed corpus with human-verified supporting documents and mined hard negatives derived from BrowseComp, enabling controlled comparison of deep-research agents and retrievers.

**Limitations.**

- Corpus and negatives are both selected per-query from the benchmark's own questions, which later work shows can inflate apparent performance
- Domain is general web-search QA (BrowseComp), not literature-specific search

<sub>selected: score · criteria: C1 3/3 · C2 2/3 · C3 3/3 · C4 3/3 · C5 1/3 · flags: methods_paper · verified 2026-08-27 via openalex, arxiv</sub>

## 2. Structurally-bounded Agentic Graph Exploration for Evidence-Grounded Scholarly DeepSearch

Rima Hazra, Sayan Layek, Somnath Banerjee, Soumen Chakrabarti et al. · 2026 · arXiv · experimental · overall 3/3

<https://doi.org/10.48550/arxiv.2608.24809>

**Key finding.** A bounded design combining a single seed query with 1.5-hop citation-graph expansion and entailment-based pruning (Crase) outperforms open-ended deep research agents by up to 3x recall@50 at roughly a third of the cost.

**Why it made the cut.** design-changing · selected by score · strongest on C2 agentic mechanism gain (3/3). Isolates citation-graph traversal as the specific mechanism driving recall gains over open-ended agentic search.

**Why it matters here.** Shows that bounded citation-graph traversal with explicit stopping rules can beat unbounded agentic search loops, directly isolating which mechanism (structured traversal vs. open-ended agentic search) carries the recall gain.

**Method.** Single search-engine query for seed papers, 1.5-hop citation-graph expansion, entailment-based pruning, and recency-aware random-walk ranking, evaluated on LitSearch and one further benchmark over a 500K-paper arXiv corpus.

**Limitations.**

- Compared against proprietary-model deep research agents rather than an explicit single-query database baseline
- Fixed 500K-paper arXiv subset limits corpus coverage claims

<sub>selected: score · criteria: C1 2/3 · C2 3/3 · C3 3/3 · C4 2/3 · C5 2/3 · verified 2026-08-27 via arxiv</sub>

## 3. LLM-guided Hierarchical Search for End-to-end Reasoning Intensive Retrieval

Nilesh Gupta, Wei-Cheng Chang, N. Bui, Cho-Jui Hsieh et al. · 2025 · no venue · experimental · overall 3/3

<https://arxiv.org/abs/2510.13217>

**Key finding.** LATTICE, an LLM-guided hierarchical search index with no embedding model at search time, achieves 46.7 nDCG@10 on the reasoning-intensive BRIGHT benchmark (matching the best fine-tuned ensemble) and 49.1 with a lightweight ensemble.

**Why it made the cut.** design-changing · selected by score · strongest on C1 baseline recall ceiling (3/3). Direct evidence on embedding-based retrieval's recall ceiling failing on reasoning-intensive queries plus a non-embedding retrieval mechanism, addressing decisions 1–3.

**Why it matters here.** Directly challenges the baseline recall-ceiling premise by showing embedding-based top-k retrieval's assumption fails on reasoning-intensive queries even for SOTA embedders, and shows query rewriting/agentic loops remain brittle atop such retrievers — informs decisions 1 and 2.

**Method.** Top-down LLM-guided construction of a hierarchical index over multi-level document summaries, with calibrated path-aggregated LLM traversal at search time; evaluated on BRIGHT plus NQ, SciFact, SciDocs.

**Limitations.**

- BRIGHT is only partially scientific-literature-specific (includes SciFact/SciDocs among broader domains)
- Reranking outperforms LATTICE at low token budgets, so the advantage is budget-dependent

<sub>selected: score · criteria: C1 3/3 · C2 3/3 · C3 3/3 · C4 1/3 · C5 2/3 · flags: contradicts, methods_paper · verified 2026-08-27 via arxiv, s2</sub>

## 4. Diagnosing Search Behavior and Failure Modes in Long-Horizon Search Agents

Qi Liu, Jiaxin Mao, Fengbin Zhu, Tat-Seng Chua · 2026 · arXiv · experimental · overall 3/3

<https://doi.org/10.48550/arxiv.2608.01913>

**Key finding.** Answer accuracy correlates with cumulative retrieval recall rather than raw search effort, and the best agents issue far fewer redundant queries, leaving a long tail of low-yield search steps in weaker agents.

**Why it made the cut.** design-changing · selected by score · strongest on C2 agentic mechanism gain (3/3). Directly diagnoses which agentic mechanisms carry measured gains and where increased search effort fails to translate into answer quality.

**Why it matters here.** Directly answers decisions 2 and 4: pinpoints that retrieval quality and query economy, not sheer agentic effort, carry the measured gain, and shows more searching often fails to improve outcomes — evidence against the premise that agentic effort reliably pays off.

**Method.** Trajectory-level diagnosis of six long-horizon search agents using human-annotated document-level relevance judgments on BrowseComp-Plus, validated on BrowseComp with an open-web search API.

**Limitations.**

- Evaluated on general QA search benchmarks (BrowseComp/BrowseComp-Plus) rather than academic literature corpora
- Only six agents studied

<sub>selected: score · criteria: C1 2/3 · C2 3/3 · C3 1/3 · C4 2/3 · C5 3/3 · flags: contradicts · verified 2026-08-27 via openalex, arxiv</sub>

## 5. Patience is all you need! An agentic system for performing scientific literature review

David W. Brett, Anniek Myatt · 2025 · arXiv.org · experimental · overall 3/3

<https://doi.org/10.48550/arxiv.2504.08752>

**Key finding.** A keyword-based (sparse) retrieval and distillation system reaches performance close to state of the art on biology literature-review benchmarks without dense retrieval infrastructure.

**Why it made the cut.** contradicting · selected by score · strongest on C1 baseline recall ceiling (3/3). Provides direct evidence that a simple sparse baseline nearly matches more complex systems, bearing on both C1 and C5.

**Why it matters here.** Directly undercuts the assumption that dense retrieval or heavier agentic machinery is needed to close the recall gap — reframes what 'baseline' means and where the real ceiling sits.

**Method.** LLM-based full-text search and distillation system evaluated against biology-related questions from existing literature benchmarks.

**Limitations.**

- biology-domain questions only
- abstract does not report absolute recall numbers
- comparison is against unspecified 'state of the art', not a controlled single-query baseline

<sub>selected: score · criteria: C1 3/3 · C2 1/3 · C3 3/3 · C4 1/3 · C5 2/3 · flags: contradicts · verified 2026-08-27 via openalex, arxiv</sub>

## 6. LitSearch: A Retrieval Benchmark for Scientific Literature Search

Anirudh Ajith, Mengzhou Xia, Alexis Chevalier, Tanya Goyal et al. · 2024 · Conference on Empirical Methods in Natural Language Processing · experimental · overall 3/3

<https://doi.org/10.48550/arxiv.2407.18940>

**Key finding.** On LitSearch (597 literature-search queries), BM25 trails state-of-the-art dense retrievers by 24.8% absolute recall@5, LLM reranking further improves the best dense retriever by 4.4%, and commercial search engines lag the best dense retriever by 32 points.

**Why it made the cut.** foundational · selected by score · strongest on C1 baseline recall ceiling (3/3). Directly answers the brief's baseline-recall-ceiling question with numbers and documents its benchmark construction in detail, making it foundational reference evidence for the whole scan.

**Why it matters here.** Establishes the exact numeric baseline recall ceiling (sparse vs dense vs commercial search) the brief's Q1 asks for, and documents its benchmark construction in enough detail to judge what its numbers can and cannot support.

**Method.** New retrieval benchmark built from GPT-4-generated questions over cited paragraphs plus author-written questions about recent papers, expert-verified, benchmarked against multiple retrievers and reranking pipelines.

**Limitations.**

- restricted to ML/NLP papers, not the full scientific literature
- queries partly LLM-generated, raising a construction-validity question the brief itself flags for other benchmarks

<sub>selected: score · criteria: C1 3/3 · C2 0/3 · C3 3/3 · C4 3/3 · C5 1/3 · flags: methods_paper · verified 2026-08-27 via openalex, arxiv</sub>

## 7. PaSa: An LLM Agent for Comprehensive Academic Paper Search

Yichen He, Guanhua Huang, Peiyuan Feng, Yuan Lin et al. · 2025 · Annual Meeting of the Association for Computational Linguistics · experimental · overall 3/3

<https://doi.org/10.48550/arxiv.2501.10120>

**Key finding.** PaSa-7B surpasses the best Google-based baseline by 37.78% in recall@20 and 39.90% in recall@50 on a real-world academic query benchmark.

**Why it made the cut.** foundational · selected by score · strongest on C1 baseline recall ceiling (3/3). A foundational, highly-cited agentic academic paper-search system with explicit recall numbers against single-query search baselines.

**Why it matters here.** Establishes the empirical recall ceiling of single-query search-engine baselines (decision 1) and quantifies the size of the agentic gain a citation-reading, RL-optimized agent adds on top.

**Method.** RL-trained LLM paper-search agent evaluated against Google/Google Scholar/GPT-4o baselines, trained on a synthetic 35k-query set (AutoScholarQuery) and tested on a held-out real-world benchmark (RealScholarQuery).

**Limitations.**

- Trained/evaluated mainly on AI-conference papers, generalization to other fields unclear
- Baselines rely on commercial search engines whose indices change over time

<sub>selected: score · criteria: C1 3/3 · C2 2/3 · C3 1/3 · C4 3/3 · C5 0/3 · verified 2026-08-27 via openalex, arxiv</sub>

## 8. Projecting BrowseComp-Plus onto ClimbMix: Toward More Realistic Corpora for Agentic Search

Sahel Sharifymoghaddam, Lin Gu, Yijun Ge, Jimmy Lin · 2026 · no venue · experimental · overall 3/3

<https://arxiv.org/abs/2608.20317>

**Key finding.** Relocating BrowseComp-Plus questions' evidence to a benchmark-agnostic corpus (ClimbMix) drops the strongest agent's evidence recall from 84.3% to 21.4% (search calls up 63%) while answer accuracy falls by only five points, on 57 fully-grounded projected questions.

**Why it made the cut.** contradicting · selected by backfill · strongest on C4 benchmark construction (3/3). The most direct demonstration here that a headline benchmark's reported retrieval performance fails to replicate under an independently constructed corpus.

**Why it matters here.** Directly answers decision 4: demonstrates that a benchmark's own per-query-selected corpus and negatives substantially inflate apparent retrieval performance, and that evidence recall collapses under a more realistic corpus even as answer accuracy looks stable — a hard demonstration that reported agentic gains do not survive a corpus change.

**Method.** A projection pipeline decomposing questions into atomic reasoning hops, grounding each hop in a new corpus, and retaining only questions verified by an automatic checker, an independent agent, and human review; applied to the 830 BrowseComp-Plus test questions, yielding 57 grounded questions.

**Limitations.**

- Only 57 of 830 questions survive the strict grounding/verification pipeline, a small and possibly non-representative subset
- The projected corpus (ClimbMix, web text) is not itself a scientific-literature corpus

<sub>selected: backfill · criteria: C1 1/3 · C2 0/3 · C3 1/3 · C4 3/3 · C5 3/3 · flags: contradicts, methods_paper · verified 2026-08-27 via arxiv, s2</sub>

## 9. Towards Recursive Self-Evolving Agentic Literature Retrieval

Yuwen Du, Tian Jin, Jing Kang, Xianghe Pang et al. · 2026 · arXiv · experimental · overall 3/3

<https://doi.org/10.48550/arxiv.2605.14306>

**Key finding.** PaSaMaster achieves 16.5\u00d7 higher F1 than Google Scholar and 37.8% higher F1 than GPT-5.2 at about 1% of the cost, across 38 disciplines, while cutting source hallucination from 32.66% to 0%.

**Why it made the cut.** design-changing · selected by backfill · strongest on C1 baseline recall ceiling (3/3). Provides the clearest quantified single-query-baseline-vs-agentic-gain comparison in the shortlist, directly in the brief's setting.

**Why it matters here.** Anchors the gap between plain search-API querying (Google Scholar) and an agentic system with a concrete magnitude, giving exactly the baseline-vs-agentic-gain comparison the brief's decisions 1 and 2 need.

**Method.** A recursive self-evolving retrieval system combining intent refinement over ranked evidence, evidence-grounded ranking over verified papers, and planning/retrieval model separation, evaluated on the newly introduced PaSaMaster-Bench.

**Limitations.**

- PaSaMaster-Bench construction and relevance-labeling process not detailed in the abstract
- Comparison partner (Google Scholar) is a search API rather than a controlled BM25/embedding baseline

<sub>selected: backfill · criteria: C1 3/3 · C2 2/3 · C3 2/3 · C4 1/3 · C5 0/3 · flags: methods_paper · verified 2026-08-27 via openalex, arxiv</sub>

## 10. Deep Research Agents: A Systematic Examination And Roadmap

Yuxuan Huang, Yihang Chen, Haozhen Zhang, Kang Li et al. · 2025 · arXiv.org · other · overall 3/3

<https://doi.org/10.48550/arxiv.2506.18096>

**Key finding.** A taxonomy and critique of Deep Research agent architectures (planning strategies, single- vs. multi-agent composition, API-based vs. browser-based retrieval) identifies benchmark limitations including restricted external-knowledge access, sequential-execution inefficiency, and metric-objective misalignment.

**Why it made the cut.** closely-related · selected by review · strongest on C3 retrieval/reranking method (2/3). The field's own synthesis/roadmap of deep research agent design and benchmark limitations, a natural orienting reference for this scan.

**Why it matters here.** Provides the orienting map of the exact system-design and benchmarking space the brief is scanning, and its critique of metric-objective misalignment bears directly on decisions 3 and 4.

**Method.** Narrative systematic examination and taxonomy of Deep Research agent architectures and existing benchmarks; abstract-only for quantitative detail.

**Limitations.**

- Narrative review rather than a systematic-protocol review or empirical study
- No quantitative results of its own to anchor claims

<sub>selected: review · criteria: C1 1/3 · C2 1/3 · C3 2/3 · C4 2/3 · C5 1/3 · flags: review · verified 2026-08-27 via arxiv</sub>

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
- [Multi-Turn Agentic Scientific Literature Search via Workflow Induction](https://doi.org/10.48550/arxiv.2607.00597) (2026) — overall 3/3
- [Open-Source Agentic Hybrid RAG Framework for Scientific Literature Review](https://doi.org/10.48550/arxiv.2508.05660) (2025) — overall 3/3
- [Search-Time Contamination in Deep Research Agents: Measuring Performance Inflation in Public Benchmark Evaluation](https://doi.org/10.48550/arxiv.2606.05241) (2026) — overall 3/3
