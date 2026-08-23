import pandas as pd
import pytest

from hmda_privacy.config import QIConfig
from hmda_privacy.risk import cohort_risk, cohort_risk_report


def test_k_is_formed_on_full_universe_before_cohort_summary() -> None:
    frame = pd.DataFrame(
        {
            "tract": ["1", "1", "2", "2"],
            "age": ["35-44", "35-44", "45-54", "45-54"],
            "cohort": ["A", "B", "A", "B"],
        }
    )
    config = QIConfig(1, "test", ("tract", "age"), (), (), 1, (1, 5, 10))
    defensible = cohort_risk(frame, config, ["cohort"])
    filtered_a = cohort_risk(frame.loc[frame["cohort"] == "A"], config, ["cohort"])
    assert defensible.loc[defensible["cohort"] == "A", "sample_unique_rate"].item() == 0
    assert filtered_a["sample_unique_rate"].item() == 1


def test_report_requires_complete_declared_universe() -> None:
    frame = pd.DataFrame({"tract": ["1", "1"], "cohort": ["A", "B"]})
    config = QIConfig(1, "test", ("tract",), (), (), 1, (1, 5, 10))
    report, metadata = cohort_risk_report(
        frame, config, ["cohort"], equivalence_universe="full_state_year"
    )
    assert len(report) == 2
    assert metadata.aggregate_only
    with pytest.raises(ValueError, match="filtered cohorts are validation-only"):
        cohort_risk_report(frame, config, ["cohort"], equivalence_universe="filtered_race")

