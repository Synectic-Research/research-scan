# Brief — enrolment defaults for a consumer savings product

## What we are building

A round-up savings feature inside an existing consumer banking app. Every card purchase is rounded
up to the nearest euro and the difference is swept into a separate savings pot. We are deciding how
users end up in the feature and how they set their contribution level.

Two design decisions are open, and both are choice-architecture decisions rather than engineering
ones:

1. **Entry.** Opt-in (users find and enable the feature), opt-out (everyone is enrolled at sign-up
   with a clear exit), or "active choice" (users cannot finish onboarding without answering yes or
   no). Legal has cleared all three; we have not chosen.
2. **Level.** Whether we ship a pre-set round-up multiplier (1×, 2×, 5×) with one pre-selected, and
   which one, versus an empty field the user fills in.

## Why we care about the research

The internal argument is that defaults will lift enrolment, so we should default everyone in. The
counter-argument from our own support team is that passively-enrolled users do not engage, withdraw
the money within weeks, and are more likely to complain — so the enrolment number would be vanity.
We want to know what the evidence actually says about that trade-off before we build, specifically:

- how large the default effect is on **enrolment**, and whether it persists at 6–12 months
- whether defaults change the **amount** saved, or only who is nominally enrolled
- whether the pre-set level anchors people who would otherwise have chosen a higher one
- whether active choice gets most of the enrolment benefit without the disengagement cost
- who is helped and who is hurt — we should not build something that works on average by working
  well for people who did not need it and badly for people who did

## Constraints that shape what is relevant

- Consumer financial product, not an employer-sponsored plan. Employer retirement research is the
  closest large literature and is relevant by analogy, but the "employer as trusted intermediary"
  mechanism does not carry over, so we need work that says something about that difference.
- Adults choosing for themselves in a mobile app; sums are small and liquid, unlike locked pensions.
- EU consumer-protection context. Anything framed as a dark pattern is a reputational risk, so
  research on when a default reads as helpful versus manipulative is directly useful.
- Recent work matters more than classic work here: the app context, the liquidity, and the
  regulatory climate all changed after the foundational pension studies.

## Not relevant

Cryptocurrency and trading apps, organ-donation policy (the default effect there is real but the
decision structure is nothing like ours), and anything about employer-plan tax mechanics.

## What a useful answer looks like

Five to ten papers that would actually change one of the two decisions above — ideally including at
least one that contradicts the "defaults always help" premise, and at least one review or
meta-analysis giving effect sizes rather than a single study's estimate.
