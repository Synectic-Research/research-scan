Purpose: research

# Brief — how reliably do LLMs extract and ground claims from scientific papers?

## What this is about

LLM systems that read a scientific paper (full text or abstract) and produce structured
claims with the evidence that supports them: claim extraction, claim–evidence linking,
citation grounding, and verification of whether a cited source actually supports a stated
claim. 2024-01 onward. Computer-science and NLP literature, plus applied work in biomedicine
where the evaluation is rigorous. Downstream use is a paper-to-decision engine that must
report each claim's trustworthiness and abstain when evidence is insufficient.

## What we need to decide or answer

1. How accurate is LLM claim extraction from full papers, measured against expert annotation,
   and how does accuracy vary with paper section, claim type and model?
2. When an LLM links a claim to supporting evidence (a passage, table or citation), how often
   is the link wrong, and what kinds of errors dominate — fabricated support, wrong direction
   (contradicting evidence read as supporting), or over-generalisation beyond the paper's
   conditions?
3. Which benchmarks exist for claim–evidence grounding, how were they constructed, and what
   can their numbers legitimately support?
4. Does making the model abstain or express calibrated uncertainty improve the trustworthiness
   of the extracted claims, or does it mostly reduce coverage?

## What we already believe (the premise)

That frontier LLMs extract claims from papers well enough to be useful, and that most errors
are in evidence linking rather than in the claims themselves. The scan should reach hardest
for work showing extraction itself failing, benchmarks whose construction inflates reported
accuracy, and results that do not replicate across models or domains.

## Exclusions

- Drug discovery and molecular property prediction.
- Patent and legal claim analysis.
- Fact-checking of news or social media.

## Known papers or authors

- The SciFact line of scientific claim verification.
- CiteME and related work on whether models cite the source that supports a claim.
