# Evidence scan — p11-t2

Run `/Users/nabergoj/Projects/research-scan/research/experiments/phase14/runs/p11-t2/C/rep5/run` · brief `/Users/nabergoj/Projects/research-scan/research/experiments/phase14/runs/p11-t2/C/rep5/run/brief.md` · rendered 2026-08-27

| # | Paper | Year | Venue | Evidence | Verified |
|---|---|---|---|---|---|
| 1 | [When to use Graphs in RAG: A Comprehensive Analysis for Graph Retrieval-Augmented Generation](https://doi.org/10.48550/arxiv.2506.05690) · 10.48550/arxiv.2506.05690 | 2025 | arXiv.org | experimental | yes |
| 2 | [BRIGHT: A Realistic and Challenging Benchmark for Reasoning-Intensive Retrieval](https://doi.org/10.48550/arxiv.2407.12883) · 10.48550/arxiv.2407.12883 | 2024 | International Conference on Learning Representations | experimental | yes |
| 3 | [Diagnosing Search Behavior and Failure Modes in Long-Horizon Search Agents](https://doi.org/10.48550/arxiv.2608.01913) · 10.48550/arxiv.2608.01913 | 2026 | arXiv | experimental | yes |
| 4 | [Towards Recursive Self-Evolving Agentic Literature Retrieval](https://doi.org/10.48550/arxiv.2605.14306) · 10.48550/arxiv.2605.14306 | 2026 | arXiv | experimental | yes |
| 5 | [BrowseComp-Plus: A More Fair and Transparent Evaluation Benchmark of Deep-Research Agent](https://doi.org/10.48550/arxiv.2508.06600) · 10.48550/arxiv.2508.06600 | 2025 | arXiv (Cornell University) | experimental | yes |
| 6 | [Deep Research Agents: A Systematic Examination And Roadmap](https://doi.org/10.48550/arxiv.2506.18096) · 10.48550/arxiv.2506.18096 | 2025 | arXiv.org | other | yes |
| 7 | [Projecting BrowseComp-Plus onto ClimbMix: Toward More Realistic Corpora for Agentic Search](https://arxiv.org/abs/2608.20317) | 2026 | — | experimental | yes |
| 8 | [Patience is all you need! An agentic system for performing scientific literature review](https://doi.org/10.48550/arxiv.2504.08752) · 10.48550/arxiv.2504.08752 | 2025 | arXiv.org | experimental | yes |
| 9 | [LitSearch: A Retrieval Benchmark for Scientific Literature Search](https://doi.org/10.48550/arxiv.2407.18940) · 10.48550/arxiv.2407.18940 | 2024 | Conference on Empirical Methods in Natural Language Processing | experimental | yes |
| 10 | [Structurally-bounded Agentic Graph Exploration for Evidence-Grounded Scholarly DeepSearch](https://doi.org/10.48550/arxiv.2608.24809) · 10.48550/arxiv.2608.24809 | 2026 | arXiv | experimental | yes |

## 1. When to use Graphs in RAG: A Comprehensive Analysis for Graph Retrieval-Augmented Generation

Zhishang Xiang, Chuan-Yu Wu, Qinggang Zhang, Shengyuan Chen et al. · 2025 · arXiv.org · experimental · overall 3/3

<https://doi.org/10.48550/arxiv.2506.05690>

**Key finding.** GraphRAG frequently underperforms vanilla RAG on many real-world tasks; GraphRAG-Bench systematically identifies the conditions under which graph structure does or does not measurably help retrieval and reasoning.

**Why it made the cut.** contradicting · selected by score · strongest on C1 baseline recall ceiling (3/3). Strongest available contradicting evidence that graph-based agentic retrieval reliably beats baseline search, with a directly transferable benchmark-construction template.

**Why it matters here.** Directly evidences that graph-traversal-based agentic gains do not always beat single-query baseline retrieval — the exact premise-challenging finding Q1/Q2/Q5 call for — and its staged-difficulty benchmark design is a template for building literature-search evaluation sets.

**Method.** Introduces GraphRAG-Bench, a benchmark with escalating-difficulty tasks (fact retrieval, complex reasoning, summarization, creative generation) evaluated end-to-end from graph construction through generation. Abstract-only.

**Limitations.**

- domain is general knowledge-graph RAG tasks, not scientific literature search specifically
- abstract does not give absolute performance numbers, only the qualitative pattern

<sub>selected: score · criteria: C1 3/3 · C2 3/3 · C3 2/3 · C4 3/3 · C5 3/3 · flags: contradicts, methods_paper · verified 2026-08-27 via openalex, arxiv</sub>

## 2. BRIGHT: A Realistic and Challenging Benchmark for Reasoning-Intensive Retrieval

Hongjin Su, Howard Yen, Mengzhou Xia, Weijia Shi et al. · 2024 · International Conference on Learning Representations · experimental · overall 3/3

<https://doi.org/10.48550/arxiv.2407.12883>

**Key finding.** The leading MTEB retriever (59.0 nDCG@10) scores only 18.3 nDCG@10 on BRIGHT's reasoning-intensive queries, while incorporating explicit query reasoning improves retrieval by up to 12.2 points.

**Why it made the cut.** foundational · selected by score · strongest on C1 baseline recall ceiling (3/3). Foundational, highly-cited quantification of the single-query search recall ceiling on complex queries and of benchmark-dependent performance collapse.

**Why it matters here.** Gives a concrete, numeric recall-ceiling collapse for single-query embedding search under complex queries (Q1) and shows that strong leaderboard performance does not generalize to a harder benchmark (Q4) — the exact pattern the brief must anchor claimed agentic gains against.

**Method.** Introduces BRIGHT, 1,384 real-world reasoning-intensive queries curated across economics, psychology, mathematics, and coding, with extensive evaluation of state-of-the-art retrievers.

**Limitations.**

- domains are economics/psychology/math/coding, not scientific-literature-search corpora specifically
- reasoning-intensive retrieval findings may not map directly onto citation-based literature search

<sub>selected: score · criteria: C1 3/3 · C2 2/3 · C3 2/3 · C4 3/3 · C5 2/3 · flags: contradicts, methods_paper · verified 2026-08-27 via openalex, arxiv</sub>

## 3. Diagnosing Search Behavior and Failure Modes in Long-Horizon Search Agents

Qi Liu, Jiaxin Mao, Fengbin Zhu, Tat-Seng Chua · 2026 · arXiv · experimental · overall 3/3

<https://doi.org/10.48550/arxiv.2608.01913>

**Key finding.** Across six agents on BrowseComp-Plus/BrowseComp, answer accuracy tracks cumulative retrieval recall far more than the number of searches or context consumed, and top agents issue far fewer redundant queries than weaker ones.

**Why it made the cut.** design-changing · selected by score · strongest on C2 agentic mechanism gain (3/3). A rare trajectory-level diagnostic showing where and why agentic search gains fail to materialize, bearing directly on decisions 2 and 4.

**Why it matters here.** Directly answers decision 2 and 4: shows that 'more agentic search effort' does not reliably translate into gains, decomposing failure into retrieval vs. utilization gaps, so the scan's premise that agentic depth is what carries the improvement needs qualifying by stopping criteria and evidence quality, not step count.

**Method.** Trajectory-level diagnosis using human-annotated document-level relevance judgments, retrieval model and evaluation harness held fixed across six agents on BrowseComp-Plus, validated on BrowseComp with an open-web API.

**Limitations.**

- single retrieval backend held fixed, so findings may not generalize across retrievers
- focused on QA-style deep search rather than academic paper retrieval specifically

<sub>selected: score · criteria: C1 1/3 · C2 3/3 · C3 1/3 · C4 2/3 · C5 3/3 · flags: contradicts · verified 2026-08-27 via openalex, arxiv</sub>

## 4. Towards Recursive Self-Evolving Agentic Literature Retrieval

Yuwen Du, Tian Jin, Jing Kang, Xianghe Pang et al. · 2026 · arXiv · experimental · overall 3/3

<https://doi.org/10.48550/arxiv.2605.14306>

**Key finding.** PaSaMaster achieves a 16.5x higher F1 than Google Scholar and 37.8% higher F1 than GPT-5.2 at about 1% of the cost across 38 disciplines, while cutting source hallucination from 32.66% to zero.

**Why it made the cut.** design-changing · selected by score · strongest on C1 baseline recall ceiling (3/3). The clearest available quantitative baseline-vs-agentic-gain comparison, directly answering the brief's first two questions.

**Why it matters here.** Directly quantifies the recall/F1 gap between a single-query search tool (Google Scholar) and an iterative agentic system, giving the brief's Q1 and Q2 concrete numbers rather than an unanchored claim.

**Method.** Recursive self-evolving agentic retrieval system separating frontier-LLM intent understanding from lightweight-model retrieval/scoring, evaluated on PaSaMaster-Bench (38 disciplines). Abstract-only.

**Limitations.**

- PaSaMaster-Bench's query source, labeling, and contamination controls are not described in the abstract
- self-reported comparison against the authors' own new benchmark

<sub>selected: score · criteria: C1 3/3 · C2 2/3 · C3 3/3 · C4 2/3 · C5 0/3 · flags: methods_paper · verified 2026-08-27 via openalex, arxiv</sub>

## 5. BrowseComp-Plus: A More Fair and Transparent Evaluation Benchmark of Deep-Research Agent

Zijian Chen, Xueguang Ma, Shengyao Zhuang, Ping Nie et al. · 2025 · arXiv (Cornell University) · experimental · overall 3/3

<https://doi.org/10.48550/arxiv.2508.06600>

**Key finding.** On a fixed, human-verified corpus, Search-R1 with BM25 reaches only 3.86% accuracy while GPT-5 reaches 55.9%, rising to 70.1% when paired with a Qwen3-Embedding-8B retriever and fewer search calls.

**Why it made the cut.** foundational · selected by score · strongest on C1 baseline recall ceiling (3/3). The fixed-corpus benchmark this literature's diagnostic and replication-failure papers are built on and argue against, directly serving decisions 1 and 3.

**Why it matters here.** Supplies exactly the baseline-ceiling numbers decision 1 needs (BM25 vs. dense retriever vs. full agent) and is the fixed-corpus benchmark that later papers in this scan (diagnostic and corpus-projection studies) build directly on, making it the reference point for what a reported gain is measured against.

**Method.** Benchmark construction: fixed corpus derived from BrowseComp with human-verified supporting documents and mined hard negatives, enabling disentangled comparison of deep-research agent reasoning from retriever quality.

**Limitations.**

- corpus and queries derive from BrowseComp, a general web-browsing benchmark, not a scientific-literature-search corpus specifically
- supporting documents and negatives were mined per-query, a construction choice later work (ClimbMix projection) shows can inflate apparent retrieval difficulty calibration

<sub>selected: score · criteria: C1 3/3 · C2 1/3 · C3 2/3 · C4 3/3 · C5 0/3 · flags: methods_paper · verified 2026-08-27 via openalex, arxiv</sub>

## 6. Deep Research Agents: A Systematic Examination And Roadmap

Yuxuan Huang, Yihang Chen, Haozhen Zhang, Kang Li et al. · 2025 · arXiv.org · other · overall 3/3

<https://doi.org/10.48550/arxiv.2506.18096>

**Key finding.** A systematic taxonomy of Deep Research agents finds that current benchmarks suffer from restricted access to external knowledge, sequential execution inefficiencies, and misalignment between evaluation metrics and agents' practical objectives.

**Why it made the cut.** plan-influencing · selected by score · strongest on C4 benchmark construction (3/3). The field's own critical synthesis of benchmark and architecture limitations, directly answering decisions 2-4 at a survey level and anchoring which sub-claims deserve primary-source follow-up.

**Why it matters here.** Synthesizes exactly the benchmark-construction concerns decision 3 asks about and flags metric/objective misalignment relevant to decision 4, giving the scan a map of where the field's evaluation is known to be weak rather than a single point estimate.

**Method.** abstract-only; narrative/systematic review proposing a taxonomy over API-based vs. browser-based retrieval, tool-use frameworks, and static vs. dynamic agent workflows, with critical evaluation of existing benchmarks.

**Limitations.**

- a survey/taxonomy rather than new empirical measurement, so its claims are secondhand
- abstract gives no quantitative figures to anchor comparisons

<sub>selected: score · criteria: C1 1/3 · C2 2/3 · C3 1/3 · C4 3/3 · C5 2/3 · flags: review · verified 2026-08-27 via arxiv</sub>

## 7. Projecting BrowseComp-Plus onto ClimbMix: Toward More Realistic Corpora for Agentic Search

Sahel Sharifymoghaddam, Lin Gu, Yijun Ge, Jimmy Lin · 2026 · no venue · experimental · overall 3/3

<https://arxiv.org/abs/2608.20317>

**Key finding.** Relocating BrowseComp-Plus's evidence into the independently-built ClimbMix corpus drops the strongest agent's evidence recall from 84.3% to 21.4% (and costs it five points of answer accuracy) while it issues 63% more search calls.

**Why it made the cut.** contradicting · selected by score · strongest on C4 benchmark construction (3/3). Directly shows a reported agentic recall figure shrinking under an independently constructed corpus, the exact gain-replication-failure evidence decision 4 asks the scan to find.

**Why it matters here.** The clearest demonstration in this scan of decision 4: a reported agentic evidence-recall figure collapses by over 60 points once the per-query-curated corpus is replaced by an independently built one, showing that benchmark construction (query-matched negatives and evidence) was inflating the original number.

**Method.** Projection pipeline decomposing each question into atomic reasoning hops, grounding each hop in a 400B-token, 553M-document corpus built without reference to any benchmark, verified by automatic checks, an independent agent, and human review; applied to 830 BrowseComp-Plus questions yielding 57 fully grounded questions.

**Limitations.**

- yields only 57 fully grounded questions from 830, a substantial reduction in evaluation coverage
- single case study transferring one benchmark onto one alternate corpus, not yet a general result across benchmarks

<sub>selected: score · criteria: C1 2/3 · C2 1/3 · C3 0/3 · C4 3/3 · C5 3/3 · flags: contradicts, methods_paper · verified 2026-08-27 via arxiv, s2</sub>

## 8. Patience is all you need! An agentic system for performing scientific literature review

David W. Brett, Anniek Myatt · 2025 · arXiv.org · experimental · overall 3/3

<https://doi.org/10.48550/arxiv.2504.08752>

**Key finding.** Sparse (keyword-based) retrieval achieves results close to state-of-the-art dense retrieval for literature review generation on biology QA benchmarks, without added infrastructure complexity.

**Why it made the cut.** design-changing · selected by score · strongest on C1 baseline recall ceiling (3/3). Directly tests the baseline recall/precision question (C1) and interrogates whether added retrieval complexity is needed, bearing on whether agentic gains are real.

**Why it matters here.** Directly answers whether simple sparse baseline retrieval already achieves near-agentic performance, tempering the premise that dense or agentic complexity is required for gains.

**Method.** LLM-based search-and-distillation system evaluated against biology literature benchmarks; compares sparse vs dense retrieval and proposes coverage-boosting steps. Abstract-only for specifics.

**Limitations.**

- Evaluated only on biology-domain QA benchmarks
- Abstract gives no quantitative recall/precision numbers
- Compares retrieval methods rather than a full agentic pipeline

<sub>selected: score · criteria: C1 3/3 · C2 1/3 · C3 2/3 · C4 1/3 · C5 2/3 · flags: methods_paper · verified 2026-08-27 via openalex, arxiv</sub>

## 9. LitSearch: A Retrieval Benchmark for Scientific Literature Search

Anirudh Ajith, Mengzhou Xia, Alexis Chevalier, Tanya Goyal et al. · 2024 · Conference on Empirical Methods in Natural Language Processing · experimental · overall 3/3

<https://doi.org/10.48550/arxiv.2407.18940>

**Key finding.** On LitSearch (597 realistic literature-search queries), BM25 lags state-of-the-art dense retrievers by 24.8% absolute recall@5, LLM-based reranking further improves the best dense retriever by 4.4%, and commercial search engines/Google Search trail the best dense retriever by 32 points.

**Why it made the cut.** foundational · selected by backfill · strongest on C1 baseline recall ceiling (3/3). The direct answer to the brief's first decision question (recall ceiling of single-query search) and a rigorously constructed benchmark that later literature-search-agent work is naturally measured against.

**Why it matters here.** Directly establishes the single-query baseline recall ceiling (BM25 vs dense vs commercial search) that the brief's first decision question needs and details exactly how the evaluation set was constructed, a benchmark precedent other agentic systems should be measured against.

**Method.** New retrieval benchmark built from GPT-4-generated questions over cited paragraphs plus author-written queries about recent papers, expert-validated; benchmarks state-of-the-art retrievers and LLM reranking pipelines.

**Limitations.**

- Restricted to recent ML/NLP papers, not all scientific domains
- Evaluates retrieval methods, not full agentic (multi-step or graph-traversal) pipelines

<sub>selected: backfill · criteria: C1 3/3 · C2 0/3 · C3 2/3 · C4 3/3 · C5 1/3 · flags: methods_paper · verified 2026-08-27 via openalex, arxiv</sub>

## 10. Structurally-bounded Agentic Graph Exploration for Evidence-Grounded Scholarly DeepSearch

Rima Hazra, Sayan Layek, Somnath Banerjee, Soumen Chakrabarti et al. · 2026 · arXiv · experimental · overall 3/3

<https://doi.org/10.48550/arxiv.2608.24809>

**Key finding.** A bounded pipeline of one-shot seed search, 1.5-hop citation expansion, entailment-based edge pruning, and recency-aware random-walk ranking outperforms proprietary deep-research agents by up to 3x recall@50 at roughly a third of the cost on LitSearch.

**Why it made the cut.** design-changing · selected by backfill · strongest on C2 agentic mechanism gain (3/3). Isolates citation-graph traversal as the mechanism carrying the reported gain, directly answering decision 2 with a controlled ablation-style design.

**Why it matters here.** Directly isolates citation-graph traversal as the specific agentic move carrying the gain, exactly the attribution decision 2 asks for, and shows a bounded, cheaper design beating open-ended agentic search rather than confirming the open-ended premise.

**Method.** Fixed, inspectable pipeline (not an open-ended search loop) evaluated against deep research agents on LitSearch and one further benchmark over a 500K-paper arXiv corpus.

**Limitations.**

- evaluated on a single 500K-paper arXiv corpus, not the broader literature
- recall@50 comparison against proprietary baselines may reflect prompting differences rather than pure mechanism differences

<sub>selected: backfill · criteria: C1 1/3 · C2 3/3 · C3 3/3 · C4 1/3 · C5 0/3 · flags: methods_paper · verified 2026-08-27 via arxiv</sub>

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

- [LLM-guided Hierarchical Search for End-to-end Reasoning Intensive Retrieval](https://arxiv.org/abs/2510.13217) (2025) — overall 3/3
- [Deep Research: A Survey of Autonomous Research Agents](https://doi.org/10.48550/arxiv.2508.12752) (2025) — overall 3/3
- [Multi-Agent System for Scientific Literature Search and Recommendation](https://doi.org/10.1109/icssas66150.2025.11081082) (2025) — overall 3/3
- [CG-RAG: Research Question Answering by Citation Graph Retrieval-Augmented LLMs](https://doi.org/10.1145/3726302.3729920) (2025) — overall 3/3
- [OpenScholar: Synthesizing Scientific Literature with Retrieval-augmented LMs](https://doi.org/10.48550/arxiv.2411.14199) (2024) — overall 3/3
