from __future__ import annotations

import numpy as np
import pandas as pd

from .config import QIConfig
from .risk import validate_analysis_frame


def equivalence_class_diversity(
    frame: pd.DataFrame,
    config: QIConfig,
    *,
    sensitive_attribute: str,
) -> pd.DataFrame:
    """Return aggregate equivalence-class k, distinct-l, and total-variation t."""
    validate_analysis_frame(frame, config)
    if sensitive_attribute not in frame:
        raise ValueError(f"Missing sensitive attribute: {sensitive_attribute}")

    global_distribution = frame[sensitive_attribute].value_counts(normalize=True, dropna=False)
    rows: list[dict[str, object]] = []
    grouped = frame.groupby(list(config.fields), dropna=False, observed=True)
    for key, group in grouped:
        values = group[sensitive_attribute].value_counts(normalize=True, dropna=False)
        support = global_distribution.index.union(values.index)
        t_distance = (
            0.5
            * np.abs(
                values.reindex(support, fill_value=0)
                - global_distribution.reindex(support, fill_value=0)
            ).sum()
        )
        keys = key if isinstance(key, tuple) else (key,)
        row = dict(zip(config.fields, keys, strict=True))
        row.update(
            {
                "k": len(group),
                "l_distinct": int(group[sensitive_attribute].nunique(dropna=False)),
                "t_total_variation": float(t_distance),
            }
        )
        rows.append(row)
    classes = pd.DataFrame(rows)
    if classes.empty:
        return classes
    return classes.loc[classes["k"] >= config.minimum_cell_size].reset_index(drop=True)


def summarize_diversity(
    classes: pd.DataFrame,
    *,
    l_threshold: int = 2,
    t_threshold: float = 0.2,
) -> dict[str, int | float]:
    if not 0 <= t_threshold <= 1:
        raise ValueError("t_threshold must be between 0 and 1")
    records = int(classes["k"].sum())
    failing_l = int(classes.loc[classes["l_distinct"] < l_threshold, "k"].sum())
    failing_t = int(classes.loc[classes["t_total_variation"] > t_threshold, "k"].sum())
    return {
        "records": records,
        "l_threshold": l_threshold,
        "records_failing_l_diversity": failing_l,
        "share_failing_l_diversity": failing_l / records if records else 0.0,
        "t_threshold": t_threshold,
        "records_failing_t_closeness": failing_t,
        "share_failing_t_closeness": failing_t / records if records else 0.0,
    }
