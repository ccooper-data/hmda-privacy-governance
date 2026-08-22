from __future__ import annotations

import re
from dataclasses import dataclass
from pathlib import Path

import yaml


@dataclass(frozen=True)
class DbtClassificationViolation:
    code: str
    model: str
    column: str


def declared_dbt_columns(schema_path: str | Path) -> dict[str, dict[str, str | None]]:
    schema = yaml.safe_load(Path(schema_path).read_text(encoding="utf-8"))
    result: dict[str, dict[str, str | None]] = {}
    for model in schema.get("models", []):
        result[model["name"]] = {
            column["name"]: column.get("meta", {}).get("classification")
            for column in model.get("columns", [])
        }
    return result


def selected_sql_columns(sql: str) -> list[str]:
    """Parse this project's simple explicit SELECT lists for drift checking."""
    match = re.search(r"\bselect\b(.*?)\bfrom\b", sql, flags=re.IGNORECASE | re.DOTALL)
    if not match:
        raise ValueError("SQL must contain an explicit SELECT ... FROM block")
    columns: list[str] = []
    for expression in match.group(1).split(","):
        cleaned = expression.strip()
        alias = re.search(r"\bas\s+([a-zA-Z_][\w]*)\s*$", cleaned, flags=re.IGNORECASE)
        if alias:
            columns.append(alias.group(1))
        else:
            name = cleaned.split()[-1].split(".")[-1]
            if not re.fullmatch(r"[a-zA-Z_][\w]*", name):
                raise ValueError(f"Selected expression requires an explicit alias: {cleaned}")
            columns.append(name)
    return columns


def check_dbt_classification_drift(
    *,
    models_dir: str | Path,
    schema_path: str | Path,
    allowed: set[str],
) -> list[DbtClassificationViolation]:
    declared = declared_dbt_columns(schema_path)
    violations: list[DbtClassificationViolation] = []
    for path in sorted(Path(models_dir).rglob("*.sql")):
        model = path.stem
        actual = selected_sql_columns(path.read_text(encoding="utf-8"))
        model_declarations = declared.get(model, {})
        for column in actual:
            classification = model_declarations.get(column)
            if classification is None:
                violations.append(DbtClassificationViolation("UNCLASSIFIED_COLUMN", model, column))
            elif classification not in allowed:
                violations.append(DbtClassificationViolation("INVALID_CLASSIFICATION", model, column))
    return violations

