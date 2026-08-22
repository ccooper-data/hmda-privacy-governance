# Source Validation Contracts

The first live contract queries the keyless CFPB aggregation endpoint for Texas 2023 originations to Black or African American applicants. The confirmed aggregate is 38,026 records and $11,390,150,000 in loan amount.

The expected values are versioned in `config/validation_contracts.yml`. `scripts/validate_live_contract.py` obtains the current API value and fails if it differs beyond the declared tolerance. The expected result is not substituted for live data.

For a downloaded CSV slice, `reconcile_local_slice` independently calculates row count and loan-amount sum and compares them with the API result. Only aggregate differences are returned.

