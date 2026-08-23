from __future__ import annotations

import argparse
import hashlib
import json
from pathlib import Path

DEFAULT_INPUTS = {
    "frontier": Path("docs/results/texas_2023_privacy_utility_frontier.json"),
    "adjusted_utility": Path("docs/results/texas_2023_adjusted_fair_lending_utility.json"),
    "qi_sensitivity": Path("docs/results/texas_2023_qi_sensitivity.json"),
    "residential_density": Path("docs/results/texas_2023_residential_density_risk.json"),
    "density_diagnostics": Path("docs/results/texas_2023_density_diagnostics.json"),
    "group_size_decomposition": Path("docs/results/texas_2023_group_size_decomposition.json"),
    "population_uniqueness": Path("docs/results/texas_2023_population_uniqueness_sensitivity.json"),
}

INPUT_FILENAMES = {name: path.name for name, path in DEFAULT_INPUTS.items()}


def _load(path: Path) -> dict:
    return json.loads(path.read_text(encoding="utf-8"))


def build_summary(inputs: dict[str, Path]) -> dict:
    data = {name: _load(path) for name, path in inputs.items()}
    density_rows = data["residential_density"]["cohorts"]
    focal_density = [
        row
        for row in density_rows
        if (row["derived_race"], row["derived_ethnicity"])
        in {
            ("ALL", "ALL"),
            ("Black or African American", "Not Hispanic or Latino"),
            ("White", "Not Hispanic or Latino"),
        }
    ]
    population = data["population_uniqueness"]["estimates"]
    return {
        "scope": {"year": 2023, "state": "TX", "applications": 1_041_819},
        "qi_definition": "selected_14_field_institution_aware_set",
        "frontier": data["frontier"]["frontier"],
        "qi_sensitivity": data["qi_sensitivity"]["overall"],
        "residential_density": focal_density,
        "density_diagnostics": {
            "density_association": data["density_diagnostics"]["density_association"],
            "two_way_risk": data["density_diagnostics"]["two_way_risk"],
            "join_exclusion_artifact": str(inputs["density_diagnostics"]),
        },
        "group_size_decomposition": data["group_size_decomposition"],
        "adjusted_utility": data["adjusted_utility"]["configurations"],
        "population_uniqueness": {
            "status": (
                "boundary_fit_not_reportable"
                if all(row.get("fit_status") == "boundary_fit_not_reportable" for row in population)
                else "review_required"
            )
        },
    }


def main() -> None:
    parser = argparse.ArgumentParser()
    parser.add_argument("--input-dir", type=Path)
    parser.add_argument("--output", type=Path, default=Path("docs/results/texas_2023_summary.json"))
    parser.add_argument(
        "--manifest",
        type=Path,
        default=Path("docs/results/texas_2023_summary.manifest.json"),
    )
    args = parser.parse_args()
    inputs = (
        {name: args.input_dir / filename for name, filename in INPUT_FILENAMES.items()}
        if args.input_dir
        else DEFAULT_INPUTS
    )
    summary = build_summary(inputs)
    encoded = json.dumps(summary, indent=2, allow_nan=False) + "\n"
    args.output.parent.mkdir(parents=True, exist_ok=True)
    args.output.write_text(encoded, encoding="utf-8")
    manifest = {
        "generator": "python scripts/build_release_summary.py",
        "inputs": {
            name: {
                "path": str(path),
                "sha256": hashlib.sha256(path.read_bytes()).hexdigest(),
            }
            for name, path in inputs.items()
        },
        "output": {
            "path": str(args.output),
            "sha256": hashlib.sha256(encoded.encode()).hexdigest(),
        },
    }
    args.manifest.write_text(json.dumps(manifest, indent=2) + "\n", encoding="utf-8")


if __name__ == "__main__":
    main()
