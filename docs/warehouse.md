# DuckDB and dbt Warehouse

## Run locally

```bash
pip install -e '.[warehouse]'
cp profiles.example.yml profiles.yml
export DBT_PROFILES_DIR="$PWD"
dbt build --vars '{hmda_lar_path: data/bronze/year=2023/hmda_2023_TX.csv}'
```

The staging model reads an immutable manifested bronze CSV. The silver application table normalizes the analysis grain and derives the denial indicator. The first gold mart aggregates by year, race, and ethnicity and suppresses groups below 20 records.

Every modeled column is classified in `models/schema.yml`. CI parses each explicit SELECT list and fails if a newly selected column has no approved classification.

`qi_profile` forms equivalence classes over the full loaded release. `risk_metrics_by_race`
then joins those class sizes back internally and publishes only small-cell-suppressed aggregate
metrics. The singular dbt test verifies that the sum of equivalence-class sizes equals the
application record count.
