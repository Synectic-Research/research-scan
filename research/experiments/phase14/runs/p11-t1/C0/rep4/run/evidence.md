# Evidence scan — p11-t1

Run `/Users/nabergoj/Projects/research-scan/research/experiments/phase14/runs/p11-t1/C0/rep4/run` · brief `/Users/nabergoj/Projects/research-scan/research/experiments/phase14/runs/p11-t1/C0/rep4/run/brief.md` · rendered 2026-08-27

> 1 of 10 papers could not be verified against a live record. They are marked below; check them by hand before citing.

| # | Paper | Year | Venue | Evidence | Verified |
|---|---|---|---|---|---|
| 1 | [The Semblance of Success in Nudging Consumers to Pay Down Credit Card Debt](https://doi.org/10.3386/w31926) · 10.3386/w31926 | 2023 | National Bureau of Economic Research | rct | yes |
| 2 | [Smaller than We Thought? The Effect of Automatic Savings Policies](https://doi.org/10.3386/w32828) · 10.3386/w32828 | 2024 | National Bureau of Economic Research | observational | yes |
| 3 | [Dark defaults: How choice architecture steers political campaign donations](https://doi.org/10.1073/pnas.2218385120) · 10.1073/pnas.2218385120 | 2023 | Proceedings of the National Academy of Sciences | observational | yes |
| 4 | [How default choice architecture impacts downstream behavior: A taxonomy, theoretical framework, and research agenda](https://doi.org/10.1002/arcp.70007) · 10.1002/arcp.70007 | 2025 | Consumer Psychology Review | other | yes |
| 5 | [Sending Out an SMS: Automatic Enrollment Experiments for Overdraft Alerts](https://doi.org/10.1111/jofi.13404) · 10.1111/jofi.13404 | 2024 | The Journal of Finance | rct | yes |
| 6 | [Framing the Default Option Right](https://doi.org/10.1002/bdm.2395) · 10.1002/bdm.2395 | 2024 | Journal of Behavioral Decision Making | experimental | yes |
| 7 | [The Effect of Choice Screens on Mobile Browser Usage: Evidence from the EU Digital Markets Act](https://doi.org/10.3386/w35112) · 10.3386/w35112 | 2026 | Social Science Research Network | observational | [UNVERIFIED — check manually] |
| 8 | [When Nudges Backfire: The Effect of Social Norms, Framing Effects, and Default Options on the Pension Saving Decisions in China](https://doi.org/10.54254/2754-1169/2025.bl30018) · 10.54254/2754-1169/2025.bl30018 | 2025 | Advances in Economics, Management and Political Sciences | rct | yes |
| 9 | [Behavioral Household Finance](https://doi.org/10.3386/w24854) · 10.3386/w24854 | 2018 | National Bureau of Economic Research | other | yes |
| 10 | [Side Effects of Nudging: Evidence from a Randomized Intervention in the Credit Card Market](https://doi.org/10.1093/rfs/hhaa108) · 10.1093/rfs/hhaa108 | 2020 | Review of Financial Studies | rct | yes |

## 1. The Semblance of Success in Nudging Consumers to Pay Down Credit Card Debt

Benedict Guttman‐Kenney, Paul Adams, Stefan Hunt, David Laibson et al. · 2023 · National Bureau of Economic Research · rct · overall 3/3

<https://doi.org/10.3386/w31926>

**Key finding.** A field experiment shrouding the credit-card autopay-minimum default cut exact-minimum payers by 23% after six months but did not significantly reduce credit card debt.

**Why it made the cut.** contradicting · selected by score · strongest on C1 default effect size (3/3). Closest available consumer financial-product test of a default/nudge changing enrollment without changing the outcome that matters, matching the brief's amount-vs-enrollment question.

**Why it matters here.** Directly tests the brief's core question—whether changing an enrollment default shifts behavior nominally but not the underlying amount—showing behavior change without an outcome improvement, a warning for judging round-up enrollment by sign-up counts alone.

**Method.** Field experiment on credit card autopay enrollment, six-month follow-up, large cardholder sample.

**Limitations.**

- Domain is credit-card repayment, not a savings sweep, so the direction of desired behavior differs.
- Abstract does not give exact debt-reduction confidence intervals.

<sub>selected: score · criteria: C1 3/3 · C2 3/3 · C3 1/3 · C4 3/3 · C5 2/3 · C6 0/3 · flags: contradicts · verified 2026-08-27 via crossref, openalex</sub>

## 2. Smaller than We Thought? The Effect of Automatic Savings Policies

James J. Choi, David Laibson, Jordan Cammarota, Richard Lombardo et al. · 2024 · National Bureau of Economic Research · observational · overall 3/3

<https://doi.org/10.3386/w32828>

**Key finding.** Steady-state saving rates rise only 0.6% of income from automatic enrollment and 0.3% from auto-escalation once job turnover, pre-vesting withdrawals, and opt-outs are accounted for; only 40% of auto-escalation defaults are accepted at the first escalation date.

**Why it made the cut.** contradicting · selected by score · strongest on C1 default effect size (3/3). Contradicts the premise that defaults reliably raise saving amounts, which the brief explicitly asked us to test.

**Why it matters here.** The clearest quantified rebuttal of the 'defaults will lift enrollment so default everyone in' premise: medium/long-run dynamics erode most of the apparent gain, directly supporting the support team's skepticism.

**Method.** Longitudinal analysis of nine 401(k) plans incorporating job separation, balance withdrawal, and opt-out dynamics.

**Limitations.**

- 401(k) retirement plans rather than liquid consumer savings.
- Abstract gives steady-state estimates but not month-by-month withdrawal timing relevant to a round-up feature.

<sub>selected: score · criteria: C1 3/3 · C2 3/3 · C3 2/3 · C4 1/3 · C5 1/3 · C6 0/3 · flags: contradicts · verified 2026-08-27 via crossref, openalex</sub>

## 3. Dark defaults: How choice architecture steers political campaign donations

Nathaniel A. Posner, A. M. Simonov, Kellen Mrkva, Eric J. Johnson · 2023 · Proceedings of the National Academy of Sciences · observational · overall 3/3

<https://doi.org/10.1073/pnas.2218385120>

**Key finding.** Pre-checked recurring-donation defaults raised campaign donations by over $43 million but also increased requested refunds by almost $3 million, with the largest effects on smaller, less-experienced donors who apparently did not intend the recurring commitment.

**Why it made the cut.** contradicting · selected by score · strongest on C1 default effect size (3/3). Directly demonstrates the 'nominal enrolment vs genuine intent' failure mode the support team worries about, via a near-identical checkbox-default mechanism.

**Why it matters here.** The pre-checked recurring-payment mechanism is structurally identical to a default-on round-up multiplier: it shows the same default can lift the headline number while creating unintended recurring commitments and complaint-like behaviour (refund requests) concentrated among the least experienced users.

**Method.** Staggered difference-in-differences design exploiting different rollout timing of pre-checked recurring-donation boxes across U.S. political campaign websites.

**Limitations.**

- political donations, not a savings or banking product
- refund requests are a proxy for regret, not a direct measure of savings withdrawal or complaints

<sub>selected: score · criteria: C1 3/3 · C2 2/3 · C3 0/3 · C4 2/3 · C5 3/3 · C6 0/3 · flags: contradicts · verified 2026-08-27 via crossref, openalex</sub>

## 4. How default choice architecture impacts downstream behavior: A taxonomy, theoretical framework, and research agenda

R. Waisman, Tim Derksen, Gerald Häubl · 2025 · Consumer Psychology Review · other · overall 3/3

<https://doi.org/10.1002/arcp.70007>

**Key finding.** Proposes a taxonomy and framework for when default effects persist, fade, or reverse downstream, driven by the time course of choice, prior preferences, and salience of trade-offs.

**Why it made the cut.** plan-influencing · selected by score · strongest on C2 persistence and depth (3/3). Directly addresses persistence and downstream default effects in consumer decision-making, the mechanism question underlying the enrollment-vs-disengagement trade-off.

**Why it matters here.** Gives the mechanism-level account of exactly the question the brief asks—whether enrollment defaults change durable behavior or fade—useful for predicting which round-up users will disengage and why.

**Method.** Conceptual/theoretical review synthesizing prior default-effect literature into a research agenda; abstract-only.

**Limitations.**

- Theoretical synthesis, not a new empirical estimate.
- Not specific to financial products, so predictions must be validated in our setting.

<sub>selected: score · criteria: C1 1/3 · C2 3/3 · C3 2/3 · C4 2/3 · C5 2/3 · C6 0/3 · flags: review · verified 2026-08-27 via crossref, openalex</sub>

## 5. Sending Out an SMS: Automatic Enrollment Experiments for Overdraft Alerts

Michael D. Grubb, Darragh Kelly, Jeroen Nieboer, Matthew Osborne et al. · 2024 · The Journal of Finance · rct · overall 3/3

<https://doi.org/10.1111/jofi.13404>

**Key finding.** At-scale UK bank field experiments show automatic enrolment into just-in-time overdraft alerts reduces unarranged overdraft charges 17-19% and arranged overdraft charges 4-8%, worth an estimated £170-240 million annually market-wide, though alerts capture less than half of the achievable savings.

**Why it made the cut.** design-changing · selected by score · strongest on C1 default effect size (3/3). Closest available consumer-banking evidence on auto-enrolment's real financial effect at scale, directly informing the entry-decision trade-off.

**Why it matters here.** This is a consumer banking auto-enrolment feature at the same institutions and scale as ours, giving a real effect-size benchmark for what auto-enrolment can deliver in a live app, and evidence that even a working default captures only part of the possible benefit.

**Method.** Large-scale randomized field experiments at major UK retail banks comparing automatic enrolment into alert types.

**Limitations.**

- measures charge reduction, not savings-pot enrolment or amount saved
- no explicit long-horizon (6-12 month) retention analysis reported in the abstract
- alerts are a passive notification, not a savings-contribution decision

<sub>selected: score · criteria: C1 3/3 · C2 2/3 · C3 0/3 · C4 3/3 · C5 1/3 · C6 0/3 · verified 2026-08-27 via crossref, openalex</sub>

## 6. Framing the Default Option Right

Luc Meunier, Yashar Bashirzadeh, Sima Ohadi · 2024 · Journal of Behavioral Decision Making · experimental · overall 3/3

<https://doi.org/10.1002/bdm.2395>

**Key finding.** Across experiments including a 4,207-person five-country European sample, default nudges produced medium-to-large shifts in risk-taking but also lowered users' ratings of the advice/wealth manager, especially when the default was one they refused.

**Why it made the cut.** plan-influencing · selected by score · strongest on C5 distributional and manipulation risk (3/3). Directly measures the manipulation/trust cost of defaults in a European financial-advice context, matching the brief's concern about dark-pattern perception.

**Why it matters here.** Provides direct European evidence that a default can be perceived as manipulative and damage trust when it's not accepted—precisely the reputational, dark-pattern risk the EU-context brief flags for the entry and level decisions.

**Method.** Three experiments, including a large representative multi-country European sample, testing default framing and presentation effects on investment allocation and perceived advice quality.

**Limitations.**

- Setting is investment/wealth-management advice rather than a round-up savings sweep specifically.
- Effect on trust is a self-reported rating, not behavioral churn or complaints.

<sub>selected: score · criteria: C1 2/3 · C2 0/3 · C3 2/3 · C4 2/3 · C5 3/3 · C6 0/3 · flags: contradicts · verified 2026-08-27 via crossref, openalex</sub>

## 7. The Effect of Choice Screens on Mobile Browser Usage: Evidence from the EU Digital Markets Act [UNVERIFIED — check manually]

Jesper Akesson, Kush Amlani, Raul Cepeda Suarez, Emily Chissell et al. · 2026 · Social Science Research Network · observational · overall 3/3

<https://doi.org/10.3386/w35112>

**Key finding.** Following the EU Digital Markets Act's mandated browser choice screens, Firefox usage rose 113% on iOS and 12% on Android relative to a no-mandate counterfactual, with effects still present 15 months after rollout.

**Why it made the cut.** design-changing · selected by score · strongest on C6 active choice comparison (3/3). Best available real-world evidence on active/forced choice screens under the same EU regulatory regime the product operates in, central to the C6 question.

**Why it matters here.** This is the most direct evidence available that a forced active-choice screen produces large, persistent behaviour change in an EU-regulated mobile app context — exactly the comparison the active-choice design option needs before it's chosen over opt-out.

**Method.** Difference-in-differences design around staggered EU Digital Markets Act choice-screen rollout across iOS and Android.

**Limitations.**

- mobile browser choice, not a financial savings decision
- platform differences (iOS vs Android rollout) complicate attributing the full effect to the choice screen alone

<sub>selected: score · criteria: C1 2/3 · C2 2/3 · C3 0/3 · C4 2/3 · C5 0/3 · C6 3/3 · UNVERIFIED (title)</sub>

## 8. When Nudges Backfire: The Effect of Social Norms, Framing Effects, and Default Options on the Pension Saving Decisions in China

Yuming Dong, Zhaoyue Wang, Zhuting He · 2025 · Advances in Economics, Management and Political Sciences · rct · overall 3/3

<https://doi.org/10.54254/2754-1169/2025.bl30018>

**Key finding.** In a 220-participant RCT on voluntary pension saving in China, all tested nudges — including default options — significantly reduced willingness to contribute relative to control, contrary to prevailing international evidence, with the largest backfire effects for positive-narrative and default-option nudges.

**Why it made the cut.** contradicting · selected by score · strongest on C1 default effect size (3/3). One of the few papers in this set that directly contradicts the 'defaults always help' premise the brief explicitly asks to test.

**Why it matters here.** Directly contradicts the brief's stated internal premise that 'defaults will lift enrolment' by showing a default option can backfire and reduce willingness to contribute, with effects varying by income, education, and gender — exactly the heterogeneity the brief wants surfaced before committing to opt-out.

**Method.** Randomized controlled trial via online survey testing social-norm, framing, default-option, and narrative nudges on voluntary pension contribution decisions.

**Limitations.**

- small online-survey sample (n=220), not a live financial product
- Chinese cultural/institutional context may not transfer to an EU consumer app
- self-reported willingness rather than observed enrolment or savings behaviour

<sub>selected: score · criteria: C1 3/3 · C2 0/3 · C3 1/3 · C4 1/3 · C5 2/3 · C6 0/3 · flags: contradicts · verified 2026-08-27 via crossref, openalex</sub>

## 9. Behavioral Household Finance

John Beshears, James J. Choi, David Laibson, Brigitte C. Madrian · 2018 · National Bureau of Economic Research · other · overall 3/3

<https://doi.org/10.3386/w24854>

**Key finding.** Synthesizes household-finance behavioral evidence across savings, borrowing, payments, asset allocation, and insurance, and reviews interventions including choice architecture, product design, and disclosure that firms and governments use to shape financial outcomes.

**Why it made the cut.** closely-related · selected by foundational · strongest on C1 default effect size (2/3). Best available broad review of choice-architecture interventions in consumer (not solely employer) financial behavior, satisfying the brief's request for synthesis-level evidence.

**Why it matters here.** The broad synthesis of choice-architecture effects across consumer financial products (not employer plans specifically) the brief asked for as a review giving effect sizes rather than a single study, useful for calibrating expectations about the round-up feature's design levers generally.

**Method.** Narrative review/overview chapter (NBER) synthesizing the behavioral household finance literature.

**Limitations.**

- a narrative overview, not a systematic review or meta-analysis with pooled effect sizes
- covers many financial domains, so savings-specific and app-specific detail is diluted
- 2018 publication, predating the newest fintech default-design literature

<sub>selected: foundational · criteria: C1 2/3 · C2 1/3 · C3 1/3 · C4 2/3 · C5 2/3 · C6 1/3 · flags: review · verified 2026-08-27 via crossref, openalex</sub>

## 10. Side Effects of Nudging: Evidence from a Randomized Intervention in the Credit Card Market

Paolina C. Medina · 2020 · Review of Financial Studies · rct · overall 3/3

<https://doi.org/10.1093/rfs/hhaa108>

**Key finding.** A randomized reminder intervention on a Brazilian financial platform cut credit-card late fees by 14% but raised checking-account overdraft fees by 9%, with users who had a history of overdraft use experiencing a net 5% increase in total fees while everyone else saved 15%.

**Why it made the cut.** contradicting · selected by foundational · strongest on C4 consumer self-directed setting (3/3). Best available evidence in this shortlist that a helpful-seeming nudge can produce net harm for an identifiable user segment, bearing directly on C5's who-is-helped/who-is-hurt question.

**Why it matters here.** Directly evidences the support team's worry: a well-intentioned nudge can help most users while making a defined subgroup worse off, which is exactly the distributional check the brief wants before defaulting everyone into round-up savings.

**Method.** Field experiment (randomized reminder nudge) with a consumer financial management platform in Brazil, comparing fee outcomes across credit card and checking account products.

**Limitations.**

- Studies payment reminders, not enrolment defaults or contribution-level anchors
- Credit card/overdraft fee context rather than a round-up savings pot
- Brazilian credit market may differ from EU consumer-protection context

<sub>selected: foundational · criteria: C1 1/3 · C2 1/3 · C3 0/3 · C4 3/3 · C5 3/3 · C6 0/3 · flags: contradicts · verified 2026-08-27 via crossref, openalex</sub>

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
- [Regulating Dark Patterns](https://doi.org/10.48550/arxiv.2310.00340) (2023) — overall 3/3
- [For Better or For Worse: Default Effects and 401(k) Savings Behavior](https://doi.org/10.3386/w8651) (2001) — overall 2/3
- [Automatic Enrollment with a 12% Default Contribution Rate](https://doi.org/10.3386/w31601) (2023) — overall 2/3
- [Active vs. Passive Decisions and Crowd-Out in Retirement Savings Accounts: Evidence from Denmark *](https://doi.org/10.1093/qje/qju013) (2014) — overall 2/3
