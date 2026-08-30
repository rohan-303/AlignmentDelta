from pathlib import Path

import pytest

from alignmentdelta.experiments.dry_run import main as dry_run_main
from alignmentdelta.experiments.validate_config import main as validate_main

ROOT = Path(__file__).parents[1]
CONFIG = ROOT / "configs" / "experiments" / "example.schema.toml"


def test_validation_cli_prints_condition_summary(capsys: pytest.CaptureFixture[str]) -> None:
    assert validate_main([str(CONFIG)]) == 0
    output = capsys.readouterr().out
    assert "experiment_condition_id: condition-" in output
    assert "scientific_execution: false" in output


def test_dry_run_writes_planned_artifact_outside_results(tmp_path: Path, capsys: pytest.CaptureFixture[str]) -> None:
    assert dry_run_main([str(CONFIG), "--output-dir", str(tmp_path)]) == 0
    output = capsys.readouterr().out
    assert "status: planned" in output
    manifest_paths = list(tmp_path.rglob("run_manifest.json"))
    assert len(manifest_paths) == 1
    manifest_text = manifest_paths[0].read_text(encoding="utf-8")
    assert '"scientific_execution": false' in manifest_text
    assert not (ROOT / "results" / "run_manifest.json").exists()


def test_dry_run_rejects_results_directory(tmp_path: Path) -> None:
    with pytest.raises(ValueError, match="must not be under results"):
        dry_run_main([str(CONFIG), "--output-dir", str(tmp_path / "results")])
