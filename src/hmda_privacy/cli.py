from __future__ import annotations

import argparse
import json
from pathlib import Path

import pandas as pd

from .config import load_qi_config
from .ingestion import ingest_slice
from .population import estimate_population_uniqueness_subsample
from .risk import cohort_risk_report, summarize_risk
from .synthetic_linkage import simulate_synthetic_linkage

DEFAULT_CONFIG = Path("config/quasi_identifiers.yml")


def _parser() -> argparse.ArgumentParser:
    parser = argparse.ArgumentParser(prog="hmda")
    commands = parser.add_subparsers(dest="command", required=True)
    ingest = commands.add_parser("ingest")
    ingest.add_argument("--year", type=int, required=True)
    ingest.add_argument("--state")
    ingest.add_argument("--county")
    ingest.add_argument("--lei")
    ingest.add_argument("--actions-taken", type=int)
    ingest.add_argument("--race")
    ingest.add_argument("--output", type=Path, required=True)
    risk = commands.add_parser("risk")
    risk.add_argument("--input", type=Path, required=True)
    risk.add_argument("--output", type=Path, required=True)
    risk.add_argument("--config", type=Path, default=DEFAULT_CONFIG)
    population = commands.add_parser("population-uniqueness")
    population.add_argument("--input", type=Path, required=True)
    population.add_argument("--sample-fraction", type=float, required=True)
    population.add_argument("--replicates", type=int, default=200)
    population.add_argument("--output", type=Path, required=True)
    population.add_argument("--config", type=Path, default=DEFAULT_CONFIG)
    linkage = commands.add_parser("synthetic-linkage")
    linkage.add_argument("--input", type=Path, required=True)
    linkage.add_argument("--records", type=int, default=10_000)
    linkage.add_argument("--output", type=Path, required=True)
    linkage.add_argument("--config", type=Path, default=DEFAULT_CONFIG)
    cohort = commands.add_parser("cohort-risk")
    cohort.add_argument("--input", type=Path, required=True)
    cohort.add_argument("--cohort-fields", nargs="+", required=True)
    cohort.add_argument(
        "--equivalence-universe",
        choices=["full_state_year", "full_national_year"],
        required=True,
    )
    cohort.add_argument("--output", type=Path, required=True)
    cohort.add_argument("--config", type=Path, default=DEFAULT_CONFIG)
    return parser


def main() -> None:
    args = _parser().parse_args()
    if args.command == "ingest":
        manifest = ingest_slice(
            year=args.year,
            state=args.state,
            county=args.county,
            lei=args.lei,
            actions_taken=args.actions_taken,
            race=args.race,
            output_dir=args.output,
        )
        print(json.dumps(manifest.__dict__, indent=2))
        return
    config = load_qi_config(args.config)
    frame = pd.read_csv(args.input, low_memory=False)
    if args.command == "risk":
        summary = summarize_risk(frame, config)
    elif args.command == "population-uniqueness":
        summary = estimate_population_uniqueness_subsample(
            frame,
            config,
            sample_fraction=args.sample_fraction,
            replicates=args.replicates,
        )
    elif args.command == "synthetic-linkage":
        summary = simulate_synthetic_linkage(
            frame, config, synthetic_records=args.records
        )
    else:
        cohorts, metadata = cohort_risk_report(
            frame,
            config,
            args.cohort_fields,
            equivalence_universe=args.equivalence_universe,
        )
        args.output.parent.mkdir(parents=True, exist_ok=True)
        payload = {
            "metadata": metadata.to_dict(),
            "cohorts": cohorts.to_dict(orient="records"),
        }
        args.output.write_text(json.dumps(payload, indent=2) + "\n", encoding="utf-8")
        return
    args.output.parent.mkdir(parents=True, exist_ok=True)
    args.output.write_text(json.dumps(summary.to_dict(), indent=2) + "\n", encoding="utf-8")


if __name__ == "__main__":
    main()
