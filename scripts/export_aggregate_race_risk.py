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
    rows = (
        duckdb.connect(str(args.database), read_only=True)
        .execute(
            """select equivalence_universe, derived_race, derived_ethnicity,
                  record_count, sample_uniqueness_rate, share_records_k_lt_5,
                  share_records_k_lt_10, prosecutor_expected_match_risk
           from risk_metrics_by_race
           order by record_count desc"""
        )
        .fetchdf()
    )
    minimum_cell_size = load_qi_config("config/quasi_identifiers.yml").minimum_cell_size
    payload = {
        "metadata": {
            "aggregate_only": True,
            "equivalence_universe": "full_state_year",
            "minimum_cell_size": minimum_cell_size,
        },
        "cohorts": rows.to_dict(orient="records"),
    }
    payload = enforce_minimum_cell(payload, minimum_cell_size=minimum_cell_size)
    args.output.parent.mkdir(parents=True, exist_ok=True)
    args.output.write_text(json.dumps(payload, indent=2) + "\n", encoding="utf-8")
    print(json.dumps(payload["metadata"], indent=2))


if __name__ == "__main__":
    main()
