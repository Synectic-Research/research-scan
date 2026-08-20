Purpose: build

# Brief — enrolment defaults for a consumer savings product

<!-- This file doubles as the brief template. Keep the Purpose line and the five section headings:
     the planning agent maps each one onto a specific part of queries.json (see
     references/plan-rubric.md). Purpose is one of build | research | orient and decides which
     sub-criteria get derived and what counts as impact; omit it and the agent infers one. The
     premise feeds the contradictory query, exclusions feed must_not, known papers feed anchors,
     and what you need to decide or answer shapes the sub-criteria.

     A `research` brief written from this same template is in brief.research-example.md. -->

## What this is about

A round-up savings feature inside an existing consumer banking app. Every card purchase is rounded
up to the nearest euro and the difference is swept into a separate savings pot. The setting:
adults choosing for themselves in a mobile app, sums that are small and liquid (unlike locked
pensions), and an EU consumer-protection context in which anything framed as a dark pattern is a
reputational risk. Employer retirement research is the closest large literature and is relevant by
analogy, but the "employer as trusted intermediary" mechanism does not carry over, so evidence that
speaks to that difference is worth more than another pension study. Recent work matters more than
classic work here: the app context, the liquidity, and the regulatory climate all changed after the
foundational pension studies.

## What we need to decide or answer

1. **Entry.** Opt-in (users find and enable the feature), opt-out (everyone is enrolled at sign-up
   with a clear exit), or "active choice" (users cannot finish onboarding without answering yes or
   no). Legal has cleared all three; we have not chosen.
2. **Level.** Whether we ship a pre-set round-up multiplier (1×, 2×, 5×) with one pre-selected, and
   which one, versus an empty field the user fills in.

What a useful answer looks like: five to ten papers that would actually change one of these two
decisions — how large the default effect is on enrolment and whether it persists at 6–12 months;
whether defaults change the amount saved or only who is nominally enrolled; whether the pre-set
level anchors people who would otherwise have chosen a higher one; whether active choice gets most
of the enrolment benefit without the disengagement cost; and who is helped versus hurt.

## What we already believe (the premise)

The internal argument is that **defaults will lift enrolment, so we should default everyone in**.
The counter-argument from our own support team is that passively-enrolled users do not engage,
withdraw the money within weeks, and are more likely to complain — so the enrolment number would be
vanity. We want the strongest available evidence *against* the premise as well as for it: a scan
that only confirms what we already believe is not evidence. We should also not build something that
works on average by working well for people who did not need it and badly for people who did.

## Exclusions

- Cryptocurrency and trading apps.
- Organ-donation policy — the default effect there is real, but the decision structure is nothing
  like ours.
- Anything about employer-plan tax mechanics.

## Known papers or authors

Work we already know and want the scan built around rather than rediscovered:

- Madrian & Shea, "The Power of Suggestion: Inertia in 401(k) Participation and Savings Behavior"
  (the foundational default-effect result).
- Thaler & Benartzi, "Save More Tomorrow" (the escalation design behind the preset-level question).
- The Beshears / Choi / Laibson / Madrian group's recent work on automatic enrolment generally.
