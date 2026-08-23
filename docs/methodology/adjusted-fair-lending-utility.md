# Adjusted fair-lending utility

## Purpose

This diagnostic asks whether a disclosure-protection configuration retains enough usable
information to estimate a Black–White denial disparity after adjustment for disclosed borrower
and loan characteristics. It is descriptive and must not be interpreted as causal evidence of
discrimination or as a substitute for a supervisory fair-lending review.

## Cohort and outcome

The analysis is limited to non-Hispanic Black and non-Hispanic White applicants with a decision
outcome: originated (1), approved but not accepted (2), denied (3), or preapproval denied (7).
The binary outcome is one for actions 3 or 7 and zero for actions 1 or 2. Withdrawn and incomplete
applications are excluded rather than treated as approvals.

## Protection-before-modeling contract

For every configuration, equivalence-class size is computed on the full state-year release.
The configured geography and numeric transformations are applied before class formation. Only
then are records in classes with k at least five retained and the decision cohort selected. This
ordering prevents subgroup filtering from artificially inflating uniqueness and ensures that the
utility estimate measures the actual protected release.

## Specification

The model is a logistic regression fit by iteratively reweighted least squares. The focal term is
an indicator for Black non-Hispanic applicants. Adjustment fields are log income, log loan amount,
age band, sex, loan type, debt-to-income band, loan purpose, occupancy type, lien status, and
dwelling category. Missing categorical values are explicit levels; missing continuous values are
median-imputed within the protected cohort. Continuous terms are standardized for numerical
stability. Reported outputs are the adjusted odds ratio, its model-based 95% confidence interval,
and an approximate average marginal effect in percentage points.

## Privacy and publication

The modeling relation is internal and row-grain and is prohibited from publication. The export
contains only configuration-level counts, rates, coefficients, confidence intervals, convergence
status, and method metadata. No record-level predictions, residuals, influential observations, or
high-risk cases are exported.

## Limitations

HMDA public fields do not contain every legitimate underwriting factor, and disclosed fields may
be coarsened or missing. The interval is model-based and does not yet include lender or geography
cluster-robust uncertainty. The approximate marginal effect is a compact utility diagnostic, not
a causal risk difference. A final determination must disclose these limits and compare sensitivity
specifications.
