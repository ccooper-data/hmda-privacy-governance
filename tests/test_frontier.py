import pandas as pd

from hmda_privacy.config import QIConfig
from hmda_privacy.frontier import build_privacy_utility_frontier
from hmda_privacy.protection import ProtectionConfig


def test_frontier_marks_current_position_and_quantifies_tradeoff() -> None:
    rows = []
    for index in range(100):
        rows.append(
            {
                "census_tract": f"48{201 + index % 2:03d}{index % 10:06d}",
                "income": 50_000 + (index % 4) * 10_000,
                "loan_amount": 200_000 + (index % 3) * 10_000,
                "race": "reference" if index < 50 else "comparison",
                "action": 3 if index % 5 == 0 else 1,
            }
        )
    frame = pd.DataFrame(rows)
    config = QIConfig(
        1,
        "test",
        ("census_tract", "income", "loan_amount"),
        (),
        ("action",),
        2,
        (1, 5, 10),
    )
    frontier = build_privacy_utility_frontier(
        frame,
        config,
        [
            ProtectionConfig("cfpb_current"),
            ProtectionConfig("county", geography="county"),
        ],
        current_baseline="cfpb_current",
        group_field="race",
        outcome_field="action",
        reference_group="reference",
        comparison_group="comparison",
    )
    assert frontier["is_current_baseline"].sum() == 1
    assert frontier.loc[frontier["configuration"] == "cfpb_current", "is_current_baseline"].item()
    assert frontier["minimum_detectable_disparity_points"].gt(0).all()

