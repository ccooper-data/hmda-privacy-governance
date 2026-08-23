from pathlib import Path


def test_exporter_converts_nonfinite_values_to_null() -> None:
    source = Path("scripts/export_privacy_utility_frontier.py").read_text(encoding="utf-8")
    assert "math.isfinite" in source
    assert "record[key] = None" in source
    assert "insufficient_protected_cohort_retention" in source
