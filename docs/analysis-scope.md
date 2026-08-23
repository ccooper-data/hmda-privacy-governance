# Equivalence-Class Analysis Scope

## Required order of operations

1. Load the complete declared release universe, such as all public Texas records for one year.
2. Form quasi-identifier equivalence classes across that complete universe.
3. Attach class size `k` internally to each source record.
4. Aggregate risk by race, ethnicity, geography density, or another approved cohort.
5. Suppress small cohort cells and publish only the aggregate table.

Filtering to a protected group before forming equivalence classes can shrink classes and inflate apparent uniqueness. The initial Texas 2023 Black-originations slice is therefore retained only as an ingestion and source-validation exercise. Its 99.82% sample-uniqueness result is not a defensible subgroup or population estimate and must not be cited as a finding.

`hmda cohort-risk` requires the analyst to declare `full_state_year` or `full_national_year` as the equivalence universe. It does not accept a filtered-group universe.

Ingestion filenames encode filter scope. A full Texas file ends in `TX_all.csv`; a filtered file includes its action and race filters. This prevents a broader analytical universe from silently overwriting a validation slice or vice versa.
