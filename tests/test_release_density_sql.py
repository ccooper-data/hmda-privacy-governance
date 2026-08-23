from pathlib import Path


def test_release_density_is_labeled_and_ranked() -> None:
    sql = Path("models/gold/tract_release_density.sql").read_text().lower()
    assert "count(*) as application_count" in sql
    assert "ntile(5)" in sql


def test_density_risk_uses_demographic_tier_and_suppresses() -> None:
    sql = Path("models/gold/risk_by_release_density.sql").read_text().lower()
    assert "ref('qi_profile_demographic_geo')" in sql
    assert "ref('tract_release_density')" in sql
    assert "having sum(profile.k) >= 20" in sql

