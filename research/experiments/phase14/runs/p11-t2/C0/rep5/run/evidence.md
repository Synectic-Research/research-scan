# Evidence scan — p11-t2

Run `/Users/nabergoj/Projects/research-scan/research/experiments/phase14/runs/p11-t2/C0/rep5/run` · brief `/Users/nabergoj/Projects/research-scan/research/experiments/phase14/runs/p11-t2/C0/rep5/run/brief.md` · rendered 2026-08-27

| # | Paper | Year | Venue | Evidence | Verified |
|---|---|---|---|---|---|
| 1 | [Diagnosing Search Behavior and Failure Modes in Long-Horizon Search Agents](https://doi.org/10.48550/arxiv.2608.01913) · 10.48550/arxiv.2608.01913 | 2026 | arXiv | observational | yes |
| 2 | [BrowseComp-Plus: A More Fair and Transparent Evaluation Benchmark of Deep-Research Agent](https://doi.org/10.48550/arxiv.2508.06600) · 10.48550/arxiv.2508.06600 | 2025 | arXiv (Cornell University) | experimental | yes |
| 3 | [Projecting BrowseComp-Plus onto ClimbMix: Toward More Realistic Corpora for Agentic Search](https://arxiv.org/abs/2608.20317) | 2026 | — | experimental | yes |
| 4 | [Structurally-bounded Agentic Graph Exploration for Evidence-Grounded Scholarly DeepSearch](https://doi.org/10.48550/arxiv.2608.24809) · 10.48550/arxiv.2608.24809 | 2026 | arXiv | experimental | yes |
| 5 | [LLM-guided Hierarchical Search for End-to-end Reasoning Intensive Retrieval](https://arxiv.org/abs/2510.13217) | 2025 | — | experimental | yes |
| 6 | [Patience is all you need! An agentic system for performing scientific literature review](https://doi.org/10.48550/arxiv.2504.08752) · 10.48550/arxiv.2504.08752 | 2025 | arXiv.org | experimental | yes |
| 7 | [OpenScholar: Synthesizing Scientific Literature with Retrieval-augmented LMs](https://doi.org/10.48550/arxiv.2411.14199) · 10.48550/arxiv.2411.14199 | 2024 | arXiv.org | experimental | yes |
| 8 | [LitSearch: A Retrieval Benchmark for Scientific Literature Search](https://doi.org/10.48550/arxiv.2407.18940) · 10.48550/arxiv.2407.18940 | 2024 | Conference on Empirical Methods in Natural Language Processing | experimental | yes |
| 9 | [Towards Recursive Self-Evolving Agentic Literature Retrieval](https://doi.org/10.48550/arxiv.2605.14306) · 10.48550/arxiv.2605.14306 | 2026 | arXiv | experimental | yes |
| 10 | [Deep Research Agents: A Systematic Examination And Roadmap](https://doi.org/10.48550/arxiv.2506.18096) · 10.48550/arxiv.2506.18096 | 2025 | arXiv.org | other | yes |

## 1. Diagnosing Search Behavior and Failure Modes in Long-Horizon Search Agents

Qi Liu, Jiaxin Mao, Fengbin Zhu, Tat-Seng Chua · 2026 · arXiv · observational · overall 3/3

<https://doi.org/10.48550/arxiv.2608.01913>

**Key finding.** Across six agents on BrowseComp-Plus and BrowseComp, answer accuracy correlates more with cumulative retrieval recall than with number of searches, and top agents issue far fewer redundant queries.

**Why it made the cut.** contradicting · selected by score · strongest on C2 agentic mechanism gain (3/3). Provides direct evidence that agentic 'more searching' does not reliably improve outcomes, exactly the gain-failure evidence the brief asks us to reach for.

**Why it matters here.** Directly undercuts the premise that more agentic search effort produces better answers — shows search effort and answer quality are only weakly aligned, meaning a claimed 'agentic gain' may reflect evidence quality rather than the agentic mechanism itself.

**Method.** Trajectory-level diagnostic study with human-annotated document relevance judgments, comparing six deep-search agents with retrieval model and evaluation harness held fixed.

**Limitations.**

- Only six agents studied
- relies on BrowseComp-Plus/BrowseComp, general-knowledge benchmarks rather than literature-specific corpora

<sub>selected: score · criteria: C1 2/3 · C2 3/3 · C3 1/3 · C4 2/3 · C5 3/3 · flags: contradicts, methods_paper · verified 2026-08-27 via openalex, arxiv</sub>

## 2. BrowseComp-Plus: A More Fair and Transparent Evaluation Benchmark of Deep-Research Agent

Zijian Chen, Xueguang Ma, Shengyao Zhuang, Ping Nie et al. · 2025 · arXiv (Cornell University) · experimental · overall 3/3

<https://doi.org/10.48550/arxiv.2508.06600>

**Key finding.** On BrowseComp-Plus's fixed, human-verified corpus, Search-R1 with BM25 achieves only 3.86% accuracy while GPT-5 reaches 55.9%, and pairing GPT-5 with a Qwen3-Embedding-8B retriever raises this to 70.1% with fewer search calls.

**Why it made the cut.** design-changing · selected by score · strongest on C1 baseline recall ceiling (3/3). The central controlled benchmark the field now uses to disentangle retriever from agent contribution — foundational for both the baseline-recall and benchmark-construction questions.

**Why it matters here.** Gives a concrete, controlled baseline recall/accuracy ceiling (BM25 at 3.86%) against which any claimed agentic gain must be measured, and exemplifies the kind of rigorous benchmark construction the brief's benchmark-construction question asks us to check every reported number against.

**Method.** Benchmark construction paper: derives a fixed corpus from BrowseComp with human-verified supporting documents and mined hard negatives, enabling disentangled evaluation of retriever vs. agent LLM contributions.

**Limitations.**

- Corpus derived per-query from the benchmark's own supporting documents, which later work suggests may inflate retrieval performance relative to more realistic corpora

<sub>selected: score · criteria: C1 3/3 · C2 1/3 · C3 1/3 · C4 3/3 · C5 1/3 · flags: methods_paper · verified 2026-08-27 via openalex, arxiv</sub>

## 3. Projecting BrowseComp-Plus onto ClimbMix: Toward More Realistic Corpora for Agentic Search

Sahel Sharifymoghaddam, Lin Gu, Yijun Ge, Jimmy Lin · 2026 · no venue · experimental · overall 3/3

<https://arxiv.org/abs/2608.20317>

**Key finding.** Relocating BrowseComp-Plus's evidence into a more realistic 553M-document corpus drops the strongest agent's evidence recall from 84.3% to 21.4% while search calls rise 63%, though answer accuracy falls only five points.

**Why it made the cut.** contradicting · selected by score · strongest on C4 benchmark construction (3/3). The clearest evidence in the shortlist that a widely used benchmark's construction inflates reported recall, directly answering the brief's hardest question.

**Why it matters here.** Directly shows a benchmark-construction artifact — a corpus built per-query from a benchmark's own supporting documents — inflates reported evidence recall relative to a more realistic corpus, precisely the gain-replication failure the brief's hardest question asks us to find.

**Method.** A projection pipeline decomposes benchmark questions into atomic reasoning hops and re-grounds each hop in a pretraining corpus assembled without reference to any benchmark, verified by automatic check, an independent agent, and human review; applied to 830 BrowseComp-Plus questions, yielding 57 fully grounded questions.

**Limitations.**

- Yields only 57 fully grounded questions out of 830, a small evaluation set
- Answer accuracy dropped only modestly despite the large recall drop, so the practical import needs more evidence

<sub>selected: score · criteria: C1 1/3 · C2 1/3 · C3 1/3 · C4 3/3 · C5 3/3 · flags: contradicts, methods_paper · verified 2026-08-27 via arxiv, s2</sub>

## 4. Structurally-bounded Agentic Graph Exploration for Evidence-Grounded Scholarly DeepSearch

Rima Hazra, Sayan Layek, Somnath Banerjee, Soumen Chakrabarti et al. · 2026 · arXiv · experimental · overall 3/3

<https://doi.org/10.48550/arxiv.2608.24809>

**Key finding.** Crase, a bounded citation-graph-traversal agent, outperforms proprietary deep research agents by up to 3x recall@50 at roughly a third of the cost.

**Why it made the cut.** design-changing · selected by score · strongest on C2 agentic mechanism gain (3/3). A clean isolation of the citation-graph-traversal mechanism's contribution, central to decision 2 of the brief.

**Why it matters here.** Isolates citation-graph traversal as the specific mechanism carrying the reported gain, with an explicit, inspectable stopping condition — directly answers what agentic design adds for a named mechanism rather than an undifferentiated agent.

**Method.** Single seed search, 1.5-hop citation-graph expansion, entailment-based edge pruning, recency-aware random-walk ranking; evaluated on LitSearch and a further 500K-paper arXiv corpus benchmark.

**Limitations.**

- Compared against proprietary agents rather than the plain single-query baseline directly
- Evaluated on a bounded 500K-paper arXiv corpus, may not generalize to broader corpora

<sub>selected: score · criteria: C1 2/3 · C2 3/3 · C3 2/3 · C4 1/3 · C5 1/3 · flags: methods_paper · verified 2026-08-27 via arxiv</sub>

## 5. LLM-guided Hierarchical Search for End-to-end Reasoning Intensive Retrieval

Nilesh Gupta, Wei-Cheng Chang, N. Bui, Cho-Jui Hsieh et al. · 2025 · no venue · experimental · overall 3/3

<https://arxiv.org/abs/2510.13217>

**Key finding.** LATTICE matches the best fine-tuned ensemble baseline (46.7 nDCG@10) on the reasoning-intensive BRIGHT benchmark with a single off-the-shelf LLM, and an ensemble variant reaches 49.1 nDCG@10, while remaining competitive on SciFact and SciDocs.

**Why it made the cut.** plan-influencing · selected by score · strongest on C3 retrieval/reranking method (3/3). A retrieval-layer mechanism (hierarchical LLM-guided traversal) evaluated partly on scientific-literature benchmarks, directly informing what underlies agentic literature search retrieval.

**Why it matters here.** A hierarchical-traversal retrieval method that removes the embedding retriever from the loop entirely, giving a concrete alternative underlying mechanism for the retrieval layer of agentic search, and its inclusion of SciFact/SciDocs places it partly in our domain.

**Method.** LLM-guided hierarchical search index built top-down from multi-level document summaries, with calibrated path-aggregated traversal replacing an embedding retriever entirely; compared against sliding-window reranking baselines.

**Limitations.**

- Best gains reported on BRIGHT, a mixed-domain reasoning benchmark, not solely scientific literature
- Reranking offers a better tradeoff at low token budgets — the traversal method's advantage is budget-dependent

<sub>selected: score · criteria: C1 2/3 · C2 2/3 · C3 3/3 · C4 1/3 · C5 1/3 · flags: methods_paper · verified 2026-08-27 via arxiv, s2</sub>

## 6. Patience is all you need! An agentic system for performing scientific literature review

David W. Brett, Anniek Myatt · 2025 · arXiv.org · experimental · overall 3/3

<https://doi.org/10.48550/arxiv.2504.08752>

**Key finding.** placeholder

**Why it made the cut.** contradicting · selected by score · strongest on C3 retrieval/reranking method (3/3). placeholder

**Why it matters here.** placeholder

**Method.** placeholder

**Limitations.**

- placeholder

<sub>selected: score · criteria: C1 2/3 · C2 1/3 · C3 3/3 · C4 1/3 · C5 2/3 · flags: contradicts · verified 2026-08-27 via openalex, arxiv</sub>

## 7. OpenScholar: Synthesizing Scientific Literature with Retrieval-augmented LMs

Akari Asai, Jacqueline He, Rulin Shao, Weijia Shi et al. · 2024 · arXiv.org · experimental · overall 3/3

<https://doi.org/10.48550/arxiv.2411.14199>

**Key finding.** OpenScholar-8B, retrieving from 45 million open-access papers, outperforms GPT-4o by 5% and PaperQA2 by 7% in correctness on the new ScholarQABench (2,967 expert-written queries), while GPT-4o hallucinates citations 78-90% of the time versus OpenScholar's human-level citation accuracy.

**Why it made the cut.** design-changing · selected by score · strongest on C3 retrieval/reranking method (3/3). A central, in-domain system-and-benchmark paper directly answering the brief's core setting: scientific-literature synthesis, retrieval-augmented generation, and a large expert-built benchmark with numeric baseline comparisons.

**Why it matters here.** Quantifies both a benchmark-construction approach for scientific literature QA (thousands of expert queries, human evals) and the size of the gain a retrieval-plus-feedback system delivers over closed-book LLMs and an existing agentic baseline (PaperQA2), giving concrete numbers to calibrate claimed improvements against.

**Method.** Specialized retrieval-augmented LM with a self-feedback inference loop, evaluated on a new large-scale multi-domain benchmark (ScholarQABench) with human expert evaluation; abstract-only for full pipeline details.

**Limitations.**

- Comparisons are correctness/citation-accuracy based rather than explicit recall/precision against a single-query search baseline
- abstract does not isolate which component (retriever vs. self-feedback loop) drives the gain

<sub>selected: score · criteria: C1 2/3 · C2 1/3 · C3 3/3 · C4 3/3 · C5 0/3 · flags: methods_paper · verified 2026-08-27 via openalex, arxiv</sub>

## 8. LitSearch: A Retrieval Benchmark for Scientific Literature Search

Anirudh Ajith, Mengzhou Xia, Alexis Chevalier, Tanya Goyal et al. · 2024 · Conference on Empirical Methods in Natural Language Processing · experimental · overall 3/3

<https://doi.org/10.48550/arxiv.2407.18940>

**Key finding.** On LitSearch's 597 realistic literature-search queries, BM25 trails state-of-the-art dense retrievers by 24.8 points absolute recall@5, LLM reranking adds a further 4.4% over the best dense retriever, and commercial search engines lag the best dense retriever by 32 points.

**Why it made the cut.** design-changing · selected by backfill · strongest on C1 baseline recall ceiling (3/3). The most direct evidence for the brief's first and third decisions: a purpose-built, well-documented literature-search benchmark quantifying the single-query recall ceiling and the added value of reranking.

**Why it matters here.** Directly establishes the single-query database-search recall ceiling (BM25 vs. dense vs. commercial engines) the brief's decision 1 asks for, and shows how benchmark construction shapes what numbers are comparable — the clearest anchor for both C1 and C4.

**Method.** New retrieval benchmark built from GPT-4-generated questions (from inline-citation paragraphs) plus author-written questions about recent papers, expert-vetted; benchmarked against retrieval models and two LLM reranking pipelines; abstract-only for full details.

**Limitations.**

- Domain limited to recent ML/NLP papers, may not generalize to other scientific fields
- reranking gains (4.4%) are modest relative to the BM25-to-dense gap, suggesting headline agentic gains beyond dense retrieval plus reranking may be smaller than assumed

<sub>selected: backfill · criteria: C1 3/3 · C2 0/3 · C3 2/3 · C4 3/3 · C5 1/3 · flags: methods_paper · verified 2026-08-27 via openalex, arxiv</sub>

## 9. Towards Recursive Self-Evolving Agentic Literature Retrieval

Yuwen Du, Tian Jin, Jing Kang, Xianghe Pang et al. · 2026 · arXiv · experimental · overall 3/3

<https://doi.org/10.48550/arxiv.2605.14306>

**Key finding.** PaSaMaster achieves a 16.5x higher F1-score than Google Scholar and 37.8% higher F1-score than GPT-5.2 across 38 disciplines in PaSaMaster-Bench, at about 1% of the cost, while reducing source hallucination from 32.66% to zero.

**Why it made the cut.** design-changing · selected by backfill · strongest on C1 baseline recall ceiling (3/3). Provides an explicit single-query search baseline comparison and a quantified agentic gain, squarely answering the brief's first two decision questions.

**Why it matters here.** Directly anchors the recall-ceiling comparison against a single-query search baseline (Google Scholar) and quantifies the agentic gain (16.5x F1), giving a concrete number to test the brief's premise against, and attributes hallucination elimination to verified-source ranking specifically.

**Method.** A recursive self-evolving agentic retrieval system that separates frontier-LLM intent understanding from lightweight-model retrieval/scoring, ranking only verified papers; evaluated against Google Scholar and GPT-5.2 on a 38-discipline custom benchmark.

**Limitations.**

- PaSaMaster-Bench is self-constructed, so construction and labeling details need independent scrutiny
- GPT-5.2 comparison may not represent the strongest possible single-query database baseline

<sub>selected: backfill · criteria: C1 3/3 · C2 2/3 · C3 2/3 · C4 1/3 · C5 0/3 · flags: methods_paper · verified 2026-08-27 via openalex, arxiv</sub>

## 10. Deep Research Agents: A Systematic Examination And Roadmap

Yuxuan Huang, Yihang Chen, Haozhen Zhang, Kang Li et al. · 2025 · arXiv.org · other · overall 3/3

<https://doi.org/10.48550/arxiv.2506.18096>

**Key finding.** The survey taxonomizes Deep Research agent architectures (static vs dynamic workflows, single- vs multi-agent) and identifies current benchmarks' key limitations — restricted external-knowledge access, sequential execution inefficiency, and metric-objective misalignment.

**Why it made the cut.** foundational · selected by review · strongest on C2 agentic mechanism gain (2/3). The synthesis paper the rest of this literature argues with — foundational orientation for the whole scan and source of the benchmark-critique framework.

**Why it matters here.** Gives the orienting taxonomy and a critical inventory of benchmark weaknesses that the benchmark-construction question needs as a map before assessing any individual benchmark claim.

**Method.** Narrative systematic examination and roadmap of Deep Research agent architectures, tool-use frameworks and evaluation practices; abstract-only for specific findings.

**Limitations.**

- Narrative review, not a systematic-review protocol
- Abstract gives no quantitative findings to weigh against specific system claims

<sub>selected: review · criteria: C1 1/3 · C2 2/3 · C3 1/3 · C4 2/3 · C5 1/3 · flags: review · verified 2026-08-27 via arxiv</sub>

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

- [PaSa: An LLM Agent for Comprehensive Academic Paper Search](https://doi.org/10.48550/arxiv.2501.10120) (2025) — overall 3/3
- [AI's Capability in Assisting Scientific Research in Physics, Astrophysics, and Cosmology I: Literature Review](https://doi.org/10.48550/arxiv.2607.25672) (2026) — overall 3/3
- [ReBOL: Retrieval via Bayesian Optimization with Batched LLM Relevance Observations and Query Reformulation](https://doi.org/10.48550/arxiv.2603.20513) (2026) — overall 3/3
- [Multi-Agent System for Scientific Literature Search and Recommendation](https://doi.org/10.1109/icssas66150.2025.11081082) (2025) — overall 3/3
- [Search-Time Contamination in Deep Research Agents: Measuring Performance Inflation in Public Benchmark Evaluation](https://doi.org/10.48550/arxiv.2606.05241) (2026) — overall 3/3
