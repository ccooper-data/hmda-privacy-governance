from pathlib import Path


def test_qi_tiers_are_nested_and_lei_is_incremental() -> None:
    demographic = Path("models/gold/qi_profile_demographic_geo.sql").read_text().lower()
    financial = Path("models/gold/qi_profile_financial_context.sql").read_text().lower()
    institution = Path("models/gold/qi_profile.sql").read_text().lower()
    common = {"census_tract", "applicant_age", "applicant_sex", "derived_race", "derived_ethnicity"}
    assert all(field in demographic for field in common)
    assert all(field in financial for field in common)
    assert "loan_amount" in financial and "income" in financial
    assert "lei" not in demographic
    assert "lei" not in financial
    assert "lei" in institution


def test_sensitivity_mart_weights_class_sizes() -> None:
    sql = Path("models/gold/qi_sensitivity_by_race.sql").read_text().lower()
    assert "sum(k)" in sql
    assert "count(*) * 1.0 / sum(k)" in sql
    assert "having sum(k) >= {{ var('minimum_cell_size') }}" in sql
