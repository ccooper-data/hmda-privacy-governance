from __future__ import annotations

import hashlib
import json
import os
import re
import tempfile
from dataclasses import asdict, dataclass
from datetime import UTC, datetime
from pathlib import Path
from typing import BinaryIO

import requests

BASE_URL = "https://ffiec.cfpb.gov/v2/data-browser-api"


@dataclass(frozen=True)
class IngestionManifest:
    source_url: str
    requested_at_utc: str
    received_at_utc: str
    parameters: dict[str, object]
    sha256: str
    bytes_received: int
    output_file: str
    http_status: int


def build_slice_url() -> str:
    return f"{BASE_URL}/view/csv"


def _safe_scope(value: str) -> str:
    return re.sub(r"[^a-z0-9]+", "-", value.lower()).strip("-")


def build_output_name(
    *,
    year: int,
    state: str | None,
    county: str | None,
    lei: str | None,
    actions_taken: int | None,
    race: str | None,
) -> str:
    geography = state or county or lei or "slice"
    parts = [str(geography)]
    if actions_taken is not None:
        parts.append(f"action-{actions_taken}")
    if race:
        parts.append(f"race-{_safe_scope(race)}")
    if actions_taken is None and not race:
        parts.append("all")
    return f"hmda_{year}_{'_'.join(parts)}.csv"


def _stream_to_file(response: requests.Response, handle: BinaryIO) -> tuple[str, int]:
    digest = hashlib.sha256()
    size = 0
    for chunk in response.iter_content(chunk_size=1024 * 1024):
        if not chunk:
            continue
        handle.write(chunk)
        digest.update(chunk)
        size += len(chunk)
    return digest.hexdigest(), size


def ingest_slice(
    *,
    year: int,
    output_dir: str | Path,
    state: str | None = None,
    county: str | None = None,
    lei: str | None = None,
    actions_taken: int | None = None,
    race: str | None = None,
    session: requests.Session | None = None,
) -> IngestionManifest:
    if not 2018 <= year <= 2025:
        raise ValueError("HMDA year must be between 2018 and 2025")
    if not any((state, county, lei)):
        raise ValueError("A state, county, or LEI filter is required")

    params: dict[str, object] = {"years": year}
    if state:
        params["states"] = state.upper()
    if county:
        params["counties"] = county
    if lei:
        params["leis"] = lei
    if actions_taken is not None:
        params["actions_taken"] = actions_taken
    if race:
        params["races"] = race

    destination = Path(output_dir) / f"year={year}"
    destination.mkdir(parents=True, exist_ok=True)
    final_path = destination / build_output_name(
        year=year,
        state=state,
        county=county,
        lei=lei,
        actions_taken=actions_taken,
        race=race,
    )
    manifest_path = final_path.with_suffix(".manifest.json")
    requested = datetime.now(UTC).isoformat()
    client = session or requests.Session()

    with client.get(build_slice_url(), params=params, stream=True, timeout=(30, 600)) as response:
        response.raise_for_status()
        with tempfile.NamedTemporaryFile(dir=destination, delete=False) as tmp:
            tmp_path = Path(tmp.name)
            digest, size = _stream_to_file(response, tmp)
        os.replace(tmp_path, final_path)
        received = datetime.now(UTC).isoformat()
        manifest = IngestionManifest(
            source_url=response.url,
            requested_at_utc=requested,
            received_at_utc=received,
            parameters=params,
            sha256=digest,
            bytes_received=size,
            output_file=str(final_path),
            http_status=response.status_code,
        )

    manifest_path.write_text(
        json.dumps(asdict(manifest), indent=2, sort_keys=True) + "\n", encoding="utf-8"
    )
    return manifest
