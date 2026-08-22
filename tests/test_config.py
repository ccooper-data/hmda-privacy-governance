from pathlib import Path

import pytest

from hmda_privacy.config import load_qi_config


def test_default_config_has_no_direct_identifiers() -> None:
    config = load_qi_config(Path("config/quasi_identifiers.yml"))
    assert not set(config.fields) & set(config.forbidden_direct_identifiers)


def test_config_rejects_direct_identifier_as_qi(tmp_path: Path) -> None:
    path = tmp_path / "bad.yml"
    path.write_text(
        """version: 1
name: bad
fields: [uli]
forbidden_direct_identifiers: [uli]
sensitive_attributes: [action_taken]
reporting: {minimum_cell_size: 20, k_thresholds: [1, 5, 10]}
""",
        encoding="utf-8",
    )
    with pytest.raises(ValueError, match="Direct identifiers"):
        load_qi_config(path)

