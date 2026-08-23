from pathlib import Path


def test_race_risk_is_scored_before_grouping() -> None:
    sql = Path("models/gold/risk_metrics_by_race.sql").read_text(encoding="utf-8").lower()
    assert "ref('fct_application')" in sql
    assert "ref('qi_profile')" in sql
    assert "is not distinct from" in sql
    assert "having count(*) >= {{ var('minimum_cell_size') }}" in sql
    assert "'full_state_year' as equivalence_universe" in sql


def test_qi_profile_uses_configured_qi_fields() -> None:
    sql = Path("models/gold/qi_profile.sql").read_text(encoding="utf-8").lower()
    for field in (
        "census_tract",
        "applicant_age",
        "applicant_sex",
        "derived_race",
        "derived_ethnicity",
        "income",
        "loan_amount",
        "loan_purpose",
        "occupancy_type",
        "lien_status",
        "derived_dwelling_category",
        "lei",
    ):
        assert field in sql
