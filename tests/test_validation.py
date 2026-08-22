import pandas as pd

from hmda_privacy.validation import AggregateResult, fetch_aggregate, reconcile_local_slice


class FakeResponse:
    def raise_for_status(self):
        return None

    def json(self):
        return {
            "aggregations": [{"count": 2, "sum": 300000.0}],
            "servedFrom": "cache",
        }


class FakeSession:
    def get(self, *args, **kwargs):
        return FakeResponse()


def test_fetch_aggregate_parses_confirmed_shape() -> None:
    result = fetch_aggregate(
        year=2023,
        state="tx",
        actions_taken=1,
        race="Black or African American",
        session=FakeSession(),
    )
    assert result == AggregateResult(2, 300000.0, "cache")


def test_local_reconciliation_passes_exact_match() -> None:
    frame = pd.DataFrame({"loan_amount": [100000, 200000]})
    result = reconcile_local_slice(frame, AggregateResult(2, 300000, "cache"))
    assert result.passed
    assert result.count_difference == 0
    assert result.sum_difference == 0


def test_local_reconciliation_fails_difference() -> None:
    frame = pd.DataFrame({"loan_amount": [100000]})
    result = reconcile_local_slice(frame, AggregateResult(2, 300000, None))
    assert not result.passed

