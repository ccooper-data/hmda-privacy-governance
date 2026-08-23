from __future__ import annotations

import argparse
import json
from dataclasses import asdict
from pathlib import Path

import pandas as pd

from hmda_privacy.config import load_qi_config
from hmda_privacy.group_size import (
    permutation_null,
    score_demographic_uniqueness,
    size_matched_ratio,
    uniqueness_by_group_size,
)


def main() -> None:
    parser = argparse.ArgumentParser()
    parser.add_argument("--input", type=Path, required=True)
    parser.add_argument("--output", type=Path, required=True)
    parser.add_argument("--iterations", type=int, default=1_000)
    parser.add_argument("--seed", type=int, default=20_260_823)
    args = parser.parse_args()
    fields = [
        "census_tract",
        "applicant_age",
        "applicant_sex",
        "derived_race",
        "derived_ethnicity",
    ]
    frame = pd.read_csv(args.input, usecols=fields, dtype="string", low_memory=False)
    scored = score_demographic_uniqueness(frame)
    minimum = load_qi_config("config/quasi_identifiers.yml").minimum_cell_size
    permutation = permutation_null(scored, iterations=args.iterations, seed=args.seed)
    matched = size_matched_ratio(scored, bootstrap_replicates=2_000, seed=args.seed)
    withdraw = not (
        permutation.observed_ratio > permutation.null_ci_high
        and permutation.p_value_two_sided < 0.05
        and not matched["underpowered"]
        and matched["uniqueness_ratio"] is not None
        and matched["ratio_ci_low"] is not None
        and matched["ratio_ci_low"] > 1
    )
    payload = {
        "metadata": {
            "aggregate_only": True,
            "preregistration": "docs/decisions/0001-preregister-group-size-decomposition.md",
            "equivalence_universe": "full_state_year",
            "iterations": args.iterations,
            "seed": args.seed,
            "minimum_cell_size": minimum,
        },
        "uniqueness_by_group_size": uniqueness_by_group_size(scored, minimum_cell_size=minimum),
        "size_matched_comparison": matched,
        "permutation_null": asdict(permutation),
        "decision": {
            "withdraw_unqualified_residual_disparity_claim": withdraw,
            "rule": "observed above null 97.5th percentile with p<0.05 and supported size-match",
        },
    }
    args.output.parent.mkdir(parents=True, exist_ok=True)
    args.output.write_text(json.dumps(payload, indent=2) + "\n", encoding="utf-8")
    print(json.dumps(payload["permutation_null"], indent=2))
    print(json.dumps(payload["decision"], indent=2))


if __name__ == "__main__":
    main()
