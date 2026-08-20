Purpose: research

# Brief — what agentic LLM systems actually add to literature search

<!-- The same five sections as brief.example.md, at Purpose: research. The difference is what
     "impact" means: nothing here is a build decision, so a paper earns its place by changing what
     we believe, what we would test, or how we would measure it. Note how that shows up in the
     sections — "What we need to decide or answer" holds questions rather than choices, and the
     sub-criteria the planner derives from it are the research set in references/plan-rubric.md
     (population/sample, exposure or method, outcome/measure, the claim under test, comparison).

     Adapted from eval/briefs/llm-lit-search.md, which drives a ratified golden topic. That file
     keeps "Known papers or authors" deliberately empty so a scored run cannot be handed its own
     answers; this one is an ordinary example and fills the section in, as a real brief should. -->

## What this is about

Agentic LLM systems for scientific literature search, 2024–2026. Three things are in scope: the
**system designs** (search combined with citation-graph traversal, query reformulation, iterative
crawling), the **benchmarks** used to evaluate them, and the **retrieval and reranking methods**
underneath.

The window opens at 2024-01. This is a computer-science literature, so the evidence lives in CS
venues and on preprint servers rather than in the applied domains those systems are pointed at.

## What we need to decide or answer

Four questions the evidence has to answer, in the order they matter:

1. **What is the recall ceiling of single-query database search?** The baseline everything else is
   measured against — without it, any reported improvement is unanchored.
2. **What do agentic designs add on top?** Which specific moves — reformulation, graph traversal,
   iterative crawling — carry the gain, and how much of it.
3. **How are evaluation sets constructed?** A benchmark's construction decides what its numbers can
   support; two systems reporting on differently-built sets are not comparable.
4. **Where do reported gains fail to hold up?** Which results do not survive a different set, a
   different metric, or a replication.

None of these is a build decision, and that is the point of `Purpose: research`. A paper earns a
slot by moving one of these four beliefs, by being the closest prior work to a claim we are making,
or by supplying a method we would have to adopt to test one — not by changing something we are
about to ship.

## What we already believe (the premise)

That agentic designs beat single-query database search, and that the gains reported for them are
real. Question four exists because we do not want that premise confirmed back to us: the scan
should reach hardest for work showing reported gains failing to replicate, benchmarks whose
construction inflates them, or settings where the plain baseline is not actually beaten.

At `Purpose: research` the `contradictory` query aims at exactly this claim, in the words the
people who dispute it would use — "reproducibility", "negative result", "does not replicate" — not
at the topic in general.

## Exclusions

- Drug discovery.
- Patent search.

## Known papers or authors

Work we already know, so the scan builds outward from it rather than rediscovering it:

- Anything from the PaSa / OpenScholar / LitSearch line of agentic search systems.
- The BEIR and BRIGHT retrieval benchmarks, as the measurement backdrop.

Anchored papers are pinned into the pool and always seeded into expansion, so naming the two or
three you already trust is usually worth more than naming ten.
