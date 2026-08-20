# Agentic LLM systems for scientific literature search

## What we're building
An orientation on agentic LLM systems for scientific literature search, 2024–2026. Three things are in scope: the system designs (search combined with citation-graph traversal, query reformulation, iterative crawling), the benchmarks used to evaluate them, and the retrieval and reranking methods underneath. The window opens at 2024-01. This is a computer-science literature, so the evidence lives in CS venues and on preprint servers rather than in the applied domains those systems are pointed at.

## Decisions we face
1. What is the recall ceiling of single-query database search? The baseline everything else is measured against.
2. What do agentic designs add on top? Which specific moves — reformulation, graph traversal, iterative crawling — carry the gain, and how much of it.
3. How are evaluation sets constructed? A benchmark's construction decides what its numbers can support.
4. Where do reported gains fail to hold up? Which results do not survive a different set, a different metric, or a replication.

## What we already believe (the premise)
That agentic designs beat single-query database search, and that the gains reported for them are real. The scan should reach hardest for work showing reported gains failing to replicate, benchmarks whose construction inflates them, or settings where the plain baseline is not actually beaten.

## Exclusions
- Drug discovery.
- Patent search.

## Known papers or authors
None.