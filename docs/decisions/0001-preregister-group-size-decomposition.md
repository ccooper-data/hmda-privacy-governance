# ADR 0001: Preregister group-size decomposition

- **Status:** Accepted before analysis
- **Date:** 2026-08-23
- **Scope:** Texas 2023 HMDA full state-year release
- **Outcome commitment:** Report the result whether it supports or withdraws the existing disparity interpretation

## Context

The demographic/geographic equivalence-class key contains census tract, applicant age, applicant
sex, derived race, and derived ethnicity. Because race and ethnicity partition the classes, groups
with fewer applications inside a tract can have higher sample uniqueness mechanically. The existing
Black non-Hispanic versus White non-Hispanic comparison does not distinguish that group-size effect
from residual association between race/ethnicity and the other matching fields.

This ADR fixes the hypotheses, estimands, procedures, tolerances, and decision rules before any
group-size-decomposition code is written or any decomposition result is generated.

## Analysis universe and definitions

- Use the complete Texas 2023 state-year release before demographic or completeness filtering.
- Form the demographic/geographic equivalence classes on census tract, applicant age, applicant
  sex, derived race, and derived ethnicity. Missing QI values remain explicit matching values.
- Define the focal cohorts as Black non-Hispanic and White non-Hispanic applications using the
  public HMDA derived fields.
- Define record-level sample uniqueness as an application belonging to an equivalence class of
  size one.
- Define the primary disparity statistic as the Black non-Hispanic sample-uniqueness rate divided
  by the White non-Hispanic sample-uniqueness rate. If the denominator is zero, the statistic is
  non-estimable and no residual-disparity claim will be made.

## Null hypothesis

The primary null hypothesis is that the observed Black/White uniqueness ratio is fully explained
by within-tract racial/ethnic group counts and the tract distribution of applications. Conditional
on census tract and its observed joint race/ethnicity margins, race/ethnicity labels are
exchangeable with respect to applicant age and applicant sex. Under this null, any ratio generated
after within-tract label permutation is structural rather than evidence of residual racial patterning.

The alternative is that the observed ratio is more extreme than would be expected from those local
group counts alone because race/ethnicity remains associated with the other demographic matching
fields within tract.

## Analysis A: uniqueness by within-tract group size

For every `(census_tract, derived_race, derived_ethnicity)` group, calculate `n_group`. Assign fixed,
predeclared bins: 1, 2, 3–4, 5–9, 10–19, 20–49, 50–99, and 100 or more applications. Report record
count, unique-record count, and uniqueness rate by bin overall and separately for the two focal
cohorts. Bins with fewer than 20 applications will be suppressed from publication but retained in
aggregate totals. The comparison is descriptive; no fitted curve will replace the binned table.

## Analysis B: size-matched tract comparison

A tract is size matched when it contains both focal cohorts and
`max(n_black, n_white) / min(n_black, n_white) <= 1.20`, equivalent to counts within 20% on a
symmetric ratio scale. The tolerance will not be changed after results are observed. Recompute the
Black/White uniqueness ratio using applications in matched tracts and report the number of matched
tracts and applications retained for each cohort.

Use 2,000 tract-cluster bootstrap resamples, with seed `20260823`, for a percentile 95% confidence
interval. If fewer than 20 matched tracts or fewer than 100 applications in either cohort remain,
label the comparison underpowered and do not use it to support a residual-disparity claim.

## Analysis C: within-tract permutation null

1. Preserve every application's tract, age, and sex.
2. Within each tract, shuffle the observed **joint** `(derived_race, derived_ethnicity)` labels
   without replacement. This exactly preserves each tract's joint racial/ethnic marginal counts.
3. Re-form equivalence classes and compute the focal Black/White uniqueness ratio.
4. Repeat 1,000 times using a NumPy `PCG64` generator with seed `20260823`.
5. Report the observed ratio, null mean, null standard deviation, equal-tail 95% null interval, and
   Monte Carlo p-value using the plus-one correction:
   `(1 + count(abs(T_perm - mean(T_perm)) >= abs(T_obs - mean(T_perm)))) / 1001`.

The overall state-year ratio is the single primary test. Density-quintile ratios are secondary and
will be reported descriptively with Holm-adjusted two-sided permutation p-values. No iteration,
seed, tail, statistic, or subgroup will be selected after observing results.

## Decision rule

The existing unqualified claim that Black non-Hispanic applicants bear a distinct residual privacy
burden will be **withdrawn** unless both conditions hold:

1. the observed overall ratio is above the 97.5th percentile of the permutation null and the
   two-sided plus-one permutation p-value is below 0.05; and
2. the size-matched comparison is not underpowered and its 95% tract-bootstrap confidence interval
   excludes 1 in the same direction.

If either condition fails, the memo will retain the raw rates only as descriptive facts and replace
the residual-disparity interpretation with the structural conclusion that the observed burden is
consistent with local group size. If both conditions pass, the memo may describe a residual
association beyond group size, but not causation, discrimination, or individual re-identification.

## Reporting commitment

All three analyses, diagnostics, sample sizes, suppressed-bin metadata, null distribution summary,
and decision outcome will be committed regardless of direction. The generating script will reject
row-level output and write aggregate results only. No real identified auxiliary data or attempted
person-level linkage is permitted.

## Integrity record

The SHA-256 digest is stored beside this ADR. The preregistration commit must be pushed to `main`
before decomposition code or results are created. Later amendments require a new ADR that cites
this file and explains the change; this file will not be rewritten after results exist.
