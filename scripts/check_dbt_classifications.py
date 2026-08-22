from __future__ import annotations

import json

from hmda_privacy.dbt_governance import check_dbt_classification_drift


def main() -> None:
    violations = check_dbt_classification_drift(
        models_dir="models",
        schema_path="models/schema.yml",
        allowed={"public", "internal", "quasi_identifier", "sensitive"},
    )
    if violations:
        print(json.dumps([item.__dict__ for item in violations], indent=2))
        raise SystemExit(1)
    print("dbt classification drift check passed")


if __name__ == "__main__":
    main()

