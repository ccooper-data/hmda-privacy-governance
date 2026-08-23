import pandas as pd

from hmda_privacy.group_size import (
    permutation_null,
    score_demographic_uniqueness,
    size_matched_ratio,
    uniqueness_by_group_size,
)


def fixture() -> pd.DataFrame:
    rows = []
    for tract in ["1", "2"]:
        for race in ["Black or African American", "White"]:
            for index in range(5):
                rows.append(
                    {
                        "census_tract": tract,
                        "applicant_age": str(index % 2),
                        "applicant_sex": str(index % 3),
                        "derived_race": race,
                        "derived_ethnicity": "Not Hispanic or Latino",
                    }
                )
    return pd.DataFrame(rows)


def test_group_size_outputs_are_aggregate_and_reproducible() -> None:
    scored = score_demographic_uniqueness(fixture())
    rows = uniqueness_by_group_size(scored, minimum_cell_size=2)
    assert sum(row["record_count"] for row in rows) == 20
    assert size_matched_ratio(scored)["matched_tracts"] == 2
    first = permutation_null(scored, iterations=10, seed=7)
    second = permutation_null(scored, iterations=10, seed=7)
    assert first == second
