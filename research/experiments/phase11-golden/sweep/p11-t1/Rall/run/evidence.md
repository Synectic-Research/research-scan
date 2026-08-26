# Evidence scan — p11-t1

Run `/Users/nabergoj/Projects/research-scan/research/experiments/phase11-golden/sweep/p11-t1/Rall/run` · brief `/Users/nabergoj/Projects/research-scan/research/experiments/phase11-golden/sweep/p11-t1/Rall/run/brief.md` · rendered 2026-08-26

| # | Paper | Year | Venue | Evidence | Verified |
|---|---|---|---|---|---|
| 1 | [The Semblance of Success in Nudging Consumers to Pay Down Credit Card Debt](https://doi.org/10.3386/w31926) · 10.3386/w31926 | 2023 | National Bureau of Economic Research | experimental | yes |
| 2 | [Dark defaults: How choice architecture steers political campaign donations](https://doi.org/10.1073/pnas.2218385120) · 10.1073/pnas.2218385120 | 2023 | Proceedings of the National Academy of Sciences | observational | yes |
| 3 | [Smaller than We Thought? The Effect of Automatic Savings Policies](https://doi.org/10.3386/w32828) · 10.3386/w32828 | 2024 | National Bureau of Economic Research | observational | yes |
| 4 | [Sending Out an SMS: Automatic Enrollment Experiments for Overdraft Alerts](https://doi.org/10.1111/jofi.13404) · 10.1111/jofi.13404 | 2024 | The Journal of Finance | experimental | yes |
| 5 | [Defaults and Decisions: Choice Architecture and Consumer Opt-Out](https://doi.org/10.1287/mnsc.2024.05272) · 10.1287/mnsc.2024.05272 | 2026 | Management Sciences | computational | yes |
| 6 | [How default choice architecture impacts downstream behavior: A taxonomy, theoretical framework, and research agenda](https://doi.org/10.1002/arcp.70007) · 10.1002/arcp.70007 | 2025 | Consumer Psychology Review | other | yes |
| 7 | [Framing the Default Option Right](https://doi.org/10.1002/bdm.2395) · 10.1002/bdm.2395 | 2024 | Journal of Behavioral Decision Making | experimental | yes |
| 8 | [Behavioral Nudges in Finance: A Review and Future Research Agenda](https://doi.org/10.1111/joes.70132) · 10.1111/joes.70132 | 2026 | Journal of economic surveys (Print) | systematic-review | yes |
| 9 | [Behavioral Household Finance](https://doi.org/10.3386/w24854) · 10.3386/w24854 | 2018 | National Bureau of Economic Research | other | yes |
| 10 | [Side Effects of Nudging: Evidence from a Randomized Intervention in the Credit Card Market](https://doi.org/10.1093/rfs/hhaa108) · 10.1093/rfs/hhaa108 | 2020 | Review of Financial Studies | rct | yes |

## 1. The Semblance of Success in Nudging Consumers to Pay Down Credit Card Debt

Benedict Guttman‐Kenney, Paul Adams, Stefan Hunt, David Laibson et al. · 2023 · National Bureau of Economic Research · experimental · overall 3/3

<https://doi.org/10.3386/w31926>

**Key finding.** A field experiment nudging cardholders off minimum-payment autopay reduced minimum-only payments by 23% after six months but did not significantly reduce credit card debt, because nudged cardholders chose autopay amounts barely above the minimum and manual payments fell.

**Why it made the cut.** contradicting · selected by score · strongest on C2 persistence and depth (3/3). Consumer fintech evidence that a default/nudge changed enrolment status without changing the amount that matters, directly bearing on the enrolment-vs-amount question.

**Why it matters here.** Shows in a genuinely consumer, self-directed financial-app setting that changing the enrolment default shifts nominal behavior without changing the underlying financial outcome — the exact 'vanity metric' risk the brief raises for round-up enrolment.

**Method.** Randomized field experiment on credit card autopay enrollment defaults, six-month follow-up on payment behavior and debt levels.

**Limitations.**

- credit card repayment behavior differs from voluntary savings accumulation
- liquidity constraints specific to indebted cardholders may not generalize to savers

<sub>selected: score · criteria: C1 2/3 · C2 3/3 · C3 1/3 · C4 3/3 · C5 2/3 · C6 0/3 · flags: contradicts · verified 2026-08-26 via crossref, openalex</sub>

## 2. Dark defaults: How choice architecture steers political campaign donations

Nathaniel A. Posner, A. M. Simonov, Kellen Mrkva, Eric J. Johnson · 2023 · Proceedings of the National Academy of Sciences · observational · overall 3/3

<https://doi.org/10.1073/pnas.2218385120>

**Key finding.** Pre-checked recurring-donation defaults raised campaign donations by over $43M but also increased refund requests by almost $3M, with the largest impact on small and default-inexperienced donors who did not compensate by changing donation amounts.

**Why it made the cut.** design-changing · selected by score · strongest on C1 default effect size (3/3). Directly transfers the mechanism of a pre-checked recurring-payment default to the round-up feature's opt-out design, with quantified uptake and harm effects.

**Why it matters here.** The closest real-world analogue to a pre-checked recurring micro-contribution default: it shows the default drives large nominal uptake but concentrates harm (regret/refunds) on smaller, less-experienced users — exactly the disengagement/complaint risk the support team is worried about for round-up enrolment.

**Method.** Staggered difference-in-differences design exploiting the different rollout timing of pre-checked recurring-donation boxes across 2020 US campaign websites.

**Limitations.**

- political donations, not a savings product
- no 6-12 month persistence measure beyond refund requests

<sub>selected: score · criteria: C1 3/3 · C2 2/3 · C3 1/3 · C4 2/3 · C5 3/3 · C6 0/3 · flags: contradicts · verified 2026-08-26 via crossref, openalex</sub>

## 3. Smaller than We Thought? The Effect of Automatic Savings Policies

James J. Choi, David Laibson, Jordan Cammarota, Richard Lombardo et al. · 2024 · National Bureau of Economic Research · observational · overall 3/3

<https://doi.org/10.3386/w32828>

**Key finding.** Accounting for job separation, withdrawal on separation, and opt-out from auto-escalation, steady-state savings increase only 0.6% of income from automatic enrollment and 0.3% from default auto-escalation, far smaller than headline estimates; only 40% of defaulted employees escalate on the first scheduled date.

**Why it made the cut.** contradicting · selected by score · strongest on C1 default effect size (3/3). Directly contradicts the premise that defaults straightforwardly translate into more saving once medium-run dynamics are modeled.

**Why it matters here.** Directly supports the support team's objection: the enrolment lift from a default is real but its dollar impact erodes once realistic attrition and disengagement are modeled, which is exactly the persistence question the brief asks about.

**Method.** Longitudinal administrative analysis of nine 401(k) plans incorporating employee turnover, vesting, and opt-out dynamics.

**Limitations.**

- 401(k) retirement plans rather than liquid consumer savings
- employer intermediary and vesting mechanics that do not carry over to a consumer app

<sub>selected: score · criteria: C1 3/3 · C2 3/3 · C3 2/3 · C4 1/3 · C5 1/3 · C6 0/3 · flags: contradicts · verified 2026-08-26 via crossref, openalex</sub>

## 4. Sending Out an SMS: Automatic Enrollment Experiments for Overdraft Alerts

Michael D. Grubb, Darragh Kelly, Jeroen Nieboer, Matthew Osborne et al. · 2024 · The Journal of Finance · experimental · overall 3/3

<https://doi.org/10.1111/jofi.13404>

**Key finding.** At-scale U.K. bank field experiments show automatic enrollment into just-in-time overdraft text alerts cuts unarranged overdraft charges by 17-19% and arranged overdraft charges by 4-8%, implying £170-240 million in annual market-wide savings, though consumers still capture less than half of the available savings.

**Why it made the cut.** design-changing · selected by score · strongest on C1 default effect size (3/3). Same institutional setting (consumer retail banking app, U.K.), same design lever (automatic enrollment vs. opt-in), with real effect sizes on realized benefit, not just enrolment counts.

**Why it matters here.** The nearest real-world precedent to our exact decision: automatic (opt-out-style) enrollment into a discretionary consumer-banking feature, run at scale inside a bank, with real behavior-change effect sizes — strong evidence that opt-out can produce durable, economically meaningful benefit rather than just nominal sign-up, while also showing the benefit captured is only partial, which should temper how much we claim from enrolment numbers alone.

**Method.** Multiple large-scale field experiments run directly inside major U.K. retail banks, with market-wide extrapolation of savings.

**Limitations.**

- overdraft alerts, not a savings/round-up feature specifically
- effect measured as charges avoided rather than savings-pot balances or long-term retention

<sub>selected: score · criteria: C1 3/3 · C2 2/3 · C3 0/3 · C4 3/3 · C5 2/3 · C6 0/3 · verified 2026-08-26 via crossref, openalex</sub>

## 5. Defaults and Decisions: Choice Architecture and Consumer Opt-Out

K. Donkor · 2026 · Management Sciences · computational · overall 3/3

<https://doi.org/10.1287/mnsc.2024.05272>

**Key finding.** A structural model of 8.6 million taxi tipping decisions finds 84% of default adherence arises from the interaction of a deviation cost and an opt-out cost together (friction complementarity), and adding a 15% tip option to the existing 20/25/30% menu captures 69% of achievable welfare gain at 5.4% revenue cost.

**Why it made the cut.** closely-related · selected by score · strongest on C3 anchoring on preset levels (3/3). Genuine consumer, self-directed setting with a structural model of preset-menu anchoring directly applicable to the multiplier design choice.

**Why it matters here.** Offers a directly transferable method for the level-design decision: it shows preset menu options anchor choices largely through friction rather than preference change, and quantifies how adding/removing a preset option shifts welfare — precisely the multiplier-menu question the brief poses.

**Method.** Structural econometric model estimated on 8.6 million consumer transactions, validated against an independent stated-preference survey of true preferences.

**Limitations.**

- tipping decisions, not savings accumulation
- single transaction context rather than repeated app engagement over months

<sub>selected: score · criteria: C1 2/3 · C2 0/3 · C3 3/3 · C4 3/3 · C5 2/3 · C6 0/3 · flags: methods_paper · verified 2026-08-26 via crossref, openalex</sub>

## 6. How default choice architecture impacts downstream behavior: A taxonomy, theoretical framework, and research agenda

R. Waisman, Tim Derksen, Gerald Häubl · 2025 · Consumer Psychology Review · other · overall 3/3

<https://doi.org/10.1002/arcp.70007>

**Key finding.** Proposes a taxonomy and framework for when default choice architecture produces lasting versus fading downstream effects on consumer behavior, identifying time course of choice/consumption, antecedent preferences, and trade-off salience as key moderators.

**Why it made the cut.** plan-influencing · selected by score · strongest on C2 persistence and depth (3/3). A recent synthesis of exactly the persistence-and-depth question the brief raises, useful for designing what to track post-launch.

**Why it matters here.** Gives the project a structured way to decide what to measure at 6-12 months (retention, amount, disengagement) rather than only enrolment, directly shaping the measurement plan for whichever entry design is chosen.

**Method.** Conceptual review and framework synthesis of the consumer behavior literature on default effects. Abstract-only.

**Limitations.**

- theoretical/taxonomic rather than an empirical estimate
- not specific to financial products, so moderators require validation in the app context

<sub>selected: score · criteria: C1 1/3 · C2 3/3 · C3 2/3 · C4 2/3 · C5 2/3 · C6 0/3 · flags: review · verified 2026-08-26 via crossref, openalex</sub>

## 7. Framing the Default Option Right

Luc Meunier, Yashar Bashirzadeh, Sima Ohadi · 2024 · Journal of Behavioral Decision Making · experimental · overall 3/3

<https://doi.org/10.1002/bdm.2395>

**Key finding.** Across three experiments including a 5-country sample (n=4207), defaults significantly shifted risk-taking with medium-to-large effect sizes, but implementing a default nudge lowered users' rating of the advisor, especially when the targeted default was refused, and framing of the default question itself had smaller but measurable anchoring effects.

**Why it made the cut.** design-changing · selected by score · strongest on C5 distributional and manipulation risk (3/3). Consumer financial-advice setting showing both the anchoring power and the reputational cost of defaults, central to the entry-design trade-off.

**Why it matters here.** Directly informs whether a pre-set multiplier reads as helpful or manipulative: it shows a default can move behavior while simultaneously damaging trust when overridden, which should weigh heavily on the entry-mechanism decision under EU dark-pattern scrutiny.

**Method.** Three behavioral experiments, including a large multi-country representative sample, manipulating default presence and framing in an investment-risk context.

**Limitations.**

- wealth-manager investment advice context rather than a savings-pot multiplier
- effect on trust/rating measured immediately, not over 6-12 months of app use

<sub>selected: score · criteria: C1 2/3 · C2 0/3 · C3 2/3 · C4 2/3 · C5 3/3 · C6 0/3 · verified 2026-08-26 via crossref, openalex</sub>

## 8. Behavioral Nudges in Finance: A Review and Future Research Agenda

Ajeet Pandey, Vibhuti Tripathi, Vaishali Pandey · 2026 · Journal of economic surveys (Print) · systematic-review · overall 3/3

<https://doi.org/10.1111/joes.70132>

**Key finding.** A systematic synthesis of 66 peer-reviewed articles identifies defaults, framing, informational cues, reminders, and social norms as the dominant nudges in financial decision-making, mapping 19 antecedents, 24 decision types, and 19 outcomes, but finds evidence concentrated in narrow institutional/geographic contexts.

**Why it made the cut.** plan-influencing · selected by score · strongest on C4 consumer self-directed setting (3/3). Provides the requested review-level synthesis of nudges in finance, directly in the financial decision-making domain the brief targets.

**Why it matters here.** This is the review/synthesis of nudges specifically in financial decision-making the brief asked for, giving a structural map of what is and isn't well studied (e.g. it flags contextual imbalance), useful for identifying where our decisions sit relative to existing evidence.

**Method.** Systematic literature review using the SPAR-4-SLR protocol across Web of Science and Scopus, organized via ADO and TCM frameworks.

**Limitations.**

- no quantitative effect sizes reported in the abstract, more a thematic/bibliometric mapping than a meta-analysis
- does not isolate consumer round-up/liquid-savings products specifically

<sub>selected: score · criteria: C1 2/3 · C2 1/3 · C3 1/3 · C4 3/3 · C5 1/3 · C6 1/3 · flags: review · verified 2026-08-26 via crossref, openalex</sub>

## 9. Behavioral Household Finance

John Beshears, James J. Choi, David Laibson, Brigitte C. Madrian · 2018 · National Bureau of Economic Research · other · overall 3/3

<https://doi.org/10.3386/w24854>

**Key finding.** A synthesis of household finance evidence covering consumption/savings, borrowing, payments, and asset allocation, alongside interventions including choice architecture and product design used by firms and governments to shape financial behavior.

**Why it made the cut.** closely-related · selected by foundational · strongest on C1 default effect size (2/3). The kind of review/meta-level synthesis the brief asks for, and it explicitly extends choice-architecture findings beyond employer retirement plans into general household finance.

**Why it matters here.** Offers a broad, consumer-finance-wide (not solely employer-plan) synthesis of when choice-architecture interventions like defaults and product design help or hurt, giving the team a framework for weighing the enrolment and level decisions against the wider behavioral evidence base.

**Method.** Narrative review/overview chapter (NBER), abstract-only detail on specific effect sizes.

**Limitations.**

- broad overview rather than a focused study of round-up savings or app-based defaults
- abstract gives no concrete effect sizes
- covers many topics beyond enrolment defaults, diluting direct applicability

<sub>selected: foundational · criteria: C1 2/3 · C2 2/3 · C3 2/3 · C4 2/3 · C5 2/3 · C6 1/3 · flags: review · verified 2026-08-26 via crossref, openalex</sub>

## 10. Side Effects of Nudging: Evidence from a Randomized Intervention in the Credit Card Market

Paolina C. Medina · 2020 · Review of Financial Studies · rct · overall 3/3

<https://doi.org/10.1093/rfs/hhaa108>

**Key finding.** A randomized nudge (payment reminders) in a Brazilian financial app reduced credit-card late fees by 14% but increased overdraft fees by 9%, with users who already overdraft experiencing a net 5% increase in total fees while everyone else saved 15%.

**Why it made the cut.** contradicting · selected by foundational · strongest on C4 consumer self-directed setting (3/3). The clearest consumer-financial-app evidence that nudges/defaults can have distributional side effects, hurting the subgroup least equipped to benefit — exactly the heterogeneity question the brief raises.

**Why it matters here.** Directly evidences the brief's stated worry — a well-intentioned default/nudge can help most users while actively harming a vulnerable subgroup — arguing against blanket opt-out enrolment without segmentation.

**Method.** Field RCT with a consumer financial management platform, administrative fee data.

**Limitations.**

- studies a reminder nudge, not an enrolment default per se
- credit/overdraft context rather than a savings round-up feature
- Brazilian market, not EU regulatory context

<sub>selected: foundational · criteria: C1 1/3 · C2 1/3 · C3 0/3 · C4 3/3 · C5 3/3 · C6 0/3 · flags: contradicts · verified 2026-08-26 via crossref, openalex</sub>

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

- [Dark patterns and consumer vulnerability](https://doi.org/10.1017/bpp.2024.49) (2025) — overall 3/3
- [Regulating Dark Patterns](https://doi.org/10.48550/arxiv.2310.00340) (2023) — overall 3/3
- [Active vs. Passive Decisions and Crowd-Out in Retirement Savings Accounts: Evidence from Denmark *](https://doi.org/10.1093/qje/qju013) (2014) — overall 2/3
- [The Behavioral Foundations of Default Effects: Theory and Evidence from Medicare Part D](https://doi.org/10.1257/aer.20210013) (2023) — overall 2/3
- [For Better or For Worse: Default Effects and 401(k) Savings Behavior](https://doi.org/10.3386/w8651) (2001) — overall 2/3
