from hmda_privacy.publication import enforce_minimum_cell


def test_n_one_redacts_count_and_sensitive_rate() -> None:
    payload = {
        "configurations": [
            {
                "configuration": "cfpb_current",
                "comparison_n": 1,
                "comparison_denial_rate": 1.0,
                "odds_ratio": 9.9,
            }
        ]
    }
    protected = enforce_minimum_cell(payload, minimum_cell_size=20)
    row = protected["configurations"][0]
    assert row == {
        "configuration": "cfpb_current",
        "suppression_status": "suppressed_minimum_cell",
        "minimum_cell_size": 20,
    }


def test_safe_aggregate_is_unchanged() -> None:
    payload = {"record_count": 20, "denial_rate": 0.25}
    assert enforce_minimum_cell(payload, minimum_cell_size=20) == payload
