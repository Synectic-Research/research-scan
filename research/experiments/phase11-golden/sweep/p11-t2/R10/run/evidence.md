# Evidence scan — p11-t2

Run `/Users/nabergoj/Projects/research-scan/research/experiments/phase11-golden/sweep/p11-t2/R10/run` · brief `/Users/nabergoj/Projects/research-scan/research/experiments/phase11-golden/sweep/p11-t2/R10/run/brief.md` · rendered 2026-08-26

| # | Paper | Year | Venue | Evidence | Verified |
|---|---|---|---|---|---|
| 1 | [Diagnosing Search Behavior and Failure Modes in Long-Horizon Search Agents](https://doi.org/10.48550/arxiv.2608.01913) · 10.48550/arxiv.2608.01913 | 2026 | arXiv | experimental | yes |
| 2 | [BrowseComp-Plus: A More Fair and Transparent Evaluation Benchmark of Deep-Research Agent](https://doi.org/10.48550/arxiv.2508.06600) · 10.48550/arxiv.2508.06600 | 2025 | arXiv (Cornell University) | computational | yes |
| 3 | [Projecting BrowseComp-Plus onto ClimbMix: Toward More Realistic Corpora for Agentic Search](https://arxiv.org/abs/2608.20317) | 2026 | — | computational | yes |
| 4 | [When Deep Research Agents Stagnate: Enhancing Reasoning with Retrieval-Aware Agent Control](https://doi.org/10.48550/arxiv.2608.15191) · 10.48550/arxiv.2608.15191 | 2026 | arXiv | experimental | yes |
| 5 | [Deep Research Agents: A Systematic Examination And Roadmap](https://doi.org/10.48550/arxiv.2506.18096) · 10.48550/arxiv.2506.18096 | 2025 | arXiv.org | other | yes |
| 6 | [HySemRAG: A Hybrid Semantic Retrieval-Augmented Generation Framework for Automated Literature Synthesis and Methodological Gap Analysis](https://doi.org/10.48550/arxiv.2508.05666) · 10.48550/arxiv.2508.05666 | 2025 | arXiv.org | experimental | yes |
| 7 | [DeepResearch Bench: A Comprehensive Benchmark for Deep Research Agents](https://doi.org/10.48550/arxiv.2506.11763) · 10.48550/arxiv.2506.11763 | 2025 | arXiv (Cornell University) | computational | yes |
| 8 | [From Inertia to Objectivity: Improving Deep Research Agents with Noise Isolation](https://doi.org/10.48550/arxiv.2608.23045) · 10.48550/arxiv.2608.23045 | 2026 | arXiv | experimental | yes |
| 9 | [EviReform: Evidence-Guided Query Reformulation for Multi-Hop Graph Retrieval](https://doi.org/10.48550/arxiv.2608.13006) · 10.48550/arxiv.2608.13006 | 2026 | arXiv | experimental | yes |
| 10 | [ResearchRubrics: A Benchmark of Prompts and Rubrics For Evaluating Deep Research Agents](https://doi.org/10.48550/arxiv.2511.07685) · 10.48550/arxiv.2511.07685 | 2025 | arXiv (Cornell University) | computational | yes |

## 1. Diagnosing Search Behavior and Failure Modes in Long-Horizon Search Agents

Qi Liu, Jiaxin Mao, Fengbin Zhu, Tat-Seng Chua · 2026 · arXiv · experimental · overall 3/3

<https://doi.org/10.48550/arxiv.2608.01913>

**Key finding.** Across six long-horizon search agents on BrowseComp-Plus (validated on BrowseComp), search effort and answer accuracy are only weakly aligned; accuracy correlates more with cumulative retrieval recall than with number of searches, and top agents issue far fewer redundant reformulated queries.

**Why it made the cut.** contradicting · selected by score · strongest on C1 baseline recall ceiling (3/3). Directly answers which agentic moves carry the gain and where the effort-equals-gain assumption breaks down, the scan's second and fourth decisions.

**Why it matters here.** Directly tests the premise that more agentic search effort drives reported gains, and shows this is often false — implying reported improvements should be measured against cumulative retrieval recall rather than iteration count, with stopping criteria as the real lever.

**Method.** Trajectory-level diagnosis using human-annotated document-level relevance judgments, holding retrieval model and evaluation harness fixed; decomposes failures into retrieval gaps vs. utilization gaps.

**Limitations.**

- Uses BrowseComp-Plus/BrowseComp web-search corpora rather than scientific-paper corpora
- Retrieval model and harness held fixed across agents, so findings may not generalize to other retrievers

<sub>selected: score · criteria: C1 3/3 · C2 3/3 · C3 2/3 · C4 3/3 · C5 3/3 · flags: contradicts · verified 2026-08-26 via openalex, arxiv</sub>

## 2. BrowseComp-Plus: A More Fair and Transparent Evaluation Benchmark of Deep-Research Agent

Zijian Chen, Xueguang Ma, Shengyao Zhuang, Ping Nie et al. · 2025 · arXiv (Cornell University) · computational · overall 3/3

<https://doi.org/10.48550/arxiv.2508.06600>

**Key finding.** On a fixed, human-verified corpus, Search-R1 with BM25 achieves only 3.86% accuracy while GPT-5 achieves 55.9%, and pairing GPT-5 with the Qwen3-Embedding-8B retriever raises accuracy to 70.1% with fewer search calls.

**Why it made the cut.** foundational · selected by score · strongest on C1 baseline recall ceiling (3/3). Addresses the baseline recall ceiling and benchmark construction decisions and is the foundational benchmark other shortlisted papers build on or contest.

**Why it matters here.** Establishes a controlled recall/accuracy baseline separating retriever quality from agent reasoning — exactly the anchor needed before attributing any gain to the agent rather than the retriever — and is the corpus several other shortlisted papers build on or challenge.

**Method.** Constructs a fixed ~100K-document corpus derived from BrowseComp queries' supporting documents plus mined hard negatives, enabling disentangled evaluation of retriever quality vs. agent reasoning.

**Limitations.**

- Corpus assembled per-query from the benchmark's own supporting documents and negatives, later critiqued as potentially inflating scores
- Web-search domain rather than scientific-literature corpus

<sub>selected: score · criteria: C1 3/3 · C2 1/3 · C3 3/3 · C4 3/3 · C5 1/3 · flags: methods_paper · verified 2026-08-26 via openalex, arxiv</sub>

## 3. Projecting BrowseComp-Plus onto ClimbMix: Toward More Realistic Corpora for Agentic Search

Sahel Sharifymoghaddam, Lin Gu, Yijun Ge, Jimmy Lin · 2026 · no venue · computational · overall 3/3

<https://arxiv.org/abs/2608.20317>

**Key finding.** Relocating BrowseComp-Plus's evidence into a 400B-token, 553M-document corpus not built around the benchmark's own queries causes the strongest agent's evidence recall to collapse from 84.3% to 21.4% and search calls to rise 63%, while answer accuracy drops only five points.

**Why it made the cut.** contradicting · selected by score · strongest on C4 benchmark construction (3/3). A concrete demonstration of a reported agentic capability shrinking dramatically under a differently-constructed, non-curated corpus, directly answering where gains fail to hold up.

**Why it matters here.** The sharpest available evidence that a benchmark's per-query-curated corpus can overstate an agent's retrieval capability: the same agent's evidence recall falls by 63 points once distractors and evidence are no longer selected relative to the query set — exactly the non-replication the brief asks us to weight most heavily.

**Method.** A projection pipeline decomposes each question into atomic reasoning hops, grounds each hop in the new ClimbMix corpus, and retains only questions verified by automatic checks, an independent agent, and human review, yielding 57 fully grounded questions from the original 830.

**Limitations.**

- Verification pipeline retains only 57 of 830 questions (about 7%), a small and possibly non-representative subset
- New paper with no external replication of the projection method yet

<sub>selected: score · criteria: C1 2/3 · C2 1/3 · C3 2/3 · C4 3/3 · C5 3/3 · flags: contradicts, methods_paper · verified 2026-08-26 via arxiv, s2</sub>

## 4. When Deep Research Agents Stagnate: Enhancing Reasoning with Retrieval-Aware Agent Control

Heydar Soudani, Elizabeth Lingg, Faegheh Hasibi, Navid Rekabsaz · 2026 · arXiv · experimental · overall 3/3

<https://doi.org/10.48550/arxiv.2608.15191>

**Key finding.** Analysis of reasoning trajectories shows most iterations of Deep Research agents contribute little or no improvement to final performance ('reasoning stagnation'); adding the proposed Retrieval-Aware Agent Controller reduces search calls by an average of 14 and improves accuracy by up to 10% (3% on average) on BrowseComp-Plus.

**Why it made the cut.** contradicting · selected by score · strongest on C2 agentic mechanism gain (3/3). Shows precisely where the iterative-crawling component of the agentic-gain premise fails, and what specific signal recovers a modest, measured gain.

**Why it matters here.** Direct evidence that iterative crawling — one of the specific agentic moves the brief asks us to isolate — frequently does not carry gain by itself; a targeted novelty/coverage signal, not raw iteration count, is what recovers the accuracy improvement, refining which mechanism actually drives gains.

**Method.** Trajectory analysis across a large set of Deep Research agents on BrowseComp-Plus, followed by an unsupervised controller (RAAC) using search-novelty and information-coverage signals to select actions and stopping points.

**Limitations.**

- Evaluated only on BrowseComp-Plus (web search), not scientific-literature corpora
- Abstract gives only deltas, not an absolute accuracy baseline

<sub>selected: score · criteria: C1 1/3 · C2 3/3 · C3 2/3 · C4 1/3 · C5 3/3 · flags: contradicts, methods_paper · verified 2026-08-26 via arxiv</sub>

## 5. Deep Research Agents: A Systematic Examination And Roadmap

Yuxuan Huang, Yihang Chen, Haozhen Zhang, Kang Li et al. · 2025 · arXiv.org · other · overall 3/3

<https://doi.org/10.48550/arxiv.2506.18096>

**Key finding.** Surveys Deep Research agent architectures (API- vs. browser-based retrieval, static vs. dynamic workflows, single- vs. multi-agent composition) and critiques current benchmarks for restricted external-knowledge access, sequential execution inefficiency, and metric-objective misalignment.

**Why it made the cut.** closely-related · selected by score · strongest on C4 benchmark construction (3/3). Provides the field-wide map of system designs and named benchmark limitations needed to interpret the rest of the shortlist.

**Why it matters here.** Provides the orienting taxonomy for classifying which agentic moves (retrieval strategy, planning strategy, agent composition) exist, and names exactly the benchmark weaknesses (misaligned metrics, restricted knowledge access) the scan should watch for when picking evaluation sets.

**Method.** Narrative systematic examination and taxonomy building rather than a controlled experiment; abstract-only for underlying methodological depth.

**Limitations.**

- Narrative review, not a documented systematic-review protocol
- No new empirical measurement of gains or baselines

<sub>selected: score · criteria: C1 1/3 · C2 1/3 · C3 2/3 · C4 3/3 · C5 1/3 · flags: review · verified 2026-08-26 via arxiv</sub>

## 6. HySemRAG: A Hybrid Semantic Retrieval-Augmented Generation Framework for Automated Literature Synthesis and Methodological Gap Analysis

Alejandro Godinez · 2025 · arXiv.org · experimental · overall 3/3

<https://doi.org/10.48550/arxiv.2508.05666>

**Key finding.** HySemRAG's structured field extraction achieves 35.1% higher semantic similarity (0.655 vs 0.485, p<0.000001) than PDF-chunking RAG, with 68.3% single-pass QA success and 99.0% citation accuracy, applied to literature synthesis and gap analysis in geospatial epidemiology.

**Why it made the cut.** design-changing · selected by score · strongest on C3 retrieval/reranking method (3/3). Directly matches the brief's system-design question: an agentic hybrid-retrieval plus citation-graph pipeline for automated literature synthesis, with measured quality and citation-accuracy numbers.

**Why it matters here.** This is close to the exact system design the brief asks about — search combined with citation-graph traversal plus agentic self-correction for literature synthesis — giving a concrete comparison point for which retrieval design choice drives quality.

**Method.** Eight-stage pipeline combining hybrid retrieval (semantic search + keyword filtering + knowledge-graph traversal), agentic self-correction, and post-hoc citation verification; evaluated over 643 observations from 60 testing sessions.

**Limitations.**

- Single-author preprint with low citation count (4), limited independent validation
- Evaluated in one applied domain (ozone/cardiovascular epidemiology), generalization unverified
- No comparison to single-query baseline recall ceiling

<sub>selected: score · criteria: C1 0/3 · C2 2/3 · C3 3/3 · C4 1/3 · C5 0/3 · flags: methods_paper · verified 2026-08-26 via openalex, arxiv</sub>

## 7. DeepResearch Bench: A Comprehensive Benchmark for Deep Research Agents

Mingxuan Du, Benfeng Xu, Chiwei Zhu, Xiaorui Wang et al. · 2025 · arXiv (Cornell University) · computational · overall 3/3

<https://doi.org/10.48550/arxiv.2506.11763>

**Key finding.** Introduces DeepResearch Bench: 100 PhD-level research tasks across 22 fields with expert-crafted references, plus a reference-based adaptive-criteria grading method and a citation-accuracy/effective-citation-count framework for assessing retrieval quality.

**Why it made the cut.** plan-influencing · selected by score · strongest on C4 benchmark construction (3/3). A second influential, differently-constructed benchmark bearing directly on benchmark construction and cross-benchmark comparability.

**Why it matters here.** A second major, independently-constructed benchmark bearing on how evaluation sets are built — comparing its construction choices against BrowseComp-Plus's fixed-corpus approach clarifies which construction choices let two systems' numbers actually be compared.

**Method.** Expert-constructed benchmark with two evaluation frameworks (report-quality grading, citation-based retrieval assessment) claimed to align with human judgment; abstract-only for correlation statistics.

**Limitations.**

- Construction detail on label reliability is abstract-only
- Domain-diverse PhD tasks rather than literature-search-specific queries

<sub>selected: score · criteria: C1 0/3 · C2 0/3 · C3 1/3 · C4 3/3 · C5 1/3 · flags: methods_paper · verified 2026-08-26 via openalex, arxiv</sub>

## 8. From Inertia to Objectivity: Improving Deep Research Agents with Noise Isolation

Xiangxin Zhang, Zhanwei Zhang, Zhihang Fu, Binbin Lin et al. · 2026 · arXiv · experimental · overall 2/3

<https://doi.org/10.48550/arxiv.2608.23045>

**Key finding.** Introduces the IBIS benchmark showing agents judge their own prior actions less objectively (inertia bias), and NIS-Agent's context isolation at webpage triage and final-answer validation cuts token cost 33% while matching baseline performance across GAIA, WebWalkerQA, BrowseComp, and BrowseComp-zh.

**Why it made the cut.** plan-influencing · selected by score · strongest on C2 agentic mechanism gain (3/3). Surfaces a mechanism-level bias directly relevant to judging whether reported agentic gains are genuine or an artifact of self-evaluation.

**Why it matters here.** Identifies a specific, previously unmeasured failure mode (inertia bias) that can distort an agent's self-evaluation of its own search/reformulation steps, meaning our evaluation protocol should isolate self-authored context before crediting an agentic move with a gain.

**Method.** Controlled benchmark (IBIS) isolating self-authored vs. externally-observed search context; NIS-Agent architecture evaluated across four web-agent benchmarks; also trains an 8B model for intrinsic resistance to the bias.

**Limitations.**

- Benchmarks (GAIA, WebWalkerQA, BrowseComp) are general web-QA, not scientific-literature corpora
- No comparison against a single-query database search baseline

<sub>selected: score · criteria: C1 0/3 · C2 3/3 · C3 1/3 · C4 2/3 · C5 1/3 · flags: methods_paper · verified 2026-08-26 via arxiv</sub>

## 9. EviReform: Evidence-Guided Query Reformulation for Multi-Hop Graph Retrieval

Xin Xu, Yoshua Y. Li · 2026 · arXiv · experimental · overall 2/3

<https://doi.org/10.48550/arxiv.2608.13006>

**Key finding.** EviReform, which reformulates residual queries from retrieved passages and propagates them through shared-entity graph edges, exceeds the strongest baseline by up to 5.59 Recall@5 points and 4.50 F1 points on 2WikiMultiHopQA, HotpotQA, and MuSiQue.

**Why it made the cut.** closely-related · selected by backfill · strongest on C2 agentic mechanism gain (3/3). Provides a candidate evidence-guided reformulation plus graph-retrieval method matching the named agentic mechanisms, though evaluated outside the literature-search setting.

**Why it matters here.** A concrete, quantified technique combining query reformulation with graph traversal — the two agentic mechanisms the brief asks us to isolate — though demonstrated on generic multi-hop QA graphs rather than citation graphs, so its transfer to literature search would need direct testing.

**Method.** Retrieval method separating original-question retrieval from evidence-derived residual-query retrieval, normalized and combined, then propagated across entity-sharing graph nodes; evaluated on three multi-hop QA benchmarks.

**Limitations.**

- Evaluated on generic multi-hop QA knowledge graphs, not citation graphs or literature-search corpora
- Not framed as an LLM agent system — no iterative agentic decision-making described
- No comparison to a single-query baseline recall ceiling

<sub>selected: backfill · criteria: C1 0/3 · C2 3/3 · C3 3/3 · C4 1/3 · C5 0/3 · flags: methods_paper · verified 2026-08-26 via openalex, arxiv</sub>

## 10. ResearchRubrics: A Benchmark of Prompts and Rubrics For Evaluating Deep Research Agents

M. Sharma, Zhang, Chen Bo Calvin, Chaithanya Bandi, Clinton Wang et al. · 2025 · arXiv (Cornell University) · computational · overall 2/3

<https://doi.org/10.48550/arxiv.2511.07685>

**Key finding.** ResearchRubrics, built with over 2,800 hours of human labor and 2,500+ expert-written rubrics across domain-diverse prompts, finds even leading Deep Research systems (Gemini DR, OpenAI DR) achieve under 68% average rubric compliance.

**Why it made the cut.** plan-influencing · selected by backfill · strongest on C4 benchmark construction (3/3). Directly informs benchmark construction — rubric design, labeling cost, and what fine-grained evaluation reveals about agentic system limitations.

**Why it matters here.** Gives a template and cautionary number for benchmark construction: fine-grained expert-rubric labeling reveals large real gaps that coarser exact-match benchmarks would hide, shaping how any literature-search benchmark we build should measure success.

**Method.** Human-labeled rubric construction with a three-axis complexity taxonomy (conceptual breadth, logical nesting, exploration); human and model-based evaluation protocols scored for alignment with human judgment.

**Limitations.**

- Domain-diverse general prompts, not specifically scientific-literature queries
- Rubric compliance, not retrieval recall, is the measured outcome

<sub>selected: backfill · criteria: C1 0/3 · C2 0/3 · C3 0/3 · C4 3/3 · C5 1/3 · flags: methods_paper · verified 2026-08-26 via openalex, arxiv</sub>

## Coverage

| Criterion | Papers kept | Gap round added |
|---|---|---|
| C1 baseline recall ceiling | 26 | +4 |
| C2 agentic mechanism gain | 89 | +5 |
| C3 retrieval/reranking method | 89 | +12 |
| C4 benchmark construction | 69 | +11 |
| C5 gain replication failure | 9 | +3 |
