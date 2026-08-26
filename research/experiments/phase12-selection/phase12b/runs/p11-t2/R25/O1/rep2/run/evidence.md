# Evidence scan — p11-t2

Run `/Users/nabergoj/Projects/research-scan/research/experiments/phase12-selection/phase12b/runs/p11-t2/R25/O1/rep2/run` · brief `/Users/nabergoj/Projects/research-scan/research/experiments/phase12-selection/phase12b/runs/p11-t2/R25/O1/rep2/run/brief.md` · rendered 2026-08-26

| # | Paper | Year | Venue | Evidence | Verified |
|---|---|---|---|---|---|
| 1 | [Diagnosing Search Behavior and Failure Modes in Long-Horizon Search Agents](https://doi.org/10.48550/arxiv.2608.01913) · 10.48550/arxiv.2608.01913 | 2026 | arXiv | experimental | yes |
| 2 | [BrowseComp-Plus: A More Fair and Transparent Evaluation Benchmark of Deep-Research Agent](https://doi.org/10.48550/arxiv.2508.06600) · 10.48550/arxiv.2508.06600 | 2025 | arXiv (Cornell University) | experimental | yes |
| 3 | [Deep Research Agents: A Systematic Examination And Roadmap](https://doi.org/10.48550/arxiv.2506.18096) · 10.48550/arxiv.2506.18096 | 2025 | arXiv.org | other | yes |
| 4 | [Projecting BrowseComp-Plus onto ClimbMix: Toward More Realistic Corpora for Agentic Search](https://arxiv.org/abs/2608.20317) | 2026 | — | experimental | yes |
| 5 | [Towards Recursive Self-Evolving Agentic Literature Retrieval](https://doi.org/10.48550/arxiv.2605.14306) · 10.48550/arxiv.2605.14306 | 2026 | arXiv | experimental | yes |
| 6 | [PaSa: An LLM Agent for Comprehensive Academic Paper Search](https://doi.org/10.48550/arxiv.2501.10120) · 10.48550/arxiv.2501.10120 | 2025 | Annual Meeting of the Association for Computational Linguistics | experimental | yes |
| 7 | [Structurally-bounded Agentic Graph Exploration for Evidence-Grounded Scholarly DeepSearch](https://doi.org/10.48550/arxiv.2608.24809) · 10.48550/arxiv.2608.24809 | 2026 | arXiv | experimental | yes |
| 8 | [From Inertia to Objectivity: Improving Deep Research Agents with Noise Isolation](https://doi.org/10.48550/arxiv.2608.23045) · 10.48550/arxiv.2608.23045 | 2026 | arXiv | experimental | yes |
| 9 | [Multi-Turn Agentic Scientific Literature Search via Workflow Induction](https://doi.org/10.48550/arxiv.2607.00597) · 10.48550/arxiv.2607.00597 | 2026 | arXiv | experimental | yes |
| 10 | [Search-Time Contamination in Deep Research Agents: Measuring Performance Inflation in Public Benchmark Evaluation](https://doi.org/10.48550/arxiv.2606.05241) · 10.48550/arxiv.2606.05241 | 2026 | arXiv.org | experimental | yes |

## 1. Diagnosing Search Behavior and Failure Modes in Long-Horizon Search Agents

Qi Liu, Jiaxin Mao, Fengbin Zhu, Tat-Seng Chua · 2026 · arXiv · experimental · overall 3/3

<https://doi.org/10.48550/arxiv.2608.01913>

**Key finding.** Across six agents evaluated on BrowseComp-Plus and BrowseComp, answer accuracy correlates more with cumulative retrieval recall than with the number of search steps or context consumed, and top-performing agents issue far fewer redundant queries.

**Why it made the cut.** design-changing · selected by score · strongest on C2 agentic mechanism gain (3/3). Direct empirical decomposition of what drives agentic search gains vs failure modes, core to the brief's second and fourth questions.

**Why it matters here.** Directly answers our Q2/Q4: search effort alone does not carry the reported agentic gain — cumulative retrieval quality does, and excess searching produces low-yield steps, undermining any claim that more iterative crawling automatically wins.

**Method.** Trajectory-level diagnosis with human-annotated document relevance judgments, comparing six deep-search agents with a fixed retrieval model and evaluation harness across two benchmarks.

**Limitations.**

- Relies on two related benchmark families (BrowseComp/BrowseComp-Plus) so may not generalize to other corpora
- Retrieval model held fixed, so findings about agent behavior may not transfer to settings with weaker/stronger retrievers

<sub>selected: score · criteria: C1 2/3 · C2 3/3 · C3 1/3 · C4 2/3 · C5 3/3 · flags: contradicts · verified 2026-08-26 via openalex, arxiv</sub>

## 2. BrowseComp-Plus: A More Fair and Transparent Evaluation Benchmark of Deep-Research Agent

Zijian Chen, Xueguang Ma, Shengyao Zhuang, Ping Nie et al. · 2025 · arXiv (Cornell University) · experimental · overall 3/3

<https://doi.org/10.48550/arxiv.2508.06600>

**Key finding.** On BrowseComp-Plus's fixed, human-verified corpus, Search-R1 with BM25 retrieval scores only 3.86% accuracy while GPT-5 reaches 55.9%, rising to 70.1% (with fewer search calls) when paired with the Qwen3-Embedding-8B retriever.

**Why it made the cut.** plan-influencing · selected by score · strongest on C1 baseline recall ceiling (3/3). The field's reference benchmark for disentangling agent and retriever contributions, directly supplying baseline recall/accuracy numbers and benchmark-construction detail central to Q1 and Q3.

**Why it matters here.** Supplies exactly the baseline-ceiling numbers (weak retriever + weak agent near zero) the brief's first question needs, and its corpus-fixing methodology is the construction standard other benchmark papers in this scan build on or challenge.

**Method.** New benchmark built from BrowseComp with a fixed corpus, human-verified supporting documents, and mined hard negatives, enabling disentangled evaluation of agent reasoning versus retriever quality.

**Limitations.**

- Corpus assembled from the benchmark's own query-derived documents plus mined negatives, which later work (ClimbMix projection) shows may make retrieval artificially easy
- Results specific to BrowseComp-style multi-hop question style

<sub>selected: score · criteria: C1 3/3 · C2 1/3 · C3 2/3 · C4 3/3 · C5 1/3 · flags: methods_paper · verified 2026-08-26 via openalex, arxiv</sub>

## 3. Deep Research Agents: A Systematic Examination And Roadmap

Yuxuan Huang, Yihang Chen, Haozhen Zhang, Kang Li et al. · 2025 · arXiv.org · other · overall 3/3

<https://doi.org/10.48550/arxiv.2506.18096>

**Key finding.** This roadmap paper proposes a taxonomy distinguishing static vs dynamic Deep Research agent workflows and single- vs multi-agent architectures, and identifies restricted external-knowledge access, sequential execution inefficiency, and metric-objective misalignment as key limitations of current benchmarks.

**Why it made the cut.** plan-influencing · selected by score · strongest on C4 benchmark construction (3/3). The synthesis/roadmap paper for the exact system class and benchmark-critique question the brief asks about; earns the review-flag ship guarantee.

**Why it matters here.** Provides the field-level map needed to compare disparately-built benchmarks and architectures against each other, and explicitly flags that current benchmark metrics may misalign with what agents are actually meant to accomplish — a direct caution for Q3/Q4.

**Method.** Narrative systematic examination and taxonomy of Deep Research agent architectures, tool-use frameworks, and benchmarks; abstract-only for specifics.

**Limitations.**

- Narrative rather than systematic-protocol review; abstract does not quantify claims
- Taxonomy is descriptive and does not itself measure gains or failures empirically

<sub>selected: score · criteria: C1 1/3 · C2 1/3 · C3 1/3 · C4 3/3 · C5 2/3 · flags: review, contradicts · verified 2026-08-26 via arxiv</sub>

## 4. Projecting BrowseComp-Plus onto ClimbMix: Toward More Realistic Corpora for Agentic Search

Sahel Sharifymoghaddam, Lin Gu, Yijun Ge, Jimmy Lin · 2026 · no venue · experimental · overall 3/3

<https://arxiv.org/abs/2608.20317>

**Key finding.** Relocating BrowseComp-Plus's 57 fully-grounded questions onto the independently-built ClimbMix corpus drops the strongest agent's evidence recall from 84.3% to 21.4% and answer accuracy by five points, despite the agent issuing 63% more search calls.

**Why it made the cut.** contradicting · selected by score · strongest on C4 benchmark construction (3/3). The clearest evidence in this shortlist that a reported agentic-search gain fails to replicate under a different, more realistic corpus — exactly what the brief's premise-testing Q4 is looking for.

**Why it matters here.** Directly demonstrates the brief's Q4 concern realized: an agentic-search gain measured on a per-query-curated corpus collapses when the same questions are projected onto a more realistic, independently-built corpus — evidence that at least some reported BrowseComp-Plus-style gains are corpus artifacts rather than durable agent capability.

**Method.** A dataset-agnostic projection pipeline decomposes benchmark questions into atomic reasoning hops and re-grounds them in a new, benchmark-independent 400B-token corpus, retaining only hops verified by automatic checks, an independent agent, and human review.

**Limitations.**

- Only 57 of 830 original questions survived full grounding verification, a small and possibly non-representative subset
- The projection method is itself new and unvalidated against further independent corpora

<sub>selected: score · criteria: C1 2/3 · C2 0/3 · C3 0/3 · C4 3/3 · C5 3/3 · flags: contradicts, methods_paper · verified 2026-08-26 via arxiv, s2</sub>

## 5. Towards Recursive Self-Evolving Agentic Literature Retrieval

Yuwen Du, Tian Jin, Jing Kang, Xianghe Pang et al. · 2026 · arXiv · experimental · overall 3/3

<https://doi.org/10.48550/arxiv.2605.14306>

**Key finding.** PaSaMaster achieves a 16.5x higher F1-score than Google Scholar and 37.8% higher F1 than GPT-5.2, at about 1% of GPT-5.2's cost, reducing source hallucination from 32.66% to zero, across 38 disciplines in PaSaMaster-Bench.

**Why it made the cut.** design-changing · selected by score · strongest on C1 baseline recall ceiling (3/3). Explicit head-to-head comparison of an agentic literature retrieval system against single-query search (Google Scholar), with a named agentic mechanism (self-evolving retrieval) credited for the gain.

**Why it matters here.** Directly benchmarks an agentic literature retrieval system against a single-query search baseline (Google Scholar), giving a concrete F1 ceiling figure and a specific mechanism (self-evolving intent refinement) credited with the gain — exactly the evidence the brief's first two decisions need.

**Method.** Recursive self-evolving agentic retrieval system separating intent understanding (frontier LLM) from retrieval/scoring (lightweight models); evaluated against Google Scholar and GPT-5.2 on a custom 38-discipline benchmark.

**Limitations.**

- Benchmark (PaSaMaster-Bench) is self-constructed with limited detail on labeling/contamination controls in the abstract
- Comparison to Google Scholar F1 may not isolate the specific mechanism (self-evolution vs. verified-source ranking) responsible for the gain

<sub>selected: score · criteria: C1 3/3 · C2 2/3 · C3 2/3 · C4 1/3 · C5 0/3 · flags: methods_paper · verified 2026-08-26 via openalex, arxiv</sub>

## 6. PaSa: An LLM Agent for Comprehensive Academic Paper Search

Yichen He, Guanhua Huang, Peiyuan Feng, Yuan Lin et al. · 2025 · Annual Meeting of the Association for Computational Linguistics · experimental · overall 3/3

<https://doi.org/10.48550/arxiv.2501.10120>

**Key finding.** PaSa-7B exceeds the best Google-based baseline by 37.78% in recall@20 and 39.90% in recall@50 on RealScholarQuery, and outperforms a prompted GPT-4o agent by 30.36% in recall and 4.25% in precision.

**Why it made the cut.** design-changing · selected by score · strongest on C1 baseline recall ceiling (3/3). Core agentic paper-search system reporting large recall gains over single/paraphrased-query baselines, central to the brief's first two questions.

**Why it matters here.** A canonical example of the exact system class the brief studies, with a paired synthetic-training/real-evaluation benchmark design whose construction choices matter for whether the reported recall gains generalize.

**Method.** RL-trained autonomous paper-search agent evaluated on a new synthetic benchmark (AutoScholarQuery, 35k queries) and a real-world benchmark (RealScholarQuery), compared against search-engine and LLM-augmented baselines.

**Limitations.**

- Trained on synthetic queries derived from top-tier AI conference papers, so may not generalize to other fields or informal queries
- Comparison baselines (paraphrased Google queries) may understate what optimized single-query search could achieve

<sub>selected: score · criteria: C1 3/3 · C2 1/3 · C3 1/3 · C4 3/3 · C5 0/3 · flags: methods_paper · verified 2026-08-26 via openalex, arxiv</sub>

## 7. Structurally-bounded Agentic Graph Exploration for Evidence-Grounded Scholarly DeepSearch

Rima Hazra, Sayan Layek, Somnath Banerjee, Soumen Chakrabarti et al. · 2026 · arXiv · experimental · overall 3/3

<https://doi.org/10.48550/arxiv.2608.24809>

**Key finding.** Crase, a bounded citation-graph-traversal agent (single seed search, 1.5-hop expansion, entailment-based edge pruning, recency-aware random-walk ranking), outperforms deep research agents built on proprietary models by up to 3x recall@50 at roughly a third of the cost on LitSearch and one further benchmark over a 500K-paper arXiv corpus.

**Why it made the cut.** design-changing · selected by score · strongest on C2 agentic mechanism gain (3/3). Directly attributes measured gains to citation-graph traversal as a bounded, distinct agentic mechanism, matching C2 precisely.

**Why it matters here.** Isolates citation-graph traversal as the specific agentic move producing the recall gain, with an explicit, inspectable stopping condition — exactly the mechanism decomposition the brief's second question asks for.

**Method.** System design paper: single seed search plus fixed-depth citation-graph expansion and pruning, evaluated against open-ended deep research agents on two literature-search benchmarks.

**Limitations.**

- Only two benchmarks tested, both with arXiv-only corpus coverage
- 1.5-hop bound may not generalize to disciplines with different citation density

<sub>selected: score · criteria: C1 1/3 · C2 3/3 · C3 3/3 · C4 1/3 · C5 0/3 · flags: methods_paper · verified 2026-08-26 via arxiv</sub>

## 8. From Inertia to Objectivity: Improving Deep Research Agents with Noise Isolation

Xiangxin Zhang, Zhanwei Zhang, Zhihang Fu, Binbin Lin et al. · 2026 · arXiv · experimental · overall 3/3

<https://doi.org/10.48550/arxiv.2608.23045>

**Key finding.** NIS-Agent, which applies context isolation at webpage-triage and final-answer-validation decision points to counter a newly identified 'inertia bias' (self-authored action history distorting subsequent judgment), matches competitive performance on GAIA/WebWalkerQA/BrowseComp/BrowseComp-zh while cutting token cost by 33%.

**Why it made the cut.** design-changing · selected by score · strongest on C2 agentic mechanism gain (2/3). Surfaces and fixes a specific agent-level failure mode that complicates naive attribution of gains to more search or context, directly relevant to Q2 and Q4.

**Why it matters here.** Identifies a specific, previously undiagnosed failure mode in deep-research agents that degrades judgment independent of search quantity — a mechanism the brief's Q4 should watch for, and a design fix worth weighing against reformulation/traversal moves.

**Method.** Introduces the IBIS benchmark to isolate inertia bias by controlling search observations while varying self-authorship, then evaluates NIS-Agent and a fine-tuned 8B model across four deep-research benchmarks.

**Limitations.**

- Bias measured via a purpose-built benchmark (IBIS) whose generalizability to other agent architectures is untested
- Token-cost savings reported relative to the paper's own baseline, not an external standard

<sub>selected: score · criteria: C1 0/3 · C2 2/3 · C3 0/3 · C4 2/3 · C5 2/3 · flags: contradicts, methods_paper · verified 2026-08-26 via arxiv</sub>

## 9. Multi-Turn Agentic Scientific Literature Search via Workflow Induction

Jisen Li, Bingxuan Li, Nanyi Jiang, Xuying Ning et al. · 2026 · arXiv · experimental · overall 3/3

<https://doi.org/10.48550/arxiv.2607.00597>

**Key finding.** PaperPilot-9B raises multi-turn literature search performance over a base Qwen3.5-9B toolset agent, from Hit@5 58.0→77.0, MRR 47.5→59.4, and nDCG@10 26.8→32.5, while cutting workflow execution errors from 9.5% to 0%.

**Why it made the cut.** design-changing · selected by backfill · strongest on C2 agentic mechanism gain (2/3). Core system design directly matching the brief's interest in workflow-decomposed agentic literature search with quantified gains.

**Why it matters here.** Directly decomposes agentic literature search into named operators (citation expansion, reranking, scoring) and measures the gain of the explicit workflow over an undifferentiated toolset agent, giving evidence for exactly which agentic moves the brief asks us to isolate.

**Method.** Introduces PaperPilot, an agent that induces an executable DAG of search operators (keyword search, citation expansion, filtering, scoring, reranking, evidence extraction) trained via supervised workflow imitation and preference optimization over corrupted workflows; evaluated in multi-turn interaction against a base toolset agent.

**Limitations.**

- Baseline is a base LLM toolset agent rather than a pure single-query database/BM25/embedding search ceiling
- No ablation isolating which individual operator (citation expansion vs reranking vs reformulation) drives the gain

<sub>selected: backfill · criteria: C1 1/3 · C2 2/3 · C3 2/3 · C4 1/3 · C5 0/3 · flags: methods_paper · verified 2026-08-26 via openalex, arxiv</sub>

## 10. Search-Time Contamination in Deep Research Agents: Measuring Performance Inflation in Public Benchmark Evaluation

Yongjie Wang, Xinyu Crystina Zhang, Kunhong Yao, Zhiwei Zeng et al. · 2026 · arXiv.org · experimental · overall 3/3

<https://doi.org/10.48550/arxiv.2606.05241>

**Key finding.** Search-Time Contamination — deep research agents retrieving benchmark metadata, question context, or ground-truth answers via web search — inflates measured performance by up to 4% across six public benchmarks.

**Why it made the cut.** contradicting · selected by backfill · strongest on C4 benchmark construction (3/3). Directly answers the brief's fourth question by quantifying how much reported agentic gains are inflated by search-time contamination rather than real capability.

**Why it matters here.** Directly shows that reported gains for web-searching research agents can be artifacts of benchmark contamination rather than genuine reasoning or retrieval improvement — exactly the failure-to-replicate evidence the brief prioritizes as its fourth question.

**Method.** Defines three contamination severity types, develops detection algorithms, and evaluates modern deep research agents on six public benchmarks to quantify contamination-driven performance inflation.

**Limitations.**

- Focuses on deep research/web agents broadly rather than scientific-literature-search agents specifically
- Reports an aggregate inflation ceiling (4%) without breaking down which agentic mechanism is most contamination-prone

<sub>selected: backfill · criteria: C1 0/3 · C2 0/3 · C3 0/3 · C4 3/3 · C5 3/3 · flags: contradicts · verified 2026-08-26 via openalex, arxiv</sub>

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
- [Deep Research Bench: Evaluating AI Web Research Agents](https://doi.org/10.48550/arxiv.2506.06287) (2025) — overall 3/3
- [Language agents achieve superhuman synthesis of scientific knowledge](https://doi.org/10.48550/arxiv.2409.13740) (2024) — overall 3/3
- [Agents-K1: Towards Agent-native Knowledge Orchestration](https://doi.org/10.48550/arxiv.2606.13669) (2026) — overall 3/3
- [When to use Graphs in RAG: A Comprehensive Analysis for Graph Retrieval-Augmented Generation](https://doi.org/10.48550/arxiv.2506.05690) (2025) — overall 2/3
