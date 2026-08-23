from pathlib import Path

from hmda_privacy.orchestration import PipelinePaths, pipeline_commands


def test_pipeline_orders_context_before_warehouse_before_exports() -> None:
    commands = pipeline_commands(PipelinePaths(Path("lar.csv"), Path("tract.csv"), Path("out")))
    assert "ingest_census_tract_context.py" in commands[0][1]
    assert commands[1][:2] == ["dbt", "build"]
    assert "export_privacy_utility_frontier.py" in commands[2][1]
    scripts = {command[1] for command in commands if command[0] == "python"}
    assert "scripts/export_group_size_decomposition.py" in scripts
    assert "scripts/export_density_diagnostics.py" in scripts
    assert "scripts/export_qi_sensitivity.py" in scripts
    assert "scripts/build_release_summary.py" in scripts
    assert "build_release_figures.py" in commands[-1][1]


def test_pipeline_reads_protection_band_widths(tmp_path: Path) -> None:
    config = tmp_path / "protection.yml"
    config.write_text(
        """configurations:
  county_banded: {income_band_width: 123, loan_amount_band_width: 456}
  state_banded: {income_band_width: 789, loan_amount_band_width: 999}
"""
    )
    commands = pipeline_commands(
        PipelinePaths(Path("lar.csv"), Path("tract.csv"), Path("out")), config
    )
    variables = commands[1][3]
    assert "123" in variables
    assert "999" in variables
