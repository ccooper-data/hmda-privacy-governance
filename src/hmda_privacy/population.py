from __future__ import annotations

from dataclasses import asdict, dataclass
from math import lgamma

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


@dataclass(frozen=True)
class GammaPoissonUniquenessEstimate:
    method: str
    coverage_fraction: float
    observed_equivalence_classes: int
    sample_unique_records: int
    gamma_shape: float
    gamma_rate: float
    probability_sample_unique_is_population_unique: float
    estimated_population_unique_records: float
    log_likelihood: float
    assumption_status: str

    def to_dict(self) -> dict[str, str | int | float]:
        return asdict(self)


def _zt_negative_binomial_log_likelihood(
    log_shape: float,
    log_rate: float,
    sizes: np.ndarray,
    frequencies: np.ndarray,
    coverage_fraction: float,
) -> float:
    shape = float(np.exp(log_shape))
    rate = float(np.exp(log_rate))
    p_zero = (rate / (rate + coverage_fraction)) ** shape
    if not 0 <= p_zero < 1 or 1 - p_zero < 1e-14:
        return float("-inf")
    log_normalizer = np.log1p(-p_zero)
    total = 0.0
    for size, frequency in zip(sizes, frequencies, strict=True):
        log_probability = (
            lgamma(float(size) + shape)
            - lgamma(shape)
            - lgamma(float(size) + 1)
            + shape * np.log(rate / (rate + coverage_fraction))
            + float(size) * np.log(coverage_fraction / (rate + coverage_fraction))
            - log_normalizer
        )
        total += float(frequency) * log_probability
    return total


def estimate_population_uniqueness_gamma_poisson(
    equivalence_class_sizes: np.ndarray | pd.Series | list[int],
    *,
    coverage_fraction: float,
) -> GammaPoissonUniquenessEstimate:
    """Fit a zero-truncated gamma-Poisson cell model and estimate population uniques.

    The coverage fraction is a declared scenario, not inferred from HMDA. The model treats
    released and unreleased counts as independent Poisson thinnings of latent cell intensity.
    """
    if not 0 < coverage_fraction < 1:
        raise ValueError("coverage_fraction must be strictly between 0 and 1")
    values = np.asarray(equivalence_class_sizes, dtype=int)
    if len(values) < 2 or np.any(values < 1):
        raise ValueError("At least two positive equivalence-class sizes are required")
    sizes, frequencies = np.unique(values, return_counts=True)

    best = (float("-inf"), 0.0, 0.0)
    for log_shape in np.linspace(np.log(0.03), np.log(30.0), 28):
        for log_rate in np.linspace(np.log(0.01), np.log(100.0), 32):
            score = _zt_negative_binomial_log_likelihood(
                log_shape, log_rate, sizes, frequencies, coverage_fraction
            )
            if score > best[0]:
                best = (score, float(log_shape), float(log_rate))

    score, log_shape, log_rate = best
    step = 0.5
    for _ in range(80):
        improved = False
        for delta_shape, delta_rate in ((step, 0), (-step, 0), (0, step), (0, -step)):
            candidate_shape = log_shape + delta_shape
            candidate_rate = log_rate + delta_rate
            candidate = _zt_negative_binomial_log_likelihood(
                candidate_shape, candidate_rate, sizes, frequencies, coverage_fraction
            )
            if candidate > score:
                score, log_shape, log_rate = candidate, candidate_shape, candidate_rate
                improved = True
        if not improved:
            step /= 2
        if step < 1e-6:
            break

    shape = float(np.exp(log_shape))
    rate = float(np.exp(log_rate))
    population_unique_probability = float(
        ((rate + coverage_fraction) / (rate + 1.0)) ** (shape + 1.0)
    )
    sample_unique_records = int(frequencies[sizes == 1].sum()) if np.any(sizes == 1) else 0
    return GammaPoissonUniquenessEstimate(
        method="zero_truncated_gamma_poisson",
        coverage_fraction=coverage_fraction,
        observed_equivalence_classes=len(values),
        sample_unique_records=sample_unique_records,
        gamma_shape=shape,
        gamma_rate=rate,
        probability_sample_unique_is_population_unique=population_unique_probability,
        estimated_population_unique_records=sample_unique_records * population_unique_probability,
        log_likelihood=float(score),
        assumption_status="scenario_only_hmda_coverage_fraction_not_identified",
    )


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
