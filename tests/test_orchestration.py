from pathlib import Path

from hmda_privacy.orchestration import PipelinePaths, pipeline_commands


def test_pipeline_orders_context_before_warehouse_before_exports() -> None:
    commands = pipeline_commands(PipelinePaths(Path("lar.csv"), Path("tract.csv"), Path("out")))
    assert "ingest_census_tract_context.py" in commands[0][1]
    assert commands[1][:2] == ["dbt", "build"]
    assert "export_privacy_utility_frontier.py" in commands[2][1]
    assert "build_release_figures.py" in commands[-1][1]
