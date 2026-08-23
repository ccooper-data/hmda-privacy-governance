from __future__ import annotations

import argparse
import json
from pathlib import Path

import duckdb

from hmda_privacy.adjusted_utility import adjusted_denial_disparity


def main() -> None:
    parser = argparse.ArgumentParser()
    parser.add_argument("--database", type=Path, default=Path("data/hmda_privacy.duckdb"))
    parser.add_argument("--output", type=Path, required=True)
    args = parser.parse_args()

    connection = duckdb.connect(str(args.database), read_only=True)
    configurations = ["cfpb_current", "county_geo", "county_banded", "state_banded"]
    results = []
    for configuration in configurations:
        frame = connection.execute(
            "select * exclude (configuration) from fair_lending_modeling_cohort "
            "where configuration = ?",
            [configuration],
        ).fetchdf()
        result = adjusted_denial_disparity(frame).to_dict()
        result["configuration"] = configuration
        results.append(result)

    payload = {
        "metadata": {
            "aggregate_only": True,
            "outcome": "denial among action_taken 1, 2, 3, or 7; denials are 3 or 7",
            "comparison": "Black non-Hispanic versus White non-Hispanic",
            "protection_order": "configuration-specific transformation and k>=5 retention precede fitting",
            "model": "logistic IRLS adjusted for disclosed borrower and loan characteristics",
            "interpretation": "descriptive disparity model; not causal evidence of discrimination",
        },
        "configurations": results,
    }
    args.output.parent.mkdir(parents=True, exist_ok=True)
    args.output.write_text(json.dumps(payload, indent=2, allow_nan=False) + "\n", encoding="utf-8")
    print(json.dumps(payload, indent=2, allow_nan=False))


if __name__ == "__main__":
    main()
