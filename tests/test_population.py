import pandas as pd
import pytest

from hmda_privacy.config import QIConfig
from hmda_privacy.population import estimate_population_uniqueness_subsample


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

