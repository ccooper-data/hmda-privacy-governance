import pandas as pd

from hmda_privacy.subject_rights import delete_synthetic_subject, export_synthetic_subject


def tables():
    return {
        "control": pd.DataFrame(
            {"synthetic_subject_key": ["S1", "S2"], "value": [1, 2]}
        ),
        "events": pd.DataFrame(
            {"synthetic_subject_key": ["S1", "S1", "S2"], "event": ["a", "b", "c"]}
        ),
        "aggregate": pd.DataFrame({"count": [3]}),
    }


def test_export_finds_every_synthetic_table() -> None:
    exported, audit = export_synthetic_subject(tables(), subject_key="S1")
    assert set(exported) == {"control", "events"}
    assert audit.records_affected == 3
    assert audit.control_cohort_only


def test_delete_cascades_without_mutating_input() -> None:
    original = tables()
    updated, audit = delete_synthetic_subject(original, subject_key="S1")
    assert len(original["events"]) == 3
    assert updated["events"]["synthetic_subject_key"].tolist() == ["S2"]
    assert audit.tables_touched == ("control", "events")
    assert audit.records_affected == 3

