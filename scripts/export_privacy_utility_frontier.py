from __future__ import annotations

import argparse
import json
import math
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
            "select * from privacy_utility_frontier "
            "order by pre_suppression_uniqueness_rate desc"
        )
        .fetchdf()
    )
    records = rows.to_dict(orient="records")
    for record in records:
        for key, value in list(record.items()):
            if isinstance(value, float) and not math.isfinite(value):
                record[key] = None
        record["utility_status"] = (
            "estimated"
            if record.get("minimum_detectable_disparity_points") is not None
            else "insufficient_protected_cohort_retention"
        )
    payload = {
        "metadata": {
            "aggregate_only": True,
            "alpha": 0.05,
            "power": 0.80,
            "utility_metric": "decision-only two-proportion MDE for each declared release state",
            "limitations": "Adjusted fair-lending model remains required for final determination",
        },
        "frontier": records,
    }
    minimum_cell_size = load_qi_config("config/quasi_identifiers.yml").minimum_cell_size
    payload = enforce_minimum_cell(payload, minimum_cell_size=minimum_cell_size)
    args.output.parent.mkdir(parents=True, exist_ok=True)
    args.output.write_text(json.dumps(payload, indent=2) + "\n", encoding="utf-8")
    print(json.dumps(payload, indent=2))


if __name__ == "__main__":
    main()
