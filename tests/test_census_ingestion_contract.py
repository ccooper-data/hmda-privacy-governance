from pathlib import Path


def test_context_ingestion_uses_public_hmda_population_and_census_land_area() -> None:
    source = Path("scripts/ingest_census_tract_context.py").read_text(encoding="utf-8")
    assert '"census_tract", "tract_population"' in source
    assert "GAZETTEER_URL" in source
    assert "population_conflicts" in source
    assert "address" not in source.lower()
