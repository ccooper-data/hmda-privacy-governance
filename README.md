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

## Architecture

- **Bronze:** immutable source files plus request/receipt metadata and SHA-256 manifests
- **Silver:** classified, tested models (planned dbt checkpoint)
- **Gold:** aggregate equivalence classes, risk metrics, and fair-lending estimates
- **Privacy:** protection configurations and the risk–utility frontier
- **Serve:** aggregate figures and `docs/expert-determination-memo.md`

No HMDA loan-level data is committed to Git. Generated data and analysis artifacts are ignored by default.

## Status

This repository is under active development. Results are not an expert determination until the methodology, data validation, uncertainty analysis, and memo are complete.

