# Evidence scan — p11-t2

Run `/Users/nabergoj/Projects/research-scan/research/experiments/phase12-selection/phase12b/runs/p11-t2/R40/O1/rep4/run` · brief `/Users/nabergoj/Projects/research-scan/research/experiments/phase12-selection/phase12b/runs/p11-t2/R40/O1/rep4/run/brief.md` · rendered 2026-08-26

| # | Paper | Year | Venue | Evidence | Verified |
|---|---|---|---|---|---|
| 1 | [When to use Graphs in RAG: A Comprehensive Analysis for Graph Retrieval-Augmented Generation](https://doi.org/10.48550/arxiv.2506.05690) · 10.48550/arxiv.2506.05690 | 2025 | arXiv.org | experimental | yes |
| 2 | [Diagnosing Search Behavior and Failure Modes in Long-Horizon Search Agents](https://doi.org/10.48550/arxiv.2608.01913) · 10.48550/arxiv.2608.01913 | 2026 | arXiv | experimental | yes |
| 3 | [BrowseComp-Plus: A More Fair and Transparent Evaluation Benchmark of Deep-Research Agent](https://doi.org/10.48550/arxiv.2508.06600) · 10.48550/arxiv.2508.06600 | 2025 | arXiv (Cornell University) | experimental | yes |
| 4 | [Deep Research Agents: A Systematic Examination And Roadmap](https://doi.org/10.48550/arxiv.2506.18096) · 10.48550/arxiv.2506.18096 | 2025 | arXiv.org | other | yes |
| 5 | [LitSearch: A Retrieval Benchmark for Scientific Literature Search](https://doi.org/10.48550/arxiv.2407.18940) · 10.48550/arxiv.2407.18940 | 2024 | Conference on Empirical Methods in Natural Language Processing | experimental | yes |
| 6 | [Projecting BrowseComp-Plus onto ClimbMix: Toward More Realistic Corpora for Agentic Search](https://arxiv.org/abs/2608.20317) | 2026 | — | experimental | yes |
| 7 | [Structurally-bounded Agentic Graph Exploration for Evidence-Grounded Scholarly DeepSearch](https://doi.org/10.48550/arxiv.2608.24809) · 10.48550/arxiv.2608.24809 | 2026 | arXiv | experimental | yes |
| 8 | [BRIGHT: A Realistic and Challenging Benchmark for Reasoning-Intensive Retrieval](https://doi.org/10.48550/arxiv.2407.12883) · 10.48550/arxiv.2407.12883 | 2024 | International Conference on Learning Representations | experimental | yes |
| 9 | [Multi-Agent System for Scientific Literature Search and Recommendation](https://doi.org/10.1109/icssas66150.2025.11081082) · 10.1109/icssas66150.2025.11081082 | 2025 | — | experimental | yes |
| 10 | [HySemRAG: A Hybrid Semantic Retrieval-Augmented Generation Framework for Automated Literature Synthesis and Methodological Gap Analysis](https://doi.org/10.48550/arxiv.2508.05666) · 10.48550/arxiv.2508.05666 | 2025 | arXiv.org | experimental | yes |

## 1. When to use Graphs in RAG: A Comprehensive Analysis for Graph Retrieval-Augmented Generation

Zhishang Xiang, Chuan-Yu Wu, Qinggang Zhang, Shengyuan Chen et al. · 2025 · arXiv.org · experimental · overall 3/3

<https://doi.org/10.48550/arxiv.2506.05690>

**Key finding.** GraphRAG frequently underperforms vanilla RAG on real-world tasks; GraphRAG-Bench systematically maps the pipeline (construction, retrieval, generation) across fact retrieval, reasoning, summarization, and creative generation to identify when graph structure actually helps.

**Why it made the cut.** contradicting · selected by score · strongest on C2 agentic mechanism gain (3/3). Directly investigates whether the graph-traversal mechanism the brief singles out actually beats a non-graph baseline, and supplies a benchmark-construction methodology transferable to literature-search evaluation.

**Why it matters here.** Directly targets Q4 for the citation-graph-traversal mechanism specifically: it shows the graph-retrieval gain the brief expects agentic systems to rely on does not reliably beat a plain retrieval baseline, and supplies the benchmark-construction template needed to test that claim rigorously in a literature-search setting.

**Method.** Introduces a comprehensive benchmark with tasks of increasing difficulty and a full-pipeline evaluation protocol comparing GraphRAG against vanilla RAG baselines.

**Limitations.**

- tasks are general-domain RAG benchmarks, not scientific-literature corpora specifically
- vanilla RAG baseline is embedding-based, not necessarily the same single-query database search the brief anchors on

<sub>selected: score · criteria: C1 2/3 · C2 3/3 · C3 3/3 · C4 3/3 · C5 3/3 · flags: contradicts, methods_paper · verified 2026-08-26 via openalex, arxiv</sub>

## 2. Diagnosing Search Behavior and Failure Modes in Long-Horizon Search Agents

Qi Liu, Jiaxin Mao, Fengbin Zhu, Tat-Seng Chua · 2026 · arXiv · experimental · overall 3/3

<https://doi.org/10.48550/arxiv.2608.01913>

**Key finding.** Across six agents on BrowseComp-Plus and BrowseComp, search effort and answer quality are only weakly aligned; accuracy tracks cumulative retrieval recall far better than the number of searches, and the best agents issue far fewer redundant queries than weaker ones.

**Why it made the cut.** contradicting · selected by score · strongest on C2 agentic mechanism gain (3/3). Provides direct trajectory-level evidence on which agentic moves carry gains and where reported search effort fails to translate into accuracy.

**Why it matters here.** Directly undercuts the premise that more iterative searching drives agentic gains; the mechanism that carries the gain is evidence quality/cumulative recall, not search volume, which should reshape how C2 gains are attributed and measured.

**Method.** Trajectory-level diagnosis with human-annotated document relevance judgments, decomposing failures into retrieval gaps vs. utilization gaps, retrieval model held fixed across six agents.

**Limitations.**

- Evaluated on BrowseComp-Plus/BrowseComp rather than a dedicated scientific-literature benchmark
- retrieval model held fixed, limiting generalization across retrievers

<sub>selected: score · criteria: C1 2/3 · C2 3/3 · C3 1/3 · C4 2/3 · C5 3/3 · flags: contradicts · verified 2026-08-26 via openalex, arxiv</sub>

## 3. BrowseComp-Plus: A More Fair and Transparent Evaluation Benchmark of Deep-Research Agent

Zijian Chen, Xueguang Ma, Shengyao Zhuang, Ping Nie et al. · 2025 · arXiv (Cornell University) · experimental · overall 3/3

<https://doi.org/10.48550/arxiv.2508.06600>

**Key finding.** On a fixed, human-verified corpus, Search-R1 with BM25 reaches only 3.86% accuracy while GPT-5 reaches 55.9%, and GPT-5 paired with a Qwen3-Embedding-8B retriever reaches 70.1% with fewer search calls, isolating retriever contribution from agent capability.

**Why it made the cut.** foundational · selected by score · strongest on C1 baseline recall ceiling (3/3). The field's reference benchmark for disentangling agent vs. retriever contribution, directly supplying single-query baseline numbers and a model of rigorous benchmark construction.

**Why it matters here.** Supplies exactly the baseline-recall-ceiling numbers (C1) and the rigorous, contamination-aware benchmark-construction template (C4) that the brief needs to anchor every other reported gain against.

**Method.** New benchmark (BrowseComp-Plus) built from BrowseComp with a fixed curated corpus, human-verified supporting documents, and mined hard negatives, enabling controlled disentangled evaluation of deep-research agents and retrievers.

**Limitations.**

- Fixed corpus (~100K docs) built from the benchmark's own queries, later shown by other work to shift difficulty when evidence is relocated to an independent corpus
- focused on general deep-research QA rather than scientific-literature search specifically

<sub>selected: score · criteria: C1 3/3 · C2 2/3 · C3 2/3 · C4 3/3 · C5 1/3 · flags: methods_paper · verified 2026-08-26 via openalex, arxiv</sub>

## 4. Deep Research Agents: A Systematic Examination And Roadmap

Yuxuan Huang, Yihang Chen, Haozhen Zhang, Kang Li et al. · 2025 · arXiv.org · other · overall 3/3

<https://doi.org/10.48550/arxiv.2506.18096>

**Key finding.** A systematic taxonomy of Deep Research agent architectures (API-based vs. browser-based retrieval, static vs. dynamic workflows, single- vs. multi-agent) that identifies key benchmark limitations including restricted external-knowledge access, sequential-execution inefficiency, and metric-objective misalignment.

**Why it made the cut.** foundational · selected by score · strongest on C4 benchmark construction (3/3). The synthesis paper that maps system designs, tool-use frameworks and benchmark critique the whole brief is organized around.

**Why it matters here.** Provides the field-level map of system designs and, critically, a critical evaluation of current benchmarks' limitations, giving the scan its organizing framework for the sequencing of the other three questions the brief poses.

**Method.** Narrative survey and taxonomy synthesis of Deep Research agent architectures, tool-use frameworks, and evaluation benchmarks, with a maintained companion repository.

**Limitations.**

- Narrative rather than systematic-protocol review; abstract gives no quantitative synthesis
- surveys the field broadly rather than adjudicating specific replication failures

<sub>selected: score · criteria: C1 2/3 · C2 2/3 · C3 2/3 · C4 3/3 · C5 2/3 · flags: review · verified 2026-08-26 via arxiv</sub>

## 5. LitSearch: A Retrieval Benchmark for Scientific Literature Search

Anirudh Ajith, Mengzhou Xia, Alexis Chevalier, Tanya Goyal et al. · 2024 · Conference on Empirical Methods in Natural Language Processing · experimental · overall 3/3

<https://doi.org/10.48550/arxiv.2407.18940>

**Key finding.** LitSearch finds a 24.8-point absolute recall@5 gap between BM25 and state-of-the-art dense retrievers on 597 realistic literature-search queries, with LLM-based reranking improving the best dense retriever by a further 4.4%, while commercial search engines lag 32 points behind.

**Why it made the cut.** foundational · selected by score · strongest on C1 baseline recall ceiling (3/3). The clearest direct answer to the brief's baseline-recall-ceiling and benchmark-construction questions, purpose-built for scientific literature search.

**Why it matters here.** Directly establishes the single-query baseline recall ceiling (BM25 vs dense vs commercial search) the brief's first question asks for, and documents exactly how the evaluation set was constructed — answering the benchmark-construction question too.

**Method.** New retrieval benchmark built from GPT-4-generated questions (from inline-citation paragraphs) plus author-written questions about recent papers, expert-reviewed; benchmarks multiple retrieval models and two LLM reranking pipelines.

**Limitations.**

- Restricted to recent ML/NLP papers rather than broader scientific domains
- 597 queries is a relatively small test set for strong generalization claims

<sub>selected: score · criteria: C1 3/3 · C2 1/3 · C3 3/3 · C4 3/3 · C5 1/3 · verified 2026-08-26 via openalex, arxiv</sub>

## 6. Projecting BrowseComp-Plus onto ClimbMix: Toward More Realistic Corpora for Agentic Search

Sahel Sharifymoghaddam, Lin Gu, Yijun Ge, Jimmy Lin · 2026 · no venue · experimental · overall 3/3

<https://arxiv.org/abs/2608.20317>

**Key finding.** Relocating BrowseComp-Plus's evidence into an independent, non-benchmark-derived corpus (ClimbMix) caused the strongest evaluated agent's evidence recall to fall from 84.3% to 21.4% and answer accuracy to drop by five points despite issuing 63% more search calls, on 57 fully-grounded projected questions.

**Why it made the cut.** contradicting · selected by score · strongest on C1 baseline recall ceiling (3/3). The clearest evidence in this shortlist that reported agentic/retrieval gains shrink dramatically once benchmark-corpus artifacts are removed, squarely answering the brief's fourth question.

**Why it matters here.** Directly demonstrates the C5 phenomenon the brief most wants: a reported agentic evaluation result collapsing once the query-selected, benchmark-derived corpus is replaced by an independently-built one, exposing benchmark-construction inflation.

**Method.** A dataset-agnostic projection pipeline that decomposes questions into atomic reasoning hops and re-grounds them in a 400B-token, 553M-document corpus (ClimbMix) built independently of the benchmark, verified by automatic checks, an independent agent, and human review.

**Limitations.**

- Pipeline yields only 57 fully grounded questions out of 830, a small validated subset
- single projection target (ClimbMix); generality of the pipeline to other corpora not yet demonstrated at scale

<sub>selected: score · criteria: C1 3/3 · C2 0/3 · C3 1/3 · C4 3/3 · C5 3/3 · flags: contradicts, methods_paper · verified 2026-08-26 via arxiv, s2</sub>

## 7. Structurally-bounded Agentic Graph Exploration for Evidence-Grounded Scholarly DeepSearch

Rima Hazra, Sayan Layek, Somnath Banerjee, Soumen Chakrabarti et al. · 2026 · arXiv · experimental · overall 3/3

<https://doi.org/10.48550/arxiv.2608.24809>

**Key finding.** Crase, a bounded citation-graph-expansion pipeline (seed search, 1.5-hop citation expansion, entailment pruning, recency-aware random-walk ranking), outperforms proprietary deep-research agents by up to 3x recall@50 at roughly a third of the cost on LitSearch and a further benchmark over a 500K-paper arXiv corpus.

**Why it made the cut.** design-changing · selected by score · strongest on C2 agentic mechanism gain (3/3). A structurally-bounded alternative to open agentic search that explicitly attributes gains to citation-graph traversal and ranking, core to the system-design question.

**Why it matters here.** Directly isolates citation-graph traversal as the specific mechanism carrying the gain over open-ended agentic search, exactly the C2 decomposition the brief wants and a candidate design to prefer over unconstrained agent loops.

**Method.** Fixed-pipeline design (no open-ended agent loop) evaluated on LitSearch and one additional benchmark against proprietary deep-research agent baselines.

**Limitations.**

- Compared against proprietary deep-research agents rather than a plain single-query baseline explicitly
- evaluated on only two benchmarks, generality across corpora untested

<sub>selected: score · criteria: C1 2/3 · C2 3/3 · C3 3/3 · C4 2/3 · C5 0/3 · flags: methods_paper · verified 2026-08-26 via arxiv</sub>

## 8. BRIGHT: A Realistic and Challenging Benchmark for Reasoning-Intensive Retrieval

Hongjin Su, Howard Yen, Mengzhou Xia, Weijia Shi et al. · 2024 · International Conference on Learning Representations · experimental · overall 3/3

<https://doi.org/10.48550/arxiv.2407.12883>

**Key finding.** The leading MTEB retrieval model (SFR-Embedding-Mistral, 59.0 nDCG@10 on standard benchmarks) scores only 18.3 nDCG@10 on BRIGHT's reasoning-intensive queries, though explicit query reasoning improves retrieval by up to 12.2 points.

**Why it made the cut.** foundational · selected by score · strongest on C1 baseline recall ceiling (3/3). The foundational benchmark establishing how poorly single-query embedding search performs on complex queries, giving Q1 its baseline-ceiling evidence and a construction method transferable to literature-search evaluation.

**Why it matters here.** Supplies the quantified baseline recall ceiling that Q1 asks for on hard, reasoning-intensive queries — the same query type agentic literature-search systems claim to help with — and its methodology for exposing the gap is directly reusable for constructing a literature-search-specific version.

**Method.** Introduces a 1,384-query benchmark spanning economics, psychology, mathematics, and coding, curated from naturally occurring human data, and evaluates state-of-the-art retrieval models against it.

**Limitations.**

- domains covered (economics, psychology, math, coding) do not include scientific literature retrieval directly
- gains from explicit reasoning are shown for query augmentation, not for agentic reformulation/graph/crawling mechanisms specifically

<sub>selected: score · criteria: C1 3/3 · C2 0/3 · C3 2/3 · C4 3/3 · C5 1/3 · flags: methods_paper · verified 2026-08-26 via openalex, arxiv</sub>

## 9. Multi-Agent System for Scientific Literature Search and Recommendation

Aswathy K Cherian, Naman Srivastava, Samyak Varia · 2025 · no venue · experimental · overall 3/3

<https://doi.org/10.1109/icssas66150.2025.11081082>

**Key finding.** A three-agent (query/retrieval/learning) system combining BM25 sparse and FAISS dense retrieval achieves an 8.5% precision improvement, 7.3% recall improvement, and ~210ms latency reduction versus PaperQA and Semantic Scholar.

**Why it made the cut.** design-changing · selected by backfill · strongest on C1 baseline recall ceiling (3/3). One of the few papers directly measuring agentic-move-attributed gains over named baseline literature-search systems, exactly the brief's core comparison.

**Why it matters here.** Directly attributes a measured recall/precision gain to specific agent roles (query expansion, hybrid retrieval, adaptive learning) over named baseline systems, giving concrete numbers for both the baseline-ceiling and agentic-mechanism-gain questions.

**Method.** Multi-agent architecture (Query Agent, Retrieval Agent, Learning Agent) with a FastAPI-backed hybrid BM25+FAISS retrieval strategy and Sentence-Transformer semantic matching, benchmarked against named literature-search baselines.

**Limitations.**

- No venue listed, unclear peer-review status
- Comparison baselines and evaluation-set construction not detailed in abstract
- Single study with no replication

<sub>selected: backfill · criteria: C1 3/3 · C2 3/3 · C3 3/3 · C4 0/3 · C5 0/3 · flags: methods_paper · verified 2026-08-26 via crossref, openalex</sub>

## 10. HySemRAG: A Hybrid Semantic Retrieval-Augmented Generation Framework for Automated Literature Synthesis and Methodological Gap Analysis

Alejandro Godinez · 2025 · arXiv.org · experimental · overall 3/3

<https://doi.org/10.48550/arxiv.2508.05666>

**Key finding.** HySemRAG's hybrid retrieval (semantic search + keyword filtering + knowledge-graph traversal) with agentic self-correction achieves 35.1% higher semantic similarity than PDF chunking (0.655 vs 0.485, p<0.000001), 68.3% single-pass QA success, and 99.0% citation accuracy across 643 evaluated observations.

**Why it made the cut.** design-changing · selected by backfill · strongest on C3 retrieval/reranking method (3/3). A literature-synthesis system whose hybrid retrieval and citation-verification design is directly the kind of architecture the brief's system-design question is about.

**Why it matters here.** Demonstrates a concrete hybrid-retrieval, graph-augmented architecture with quantified extraction-quality and citation-accuracy gains, directly informing the retrieval/reranking design (C3) question the brief asks about, and citation verification bears on the recall/quality tradeoff.

**Method.** Eight-stage ETL+RAG pipeline (metadata acquisition, PDF retrieval, layout analysis, field extraction, topic modeling, knowledge-graph construction) evaluated across 60 testing sessions producing 643 observations, applied to geospatial epidemiology literature.

**Limitations.**

- Case study applied to one applied domain (ozone/cardiovascular epidemiology), generality across scientific fields asserted but not extensively tested
- gains attributed to system as a whole rather than isolated per hybrid-retrieval component

<sub>selected: backfill · criteria: C1 1/3 · C2 2/3 · C3 3/3 · C4 2/3 · C5 0/3 · flags: methods_paper · verified 2026-08-26 via openalex, arxiv</sub>

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

- [Towards Recursive Self-Evolving Agentic Literature Retrieval](https://doi.org/10.48550/arxiv.2605.14306) (2026) — overall 3/3
- [PaSa: An LLM Agent for Comprehensive Academic Paper Search](https://doi.org/10.48550/arxiv.2501.10120) (2025) — overall 3/3
- [Patience is all you need! An agentic system for performing scientific literature review](https://doi.org/10.48550/arxiv.2504.08752) (2025) — overall 3/3
- [CG-RAG: Research Question Answering by Citation Graph Retrieval-Augmented LLMs](https://doi.org/10.1145/3726302.3729920) (2025) — overall 3/3
- [OpenScholar: Synthesizing Scientific Literature with Retrieval-augmented LMs](https://doi.org/10.48550/arxiv.2411.14199) (2024) — overall 3/3
