from __future__ import annotations

import json

from hmda_privacy.governance import load_yaml, validate_governance_policy


def main() -> None:
    policy = load_yaml("config/governance.yml")
    exceptions = load_yaml("config/exceptions.yml")
    actual = {
        model: list(spec["columns"])
        for model, spec in policy["published_marts"].items()
    }
    violations = validate_governance_policy(policy, actual, exceptions=exceptions)
    if violations:
        print(json.dumps([item.__dict__ for item in violations], indent=2))
        raise SystemExit(1)
    print("Governance policy check passed")


if __name__ == "__main__":
    main()
