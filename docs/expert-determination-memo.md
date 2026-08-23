# Technical Disclosure-Risk Determination Memo

> **Decision status:** Completed technical recommendation for the scoped Texas 2023 analysis.
> This is not a legal opinion or certification under a specific de-identification safe harbor.
> A qualified reviewing organization must accept the recommendation and residual risk before use.

## Executive determination

The current public-field configuration is not suitable for republication as an unsuppressed
row-level analytical extract under the modeled institution-aware threat scenario. Of 1,041,819
Texas 2023 HMDA applications, 94.18% are sample unique when tract, disclosed demographics,
financial/loan context, and LEI are combined. This is a statistical disclosure-risk finding; no
person was identified and no identified auxiliary source was acquired.

For a derivative research release, adopt the **state-banded configuration with k≥5 suppression**:
state geography, $50,000 income bands, $100,000 loan-amount bands, and removal of equivalence
classes smaller than five. This configuration reduces pre-suppression sample uniqueness to
30.24%, retains 49.71% of records at k≥5, supports an unadjusted Black–White denial-disparity MDE
of 0.69 percentage points, and retains 135,223 decision records for the adjusted model. No
row-level protected output is authorized by this repository; aggregate publication is the default.

## 1. Scope and data

- Data: 2023 public HMDA Loan/Application Register, Texas full state-year release.
- Applications: 1,041,819.
- Bronze SHA-256: `2965d27916912b99d614764a75c0096290f1a35761b5c593725a4a33157b002a`.
- Validation anchor: 38,026 Black-borrower Texas originations totaling $11,390,150,000. This
  filtered query validates ingestion only and is not used to calculate subgroup uniqueness.
- Residential context: 6,771 tracts from public HMDA `tract_population` joined to 2023 Census
  Gazetteer land area; zero conflicting population values. Density analysis covers 1,015,333
  applications, 97.46% of the state-year release.

This determination applies only to this state, year, field set, transformation set, and threat
model. It does not generalize automatically to national HMDA data or another release year.

## 2. Ethical boundary and threat models

Guardrails were documented before empirical work. The analysis measures equivalence-class
uniqueness and theoretical or synthetic linkage risk. It prohibits identified auxiliary datasets,
attempted identification, row-level high-risk exports, and publication of cells below 20.

- **Prosecutor:** knows a target is in the release and possesses some disclosed quasi-identifiers.
- **Journalist:** has partial demographic, geographic, and transaction context but not a complete
  identified registry.
- **Marketer:** has broad commercial context. Real linkage is prohibited; only synthetic auxiliary
  data may model this threat.

## 3. Methodology

Equivalence classes are formed on the entire state-year release before demographic filtering.
Three nested QI tiers isolate demographic/geographic fields, financial and loan context, and LEI.
Risk is reported through sample uniqueness, shares below k thresholds, and prosecutor expected
match risk. Published cohort cells contain at least 20 records.

Four protection configurations are evaluated: current tract-level fields, county geography,
county plus numeric bands, and state plus wider numeric bands. The utility frontier reports k≥5
retention and the two-sided 80%-power, 5%-alpha minimum detectable denial-rate disparity. A
decision-only logistic model estimates descriptive Black–White disparity after configuration and
k≥5 protection are applied.

A zero-truncated gamma–Poisson population-uniqueness model was fit across declared coverage
scenarios. Every real-data fit collapsed to a gamma-shape boundary, so the estimator returns
`boundary_fit_not_reportable`. No population-unique point estimate is accepted.

## 4. Quantified risk findings

| QI tier | Sample uniqueness | Prosecutor risk |
|---|---:|---:|
| Demographic + tract geography | 14.44% | 28.44% |
| Financial/loan context added | 87.30% | 91.66% |
| Institution-aware, including LEI | 94.18% | 96.18% |

Financial and loan context is the dominant risk amplifier. LEI adds approximately 6.89 percentage
points of sample uniqueness beyond the financial-context tier.

Under the demographic/geographic threat model, Black non-Hispanic applicants have 16.03% sample
uniqueness and 32.86% prosecutor risk, compared with 5.66% and 19.51% for White non-Hispanic
applicants. The residual privacy burden is not evenly distributed.

The preregistered expectation that risk would peak in low-density residential tracts did not hold.
Overall uniqueness is 12.34% in the lowest-density quintile and 23.38% in the highest. For Black
non-Hispanic applicants it rises from 16.57% to 28.97%; for White non-Hispanic applicants, from
3.57% to 13.84%. This differs from release density, where risk decreases as the number of HMDA
applications per tract increases. Residential density and release density are not interchangeable.

## 5. Quantified utility impact

| Configuration | Uniqueness | Retained at k≥5 | Unadjusted MDE |
|---|---:|---:|---:|
| CFPB current | 94.18% | 1.70% | Not estimable |
| County geography | 87.35% | 8.00% | Not estimable |
| County + $25k/$50k bands | 69.48% | 14.63% | 2.50 points |
| State + $50k/$100k bands | 30.24% | 49.71% | 0.69 points |

Current and county-only configurations retain no usable Black–White comparison after k≥5. The
banded configurations create larger equivalence classes and improve both privacy and analytical
utility under suppression.

The adjusted models converge for both estimable configurations. County-banded adjusted odds
ratio is 2.17 (95% CI 1.74–2.71; n=8,491). State-banded adjusted odds ratio is 2.04 (95% CI
1.95–2.13; n=135,223). These are descriptive conditional disparities, not causal findings.

## 6. Recommendation and controls

1. Do not create an additional unsuppressed row-level derivative of the current public fields.
2. If a derivative microdata research release is required, use state geography, $50,000 income
   bands, $100,000 loan-amount bands, and k≥5 suppression.
3. Keep LEI out unless a documented use case justifies its 6.89-point risk increment and additional
   protection is applied.
4. Publish project results as aggregate tables and figures with minimum cell size 20.
5. Require purpose approval, immutable configuration metadata, and review for any exception.

## 7. Residual risk accepted and rationale

The recommendation does not make the source data anonymous. Pre-suppression uniqueness remains
30.24%, half the release is removed at k≥5, model results are QI-sensitive, and population
uniqueness is not estimable. Residual risk is accepted only for a controlled derivative because
small classes are excluded, precision is reduced, and utility remains stronger than under other
tested k≥5 alternatives. Aggregate-only publication accepts substantially less disclosure risk
and remains the default.

## 8. Re-evaluation triggers

- A new HMDA year, geography vintage, or material source-schema change.
- Addition or removal of a QI, especially LEI, tract, income, or loan amount.
- New evidence about realistic auxiliary-data availability.
- A change in thresholds, intended users, access controls, or publication purpose.
- Subgroup risk exceeding the accepted level or a material density-pattern change.
- A validated population-uniqueness estimator producing a stable result.
- Model validation failure, non-convergence, or material specification change.

## 9. Limitations and review record

HMDA omits some legitimate underwriting factors, so adjusted disparities may contain omitted
variable bias. Confidence intervals are model-based and not lender- or geography-cluster robust.
Tract population density is contextual and not an official rural classification. Unmatched tracts
are excluded. The protection sweep is not exhaustive. No real identified linkage was performed,
so threat results remain conditional on stated adversary knowledge.

- **Prepared by:** Cory Cooper
- **Analysis date:** 2026-08-23
- **Required approver:** Independent privacy/governance reviewer
- **Review decision:** Pending external acceptance
