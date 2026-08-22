from __future__ import annotations

from dataclasses import dataclass

import numpy as np
import pandas as pd

from .config import QIConfig
from .risk import equivalence_classes, validate_analysis_frame


@dataclass(frozen=True)
class ProtectionConfig:
    name: str
    geography: str = "tract"
    income_band_width: int | None = None
    loan_amount_band_width: int | None = None
    suppress_k_below: int | None = None


def generalize_geography(series: pd.Series, level: str) -> pd.Series:
    tract = series.astype("string").str.replace(r"\.0$", "", regex=True).str.zfill(11)
    if level == "tract":
        return tract
    if level == "county":
        return tract.str.slice(0, 5)
    if level == "state":
        return tract.str.slice(0, 2)
    if level == "national":
        return pd.Series("US", index=series.index, dtype="string")
    raise ValueError(f"Unsupported geography level: {level}")


def generalize_numeric(series: pd.Series, width: int | None) -> pd.Series:
    numeric = pd.to_numeric(series, errors="coerce")
    if width is None:
        return numeric
    if width <= 0:
        raise ValueError("Band width must be positive")
    lower = np.floor(numeric / width) * width
    return lower.astype("Int64").astype("string") + "-" + (lower + width).astype("Int64").astype("string")


def apply_protection(
    frame: pd.DataFrame,
    qi_config: QIConfig,
    protection: ProtectionConfig,
) -> tuple[pd.DataFrame, QIConfig]:
    """Return a protected analytical copy and its transformed QI definition."""
    validate_analysis_frame(frame, qi_config)
    protected = frame.copy()
    fields = list(qi_config.fields)

    if "census_tract" in protected:
        protected["geography"] = generalize_geography(
            protected["census_tract"], protection.geography
        )
        fields[fields.index("census_tract")] = "geography"
    if "income" in protected:
        protected["income_generalized"] = generalize_numeric(
            protected["income"], protection.income_band_width
        )
        fields[fields.index("income")] = "income_generalized"
    if "loan_amount" in protected:
        protected["loan_amount_generalized"] = generalize_numeric(
            protected["loan_amount"], protection.loan_amount_band_width
        )
        fields[fields.index("loan_amount")] = "loan_amount_generalized"

    transformed = QIConfig(
        version=qi_config.version,
        name=f"{qi_config.name}:{protection.name}",
        fields=tuple(fields),
        forbidden_direct_identifiers=qi_config.forbidden_direct_identifiers,
        sensitive_attributes=qi_config.sensitive_attributes,
        minimum_cell_size=qi_config.minimum_cell_size,
        k_thresholds=qi_config.k_thresholds,
    )
    if protection.suppress_k_below is None:
        return protected, transformed
    if protection.suppress_k_below < 2:
        raise ValueError("Suppression threshold must be at least 2")
    classes = equivalence_classes(protected, transformed)
    safe = classes.loc[classes["k"] >= protection.suppress_k_below, list(transformed.fields)]
    protected = protected.merge(safe, on=list(transformed.fields), how="inner", validate="many_to_one")
    return protected, transformed

