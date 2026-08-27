# Evidence scan — p11-t1

Run `/Users/nabergoj/Projects/research-scan/research/experiments/phase14/runs/p11-t1/C0/rep1/run` · brief `/Users/nabergoj/Projects/research-scan/research/experiments/phase14/runs/p11-t1/C0/rep1/run/brief.md` · rendered 2026-08-26

> 1 of 10 papers could not be verified against a live record. They are marked below; check them by hand before citing.

| # | Paper | Year | Venue | Evidence | Verified |
|---|---|---|---|---|---|
| 1 | [The Semblance of Success in Nudging Consumers to Pay Down Credit Card Debt](https://doi.org/10.3386/w31926) · 10.3386/w31926 | 2023 | National Bureau of Economic Research | rct | yes |
| 2 | [Dark defaults: How choice architecture steers political campaign donations](https://doi.org/10.1073/pnas.2218385120) · 10.1073/pnas.2218385120 | 2023 | Proceedings of the National Academy of Sciences | observational | yes |
| 3 | [Framing the Default Option Right](https://doi.org/10.1002/bdm.2395) · 10.1002/bdm.2395 | 2024 | Journal of Behavioral Decision Making | experimental | yes |
| 4 | [The Effect of Choice Screens on Mobile Browser Usage: Evidence from the EU Digital Markets Act](https://doi.org/10.3386/w35112) · 10.3386/w35112 | 2026 | Social Science Research Network | observational | [UNVERIFIED — check manually] |
| 5 | [Sending Out an SMS: Automatic Enrollment Experiments for Overdraft Alerts](https://doi.org/10.1111/jofi.13404) · 10.1111/jofi.13404 | 2024 | The Journal of Finance | rct | yes |
| 6 | [Defaults and Decisions: Choice Architecture and Consumer Opt-Out](https://doi.org/10.1287/mnsc.2024.05272) · 10.1287/mnsc.2024.05272 | 2026 | Management Sciences | observational | yes |
| 7 | [How default choice architecture impacts downstream behavior: A taxonomy, theoretical framework, and research agenda](https://doi.org/10.1002/arcp.70007) · 10.1002/arcp.70007 | 2025 | Consumer Psychology Review | other | yes |
| 8 | [Regulating Dark Patterns](https://doi.org/10.48550/arxiv.2310.00340) · 10.48550/arxiv.2310.00340 | 2023 | Aston Publications Explorer (Aston University) | other | yes |
| 9 | [Behavioral Household Finance](https://doi.org/10.3386/w24854) · 10.3386/w24854 | 2018 | National Bureau of Economic Research | other | yes |
| 10 | [Side Effects of Nudging: Evidence from a Randomized Intervention in the Credit Card Market](https://doi.org/10.1093/rfs/hhaa108) · 10.1093/rfs/hhaa108 | 2020 | Review of Financial Studies | rct | yes |

## 1. The Semblance of Success in Nudging Consumers to Pay Down Credit Card Debt

Benedict Guttman‐Kenney, Paul Adams, Stefan Hunt, David Laibson et al. · 2023 · National Bureau of Economic Research · rct · overall 3/3

<https://doi.org/10.3386/w31926>

**Key finding.** A field experiment shrouding the autopay-minimum option cut minimum-only payers by 23% after six months, but did not significantly reduce credit card debt, and actually increased missed payments among some nudged cardholders.

**Why it made the cut.** contradicting · selected by score · strongest on C2 persistence and depth (3/3). Consumer fintech field experiment showing a default-like nudge changes nominal behavior but not the underlying financial outcome, with real harms to liquidity-constrained users.

**Why it matters here.** Directly tests the core worry in the brief: a nudge can shift nominal enrollment/behavior without changing the underlying financial outcome, and can even create new harms (missed payments) for liquidity-constrained users — exactly the disengagement/complaint risk our support team flagged.

**Method.** Field experiment on credit card autopay enrollment with 6-month follow-up; liquidity-constraint analysis explains heterogeneous response.

**Limitations.**

- credit card minimum payments differ structurally from round-up savings
- effect measured on payment behavior, not a save/enrollment default per se

<sub>selected: score · criteria: C1 2/3 · C2 3/3 · C3 2/3 · C4 3/3 · C5 2/3 · C6 0/3 · flags: contradicts · verified 2026-08-26 via crossref, openalex</sub>

## 2. Dark defaults: How choice architecture steers political campaign donations

Nathaniel A. Posner, A. M. Simonov, Kellen Mrkva, Eric J. Johnson · 2023 · Proceedings of the National Academy of Sciences · observational · overall 3/3

<https://doi.org/10.1073/pnas.2218385120>

**Key finding.** Pre-checked recurring-donation defaults raised campaign donations by over $43 million but also increased requested refunds by almost $3 million, with the largest effects on small, inexperienced donors who had not intended to commit to recurring payments.

**Why it made the cut.** design-changing · selected by score · strongest on C1 default effect size (3/3). Provides a close consumer-facing analogue — a prechecked recurring financial commitment — with distributional evidence on who is harmed by the default, directly speaking to the brief's manipulation-risk question.

**Why it matters here.** The closest real-world precedent for a recurring-money default in a consumer, self-directed setting: it shows defaults can lift nominal sign-up while generating regret (refunds) concentrated among the least experienced users — exactly the disengagement/complaint risk the support team is warning about for round-ups.

**Method.** Staggered difference-in-differences design exploiting the different timing of prechecked-box rollouts across 2020 US campaign websites.

**Limitations.**

- political donations, not a banking/savings product
- US setting, not EU consumer-protection regime
- refunds are a proxy for regret, not a direct measure of withdrawal or 6-12 month persistence

<sub>selected: score · criteria: C1 3/3 · C2 2/3 · C3 1/3 · C4 2/3 · C5 3/3 · C6 0/3 · verified 2026-08-26 via crossref, openalex</sub>

## 3. Framing the Default Option Right

Luc Meunier, Yashar Bashirzadeh, Sima Ohadi · 2024 · Journal of Behavioral Decision Making · experimental · overall 3/3

<https://doi.org/10.1002/bdm.2395>

**Key finding.** Across three experiments including a 4,207-person five-country European sample, defaults produce medium-to-large effects on risk-taking, but implementing a default (especially one participants refuse) lowers trust and rating of the advisor delivering it.

**Why it made the cut.** design-changing · selected by score · strongest on C1 default effect size (3/3). EU consumer financial-advice experiments quantifying when a default is perceived as manipulative, directly bearing on reputational risk of opt-out design.

**Why it matters here.** Gives EU-context experimental evidence that a default can backfire on trust/perceived honesty when refused — precisely the dark-pattern reputational risk the brief flags, and directly informs how to frame the multiplier default so it doesn't read as manipulative.

**Method.** Three experiments, one a large representative multi-country European sample, testing default and framing manipulations on investment risk allocation.

**Limitations.**

- wealth-management advice context rather than round-up savings
- no measurement of persistence beyond the experimental session

<sub>selected: score · criteria: C1 3/3 · C2 0/3 · C3 2/3 · C4 2/3 · C5 3/3 · C6 0/3 · verified 2026-08-26 via crossref, openalex</sub>

## 4. The Effect of Choice Screens on Mobile Browser Usage: Evidence from the EU Digital Markets Act [UNVERIFIED — check manually]

Jesper Akesson, Kush Amlani, Raul Cepeda Suarez, Emily Chissell et al. · 2026 · Social Science Research Network · observational · overall 3/3

<https://doi.org/10.3386/w35112>

**Key finding.** Mandated EU active-choice browser screens produced large, persistent shifts in default-alternative usage — Firefox usage was 113% higher on iOS and 12% higher on Android relative to a no-mandate counterfactual, with effects still visible 15+ months later.

**Why it made the cut.** design-changing · selected by score · strongest on C6 active choice comparison (3/3). Closest available real-world test of active choice under EU regulation in a mobile app, giving persistence data code C6 and C2 need.

**Why it matters here.** The most direct recent evidence that a forced active-choice screen, imposed under EU digital-market regulation, produces large and durable behavior change in a mobile-app context — directly informing whether active choice can substitute for opt-out on the entry decision.

**Method.** Difference-in-differences design around the staggered EU Digital Markets Act rollout of mandatory choice screens on iOS and Android.

**Limitations.**

- browser default switching, not financial enrollment or savings amounts
- platform-level aggregate data, no individual heterogeneity or engagement/withdrawal measures

<sub>selected: score · criteria: C1 2/3 · C2 2/3 · C3 0/3 · C4 2/3 · C5 1/3 · C6 3/3 · UNVERIFIED (title)</sub>

## 5. Sending Out an SMS: Automatic Enrollment Experiments for Overdraft Alerts

Michael D. Grubb, Darragh Kelly, Jeroen Nieboer, Matthew Osborne et al. · 2024 · The Journal of Finance · rct · overall 3/3

<https://doi.org/10.1111/jofi.13404>

**Key finding.** At-scale UK bank field experiments show automatic enrollment into just-in-time overdraft text alerts reduced unarranged overdraft charges by 17-19% and arranged overdraft charges by 4-8%, worth an estimated £170-240 million market-wide, though alerts captured less than half of consumers' potential savings.

**Why it made the cut.** design-changing · selected by score · strongest on C1 default effect size (3/3). Directly on-point: UK consumer bank auto-enrollment experiment with quantified benefit and no employer-trust mechanism, matching the brief's setting closely.

**Why it matters here.** This is the closest real-world precedent to the round-up feature: a UK consumer bank auto-enrolling customers into a financial behavior nudge with measured, sizeable benefit and no employer intermediary, giving a credible upper bound for what an opt-out design could achieve in this exact setting.

**Method.** Large-scale randomized field experiments run by major UK retail banks on automatic enrollment into SMS alerts.

**Limitations.**

- measures charge reduction, not savings-pot balances or long-run engagement/withdrawal behavior
- alerts are a passive notification, not a recurring money-movement commitment like round-ups

<sub>selected: score · criteria: C1 3/3 · C2 1/3 · C3 0/3 · C4 3/3 · C5 2/3 · C6 0/3 · verified 2026-08-26 via crossref, openalex</sub>

## 6. Defaults and Decisions: Choice Architecture and Consumer Opt-Out

K. Donkor · 2026 · Management Sciences · observational · overall 3/3

<https://doi.org/10.1287/mnsc.2024.05272>

**Key finding.** A structural model on 8.6 million taxi tipping decisions finds 84% of default adherence comes from the interaction of deviation cost and opt-out cost, and shows adding a lower preset option (15%) to an existing 20/25/30% menu captures 69% of achievable consumer welfare gain at 5.4% revenue cost.

**Why it made the cut.** closely-related · selected by score · strongest on C3 anchoring on preset levels (3/3). Consumer preset-menu decision study structurally identical in form to the multiplier-menu design question, quantifying anchoring and welfare trade-offs.

**Why it matters here.** The clearest available evidence on how a preset menu of options (directly analogous to a 1x/2x/5x multiplier menu) anchors choices and how adding/adjusting menu items trades off welfare against revenue — a direct methodological template for the level decision.

**Method.** Structural econometric model estimated on 8.6 million NYC taxi transactions, validated against a stated-preference survey; counterfactual menu-design simulation.

**Limitations.**

- tipping decisions rather than savings
- single transaction choice, not a persistent enrollment decision

<sub>selected: score · criteria: C1 2/3 · C2 0/3 · C3 3/3 · C4 2/3 · C5 2/3 · C6 0/3 · flags: methods_paper · verified 2026-08-26 via crossref, openalex</sub>

## 7. How default choice architecture impacts downstream behavior: A taxonomy, theoretical framework, and research agenda

R. Waisman, Tim Derksen, Gerald Häubl · 2025 · Consumer Psychology Review · other · overall 3/3

<https://doi.org/10.1002/arcp.70007>

**Key finding.** Proposes a taxonomy and framework for when default effects persist, decay, or reverse downstream, identifying time course of choice/consumption, antecedent preferences, and trade-off salience as key moderators.

**Why it made the cut.** plan-influencing · selected by score · strongest on C2 persistence and depth (3/3). General consumer-behavior review directly addressing whether and when defaults produce lasting versus decaying downstream effects.

**Why it matters here.** Gives a general, non-employer-specific framework for exactly the question the brief asks — will enrolment persist or decay — and names the moderators (antecedent preference, salience of trade-offs) we should measure once we launch.

**Method.** Conceptual review and framework synthesis across the consumer-behavior default literature; abstract-only.

**Limitations.**

- theoretical/synthesis paper, not new empirical data
- not specific to financial products

<sub>selected: score · criteria: C1 1/3 · C2 3/3 · C3 1/3 · C4 2/3 · C5 2/3 · C6 0/3 · flags: review, methods_paper · verified 2026-08-26 via crossref, openalex</sub>

## 8. Regulating Dark Patterns

Martin Brenncke · 2023 · Aston Publications Explorer (Aston University) · other · overall 3/3

<https://doi.org/10.48550/arxiv.2310.00340>

**Key finding.** Develops a six-category taxonomy of autonomy violations used by EU law to distinguish acceptable choice-architecture influence (including pre-selected defaults) from regulable dark patterns.

**Why it made the cut.** plan-influencing · selected by score · strongest on C5 distributional and manipulation risk (3/3). Directly addresses the brief's named concern that an opt-out default could read as manipulative under EU consumer law.

**Why it matters here.** Gives the specific EU legal test for when an opt-out or pre-set multiplier crosses from 'helpful default' into 'dark pattern,' directly shaping how the entry and level decisions should be worded and disclosed to stay outside reputational/legal risk.

**Method.** Legal/normative analysis mapping EU dark-pattern law; abstract-only for empirical content.

**Limitations.**

- normative/legal analysis, not an empirical measurement of enrollment or saving effects
- not specific to financial products

<sub>selected: score · criteria: C1 0/3 · C2 0/3 · C3 0/3 · C4 2/3 · C5 3/3 · C6 1/3 · flags: review · verified 2026-08-26 via openalex</sub>

## 9. Behavioral Household Finance

John Beshears, James J. Choi, David Laibson, Brigitte C. Madrian · 2018 · National Bureau of Economic Research · other · overall 3/3

<https://doi.org/10.3386/w24854>

**Key finding.** This review synthesizes household-finance evidence on consumption/savings, borrowing, payments, and asset allocation, and surveys interventions — education, peer effects, product design, disclosure, and choice architecture — that shape household financial behavior.

**Why it made the cut.** closely-related · selected by foundational · strongest on C1 default effect size (2/3). The review/synthesis needed to check the shortlist against the wider behavioral household finance evidence base.

**Why it matters here.** Serves as the broad synthesis anchor for the choice-architecture question, situating default and product-design effects within the wider consumer (not employer-plan) household finance literature the brief asks us to draw on.

**Method.** Narrative review/book chapter synthesizing the behavioral household finance literature; not a systematic-review protocol.

**Limitations.**

- Broad narrative overview rather than a quantitative meta-analysis with effect sizes
- Covers many financial domains, not round-up savings specifically
- Some included studies still draw heavily on employer-retirement literature

<sub>selected: foundational · criteria: C1 2/3 · C2 1/3 · C3 1/3 · C4 2/3 · C5 1/3 · C6 1/3 · flags: review · verified 2026-08-26 via crossref, openalex</sub>

## 10. Side Effects of Nudging: Evidence from a Randomized Intervention in the Credit Card Market

Paolina C. Medina · 2020 · Review of Financial Studies · rct · overall 3/3

<https://doi.org/10.1093/rfs/hhaa108>

**Key finding.** Payment reminders cut credit-card late fees by 14% but raised overdraft fees by 9%, with the unintended harm concentrated in users with an overdraft history, who saw a net 5% increase in total fees while everyone else saved 15%.

**Why it made the cut.** plan-influencing · selected by foundational · strongest on C4 consumer self-directed setting (3/3). Provides concrete evidence of heterogeneous, sometimes harmful, effects of a nudge in a self-directed consumer financial product, directly informing the brief's distributional/manipulation-risk question (C5).

**Why it matters here.** Direct, quantified evidence that a well-intentioned nudge can help most users while actively harming a vulnerable subgroup — exactly the distributional risk the brief flags for the round-up feature; argues for segmenting rollout and monitoring by user risk profile rather than assuming a uniform default helps everyone.

**Method.** Randomized field experiment with a financial management platform in Brazil, testing payment reminder nudges on credit card and checking account behaviour.

**Limitations.**

- studies payment reminders, not enrolment defaults or preset contribution levels
- Brazilian credit card/checking account context, not EU round-up savings
- no data on persistence beyond the fee outcomes measured

<sub>selected: foundational · criteria: C1 0/3 · C2 1/3 · C3 0/3 · C4 3/3 · C5 3/3 · C6 0/3 · flags: contradicts · verified 2026-08-26 via crossref, openalex</sub>

## Coverage

| Criterion | Papers kept | Gap round added |
|---|---|---|
| C1 default effect size | 35 | +2 |
| C2 persistence and depth | 14 | +0 |
| C3 anchoring on preset levels | 9 | +1 |
| C4 consumer self-directed setting | 11 | +1 |
| C5 distributional and manipulation risk | 42 | +4 |
| C6 active choice comparison | 5 | +1 |

## Alternates

Next in order, not selected:

- [Enhanced active choice: A new method to motivate behavior change](https://doi.org/10.1016/j.jcps.2011.06.003) (2011) — overall 3/3
- [Do people like financial nudges?](https://doi.org/10.1017/jdm.2024.32) (2025) — overall 3/3
- [Automatic Enrollment with a 12% Default Contribution Rate](https://doi.org/10.3386/w31601) (2023) — overall 2/3
- [For Better or For Worse: Default Effects and 401(k) Savings Behavior](https://doi.org/10.3386/w8651) (2001) — overall 2/3
- Perspectives on the Economics of Aging (n.d.) — overall 2/3
