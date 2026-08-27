# Evidence scan — p11-t2

Run `/Users/nabergoj/Projects/research-scan/research/experiments/phase14/runs/p11-t2/S/rep1/run` · brief `/Users/nabergoj/Projects/research-scan/research/experiments/phase14/runs/p11-t2/S/rep1/run/brief.md` · rendered 2026-08-26

| # | Paper | Year | Venue | Evidence | Verified |
|---|---|---|---|---|---|
| 1 | [Diagnosing Search Behavior and Failure Modes in Long-Horizon Search Agents](https://doi.org/10.48550/arxiv.2608.01913) · 10.48550/arxiv.2608.01913 | 2026 | arXiv | experimental | yes |
| 2 | [LitSearch: A Retrieval Benchmark for Scientific Literature Search](https://doi.org/10.48550/arxiv.2407.18940) · 10.48550/arxiv.2407.18940 | 2024 | Conference on Empirical Methods in Natural Language Processing | experimental | yes |
| 3 | [BrowseComp-Plus: A More Fair and Transparent Evaluation Benchmark of Deep-Research Agent](https://doi.org/10.48550/arxiv.2508.06600) · 10.48550/arxiv.2508.06600 | 2025 | arXiv (Cornell University) | experimental | yes |
| 4 | [BRIGHT: A Realistic and Challenging Benchmark for Reasoning-Intensive Retrieval](https://doi.org/10.48550/arxiv.2407.12883) · 10.48550/arxiv.2407.12883 | 2024 | International Conference on Learning Representations | experimental | yes |
| 5 | [Structurally-bounded Agentic Graph Exploration for Evidence-Grounded Scholarly DeepSearch](https://doi.org/10.48550/arxiv.2608.24809) · 10.48550/arxiv.2608.24809 | 2026 | arXiv | experimental | yes |
| 6 | [LLM-guided Hierarchical Search for End-to-end Reasoning Intensive Retrieval](https://arxiv.org/abs/2510.13217) | 2025 | — | experimental | yes |
| 7 | [OpenScholar: Synthesizing Scientific Literature with Retrieval-augmented LMs](https://doi.org/10.48550/arxiv.2411.14199) · 10.48550/arxiv.2411.14199 | 2024 | arXiv.org | experimental | yes |
| 8 | [Deep Research Agents: A Systematic Examination And Roadmap](https://doi.org/10.48550/arxiv.2506.18096) · 10.48550/arxiv.2506.18096 | 2025 | arXiv.org | other | yes |
| 9 | [PaSa: An LLM Agent for Comprehensive Academic Paper Search](https://doi.org/10.48550/arxiv.2501.10120) · 10.48550/arxiv.2501.10120 | 2025 | Annual Meeting of the Association for Computational Linguistics | experimental | yes |
| 10 | [Projecting BrowseComp-Plus onto ClimbMix: Toward More Realistic Corpora for Agentic Search](https://arxiv.org/abs/2608.20317) | 2026 | — | computational | yes |

## 1. Diagnosing Search Behavior and Failure Modes in Long-Horizon Search Agents

Qi Liu, Jiaxin Mao, Fengbin Zhu, Tat-Seng Chua · 2026 · arXiv · experimental · overall 3/3

<https://doi.org/10.48550/arxiv.2608.01913>

**Key finding.** Answer accuracy correlates much more strongly with cumulative retrieval recall than with number of searches or context consumed, and the best agents issue far fewer redundant queries despite exploratory reformulation still helping.

**Why it made the cut.** design-changing · selected by score · strongest on C1 baseline recall ceiling (3/3). Provides a fine-grained mechanism-level account of what agentic search adds and where it fails, directly addressing questions 2 and 4 of the brief.

**Why it matters here.** Directly answers what specific agentic moves carry the gain: reformulation helps but redundant searching does not, and evidence quality (not search volume) is the driver — reframes what 'agentic gain' should even be measured against.

**Method.** Trajectory-level diagnosis with human-annotated document relevance judgments across six agents on BrowseComp-Plus, validated on BrowseComp with an open-web API; decomposes failures into retrieval gaps vs utilization gaps.

**Limitations.**

- fixed retrieval model/harness may not generalize to other retrievers
- focused on six agents, not exhaustive of design space

<sub>selected: score · criteria: C1 3/3 · C2 3/3 · C3 1/3 · C4 2/3 · C5 2/3 · verified 2026-08-26 via openalex, arxiv</sub>

## 2. LitSearch: A Retrieval Benchmark for Scientific Literature Search

Anirudh Ajith, Mengzhou Xia, Alexis Chevalier, Tanya Goyal et al. · 2024 · Conference on Empirical Methods in Natural Language Processing · experimental · overall 3/3

<https://doi.org/10.48550/arxiv.2407.18940>

**Key finding.** On LitSearch's 597 realistic literature-search queries, BM25 trails state-of-the-art dense retrievers by 24.8 points absolute recall@5, and LLM-based reranking further improves the best dense retriever by 4.4%, while commercial search engines lag the best dense retriever by 32 points.

**Why it made the cut.** foundational · selected by score · strongest on C1 baseline recall ceiling (3/3). The paper that most directly answers the brief's first and third questions—what the single-query baseline recall ceiling is, and how a literature-search benchmark should be constructed.

**Why it matters here.** Directly establishes the single-query baseline recall ceiling (BM25 vs. dense vs. commercial search) that any agentic literature-search system's claimed improvement must be measured against, and documents a reusable benchmark-construction methodology—the anchor evidence for both C1 and C4.

**Method.** New retrieval benchmark built from GPT-4-generated questions over cited paragraphs plus author-written questions about their own recent papers, expert-verified; benchmarking of state-of-the-art dense retrievers, rerankers, and commercial search engines.

**Limitations.**

- ML/NLP paper queries only, not tested across broader scientific domains
- Benchmark is static, leaving open whether an agentic system's gains would hold on a dynamic or larger corpus

<sub>selected: score · criteria: C1 3/3 · C2 1/3 · C3 3/3 · C4 3/3 · C5 1/3 · flags: methods_paper · verified 2026-08-26 via openalex, arxiv</sub>

## 3. BrowseComp-Plus: A More Fair and Transparent Evaluation Benchmark of Deep-Research Agent

Zijian Chen, Xueguang Ma, Shengyao Zhuang, Ping Nie et al. · 2025 · arXiv (Cornell University) · experimental · overall 3/3

<https://doi.org/10.48550/arxiv.2508.06600>

**Key finding.** On a fixed, human-verified corpus, Search-R1 with BM25 achieves only 3.86% accuracy, GPT-5 alone reaches 55.9%, and GPT-5 with a Qwen3-Embedding-8B retriever reaches 70.1% with fewer search calls.

**Why it made the cut.** foundational · selected by score · strongest on C1 baseline recall ceiling (3/3). The benchmark most directly built to answer the brief's baseline-recall and benchmark-construction questions, widely adopted and cited (167 citations).

**Why it matters here.** Establishes the concrete baseline recall/accuracy numbers question 1 requires, and shows exactly how much of the reported gain is retriever-driven versus agent-driven — the field's reference point for fair comparison.

**Method.** Benchmark derived from BrowseComp with a fixed curated corpus, human-verified supporting documents, and mined hard negatives, enabling controlled disentangled evaluation of agent vs retriever contributions.

**Limitations.**

- corpus limited to documents mined per-query, later shown (by a follow-up paper) to be less realistic than a general web-scale corpus

<sub>selected: score · criteria: C1 3/3 · C2 1/3 · C3 2/3 · C4 3/3 · C5 1/3 · flags: methods_paper · verified 2026-08-26 via openalex, arxiv</sub>

## 4. BRIGHT: A Realistic and Challenging Benchmark for Reasoning-Intensive Retrieval

Hongjin Su, Howard Yen, Mengzhou Xia, Weijia Shi et al. · 2024 · International Conference on Learning Representations · experimental · overall 3/3

<https://doi.org/10.48550/arxiv.2407.12883>

**Key finding.** The leading MTEB retriever (SFR-Embedding-Mistral, 59.0 nDCG@10 on standard benchmarks) scores only 18.3 nDCG@10 on BRIGHT's reasoning-intensive queries; adding explicit reasoning about the query improves retrieval by up to 12.2 points.

**Why it made the cut.** foundational · selected by score · strongest on C1 baseline recall ceiling (3/3). Foundational, highly-cited demonstration of how low the single-query retrieval ceiling can be on reasoning-intensive queries, setting the baseline that agentic gains must be measured against.

**Why it matters here.** Establishes a hard, quantified ceiling on what single-query embedding-based database search can recover once queries require reasoning, the exact C1 anchor the brief says everything else must be measured against.

**Method.** 1,384 real-world, naturally-occurring reasoning-intensive queries across economics, psychology, mathematics, and coding; evaluates state-of-the-art retrievers and reasoning-augmented retrieval. Abstract-only.

**Limitations.**

- Domains are economics/psychology/math/coding, not scientific-literature search specifically
- abstract-only
- does not evaluate full agentic literature-search pipelines

<sub>selected: score · criteria: C1 3/3 · C2 1/3 · C3 2/3 · C4 2/3 · C5 2/3 · flags: methods_paper · verified 2026-08-26 via openalex, arxiv</sub>

## 5. Structurally-bounded Agentic Graph Exploration for Evidence-Grounded Scholarly DeepSearch

Rima Hazra, Sayan Layek, Somnath Banerjee, Soumen Chakrabarti et al. · 2026 · arXiv · experimental · overall 3/3

<https://doi.org/10.48550/arxiv.2608.24809>

**Key finding.** A bounded citation-graph traversal system (1.5-hop expansion, entailment pruning, recency-aware random walk) outperforms proprietary deep research agents by up to 3x recall@50 at roughly a third of the cost on LitSearch and a further arXiv-scale benchmark.

**Why it made the cut.** design-changing · selected by score · strongest on C2 agentic mechanism gain (3/3). Directly attributes a measured recall gain to citation-graph traversal specifically, the core mechanism question 2 asks about.

**Why it matters here.** Isolates citation-graph traversal as the specific mechanism carrying the gain, with an explicit, fixed stopping condition — direct evidence for question 2 and a concrete alternative design to open-ended agent loops.

**Method.** Single seed search plus fixed-depth citation-graph expansion and pruning, evaluated on LitSearch and one further benchmark over a 500K-paper arXiv corpus, abstract-only detail.

**Limitations.**

- compares against proprietary agents whose exact configuration is opaque
- bounded to 1.5-hop neighborhoods, so generalization to deeper structures untested

<sub>selected: score · criteria: C1 2/3 · C2 3/3 · C3 2/3 · C4 2/3 · C5 1/3 · flags: methods_paper · verified 2026-08-26 via arxiv</sub>

## 6. LLM-guided Hierarchical Search for End-to-end Reasoning Intensive Retrieval

Nilesh Gupta, Wei-Cheng Chang, N. Bui, Cho-Jui Hsieh et al. · 2025 · no venue · experimental · overall 3/3

<https://arxiv.org/abs/2510.13217>

**Key finding.** LATTICE, an LLM-guided hierarchical search index with no embedding model at search time, matches the best fine-tuned ensemble on BRIGHT (46.7 nDCG@10) and reaches 49.1 with a lightweight ensemble, while explicitly showing embedding-based top-k retrieval fails to place relevant documents for reasoning-intensive queries.

**Why it made the cut.** design-changing · selected by score · strongest on C1 baseline recall ceiling (3/3). Names the specific baseline recall ceiling problem (embedding top-k failure) the brief asks question 1 to establish, and proposes a retrieval method addressing it.

**Why it matters here.** Directly quantifies where single-query embedding retrieval hits a ceiling for reasoning-intensive queries and offers a retrieval architecture that removes the embedding bottleneck — bears squarely on questions 1 and 3.

**Method.** Top-down LLM-guided construction of a hierarchical document-summary index plus calibrated path-aggregated LLM traversal, evaluated on BRIGHT and traditional IR benchmarks (NQ, SciFact, SciDocs).

**Limitations.**

- evaluated primarily on BRIGHT, a reasoning-intensive IR benchmark rather than a literature-search benchmark specifically
- token-budget tradeoffs against reranking not fully resolved

<sub>selected: score · criteria: C1 3/3 · C2 1/3 · C3 3/3 · C4 1/3 · C5 2/3 · flags: methods_paper · verified 2026-08-26 via arxiv, s2</sub>

## 7. OpenScholar: Synthesizing Scientific Literature with Retrieval-augmented LMs

Akari Asai, Jacqueline He, Rulin Shao, Weijia Shi et al. · 2024 · arXiv.org · experimental · overall 3/3

<https://doi.org/10.48550/arxiv.2411.14199>

**Key finding.** OpenScholar-8B outperforms GPT-4o by 5% and PaperQA2 by 7% in correctness on the new ScholarQABench (2,967 expert queries, 208 long-form answers across four science domains), while GPT-4o hallucinates citations 78-90% of the time versus near-human citation accuracy for OpenScholar.

**Why it made the cut.** design-changing · selected by score · strongest on C3 retrieval/reranking method (3/3). Central, large-scale evidence for both system design and benchmark construction in exactly the brief's setting—scientific literature synthesis.

**Why it matters here.** A major system-plus-benchmark result directly in the brief's setting: it quantifies gains over both a closed system (PaperQA2) and a general LLM baseline, and its ScholarQABench construction is a concrete precedent for the C4 benchmark-construction question.

**Method.** Retrieval-augmented LM over a 45-million-paper open-access datastore with a self-feedback inference loop; evaluated on the newly built ScholarQABench and via human preference studies (experts preferred OpenScholar responses 51-70% of the time).

**Limitations.**

- No explicit comparison against a plain single-query BM25/embedding-only baseline reported in the abstract
- Reported gains are relative to other systems, not decomposed by specific agentic mechanism

<sub>selected: score · criteria: C1 2/3 · C2 2/3 · C3 3/3 · C4 3/3 · C5 0/3 · flags: methods_paper · verified 2026-08-26 via openalex, arxiv</sub>

## 8. Deep Research Agents: A Systematic Examination And Roadmap

Yuxuan Huang, Yihang Chen, Haozhen Zhang, Kang Li et al. · 2025 · arXiv.org · other · overall 3/3

<https://doi.org/10.48550/arxiv.2506.18096>

**Key finding.** Provides a taxonomy of Deep Research agent architectures (static vs dynamic workflows, single- vs multi-agent) and a critical evaluation of current benchmarks, identifying restricted external-knowledge access, sequential execution inefficiencies, and metric-objective misalignment as key limitations.

**Why it made the cut.** plan-influencing · selected by backfill · strongest on C4 benchmark construction (3/3). The field's own review of Deep Research agent design and benchmark limitations, giving a synthesis view no single system paper provides.

**Why it matters here.** Synthesizes and critiques the whole benchmark landscape this scan needs to navigate, flagging exactly the kind of construction problems (metric-objective misalignment) question 3 asks the scan to interrogate.

**Method.** Narrative systematic review of foundational technologies and architectural components across information acquisition, tool-use frameworks, and agent composition, with an accompanying curated repository.

**Limitations.**

- a narrative rather than systematic-protocol review, so coverage claims are not independently verifiable from the abstract
- taxonomy may already be dated given the field's rapid pace

<sub>selected: backfill · criteria: C1 1/3 · C2 2/3 · C3 2/3 · C4 3/3 · C5 1/3 · flags: review · verified 2026-08-26 via arxiv</sub>

## 9. PaSa: An LLM Agent for Comprehensive Academic Paper Search

Yichen He, Guanhua Huang, Peiyuan Feng, Yuan Lin et al. · 2025 · Annual Meeting of the Association for Computational Linguistics · experimental · overall 3/3

<https://doi.org/10.48550/arxiv.2501.10120>

**Key finding.** PaSa-7B surpasses the best Google+GPT-4o baseline by 37.78% in recall@20 and 39.90% in recall@50 on RealScholarQuery, using an RL-trained agent that searches, reads, and selects references.

**Why it made the cut.** design-changing · selected by backfill · strongest on C2 agentic mechanism gain (3/3). Directly answers what agentic mechanisms add over single-query search and how a literature-search benchmark can be constructed (C2, C4).

**Why it matters here.** A foundational agentic academic-search system with an explicit baseline comparison and a purpose-built, well-documented benchmark construction — the closest thing in the corpus to the brief's central system-plus-benchmark pairing.

**Method.** RL-optimized LLM agent trained on a synthetic 35k-query dataset (AutoScholarQuery), evaluated against Google/Scholar/GPT-4o baselines on a new real-world benchmark (RealScholarQuery).

**Limitations.**

- trained on synthetic queries despite testing on real ones, raising generalization questions
- benchmark sourced from top-tier AI conferences only, limiting corpus coverage

<sub>selected: backfill · criteria: C1 2/3 · C2 3/3 · C3 1/3 · C4 3/3 · C5 0/3 · flags: methods_paper · verified 2026-08-26 via openalex, arxiv</sub>

## 10. Projecting BrowseComp-Plus onto ClimbMix: Toward More Realistic Corpora for Agentic Search

Sahel Sharifymoghaddam, Lin Gu, Yijun Ge, Jimmy Lin · 2026 · no venue · computational · overall 3/3

<https://arxiv.org/abs/2608.20317>

**Key finding.** Relocating BrowseComp-Plus's evidence into a more realistic, benchmark-independent corpus (ClimbMix) drops the strongest agent's evidence recall from 84.3% to 21.4% and costs five points of answer accuracy despite 63% more search calls, on 57 fully grounded projected questions.

**Why it made the cut.** contradicting · selected by contradicting · strongest on C4 benchmark construction (3/3). The clearest demonstration in the set of a reported agentic gain shrinking dramatically under a different, less benchmark-selected corpus.

**Why it matters here.** Directly demonstrates that a benchmark's own construction (query-selected corpus) inflates apparent agent capability, and that the gain collapses under a more realistic corpus — precisely the replication-failure evidence question 4 asks for.

**Method.** A projection pipeline decomposing questions into atomic reasoning hops, grounding each hop in a new corpus with automatic, agent, and human verification, applied to the 830 BrowseComp-Plus test questions.

**Limitations.**

- yields only 57 fully grounded questions from 830, a large reduction in test-set size
- single benchmark (BrowseComp-Plus) projected; generalization to other benchmarks not yet shown

<sub>selected: contradicting · criteria: C1 1/3 · C2 0/3 · C3 0/3 · C4 3/3 · C5 3/3 · flags: contradicts, methods_paper · verified 2026-08-26 via arxiv, s2</sub>

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

- [Multi-Agent System for Scientific Literature Search and Recommendation](https://doi.org/10.1109/icssas66150.2025.11081082) (2025) — overall 3/3
- [Towards Recursive Self-Evolving Agentic Literature Retrieval](https://doi.org/10.48550/arxiv.2605.14306) (2026) — overall 3/3
- [Deep Research: A Survey of Autonomous Research Agents](https://doi.org/10.48550/arxiv.2508.12752) (2025) — overall 3/3
- [Multi-Turn Agentic Scientific Literature Search via Workflow Induction](https://doi.org/10.48550/arxiv.2607.00597) (2026) — overall 3/3
- [Patience is all you need! An agentic system for performing scientific literature review](https://doi.org/10.48550/arxiv.2504.08752) (2025) — overall 3/3
