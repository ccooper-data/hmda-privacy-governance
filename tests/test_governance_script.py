import os
import shutil
import subprocess
import sys
from pathlib import Path


def test_governance_script_fails_for_unauthorized_gold_model(tmp_path: Path) -> None:
    source = Path.cwd()
    shutil.copytree(source / "models", tmp_path / "models")
    shutil.copytree(source / "config", tmp_path / "config")
    (tmp_path / "models/gold/rogue_publication.sql").write_text(
        "select lei from {{ ref('fct_application') }}", encoding="utf-8"
    )
    completed = subprocess.run(
        [sys.executable, str(source / "scripts/check_governance.py")],
        cwd=tmp_path,
        text=True,
        capture_output=True,
        check=False,
        env={**os.environ, "PYTHONPATH": str(source / "src")},
    )
    assert completed.returncode == 1
    assert "ModuleNotFoundError" not in completed.stderr
    assert "UNDECLARED_GOLD_MODEL" in completed.stdout
