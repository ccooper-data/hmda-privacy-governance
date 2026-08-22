# Synthetic Linkage Threat Simulation

The simulator never obtains or uses identified auxiliary data. It creates an identity-free table containing only configured quasi-identifiers sampled from empirical one-way marginal distributions.

The first model deliberately samples columns independently. It therefore preserves one-way marginals but not joint relationships. This is a transparent baseline, not a claim that the synthetic data reproduces a real external registry.

Only aggregate results are returned:

- exact-match rate;
- unique-match rate;
- expected correct matches under random selection within an equivalence class; and
- expected correct-match rate.

Synthetic rows and matched rows are not written by the command-line interface.

