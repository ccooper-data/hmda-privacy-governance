from __future__ import annotations

import json
from pathlib import Path

import yaml

from hmda_privacy.dbt_governance import selected_sql_columns
from hmda_privacy.governance import load_yaml, validate_governance_policy


def main() -> None:
    policy = load_yaml("config/governance.yml")
    exceptions = load_yaml("config/exceptions.yml")
    schema = yaml.safe_load(Path("models/schema.yml").read_text(encoding="utf-8"))
    declarations = {model["name"]: model for model in schema.get("models", [])}
    actual: dict[str, list[str]] = {}
    structural: list[dict[str, str | None]] = []
    for path in sorted(Path("models/gold").glob("*.sql")):
        model = path.stem
        declaration = declarations.get(model)
        if declaration is None:
            structural.append({"code": "UNDECLARED_GOLD_MODEL", "model": model, "column": None})
            continue
        publication = declaration.get("meta", {}).get("publication")
        if publication not in {"published", "prohibited"}:
            structural.append(
                {"code": "MISSING_PUBLICATION_DECISION", "model": model, "column": None}
            )
            continue
        if publication == "published":
            if model not in policy["published_marts"]:
                structural.append(
                    {"code": "UNAUTHORIZED_PUBLISHED_MART", "model": model, "column": None}
                )
            actual[model] = selected_sql_columns(path.read_text(encoding="utf-8"))
        elif model in policy["published_marts"]:
            structural.append(
                {"code": "PROHIBITED_MODEL_DECLARED_PUBLIC", "model": model, "column": None}
            )
    for model in sorted(set(policy["published_marts"]) - set(actual)):
        structural.append({"code": "MISSING_PUBLISHED_MART", "model": model, "column": None})
    violations = validate_governance_policy(policy, actual, exceptions=exceptions)
    payload = structural + [item.__dict__ for item in violations]
    if payload:
        print(json.dumps(payload, indent=2))
        raise SystemExit(1)
    print("Governance policy check passed")


if __name__ == "__main__":
    main()
