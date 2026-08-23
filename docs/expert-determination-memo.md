# Technical Disclosure-Risk Determination Memo

> **Decision status: DRAFT TECHNICAL RECOMMENDATION.** The earlier release recommendation was
> withdrawn after adversarial review changed the QI definition and corrected the utility cohort.
> This is not a legal opinion or de-identification certification. Independent acceptance is pending.

## Executive finding

The unsuppressed public HMDA file presents high exact-match uniqueness under the selected 14-field
institution-aware threat model. Of 1,041,819 Texas 2023 applications, 95.70% are sample unique when
tract, disclosed demographics, income, loan amount, loan type, debt-to-income band, loan context,
and lender LEI are combined. This is conditional sample uniqueness—not an identification
probability—and no person was identified or linked to an identified auxiliary source.

The former recommendation to adopt state-banded fields with k≥5 is no longer accepted as final.
After aligning the privacy and utility field sets, state-banded pre-suppression uniqueness is
57.34%, k≥5 retains 24.68% of records, and the decision-cohort Black–White MDE is 2.23 percentage
points versus 0.56 points for today's unsuppressed public file. State-banded remains the strongest
tested microdata candidate, but its 75.32% suppression cost requires independent purpose-specific
acceptance. Aggregate publication remains the only currently authorized output.

## 1. Scope and integrity

- Data: 2023 public HMDA Loan/Application Register, complete Texas state-year release.
- Applications: 1,041,819.
- Bronze SHA-256: `2965d27916912b99d614764a75c0096290f1a35761b5c593725a4a33157b002a`.
- QI definition: selected 14-field institution-aware set in `config/quasi_identifiers.yml`.
- Residential context: 6,771 HMDA-active tracts; 1,015,333 applications matched (97.46%).
- Preregistration: `docs/decisions/0001-preregister-group-size-decomposition.md`, committed and
  hashed before the decomposition implementation or results.

This determination is limited to this state, year, QI set, threat model, and transformation sweep.

## 2. Ethical boundary

The project prohibits identified auxiliary data, attempted identification, row-level high-risk
exports, and published cells below 20. Export paths redact a complete aggregate record when any
contributing reference or comparison cell is below the configured threshold. Real linkage is not
performed; linkage modeling is synthetic only.

## 3. Methods

Equivalence classes are formed on the complete state-year universe before cohort filtering. SQL
`GROUP BY` and Python `groupby(dropna=False)` retain missing QI values as explicit matching values.
This generally enlarges missing-value classes and is conservative for uniqueness relative to
dropping incomplete records.

The utility diagnostic uses only decision actions 1, 2, 3, and 7. Denials are actions 3 and 7;
withdrawn, incomplete, and purchased applications are excluded. The MDE is a two-sided normal
approximation with alpha 0.05 and power 0.80. The actual unsuppressed file is reported separately
from each hypothetical k≥5 release. Frontier columns distinguish pre-suppression uniqueness,
post-suppression uniqueness, and suppression cost.

## 4. Group-size decomposition

The raw demographic/geographic uniqueness ratio is 2.830: 16.03% for Black non-Hispanic versus
5.66% for White non-Hispanic applicants. That raw comparison is not interpreted as an independent
racial effect.

The preregistered 1,000-iteration within-tract permutation preserved every tract's joint
race/ethnicity margins. Its null ratio was 2.738 (95% interval 2.695–2.778); the observed ratio was
above the null, two-sided plus-one p=0.001. However, in the preregistered size-matched analysis—243
tracts, 5,193 Black and 5,162 White applications—the ratio was 0.975 (tract-bootstrap 95% interval
0.878–1.084). Because both preregistered conditions were required, the unqualified residual racial
disparity claim is withdrawn.

The supported policy interpretation is structural: much of the aggregate disparity arises because
race is released and locally smaller demographic groups necessarily form smaller matching classes.
The remedy should target geographic and financial resolution rather than removing race, which would
undermine HMDA's fair-lending purpose. The permutation result also indicates residual within-tract
association before size matching, but it does not survive the preregistered equal-size comparison.

## 5. Density findings

Black non-Hispanic uniqueness by residential-density quintile is 16.57%, 10.31%, 15.89%, 20.72%,
and 28.97%. The series is U-shaped—not monotone—and the low-density expectation partially holds
because quintile 1 exceeds quintiles 2 and 3. White non-Hispanic rates are 3.57%, 3.90%, 6.55%,
8.79%, and 13.84%.

Residential- and release-density quintiles are related but not interchangeable: their tract-level
correlation is -0.242 across 6,771 matched tracts. Within every residential quintile, uniqueness
falls as release volume rises. Residential quintiles include only HMDA-active tracts with available
population and positive land area, and equalize tract counts rather than application counts.
The 26,486 unmatched applications are separately audited by race, ethnicity, action, dwelling type,
and lender in the generated density-diagnostics artifact.

## 6. Corrected privacy–utility frontier

| Release state | Pre-suppression uniqueness | Post-suppression uniqueness | Retained | Decision MDE |
|---|---:|---:|---:|---:|
| Actual CFPB unsuppressed | 95.70% | 95.70% | 100.00% | 0.56 pp |
| Current fields + k≥5 | 95.70% | 0.00% | 1.20% | Not estimable |
| County geography + k≥5 | 89.34% | 0.00% | 6.51% | Not estimable |
| County + $25k/$50k bands + k≥5 | 82.29% | 0.00% | 10.56% | 10.15 pp |
| State + $50k/$100k bands + k≥5 | 57.34% | 0.00% | 24.68% | 2.23 pp |

The zero post-suppression uniqueness is mechanical under k≥5 and is not a claim of anonymity.
Attribute disclosure, linkage under omitted QIs, and model misspecification remain possible.

The county-banded adjusted model did not converge (n=871) and cannot support comparison. The
state-banded model converged (n=30,515) with descriptive adjusted OR 2.06 (95% CI 1.82–2.33).
Exact covariate common support covers 37.0% of retained White records and 91.7% of retained Black
records, confirming material selection into modal QI cells. The estimate is descriptive, not causal,
and is not directly comparable with the failed county model.

## 7. Draft recommendation

1. Do not republish an additional unsuppressed row-level derivative.
2. Publish project findings only as aggregates with minimum cell size 20.
3. If microdata are operationally required, treat state-banded plus k≥5 as a candidate for a
   controlled-access environment—not an approved public release—pending purpose-specific review of
   its 75.32% suppression and 2.23-point MDE.
4. Keep LEI out of a derivative unless a documented analytical need and additional protection justify it.
5. Re-evaluate for every year, QI change, geography vintage, threat-model change, or intended user.

## 8. Residual uncertainty

Population uniqueness remains non-reportable because every gamma–Poisson fit reached a parameter
boundary. The protection sweep is not exhaustive. Confidence intervals are model-based and not
lender- or geography-cluster robust. HMDA omits legitimate underwriting variables. Density-join
exclusions may be selective. No actual linkage attack was performed.

- **Prepared by:** Cory Cooper
- **Analysis date:** 2026-08-23
- **Required approver:** Independent privacy/governance reviewer
- **Review decision:** Pending
