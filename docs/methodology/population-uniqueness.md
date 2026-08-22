# Population-Uniqueness Methodology

## Current estimator

The current checkpoint implements a repeated-subsampling proxy. The released file is treated as a proxy population. Each replicate draws from it at the declared original sampling fraction. The proportion of replicate-unique equivalence classes that are also unique in the full released file estimates the proportion of released-file uniques that may be population unique.

This approach is reproducible and useful as a sensitivity diagnostic, but it relies on the released file adequately representing the population equivalence-class structure. It is **not** labeled as a Pitman or Zayatz estimator.

## Interpretation constraints

- The supplied sampling fraction must have a documented denominator.
- Intervals describe variation across resamples; they are not automatically valid design-based confidence intervals.
- Small sampling fractions and sparse, high-dimensional QI sets can produce unstable estimates.
- The expert-determination memo must compare this proxy against a validated standard-model estimator before recommending a release configuration.

## Literature anchors

- Zayatz, *Estimation of the Percent of Unique Population Elements on a Microdata File Using the Sample* (U.S. Census Bureau, 1991).
- Steel, *A New Estimation for the Number of Unique Population Elements Based on the Observed Sample* (U.S. Census Bureau, 1999).
- Reiter, *Estimating Risks of Identification Disclosure in Microdata* (JASA, 2005).

