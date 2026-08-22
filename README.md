# HMDA Disclosure Risk & Governance Platform

This project measures how much re-identification risk remains in publicly released Home Mortgage Disclosure Act (HMDA) data and what stronger privacy protection would cost in fair-lending analytical utility.

## Ethical guardrails — read before writing or running code

This project measures re-identification risk on real people's mortgage records. The boundary between privacy engineering and doxxing is a design decision.

### Permitted

- Measure uniqueness, equivalence-class sizes, k-anonymity distributions, and population-uniqueness estimates.
- Model linkage risk theoretically.
- Simulate linkage only against synthetic auxiliary data generated from aggregate marginal distributions.
- Report results only in aggregate and suppress small cells.

### Prohibited

- Obtaining or using identified auxiliary data such as voter files, property-owner records, or marketing lists.
- Attempting to identify an applicant or borrower.
- Publishing a record or field combination that narrows to a person.
- Exporting row-level high-risk records from analysis code.

The package enforces these rules by returning aggregate risk tables, rejecting direct identifiers in quasi-identifier configurations, and applying small-cell suppression to cohort outputs. See [SECURITY.md](SECURITY.md).

## Research question

> How much re-identification risk remains in public HMDA data after the CFPB's disclosure modifications, and what would stronger protection cost in the ability to detect lending discrimination?

## First checkpoint

The initial implementation contains the two components where early design mistakes are most expensive:

1. A resumable, SHA-256-manifested HTTP ingestion layer for keyless FFIEC/CFPB CSV endpoints.
2. A privacy-safe risk engine for equivalence classes, sample uniqueness, k-distributions, prosecutor risk, and aggregate cohort concentration.
3. An assumption-labeled population-uniqueness subsampling diagnostic and an identity-free synthetic linkage simulation.
4. A protection engine for geographic and numeric generalization, k-suppression, l-diversity, t-closeness, and differentially private aggregate counts.
5. A fair-lending power diagnostic and privacy–utility frontier with the current CFPB-style configuration explicitly marked.
6. Executable governance gates for column classification, restricted publication, expiring exceptions, retention, and a synthetic-only subject-rights path.

The default quasi-identifier set is explicitly versioned in `config/quasi_identifiers.yml`. It can be changed only through configuration and CI review.

## Quick start

```bash
python -m venv .venv
source .venv/bin/activate
pip install -e '.[dev]'
pytest
```

Download a filtered slice:

```bash
hmda ingest --year 2023 --state TX --output data/bronze
```

Profile a local CSV without emitting row-level matches:

```bash
hmda risk --input data/bronze/<file>.csv --output artifacts/risk-summary.json
```

Estimate population uniqueness using a declared sampling fraction:

```bash
hmda population-uniqueness --input <file>.csv --sample-fraction 0.10 \
  --output artifacts/population-uniqueness.json
```

Run a synthetic-only linkage simulation:

```bash
hmda synthetic-linkage --input <file>.csv --records 10000 \
  --output artifacts/synthetic-linkage.json
```

The current population-uniqueness routine is explicitly labeled a repeated-subsampling
proxy. It is not represented as a Zayatz or Pitman implementation. A validated standard-model
estimator must be added and compared before the expert-determination memo is finalized.

Protection configurations are versioned in `config/protection.yml`. The differential-privacy
implementation documents its event-level contribution assumption and does not expose true
counts in its returned public table.

The first utility metric is an unadjusted two-proportion power analysis. It is deliberately
identified as a diagnostic rather than the final adjusted fair-lending model.

## Architecture

- **Bronze:** immutable source files plus request/receipt metadata and SHA-256 manifests
- **Silver:** classified, tested models (planned dbt checkpoint)
- **Gold:** aggregate equivalence classes, risk metrics, and fair-lending estimates
- **Privacy:** protection configurations and the risk–utility frontier
- **Serve:** aggregate figures and `docs/expert-determination-memo.md`

No HMDA loan-level data is committed to Git. Generated data and analysis artifacts are ignored by default.

## Status

This repository is under active development. Results are not an expert determination until the methodology, data validation, uncertainty analysis, and memo are complete.
