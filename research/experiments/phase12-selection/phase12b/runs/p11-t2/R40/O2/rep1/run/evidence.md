# Evidence scan — p11-t2

Run `/Users/nabergoj/Projects/research-scan/research/experiments/phase12-selection/phase12b/runs/p11-t2/R40/O2/rep1/run` · brief `/Users/nabergoj/Projects/research-scan/research/experiments/phase12-selection/phase12b/runs/p11-t2/R40/O2/rep1/run/brief.md` · rendered 2026-08-26

| # | Paper | Year | Venue | Evidence | Verified |
|---|---|---|---|---|---|
| 1 | [LLM-guided Hierarchical Search for End-to-end Reasoning Intensive Retrieval](https://arxiv.org/abs/2510.13217) | 2025 | — | computational | yes |
| 2 | [LitSearch: A Retrieval Benchmark for Scientific Literature Search](https://doi.org/10.48550/arxiv.2407.18940) · 10.48550/arxiv.2407.18940 | 2024 | Conference on Empirical Methods in Natural Language Processing | experimental | yes |
| 3 | [BrowseComp-Plus: A More Fair and Transparent Evaluation Benchmark of Deep-Research Agent](https://doi.org/10.48550/arxiv.2508.06600) · 10.48550/arxiv.2508.06600 | 2025 | arXiv (Cornell University) | experimental | yes |
| 4 | [Projecting BrowseComp-Plus onto ClimbMix: Toward More Realistic Corpora for Agentic Search](https://arxiv.org/abs/2608.20317) | 2026 | — | experimental | yes |
| 5 | [Towards Recursive Self-Evolving Agentic Literature Retrieval](https://doi.org/10.48550/arxiv.2605.14306) · 10.48550/arxiv.2605.14306 | 2026 | arXiv | experimental | yes |
| 6 | [BRIGHT: A Realistic and Challenging Benchmark for Reasoning-Intensive Retrieval](https://doi.org/10.48550/arxiv.2407.12883) · 10.48550/arxiv.2407.12883 | 2024 | International Conference on Learning Representations | experimental | yes |
| 7 | [AI's Capability in Assisting Scientific Research in Physics, Astrophysics, and Cosmology I: Literature Review](https://doi.org/10.48550/arxiv.2607.25672) · 10.48550/arxiv.2607.25672 | 2026 | arXiv | experimental | yes |
| 8 | [Deep Research: A Survey of Autonomous Research Agents](https://doi.org/10.48550/arxiv.2508.12752) · 10.48550/arxiv.2508.12752 | 2025 | arXiv.org | other | yes |
| 9 | [Multi-Turn Agentic Scientific Literature Search via Workflow Induction](https://doi.org/10.48550/arxiv.2607.00597) · 10.48550/arxiv.2607.00597 | 2026 | arXiv | experimental | yes |
| 10 | [PaSa: An LLM Agent for Comprehensive Academic Paper Search](https://doi.org/10.48550/arxiv.2501.10120) · 10.48550/arxiv.2501.10120 | 2025 | Annual Meeting of the Association for Computational Linguistics | experimental | yes |

## 1. LLM-guided Hierarchical Search for End-to-end Reasoning Intensive Retrieval

Nilesh Gupta, Wei-Cheng Chang, N. Bui, Cho-Jui Hsieh et al. · 2025 · no venue · computational · overall 3/3

<https://arxiv.org/abs/2510.13217>

**Key finding.** LATTICE removes embeddings from search-time retrieval entirely, matching the best fine-tuned ensemble on BRIGHT (46.7 nDCG@10, 49.1 with a cheap-retrieval ensemble) while remaining competitive on SciFact/SciDocs.

**Why it made the cut.** design-changing · selected by score · strongest on C1 baseline recall ceiling (3/3). A retrieval architecture that eliminates the embedding retriever the brief asks us to benchmark against, with an explicit budget-dependent comparison to reranking.

**Why it matters here.** Directly answers what happens when the embedding-based recall ceiling is bypassed rather than patched by query rewriting, and shows the gain is budget-dependent (reranking wins at low token budgets, LATTICE wins asymptotically) — a nuance any 'agentic beats baseline' claim needs to state.

**Method.** LLM-guided hierarchical index built top-down from multi-level document summaries, with calibrated path-aggregated traversal at query time; evaluated on BRIGHT, NQ, SciFact, SciDocs against fine-tuned and reranking baselines.

**Limitations.**

- evaluated mainly on general/reasoning IR benchmarks, only partial overlap with scholarly-literature-specific corpora
- single-LLM comparisons; generalization to other backbones only lightly tested

<sub>selected: score · criteria: C1 3/3 · C2 3/3 · C3 3/3 · C4 1/3 · C5 2/3 · flags: methods_paper · verified 2026-08-26 via arxiv, s2</sub>

## 2. LitSearch: A Retrieval Benchmark for Scientific Literature Search

Anirudh Ajith, Mengzhou Xia, Alexis Chevalier, Tanya Goyal et al. · 2024 · Conference on Empirical Methods in Natural Language Processing · experimental · overall 3/3

<https://doi.org/10.48550/arxiv.2407.18940>

**Key finding.** On 597 realistic literature-search queries, BM25 trails state-of-the-art dense retrievers by 24.8 absolute points of recall@5, LLM-based reranking adds a further 4.4% on the best dense retriever, and commercial search engines lag the best dense retriever by 32 points.

**Why it made the cut.** foundational · selected by score · strongest on C1 baseline recall ceiling (3/3). The clearest documented baseline-recall-ceiling numbers and benchmark-construction methodology among the shortlist, directly answering decisions 1 and 3.

**Why it matters here.** Gives the exact BM25-vs-dense-retriever recall gap the brief's decision 1 asks for, plus a fully documented construction method (query source, expert verification) that is the template question 3 needs for judging other benchmarks' comparability.

**Method.** Benchmark of 597 queries built from GPT-4-generated questions over inline-citation paragraphs plus author-written queries about recent papers, expert-verified; extensive benchmarking of retrievers and two LLM reranking pipelines.

**Limitations.**

- restricted to recent ML/NLP papers, not broader scientific literature
- query set skews toward citation-context-derivable questions, which may not represent all literature-search intents

<sub>selected: score · criteria: C1 3/3 · C2 2/3 · C3 2/3 · C4 3/3 · C5 1/3 · flags: methods_paper · verified 2026-08-26 via openalex, arxiv</sub>

## 3. BrowseComp-Plus: A More Fair and Transparent Evaluation Benchmark of Deep-Research Agent

Zijian Chen, Xueguang Ma, Shengyao Zhuang, Ping Nie et al. · 2025 · arXiv (Cornell University) · experimental · overall 3/3

<https://doi.org/10.48550/arxiv.2508.06600>

**Key finding.** With a fixed corpus, BM25-based Search-R1 reaches only 3.86% accuracy while GPT-5 reaches 55.9%, and pairing GPT-5 with the Qwen3-Embedding-8B retriever raises accuracy to 70.1% with fewer search calls.

**Why it made the cut.** foundational · selected by score · strongest on C1 baseline recall ceiling (3/3). Foundational fixed-corpus benchmark giving explicit single-query retriever baseline numbers (BM25 vs. embedding) that the brief's Q1 needs, and whose construction limitation is directly tested by another shortlisted paper.

**Why it matters here.** Gives concrete, controlled numbers for the retrieval baseline (BM25 vs. embedding retriever) that any claimed agentic gain in literature or deep-research search must be measured against — directly the recall-ceiling question the brief opens with — and its fixed-corpus methodology is the direct precursor the ClimbMix projection paper in this same shortlist critiques.

**Method.** Introduces a fixed, human-verified corpus with mined hard negatives derived from BrowseComp, enabling disentangled measurement of retriever versus agent contribution to deep-research performance.

**Limitations.**

- Corpus derived from the benchmark's own queries (evidence and negatives both selected per-query), a construction flaw later shown to inflate scores
- general web-search setting rather than a scientific-literature corpus

<sub>selected: score · criteria: C1 3/3 · C2 0/3 · C3 3/3 · C4 3/3 · C5 1/3 · flags: methods_paper · verified 2026-08-26 via openalex, arxiv</sub>

## 4. Projecting BrowseComp-Plus onto ClimbMix: Toward More Realistic Corpora for Agentic Search

Sahel Sharifymoghaddam, Lin Gu, Yijun Ge, Jimmy Lin · 2026 · no venue · experimental · overall 3/3

<https://arxiv.org/abs/2608.20317>

**Key finding.** Relocating BrowseComp-Plus's evidence into a 400B-token corpus not built from the benchmark's own queries drops the strongest agent's evidence recall from 84.3% to 21.4% while issuing 63% more search calls, though answer accuracy falls only five points.

**Why it made the cut.** contradicting · selected by score · strongest on C4 benchmark construction (3/3). The clearest evidence in the shortlist that reported agentic-search gains can collapse under a more realistic, non-curated corpus, directly answering the brief's Q4, with a projection methodology that explicitly transfers to auditing literature-search benchmark construction (Q3).

**Why it matters here.** Shows a benchmark's own construction (evidence and distractors both selected per-query from a small curated corpus) inflates measured retrieval performance; the same critique and projection technique applies directly to auditing any literature-search benchmark built the same way, which is exactly the failure-to-replicate evidence the brief is looking for.

**Method.** A dataset-agnostic projection pipeline decomposes questions into atomic reasoning hops and re-grounds each hop in a new corpus, retaining only questions verified by automatic checks, an independent agent, and human review; applied to 830 BrowseComp-Plus questions, yielding 57 fully grounded questions.

**Limitations.**

- Final grounded set is small (57 questions)
- corpus is general web text (ClimbMix), not a scientific-literature corpus

<sub>selected: score · criteria: C1 2/3 · C2 1/3 · C3 1/3 · C4 3/3 · C5 3/3 · flags: contradicts, methods_paper · verified 2026-08-26 via arxiv, s2</sub>

## 5. Towards Recursive Self-Evolving Agentic Literature Retrieval

Yuwen Du, Tian Jin, Jing Kang, Xianghe Pang et al. · 2026 · arXiv · experimental · overall 3/3

<https://doi.org/10.48550/arxiv.2605.14306>

**Key finding.** PaSaMaster achieves 16.5x higher F1 than Google Scholar and 37.8% higher F1 than GPT-5.2 at about 1% of the cost across 38 disciplines, reducing citation hallucination from 32.66% to zero.

**Why it made the cut.** design-changing · selected by score · strongest on C2 agentic mechanism gain (3/3). Directly measures agentic gain over a single-query database-search baseline and attributes it to named mechanisms, core to the brief's first two questions.

**Why it matters here.** Quantifies the gap between agentic literature search and a single-query baseline (Google Scholar) directly and decomposes the gain into named mechanisms (self-evolving retrieval, verified ranking, cost separation), exactly the evidence the brief's Q1/Q2 need.

**Method.** Recursive self-evolving agentic retrieval combining self-evolving intent refinement, hallucination-free ranking over verified papers, and planning/retrieval cost separation, evaluated on the newly introduced PaSaMaster-Bench across 38 disciplines.

**Limitations.**

- Benchmark (PaSaMaster-Bench) is introduced by the same team, raising independent-validation questions
- abstract reports relative F1 multipliers, not absolute recall numbers

<sub>selected: score · criteria: C1 2/3 · C2 3/3 · C3 3/3 · C4 2/3 · C5 0/3 · flags: methods_paper · verified 2026-08-26 via openalex, arxiv</sub>

## 6. BRIGHT: A Realistic and Challenging Benchmark for Reasoning-Intensive Retrieval

Hongjin Su, Howard Yen, Mengzhou Xia, Weijia Shi et al. · 2024 · International Conference on Learning Representations · experimental · overall 3/3

<https://doi.org/10.48550/arxiv.2407.12883>

**Key finding.** On BRIGHT's 1,384 reasoning-intensive real-world queries, the leading MTEB retriever (59.0 nDCG@10 elsewhere) scores only 18.3 nDCG@10, while adding explicit query reasoning improves retrieval by up to 12.2 points.

**Why it made the cut.** foundational · selected by score · strongest on C1 baseline recall ceiling (3/3). The clearest quantified illustration of the recall ceiling single-query dense retrieval hits on reasoning-intensive queries, the exact anchor the brief's Q1 needs, and a widely-cited reference point the field argues with.

**Why it matters here.** Gives a hard, quantified baseline-recall-ceiling number for embedding-based single-query retrieval on reasoning-heavy queries (18.3 vs 59.0 nDCG@10), and the explicit-reasoning query augmentation it tests is the same query-reformulation mechanism scored under C2 — directly anchoring Q1 and Q2 even outside the literature-search domain.

**Method.** New retrieval benchmark of naturally occurring, human-curated reasoning-intensive queries across economics, psychology, math and coding; evaluates state-of-the-art embedding retrievers and a reasoning-augmented variant.

**Limitations.**

- Domains are economics, psychology, math and coding, not scientific-literature search specifically
- Reasoning-augmentation gain is on retrieval quality, not shown for a full agentic literature-search pipeline

<sub>selected: score · criteria: C1 3/3 · C2 2/3 · C3 1/3 · C4 3/3 · C5 1/3 · flags: methods_paper · verified 2026-08-26 via openalex, arxiv</sub>

## 7. AI's Capability in Assisting Scientific Research in Physics, Astrophysics, and Cosmology I: Literature Review

Anamaria Hell, Kateryna Vovk, Veena Krishnaraj, Jia Liu et al. · 2026 · arXiv · experimental · overall 3/3

<https://doi.org/10.48550/arxiv.2607.25672>

**Key finding.** Across 8 controlled literature-review projects, overlap between human- and AI(LLM/deep-research)-selected references was under 6%, and mid-2025 models had incorrect metadata in 64% of real references retrieved (though a 2026 model showed zero fabrication/mismatch on one test project).

**Why it made the cut.** contradicting · selected by score · strongest on C4 benchmark construction (3/3). Directly tests the premise that agentic literature search matches expert search and finds it does not — the strongest counter-evidence in this batch to the brief's stated premise.

**Why it matters here.** Hard evidence that current AI-assisted literature search does not reproduce expert search coverage and carries substantial metadata-error risk, directly challenging the premise that agentic gains generalize to real expert-quality retrieval — this is exactly the kind of failure-to-replicate evidence the brief asks us to weight most.

**Method.** Parallel controlled study: expert researchers and LLM prompters (ChatGPT-4o, ChatGPT Deep Research, Gemini, later ChatGPT Pro 5.5) perform identical literature-review tasks across physics/astrophysics/cosmology; reference overlap and hallucination/metadata-mismatch rates measured directly.

**Limitations.**

- queries are domain-specific (physics/astrophysics/cosmology), an applied domain rather than a CS benchmark
- small sample (8 projects) and single-project test of the improved 2026 model
- systems tested are general LLM/deep-research tools, not purpose-built citation-graph or reformulation agents

<sub>selected: score · criteria: C1 2/3 · C2 1/3 · C3 0/3 · C4 3/3 · C5 3/3 · flags: contradicts · verified 2026-08-26 via openalex, arxiv</sub>

## 8. Deep Research: A Survey of Autonomous Research Agents

Wenlin Zhang, Xiaopeng Li, Yingyi Zhang, Pengyue Jia et al. · 2025 · arXiv.org · other · overall 3/3

<https://doi.org/10.48550/arxiv.2508.12752>

**Key finding.** Systematizes the deep-research agent pipeline into four stages — planning, question developing, web exploration, and report generation — categorizing representative methods, optimization techniques, and benchmarks for each.

**Why it made the cut.** plan-influencing · selected by score · strongest on C1 baseline recall ceiling (2/3). A synthesis of the exact system category (planning/retrieval/synthesis agentic pipelines) the brief investigates, useful for organizing the mechanism-by-mechanism question even though it does not itself supply new evidence on gains.

**Why it matters here.** Gives a shared taxonomy (planning/question-developing/web-exploration/report-generation) for classifying the specific agentic moves the brief is trying to isolate, useful for structuring how we sequence the scan's own investigation of mechanism-by-mechanism gains.

**Method.** Narrative systematic survey of autonomous research-agent literature, abstract-only detail on scope and coverage.

**Limitations.**

- abstract-only, narrative rather than systematic-protocol review despite covering benchmarks and optimization techniques
- covers general 'deep research' web agents, only partially overlapping with citation-graph-based scholarly search

<sub>selected: score · criteria: C1 2/3 · C2 2/3 · C3 2/3 · C4 2/3 · C5 1/3 · flags: review · verified 2026-08-26 via openalex, arxiv</sub>

## 9. Multi-Turn Agentic Scientific Literature Search via Workflow Induction

Jisen Li, Bingxuan Li, Nanyi Jiang, Xuying Ning et al. · 2026 · arXiv · experimental · overall 3/3

<https://doi.org/10.48550/arxiv.2607.00597>

**Key finding.** PaperPilot-9B raises Hit@5 from 58.0 to 77.0, MRR from 47.5 to 59.4, and nDCG@10 from 26.8 to 32.5 over the base Qwen3.5-9B toolset agent, while cutting workflow execution errors from 9.5% to 0%.

**Why it made the cut.** design-changing · selected by backfill · strongest on C2 agentic mechanism gain (3/3). In-domain agentic scientific-literature-search system with explicit operator decomposition and quantified gains over a baseline agent, squarely answering the brief's Q1-Q2.

**Why it matters here.** Decomposes an agentic scientific-literature-search system into named operators (citation expansion, reranking, filtering) and measures the gain over a toolset baseline, concrete evidence for which agentic moves carry improvement in exactly the brief's target setting.

**Method.** Frames scientific literature search as workflow induction: an executable DAG of operators (keyword search, citation expansion, filtering, scoring, reranking, evidence extraction) trained via supervised workflow imitation and preference optimization over corrupted workflows.

**Limitations.**

- Single model family (Qwen3.5-9B) tested
- abstract does not describe how the evaluation benchmark's relevance labels were constructed

<sub>selected: backfill · criteria: C1 1/3 · C2 3/3 · C3 3/3 · C4 1/3 · C5 0/3 · flags: methods_paper · verified 2026-08-26 via openalex, arxiv</sub>

## 10. PaSa: An LLM Agent for Comprehensive Academic Paper Search

Yichen He, Guanhua Huang, Peiyuan Feng, Yuan Lin et al. · 2025 · Annual Meeting of the Association for Computational Linguistics · experimental · overall 3/3

<https://doi.org/10.48550/arxiv.2501.10120>

**Key finding.** PaSa-7B beats the best Google-based baseline by 37.78% in recall@20 and 39.90% in recall@50 on RealScholarQuery, and exceeds a prompted-GPT-4o version of itself by 30.36% recall and 4.25% precision.

**Why it made the cut.** foundational · selected by backfill · strongest on C1 baseline recall ceiling (3/3). A foundational agentic paper-search system with explicit baseline-recall numbers and two purpose-built benchmarks, central to how later work in this space is evaluated.

**Why it matters here.** Gives concrete baseline-ceiling numbers (Google/Google Scholar recall) that any later agentic system's improvement should be measured against, and its two purpose-built benchmarks are widely referenced as the construction template question 3 asks about.

**Method.** RL-trained LLM agent that invokes search tools, reads papers, and selects references; trained on synthetic AutoScholarQuery (35k queries) and evaluated on a new real-world RealScholarQuery benchmark against Google/Google Scholar/ChatGPT/GPT-o1 baselines.

**Limitations.**

- gain is reported for the system as a whole; the abstract does not decompose which specific agentic move (search invocation vs. reference-following) drives it
- trained on synthetic data, evaluated mainly against non-agentic or single-query baselines rather than other agentic designs

<sub>selected: backfill · criteria: C1 3/3 · C2 1/3 · C3 1/3 · C4 3/3 · C5 0/3 · flags: methods_paper · verified 2026-08-26 via openalex, arxiv</sub>

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

- [Open-Source Agentic Hybrid RAG Framework for Scientific Literature Review](https://doi.org/10.48550/arxiv.2508.05660) (2025) — overall 3/3
- [Fact, Fetch, and Reason: A Unified Evaluation of Retrieval-Augmented Generation](https://doi.org/10.48550/arxiv.2409.12941) (2024) — overall 3/3
- [Structurally-bounded Agentic Graph Exploration for Evidence-Grounded Scholarly DeepSearch](https://doi.org/10.48550/arxiv.2608.24809) (2026) — overall 3/3
- [Patience is all you need! An agentic system for performing scientific literature review](https://doi.org/10.48550/arxiv.2504.08752) (2025) — overall 3/3
- [CG-RAG: Research Question Answering by Citation Graph Retrieval-Augmented LLMs](https://doi.org/10.1145/3726302.3729920) (2025) — overall 3/3
