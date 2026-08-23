from __future__ import annotations

from hmda_privacy.governance import load_yaml
from hmda_privacy.scope_guard import analysis_scope_violations


def main() -> None:
    scopes = load_yaml("config/analysis_scopes.yml")["scopes"]
    validation = scopes["texas_2023_black_originations_validation"]
    analytical = scopes["texas_2023_full_release"]
    if validation.get("status") != "validation_only":
        raise SystemExit("Filtered validation slice must remain validation_only")
    if analytical.get("equivalence_universe") != "full_state_year":
        raise SystemExit("Texas analytical scope must use full_state_year equivalence classes")
    violations = analysis_scope_violations(".")
    if violations:
        for violation in violations:
            print(f"{violation.code}: {violation.path}: {violation.detail}")
        raise SystemExit("Analysis SQL violates the declared full-universe scope")
    print("Analysis scope check passed")


if __name__ == "__main__":
    main()
