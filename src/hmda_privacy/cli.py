from __future__ import annotations

import argparse
import json
from pathlib import Path

import pandas as pd

from .config import load_qi_config
from .ingestion import ingest_slice
from .risk import summarize_risk

DEFAULT_CONFIG = Path("config/quasi_identifiers.yml")


def _parser() -> argparse.ArgumentParser:
    parser = argparse.ArgumentParser(prog="hmda")
    commands = parser.add_subparsers(dest="command", required=True)
    ingest = commands.add_parser("ingest")
    ingest.add_argument("--year", type=int, required=True)
    ingest.add_argument("--state")
    ingest.add_argument("--county")
    ingest.add_argument("--lei")
    ingest.add_argument("--output", type=Path, required=True)
    risk = commands.add_parser("risk")
    risk.add_argument("--input", type=Path, required=True)
    risk.add_argument("--output", type=Path, required=True)
    risk.add_argument("--config", type=Path, default=DEFAULT_CONFIG)
    return parser


def main() -> None:
    args = _parser().parse_args()
    if args.command == "ingest":
        manifest = ingest_slice(
            year=args.year,
            state=args.state,
            county=args.county,
            lei=args.lei,
            output_dir=args.output,
        )
        print(json.dumps(manifest.__dict__, indent=2))
        return
    config = load_qi_config(args.config)
    frame = pd.read_csv(args.input, low_memory=False)
    summary = summarize_risk(frame, config)
    args.output.parent.mkdir(parents=True, exist_ok=True)
    args.output.write_text(json.dumps(summary.to_dict(), indent=2) + "\n", encoding="utf-8")


if __name__ == "__main__":
    main()

