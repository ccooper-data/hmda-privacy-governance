from __future__ import annotations

from dataclasses import asdict, dataclass
from datetime import UTC, datetime

import pandas as pd


@dataclass(frozen=True)
class SubjectRightsAudit:
    subject_key: str
    action: str
    tables_touched: tuple[str, ...]
    records_affected: int
    occurred_at_utc: str
    control_cohort_only: bool = True

    def to_dict(self) -> dict[str, str | int | bool | tuple[str, ...]]:
        return asdict(self)


def export_synthetic_subject(
    tables: dict[str, pd.DataFrame],
    *,
    subject_key: str,
    key_column: str = "synthetic_subject_key",
) -> tuple[dict[str, pd.DataFrame], SubjectRightsAudit]:
    exports: dict[str, pd.DataFrame] = {}
    count = 0
    for name, table in tables.items():
        if key_column not in table:
            continue
        matched = table.loc[table[key_column].eq(subject_key)].copy()
        if not matched.empty:
            exports[name] = matched
            count += len(matched)
    audit = SubjectRightsAudit(
        subject_key=subject_key,
        action="export",
        tables_touched=tuple(sorted(exports)),
        records_affected=count,
        occurred_at_utc=datetime.now(UTC).isoformat(),
    )
    return exports, audit


def delete_synthetic_subject(
    tables: dict[str, pd.DataFrame],
    *,
    subject_key: str,
    key_column: str = "synthetic_subject_key",
) -> tuple[dict[str, pd.DataFrame], SubjectRightsAudit]:
    updated: dict[str, pd.DataFrame] = {}
    touched: list[str] = []
    count = 0
    for name, table in tables.items():
        if key_column not in table:
            updated[name] = table.copy()
            continue
        mask = table[key_column].eq(subject_key)
        affected = int(mask.sum())
        if affected:
            touched.append(name)
            count += affected
        updated[name] = table.loc[~mask].copy()
    audit = SubjectRightsAudit(
        subject_key=subject_key,
        action="delete",
        tables_touched=tuple(sorted(touched)),
        records_affected=count,
        occurred_at_utc=datetime.now(UTC).isoformat(),
    )
    return updated, audit

