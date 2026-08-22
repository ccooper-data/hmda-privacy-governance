from pathlib import Path

from hmda_privacy.dbt_governance import (
    check_dbt_classification_drift,
    selected_sql_columns,
)


def test_explicit_select_parser_handles_aliases() -> None:
    sql = "select activity_year, count(*) as record_count from source group by 1"
    assert selected_sql_columns(sql) == ["activity_year", "record_count"]


def test_new_unclassified_column_fails(tmp_path: Path) -> None:
    models = tmp_path / "models"
    models.mkdir()
    (models / "example.sql").write_text("select known, new_column from source", encoding="utf-8")
    schema = models / "schema.yml"
    schema.write_text(
        """version: 2
models:
  - name: example
    columns:
      - name: known
        meta: {classification: public}
""",
        encoding="utf-8",
    )
    violations = check_dbt_classification_drift(
        models_dir=models,
        schema_path=schema,
        allowed={"public", "internal", "quasi_identifier", "sensitive"},
    )
    assert [(item.code, item.column) for item in violations] == [
        ("UNCLASSIFIED_COLUMN", "new_column")
    ]

