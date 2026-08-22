import hashlib
import json
from pathlib import Path

import pytest

from hmda_privacy.ingestion import ingest_slice


class FakeResponse:
    url = "https://example.test/view/csv?years=2023&states=TX"
    status_code = 200

    def __enter__(self):
        return self

    def __exit__(self, *args):
        return None

    def raise_for_status(self):
        return None

    def iter_content(self, chunk_size):
        yield b"a,b\n1,2\n"


class FakeSession:
    def get(self, *args, **kwargs):
        return FakeResponse()


def test_ingest_writes_immutable_file_and_manifest(tmp_path: Path) -> None:
    manifest = ingest_slice(year=2023, state="tx", output_dir=tmp_path, session=FakeSession())
    output = Path(manifest.output_file)
    assert output.read_bytes() == b"a,b\n1,2\n"
    assert manifest.sha256 == hashlib.sha256(output.read_bytes()).hexdigest()
    stored = json.loads(output.with_suffix(".manifest.json").read_text())
    assert stored["parameters"] == {"states": "TX", "years": 2023}


def test_ingest_requires_filter(tmp_path: Path) -> None:
    with pytest.raises(ValueError, match="filter is required"):
        ingest_slice(year=2023, output_dir=tmp_path, session=FakeSession())

