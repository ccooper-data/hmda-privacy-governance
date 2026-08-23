import json
from pathlib import Path

from hmda_privacy.reporting import build_release_figures


def test_release_figures_are_svg_and_mark_current_configuration(tmp_path: Path) -> None:
    summary = Path("docs/results/texas_2023_summary.json")
    outputs = build_release_figures(summary, tmp_path)
    assert len(outputs) == 2
    for output in outputs:
        assert output.read_text(encoding="utf-8").startswith("<svg")
    frontier = outputs[0].read_text(encoding="utf-8")
    assert "cfpb current" in frontier
    assert "Sample uniqueness" in frontier
    assert json.loads(summary.read_text())["population_uniqueness"]["status"] == "boundary_fit_not_reportable"
