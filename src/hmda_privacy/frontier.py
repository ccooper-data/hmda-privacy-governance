from __future__ import annotations

from dataclasses import asdict, dataclass

import pandas as pd

from .config import QIConfig
from .protection import ProtectionConfig, apply_protection
from .risk import summarize_risk
from .utility import disparity_power_analysis


@dataclass(frozen=True)
class FrontierPoint:
    configuration: str
    is_current_baseline: bool
    retained_records: int
    retained_share: float
    sample_uniqueness_rate: float
    prosecutor_expected_match_risk: float
    minimum_detectable_disparity_points: float

    def to_dict(self) -> dict[str, str | bool | int | float]:
        return asdict(self)


def build_privacy_utility_frontier(
    frame: pd.DataFrame,
    qi_config: QIConfig,
    protections: list[ProtectionConfig],
    *,
    current_baseline: str,
    group_field: str,
    outcome_field: str,
    reference_group: str,
    comparison_group: str,
) -> pd.DataFrame:
    """Evaluate aggregate risk and unadjusted disparity-detection power."""
    if current_baseline not in {item.name for item in protections}:
        raise ValueError("current_baseline must name a protection configuration")
    points: list[FrontierPoint] = []
    total = len(frame)
    for protection in protections:
        protected, transformed = apply_protection(frame, qi_config, protection)
        risk = summarize_risk(protected, transformed)
        utility = disparity_power_analysis(
            protected,
            group_field=group_field,
            outcome_field=outcome_field,
            reference_group=reference_group,
            comparison_group=comparison_group,
        )
        points.append(
            FrontierPoint(
                configuration=protection.name,
                is_current_baseline=protection.name == current_baseline,
                retained_records=len(protected),
                retained_share=len(protected) / total if total else 0.0,
                sample_uniqueness_rate=risk.sample_uniqueness_rate,
                prosecutor_expected_match_risk=risk.prosecutor_expected_match_risk,
                minimum_detectable_disparity_points=utility.minimum_detectable_disparity_points,
            )
        )
    return pd.DataFrame([point.to_dict() for point in points])

