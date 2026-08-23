from __future__ import annotations

from dataclasses import asdict, dataclass

import pandas as pd

from .config import QIConfig


@dataclass(frozen=True)
class RiskSummary:
    record_count: int
    equivalence_class_count: int
    sample_unique_records: int
    sample_uniqueness_rate: float
    records_k_lt_5: int
    records_k_lt_10: int
    prosecutor_expected_match_risk: float

    def to_dict(self) -> dict[str, int | float]:
        return asdict(self)


@dataclass(frozen=True)
class CohortRiskMetadata:
    equivalence_universe: str
    cohort_fields: tuple[str, ...]
    source_record_count: int
    published_cohort_count: int
    minimum_cell_size: int
    aggregate_only: bool = True

    def to_dict(self) -> dict[str, str | int | bool | tuple[str, ...]]:
        return asdict(self)


def validate_analysis_frame(frame: pd.DataFrame, config: QIConfig) -> None:
    missing = sorted(set(config.fields) - set(frame.columns))
    if missing:
        raise ValueError(f"Missing configured quasi-identifiers: {missing}")
    forbidden = sorted(set(config.forbidden_direct_identifiers) & set(frame.columns))
    if forbidden:
        raise ValueError(f"Input contains prohibited direct identifiers: {forbidden}")


def equivalence_classes(frame: pd.DataFrame, config: QIConfig) -> pd.DataFrame:
    """Return aggregate QI equivalence classes; never return source row identifiers."""
    validate_analysis_frame(frame, config)
    classes = (
        frame.groupby(list(config.fields), dropna=False, observed=True)
        .size()
        .rename("k")
        .reset_index()
    )
    return classes


def summarize_risk(frame: pd.DataFrame, config: QIConfig) -> RiskSummary:
    classes = equivalence_classes(frame, config)
    total = int(classes["k"].sum())
    unique_records = int(classes.loc[classes["k"] == 1, "k"].sum())
    k_lt_5 = int(classes.loc[classes["k"] < 5, "k"].sum())
    k_lt_10 = int(classes.loc[classes["k"] < 10, "k"].sum())
    # Record-weighted mean of 1/k equals number of classes divided by records.
    prosecutor_risk = float(len(classes) / total) if total else 0.0
    return RiskSummary(
        record_count=total,
        equivalence_class_count=len(classes),
        sample_unique_records=unique_records,
        sample_uniqueness_rate=float(unique_records / total) if total else 0.0,
        records_k_lt_5=k_lt_5,
        records_k_lt_10=k_lt_10,
        prosecutor_expected_match_risk=prosecutor_risk,
    )


def cohort_risk(
    frame: pd.DataFrame,
    config: QIConfig,
    cohort_fields: list[str],
) -> pd.DataFrame:
    """Aggregate risk by cohort and suppress cells below the configured minimum."""
    missing = sorted(set(cohort_fields) - set(frame.columns))
    if missing:
        raise ValueError(f"Missing cohort fields: {missing}")
    classes = equivalence_classes(frame, config)
    merged = frame[list(config.fields) + cohort_fields].merge(
        classes, on=list(config.fields), how="left", validate="many_to_one"
    )
    result = (
        merged.assign(is_unique=merged["k"].eq(1), prosecutor_risk=1 / merged["k"])
        .groupby(cohort_fields, dropna=False, observed=True)
        .agg(
            record_count=("k", "size"),
            sample_unique_rate=("is_unique", "mean"),
            prosecutor_expected_match_risk=("prosecutor_risk", "mean"),
        )
        .reset_index()
    )
    return result.loc[result["record_count"] >= config.minimum_cell_size].reset_index(drop=True)


def cohort_risk_report(
    frame: pd.DataFrame,
    config: QIConfig,
    cohort_fields: list[str],
    *,
    equivalence_universe: str,
) -> tuple[pd.DataFrame, CohortRiskMetadata]:
    """Compute k on the complete declared universe, then summarize by cohort."""
    allowed_universes = {"full_state_year", "full_national_year"}
    if equivalence_universe not in allowed_universes:
        raise ValueError(
            "equivalence_universe must be full_state_year or full_national_year; "
            "filtered cohorts are validation-only"
        )
    report = cohort_risk(frame, config, cohort_fields)
    metadata = CohortRiskMetadata(
        equivalence_universe=equivalence_universe,
        cohort_fields=tuple(cohort_fields),
        source_record_count=len(frame),
        published_cohort_count=len(report),
        minimum_cell_size=config.minimum_cell_size,
    )
    return report, metadata
