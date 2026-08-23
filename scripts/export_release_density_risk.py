from __future__ import annotations

import argparse
import json
from pathlib import Path

import duckdb

from hmda_privacy.config import load_qi_config
from hmda_privacy.publication import enforce_minimum_cell


def main() -> None:
    parser = argparse.ArgumentParser()
    parser.add_argument("--database", type=Path, default=Path("data/hmda_privacy.duckdb"))
    parser.add_argument("--output", type=Path, required=True)
    args = parser.parse_args()
    connection = duckdb.connect(str(args.database), read_only=True)
    rows = connection.execute(
        """select release_density_quintile, derived_race, derived_ethnicity,
                  record_count, sample_uniqueness_rate, prosecutor_expected_match_risk
           from risk_by_release_density
           order by release_density_quintile, record_count desc"""
    ).fetchdf()
    overall = connection.execute(
        """select release_density_quintile, sum(record_count) as record_count,
                  sum(record_count * sample_uniqueness_rate) / sum(record_count)
                      as sample_uniqueness_rate,
                  sum(record_count * prosecutor_expected_match_risk) / sum(record_count)
                      as prosecutor_expected_match_risk
           from risk_by_release_density
           group by release_density_quintile
           order by release_density_quintile"""
    ).fetchdf()
    payload = {
        "metadata": {
            "aggregate_only": True,
            "density_measure": "HMDA applications per census tract",
            "not_population_density": True,
            "qi_tier": "demographic_geo",
            "quintile_order": "1=lowest application volume, 5=highest",
        },
        "overall": overall.to_dict(orient="records"),
        "cohorts": rows.to_dict(orient="records"),
    }
    minimum_cell_size = load_qi_config("config/quasi_identifiers.yml").minimum_cell_size
    payload = enforce_minimum_cell(payload, minimum_cell_size=minimum_cell_size)
    args.output.parent.mkdir(parents=True, exist_ok=True)
    args.output.write_text(json.dumps(payload, indent=2) + "\n", encoding="utf-8")
    print(json.dumps(payload["metadata"], indent=2))


if __name__ == "__main__":
    main()
