from __future__ import annotations

from dataclasses import asdict, dataclass
from statistics import NormalDist

import pandas as pd


@dataclass(frozen=True)
class DisparityPowerResult:
    reference_group: str
    comparison_group: str
    reference_n: int
    comparison_n: int
    baseline_denial_rate: float
    alpha: float
    power: float
    minimum_detectable_disparity_points: float

    def to_dict(self) -> dict[str, str | int | float]:
        return asdict(self)


def minimum_detectable_rate_disparity(
    *,
    reference_n: int,
    comparison_n: int,
    baseline_rate: float,
    alpha: float = 0.05,
    power: float = 0.80,
) -> float:
    """Normal-approximation MDE for a two-sided two-proportion comparison."""
    if reference_n < 2 or comparison_n < 2:
        raise ValueError("Each group must contain at least two observations")
    if not 0 < baseline_rate < 1:
        raise ValueError("baseline_rate must be strictly between 0 and 1")
    if not 0 < alpha < 1 or not 0 < power < 1:
        raise ValueError("alpha and power must be strictly between 0 and 1")
    normal = NormalDist()
    z_alpha = normal.inv_cdf(1 - alpha / 2)
    z_power = normal.inv_cdf(power)
    standard_error = (
        baseline_rate * (1 - baseline_rate) * (1 / reference_n + 1 / comparison_n)
    ) ** 0.5
    return float((z_alpha + z_power) * standard_error)


def disparity_power_analysis(
    frame: pd.DataFrame,
    *,
    group_field: str,
    outcome_field: str,
    reference_group: str,
    comparison_group: str,
    denied_values: tuple[int, ...] = (3, 7),
    alpha: float = 0.05,
    power: float = 0.80,
) -> DisparityPowerResult:
    missing = sorted({group_field, outcome_field} - set(frame.columns))
    if missing:
        raise ValueError(f"Missing power-analysis fields: {missing}")
    selected = frame.loc[frame[group_field].isin([reference_group, comparison_group])].copy()
    selected["_denied"] = selected[outcome_field].isin(denied_values).astype(int)
    counts = selected.groupby(group_field, observed=True)["_denied"].agg(["size", "mean"])
    if reference_group not in counts.index or comparison_group not in counts.index:
        raise ValueError("Both comparison groups must be present")
    reference_n = int(counts.loc[reference_group, "size"])
    comparison_n = int(counts.loc[comparison_group, "size"])
    baseline = float(counts.loc[reference_group, "mean"])
    mde = minimum_detectable_rate_disparity(
        reference_n=reference_n,
        comparison_n=comparison_n,
        baseline_rate=baseline,
        alpha=alpha,
        power=power,
    )
    return DisparityPowerResult(
        reference_group=reference_group,
        comparison_group=comparison_group,
        reference_n=reference_n,
        comparison_n=comparison_n,
        baseline_denial_rate=baseline,
        alpha=alpha,
        power=power,
        minimum_detectable_disparity_points=100 * mde,
    )

