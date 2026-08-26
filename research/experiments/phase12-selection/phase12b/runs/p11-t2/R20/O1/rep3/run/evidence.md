# Evidence scan — p11-t2

Run `/Users/nabergoj/Projects/research-scan/research/experiments/phase12-selection/phase12b/runs/p11-t2/R20/O1/rep3/run` · brief `/Users/nabergoj/Projects/research-scan/research/experiments/phase12-selection/phase12b/runs/p11-t2/R20/O1/rep3/run/brief.md` · rendered 2026-08-26

| # | Paper | Year | Venue | Evidence | Verified |
|---|---|---|---|---|---|
| 1 | [Diagnosing Search Behavior and Failure Modes in Long-Horizon Search Agents](https://doi.org/10.48550/arxiv.2608.01913) · 10.48550/arxiv.2608.01913 | 2026 | arXiv | experimental | yes |
| 2 | [BrowseComp-Plus: A More Fair and Transparent Evaluation Benchmark of Deep-Research Agent](https://doi.org/10.48550/arxiv.2508.06600) · 10.48550/arxiv.2508.06600 | 2025 | arXiv (Cornell University) | experimental | yes |
| 3 | [Towards Recursive Self-Evolving Agentic Literature Retrieval](https://doi.org/10.48550/arxiv.2605.14306) · 10.48550/arxiv.2605.14306 | 2026 | arXiv | experimental | yes |
| 4 | [Deep Research Agents: A Systematic Examination And Roadmap](https://doi.org/10.48550/arxiv.2506.18096) · 10.48550/arxiv.2506.18096 | 2025 | arXiv.org | other | yes |
| 5 | [Projecting BrowseComp-Plus onto ClimbMix: Toward More Realistic Corpora for Agentic Search](https://arxiv.org/abs/2608.20317) | 2026 | — | experimental | yes |
| 6 | [PaSa: An LLM Agent for Comprehensive Academic Paper Search](https://doi.org/10.48550/arxiv.2501.10120) · 10.48550/arxiv.2501.10120 | 2025 | Annual Meeting of the Association for Computational Linguistics | experimental | yes |
| 7 | [Structurally-bounded Agentic Graph Exploration for Evidence-Grounded Scholarly DeepSearch](https://doi.org/10.48550/arxiv.2608.24809) · 10.48550/arxiv.2608.24809 | 2026 | arXiv | experimental | yes |
| 8 | [Multi-Turn Agentic Scientific Literature Search via Workflow Induction](https://doi.org/10.48550/arxiv.2607.00597) · 10.48550/arxiv.2607.00597 | 2026 | arXiv | experimental | yes |
| 9 | [AI's Capability in Assisting Scientific Research in Physics, Astrophysics, and Cosmology I: Literature Review](https://doi.org/10.48550/arxiv.2607.25672) · 10.48550/arxiv.2607.25672 | 2026 | arXiv | observational | yes |
| 10 | [Language agents achieve superhuman synthesis of scientific knowledge](https://doi.org/10.48550/arxiv.2409.13740) · 10.48550/arxiv.2409.13740 | 2024 | arXiv (Cornell University) | experimental | yes |

## 1. Diagnosing Search Behavior and Failure Modes in Long-Horizon Search Agents

Qi Liu, Jiaxin Mao, Fengbin Zhu, Tat-Seng Chua · 2026 · arXiv · experimental · overall 3/3

<https://doi.org/10.48550/arxiv.2608.01913>

**Key finding.** Across six agents on BrowseComp-Plus and BrowseComp, search effort and answer quality are only weakly aligned; accuracy tracks cumulative retrieval recall far better than number of searches, and the best agents issue far fewer redundant queries despite useful evidence often appearing early.

**Why it made the cut.** plan-influencing · selected by score · strongest on C2 agentic mechanism gain (3/3). A trajectory-level failure-mode analysis that decomposes retrieval vs. utilization gaps in agentic search, central to whether agentic moves carry the claimed gain.

**Why it matters here.** Directly answers question 2 and 4: it isolates which agentic behaviors (query reformulation, evidence selection, stopping) actually carry the gain, and shows that raw search volume is a misleading proxy for improvement, which should reshape how we measure agentic gains rather than just count search calls.

**Method.** Trajectory-level diagnosis with human-annotated document relevance judgments, retrieval model and evaluation harness held fixed across six long-horizon search agents on BrowseComp-Plus, validated on BrowseComp with an open-web API.

**Limitations.**

- evaluated on a small set of six agents
- relies on document-level relevance judgments that may not generalize across corpora

<sub>selected: score · criteria: C1 1/3 · C2 3/3 · C3 1/3 · C4 2/3 · C5 3/3 · flags: contradicts · verified 2026-08-26 via openalex, arxiv</sub>

## 2. BrowseComp-Plus: A More Fair and Transparent Evaluation Benchmark of Deep-Research Agent

Zijian Chen, Xueguang Ma, Shengyao Zhuang, Ping Nie et al. · 2025 · arXiv (Cornell University) · experimental · overall 3/3

<https://doi.org/10.48550/arxiv.2508.06600>

**Key finding.** On a fixed, human-verified corpus, Search-R1 with BM25 retrieval reaches only 3.86% accuracy while GPT-5 reaches 55.9%, rising to 70.1% when GPT-5 is paired with a stronger Qwen3-Embedding-8B retriever and fewer search calls.

**Why it made the cut.** foundational · selected by score · strongest on C1 baseline recall ceiling (3/3). The central controlled benchmark establishing single-query retriever baselines and disentangling retrieval from agent quality — foundational to nearly every other paper in this list.

**Why it matters here.** Gives the field's clearest quantified baseline-recall ceiling (BM25 at 3.86% accuracy) against which every reported agentic gain in this space should be measured, and its construction methodology (fixed corpus, human verification) is the template question 3 is asking about.

**Method.** Benchmark construction paper: derives a fixed corpus with human-verified supporting documents and mined hard negatives from BrowseComp, enabling controlled disentanglement of retriever quality from agent reasoning quality.

**Limitations.**

- single benchmark domain (BrowseComp-style deep-research questions)
- results depend heavily on the paired retriever, complicating cross-paper comparison

<sub>selected: score · criteria: C1 3/3 · C2 1/3 · C3 2/3 · C4 3/3 · C5 1/3 · flags: methods_paper · verified 2026-08-26 via openalex, arxiv</sub>

## 3. Towards Recursive Self-Evolving Agentic Literature Retrieval

Yuwen Du, Tian Jin, Jing Kang, Xianghe Pang et al. · 2026 · arXiv · experimental · overall 3/3

<https://doi.org/10.48550/arxiv.2605.14306>

**Key finding.** PaSaMaster achieves a 16.5× higher F1-score than Google Scholar and a 37.8% higher F1-score than GPT-5.2 across 38 disciplines in PaSaMaster-Bench, at about 1% of the cost, while cutting source hallucination from 32.66% to zero.

**Why it made the cut.** design-changing · selected by score · strongest on C1 baseline recall ceiling (3/3). Reports large gains over an explicit single-query database baseline attributed to a specific iterative retrieval mechanism, hitting decisions 1 and 2 directly.

**Why it matters here.** Directly anchors the recall/precision ceiling question (decision 1) against a real single-query search baseline (Google Scholar) and attributes the gain to a specific self-evolving retrieval mechanism (decision 2), with an explicit multi-discipline benchmark (decision 3).

**Method.** Recursive self-evolving retrieval architecture separating frontier-LLM intent understanding from lightweight-model retrieval/scoring, evaluated against Google Scholar and GPT-5.2 baselines on a new 38-discipline benchmark. Abstract-only.

**Limitations.**

- benchmark and baseline comparisons are self-reported by the system's own authors
- F1 multiplier vs Google Scholar depends on undisclosed query/evaluation protocol for Google Scholar
- no discussion of conditions under which the gain might not replicate

<sub>selected: score · criteria: C1 3/3 · C2 3/3 · C3 2/3 · C4 2/3 · C5 0/3 · flags: methods_paper · verified 2026-08-26 via openalex, arxiv</sub>

## 4. Deep Research Agents: A Systematic Examination And Roadmap

Yuxuan Huang, Yihang Chen, Haozhen Zhang, Kang Li et al. · 2025 · arXiv.org · other · overall 3/3

<https://doi.org/10.48550/arxiv.2506.18096>

**Key finding.** A taxonomy and critical review of Deep Research agents identifies systematic benchmark limitations — restricted external-knowledge access, sequential execution inefficiencies, and misalignment between evaluation metrics and agents' practical objectives — across current architectures.

**Why it made the cut.** plan-influencing · selected by score · strongest on C4 benchmark construction (3/3). A survey that organizes the system-design space and explicitly flags benchmark-construction and metric-misalignment problems, informing how the scan should read every other paper's numbers.

**Why it matters here.** Synthesizes exactly the taxonomy the brief needs to compare designs (reformulation, graph traversal, iterative crawling) on common terms, and its critique of benchmark-metric misalignment is a direct pointer to where reported gains in this literature may not be trustworthy.

**Method.** Narrative systematic examination and taxonomy of Deep Research agent architectures, information-acquisition strategies (API vs. browser), tool-use frameworks, and existing benchmarks; abstract-only detail on selection method.

**Limitations.**

- narrative rather than systematic-protocol review
- abstract does not quantify claims, relies on qualitative taxonomy

<sub>selected: score · criteria: C1 1/3 · C2 2/3 · C3 1/3 · C4 3/3 · C5 2/3 · flags: review · verified 2026-08-26 via arxiv</sub>

## 5. Projecting BrowseComp-Plus onto ClimbMix: Toward More Realistic Corpora for Agentic Search

Sahel Sharifymoghaddam, Lin Gu, Yijun Ge, Jimmy Lin · 2026 · no venue · experimental · overall 3/3

<https://arxiv.org/abs/2608.20317>

**Key finding.** Relocating BrowseComp-Plus's questions to a benchmark-agnostic 400B-token corpus (ClimbMix) drops the strongest agent's evidence recall from 84.3% to 21.4% and costs 63% more search calls for only a 5-point drop in final answer accuracy, exposing that the original corpus's query-derived evidence and negatives inflated retrieval-looking performance.

**Why it made the cut.** contradicting · selected by score · strongest on C4 benchmark construction (3/3). The single clearest demonstration in this shortlist of a reported agentic-search gain shrinking dramatically under a different, more realistic corpus — exactly the hardest evidence the brief asks the scan to surface.

**Why it matters here.** Directly demonstrates question 4: a benchmark's construction (evidence and negatives selected per query) can inflate retrieval numbers that collapse under a neutral corpus, meaning reported agentic gains on BrowseComp-Plus-style benchmarks should be read as corpus-dependent rather than general.

**Method.** Projection pipeline decomposing each BrowseComp-Plus question into atomic reasoning hops, grounding each hop in ClimbMix via automatic verification, an independent agent check, and human review; yields 57 fully-grounded questions with relevance judgments, applied to the strongest evaluated agent.

**Limitations.**

- only 57 fully-grounded questions after strict verification, a small evaluation set
- tested on a single strongest agent per the abstract
- pipeline generality across other benchmark types not yet demonstrated beyond this first projection

<sub>selected: score · criteria: C1 1/3 · C2 1/3 · C3 0/3 · C4 3/3 · C5 3/3 · flags: contradicts, methods_paper · verified 2026-08-26 via arxiv, s2</sub>

## 6. PaSa: An LLM Agent for Comprehensive Academic Paper Search

Yichen He, Guanhua Huang, Peiyuan Feng, Yuan Lin et al. · 2025 · Annual Meeting of the Association for Computational Linguistics · experimental · overall 3/3

<https://doi.org/10.48550/arxiv.2501.10120>

**Key finding.** PaSa-7B, an RL-trained paper-search agent, beats the best Google+GPT-4o baseline by 37.78% in recall@20 and 39.90% in recall@50 on the real-world RealScholarQuery benchmark.

**Why it made the cut.** foundational · selected by score · strongest on C1 baseline recall ceiling (3/3). Foundational agentic academic-search system with explicit baseline comparisons and benchmark construction, directly on the brief's core system-and-benchmark axis.

**Why it matters here.** One of the clearest quantified comparisons of agentic paper search against single-query search-engine baselines, and its two-benchmark design (synthetic train / real-world test) is a template for how construction choices affect reported gains.

**Method.** RL-trained LLM agent optimized on a synthetic 35k-query dataset (AutoScholarQuery), evaluated on a newly built real-world benchmark (RealScholarQuery) against Google, Google Scholar, ChatGPT, and GPT-o1 baselines.

**Limitations.**

- trained on synthetic queries which may not transfer perfectly to real usage
- recall-based metrics only, no analysis of failure modes

<sub>selected: score · criteria: C1 3/3 · C2 1/3 · C3 1/3 · C4 3/3 · C5 0/3 · flags: methods_paper · verified 2026-08-26 via openalex, arxiv</sub>

## 7. Structurally-bounded Agentic Graph Exploration for Evidence-Grounded Scholarly DeepSearch

Rima Hazra, Sayan Layek, Somnath Banerjee, Soumen Chakrabarti et al. · 2026 · arXiv · experimental · overall 3/3

<https://doi.org/10.48550/arxiv.2608.24809>

**Key finding.** A bounded, single-query-seeded 1.5-hop citation-graph expansion with entailment pruning and recency-aware random-walk ranking (Crase) outperforms open-ended deep research agents by up to 3x recall@50 at roughly a third of the cost on LitSearch and a further benchmark over a 500K-paper arXiv corpus.

**Why it made the cut.** design-changing · selected by score · strongest on C2 agentic mechanism gain (3/3). Proposes and quantifies a specific citation-graph-traversal mechanism as the source of gain over open-ended agentic search, matching C2 and C3 directly.

**Why it matters here.** Directly attributes a measured, large gain to a specific agentic move (bounded citation-graph traversal) rather than an undifferentiated agent loop, which is exactly the decomposition the brief's question 2 asks for.

**Method.** System design paper: one search-engine query for seeds, 1.5-hop citation expansion, entailment-based edge pruning, recency-aware random-walk reranking; compared against proprietary-model deep research agents on two benchmarks over a fixed 500K-paper corpus.

**Limitations.**

- evaluated on a fixed arXiv corpus that may not generalize to other fields
- no ablation isolating entailment pruning versus the random-walk ranking separately in the abstract

<sub>selected: score · criteria: C1 1/3 · C2 3/3 · C3 3/3 · C4 1/3 · C5 0/3 · flags: methods_paper · verified 2026-08-26 via arxiv</sub>

## 8. Multi-Turn Agentic Scientific Literature Search via Workflow Induction

Jisen Li, Bingxuan Li, Nanyi Jiang, Xuying Ning et al. · 2026 · arXiv · experimental · overall 3/3

<https://doi.org/10.48550/arxiv.2607.00597>

**Key finding.** PaperPilot-9B raises Hit@5 from 58.0 to 77.0, MRR from 47.5 to 59.4, and nDCG@10 from 26.8 to 32.5 over a base toolset agent, while reducing workflow execution errors from 9.5% to 0%.

**Why it made the cut.** design-changing · selected by score · strongest on C2 agentic mechanism gain (3/3). Directly tests which agentic components (workflow induction, citation expansion, reranking) drive gains in a multi-turn literature search agent — core to the brief's decision 2.

**Why it matters here.** Demonstrates that decomposing the agent into an explicit, editable DAG of citation-expansion, filtering, scoring and reranking operators — rather than leaving it as an undifferentiated agentic loop — is what carries the measured gain, directly answering the brief's second decision.

**Method.** Trains a 9B model via supervised workflow imitation plus preference optimization over corrupted workflows, evaluated in multi-turn interaction against a base Qwen3.5-9B toolset agent. Abstract-only.

**Limitations.**

- comparison baseline is a toolset agent, not an explicit single-query database search ceiling
- no benchmark construction detail given in the abstract
- very recent preprint with zero citations

<sub>selected: score · criteria: C1 1/3 · C2 3/3 · C3 2/3 · C4 0/3 · C5 0/3 · flags: methods_paper · verified 2026-08-26 via openalex, arxiv</sub>

## 9. AI's Capability in Assisting Scientific Research in Physics, Astrophysics, and Cosmology I: Literature Review

Anamaria Hell, Kateryna Vovk, Veena Krishnaraj, Jia Liu et al. · 2026 · arXiv · observational · overall 3/3

<https://doi.org/10.48550/arxiv.2607.25672>

**Key finding.** Across eight expert-conceived literature-review tasks, overlap between human- and AI-selected references was under 6%, and mid-2025 LLM tools produced real-but-wrong metadata in 64% of cited references despite low outright fabrication (3%).

**Why it made the cut.** contradicting · selected by backfill · strongest on C5 gain replication failure (3/3). Empirically shows agentic/LLM-assisted literature search failing to reproduce expert search quality, exactly the hardest-to-find contradicting evidence the brief asks for.

**Why it matters here.** A direct empirical challenge to the premise that agentic LLM literature search reliably matches or beats expert/human search — low overlap and high metadata error rates mean reported 'success' numbers from these tools require independent verification before being trusted as ceiling or gain estimates.

**Method.** Controlled parallel comparison of human experts versus mid-2025 LLM tools (ChatGPT-4o, ChatGPT Deep Research, Gemini) performing identical literature-search tasks across eight physics/astrophysics/cosmology projects; single-project follow-up test of a 2026 model shows zero errors.

**Limitations.**

- small sample of eight projects
- domain-specific to physics/astro/cosmology
- improvement claim for the 2026 model rests on a single project

<sub>selected: backfill · criteria: C1 1/3 · C2 0/3 · C3 0/3 · C4 2/3 · C5 3/3 · flags: contradicts · verified 2026-08-26 via openalex, arxiv</sub>

## 10. Language agents achieve superhuman synthesis of scientific knowledge

Michael Skarlinski, Sam Cox, Jon M. Laurent, James D. Braza et al. · 2024 · arXiv (Cornell University) · experimental · overall 3/3

<https://doi.org/10.48550/arxiv.2409.13740>

**Key finding.** PaperQA2 matches or exceeds subject-matter-expert performance on literature retrieval, summarization, and contradiction-detection tasks, identifying 2.34 ± 1.99 contradictions per paper in a biology subset, 70% of which are validated by human experts.

**Why it made the cut.** foundational · selected by backfill · strongest on C4 benchmark construction (2/3). The foundational, highly-cited claim that agentic literature search agents exceed expert performance, against which later replication-failure evidence must be read.

**Why it matters here.** The landmark claim the field argues with — that an agentic literature-search system already exceeds human experts — sets the premise the brief's decision 4 asks us to stress-test, and LitQA2 is a benchmark later systems are measured against.

**Method.** Rigorous human-AI comparison methodology on real-world literature-research tasks (retrieval, summarization, contradiction detection), with a new benchmark (LitQA2) guiding system design. Abstract-only.

**Limitations.**

- comparison is to human experts rather than to a single-query database search baseline
- abstract does not isolate which agentic mechanism drives the gain
- contradiction-detection validated only on a biology subset

<sub>selected: backfill · criteria: C1 1/3 · C2 1/3 · C3 1/3 · C4 2/3 · C5 0/3 · flags: methods_paper · verified 2026-08-26 via openalex, arxiv</sub>

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

- [When to use Graphs in RAG: A Comprehensive Analysis for Graph Retrieval-Augmented Generation](https://doi.org/10.48550/arxiv.2506.05690) (2025) — overall 2/3
- [Is Grep All You Need? How Agent Harnesses Reshape Agentic Search](https://doi.org/10.48550/arxiv.2605.15184) (2026) — overall 2/3
- [EviReform: Evidence-Guided Query Reformulation for Multi-Hop Graph Retrieval](https://doi.org/10.48550/arxiv.2608.13006) (2026) — overall 2/3
- [ReBOL: Retrieval via Bayesian Optimization with Batched LLM Relevance Observations and Query Reformulation](https://doi.org/10.48550/arxiv.2603.20513) (2026) — overall 2/3
- [WisPaper: Your AI Scholar Search Engine](https://doi.org/10.48550/arxiv.2512.06879) (2025) — overall 2/3
