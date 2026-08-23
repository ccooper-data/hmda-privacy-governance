from __future__ import annotations

import argparse
import io
import json
import zipfile
from pathlib import Path

import pandas as pd
import requests

GAZETTEER_URL = (
    "https://www2.census.gov/geo/docs/maps-data/data/gazetteer/"
    "2023_Gazetteer/2023_Gaz_tracts_national.zip"
)


def main() -> None:
    parser = argparse.ArgumentParser()
    parser.add_argument("--state-fips", default="48")
    parser.add_argument("--hmda-lar-path", type=Path, required=True)
    parser.add_argument("--output", type=Path, required=True)
    args = parser.parse_args()

    hmda = pd.read_csv(
        args.hmda_lar_path,
        usecols=["census_tract", "tract_population"],
        dtype=str,
        low_memory=False,
    )
    hmda["census_tract"] = hmda["census_tract"].str.strip()
    hmda["population"] = pd.to_numeric(hmda["tract_population"], errors="coerce")
    population_conflicts = int(
        (hmda.groupby("census_tract", observed=True)["population"].nunique() > 1).sum()
    )
    population = (
        hmda.dropna(subset=["census_tract", "population"])
        .groupby("census_tract", as_index=False, observed=True)["population"]
        .median()
    )

    gazetteer_response = requests.get(
        GAZETTEER_URL,
        headers={"User-Agent": "hmda-privacy-governance/0.1 aggregate-research"},
        timeout=120,
    )
    gazetteer_response.raise_for_status()
    gazetteer_bytes = gazetteer_response.content
    with zipfile.ZipFile(io.BytesIO(gazetteer_bytes)) as archive:
        text_name = next(name for name in archive.namelist() if name.lower().endswith(".txt"))
        gazetteer = pd.read_csv(archive.open(text_name), sep="\t", dtype=str)
    gazetteer.columns = [column.strip() for column in gazetteer.columns]
    gazetteer = gazetteer.loc[gazetteer["USPS"].str.strip() == "TX"].copy()
    gazetteer["census_tract"] = gazetteer["GEOID"].str.strip()
    gazetteer["land_area_sqmi"] = pd.to_numeric(
        gazetteer["ALAND_SQMI"].str.strip(), errors="coerce"
    )

    context = population.merge(
        gazetteer[["census_tract", "land_area_sqmi"]],
        on="census_tract",
        how="inner",
        validate="one_to_one",
    )
    context = context.loc[(context["population"] >= 0) & (context["land_area_sqmi"] > 0)]
    context["population_density_per_sqmi"] = context["population"] / context["land_area_sqmi"]
    args.output.parent.mkdir(parents=True, exist_ok=True)
    context.sort_values("census_tract").to_csv(args.output, index=False)
    manifest = {
        "aggregate_geography_only": True,
        "state_fips": args.state_fips,
        "records": len(context),
        "population_source": "public HMDA LAR tract_population field",
        "hmda_lar_path": str(args.hmda_lar_path),
        "tracts_with_conflicting_population_values": population_conflicts,
        "gazetteer_source": GAZETTEER_URL,
        "density_formula": "HMDA tract_population / Census Gazetteer land area square miles",
    }
    manifest_path = args.output.with_suffix(".manifest.json")
    manifest_path.write_text(json.dumps(manifest, indent=2) + "\n", encoding="utf-8")
    print(json.dumps(manifest, indent=2))


if __name__ == "__main__":
    main()
