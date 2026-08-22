from __future__ import annotations

from dataclasses import asdict, dataclass

import pandas as pd
import requests

from .ingestion import BASE_URL


@dataclass(frozen=True)
class AggregateResult:
    count: int
    loan_amount_sum: float
    served_from: str | None

    def to_dict(self) -> dict[str, int | float | str | None]:
        return asdict(self)


@dataclass(frozen=True)
class ReconciliationResult:
    api_count: int
    local_count: int
    count_difference: int
    api_loan_amount_sum: float
    local_loan_amount_sum: float
    sum_difference: float
    passed: bool

    def to_dict(self) -> dict[str, int | float | bool]:
        return asdict(self)


def fetch_aggregate(
    *,
    year: int,
    state: str,
    actions_taken: int,
    race: str,
    session: requests.Session | None = None,
) -> AggregateResult:
    client = session or requests.Session()
    params = {
        "years": year,
        "states": state.upper(),
        "actions_taken": actions_taken,
        "races": race,
    }
    response = client.get(f"{BASE_URL}/view/aggregations", params=params, timeout=(30, 120))
    response.raise_for_status()
    payload = response.json()
    rows = payload.get("aggregations", [])
    if len(rows) != 1:
        raise ValueError(f"Expected one aggregate row, received {len(rows)}")
    row = rows[0]
    return AggregateResult(
        count=int(row["count"]),
        loan_amount_sum=float(row["sum"]),
        served_from=payload.get("servedFrom"),
    )


def reconcile_local_slice(
    frame: pd.DataFrame,
    aggregate: AggregateResult,
    *,
    loan_amount_field: str = "loan_amount",
    count_tolerance: int = 0,
    sum_tolerance: float = 1.0,
) -> ReconciliationResult:
    if loan_amount_field not in frame:
        raise ValueError(f"Missing loan amount field: {loan_amount_field}")
    local_count = len(frame)
    local_sum = float(pd.to_numeric(frame[loan_amount_field], errors="coerce").sum())
    count_difference = local_count - aggregate.count
    sum_difference = local_sum - aggregate.loan_amount_sum
    passed = abs(count_difference) <= count_tolerance and abs(sum_difference) <= sum_tolerance
    return ReconciliationResult(
        api_count=aggregate.count,
        local_count=local_count,
        count_difference=count_difference,
        api_loan_amount_sum=aggregate.loan_amount_sum,
        local_loan_amount_sum=local_sum,
        sum_difference=sum_difference,
        passed=passed,
    )


def validate_contract(
    aggregate: AggregateResult,
    contract: dict,
) -> ReconciliationResult:
    synthetic_frame = pd.DataFrame(
        {"loan_amount": [float(contract["expected_loan_amount_sum"])]}
    )
    # Contract validation compares declared expectations without creating record-shaped data.
    local_count = int(contract["expected_count"])
    local_sum = float(synthetic_frame["loan_amount"].iloc[0])
    count_difference = local_count - aggregate.count
    sum_difference = local_sum - aggregate.loan_amount_sum
    passed = (
        abs(count_difference) <= int(contract.get("count_tolerance", 0))
        and abs(sum_difference) <= float(contract.get("sum_tolerance", 1.0))
    )
    return ReconciliationResult(
        api_count=aggregate.count,
        local_count=local_count,
        count_difference=count_difference,
        api_loan_amount_sum=aggregate.loan_amount_sum,
        local_loan_amount_sum=local_sum,
        sum_difference=sum_difference,
        passed=passed,
    )

