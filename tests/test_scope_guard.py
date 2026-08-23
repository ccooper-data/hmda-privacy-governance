from pathlib import Path

from hmda_privacy.scope_guard import analysis_scope_violations


def _project(tmp_path: Path, silver_sql: str, qi_sql: str) -> Path:
    silver = tmp_path / "models/silver"
    gold = tmp_path / "models/gold"
    silver.mkdir(parents=True)
    gold.mkdir(parents=True)
    (silver / "fct_application.sql").write_text(silver_sql, encoding="utf-8")
    (gold / "qi_profile.sql").write_text(qi_sql, encoding="utf-8")
    return tmp_path


def test_scope_gate_accepts_year_filter_and_full_universe_profile(tmp_path: Path) -> None:
    root = _project(
        tmp_path,
        "select * from source where activity_year between 2018 and 2025",
        "select derived_race, count(*) as k from fct_application group by derived_race",
    )
    assert analysis_scope_violations(root) == []


def test_scope_gate_rejects_demographic_universe_filter(tmp_path: Path) -> None:
    root = _project(
        tmp_path,
        "select * from source where derived_race = 'Black or African American'",
        "select derived_race, count(*) as k from fct_application group by derived_race",
    )
    assert {item.code for item in analysis_scope_violations(root)} == {
        "DEMOGRAPHIC_UNIVERSE_FILTER"
    }


def test_scope_gate_rejects_qi_completeness_filter(tmp_path: Path) -> None:
    root = _project(
        tmp_path,
        "select * from source where census_tract is not null",
        "select census_tract, count(*) as k from fct_application group by census_tract",
    )
    assert {item.code for item in analysis_scope_violations(root)} == {"QI_COMPLETENESS_FILTER"}
