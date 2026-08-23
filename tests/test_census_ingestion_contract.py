from pathlib import Path


def test_census_request_uses_required_tract_hierarchy_and_diagnostics() -> None:
    source = Path("scripts/ingest_census_tract_context.py").read_text(encoding="utf-8")
    assert '"for": "tract:*"' in source
    assert 'county:*' in source
    assert '"Accept": "application/json"' in source
    assert "response was not JSON" in source
