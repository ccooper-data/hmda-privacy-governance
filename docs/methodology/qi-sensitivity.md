# Quasi-Identifier Sensitivity Design

The platform evaluates three nested, threat-informed QI sets:

1. `demographic_geo`: census tract, binned age, sex, race, and ethnicity.
2. `financial_context`: the demographic/geographic tier plus income, loan amount, loan type,
   debt-to-income band, loan purpose, occupancy, lien status, and dwelling category.
3. `institution_aware`: the financial-context tier plus lender LEI.

The nested design attributes incremental risk to added information rather than treating the most expansive QI set as the only plausible attacker knowledge. In particular, the difference between `financial_context` and `institution_aware` measures LEI's incremental effect.

Each tier is formed over the same complete state-year universe. dbt tests verify that the sum of equivalence-class sizes equals the source application count at every tier. Only aggregate, small-cell-suppressed cohort results are exported.
