# Evidence scan — p11-t2

Run `/Users/nabergoj/Projects/research-scan/research/experiments/phase14/runs/p11-t2/C/rep3/run` · brief `/Users/nabergoj/Projects/research-scan/research/experiments/phase14/runs/p11-t2/C/rep3/run/brief.md` · rendered 2026-08-26

| # | Paper | Year | Venue | Evidence | Verified |
|---|---|---|---|---|---|
| 1 | [When to use Graphs in RAG: A Comprehensive Analysis for Graph Retrieval-Augmented Generation](https://doi.org/10.48550/arxiv.2506.05690) · 10.48550/arxiv.2506.05690 | 2025 | arXiv.org | experimental | yes |
| 2 | [BrowseComp-Plus: A More Fair and Transparent Evaluation Benchmark of Deep-Research Agent](https://doi.org/10.48550/arxiv.2508.06600) · 10.48550/arxiv.2508.06600 | 2025 | arXiv (Cornell University) | experimental | yes |
| 3 | [Towards Recursive Self-Evolving Agentic Literature Retrieval](https://doi.org/10.48550/arxiv.2605.14306) · 10.48550/arxiv.2605.14306 | 2026 | arXiv | experimental | yes |
| 4 | [Patience is all you need! An agentic system for performing scientific literature review](https://doi.org/10.48550/arxiv.2504.08752) · 10.48550/arxiv.2504.08752 | 2025 | arXiv.org | experimental | yes |
| 5 | [Fact, Fetch, and Reason: A Unified Evaluation of Retrieval-Augmented Generation](https://doi.org/10.48550/arxiv.2409.12941) · 10.48550/arxiv.2409.12941 | 2024 | North American Chapter of the Association for Computational Linguistics | experimental | yes |
| 6 | [LitSearch: A Retrieval Benchmark for Scientific Literature Search](https://doi.org/10.48550/arxiv.2407.18940) · 10.48550/arxiv.2407.18940 | 2024 | Conference on Empirical Methods in Natural Language Processing | experimental | yes |
| 7 | [Diagnosing Search Behavior and Failure Modes in Long-Horizon Search Agents](https://doi.org/10.48550/arxiv.2608.01913) · 10.48550/arxiv.2608.01913 | 2026 | arXiv | experimental | yes |
| 8 | [Deep Research Agents: A Systematic Examination And Roadmap](https://doi.org/10.48550/arxiv.2506.18096) · 10.48550/arxiv.2506.18096 | 2025 | arXiv.org | other | yes |
| 9 | [Is Grep All You Need? How Agent Harnesses Reshape Agentic Search](https://doi.org/10.48550/arxiv.2605.15184) · 10.48550/arxiv.2605.15184 | 2026 | arXiv.org | experimental | yes |
| 10 | [PaSa: An LLM Agent for Comprehensive Academic Paper Search](https://doi.org/10.48550/arxiv.2501.10120) · 10.48550/arxiv.2501.10120 | 2025 | Annual Meeting of the Association for Computational Linguistics | experimental | yes |

## 1. When to use Graphs in RAG: A Comprehensive Analysis for Graph Retrieval-Augmented Generation

Zhishang Xiang, Chuan-Yu Wu, Qinggang Zhang, Shengyuan Chen et al. · 2025 · arXiv.org · experimental · overall 3/3

<https://doi.org/10.48550/arxiv.2506.05690>

**Key finding.** GraphRAG frequently underperforms vanilla RAG on real-world tasks; GraphRAG-Bench systematically identifies the conditions (hierarchical retrieval, deep contextual reasoning) under which graph structure actually helps.

**Why it made the cut.** contradicting · selected by score · strongest on C2 agentic mechanism gain (3/3). The clearest evidence in the shortlist that a specific agentic mechanism (graph retrieval) does not reliably beat a simpler baseline, directly contradicting the brief's stated premise.

**Why it matters here.** Directly answers question 4: it shows the graph-traversal gain agentic designs are assumed to carry does not hold universally, which should make the scan skeptical of any citation-graph-traversal claim not tested under matched conditions.

**Method.** New benchmark (GraphRAG-Bench) spanning fact retrieval, complex reasoning, contextual summarization, and creative generation, with end-to-end pipeline evaluation from graph construction through generation.

**Limitations.**

- General-domain RAG evaluation, not scientific literature search specifically
- Findings about GraphRAG vs vanilla RAG may not directly generalize to citation-graph traversal over papers

<sub>selected: score · criteria: C1 1/3 · C2 3/3 · C3 2/3 · C4 3/3 · C5 3/3 · flags: contradicts, methods_paper · verified 2026-08-26 via openalex, arxiv</sub>

## 2. BrowseComp-Plus: A More Fair and Transparent Evaluation Benchmark of Deep-Research Agent

Zijian Chen, Xueguang Ma, Shengyao Zhuang, Ping Nie et al. · 2025 · arXiv (Cornell University) · experimental · overall 3/3

<https://doi.org/10.48550/arxiv.2508.06600>

**Key finding.** Search-R1 with a BM25 retriever achieves only 3.86% accuracy versus GPT-5's 55.9%, while GPT-5 paired with a Qwen3-Embedding-8B retriever reaches 70.1% accuracy with fewer search calls, on a fixed human-verified corpus.

**Why it made the cut.** foundational · selected by score · strongest on C1 baseline recall ceiling (3/3). The foundational benchmark-construction and baseline-recall paper this scan's other benchmarks are built against -- answers decisions 1 and 3 directly and anchors decision 4.

**Why it matters here.** Directly establishes the baseline recall/accuracy ceiling of single-query retrieval (BM25) versus stronger retrievers and full agentic systems, and is the benchmark-construction precedent several other papers in this scan build on or critique.

**Method.** Introduces BrowseComp-Plus, a fixed curated corpus derived from BrowseComp with human-verified supporting documents and mined hard negatives, enabling controlled comparison of deep-research agents and retrievers.

**Limitations.**

- corpus derived from BrowseComp's own query-selected documents, later shown to inflate apparent recall relative to a more realistic corpus
- focused on general web-style queries, not literature-search-specific queries

<sub>selected: score · criteria: C1 3/3 · C2 2/3 · C3 2/3 · C4 3/3 · C5 1/3 · flags: methods_paper · verified 2026-08-26 via openalex, arxiv</sub>

## 3. Towards Recursive Self-Evolving Agentic Literature Retrieval

Yuwen Du, Tian Jin, Jing Kang, Xianghe Pang et al. · 2026 · arXiv · experimental · overall 3/3

<https://doi.org/10.48550/arxiv.2605.14306>

**Key finding.** PaSaMaster achieves a 16.5x higher F1-score than Google Scholar and 37.8% higher F1 than GPT-5.2 at about 1% of the cost, while cutting source hallucination from 32.66% to zero, across 38 disciplines in PaSaMaster-Bench.

**Why it made the cut.** design-changing · selected by score · strongest on C1 baseline recall ceiling (3/3). The most direct evidence in this shortlist for the exact single-query-vs-agentic-gain comparison the brief's first decision asks for.

**Why it matters here.** Directly anchors question 1 by quantifying the gap between plain search-engine querying (Google Scholar) and an iterative agentic system, giving a concrete magnitude for the premise the brief wants tested rather than assumed.

**Method.** Recursive self-evolving agent separating frontier-LLM intent understanding from lightweight-model retrieval/scoring over verified papers; evaluated on a custom 38-discipline benchmark against Google Scholar and GPT-5.2 baselines.

**Limitations.**

- Benchmark and baselines are the authors' own construction, raising the contamination/comparability concerns the brief flags as important (C4)
- No independent replication or alternative-metric check reported

<sub>selected: score · criteria: C1 3/3 · C2 2/3 · C3 3/3 · C4 2/3 · C5 0/3 · flags: methods_paper · verified 2026-08-26 via openalex, arxiv</sub>

## 4. Patience is all you need! An agentic system for performing scientific literature review

David W. Brett, Anniek Myatt · 2025 · arXiv.org · experimental · overall 3/3

<https://doi.org/10.48550/arxiv.2504.08752>

**Key finding.** A keyword-based (sparse) retrieval and distillation system for scientific literature review achieves results close to state-of-the-art dense retrieval on biology benchmarks, without the infrastructure overhead of dense retrieval.

**Why it made the cut.** contradicting · selected by score · strongest on C1 baseline recall ceiling (3/3). Empirically compares sparse vs dense retrieval for scientific literature review, bearing directly on the baseline recall ceiling and gain-replication questions.

**Why it matters here.** Directly challenges the premise that complex (dense/agentic) retrieval infrastructure is needed to beat single-query search, bearing squarely on the recall-ceiling question (Q1) and the replication question (Q4).

**Method.** LLM-based full-text search and distillation system evaluated against biology literature-review benchmark questions; abstract-only detail.

**Limitations.**

- biology-domain benchmark only
- abstract gives no quantitative recall numbers
- single-domain evaluation, generalization unclear

<sub>selected: score · criteria: C1 3/3 · C2 1/3 · C3 3/3 · C4 1/3 · C5 2/3 · flags: contradicts, methods_paper · verified 2026-08-26 via openalex, arxiv</sub>

## 5. Fact, Fetch, and Reason: A Unified Evaluation of Retrieval-Augmented Generation

Satyapriya Krishna, Kalpesh Krishna, Anhad Mohananey, S. Schwarcz et al. · 2024 · North American Chapter of the Association for Computational Linguistics · experimental · overall 3/3

<https://doi.org/10.48550/arxiv.2409.12941>

**Key finding.** State-of-the-art LLMs achieve only 0.40 accuracy on FRAMES multi-hop questions with no retrieval, rising to 0.66 with a multi-step retrieval pipeline (>50% improvement).

**Why it made the cut.** plan-influencing · selected by score · strongest on C1 baseline recall ceiling (3/3). Explicit no-retrieval vs multi-step-retrieval baseline comparison plus benchmark construction detail directly answers Q1 and Q3.

**Why it matters here.** Gives an explicit no-retrieval versus multi-step-retrieval baseline number, anchoring exactly the kind of comparison point the brief needs before crediting agentic gains, and models how to construct a demanding multi-hop evaluation set.

**Method.** New FRAMES benchmark of challenging multi-hop questions requiring multi-source integration; baseline (no-retrieval) versus multi-step retrieval pipeline compared.

**Limitations.**

- general knowledge/QA domain rather than scientific-literature search specifically
- does not test citation-graph traversal or crawling as agentic moves

<sub>selected: score · criteria: C1 3/3 · C2 2/3 · C3 2/3 · C4 3/3 · C5 0/3 · flags: methods_paper · verified 2026-08-26 via openalex, arxiv</sub>

## 6. LitSearch: A Retrieval Benchmark for Scientific Literature Search

Anirudh Ajith, Mengzhou Xia, Alexis Chevalier, Tanya Goyal et al. · 2024 · Conference on Empirical Methods in Natural Language Processing · experimental · overall 3/3

<https://doi.org/10.48550/arxiv.2407.18940>

**Key finding.** On LitSearch (597 realistic literature-search queries), there is a 24.8% absolute recall@5 gap between BM25 and state-of-the-art dense retrievers, with LLM-based reranking adding a further 4.4% improvement; commercial search engines lag the best dense retriever by 32 points.

**Why it made the cut.** foundational · selected by score · strongest on C1 baseline recall ceiling (3/3). Provides the quantitative single-query baseline recall ceiling and a rigorous, well-documented benchmark-construction methodology that anchors the brief's first and third decision questions.

**Why it matters here.** Gives the exact quantitative baseline recall ceiling (BM25 vs dense) the brief's Q1 needs, plus a transparent benchmark-construction methodology (Q3) that later agentic-search work is measured against.

**Method.** New retrieval benchmark built from GPT-4-generated questions from cited paragraphs plus author-written questions about recent papers, expert-verified; benchmarks BM25, dense retrievers, and LLM reranking pipelines.

**Limitations.**

- restricted to ML/NLP papers, not the full breadth of scientific literature
- does not evaluate agentic (multi-step, graph-traversal) systems, only single-pass retrieval and reranking

<sub>selected: score · criteria: C1 3/3 · C2 0/3 · C3 3/3 · C4 3/3 · C5 1/3 · flags: methods_paper · verified 2026-08-26 via openalex, arxiv</sub>

## 7. Diagnosing Search Behavior and Failure Modes in Long-Horizon Search Agents

Qi Liu, Jiaxin Mao, Fengbin Zhu, Tat-Seng Chua · 2026 · arXiv · experimental · overall 3/3

<https://doi.org/10.48550/arxiv.2608.01913>

**Key finding.** Across six agents on BrowseComp-Plus and BrowseComp, answer accuracy correlates more with cumulative retrieval recall than with number of searches, and useful evidence often appears early while agents keep searching unnecessarily.

**Why it made the cut.** contradicting · selected by score · strongest on C2 agentic mechanism gain (3/3). Directly tests whether agentic moves (reformulation, iterative search) causally drive gains, exactly the mechanism decomposition and replication-failure evidence the brief needs.

**Why it matters here.** Directly addresses decisions 2 and 4: shows agentic search effort (extra queries, reformulation, context consumption) is only weakly linked to answer quality, undermining the assumption that more iterative search always drives gains.

**Method.** abstract-only; trajectory-level diagnosis using human-annotated document-level relevance judgments across six long-horizon search agents with retrieval model and harness held fixed.

**Limitations.**

- evaluated on BrowseComp-Plus/BrowseComp only, not literature-specific corpora
- retrieval model and harness held fixed, limiting generalization across retrievers

<sub>selected: score · criteria: C1 1/3 · C2 3/3 · C3 1/3 · C4 1/3 · C5 3/3 · flags: contradicts · verified 2026-08-26 via openalex, arxiv</sub>

## 8. Deep Research Agents: A Systematic Examination And Roadmap

Yuxuan Huang, Yihang Chen, Haozhen Zhang, Kang Li et al. · 2025 · arXiv.org · other · overall 3/3

<https://doi.org/10.48550/arxiv.2506.18096>

**Key finding.** Proposes a taxonomy of Deep Research agent architectures (static/dynamic workflows, single/multi-agent) and identifies key benchmark limitations, including restricted external-knowledge access, sequential execution inefficiencies, and misalignment between metrics and practical objectives.

**Why it made the cut.** foundational · selected by score · strongest on C4 benchmark construction (3/3). The field's own systematic survey and taxonomy of deep research agents, giving the orientation and critical benchmark assessment the scan needs across all four decisions.

**Why it matters here.** Directly informs decision 3: identifies systemic weaknesses in how current deep-research benchmarks are built and scored, providing the survey-level map the scan's benchmark-construction question needs.

**Method.** abstract-only; narrative/systematic literature review and taxonomy construction across deep research agent architectures and their evaluation benchmarks.

**Limitations.**

- abstract-only, narrative synthesis rather than systematic empirical comparison
- does not quantify specific gains attributable to individual agentic mechanisms

<sub>selected: score · criteria: C1 1/3 · C2 2/3 · C3 1/3 · C4 3/3 · C5 2/3 · flags: review · verified 2026-08-26 via arxiv</sub>

## 9. Is Grep All You Need? How Agent Harnesses Reshape Agentic Search

Sahil Sen, Akhil Kasturi, Elias Lumer, Anmol Gulati et al. · 2026 · arXiv.org · experimental · overall 3/3

<https://doi.org/10.48550/arxiv.2605.15184>

**Key finding.** Across a custom agent harness and provider CLIs (Claude Code, Codex, Gemini CLI) on a 116-question LongMemEval sample, grep-based retrieval generally yields higher accuracy than vector retrieval, though results depend strongly on which harness is used.

**Why it made the cut.** contradicting · selected by backfill · strongest on C3 retrieval/reranking method (3/3). An explicit method-level finding -- grep vs vector retrieval as the underlying retrieval technique in agent tool-calling loops -- that bears directly on the retrieval-method and baseline-ceiling questions (C1/C3) even though tested outside the literature-search setting.

**Why it matters here.** Directly challenges the implicit assumption that dense/embedding retrieval is the stronger baseline underlying agentic search -- the same recall-ceiling question (C1) the brief asks of literature-search systems -- and shows harness architecture, not retrieval method alone, drives outcomes.

**Method.** Two controlled experiments comparing grep vs vector retrieval across multiple agent harnesses and tool-output presentation formats, with a second experiment progressively adding distractor context.

**Limitations.**

- Evaluated on LongMemEval conversational-memory QA, not scientific literature corpora
- Findings may not transfer to citation-structured scientific corpora where semantic matching plays a different role

<sub>selected: backfill · criteria: C1 2/3 · C2 1/3 · C3 3/3 · C4 1/3 · C5 2/3 · flags: contradicts · verified 2026-08-26 via openalex, arxiv</sub>

## 10. PaSa: An LLM Agent for Comprehensive Academic Paper Search

Yichen He, Guanhua Huang, Peiyuan Feng, Yuan Lin et al. · 2025 · Annual Meeting of the Association for Computational Linguistics · experimental · overall 3/3

<https://doi.org/10.48550/arxiv.2501.10120>

**Key finding.** PaSa-7B surpasses the best Google-based baseline (Google with GPT-4o) by 37.78% in recall@20 and 39.90% in recall@50 on the real-world RealScholarQuery benchmark.

**Why it made the cut.** design-changing · selected by backfill · strongest on C1 baseline recall ceiling (3/3). Closest prior work: an agentic academic paper-search system directly compared against single-query database/search-engine baselines with recall numbers and benchmark construction detail.

**Why it matters here.** Provides the clearest single-query-search baseline comparison (Google, Google Scholar) against an agentic paper-search system with concrete recall numbers, anchoring decision 1 and giving benchmark-construction precedent for decision 3.

**Method.** RL-trained LLM agent that invokes search tools, reads papers, and selects references, trained on synthetic AutoScholarQuery (35k queries) and evaluated on RealScholarQuery.

**Limitations.**

- benchmarks focus on AI-conference papers, may not generalize across all scientific fields
- gains reported by the system's own authors without independent replication cited here

<sub>selected: backfill · criteria: C1 3/3 · C2 2/3 · C3 1/3 · C4 3/3 · C5 0/3 · flags: methods_paper · verified 2026-08-26 via openalex, arxiv</sub>

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

- [BRIGHT: A Realistic and Challenging Benchmark for Reasoning-Intensive Retrieval](https://doi.org/10.48550/arxiv.2407.12883) (2024) — overall 3/3
- [Structurally-bounded Agentic Graph Exploration for Evidence-Grounded Scholarly DeepSearch](https://doi.org/10.48550/arxiv.2608.24809) (2026) — overall 3/3
- [CG-RAG: Research Question Answering by Citation Graph Retrieval-Augmented LLMs](https://doi.org/10.1145/3726302.3729920) (2025) — overall 3/3
- [Projecting BrowseComp-Plus onto ClimbMix: Toward More Realistic Corpora for Agentic Search](https://arxiv.org/abs/2608.20317) (2026) — overall 3/3
- [Deep Research: A Survey of Autonomous Research Agents](https://doi.org/10.48550/arxiv.2508.12752) (2025) — overall 3/3
