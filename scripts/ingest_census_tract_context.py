from __future__ import annotations

import argparse
import hashlib
import io
import json
import zipfile
from pathlib import Path

import pandas as pd
import requests

ACS_URL = "https://api.census.gov/data/2023/acs/acs5"
GAZETTEER_URL = (
    "https://www2.census.gov/geo/docs/maps-data/data/gazetteer/"
    "2023_Gazetteer/2023_Gaz_tracts_national.zip"
)


def _sha256(content: bytes) -> str:
    return hashlib.sha256(content).hexdigest()


def main() -> None:
    parser = argparse.ArgumentParser()
    parser.add_argument("--state-fips", default="48")
    parser.add_argument("--output", type=Path, required=True)
    args = parser.parse_args()

    acs_response = requests.get(
        ACS_URL,
        params={
            "get": "NAME,B01003_001E",
            "for": "tract:*",
            "in": f"state:{args.state_fips} county:*",
        },
        headers={
            "Accept": "application/json",
            "User-Agent": "hmda-privacy-governance/0.1 aggregate-research",
        },
        timeout=120,
    )
    acs_response.raise_for_status()
    acs_bytes = acs_response.content
    try:
        acs_rows = acs_response.json()
    except requests.exceptions.JSONDecodeError as error:
        preview = acs_response.text[:300].replace("\n", " ")
        raise RuntimeError(
            f"Census ACS response was not JSON; content-type="
            f"{acs_response.headers.get('content-type')!r}; body={preview!r}"
        ) from error
    if not isinstance(acs_rows, list) or len(acs_rows) < 2:
        raise RuntimeError("Census ACS response contained no tract records")
    acs = pd.DataFrame(acs_rows[1:], columns=acs_rows[0])
    acs["census_tract"] = acs["state"] + acs["county"] + acs["tract"]
    acs["population"] = pd.to_numeric(acs["B01003_001E"], errors="coerce")

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

    context = acs[["census_tract", "population"]].merge(
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
        "acs_source": ACS_URL,
        "acs_sha256": _sha256(acs_bytes),
        "gazetteer_source": GAZETTEER_URL,
        "gazetteer_sha256": _sha256(gazetteer_bytes),
        "population_variable": "B01003_001E",
        "density_formula": "ACS total population / Gazetteer land area square miles",
    }
    manifest_path = args.output.with_suffix(".manifest.json")
    manifest_path.write_text(json.dumps(manifest, indent=2) + "\n", encoding="utf-8")
    print(json.dumps(manifest, indent=2))


if __name__ == "__main__":
    main()
