import numpy as np
import pandas as pd

from hmda_privacy.adjusted_utility import adjusted_denial_disparity


def test_adjusted_model_estimates_positive_group_disparity() -> None:
    rng = np.random.default_rng(42)
    rows = 1500
    is_black = rng.integers(0, 2, rows)
    income = rng.lognormal(11, 0.4, rows)
    logits = -1.8 + 0.65 * is_black - 0.25 * (np.log(income) - 11)
    denied = rng.binomial(1, 1 / (1 + np.exp(-logits)))
    frame = pd.DataFrame(
        {
            "is_black": is_black,
            "is_denied": denied,
            "protected_income": income,
            "protected_loan_amount": rng.lognormal(12.5, 0.3, rows),
            "applicant_age": rng.choice(["35-44", "45-54"], rows),
            "loan_type": rng.choice(["1", "2"], rows),
        }
    )
    result = adjusted_denial_disparity(frame)
    assert result.converged
    assert result.adjusted_odds_ratio is not None
    assert result.adjusted_odds_ratio > 1
    assert result.odds_ratio_ci_low < result.adjusted_odds_ratio < result.odds_ratio_ci_high


def test_adjusted_model_reports_nonestimable_empty_group() -> None:
    frame = pd.DataFrame(
        {
            "is_black": [0, 0],
            "is_denied": [0, 1],
            "protected_income": [1, 2],
            "protected_loan_amount": [1, 2],
        }
    )
    result = adjusted_denial_disparity(frame)
    assert result.status == "insufficient_retained_comparison"
    assert result.adjusted_odds_ratio is None
