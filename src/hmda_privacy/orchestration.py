from __future__ import annotations

import subprocess
from dataclasses import dataclass
from pathlib import Path

import yaml


@dataclass(frozen=True)
class PipelinePaths:
    hmda_lar: Path
    tract_context: Path
    artifact_dir: Path


def pipeline_commands(
    paths: PipelinePaths, protection_path: Path = Path("config/protection.yml")
) -> list[list[str]]:
    protection = yaml.safe_load(protection_path.read_text(encoding="utf-8"))["configurations"]
    county = protection["county_banded"]
    state = protection["state_banded"]
    variables = str(
        {
            "hmda_lar_path": str(paths.hmda_lar),
            "census_tract_context_path": str(paths.tract_context),
            "county_income_band_width": county["income_band_width"],
            "county_loan_amount_band_width": county["loan_amount_band_width"],
            "state_income_band_width": state["income_band_width"],
            "state_loan_amount_band_width": state["loan_amount_band_width"],
        }
    )
    return [
        [
            "python",
            "scripts/ingest_census_tract_context.py",
            "--state-fips",
            "48",
            "--hmda-lar-path",
            str(paths.hmda_lar),
            "--output",
            str(paths.tract_context),
        ],
        ["dbt", "build", "--vars", variables],
        [
            "python",
            "scripts/export_privacy_utility_frontier.py",
            "--output",
            str(paths.artifact_dir / "texas_2023_privacy_utility_frontier.json"),
        ],
        [
            "python",
            "scripts/export_adjusted_fair_lending_utility.py",
            "--output",
            str(paths.artifact_dir / "texas_2023_adjusted_fair_lending_utility.json"),
        ],
        [
            "python",
            "scripts/export_residential_density_risk.py",
            "--output",
            str(paths.artifact_dir / "texas_2023_residential_density_risk.json"),
        ],
        [
            "python",
            "scripts/export_release_density_risk.py",
            "--output",
            str(paths.artifact_dir / "texas_2023_release_density_risk.json"),
        ],
        [
            "python",
            "scripts/export_density_diagnostics.py",
            "--output",
            str(paths.artifact_dir / "texas_2023_density_diagnostics.json"),
        ],
        [
            "python",
            "scripts/export_aggregate_race_risk.py",
            "--output",
            str(paths.artifact_dir / "texas_2023_race_risk.json"),
        ],
        [
            "python",
            "scripts/export_qi_sensitivity.py",
            "--output",
            str(paths.artifact_dir / "texas_2023_qi_sensitivity.json"),
        ],
        [
            "python",
            "scripts/export_population_uniqueness_sensitivity.py",
            "--output",
            str(paths.artifact_dir / "texas_2023_population_uniqueness_sensitivity.json"),
        ],
        [
            "python",
            "scripts/export_group_size_decomposition.py",
            "--input",
            str(paths.hmda_lar),
            "--output",
            str(paths.artifact_dir / "texas_2023_group_size_decomposition.json"),
        ],
        [
            "python",
            "scripts/build_release_summary.py",
            "--input-dir",
            str(paths.artifact_dir),
        ],
        ["python", "scripts/build_release_figures.py"],
    ]


def run_pipeline(paths: PipelinePaths, *, root: Path = Path(".")) -> None:
    for command in pipeline_commands(paths):
        subprocess.run(command, cwd=root, check=True)


def build_dagster_definitions():
    """Return Dagster definitions while keeping Dagster an optional dependency."""
    try:
        from dagster import Definitions, asset
    except ImportError as error:
        raise RuntimeError(
            "Install the orchestration extra: pip install -e '.[orchestration]'"
        ) from error

    paths = PipelinePaths(
        Path("data/bronze/year=2023/hmda_2023_TX_all.csv"),
        Path("data/external/census_tract_context_2023_TX.csv"),
        Path("artifacts"),
    )
    commands = pipeline_commands(paths)

    @asset(group_name="privacy_pipeline")
    def census_tract_context() -> str:
        subprocess.run(commands[0], check=True)
        return str(paths.tract_context)

    @asset(deps=[census_tract_context], group_name="privacy_pipeline")
    def governed_warehouse() -> str:
        subprocess.run(commands[1], check=True)
        return "data/hmda_privacy.duckdb"

    @asset(deps=[governed_warehouse], group_name="privacy_pipeline")
    def aggregate_release() -> list[str]:
        for command in commands[2:]:
            subprocess.run(command, check=True)
        return [str(paths.artifact_dir), "docs/figures"]

    return Definitions(assets=[census_tract_context, governed_warehouse, aggregate_release])
