from __future__ import annotations

import re
from dataclasses import dataclass
from pathlib import Path

DEMOGRAPHIC_COLUMNS = {
    "derived_race",
    "derived_ethnicity",
    "applicant_race",
    "applicant_ethnicity",
    "applicant_sex",
}
QI_COLUMNS = {
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
}


@dataclass(frozen=True)
class ScopeViolation:
    path: str
    code: str
    detail: str


def _where_clauses(sql: str) -> list[str]:
    without_comments = re.sub(r"--.*?$|/\*.*?\*/", " ", sql, flags=re.MULTILINE | re.DOTALL)
    return re.findall(
        r"\bwhere\b(.*?)(?=\bgroup\s+by\b|\border\s+by\b|\bhaving\b|\bunion\b|$)",
        without_comments,
        flags=re.IGNORECASE | re.DOTALL,
    )


def analysis_scope_violations(root: str | Path) -> list[ScopeViolation]:
    root_path = Path(root)
    targets = [root_path / "models/silver/fct_application.sql"]
    targets.extend(sorted((root_path / "models/gold").glob("qi_profile*.sql")))
    violations: list[ScopeViolation] = []
    for path in targets:
        sql = path.read_text(encoding="utf-8")
        for clause in _where_clauses(sql):
            lowered = clause.lower()
            demographics = sorted(column for column in DEMOGRAPHIC_COLUMNS if column in lowered)
            if demographics:
                violations.append(
                    ScopeViolation(
                        str(path.relative_to(root_path)),
                        "DEMOGRAPHIC_UNIVERSE_FILTER",
                        ", ".join(demographics),
                    )
                )
            completeness = sorted(
                column
                for column in QI_COLUMNS
                if re.search(
                    rf"\b{re.escape(column)}\b\s+is\s+not\s+null|"
                    rf"\bcoalesce\s*\(\s*{re.escape(column)}\b|"
                    rf"\b{re.escape(column)}\b\s*(?:<>|!=)\s*''",
                    lowered,
                )
            )
            if completeness:
                violations.append(
                    ScopeViolation(
                        str(path.relative_to(root_path)),
                        "QI_COMPLETENESS_FILTER",
                        ", ".join(completeness),
                    )
                )
    return violations
