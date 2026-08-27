# Evidence scan — p11-t2

Run `/Users/nabergoj/Projects/research-scan/research/experiments/phase14/runs/p11-t2/C0/rep3/run` · brief `/Users/nabergoj/Projects/research-scan/research/experiments/phase14/runs/p11-t2/C0/rep3/run/brief.md` · rendered 2026-08-26

| # | Paper | Year | Venue | Evidence | Verified |
|---|---|---|---|---|---|
| 1 | [When to use Graphs in RAG: A Comprehensive Analysis for Graph Retrieval-Augmented Generation](https://doi.org/10.48550/arxiv.2506.05690) · 10.48550/arxiv.2506.05690 | 2025 | arXiv.org | experimental | yes |
| 2 | [Diagnosing Search Behavior and Failure Modes in Long-Horizon Search Agents](https://doi.org/10.48550/arxiv.2608.01913) · 10.48550/arxiv.2608.01913 | 2026 | arXiv | experimental | yes |
| 3 | [BrowseComp-Plus: A More Fair and Transparent Evaluation Benchmark of Deep-Research Agent](https://doi.org/10.48550/arxiv.2508.06600) · 10.48550/arxiv.2508.06600 | 2025 | arXiv (Cornell University) | experimental | yes |
| 4 | [Projecting BrowseComp-Plus onto ClimbMix: Toward More Realistic Corpora for Agentic Search](https://arxiv.org/abs/2608.20317) | 2026 | — | experimental | yes |
| 5 | [Towards Recursive Self-Evolving Agentic Literature Retrieval](https://doi.org/10.48550/arxiv.2605.14306) · 10.48550/arxiv.2605.14306 | 2026 | arXiv | experimental | yes |
| 6 | [Structurally-bounded Agentic Graph Exploration for Evidence-Grounded Scholarly DeepSearch](https://doi.org/10.48550/arxiv.2608.24809) · 10.48550/arxiv.2608.24809 | 2026 | arXiv | experimental | yes |
| 7 | [Patience is all you need! An agentic system for performing scientific literature review](https://doi.org/10.48550/arxiv.2504.08752) · 10.48550/arxiv.2504.08752 | 2025 | arXiv.org | experimental | yes |
| 8 | [PaSa: An LLM Agent for Comprehensive Academic Paper Search](https://doi.org/10.48550/arxiv.2501.10120) · 10.48550/arxiv.2501.10120 | 2025 | Annual Meeting of the Association for Computational Linguistics | experimental | yes |
| 9 | [OpenScholar: Synthesizing Scientific Literature with Retrieval-augmented LMs](https://doi.org/10.48550/arxiv.2411.14199) · 10.48550/arxiv.2411.14199 | 2024 | arXiv.org | experimental | yes |
| 10 | [Deep Research Agents: A Systematic Examination And Roadmap](https://doi.org/10.48550/arxiv.2506.18096) · 10.48550/arxiv.2506.18096 | 2025 | arXiv.org | other | yes |

## 1. When to use Graphs in RAG: A Comprehensive Analysis for Graph Retrieval-Augmented Generation

Zhishang Xiang, Chuan-Yu Wu, Qinggang Zhang, Shengyuan Chen et al. · 2025 · arXiv.org · experimental · overall 3/3

<https://doi.org/10.48550/arxiv.2506.05690>

**Key finding.** GraphRAG frequently underperforms vanilla RAG on many real-world tasks; GraphRAG-Bench systematically identifies the conditions under which graph-based retrieval does and does not outperform standard RAG across fact retrieval, complex reasoning, summarization, and creative generation.

**Why it made the cut.** contradicting · selected by score · strongest on C2 agentic mechanism gain (3/3). A benchmark explicitly designed to test when graph-based retrieval helps or hurts, directly feeding decision 4's search for gains that fail to replicate.

**Why it matters here.** Directly tests whether graph-traversal retrieval — the same mechanism behind citation-graph traversal in agentic literature-search systems — actually delivers the improvement it is credited with, documenting a case where the premise that graph-based mechanisms beat plain retrieval does not hold.

**Method.** New benchmark (GraphRAG-Bench) with graduated-difficulty tasks and full-pipeline evaluation (graph construction, retrieval, generation) comparing GraphRAG to vanilla RAG.

**Limitations.**

- General-domain RAG tasks, not scientific literature corpora specifically
- Does not evaluate literature-search-specific citation graphs

<sub>selected: score · criteria: C1 1/3 · C2 3/3 · C3 3/3 · C4 3/3 · C5 3/3 · flags: contradicts, methods_paper · verified 2026-08-26 via openalex, arxiv</sub>

## 2. Diagnosing Search Behavior and Failure Modes in Long-Horizon Search Agents

Qi Liu, Jiaxin Mao, Fengbin Zhu, Tat-Seng Chua · 2026 · arXiv · experimental · overall 3/3

<https://doi.org/10.48550/arxiv.2608.01913>

**Key finding.** Across six agents on BrowseComp-Plus and BrowseComp, answer accuracy tracks cumulative retrieval recall far more than the number of searches or context consumed, and the best agents issue far fewer redundant queries while useful evidence often surfaces early yet agents keep searching anyway.

**Why it made the cut.** contradicting · selected by score · strongest on C2 agentic mechanism gain (3/3). A trajectory-level diagnostic that separates what specific agentic moves (reformulation, stopping) actually contribute, directly answering brief questions 2 and 4.

**Why it matters here.** Directly tests the premise that more agentic search effort produces better answers and finds it weakly supported, redirecting where the project should look for gains — evidence quality and stopping criteria, not search volume — and gives a concrete decomposition (retrieval gap vs. utilization gap) to measure by.

**Method.** Trajectory-level diagnosis using human-annotated document relevance judgments, holding the retrieval model and evaluation harness fixed across six long-horizon search agents on BrowseComp-Plus, validated on BrowseComp with an open-web API.

**Limitations.**

- relies on human-annotated relevance judgments that may not generalize to other corpora
- only six agents studied, all on two closely related benchmarks

<sub>selected: score · criteria: C1 2/3 · C2 3/3 · C3 2/3 · C4 1/3 · C5 3/3 · flags: contradicts · verified 2026-08-26 via openalex, arxiv</sub>

## 3. BrowseComp-Plus: A More Fair and Transparent Evaluation Benchmark of Deep-Research Agent

Zijian Chen, Xueguang Ma, Shengyao Zhuang, Ping Nie et al. · 2025 · arXiv (Cornell University) · experimental · overall 3/3

<https://doi.org/10.48550/arxiv.2508.06600>

**Key finding.** On a fixed, human-verified corpus, Search-R1 with BM25 achieves only 3.86% accuracy while GPT-5 reaches 55.9%, rising to 70.1% with fewer search calls when paired with a Qwen3-Embedding-8B retriever, showing the retriever choice alone drives large swings in deep-research performance.

**Why it made the cut.** foundational · selected by score · strongest on C1 baseline recall ceiling (3/3). The controlled benchmark underlying multiple other shortlisted papers' baseline and mechanism claims, central to how agentic gains in this literature are measured.

**Why it matters here.** Establishes exactly the kind of controlled baseline the brief's decision 1 needs — quantified retrieval-method ceilings (BM25 vs. dense) independent of agent capability — and is the benchmark other shortlisted papers (diagnostic and corpus-projection studies) build directly on.

**Method.** A benchmark derived from BrowseComp with a fixed, curated document corpus, human-verified supporting documents, and mined hard negatives, enabling controlled disentanglement of retriever and agent contributions.

**Limitations.**

- corpus and negatives are mined from the benchmark's own queries, which the later ClimbMix-projection paper shows may inflate reported recall
- single benchmark domain (BrowseComp-style complex web queries), not scholarly-paper search specifically

<sub>selected: score · criteria: C1 3/3 · C2 2/3 · C3 2/3 · C4 3/3 · C5 1/3 · flags: methods_paper · verified 2026-08-26 via openalex, arxiv</sub>

## 4. Projecting BrowseComp-Plus onto ClimbMix: Toward More Realistic Corpora for Agentic Search

Sahel Sharifymoghaddam, Lin Gu, Yijun Ge, Jimmy Lin · 2026 · no venue · experimental · overall 3/3

<https://arxiv.org/abs/2608.20317>

**Key finding.** Relocating BrowseComp-Plus's evidence into an independently-built 553M-document corpus (ClimbMix) causes the strongest agent's evidence recall to fall from 84.3% to 21.4% and answer accuracy to drop five points while issuing 63% more search calls.

**Why it made the cut.** contradicting · selected by score · strongest on C4 benchmark construction (3/3). The clearest demonstration in the shortlist that a widely-used agentic-search benchmark's reported gains do not survive a change of corpus, directly answering the brief's hardest question.

**Why it matters here.** Directly demonstrates that a benchmark whose corpus was assembled per-query (BrowseComp-Plus) inflates reported retrieval performance relative to a more realistic, independently-built corpus — exactly the kind of gain-failure-under-a-different-corpus evidence the brief's decision 4 is looking for.

**Method.** A projection pipeline decomposes benchmark questions into atomic reasoning hops, re-grounds each hop in a corpus (ClimbMix) built without reference to the benchmark, and retains only questions verified by automatic checks, an independent agent, and human review; yields 57 fully re-grounded questions from 830 originals.

**Limitations.**

- only 57 of 830 original questions survive the re-grounding pipeline, a large reduction in coverage
- single projection target (ClimbMix); generality of the pipeline to other corpora is asserted but only one instance is shown

<sub>selected: score · criteria: C1 2/3 · C2 1/3 · C3 1/3 · C4 3/3 · C5 3/3 · flags: contradicts, methods_paper · verified 2026-08-26 via arxiv, s2</sub>

## 5. Towards Recursive Self-Evolving Agentic Literature Retrieval

Yuwen Du, Tian Jin, Jing Kang, Xianghe Pang et al. · 2026 · arXiv · experimental · overall 3/3

<https://doi.org/10.48550/arxiv.2605.14306>

**Key finding.** PaSaMaster achieves a 16.5x higher F1-score than Google Scholar and 37.8% higher F1-score than GPT-5.2 at about 1% of the cost across 38 disciplines (PaSaMaster-Bench), reducing source hallucination from 32.66% to zero.

**Why it made the cut.** design-changing · selected by score · strongest on C1 baseline recall ceiling (3/3). Directly compares an agentic literature-retrieval system against a single-query database baseline and attributes gains to specific mechanisms, central to the brief's first two decisions.

**Why it matters here.** Gives a concrete, quantified comparison against a single-query search baseline (Google Scholar) establishing how large the claimed agentic gain can be, directly bearing on decisions 1 and 2, though as an all-positive result it needs independent replication to test decision 4.

**Method.** Recursive self-evolving agentic retrieval combining iterative intent refinement, evidence-grounded ranking over verified papers (not generated citations), and planning-retrieval separation using frontier LLMs for intent and lightweight models for retrieval/scoring; evaluated on a new 38-discipline benchmark.

**Limitations.**

- Self-reported new benchmark (PaSaMaster-Bench) not independently validated
- No analysis of whether the reported gain holds under a different benchmark or metric

<sub>selected: score · criteria: C1 3/3 · C2 2/3 · C3 3/3 · C4 2/3 · C5 0/3 · flags: methods_paper · verified 2026-08-26 via openalex, arxiv</sub>

## 6. Structurally-bounded Agentic Graph Exploration for Evidence-Grounded Scholarly DeepSearch

Rima Hazra, Sayan Layek, Somnath Banerjee, Soumen Chakrabarti et al. · 2026 · arXiv · experimental · overall 3/3

<https://doi.org/10.48550/arxiv.2608.24809>

**Key finding.** A bounded citation-graph exploration agent (Crase) that expands seed papers along a 1.5-hop citation neighborhood and prunes unsupported edges outperforms open-ended deep research agents built on proprietary models by up to 3x recall@50 at roughly a third of the cost on LitSearch and a further benchmark.

**Why it made the cut.** design-changing · selected by score · strongest on C2 agentic mechanism gain (3/3). Directly attributes a measured recall gain to citation-graph traversal versus open-ended agentic search, the sharpest mechanism-level evidence in the set.

**Why it matters here.** Isolates citation-graph traversal as the specific mechanism carrying the gain over open-ended agentic search, with an explicit cost/recall tradeoff — exactly the kind of mechanism attribution the brief's decision 2 needs.

**Method.** Single seed search plus fixed-depth citation-graph expansion, entailment-based edge pruning, and recency-aware random-walk ranking over a 500K-paper arXiv corpus, compared against deep research agents.

**Limitations.**

- evaluated on a fixed 500K-paper arXiv corpus, not the full scholarly literature
- bounded 1.5-hop design may miss papers outside citation neighborhoods of seeds

<sub>selected: score · criteria: C1 2/3 · C2 3/3 · C3 2/3 · C4 2/3 · C5 1/3 · flags: methods_paper · verified 2026-08-26 via arxiv</sub>

## 7. Patience is all you need! An agentic system for performing scientific literature review

David W. Brett, Anniek Myatt · 2025 · arXiv.org · experimental · overall 3/3

<https://doi.org/10.48550/arxiv.2504.08752>

**Key finding.** A keyword-based (sparse) literature search-and-distillation agent performs close to state-of-the-art on biology QA benchmarks without needing dense retrieval infrastructure, and coverage of relevant documents can be increased through the agent's iterative approach.

**Why it made the cut.** design-changing · selected by score · strongest on C3 retrieval/reranking method (3/3). Directly on-topic system comparing sparse vs dense retrieval for scientific literature review, bearing on both the baseline-ceiling and mechanism-attribution questions.

**Why it matters here.** Directly challenges the assumption that dense retrieval or heavier infrastructure is needed for agentic literature search gains, suggesting the baseline sparse-search ceiling is higher than usually assumed — this reweights how much credit agentic complexity deserves.

**Method.** LLM-based agentic system evaluated against biology-domain literature QA benchmarks; sparse vs. dense retrieval compared empirically.

**Limitations.**

- evaluated only on biology-domain questions
- comparison benchmarks are pre-existing, not newly constructed with contamination controls

<sub>selected: score · criteria: C1 2/3 · C2 2/3 · C3 3/3 · C4 1/3 · C5 2/3 · flags: methods_paper · verified 2026-08-26 via openalex, arxiv</sub>

## 8. PaSa: An LLM Agent for Comprehensive Academic Paper Search

Yichen He, Guanhua Huang, Peiyuan Feng, Yuan Lin et al. · 2025 · Annual Meeting of the Association for Computational Linguistics · experimental · overall 3/3

<https://doi.org/10.48550/arxiv.2501.10120>

**Key finding.** PaSa-7B, an RL-trained autonomous paper-search agent, surpasses the best Google-based baseline by 37.78% in recall@20 and 39.90% in recall@50 on the real-world RealScholarQuery benchmark.

**Why it made the cut.** design-changing · selected by backfill · strongest on C1 baseline recall ceiling (3/3). A flagship agentic paper-search system with an explicit baseline comparison and benchmark construction, central to the brief's core question.

**Why it matters here.** Provides a concrete, numeric anchor for how large an agentic gain over single-query search-engine baselines can be, and its two-benchmark construction (synthetic training set vs. real evaluation set) is exactly the kind of contamination-control design decision question 3 asks about.

**Method.** RL-optimized LLM agent trained on a synthetic 35k-query dataset (AutoScholarQuery), evaluated against Google, Google Scholar, ChatGPT, and GPT-o1 baselines on a newly built real-world benchmark (RealScholarQuery).

**Limitations.**

- trained on synthetic queries which may not fully represent real research needs despite the separate real benchmark
- comparison baselines are general web search engines rather than academic search APIs specifically tuned for recall

<sub>selected: backfill · criteria: C1 3/3 · C2 2/3 · C3 1/3 · C4 3/3 · C5 0/3 · flags: methods_paper · verified 2026-08-26 via openalex, arxiv</sub>

## 9. OpenScholar: Synthesizing Scientific Literature with Retrieval-augmented LMs

Akari Asai, Jacqueline He, Rulin Shao, Weijia Shi et al. · 2024 · arXiv.org · experimental · overall 3/3

<https://doi.org/10.48550/arxiv.2411.14199>

**Key finding.** OpenScholar-8B, retrieving from 45 million open-access papers with a self-feedback inference loop, outperforms GPT-4o by 5% and PaperQA2 by 7% in correctness on the new ScholarQABench benchmark, while GPT-4o hallucinates citations 78-90% of the time versus OpenScholar's human-comparable citation accuracy.

**Why it made the cut.** design-changing · selected by backfill · strongest on C3 retrieval/reranking method (3/3). A core exemplar system for scientific-literature synthesis with its own purpose-built, well-documented benchmark — squarely the system class and evaluation type the brief is scanning for.

**Why it matters here.** A flagship, directly on-domain system with both a purpose-built benchmark (construction detailed) and numeric comparisons against strong baselines (GPT-4o, PaperQA2, human experts), giving concrete numbers for the baseline-ceiling and mechanism questions the brief prioritizes.

**Method.** Retrieval-augmented LM with dedicated datastore, retriever, and self-feedback loop; evaluated on ScholarQABench (2,967 expert queries, 208 long-form answers across 4 domains) with human expert preference studies.

**Limitations.**

- benchmark construction and correctness metrics are LLM/human-judged, not purely automatic recall
- does not isolate which component (datastore size, retriever, self-feedback loop) drives which share of the gain

<sub>selected: backfill · criteria: C1 1/3 · C2 2/3 · C3 3/3 · C4 3/3 · C5 0/3 · flags: methods_paper · verified 2026-08-26 via openalex, arxiv</sub>

## 10. Deep Research Agents: A Systematic Examination And Roadmap

Yuxuan Huang, Yihang Chen, Haozhen Zhang, Kang Li et al. · 2025 · arXiv.org · other · overall 3/3

<https://doi.org/10.48550/arxiv.2506.18096>

**Key finding.** A systematic taxonomy of Deep Research agents finds that current benchmarks suffer from restricted external-knowledge access, sequential execution inefficiencies, and misalignment between evaluation metrics and agents' practical objectives.

**Why it made the cut.** foundational · selected by review · strongest on C2 agentic mechanism gain (2/3). A survey/roadmap directly addressing benchmark construction limitations and taxonomizing agentic mechanisms, the synthesis the scan should ship alongside primary studies.

**Why it matters here.** Provides the field-level map and explicit critique of benchmark limitations that the brief's decision 3 needs to interpret any single system's reported numbers, and is the kind of synthesis paper other work in this scan argues with or extends.

**Method.** Narrative survey and taxonomy construction covering information-acquisition strategies, tool-use frameworks, and planning/composition architectures across the Deep Research agent literature, with critical benchmark evaluation.

**Limitations.**

- narrative rather than systematic-protocol review, so coverage and inclusion criteria are not formally specified
- no new empirical results of its own

<sub>selected: review · criteria: C1 1/3 · C2 2/3 · C3 1/3 · C4 2/3 · C5 1/3 · flags: review · verified 2026-08-26 via arxiv</sub>

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

- [LitSearch: A Retrieval Benchmark for Scientific Literature Search](https://doi.org/10.48550/arxiv.2407.18940) (2024) — overall 3/3
- [Multi-Turn Agentic Scientific Literature Search via Workflow Induction](https://doi.org/10.48550/arxiv.2607.00597) (2026) — overall 3/3
- [LLM-guided Hierarchical Search for End-to-end Reasoning Intensive Retrieval](https://arxiv.org/abs/2510.13217) (2025) — overall 3/3
- [Multi-Agent System for Scientific Literature Search and Recommendation](https://doi.org/10.1109/icssas66150.2025.11081082) (2025) — overall 3/3
- [CG-RAG: Research Question Answering by Citation Graph Retrieval-Augmented LLMs](https://doi.org/10.1145/3726302.3729920) (2025) — overall 3/3
