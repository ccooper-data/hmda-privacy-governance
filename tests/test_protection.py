import pandas as pd
import pytest

from hmda_privacy.config import QIConfig
from hmda_privacy.protection import (
    ProtectionConfig,
    apply_protection,
    generalize_geography,
    generalize_numeric,
)


def config() -> QIConfig:
    return QIConfig(
        1,
        "test",
        ("census_tract", "income", "loan_amount"),
        ("uli",),
        ("action_taken",),
        2,
        (1, 5, 10),
    )


def test_geography_hierarchy() -> None:
    series = pd.Series(["48201310100"])
    assert generalize_geography(series, "tract").iloc[0] == "48201310100"
    assert generalize_geography(series, "county").iloc[0] == "48201"
    assert generalize_geography(series, "state").iloc[0] == "48"


def test_numeric_bands() -> None:
    result = generalize_numeric(pd.Series([49_999, 50_000]), 50_000)
    assert result.tolist() == ["0-50000", "50000-100000"]


def test_protection_generalizes_and_suppresses() -> None:
    frame = pd.DataFrame(
        {
            "census_tract": ["48201310100", "48201310101", "06001000100"],
            "income": [75_000, 76_000, 10_000],
            "loan_amount": [300_000, 320_000, 100_000],
        }
    )
    protected, transformed = apply_protection(
        frame,
        config(),
        ProtectionConfig("moderate", "county", 25_000, 50_000, 2),
    )
    assert len(protected) == 2
    assert transformed.fields == (
        "geography",
        "income_generalized",
        "loan_amount_generalized",
    )


def test_invalid_geography_rejected() -> None:
    with pytest.raises(ValueError, match="Unsupported"):
        generalize_geography(pd.Series(["1"]), "block")

