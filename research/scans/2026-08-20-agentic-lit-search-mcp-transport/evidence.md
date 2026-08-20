# Evidence scan — agentic-lit-search

Run `research/scans/2026-08-20-agentic-lit-search` · brief `research/scans/2026-08-20-agentic-lit-search/brief.md` · rendered 2026-08-20

| # | Paper | Year | Venue | Evidence | Verified |
|---|---|---|---|---|---|
| 1 | ScholarGym: Benchmarking Large Language Model Capabilities in the Information-Gathering Stage of Deep Research | 2026 | — | computational | yes |
| 2 | OpenScholar: Synthesizing Scientific Literature with Retrieval-augmented LMs | 2024 | arXiv.org | computational | yes |
| 3 | BRIGHT: A Realistic and Challenging Benchmark for Reasoning-Intensive Retrieval | 2024 | International Conference on Learning Representations | computational | yes |
| 4 | BrowseComp-Plus: A More Fair and Transparent Evaluation Benchmark of Deep-Research Agent | 2025 | arXiv (Cornell University) | computational | yes |
| 5 | Diagnosing Search Behavior and Failure Modes in Long-Horizon Search Agents | 2026 | — | computational | yes |
| 6 | Can Deep Research Agents Retrieve and Organize? Evaluating the Synthesis Gap with Expert Taxonomies | 2026 | arXiv.org | computational | yes |
| 7 | When to use Graphs in RAG: A Comprehensive Analysis for Graph Retrieval-Augmented Generation | 2025 | arXiv.org | computational | yes |
| 8 | ScholarQuest: A Taxonomy-Guided Benchmark for Agentic Academic Paper Search in Open Literature Environments | 2026 | arXiv (Cornell University) | computational | yes |
| 9 | Which academic search systems are suitable for systematic reviews or meta‐analyses? Evaluating retrieval qualities of Google Scholar, PubMed, and 26 other resources | 2020 | Research Synthesis Methods | experimental | yes |
| 10 | Dense Passage Retrieval for Open-Domain Question Answering | 2020 | Conference on Empirical Methods in Natural Language Processing | computational | yes |

## 1. ScholarGym: Benchmarking Large Language Model Capabilities in the Information-Gathering Stage of Deep Research

Hao Shen, Hang Yang, Zhouhong Gu, Weili Han · 2026 · no venue · computational · overall 3/3

<https://arxiv.org/abs/2601.21654>

**Key finding.** Iterative query decomposition yields 2.9-3.3x F1 gains over single-query retrieval, models with extended thinking trade recall for precision, and query planning plus relevance assessment are the two bottlenecks separating proprietary from open models.

**Why it made the cut.** plan-influencing · selected by score · strongest on C1 agentic search design (3/3). Answers the first two questions in one design: a fixed single-query baseline, and stage-level attribution of what agentic decomposition adds.

**Why it matters here.** The single most useful entry point: it separates the stages, holds retrieval fixed, and puts a number on what reformulation alone is worth against the single-query baseline.

**Method.** Evaluation environment isolating the information-gathering stage into query planning, tool invocation and relevance assessment, over 2,536 expert-annotated queries and a static 570K-paper corpus with deterministic retrieval; abstract-only.

**Limitations.**

- static corpus of 570K papers is far smaller than the live literature
- the multiplier is on F1 over the authors' query set, so it depends on how those queries were written
- evaluates only the gathering stage, not the report the user finally reads

<sub>selected: score · criteria: C1 3/3 · C2 3/3 · C3 3/3 · C4 2/3 · C5 2/3 · flags: methods_paper · verified 2026-08-20 via arxiv, s2</sub>

## 2. OpenScholar: Synthesizing Scientific Literature with Retrieval-augmented LMs

Akari Asai, Jacqueline He, Rulin Shao, Weijia Shi et al. · 2024 · arXiv.org · computational · overall 3/3

<https://doi.org/10.48550/arxiv.2411.14199>

**Key finding.** An 8B retrieval-augmented model over 45 million open-access papers beats GPT-4o by 5% and PaperQA2 by 7% in correctness, while GPT-4o hallucinates citations 78 to 90% of the time; experts preferred its answers to expert-written ones 51% of the time.

**Why it made the cut.** closely-related · selected by score · strongest on C1 agentic search design (3/3). Sets the open baseline and supplies the first large multi-domain literature search benchmark the field measures against.

**Why it matters here.** The reference system and the reference benchmark for scholarly literature synthesis, and the source of the citation-hallucination figure that motivates most work after it.

**Method.** Specialized retrieval-augmented LM with a self-feedback inference loop, evaluated on ScholarQABench: 2,967 expert-written queries and 208 long-form answers across four fields, with human expert judging.

**Limitations.**

- the benchmark was built by the team that built the system
- correctness margins are single-digit percentages
- expert preference judgments involve small numbers of raters per query

<sub>selected: score · criteria: C1 3/3 · C2 2/3 · C3 3/3 · C4 3/3 · C5 2/3 · verified 2026-08-20 via openalex, arxiv</sub>

## 3. BRIGHT: A Realistic and Challenging Benchmark for Reasoning-Intensive Retrieval

Hongjin Su, Howard Yen, Mengzhou Xia, Weijia Shi et al. · 2024 · International Conference on Learning Representations · computational · overall 3/3

<https://doi.org/10.48550/arxiv.2407.12883>

**Key finding.** The leading MTEB model scores 59.0 nDCG@10 on the leaderboard but 18.3 on a reasoning-intensive set of 1,384 real queries; adding explicit reasoning about the query recovers up to 12.2 points.

**Why it made the cut.** contradicting · selected by score · strongest on C2 baseline recall (3/3). The measured collapse from 59.0 to 18.3 for one unchanged model across two differently-constructed sets is the brief's fourth question demonstrated directly, and query-reasoning gain is the reformulation move measured in isolation.

**Why it matters here.** The cleanest demonstration that retrieval scores are a property of the query set, not the retriever, which is the single most useful caution when reading any reported gain.

**Method.** Benchmark of naturally occurring and curated human queries across economics, psychology, mathematics and coding, evaluated against state-of-the-art retrievers; abstract-only.

**Limitations.**

- domains are not scientific literature search, though several are academic
- query curation choices determine how large the drop is
- reasoning gain measured on the same set that produced the drop

<sub>selected: score · criteria: C1 1/3 · C2 3/3 · C3 3/3 · C4 3/3 · C5 3/3 · flags: contradicts · verified 2026-08-20 via openalex, arxiv</sub>

## 4. BrowseComp-Plus: A More Fair and Transparent Evaluation Benchmark of Deep-Research Agent

Zijian Chen, Xueguang Ma, Shengyao Zhuang, Ping Nie et al. · 2025 · arXiv (Cornell University) · computational · overall 3/3

<https://doi.org/10.48550/arxiv.2508.06600>

**Key finding.** On a fixed corpus, Search-R1 with BM25 reaches 3.86% accuracy while GPT-5 reaches 55.9%, rising to 70.1% with a stronger embedding retriever and fewer search calls.

**Why it made the cut.** contradicting · selected by score · strongest on C3 benchmark construction (3/3). The benchmark-construction technique transfers directly: a frozen corpus with verified supporting documents and mined negatives is exactly what isolates retriever contribution in a literature-search benchmark, and the paper measures how much swapping the retriever alone moves the score.

**Why it matters here.** Shows that scores on live-API benchmarks confound the agent with its retriever and with a moving corpus, so a newcomer should distrust any agentic gain not measured on a fixed corpus.

**Method.** Benchmark derived from BrowseComp with a frozen curated corpus, human-verified supporting documents and mined hard negatives, enabling controlled retriever swaps; abstract-only.

**Limitations.**

- corpus is web documents, not scholarly literature
- derived from an existing benchmark, inheriting its query distribution
- fixed corpus removes the recency that real search depends on

<sub>selected: score · criteria: C1 1/3 · C2 2/3 · C3 3/3 · C4 3/3 · C5 3/3 · flags: contradicts, methods_paper · verified 2026-08-20 via openalex, arxiv</sub>

## 5. Diagnosing Search Behavior and Failure Modes in Long-Horizon Search Agents

Qi Liu, Jiaxin Mao, Fengbin Zhu, Tat-Seng Chua · 2026 · no venue · computational · overall 3/3

<https://arxiv.org/abs/2608.01913>

**Key finding.** Search effort and answer quality are only weakly aligned: accuracy tracks cumulative retrieval recall rather than the number of searches or context consumed, useful evidence usually appears early, and the best agents issue far fewer redundant queries.

**Why it made the cut.** contradicting · selected by score · strongest on C1 agentic search design (3/3). The measurement design transfers directly: holding the retriever and harness fixed and scoring each step against human relevance judgments is how one would attribute gains among reformulation, traversal and crawling in literature search, and it finds the effort-quality link weak.

**Why it matters here.** The paper that tells a newcomer where to look: not at the agent loop but at cumulative retrieval recall, and it shows that more iterations is the wrong thing to sell.

**Method.** Trajectory-level diagnosis of six agents with the retrieval model and evaluation harness held fixed, using human-annotated document-level relevance judgments to separate retrieval gaps from utilization gaps; validated on a second setting with a live search API.

**Limitations.**

- web corpora rather than scholarly literature
- six agents on two benchmarks, so the correlation is over a small system sample
- reformulation is judged useful without an isolated ablation of it

<sub>selected: score · criteria: C1 3/3 · C2 3/3 · C3 1/3 · C4 2/3 · C5 3/3 · flags: contradicts · verified 2026-08-20 via arxiv, s2</sub>

## 6. Can Deep Research Agents Retrieve and Organize? Evaluating the Synthesis Gap with Expert Taxonomies

Ming Zhang, Jiabao Zhuang, Wenqing Jing, Ziyu Kong et al. · 2026 · arXiv.org · computational · overall 3/3

<https://doi.org/10.48550/arxiv.2601.12369>

**Key finding.** The best of seven deep research agents retrieves only 20.92% of expert-cited papers, no bottom-up run reaches the experts' average taxonomy depth of 4.86, and models that match depth do so by fragmenting the taxonomy.

**Why it made the cut.** contradicting · selected by score · strongest on C2 baseline recall (3/3). Separates retrieval failure from organization failure on scholarly literature and reports both as measured gaps, which is the brief's fourth question answered in its own setting.

**Why it matters here.** Puts a hard number on the retrieval side of automated survey writing and shows the reported hierarchy metrics are uncalibrated, so a newcomer discounts organization scores until depth is matched.

**Method.** Benchmark from 72 highly cited LLM surveys, 3,815 cited papers and expert-authored taxonomies, scored with ARI, V-Measure and three hierarchy metrics across 7 agents and 16 LLM configurations, plus a controlled depth-matching probe.

**Limitations.**

- expert-cited paper sets treat one survey's citation list as ground truth
- restricted to LLM surveys, a fast-moving and unusually well-covered area
- retrieval is scored end-to-end from a topic, so query phrasing is part of what is measured

<sub>selected: score · criteria: C1 2/3 · C2 3/3 · C3 3/3 · C4 1/3 · C5 3/3 · flags: contradicts · verified 2026-08-20 via openalex, arxiv</sub>

## 7. When to use Graphs in RAG: A Comprehensive Analysis for Graph Retrieval-Augmented Generation

Zhishang Xiang, Chuan-Yu Wu, Qinggang Zhang, Shengyuan Chen et al. · 2025 · arXiv.org · computational · overall 3/3

<https://doi.org/10.48550/arxiv.2506.05690>

**Key finding.** Graph retrieval frequently underperforms vanilla retrieval on real-world tasks; a staged benchmark identifies the specific task types and pipeline conditions under which graph structure actually pays.

**Why it made the cut.** contradicting · selected by score · strongest on C3 benchmark construction (3/3). The stage-by-stage comparison of graph-structured against flat retrieval is the same architectural test citation-graph traversal needs, and it finds the graph often loses.

**Why it matters here.** The corrective to the assumption that adding graph structure helps, which matters because citation-graph traversal is the agentic move with the strongest intuitive appeal.

**Method.** Benchmark with tasks of increasing difficulty spanning fact retrieval, complex reasoning, contextual summarization and generation, evaluated stage by stage from graph construction through retrieval to generation; abstract-only.

**Limitations.**

- knowledge graphs over general corpora rather than citation graphs over papers
- conditions identified on the authors' own task taxonomy
- no cost accounting for graph construction against the benefit

<sub>selected: score · criteria: C1 1/3 · C2 2/3 · C3 3/3 · C4 3/3 · C5 3/3 · flags: contradicts · verified 2026-08-20 via openalex, arxiv</sub>

## 8. ScholarQuest: A Taxonomy-Guided Benchmark for Agentic Academic Paper Search in Open Literature Environments

Tingyue Pan, Mingyue Cheng, Daoyu Wang, Yitong Zhou et al. · 2026 · arXiv (Cornell University) · computational · overall 3/3

<https://doi.org/10.48550/arxiv.2606.20235>

**Key finding.** Agentic methods beat single-shot retrieval, but the best agent reaches only 0.314 Recall@100 and 0.355 Recall@All on a taxonomy-guided open-literature benchmark.

**Why it made the cut.** plan-influencing · selected by score · strongest on C2 baseline recall (3/3). Gives both halves of the brief's first two questions at once: agentic beats single-shot, and the ceiling is low.

**Why it matters here.** Reframes the whole picture: the relative claim holds while the absolute number stays near a third, so a newcomer reads every reported gain as a gain over a low base.

**Method.** Benchmark over 1,000+ CS topics and four research intents, with scalable answer construction and a shared retrieval backend for reproducible comparison; abstract-only.

**Limitations.**

- answers are constructed automatically from a taxonomy rather than judged by experts
- restricted to computer science topics
- recall ceiling partly reflects how the answer sets were built

<sub>selected: score · criteria: C1 2/3 · C2 3/3 · C3 3/3 · C4 1/3 · C5 2/3 · verified 2026-08-20 via openalex, arxiv</sub>

## 9. Which academic search systems are suitable for systematic reviews or meta‐analyses? Evaluating retrieval qualities of Google Scholar, PubMed, and 26 other resources

Michael Gusenbauer, Neal R Haddaway · 2020 · Research Synthesis Methods · experimental · overall 3/3

<https://doi.org/10.1002/jrsm.1378>

**Key finding.** Testing 28 widely used academic search systems on precision, recall and reproducibility of Boolean searches, only about half can be recommended for evidence synthesis without substantial caveats, and Google Scholar is unsuitable as a principal search system.

**Why it made the cut.** foundational · selected by foundational · strongest on C2 baseline recall (3/3). The work every agentic paper-search paper cites when it claims database search is the weak baseline, and the only one here that measured all 28 systems directly.

**Why it matters here.** The pre-agentic answer to the brief's first question, and the reason the baseline matters: the recall ceiling belongs to the search system's query interface, not to the searcher's skill.

**Method.** Query-based empirical protocol testing how well users can interact with and retrieve records from each of 28 systems including Google Scholar, PubMed and Web of Science.

**Limitations.**

- published in 2020, before the systems and interfaces the current literature tests
- measures the interface's Boolean capability rather than end-to-end recall of a research question
- framed for systematic review practice rather than open-ended literature exploration

<sub>selected: foundational · criteria: C1 0/3 · C2 3/3 · C3 2/3 · C4 3/3 · C5 2/3 · flags: methods_paper · verified 2026-08-20 via crossref, openalex</sub>

## 10. Dense Passage Retrieval for Open-Domain Question Answering

Vladimir Karpukhin, Barlas Oğuz, Sewon Min, Patrick Lewis et al. · 2020 · Conference on Empirical Methods in Natural Language Processing · computational · overall 2/3

<https://doi.org/10.18653/v1/2020.emnlp-main.550>

**Key finding.** A simple dual-encoder dense retriever trained on a small number of question-passage pairs beats a strong Lucene-BM25 system by 9 to 19 percent absolute in top-20 passage retrieval accuracy.

**Why it made the cut.** foundational · selected by foundational · strongest on C4 retrieval and reranking (3/3). The origin of the dense-versus-lexical comparison that the scientific literature search benchmarks still report.

**Why it matters here.** The result that made dense retrieval the default first stage, and the template for how every later retrieval gain is reported: absolute top-k accuracy against a BM25 baseline.

**Method.** Dual-encoder dense retrieval trained on limited supervision, evaluated across open-domain QA datasets against a tuned BM25 system.

**Limitations.**

- open-domain QA over Wikipedia, not scientific literature
- gains depend on in-domain training data that scholarly search often lacks
- top-20 accuracy on short factoid questions is a weak proxy for literature recall

<sub>selected: foundational · criteria: C1 0/3 · C2 2/3 · C3 0/3 · C4 3/3 · C5 0/3 · flags: methods_paper · verified 2026-08-20 via crossref, openalex</sub>

## Coverage

| Criterion | Papers kept |
|---|---|
| C1 agentic search design | 51 |
| C2 baseline recall | 15 |
| C3 benchmark construction | 50 |
| C4 retrieval and reranking | 67 |
| C5 gains that fail | 30 |

## Alternates

Next in order, not selected:

- [SeekerGym: A Benchmark for Reliable Information Seeking](https://doi.org/10.48550/arxiv.2604.17143) (2026) — overall 3/3
- [WisPaper: Your AI Scholar Search Engine](https://doi.org/10.48550/arxiv.2512.06879) (2025) — overall 3/3
- [DeepResearchGym: A Free, Transparent, and Reproducible Evaluation Sandbox for Deep Research](https://doi.org/10.48550/arxiv.2505.19253) (2025) — overall 3/3
- [Language agents achieve superhuman synthesis of scientific knowledge](https://doi.org/10.48550/arxiv.2409.13740) (2024) — overall 3/3
- [LitSearch: A Retrieval Benchmark for Scientific Literature Search](https://doi.org/10.48550/arxiv.2407.18940) (2024) — overall 3/3
