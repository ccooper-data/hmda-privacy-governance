from pathlib import Path


def test_protection_sweep_has_current_and_generalized_configurations() -> None:
    sql = Path("models/gold/protection_equivalence_classes.sql").read_text().lower()
    for name in ("cfpb_current", "county_geo", "county_banded", "state_banded"):
        assert name in sql
    assert "floor(income / 25000)" in sql
    assert "floor(loan_amount / 100000)" in sql


def test_frontier_marks_baseline_and_reports_mde() -> None:
    sql = Path("models/gold/privacy_utility_frontier.sql").read_text().lower()
    assert "is_current_baseline" in sql
    assert "retained_share_k5" in sql
    assert "minimum_detectable_disparity_points_k5" in sql
    assert "utility_estimable_k5" in sql
    assert "2.801585" in sql
