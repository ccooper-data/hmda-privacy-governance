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
    cross = connection.execute("select * from risk_by_density_cross order by 1, 2").fetchdf()
    audit = connection.execute(
        "select * from density_join_exclusion_audit order by dimension, join_status, record_count desc"
    ).fetchdf()
    association = connection.execute(
        """select corr(residential.residential_density_quintile,
                        release.release_density_quintile) as tract_quintile_correlation,
                  count(*) as matched_tracts
           from tract_residential_density as residential
           inner join tract_release_density as release using (census_tract)"""
    ).fetchone()
    minimum = load_qi_config("config/quasi_identifiers.yml").minimum_cell_size
    payload = {
        "metadata": {
            "aggregate_only": True,
            "minimum_cell_size": minimum,
            "residential_universe": "HMDA-active tracts with population and positive land area",
        },
        "density_association": {
            "tract_quintile_correlation": association[0],
            "matched_tracts": association[1],
        },
        "two_way_risk": cross.to_dict(orient="records"),
        "join_exclusion_audit": audit.to_dict(orient="records"),
    }
    payload = enforce_minimum_cell(payload, minimum_cell_size=minimum)
    args.output.parent.mkdir(parents=True, exist_ok=True)
    args.output.write_text(json.dumps(payload, indent=2) + "\n", encoding="utf-8")


if __name__ == "__main__":
    main()
