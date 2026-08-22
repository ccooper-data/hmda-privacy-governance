from __future__ import annotations

from dataclasses import dataclass
from datetime import UTC, date, datetime
from pathlib import Path

import yaml


@dataclass(frozen=True)
class GovernanceViolation:
    code: str
    model: str
    column: str | None
    message: str


def load_yaml(path: str | Path) -> dict:
    return yaml.safe_load(Path(path).read_text(encoding="utf-8"))


def validate_governance_policy(
    policy: dict,
    actual_models: dict[str, list[str]],
    *,
    exceptions: dict | None = None,
    as_of: date | None = None,
) -> list[GovernanceViolation]:
    """Validate classifications and publication restrictions as a CI gate."""
    allowed = set(policy["allowed_classifications"])
    restricted = set(policy["restricted_in_published_marts"])
    declared_models = policy["published_marts"]
    effective_date = as_of or datetime.now(UTC).date()
    active_exceptions = _active_exceptions(exceptions or {"exceptions": []}, effective_date)
    violations: list[GovernanceViolation] = []

    for model, actual_columns in actual_models.items():
        declarations = declared_models.get(model, {}).get("columns", {})
        for column in actual_columns:
            classification = declarations.get(column)
            if classification is None:
                violation = GovernanceViolation(
                    "UNCLASSIFIED_COLUMN", model, column, "Published column has no classification"
                )
            elif classification not in allowed:
                violation = GovernanceViolation(
                    "INVALID_CLASSIFICATION",
                    model,
                    column,
                    f"Unsupported classification: {classification}",
                )
            elif classification in restricted:
                violation = GovernanceViolation(
                    "RESTRICTED_PUBLICATION",
                    model,
                    column,
                    f"{classification} column cannot reach a published mart",
                )
            else:
                continue
            if (violation.code, model, column) not in active_exceptions:
                violations.append(violation)
    return violations


def _active_exceptions(register: dict, as_of: date) -> set[tuple[str, str, str | None]]:
    active: set[tuple[str, str, str | None]] = set()
    for item in register.get("exceptions", []):
        required = {"id", "code", "model", "owner", "reason", "expires_on"}
        missing = required - set(item)
        if missing:
            raise ValueError(f"Exception is missing required fields: {sorted(missing)}")
        expiry = date.fromisoformat(str(item["expires_on"]))
        if expiry >= as_of:
            active.add((item["code"], item["model"], item.get("column")))
    return active


def validate_retention(
    *,
    created_at: datetime,
    retention_days: int,
    as_of: datetime | None = None,
) -> bool:
    if retention_days < 1:
        raise ValueError("retention_days must be positive")
    now = as_of or datetime.now(UTC)
    if created_at.tzinfo is None or now.tzinfo is None:
        raise ValueError("Retention timestamps must be timezone-aware")
    return (now - created_at).days <= retention_days
