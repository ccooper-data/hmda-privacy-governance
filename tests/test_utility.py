from pathlib import Path
from statistics import NormalDist

import pandas as pd
import pytest

from hmda_privacy.utility import disparity_power_analysis, minimum_detectable_rate_disparity


def test_mde_decreases_with_larger_samples() -> None:
    small = minimum_detectable_rate_disparity(reference_n=100, comparison_n=100, baseline_rate=0.2)
    large = minimum_detectable_rate_disparity(
        reference_n=1_000, comparison_n=1_000, baseline_rate=0.2
    )
    assert large < small


def test_power_analysis_reports_percentage_points() -> None:
    frame = pd.DataFrame(
        {
            "race": ["reference"] * 50 + ["comparison"] * 50,
            "action": [3] * 10 + [1] * 40 + [3] * 15 + [1] * 35,
        }
    )
    result = disparity_power_analysis(
        frame,
        group_field="race",
        outcome_field="action",
        reference_group="reference",
        comparison_group="comparison",
    )
    assert result.reference_n == 50
    assert result.baseline_denial_rate == 0.2
    assert result.minimum_detectable_disparity_points > 0


def test_mde_rejects_invalid_baseline() -> None:
    with pytest.raises(ValueError, match="baseline_rate"):
        minimum_detectable_rate_disparity(reference_n=10, comparison_n=10, baseline_rate=0)


def test_sql_and_python_use_same_alpha_power_coefficient() -> None:
    coefficient = NormalDist().inv_cdf(0.975) + NormalDist().inv_cdf(0.80)
    sql = Path("models/gold/privacy_utility_frontier.sql").read_text(encoding="utf-8")
    assert "2.801585" in sql
    assert coefficient == pytest.approx(2.801585, abs=1e-6)
