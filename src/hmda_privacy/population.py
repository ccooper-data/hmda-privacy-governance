from __future__ import annotations

from dataclasses import asdict, dataclass

import numpy as np
import pandas as pd

from .config import QIConfig
from .risk import equivalence_classes, validate_analysis_frame


@dataclass(frozen=True)
class PopulationUniquenessEstimate:
    method: str
    sample_fraction: float
    sample_unique_records: int
    estimated_population_unique_records: float
    estimated_share_sample_uniques_population_unique: float
    bootstrap_standard_error: float
    interval_low: float
    interval_high: float
    replicates: int
    random_seed: int

    def to_dict(self) -> dict[str, str | int | float]:
        return asdict(self)


def _unique_keys(frame: pd.DataFrame, fields: tuple[str, ...]) -> pd.MultiIndex:
    counts = frame.groupby(list(fields), dropna=False, observed=True).size()
    return counts[counts == 1].index


def estimate_population_uniqueness_subsample(
    frame: pd.DataFrame,
    config: QIConfig,
    *,
    sample_fraction: float,
    replicates: int = 200,
    random_seed: int = 20260822,
) -> PopulationUniquenessEstimate:
    """Estimate Pr(population unique | sample unique) by repeated subsampling.

    The sample is treated as a proxy population. Each replicate draws from it at the
    supplied original sampling fraction. The share of replicate uniques that are also
    unique in the full sample proxies the share of released-file uniques that are unique
    in the target population. This estimator is diagnostic and assumption-sensitive; it
    is not presented as a Zayatz or Pitman implementation.
    """
    validate_analysis_frame(frame, config)
    if not 0 < sample_fraction < 1:
        raise ValueError("sample_fraction must be strictly between 0 and 1")
    if replicates < 30:
        raise ValueError("At least 30 replicates are required")
    if len(frame) < 2:
        raise ValueError("At least two records are required")

    sample_unique_count = int((equivalence_classes(frame, config)["k"] == 1).sum())
    full_unique_keys = _unique_keys(frame, config.fields)
    draw_size = max(1, round(len(frame) * sample_fraction))
    rng = np.random.default_rng(random_seed)
    estimates: list[float] = []

    for _ in range(replicates):
        indices = rng.choice(len(frame), size=draw_size, replace=False)
        draw = frame.iloc[indices]
        draw_unique_keys = _unique_keys(draw, config.fields)
        if len(draw_unique_keys) == 0:
            continue
        also_full_unique = draw_unique_keys.isin(full_unique_keys).sum()
        estimates.append(float(also_full_unique / len(draw_unique_keys)))

    if len(estimates) < 30:
        raise ValueError("Too few usable replicates; QI set produced no stable unique classes")

    values = np.asarray(estimates)
    proportion = float(values.mean())
    low, high = np.quantile(values, [0.025, 0.975])
    return PopulationUniquenessEstimate(
        method="repeated_subsampling_proxy",
        sample_fraction=sample_fraction,
        sample_unique_records=sample_unique_count,
        estimated_population_unique_records=float(sample_unique_count * proportion),
        estimated_share_sample_uniques_population_unique=proportion,
        bootstrap_standard_error=float(values.std(ddof=1)),
        interval_low=float(low),
        interval_high=float(high),
        replicates=len(estimates),
        random_seed=random_seed,
    )

