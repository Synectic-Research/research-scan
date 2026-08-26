# Evidence scan — p11-t2

Run `/Users/nabergoj/Projects/research-scan/research/experiments/phase11-golden/sweep/p11-t2/R25/run` · brief `/Users/nabergoj/Projects/research-scan/research/experiments/phase11-golden/sweep/p11-t2/R25/run/brief.md` · rendered 2026-08-26

| # | Paper | Year | Venue | Evidence | Verified |
|---|---|---|---|---|---|
| 1 | [BrowseComp-Plus: A More Fair and Transparent Evaluation Benchmark of Deep-Research Agent](https://doi.org/10.48550/arxiv.2508.06600) · 10.48550/arxiv.2508.06600 | 2025 | arXiv (Cornell University) | experimental | yes |
| 2 | [Diagnosing Search Behavior and Failure Modes in Long-Horizon Search Agents](https://doi.org/10.48550/arxiv.2608.01913) · 10.48550/arxiv.2608.01913 | 2026 | arXiv | observational | yes |
| 3 | [PaSa: An LLM Agent for Comprehensive Academic Paper Search](https://doi.org/10.48550/arxiv.2501.10120) · 10.48550/arxiv.2501.10120 | 2025 | Annual Meeting of the Association for Computational Linguistics | experimental | yes |
| 4 | [Structurally-bounded Agentic Graph Exploration for Evidence-Grounded Scholarly DeepSearch](https://doi.org/10.48550/arxiv.2608.24809) · 10.48550/arxiv.2608.24809 | 2026 | arXiv | computational | yes |
| 5 | [Projecting BrowseComp-Plus onto ClimbMix: Toward More Realistic Corpora for Agentic Search](https://arxiv.org/abs/2608.20317) | 2026 | — | computational | yes |
| 6 | [Towards Recursive Self-Evolving Agentic Literature Retrieval](https://doi.org/10.48550/arxiv.2605.14306) · 10.48550/arxiv.2605.14306 | 2026 | arXiv | computational | yes |
| 7 | [Deep Research Agents: A Systematic Examination And Roadmap](https://doi.org/10.48550/arxiv.2506.18096) · 10.48550/arxiv.2506.18096 | 2025 | arXiv.org | other | yes |
| 8 | [Multi-Turn Agentic Scientific Literature Search via Workflow Induction](https://doi.org/10.48550/arxiv.2607.00597) · 10.48550/arxiv.2607.00597 | 2026 | arXiv | experimental | yes |
| 9 | [Search-Time Contamination in Deep Research Agents: Measuring Performance Inflation in Public Benchmark Evaluation](https://doi.org/10.48550/arxiv.2606.05241) · 10.48550/arxiv.2606.05241 | 2026 | arXiv.org | computational | yes |
| 10 | [From Inertia to Objectivity: Improving Deep Research Agents with Noise Isolation](https://doi.org/10.48550/arxiv.2608.23045) · 10.48550/arxiv.2608.23045 | 2026 | arXiv | experimental | yes |

## 1. BrowseComp-Plus: A More Fair and Transparent Evaluation Benchmark of Deep-Research Agent

Zijian Chen, Xueguang Ma, Shengyao Zhuang, Ping Nie et al. · 2025 · arXiv (Cornell University) · experimental · overall 3/3

<https://doi.org/10.48550/arxiv.2508.06600>

**Key finding.** On a fixed, human-verified corpus, Search-R1 with a BM25 retriever achieves only 3.86% accuracy while GPT-5 achieves 55.9%, rising to 70.1% with fewer search calls when paired with the Qwen3-Embedding-8B retriever.

**Why it made the cut.** foundational · selected by score · strongest on C1 baseline recall ceiling (3/3). Establishes the fixed-corpus, disentangled baseline-vs-agent methodology anchoring recall-ceiling and retrieval-method comparisons across this entire research area.

**Why it matters here.** Gives exactly the baseline recall/precision ceiling decision 1 asks for — BM25 versus stronger embedding retrievers versus agent — under controlled conditions, and is already the benchmark several other shortlisted papers build directly on.

**Method.** Introduces BrowseComp-Plus, a fixed corpus derived from BrowseComp with human-verified supporting documents and mined hard negatives, enabling disentangled evaluation of agent versus retriever contributions.

**Limitations.**

- Corpus (~100K documents) is assembled from the benchmark's own queries plus mined negatives, which later work shows can inflate retrieval numbers

<sub>selected: score · criteria: C1 3/3 · C2 1/3 · C3 3/3 · C4 3/3 · C5 1/3 · flags: methods_paper · verified 2026-08-26 via openalex, arxiv</sub>

## 2. Diagnosing Search Behavior and Failure Modes in Long-Horizon Search Agents

Qi Liu, Jiaxin Mao, Fengbin Zhu, Tat-Seng Chua · 2026 · arXiv · observational · overall 3/3

<https://doi.org/10.48550/arxiv.2608.01913>

**Key finding.** Search effort and answer quality are only weakly aligned; cumulative retrieval recall predicts accuracy far better than the number of searches, useful evidence often appears early yet agents keep searching, and the best-performing agents issue far fewer redundant queries.

**Why it made the cut.** design-changing · selected by score · strongest on C2 agentic mechanism gain (3/3). Directly diagnoses which agentic behaviors carry gains and shows raw search effort does not, addressing the brief's decisions 2 and 4.

**Why it matters here.** Directly undercuts the assumption that more iterative agentic search yields more gain: the diagnostic method (recall vs. iteration-count decomposition) transfers straight to evaluating any long-horizon literature-search agent and reframes decision 2/4 around stopping criteria and evidence quality rather than search volume.

**Method.** Trajectory-level diagnosis with human-annotated document relevance judgments across six agents on BrowseComp-Plus, validated on BrowseComp via an open-web search API; decomposes failures into retrieval gaps versus utilization gaps.

**Limitations.**

- Fixed retrieval model/harness limits generalization to other retrievers
- BrowseComp-Plus/BrowseComp queries are general knowledge tasks, not scientific-literature search specifically

<sub>selected: score · criteria: C1 2/3 · C2 3/3 · C3 1/3 · C4 1/3 · C5 3/3 · flags: contradicts · verified 2026-08-26 via openalex, arxiv</sub>

## 3. PaSa: An LLM Agent for Comprehensive Academic Paper Search

Yichen He, Guanhua Huang, Peiyuan Feng, Yuan Lin et al. · 2025 · Annual Meeting of the Association for Computational Linguistics · experimental · overall 3/3

<https://doi.org/10.48550/arxiv.2501.10120>

**Key finding.** PaSa-7B surpasses the best Google-based baseline by 37.78% in recall@20 and 39.90% in recall@50 on RealScholarQuery, and exceeds a GPT-4o-prompted variant by 30.36% in recall and 4.25% in precision.

**Why it made the cut.** foundational · selected by score · strongest on C1 baseline recall ceiling (3/3). Foundational system establishing the quantitative baseline-vs-agentic-gain comparison the brief's decisions 1 and 2 are built around.

**Why it matters here.** The canonical baseline-vs-agentic-gain comparison for scholarly search, establishing concrete recall numbers against single-query search baselines that later systems must be measured against (decisions 1 and 2).

**Method.** RL-trained LLM agent for academic paper search, trained on synthetic AutoScholarQuery (35k queries) and evaluated on the real-world RealScholarQuery benchmark.

**Limitations.**

- Training relies on synthetic query generation, which may not fully generalize
- No independent replication or alternative benchmark reported here

<sub>selected: score · criteria: C1 3/3 · C2 2/3 · C3 2/3 · C4 3/3 · C5 0/3 · flags: methods_paper · verified 2026-08-26 via openalex, arxiv</sub>

## 4. Structurally-bounded Agentic Graph Exploration for Evidence-Grounded Scholarly DeepSearch

Rima Hazra, Sayan Layek, Somnath Banerjee, Soumen Chakrabarti et al. · 2026 · arXiv · computational · overall 3/3

<https://doi.org/10.48550/arxiv.2608.24809>

**Key finding.** Crase, using bounded 1.5-hop citation-graph expansion with entailment-based pruning and recency-aware random-walk ranking, outperforms deep research agents built on proprietary models by up to 3x recall@50 at roughly a third of the cost on LitSearch and a further benchmark over a 500K-paper arXiv corpus.

**Why it made the cut.** design-changing · selected by score · strongest on C2 agentic mechanism gain (3/3). The clearest example here of attributing a measured recall gain to a specific, named agentic mechanism (bounded citation-graph traversal) rather than an undifferentiated agent system.

**Why it matters here.** Attributes a measured recall gain to a specific, bounded citation-graph-traversal mechanism rather than an open-ended agent loop, and shows this beats costlier open-ended deep-research agents, exactly the mechanism-attribution evidence decision 2 needs.

**Method.** Single seed-paper search, fixed 1.5-hop citation expansion, entailment-based edge pruning, recency-aware random-walk ranking; evaluated on LitSearch plus one further benchmark. Abstract-only.

**Limitations.**

- Evaluated on only LitSearch plus one further benchmark
- Bounded to 1.5-hop neighborhoods, may miss longer-range citation structure

<sub>selected: score · criteria: C1 2/3 · C2 3/3 · C3 3/3 · C4 1/3 · C5 1/3 · flags: contradicts, methods_paper · verified 2026-08-26 via arxiv</sub>

## 5. Projecting BrowseComp-Plus onto ClimbMix: Toward More Realistic Corpora for Agentic Search

Sahel Sharifymoghaddam, Lin Gu, Yijun Ge, Jimmy Lin · 2026 · no venue · computational · overall 3/3

<https://arxiv.org/abs/2608.20317>

**Key finding.** Relocating BrowseComp-Plus questions' evidence into an independently built 400B-token corpus (ClimbMix) collapses the strongest agent's evidence recall from 84.3% to 21.4% while accuracy drops only five points and search calls rise 63%.

**Why it made the cut.** contradicting · selected by score · strongest on C4 benchmark construction (3/3). The clearest evidence in the shortlist of a reported agentic-search gain failing to hold under a less-curated corpus — exactly what decision 4 asks for.

**Why it matters here.** Exactly the target of decision 4: a reported agentic-search gain (evidence recall) shrinks dramatically once the fixed, per-query-curated corpus is swapped for an independently assembled one, showing benchmark construction was inflating retrieval numbers.

**Method.** Introduces a projection pipeline decomposing questions into atomic reasoning hops and re-grounding each hop in a benchmark-independent corpus, verified by automatic checks, an independent agent, and human review; yields 57 fully grounded questions from 830 BrowseComp-Plus test questions.

**Limitations.**

- Only 57 fully-grounded questions survive the pipeline, a small sample
- Not yet validated across benchmarks beyond BrowseComp-Plus

<sub>selected: score · criteria: C1 1/3 · C2 0/3 · C3 1/3 · C4 3/3 · C5 3/3 · flags: contradicts, methods_paper · verified 2026-08-26 via arxiv, s2</sub>

## 6. Towards Recursive Self-Evolving Agentic Literature Retrieval

Yuwen Du, Tian Jin, Jing Kang, Xianghe Pang et al. · 2026 · arXiv · computational · overall 3/3

<https://doi.org/10.48550/arxiv.2605.14306>

**Key finding.** PaSaMaster achieves a 16.5x higher F1-score than Google Scholar and a 37.8% higher F1-score than GPT-5.2, at about 1% of the cost, while reducing source hallucination from 32.66% to zero across 38 disciplines.

**Why it made the cut.** design-changing · selected by score · strongest on C1 baseline recall ceiling (2/3). Directly addresses agentic mechanism attribution and baseline comparison central to the brief's core decisions.

**Why it matters here.** Provides a concrete recent system design (self-evolving retrieval plus planning/retrieval separation) with a large multidisciplinary benchmark quantifying gains over single-query baselines, directly informing decisions 1-3.

**Method.** Recursive self-evolving agentic retrieval system separating intent-understanding (frontier LLM) from retrieval/scoring (lightweight models); evaluated on PaSaMaster-Bench spanning 38 disciplines. Abstract-only.

**Limitations.**

- Abstract gives no detail on benchmark query source or relevance labeling
- Self-reported comparison; no independent replication reported

<sub>selected: score · criteria: C1 2/3 · C2 2/3 · C3 2/3 · C4 2/3 · C5 0/3 · flags: methods_paper · verified 2026-08-26 via openalex, arxiv</sub>

## 7. Deep Research Agents: A Systematic Examination And Roadmap

Yuxuan Huang, Yihang Chen, Haozhen Zhang, Kang Li et al. · 2025 · arXiv.org · other · overall 3/3

<https://doi.org/10.48550/arxiv.2506.18096>

**Key finding.** Provides a taxonomy of Deep Research agent architectures (static/dynamic workflows, single/multi-agent) and identifies benchmark limitations including restricted external-knowledge access and metric misalignment with practical DR objectives.

**Why it made the cut.** foundational · selected by score · strongest on C3 retrieval/reranking method (2/3). The main survey/roadmap synthesizing the field's architectures and benchmark critiques, useful as an orienting reference.

**Why it matters here.** Orients the whole scan: names the architectural building blocks and critiques the benchmarks in ways that directly shape which papers to trust for the agentic-mechanism and benchmark-construction decisions.

**Method.** Systematic literature review and taxonomy of DR agent architectures, information-acquisition strategies (API vs. browser retrieval), and tool-use frameworks, with a maintained repository of DR agent research.

**Limitations.**

- Narrative/taxonomic review rather than quantitative synthesis
- No new empirical measurement of recall ceilings or gain attribution

<sub>selected: score · criteria: C1 1/3 · C2 1/3 · C3 2/3 · C4 2/3 · C5 1/3 · flags: review · verified 2026-08-26 via arxiv</sub>

## 8. Multi-Turn Agentic Scientific Literature Search via Workflow Induction

Jisen Li, Bingxuan Li, Nanyi Jiang, Xuying Ning et al. · 2026 · arXiv · experimental · overall 3/3

<https://doi.org/10.48550/arxiv.2607.00597>

**Key finding.** PaperPilot-9B, which frames literature search as an executable DAG of operators (keyword search, citation expansion, filtering, scoring, reranking, evidence extraction), improves multi-turn Hit@5 from 58.0 to 77.0, MRR from 47.5 to 59.4, and nDCG@10 from 26.8 to 32.5 over a base toolset agent, while cutting workflow execution errors from 9.5% to 0%.

**Why it made the cut.** design-changing · selected by score · strongest on C2 agentic mechanism gain (3/3). The most directly on-target paper: a scientific-literature-search agent with explicit citation-expansion, reformulation, and reranking operators, quantifying each design's contribution.

**Why it matters here.** The paper closest to the brief's exact system: explicit, editable workflows decomposing citation expansion, reformulation, and reranking as separately controllable operators — directly answers which specific agentic moves (decision 2) carry measured gains in a literature-search-specific setting.

**Method.** Trains a 9B model via supervised workflow imitation and preference optimization over controlled workflow corruptions; evaluates multi-turn scientific literature search against a Qwen3.5-9B toolset-agent baseline.

**Limitations.**

- Gains measured against a single toolset-agent baseline, not a pure single-query database-search baseline
- 9B-scale model; unclear how gains generalize to larger or different backbones

<sub>selected: score · criteria: C1 1/3 · C2 3/3 · C3 2/3 · C4 1/3 · C5 0/3 · flags: methods_paper · verified 2026-08-26 via openalex, arxiv</sub>

## 9. Search-Time Contamination in Deep Research Agents: Measuring Performance Inflation in Public Benchmark Evaluation

Yongjie Wang, Xinyu Crystina Zhang, Kunhong Yao, Zhiwei Zeng et al. · 2026 · arXiv.org · computational · overall 3/3

<https://doi.org/10.48550/arxiv.2606.05241>

**Key finding.** Search-time contamination (benchmark metadata, question-context, or answer leakage via web search) inflates deep research agent benchmark performance by up to 4% across six public benchmarks.

**Why it made the cut.** contradicting · selected by backfill · strongest on C4 benchmark construction (3/3). Directly targets decision 4 (gain replication failure) by showing benchmark contamination inflates deep research agent scores.

**Why it matters here.** Directly answers decision 4: shows reported agentic gains on public benchmarks can be inflated by leaked benchmark content via web search rather than genuine retrieval/reasoning improvement, and questions cross-system comparability (decision 3).

**Method.** Defines three contamination severity types and develops detection algorithms; evaluates modern deep research agents on six public benchmarks. Abstract-only.

**Limitations.**

- Only quantifies up to 4% inflation, not the full picture of where gains come from
- Framed around web-search deep research agents generally, not literature-search agents specifically

<sub>selected: backfill · criteria: C1 0/3 · C2 1/3 · C3 0/3 · C4 3/3 · C5 3/3 · flags: contradicts, methods_paper · verified 2026-08-26 via openalex, arxiv</sub>

## 10. From Inertia to Objectivity: Improving Deep Research Agents with Noise Isolation

Xiangxin Zhang, Zhanwei Zhang, Zhihang Fu, Binbin Lin et al. · 2026 · arXiv · experimental · overall 3/3

<https://doi.org/10.48550/arxiv.2608.23045>

**Key finding.** NIS-Agent reduces token cost by 33% versus baseline while matching or exceeding it on GAIA, WebWalkerQA, BrowseComp and BrowseComp-zh, by isolating context at webpage-triage and answer-validation decision points to counter a newly identified 'inertia bias'.

**Why it made the cut.** design-changing · selected by backfill · strongest on C2 agentic mechanism gain (2/3). Identifies and fixes a specific bias mechanism inside agentic search loops, directly informing agentic-mechanism design (decision 2).

**Why it matters here.** Names and fixes a specific bias mechanism inside agentic search loops (self-authored action history distorting later judgment), giving a concrete architectural move — isolating triage from validation context — that a literature-search agent design should adopt or test against.

**Method.** Introduces the IBIS benchmark, which controls search observations to isolate whether an agent is judging the outcome of its own prior action; evaluates the NIS-Agent context-isolation framework and a purpose-trained 8B model.

**Limitations.**

- Evaluated on general web/QA deep-research benchmarks (GAIA, BrowseComp) rather than scientific-literature corpora
- No comparison to a single-query database-search baseline

<sub>selected: backfill · criteria: C1 0/3 · C2 2/3 · C3 1/3 · C4 2/3 · C5 1/3 · flags: methods_paper · verified 2026-08-26 via arxiv</sub>

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

- [When Deep Research Agents Stagnate: Enhancing Reasoning with Retrieval-Aware Agent Control](https://doi.org/10.48550/arxiv.2608.15191) (2026) — overall 3/3
- [Deep Research Bench: Evaluating AI Web Research Agents](https://doi.org/10.48550/arxiv.2506.06287) (2025) — overall 3/3
- [Language agents achieve superhuman synthesis of scientific knowledge](https://doi.org/10.48550/arxiv.2409.13740) (2024) — overall 3/3
- [ResearchRubrics: A Benchmark of Prompts and Rubrics For Evaluating Deep Research Agents](https://doi.org/10.48550/arxiv.2511.07685) (2025) — overall 3/3
- [DeepResearch Bench: A Comprehensive Benchmark for Deep Research Agents](https://doi.org/10.48550/arxiv.2506.11763) (2025) — overall 3/3
