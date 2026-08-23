from __future__ import annotations

import argparse
import json
from pathlib import Path

import duckdb


def main() -> None:
    parser = argparse.ArgumentParser()
    parser.add_argument("--database", type=Path, default=Path("data/hmda_privacy.duckdb"))
    parser.add_argument("--output", type=Path, required=True)
    args = parser.parse_args()
    rows = duckdb.connect(str(args.database), read_only=True).execute(
        "select * from risk_by_residential_density "
        "order by residential_density_quintile, derived_race, derived_ethnicity"
    ).fetchdf()
    payload = {
        "metadata": {
            "aggregate_only": True,
            "minimum_cell_size": 20,
            "density_definition": "HMDA tract_population divided by Census Gazetteer land square miles",
            "quintile_order": "1 is lowest residential density; 5 is highest",
            "risk_qi_tier": "demographic_geo",
        },
        "cohorts": rows.to_dict(orient="records"),
    }
    args.output.parent.mkdir(parents=True, exist_ok=True)
    args.output.write_text(json.dumps(payload, indent=2, allow_nan=False) + "\n", encoding="utf-8")
    print(json.dumps(payload, indent=2, allow_nan=False))


if __name__ == "__main__":
    main()
