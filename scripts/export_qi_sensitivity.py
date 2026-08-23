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
        """select qi_tier, derived_race, derived_ethnicity, record_count,
                  sample_uniqueness_rate, share_records_k_lt_5,
                  prosecutor_expected_match_risk
           from qi_sensitivity_by_race
           order by qi_tier, record_count desc"""
    ).fetchdf()
    overall = connection.execute(
        """with profiles as (
               select 'demographic_geo' as qi_tier, k from qi_profile_demographic_geo
               union all
               select 'financial_context', k from qi_profile_financial_context
               union all
               select 'institution_aware', k from qi_profile
           )
           select qi_tier, sum(k) as record_count,
                  sum(case when k = 1 then 1 else 0 end) / sum(k)
                      as sample_uniqueness_rate,
                  count(*) / sum(k) as prosecutor_expected_match_risk
           from profiles
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
    minimum_cell_size = load_qi_config("config/quasi_identifiers.yml").minimum_cell_size
    payload = enforce_minimum_cell(payload, minimum_cell_size=minimum_cell_size)
    args.output.parent.mkdir(parents=True, exist_ok=True)
    args.output.write_text(json.dumps(payload, indent=2) + "\n", encoding="utf-8")
    print(json.dumps(payload["metadata"], indent=2))


if __name__ == "__main__":
    main()
