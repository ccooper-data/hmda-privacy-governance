from __future__ import annotations

import json

from hmda_privacy.governance import load_yaml
from hmda_privacy.validation import fetch_aggregate, validate_contract


def main() -> None:
    contracts = load_yaml("config/validation_contracts.yml")["contracts"]
    results = {}
    failed = False
    for name, contract in contracts.items():
        aggregate = fetch_aggregate(
            year=int(contract["year"]),
            state=str(contract["state"]),
            actions_taken=int(contract["actions_taken"]),
            race=str(contract["race"]),
        )
        result = validate_contract(aggregate, contract)
        results[name] = result.to_dict()
        failed = failed or not result.passed
    print(json.dumps(results, indent=2, sort_keys=True))
    if failed:
        raise SystemExit(1)


if __name__ == "__main__":
    main()

