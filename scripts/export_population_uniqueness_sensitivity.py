from __future__ import annotations

import argparse
import json
from pathlib import Path

import duckdb

from hmda_privacy.population import estimate_population_uniqueness_gamma_poisson


def main() -> None:
    parser = argparse.ArgumentParser()
    parser.add_argument("--database", type=Path, default=Path("data/hmda_privacy.duckdb"))
    parser.add_argument("--output", type=Path, required=True)
    parser.add_argument("--coverage-fractions", type=float, nargs="+", default=[0.1, 0.25, 0.5])
    args = parser.parse_args()

    sizes = duckdb.connect(str(args.database), read_only=True).execute(
        "select k from qi_profile"
    ).fetchnumpy()["k"]
    estimates = [
        estimate_population_uniqueness_gamma_poisson(
            sizes, coverage_fraction=coverage_fraction
        ).to_dict()
        for coverage_fraction in args.coverage_fractions
    ]
    payload = {
        "metadata": {
            "aggregate_only": True,
            "equivalence_universe": "full_state_year",
            "coverage_interpretation": "declared sensitivity scenarios, not HMDA sampling rates",
            "warning": "HMDA is not a probability sample of residents; no scenario is labeled true",
        },
        "estimates": estimates,
    }
    args.output.parent.mkdir(parents=True, exist_ok=True)
    args.output.write_text(json.dumps(payload, indent=2, allow_nan=False) + "\n", encoding="utf-8")
    print(json.dumps(payload, indent=2, allow_nan=False))


if __name__ == "__main__":
    main()
