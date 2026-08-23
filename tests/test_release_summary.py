import json
from pathlib import Path

from scripts.build_release_summary import DEFAULT_INPUTS, build_summary


def test_committed_summary_matches_aggregate_inputs_when_available() -> None:
    if not all(path.exists() for path in DEFAULT_INPUTS.values()):
        return
    expected = build_summary(DEFAULT_INPUTS)
    committed = json.loads(Path("docs/results/texas_2023_summary.json").read_text())
    assert committed == expected
