# Executable Governance Controls

## Classification gate

Every published column must have one allowed classification. Unclassified columns, invalid tags, and restricted classifications in published marts fail the governance check. The CI workflow runs this check on every push and pull request.

## Exceptions

Exceptions require an ID, violation code, model, accountable owner, reason, and expiration date. Expired exceptions do not bypass a violation.

## Retention and purpose

Retention periods and permitted purposes are versioned in `config/governance.yml`. Time checks require timezone-aware timestamps.

## Subject-rights control path

The export and cascading-deletion demonstration is restricted to an explicitly synthetic control cohort keyed by `synthetic_subject_key`. It locates every table containing the key, produces an export or deletion result, and emits an aggregate audit record. It is not used to search for or identify an HMDA borrower.

