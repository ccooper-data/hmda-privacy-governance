import pandas as pd

from hmda_privacy.config import QIConfig
from hmda_privacy.synthetic_linkage import (
    generate_synthetic_auxiliary,
    simulate_synthetic_linkage,
)


def config() -> QIConfig:
    return QIConfig(1, "test", ("tract", "age"), ("uli",), (), 2, (1, 5, 10))


def test_synthetic_generator_contains_qis_only() -> None:
    frame = pd.DataFrame(
        {"tract": ["1", "1", "2"], "age": [20, 20, 30], "secret": ["x", "y", "z"]}
    )
    synthetic = generate_synthetic_auxiliary(frame, config(), records=25, random_seed=4)
    assert list(synthetic) == ["tract", "age"]
    assert len(synthetic) == 25


def test_linkage_returns_aggregate_summary_only() -> None:
    frame = pd.DataFrame({"tract": ["1", "1", "2"], "age": [20, 20, 30]})
    summary = simulate_synthetic_linkage(frame, config(), synthetic_records=100, random_seed=5)
    assert summary.synthetic_records == 100
    assert 0 <= summary.exact_match_rate <= 1
    assert 0 <= summary.expected_correct_match_rate <= 1
    assert set(summary.to_dict()) == {
        "method",
        "synthetic_records",
        "exact_match_records",
        "exact_match_rate",
        "unique_match_records",
        "unique_match_rate",
        "expected_correct_matches",
        "expected_correct_match_rate",
        "random_seed",
    }

