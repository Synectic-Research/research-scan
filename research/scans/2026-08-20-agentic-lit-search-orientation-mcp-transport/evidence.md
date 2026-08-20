# Evidence scan — agentic-lit-search-orientation

Run `research/scans/2026-08-20-agentic-lit-search-orientation` · brief `research/scans/2026-08-20-agentic-lit-search-orientation/brief.md` · rendered 2026-08-20

| # | Paper | Year | Venue | Evidence | Verified |
|---|---|---|---|---|---|
| 1 | ScholarQuest: A Taxonomy-Guided Benchmark for Agentic Academic Paper Search in Open Literature Environments | 2026 | arXiv (Cornell University) | computational | yes |
| 2 | On-Device Deep Research at 4B: Exposure Bounds Faithfulness, Retrieval Bounds Coverage | 2026 | — | experimental | yes |
| 3 | Rethinking Literature Search Evaluation: Deep Research Helps, and Human Citation Lists Are Not a Ground Truth | 2026 | arXiv.org | computational | yes |
| 4 | BrowseComp-Plus: A More Fair and Transparent Evaluation Benchmark of Deep-Research Agent | 2025 | arXiv (Cornell University) | computational | yes |
| 5 | Superintelligent Retrieval Agent: The Next Frontier of Agentic Retrieval | 2026 | arXiv | computational | yes |
| 6 | A Collection of Systematic Reviews in Computer Science | 2026 | arXiv | computational | yes |
| 7 | Lacuna: A Research Map for Machine Learning | 2026 | arXiv | computational | yes |
| 8 | Deep Research: A Systematic Survey | 2025 | arXiv.org | other | yes |
| 9 | Which academic search systems are suitable for systematic reviews or meta‐analyses? Evaluating retrieval qualities of Google Scholar, PubMed, and 26 other resources | 2020 | Research Synthesis Methods | experimental | yes |
| 10 | SPECTER: Document-level Representation Learning using Citation-informed Transformers | 2020 | Annual Meeting of the Association for Computational Linguistics | computational | yes |

## 1. ScholarQuest: A Taxonomy-Guided Benchmark for Agentic Academic Paper Search in Open Literature Environments

Tingyue Pan, Mingyue Cheng, Daoyu Wang, Yitong Zhou et al. · 2026 · arXiv (Cornell University) · computational · overall 3/3

<https://doi.org/10.48550/arxiv.2606.20235>

**Key finding.** Agentic methods beat single-shot retrieval baselines, but the best agent reaches only 0.314 Recall@100 and 0.355 Recall@All, leaving most relevant papers unfound.

**Why it made the cut.** contradicting · selected by score · strongest on C1 agentic system design (3/3). The clearest recent statement of the recall ceiling agentic paper search actually reaches, on a benchmark built to be reproducible.

**Why it matters here.** Shows the relative and absolute claims come apart: agentic designs do win the comparison, and still miss roughly two thirds of the target set, which is the number to carry into any claim that literature search is solved.

**Method.** Taxonomy-guided benchmark built from over 1,000 computer science topics and four query intents (method-oriented, setting-anchored, comparison-based, scope-controlled), with scalable answer construction and a shared retrieval backend, ScholarBase, for reproducible comparison. Abstract-only.

**Limitations.**

- computer science topics only
- answers constructed programmatically from a taxonomy rather than by expert annotation
- a fixed retrieval backend improves comparability but changes the task from open-web search

<sub>selected: score · criteria: C1 3/3 · C2 3/3 · C3 3/3 · C4 2/3 · C5 3/3 · flags: contradicts · verified 2026-08-20 via openalex, arxiv</sub>

## 2. On-Device Deep Research at 4B: Exposure Bounds Faithfulness, Retrieval Bounds Coverage

Vinay Kumar Chaganti · 2026 · no venue · experimental · overall 3/3

<https://arxiv.org/abs/2607.12257>

**Key finding.** Raising per-source exposure lifts cited-claim faithfulness from 0.45 to 0.58 on retrieved sources and 0.37 to 0.58 on gold sources, but trustworthy coverage stays near 0.22 at any exposure because retrieval recall is held near 0.40.

**Why it made the cut.** design-changing · selected by score · strongest on C1 agentic system design (3/3). The cleanest component-level answer to which part of an agentic pipeline carries the gain, with numbers on both sides.

**Why it matters here.** Separates two things the field reports as one score and shows they have different causes: generation-side context fixes faithfulness while retrieval alone sets coverage, so the ceiling on a research agent is a retrieval ceiling, not a reasoning one.

**Method.** Controlled 2x2 crossing of source exposure (400 versus 1500 characters) against source quality (gold versus retrieved papers) with one fixed 4B generator, scored by a primary and a second independent judge. Abstract-only.

**Limitations.**

- a single 4B model on one hardware configuration, so absolute numbers will not transfer
- judge convergence is tight under the primary judge and only approximate under the second
- small-scale study without a stated corpus size or query count in the abstract

<sub>selected: score · criteria: C1 3/3 · C2 3/3 · C3 2/3 · C4 3/3 · C5 3/3 · flags: contradicts · verified 2026-08-20 via arxiv, s2</sub>

## 3. Rethinking Literature Search Evaluation: Deep Research Helps, and Human Citation Lists Are Not a Ground Truth

Gaurav Sahu, Laurent Charlin, Christopher Pal · 2026 · arXiv.org · computational · overall 3/3

<https://doi.org/10.48550/arxiv.2605.29234>

**Key finding.** Breadth-first bibliography expansion lifts recall on a 250-paper benchmark from below 20% to above 80%, but only 51% of human citations are judged moderately relevant or higher against 86-88% for the strongest AI rerankers, and humans are 2.5x more likely than those rerankers to cite a direct collaborator.

**Why it made the cut.** contradicting · selected by score · strongest on C1 agentic system design (3/3). Directly attacks the brief's premise on two fronts: it confirms a large agentic gain while showing the evaluation target that gain is measured against is unsound.

**Why it matters here.** The one paper that supplies both halves of the orientation at once: how far citation-graph traversal moves recall above the single-query baseline, and why the human reference list everyone scores against is a biased target rather than ground truth.

**Method.** Deep Research pipeline over full query papers with breadth-first citation expansion, evaluated on RollingEval-Jun25; neutral LLM-as-a-judge relevance audit of human reference lists cross-checked against the OpenAlex co-authorship graph. Abstract-only.

**Limitations.**

- one 250-paper benchmark, so the recall figures are not necessarily transportable
- the relevance audit uses an LLM judge, whose own biases are not independently validated here
- co-authorship distance is a proxy for citation bias, not a direct measure of relevance error

<sub>selected: score · criteria: C1 3/3 · C2 3/3 · C3 3/3 · C4 2/3 · C5 3/3 · flags: contradicts · verified 2026-08-20 via openalex, arxiv</sub>

## 4. BrowseComp-Plus: A More Fair and Transparent Evaluation Benchmark of Deep-Research Agent

Zijian Chen, Xueguang Ma, Shengyao Zhuang, Ping Nie et al. · 2025 · arXiv (Cornell University) · computational · overall 3/3

<https://doi.org/10.48550/arxiv.2508.06600>

**Key finding.** On a fixed curated corpus, Search-R1 with a BM25 retriever reaches 3.86% accuracy while GPT-5 reaches 55.9%, and pairing GPT-5 with a Qwen3-Embedding-8B retriever lifts it to 70.1% with fewer search calls.

**Why it made the cut.** design-changing · selected by score · strongest on C1 agentic system design (3/3). The method transfer is explicit and named by the authors: fixing the corpus so retriever contribution can be isolated, which is the only way the brief's second decision can be answered.

**Why it matters here.** The experiment that makes attribution possible at all: swapping only the retriever moves accuracy by tens of points and cuts search calls, which is the strongest available evidence that the retriever, not the agentic scaffolding, carries most of the gain.

**Method.** BrowseComp rebuilt over a fixed corpus with human-verified supporting documents and mined hard negatives, so retriever and agent can be varied independently. Abstract-only.

**Limitations.**

- derived from a general web benchmark rather than a scholarly corpus
- a fixed corpus removes the open-web difficulty that agentic crawling exists to handle
- accuracy on short-answer questions rather than recall over a target paper set

<sub>selected: score · criteria: C1 3/3 · C2 2/3 · C3 3/3 · C4 3/3 · C5 3/3 · flags: contradicts, methods_paper · verified 2026-08-20 via openalex, arxiv</sub>

## 5. Superintelligent Retrieval Agent: The Next Frontier of Agentic Retrieval

Zeyu Yang, Qi Ma, Jason Chen, Anshumali Shrivastava · 2026 · arXiv · computational · overall 3/3

<https://doi.org/10.48550/arxiv.2605.06647>

**Key finding.** A single weighted BM25 call with validated LLM term expansion achieves the strongest average retrieval across ten BEIR benchmarks, beating dense retrievers, learned sparse retrievers and LLM search-agent baselines without relevance labels or fine-tuning, and on a 25.6-million-document Wikipedia index it outperforms multi-round Perplexity agents at every budget, reaching 9.70% Recall@1, 15.27% Recall@10 and 36.14% Recall@100.

**Why it made the cut.** contradicting · selected by score · strongest on C1 agentic system design (3/3). Explicit method transfer: the comparison is single-call retrieval against multi-round agents at matched budget, which is exactly the contrast the brief's second and fourth decisions require.

**Why it matters here.** The strongest single challenge to the brief's premise: compressing multi-round exploratory search into one corpus-aware lexical call beats the agentic loop at matched budget, which means the rounds themselves were not where the gain lived.

**Method.** Offline LLM enrichment of documents with missing search vocabulary, query-time prediction of omitted evidence vocabulary, corpus-statistics tool calls filtering low-margin terms, then one weighted BM25 call; evaluated on ten BEIR sets, downstream QA, and a new 232-query BrowseComp-derived Wikipedia benchmark. Abstract-only.

**Limitations.**

- general and encyclopedic corpora rather than scholarly literature
- requires offline index-time enrichment, a cost the agentic baselines do not pay
- absolute recall on the hard benchmark remains low, 36.14% at rank 100

<sub>selected: score · criteria: C1 3/3 · C2 3/3 · C3 2/3 · C4 3/3 · C5 3/3 · flags: contradicts, methods_paper · verified 2026-08-20 via openalex, arxiv</sub>

## 6. A Collection of Systematic Reviews in Computer Science

Pierre Achkar, Tim Gollub amd Martin Potthast · 2026 · arXiv · computational · overall 3/3

<https://doi.org/10.48550/arxiv.2604.16330>

**Key finding.** A corpus of 1,212 computer science systematic reviews with their expert-designed Boolean queries and 104,316 resolved references shows systematic differences in precision, recall and ranking across retrieval paradigms and exposes the limits of naive zero-shot LLM Boolean generation.

**Why it made the cut.** design-changing · selected by score · strongest on C2 baseline search recall (3/3). Moves the baseline-recall question out of the biomedical setting into computer science, with expert queries as the reference point.

**Why it matters here.** The only resource in the pool that puts the expert Boolean baseline, the LLM-generated query, and both retrieval paradigms on the same computer science data, which is the comparison the brief's first decision needs and the one usually run only on biomedical sets.

**Method.** Collection of reviews with original and normalized expert Boolean queries over titles and abstracts, plus baseline experiments comparing expert Boolean, zero-shot LLM Boolean, BM25 and dense retrieval under one evaluation setting. Abstract-only.

**Limitations.**

- normalized title-and-abstract Boolean queries approximate rather than reproduce the original database searches
- baseline experiments are illustrative rather than an exhaustive evaluation
- no agentic multi-round system is evaluated on the collection yet

<sub>selected: score · criteria: C1 2/3 · C2 3/3 · C3 3/3 · C4 3/3 · C5 3/3 · flags: contradicts, methods_paper · verified 2026-08-20 via openalex, arxiv</sub>

## 7. Lacuna: A Research Map for Machine Learning

Martin Weiss, Miles Q. Li, Alejandro H. Artiles, Yacine Mkhinini et al. · 2026 · arXiv · computational · overall 3/3

<https://doi.org/10.48550/arxiv.2606.26246>

**Key finding.** A persistent research map beats OpenScholar v3 on LitSearch retrieval (Recall@10 0.538 versus 0.424) and its deep research agent reaches 0.052 citation F1 and 7.82/10 report quality against GPT-Researcher's 0.039 and 5.24/10.

**Why it made the cut.** closely-related · selected by score · strongest on C1 agentic system design (3/3). A head-to-head recall comparison between two scholarly systems, plus absolute citation numbers that put the relative gains in perspective.

**Why it matters here.** Shows the third design branch alongside search-then-read and citation crawling, a precomputed structured map, and its citation F1 of 0.052 is a blunt reminder of how low the absolute numbers still are even when the relative comparison is won.

**Method.** LLM-built map of papers and scholarly metadata into summaries, concepts and proposals with links back to source records, evaluated on LitSearch, Multi-XScience-CS/ML and ScholarQA-CS-ML plus 25 ReportBench-ML survey tasks. Abstract-only.

**Limitations.**

- machine learning literature only
- compared against two named systems rather than a strong tuned retrieval baseline
- the map is precomputed, so freshness and build cost are not accounted for in the retrieval numbers

<sub>selected: score · criteria: C1 3/3 · C2 3/3 · C3 2/3 · C4 3/3 · C5 2/3 · verified 2026-08-20 via openalex, arxiv</sub>

## 8. Deep Research: A Systematic Survey

Zhengliang Shi, Yiqun Chen, Haitao Li, Weiwei Sun et al. · 2025 · arXiv.org · other · overall 3/3

<https://doi.org/10.48550/arxiv.2512.02038>

**Key finding.** Organizes deep research into four components, query planning, information acquisition, memory management and answer generation, each with sub-taxonomies, plus a three-stage roadmap distinguishing it from single-shot prompting and standard retrieval-augmented generation.

**Why it made the cut.** closely-related · selected by review · strongest on C1 agentic system design (3/3). The field synthesis the orientation needs, covering system designs, training methods and evaluation in one taxonomy.

**Why it matters here.** The map to read first: it gives a newcomer the component vocabulary the rest of this literature assumes, and its four-part decomposition is what makes questions about which move carries the gain askable at all.

**Method.** Systematic survey consolidating system designs, optimization techniques from prompting through supervised fine-tuning to agentic reinforcement learning, and evaluation criteria. Abstract-only.

**Limitations.**

- surveys the general deep research paradigm rather than scientific literature search specifically
- no independent evaluation of the systems it catalogues
- a fast-moving field the authors themselves commit to continuously updating

<sub>selected: review · criteria: C1 3/3 · C2 1/3 · C3 2/3 · C4 2/3 · C5 1/3 · flags: review · verified 2026-08-20 via openalex, arxiv</sub>

## 9. Which academic search systems are suitable for systematic reviews or meta‐analyses? Evaluating retrieval qualities of Google Scholar, PubMed, and 26 other resources

Michael Gusenbauer, Neal R Haddaway · 2020 · Research Synthesis Methods · experimental · overall 3/3

<https://doi.org/10.1002/jrsm.1378>

**Key finding.** Across 28 widely used academic search systems, precision, recall and reproducibility vary substantially, only about half can be recommended for evidence synthesis without substantial caveats, and Google Scholar is shown to be inappropriate as a principal search system.

**Why it made the cut.** foundational · selected by foundational · strongest on C2 baseline search recall (3/3). The foundational measurement of how much the choice of search system alone determines recall, cited across this literature.

**Why it matters here.** The paper the recall question starts from: it establishes that the single-query baseline is not one number but a property of the system queried, which is why later claims of agentic improvement have to name their baseline system before the comparison means anything.

**Method.** A query-based method testing how well each system lets a user express and retrieve a Boolean search, applied uniformly across 28 systems including Google Scholar, PubMed and Web of Science. Abstract-only.

**Limitations.**

- published in 2020, so several systems and their APIs have changed
- assesses search-system capability rather than end-to-end retrieval of a known target set
- evidence-synthesis framing, with Boolean expressiveness as the central criterion

<sub>selected: foundational · criteria: C1 0/3 · C2 3/3 · C3 2/3 · C4 2/3 · C5 3/3 · flags: methods_paper · verified 2026-08-20 via crossref, openalex</sub>

## 10. SPECTER: Document-level Representation Learning using Citation-informed Transformers

Arman Cohan, Sergey Feldman, Iz Beltagy, Doug Downey et al. · 2020 · Annual Meeting of the Association for Computational Linguistics · computational · overall 3/3

<https://doi.org/10.18653/v1/2020.acl-main.207>

**Key finding.** Pretraining a transformer on the citation graph as a document-relatedness signal produces scientific paper embeddings that beat competitive baselines across seven document-level tasks without task-specific fine-tuning, alongside the SciDocs benchmark.

**Why it made the cut.** foundational · selected by foundational · strongest on C3 benchmark construction (3/3). The foundational scholarly document embedding and benchmark that the retrieval layer of these systems is measured against.

**Why it matters here.** The origin of the scholarly dense retriever that current work either builds on or, as in the sparse-versus-dense comparisons in this scan, fails to beat sparse retrieval with, so its assumptions are the ones being tested.

**Method.** Citation-informed contrastive pretraining for document-level embeddings, evaluated on a new seven-task benchmark spanning citation prediction, classification and recommendation. Abstract-only.

**Limitations.**

- 2020, and later scholarly embedding models have superseded it
- citation-graph supervision encodes existing citation bias into the representation
- SciDocs tasks are proxies for retrieval rather than retrieval itself

<sub>selected: foundational · criteria: C1 0/3 · C2 1/3 · C3 3/3 · C4 3/3 · C5 1/3 · flags: methods_paper · verified 2026-08-20 via crossref, openalex</sub>

## Coverage

| Criterion | Papers kept | Gap round added |
|---|---|---|
| C1 agentic system design | 103 | +34 |
| C2 baseline search recall | 38 | +21 |
| C3 benchmark construction | 73 | +20 |
| C4 retrieval and reranking | 78 | +5 |
| C5 gains that fail | 52 | +15 |

## Alternates

Next in order, not selected:

- [Can Deep Research Agents Retrieve and Organize? Evaluating the Synthesis Gap with Expert Taxonomies](https://doi.org/10.48550/arxiv.2601.12369) (2026) — overall 3/3
- [Total Recall QA: A Verifiable Evaluation Suite for Deep Research Agents](https://doi.org/10.1145/3805712.3808629) (2026) — overall 3/3
- [Empowering open medium-sized generative language models for effective structured search in biomedical systematic reviews](https://doi.org/10.1016/j.ijmedinf.2026.106463) (2026) — overall 3/3
- [AutoResearchBench: Benchmarking AI Agents on Complex Scientific Literature Discovery](https://doi.org/10.48550/arxiv.2604.25256) (2026) — overall 3/3
- [PaSa: An LLM Agent for Comprehensive Academic Paper Search](https://doi.org/10.18653/v1/2025.acl-long.572) (2025) — overall 3/3
