# Population-Uniqueness Methodology

## Estimators

The current checkpoint implements a repeated-subsampling proxy. The released file is treated as a proxy population. Each replicate draws from it at the declared original sampling fraction. The proportion of replicate-unique equivalence classes that are also unique in the full released file estimates the proportion of released-file uniques that may be population unique.

This approach is reproducible and useful as a sensitivity diagnostic, but it relies on the released file adequately representing the population equivalence-class structure. It is **not** labeled as a Pitman or Zayatz estimator.

The standard model-based comparison is a zero-truncated gamma–Poisson equivalence-class model.
It assumes latent cell intensities follow a gamma distribution and that released and unreleased
cell counts arise through independent Poisson thinning. Parameters are fit by maximum likelihood
to the observed positive class-size distribution. For a released-file unique, the posterior
probability of no additional population members is

`((rate + coverage) / (rate + 1)) ** (shape + 1)`.

HMDA is a census of reportable applications rather than a probability sample of residents or
property owners. Consequently, the coverage fraction is not identified by the release. Results
are reported across declared sensitivity scenarios; none is labeled the true population risk.

## Interpretation constraints

- The supplied sampling fraction must have a documented denominator.
- Intervals describe variation across resamples; they are not automatically valid design-based confidence intervals.
- Small sampling fractions and sparse, high-dimensional QI sets can produce unstable estimates.
- Gamma–Poisson results depend on cell-distribution fit and the declared coverage scenario.
- Population-uniqueness sensitivity supplements, but does not replace, release-universe sample uniqueness.

## Literature anchors

- Zayatz, *Estimation of the Percent of Unique Population Elements on a Microdata File Using the Sample* (U.S. Census Bureau, 1991).
- Steel, *A New Estimation for the Number of Unique Population Elements Based on the Observed Sample* (U.S. Census Bureau, 1999).
- Reiter, *Estimating Risks of Identification Disclosure in Microdata* (JASA, 2005).
