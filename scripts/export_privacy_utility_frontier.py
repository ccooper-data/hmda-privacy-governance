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
        "select * from privacy_utility_frontier order by sample_uniqueness_rate desc"
    ).fetchdf()
    payload = {
        "metadata": {
            "aggregate_only": True,
            "alpha": 0.05,
            "power": 0.80,
            "utility_metric": "unadjusted two-proportion MDE after k>=5 suppression",
            "limitations": "Adjusted fair-lending model remains required for final determination",
        },
        "frontier": rows.to_dict(orient="records"),
    }
    args.output.parent.mkdir(parents=True, exist_ok=True)
    args.output.write_text(json.dumps(payload, indent=2) + "\n", encoding="utf-8")
    print(json.dumps(payload, indent=2))


if __name__ == "__main__":
    main()

