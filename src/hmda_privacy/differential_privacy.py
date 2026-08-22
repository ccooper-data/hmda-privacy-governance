from __future__ import annotations

from dataclasses import asdict, dataclass

import numpy as np
import pandas as pd


@dataclass(frozen=True)
class DPAggregateMetadata:
    mechanism: str
    epsilon: float
    sensitivity: float
    random_seed: int
    postprocessing: str

    def to_dict(self) -> dict[str, str | int | float]:
        return asdict(self)


def dp_group_counts(
    frame: pd.DataFrame,
    *,
    group_fields: list[str],
    epsilon: float,
    sensitivity: float = 1.0,
    random_seed: int = 20260822,
) -> tuple[pd.DataFrame, DPAggregateMetadata]:
    """Release non-negative group counts with the Laplace mechanism.

    This provides event-level epsilon-DP only when each person contributes to at most
    one row. A production release must enforce or bound person-level contribution.
    """
    if epsilon <= 0:
        raise ValueError("epsilon must be positive")
    if sensitivity <= 0:
        raise ValueError("sensitivity must be positive")
    missing = sorted(set(group_fields) - set(frame.columns))
    if missing:
        raise ValueError(f"Missing group fields: {missing}")
    counts = (
        frame.groupby(group_fields, dropna=False, observed=True)
        .size()
        .rename("true_count")
        .reset_index()
    )
    rng = np.random.default_rng(random_seed)
    noise = rng.laplace(loc=0.0, scale=sensitivity / epsilon, size=len(counts))
    counts["dp_count"] = np.maximum(0, np.rint(counts["true_count"] + noise)).astype(int)
    public = counts[group_fields + ["dp_count"]]
    metadata = DPAggregateMetadata(
        mechanism="laplace",
        epsilon=epsilon,
        sensitivity=sensitivity,
        random_seed=random_seed,
        postprocessing="rounded_to_integer_and_clamped_at_zero",
    )
    return public, metadata

