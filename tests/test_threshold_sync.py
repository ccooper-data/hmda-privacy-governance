from pathlib import Path

import yaml

from hmda_privacy.config import load_qi_config


def test_dbt_threshold_matches_governance_config() -> None:
    dbt = yaml.safe_load(Path("dbt_project.yml").read_text(encoding="utf-8"))
    configured = load_qi_config("config/quasi_identifiers.yml").minimum_cell_size
    assert dbt["vars"]["minimum_cell_size"] == configured


def test_minimum_cell_sql_uses_dbt_variable() -> None:
    paths = [
        *Path("dbt_tests").glob("assert_*_minimum_cell.sql"),
        Path("models/gold/risk_by_release_density.sql"),
        Path("models/gold/risk_by_residential_density.sql"),
        Path("models/gold/risk_metrics_by_race.sql"),
        Path("models/gold/qi_sensitivity_by_race.sql"),
        Path("models/gold/risk_cohort_counts.sql"),
    ]
    assert paths
    for path in paths:
        assert "var('minimum_cell_size')" in path.read_text(encoding="utf-8")
