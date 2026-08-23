import numpy as np
import pandas as pd
import pytest

from hmda_privacy.config import QIConfig
from hmda_privacy.population import (
    estimate_population_uniqueness_gamma_poisson,
    estimate_population_uniqueness_subsample,
)


def config() -> QIConfig:
    return QIConfig(1, "test", ("tract", "age"), ("uli",), (), 2, (1, 5, 10))


def test_population_proxy_is_reproducible_and_bounded() -> None:
    frame = pd.DataFrame(
        {"tract": ["1", "1", "2", "3", "4", "5"], "age": [20, 20, 30, 40, 50, 60]}
    )
    first = estimate_population_uniqueness_subsample(
        frame, config(), sample_fraction=0.5, replicates=50, random_seed=7
    )
    second = estimate_population_uniqueness_subsample(
        frame, config(), sample_fraction=0.5, replicates=50, random_seed=7
    )
    assert first == second
    assert 0 <= first.estimated_share_sample_uniques_population_unique <= 1
    assert first.sample_unique_records == 4


def test_population_proxy_rejects_invalid_fraction() -> None:
    frame = pd.DataFrame({"tract": ["1", "2"], "age": [20, 30]})
    with pytest.raises(ValueError, match="strictly between"):
        estimate_population_uniqueness_subsample(frame, config(), sample_fraction=1)


def test_gamma_poisson_estimator_is_bounded_and_coverage_sensitive() -> None:
    sizes = [1] * 100 + [2] * 40 + [3] * 20 + [4] * 10
    low = estimate_population_uniqueness_gamma_poisson(sizes, coverage_fraction=0.1)
    high = estimate_population_uniqueness_gamma_poisson(sizes, coverage_fraction=0.5)
    assert 0 <= low.probability_sample_unique_is_population_unique <= 1
    assert 0 <= high.probability_sample_unique_is_population_unique <= 1
    assert high.probability_sample_unique_is_population_unique > low.probability_sample_unique_is_population_unique
    assert high.sample_unique_records == 100
    assert high.fit_status == "estimated"


def test_gamma_poisson_estimator_rejects_invalid_classes() -> None:
    with pytest.raises(ValueError, match="positive equivalence"):
        estimate_population_uniqueness_gamma_poisson([0, 1], coverage_fraction=0.5)


def test_gamma_poisson_recovers_known_synthetic_population_risk() -> None:
    rng = np.random.default_rng(19)
    coverage = 0.25
    intensity = rng.gamma(shape=0.7, scale=1 / 0.35, size=30_000)
    released = rng.poisson(coverage * intensity)
    unreleased = rng.poisson((1 - coverage) * intensity)
    observed = released > 0
    true_probability = float(
        ((released == 1) & (unreleased == 0)).sum() / (released == 1).sum()
    )
    estimate = estimate_population_uniqueness_gamma_poisson(
        released[observed], coverage_fraction=coverage
    )
    assert abs(estimate.probability_sample_unique_is_population_unique - true_probability) < 0.04


def test_gamma_poisson_rejects_boundary_fit_as_not_reportable() -> None:
    estimate = estimate_population_uniqueness_gamma_poisson(
        [1] * 10_000 + [10] * 100, coverage_fraction=0.25
    )
    assert estimate.fit_status == "boundary_fit_not_reportable"
    assert estimate.probability_sample_unique_is_population_unique is None
