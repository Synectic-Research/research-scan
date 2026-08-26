# Evidence scan — p11-t2

Run `/Users/nabergoj/Projects/research-scan/research/experiments/phase11-golden/sweep/p11-t2/R15/run` · brief `/Users/nabergoj/Projects/research-scan/research/experiments/phase11-golden/sweep/p11-t2/R15/run/brief.md` · rendered 2026-08-26

| # | Paper | Year | Venue | Evidence | Verified |
|---|---|---|---|---|---|
| 1 | [BrowseComp-Plus: A More Fair and Transparent Evaluation Benchmark of Deep-Research Agent](https://doi.org/10.48550/arxiv.2508.06600) · 10.48550/arxiv.2508.06600 | 2025 | arXiv (Cornell University) | other | yes |
| 2 | [Diagnosing Search Behavior and Failure Modes in Long-Horizon Search Agents](https://doi.org/10.48550/arxiv.2608.01913) · 10.48550/arxiv.2608.01913 | 2026 | arXiv | observational | yes |
| 3 | [Projecting BrowseComp-Plus onto ClimbMix: Toward More Realistic Corpora for Agentic Search](https://arxiv.org/abs/2608.20317) | 2026 | — | other | yes |
| 4 | [Multi-Turn Agentic Scientific Literature Search via Workflow Induction](https://doi.org/10.48550/arxiv.2607.00597) · 10.48550/arxiv.2607.00597 | 2026 | arXiv | experimental | yes |
| 5 | [Deep Research Agents: A Systematic Examination And Roadmap](https://doi.org/10.48550/arxiv.2506.18096) · 10.48550/arxiv.2506.18096 | 2025 | arXiv.org | other | yes |
| 6 | [When Deep Research Agents Stagnate: Enhancing Reasoning with Retrieval-Aware Agent Control](https://doi.org/10.48550/arxiv.2608.15191) · 10.48550/arxiv.2608.15191 | 2026 | arXiv | experimental | yes |
| 7 | [Search-Time Contamination in Deep Research Agents: Measuring Performance Inflation in Public Benchmark Evaluation](https://doi.org/10.48550/arxiv.2606.05241) · 10.48550/arxiv.2606.05241 | 2026 | arXiv.org | experimental | yes |
| 8 | [EviReform: Evidence-Guided Query Reformulation for Multi-Hop Graph Retrieval](https://doi.org/10.48550/arxiv.2608.13006) · 10.48550/arxiv.2608.13006 | 2026 | arXiv | experimental | yes |
| 9 | [ResearchRubrics: A Benchmark of Prompts and Rubrics For Evaluating Deep Research Agents](https://doi.org/10.48550/arxiv.2511.07685) · 10.48550/arxiv.2511.07685 | 2025 | arXiv (Cornell University) | other | yes |
| 10 | [DynaKRAG: A Unified Framework for Learnable Evidence Control in Multi-Hop Retrieval-Augmented Generation](https://doi.org/10.48550/arxiv.2607.06507) · 10.48550/arxiv.2607.06507 | 2026 | arXiv | experimental | yes |

## 1. BrowseComp-Plus: A More Fair and Transparent Evaluation Benchmark of Deep-Research Agent

Zijian Chen, Xueguang Ma, Shengyao Zhuang, Ping Nie et al. · 2025 · arXiv (Cornell University) · other · overall 3/3

<https://doi.org/10.48550/arxiv.2508.06600>

**Key finding.** On a fixed, curated corpus, Search-R1 with BM25 achieves only 3.86% accuracy versus GPT-5 at 55.9%, rising to 70.1% when GPT-5 is paired with the Qwen3-Embedding-8B retriever.

**Why it made the cut.** design-changing · selected by score · strongest on C1 baseline recall ceiling (3/3). Directly measures the single-query retrieval baseline ceiling with a controlled corpus and disentangles retriever from agent contribution — the anchor paper for decision 1.

**Why it matters here.** Gives a concrete, reproducible retrieval-baseline ceiling (BM25 vs. dense retriever) that any claimed agentic gain must be measured against, and shows retriever choice alone swings accuracy by over an order of magnitude — directly anchors decision 1.

**Method.** Introduces BrowseComp-Plus, a fixed corpus derived from BrowseComp with human-verified supporting documents and mined hard negatives, enabling controlled disentanglement of agent vs. retriever contributions.

**Limitations.**

- Corpus assembled per-query from the benchmark's own documents, later shown to bias evidence selection (see dc6612fba47a)
- single benchmark family (BrowseComp)

<sub>selected: score · criteria: C1 3/3 · C2 1/3 · C3 3/3 · C4 3/3 · C5 1/3 · flags: methods_paper · verified 2026-08-26 via openalex, arxiv</sub>

## 2. Diagnosing Search Behavior and Failure Modes in Long-Horizon Search Agents

Qi Liu, Jiaxin Mao, Fengbin Zhu, Tat-Seng Chua · 2026 · arXiv · observational · overall 3/3

<https://doi.org/10.48550/arxiv.2608.01913>

**Key finding.** Search effort and answer quality are only weakly aligned; answer accuracy correlates more with cumulative retrieval recall than with number of searches, and useful evidence often appears early while agents keep searching redundantly.

**Why it made the cut.** contradicting · selected by score · strongest on C2 agentic mechanism gain (3/3). Directly answers decision 4 (where reported gains fail to hold) by showing search effort doesn't track answer quality, using controlled relevance judgments relevant to decision 3 as well.

**Why it matters here.** Directly undercuts the premise that more iterative agentic search reliably improves outcomes, showing that the best agents issue fewer redundant queries — this reframes what an 'agentic gain' should be measured against and how stopping criteria should be designed.

**Method.** Trajectory-level diagnosis of six long-horizon search agents on BrowseComp-Plus (fixed retrieval, human-annotated document-level relevance judgments), validated on BrowseComp with an open-web API; decomposes failures into retrieval gaps vs. utilization gaps.

**Limitations.**

- Limited to six agents and two benchmarks (BrowseComp-Plus, BrowseComp)
- retrieval model and harness held fixed, so findings may not generalize to other retrievers

<sub>selected: score · criteria: C1 2/3 · C2 3/3 · C3 1/3 · C4 1/3 · C5 3/3 · flags: contradicts · verified 2026-08-26 via openalex, arxiv</sub>

## 3. Projecting BrowseComp-Plus onto ClimbMix: Toward More Realistic Corpora for Agentic Search

Sahel Sharifymoghaddam, Lin Gu, Yijun Ge, Jimmy Lin · 2026 · no venue · other · overall 3/3

<https://arxiv.org/abs/2608.20317>

**Key finding.** Relocating BrowseComp-Plus questions onto an independently built corpus (ClimbMix) causes the strongest agent's evidence recall to fall from 84.3% to 21.4% and answer accuracy to drop by five points, while search calls rise by 63%.

**Why it made the cut.** contradicting · selected by score · strongest on C4 benchmark construction (3/3). Directly demonstrates a reported agentic/retrieval gain shrinking dramatically under an independently constructed corpus, exactly the replication-failure evidence decision 4 asks for.

**Why it matters here.** Directly shows that a benchmark's per-query corpus construction (documents selected per query, as in BrowseComp-Plus) inflates reported retrieval performance — exactly the decision-4 evidence the brief wants, that a reported gain does not survive a different, independently built corpus.

**Method.** A projection pipeline decomposes each question into atomic reasoning hops and grounds every hop in a 400B-token, 553M-document corpus built without reference to any benchmark, verified by automatic checks, an independent agent, and human review; yields 57 fully grounded questions from 830 BrowseComp-Plus test questions.

**Limitations.**

- Very small resulting benchmark (57 questions) after strict verification
- pipeline validated on only one source benchmark (BrowseComp-Plus) so far

<sub>selected: score · criteria: C1 1/3 · C2 1/3 · C3 1/3 · C4 3/3 · C5 3/3 · flags: contradicts, methods_paper · verified 2026-08-26 via arxiv, s2</sub>

## 4. Multi-Turn Agentic Scientific Literature Search via Workflow Induction

Jisen Li, Bingxuan Li, Nanyi Jiang, Xuying Ning et al. · 2026 · arXiv · experimental · overall 3/3

<https://doi.org/10.48550/arxiv.2607.00597>

**Key finding.** PaperPilot's workflow-induction agent improves multi-turn scientific literature search over a base toolset agent, raising Hit@5 from 58.0 to 77.0, MRR from 47.5 to 59.4, nDCG@10 from 26.8 to 32.5, and cutting workflow execution errors from 9.5% to 0%.

**Why it made the cut.** design-changing · selected by score · strongest on C2 agentic mechanism gain (3/3). Directly matches the brief's system: a scientific-literature-search agent combining citation expansion, reranking, and query reformulation with quantified, decomposable gains over a fixed baseline.

**Why it matters here.** The most directly on-target system in the shortlist: an explicit, editable agentic workflow for scientific literature search combining citation expansion, reranking, and query refinement, with quantified gains over a fixed-pipeline agent — exactly the design comparison decision 2 needs.

**Method.** Frames scientific literature search as induction of an executable DAG of operators (keyword search, citation expansion, filtering, scoring, reranking, evidence extraction); trained via supervised workflow imitation and preference optimization over controlled workflow corruptions, evaluated against a Qwen3.5-9B toolset-agent baseline.

**Limitations.**

- Baseline is a toolset agent, not a plain single-query database search, so the decision-1 recall ceiling is not directly established
- gains measured on the authors' own workflow-corruption training setup; generalization to independent benchmarks untested

<sub>selected: score · criteria: C1 1/3 · C2 3/3 · C3 3/3 · C4 1/3 · C5 0/3 · flags: methods_paper · verified 2026-08-26 via openalex, arxiv</sub>

## 5. Deep Research Agents: A Systematic Examination And Roadmap

Yuxuan Huang, Yihang Chen, Haozhen Zhang, Kang Li et al. · 2025 · arXiv.org · other · overall 3/3

<https://doi.org/10.48550/arxiv.2506.18096>

**Key finding.** Proposes a taxonomy distinguishing static vs. dynamic agent workflows and single- vs. multi-agent architectures, and critiques current benchmarks for restricted external-knowledge access, sequential inefficiencies, and metric misalignment with practical objectives.

**Why it made the cut.** foundational · selected by score · strongest on C2 agentic mechanism gain (2/3). Orienting survey that frames the taxonomy of agentic mechanisms and names benchmark construction weaknesses relevant to decisions 2-4.

**Why it matters here.** Gives the field's current taxonomy and names specific benchmark weaknesses (metric misalignment, restricted knowledge access) that decisions 3 and 4 need to be checked against before trusting any single system's reported numbers.

**Method.** Systematic survey/roadmap analyzing information acquisition strategies (API vs. browser), tool-use frameworks, and existing benchmarks for Deep Research agents; maintains a curated public repository.

**Limitations.**

- Survey, not new empirical evidence
- benchmark critique is qualitative, not quantified

<sub>selected: score · criteria: C1 1/3 · C2 2/3 · C3 1/3 · C4 2/3 · C5 1/3 · flags: review · verified 2026-08-26 via arxiv</sub>

## 6. When Deep Research Agents Stagnate: Enhancing Reasoning with Retrieval-Aware Agent Control

Heydar Soudani, Elizabeth Lingg, Faegheh Hasibi, Navid Rekabsaz · 2026 · arXiv · experimental · overall 3/3

<https://doi.org/10.48550/arxiv.2608.15191>

**Key finding.** Adding the Retrieval-Aware Agent Controller (RAAC) to deep research agents on BrowseComp-Plus reduces search calls by an average of 14 and improves the best-performing agent's accuracy by up to 10% (3% on average).

**Why it made the cut.** design-changing · selected by score · strongest on C2 agentic mechanism gain (3/3). Attributes a quantified performance gain to a specific, well-defined agentic control mechanism (retrieval-aware stopping/action selection), directly answering decision 2.

**Why it matters here.** Isolates a specific controllable mechanism (novelty/coverage-aware stopping and action selection) as the source of measured gain, exactly the kind of mechanism attribution decision 2 needs rather than crediting the whole system.

**Method.** Analyzes reasoning trajectories of multiple deep-research agents to show most iterations add little value ('reasoning stagnation'), then introduces unsupervised signals (search novelty, information coverage) driving RAAC's action selection, evaluated across a large set of DRAs on BrowseComp-Plus.

**Limitations.**

- Gains concentrated in the best-performing agent (10%) vs. average (3%), so benefit is agent-dependent
- evaluated on one benchmark family (BrowseComp-Plus)

<sub>selected: score · criteria: C1 1/3 · C2 3/3 · C3 2/3 · C4 0/3 · C5 1/3 · flags: methods_paper · verified 2026-08-26 via arxiv</sub>

## 7. Search-Time Contamination in Deep Research Agents: Measuring Performance Inflation in Public Benchmark Evaluation

Yongjie Wang, Xinyu Crystina Zhang, Kunhong Yao, Zhiwei Zeng et al. · 2026 · arXiv.org · experimental · overall 3/3

<https://doi.org/10.48550/arxiv.2606.05241>

**Key finding.** Search-Time Contamination — where deep research agents retrieve benchmark metadata, question context, or ground-truth answers via web search during evaluation — is widespread across six public benchmarks and inflates measured performance by up to 4%.

**Why it made the cut.** contradicting · selected by score · strongest on C4 benchmark construction (3/3). Directly answers the brief's question of where reported agentic gains fail to hold up, showing a concrete, measured mechanism (search-time leakage) that inflates benchmark scores.

**Why it matters here.** Directly undermines the premise that reported agentic gains are real: some of the measured improvement on public benchmarks is search-time leakage rather than genuine reasoning or retrieval capability, meaning any comparison to single-query baselines run on the same contaminated benchmarks needs re-checking before its gain is trusted.

**Method.** Defines three contamination severity levels (metadata leakage, question-context leakage, explicit answer leakage), builds detection algorithms, and evaluates modern deep research agents on six public benchmarks.

**Limitations.**

- Benchmarks studied are general reasoning/QA benchmarks for deep research agents, not necessarily scientific-literature-search-specific sets
- Contamination severity may vary by benchmark and agent architecture not covered here

<sub>selected: score · criteria: C1 1/3 · C2 0/3 · C3 0/3 · C4 3/3 · C5 3/3 · flags: contradicts, methods_paper · verified 2026-08-26 via openalex, arxiv</sub>

## 8. EviReform: Evidence-Guided Query Reformulation for Multi-Hop Graph Retrieval

Xin Xu, Yoshua Y. Li · 2026 · arXiv · experimental · overall 3/3

<https://doi.org/10.48550/arxiv.2608.13006>

**Key finding.** EviReform's evidence-guided residual queries improve multi-hop graph retrieval by up to 5.59 Recall@5 points and 4.50 F1 points over the strongest baseline on 2WikiMultiHopQA, HotpotQA, and MuSiQue.

**Why it made the cut.** plan-influencing · selected by score · strongest on C2 agentic mechanism gain (3/3). A quantified method paper isolating query reformulation combined with graph retrieval as the source of retrieval gain, directly informing decision 2 and the underlying retrieval-method question.

**Why it matters here.** Provides a concrete, quantified mechanism for combining query reformulation with graph traversal — the two specific agentic moves the brief names — clarifying which part of a hybrid design actually carries a measured retrieval gain.

**Method.** Separates residual-query formulation (from retrieved passages) from graph-based evidence aggregation, normalizing and combining original and residual retrieval signals propagated along entity-shared propositions; evaluated on three multi-hop QA benchmarks.

**Limitations.**

- Evaluated on generic multi-hop QA benchmarks rather than scientific literature/citation graphs
- no comparison against a single-query database search baseline

<sub>selected: score · criteria: C1 0/3 · C2 3/3 · C3 3/3 · C4 0/3 · C5 0/3 · flags: methods_paper · verified 2026-08-26 via openalex, arxiv</sub>

## 9. ResearchRubrics: A Benchmark of Prompts and Rubrics For Evaluating Deep Research Agents

M. Sharma, Zhang, Chen Bo Calvin, Chaithanya Bandi, Clinton Wang et al. · 2025 · arXiv (Cornell University) · other · overall 3/3

<https://doi.org/10.48550/arxiv.2511.07685>

**Key finding.** Even leading deep-research agents (Gemini DR, OpenAI DR) achieve under 68% average compliance with 2,500+ expert-written rubrics across domain-diverse prompts.

**Why it made the cut.** plan-influencing · selected by backfill · strongest on C4 benchmark construction (3/3). A rigorously constructed benchmark with explicit labeling methodology — central evidence for how evaluation sets for literature-search-like agents should be built.

**Why it matters here.** A rigorously constructed rubric-based benchmark showing current deep-research agents fall well short of full compliance, directly informing how evaluation sets should be built and interpreted (decision 3) rather than trusting self-reported end-to-end scores.

**Method.** ResearchRubrics benchmark built with 2,800+ hours of human labor pairing realistic prompts with fine-grained expert rubrics, plus a three-axis complexity taxonomy and human/model-based evaluation protocols.

**Limitations.**

- Rubric-based scoring does not directly measure recall against a single-query baseline
- domain-diverse prompts may not map cleanly onto scientific literature search specifically

<sub>selected: backfill · criteria: C1 0/3 · C2 0/3 · C3 0/3 · C4 3/3 · C5 2/3 · flags: methods_paper · verified 2026-08-26 via openalex, arxiv</sub>

## 10. DynaKRAG: A Unified Framework for Learnable Evidence Control in Multi-Hop Retrieval-Augmented Generation

Yaqi Wu, Xiaolei Guo, Chenyu Zhou, Jiaqi Huang et al. · 2026 · arXiv · experimental · overall 3/3

<https://doi.org/10.48550/arxiv.2607.06507>

**Key finding.** DynaKRAG's learned state-conditioned policy for coordinating iterative retrieval, query reformulation, and sufficiency checking ranks first in EM/F1 across all nine dataset-backbone pairs, with 10.1-34.3% token efficiency and 15.1-43.4% retrieval-call efficiency gains.

**Why it made the cut.** plan-influencing · selected by backfill · strongest on C2 agentic mechanism gain (3/3). Quantifies specific agentic evidence-control operations' contribution to retrieval gain and efficiency, directly relevant to decision 2's mechanism attribution question.

**Why it matters here.** Demonstrates that coordinating specific agentic operations (iterative retrieval, reformulation, sufficiency checking) via a learned policy, rather than a fixed pipeline, yields measurable efficiency and accuracy gains, informing how to attribute and design agentic mechanisms (decision 2).

**Method.** Unified evidence-action framework with a deterministic validity layer, a learned continuation gate, and a learned advantage scorer over evidence operations; evaluated on HotpotQA, 2Wiki, and MuSiQue with three backbones (Qwen2.5-7B, GPT-4o-mini, Llama-3.1-8B).

**Limitations.**

- Evaluated on generic multi-hop QA rather than scientific literature search
- requires training a learned policy, adding complexity relative to prompted agent baselines

<sub>selected: backfill · criteria: C1 0/3 · C2 3/3 · C3 2/3 · C4 0/3 · C5 0/3 · flags: methods_paper · verified 2026-08-26 via openalex, arxiv</sub>

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

- [DeepResearch Bench: A Comprehensive Benchmark for Deep Research Agents](https://doi.org/10.48550/arxiv.2506.11763) (2025) — overall 3/3
- [HySemRAG: A Hybrid Semantic Retrieval-Augmented Generation Framework for Automated Literature Synthesis and Methodological Gap Analysis](https://doi.org/10.48550/arxiv.2508.05666) (2025) — overall 2/3
- [From Inertia to Objectivity: Improving Deep Research Agents with Noise Isolation](https://doi.org/10.48550/arxiv.2608.23045) (2026) — overall 2/3
- [Why Neighborhoods Matter: Traversal Context and Provenance in Agentic GraphRAG](https://doi.org/10.48550/arxiv.2605.15109) (2026) — overall 2/3
- [Autonomous Research Agents: A Survey of AI Scientists and the Verification Gap](https://doi.org/10.48550/arxiv.2608.05179) (2026) — overall 1/3
