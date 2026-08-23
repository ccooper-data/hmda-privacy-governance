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
    connection = duckdb.connect(str(args.database), read_only=True)
    rows = connection.execute(
        """select qi_tier, derived_race, derived_ethnicity, record_count,
                  sample_uniqueness_rate, share_records_k_lt_5,
                  prosecutor_expected_match_risk
           from qi_sensitivity_by_race
           order by qi_tier, record_count desc"""
    ).fetchdf()
    overall = connection.execute(
        """select qi_tier, sum(record_count) as record_count,
                  sum(record_count * sample_uniqueness_rate) / sum(record_count)
                      as sample_uniqueness_rate,
                  sum(record_count * prosecutor_expected_match_risk) / sum(record_count)
                      as prosecutor_expected_match_risk
           from qi_sensitivity_by_race
           group by qi_tier order by qi_tier"""
    ).fetchdf()
    payload = {
        "metadata": {
            "aggregate_only": True,
            "equivalence_universe": "full_state_year",
            "qi_tiers": {
                "demographic_geo": "tract + age + sex + race + ethnicity",
                "financial_context": "demographic_geo + income + loan/occupancy context",
                "institution_aware": "financial_context + lender LEI",
            },
        },
        "overall": overall.to_dict(orient="records"),
        "cohorts": rows.to_dict(orient="records"),
    }
    args.output.parent.mkdir(parents=True, exist_ok=True)
    args.output.write_text(json.dumps(payload, indent=2) + "\n", encoding="utf-8")
    print(json.dumps(payload["metadata"], indent=2))


if __name__ == "__main__":
    main()

