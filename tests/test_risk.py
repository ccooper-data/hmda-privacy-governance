from dataclasses import replace

import pandas as pd
import pytest

from hmda_privacy.config import QIConfig
from hmda_privacy.risk import cohort_risk, equivalence_classes, summarize_risk


@pytest.fixture
def config() -> QIConfig:
    return QIConfig(
        version=1,
        name="test",
        fields=("tract", "age_band"),
        forbidden_direct_identifiers=("uli",),
        sensitive_attributes=("action_taken",),
        minimum_cell_size=2,
        k_thresholds=(1, 5, 10),
    )


@pytest.fixture
def frame() -> pd.DataFrame:
    return pd.DataFrame(
        {
            "tract": ["1", "1", "2", "3"],
            "age_band": ["25-34", "25-34", "35-44", "45-54"],
            "race": ["A", "A", "B", "C"],
        }
    )


def test_equivalence_classes_are_aggregate(frame, config) -> None:
    classes = equivalence_classes(frame, config)
    assert sorted(classes["k"].tolist()) == [1, 1, 2]
    assert set(classes) == {"tract", "age_band", "k"}


def test_risk_summary_is_record_weighted(frame, config) -> None:
    summary = summarize_risk(frame, config)
    assert summary.record_count == 4
    assert summary.sample_unique_records == 2
    assert summary.sample_uniqueness_rate == 0.5
    assert summary.prosecutor_expected_match_risk == 0.75


def test_forbidden_identifier_rejected(frame, config) -> None:
    frame["uli"] = ["a", "b", "c", "d"]
    with pytest.raises(ValueError, match="prohibited direct identifiers"):
        summarize_risk(frame, config)


def test_cohort_output_suppresses_small_cells(frame, config) -> None:
    result = cohort_risk(frame, config, ["race"])
    assert result["race"].tolist() == ["A"]
    strict = replace(config, minimum_cell_size=3)
    assert cohort_risk(frame, strict, ["race"]).empty

