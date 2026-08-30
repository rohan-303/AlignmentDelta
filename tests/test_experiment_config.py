"""Tests for the Step 1.2 experiment contract schema."""

from __future__ import annotations

from pathlib import Path

import pytest

from alignmentdelta.experiments.config import load_experiment_config

ROOT = Path(__file__).parents[1]
CONFIG = ROOT / "configs" / "experiments" / "example.schema.toml"


def test_placeholder_experiment_configuration_loads() -> None:
    config = load_experiment_config(CONFIG)
    assert config.schema_version == "0.1"
    assert config.phase == "pilot"
    assert config.source_model.identifier == "<MODEL_ID>"
    assert config.transformation.intervention_strength == 0.0
    assert config.reproducibility.planned_replicates == 1


def test_missing_required_section_is_rejected(tmp_path: Path) -> None:
    path = tmp_path / "missing.toml"
    path.write_text('[study]\nname = "example"\n', encoding="utf-8")
    with pytest.raises(ValueError, match="required"):
        load_experiment_config(path)


def test_unknown_field_is_rejected(tmp_path: Path) -> None:
    path = tmp_path / "unknown.toml"
    path.write_text(CONFIG.read_text(encoding="utf-8") + "\nextra_root = true\n", encoding="utf-8")
    with pytest.raises(ValueError, match="unknown"):
        load_experiment_config(path)


def test_invalid_transformation_parameters_are_rejected(tmp_path: Path) -> None:
    text = CONFIG.read_text(encoding="utf-8").replace(
        'parameters = { parameter_name = "<PARAMETER_VALUE>" }',
        'parameters = "<PARAMETERS_MUST_BE_A_TABLE>"',
    )
    path = tmp_path / "bad-parameters.toml"
    path.write_text(text, encoding="utf-8")
    with pytest.raises(ValueError, match="parameters"):
        load_experiment_config(path)


def test_invalid_intervention_strength_is_rejected(tmp_path: Path) -> None:
    text = CONFIG.read_text(encoding="utf-8").replace("intervention_strength = 0.0", "intervention_strength = 1.5")
    path = tmp_path / "bad-strength.toml"
    path.write_text(text, encoding="utf-8")
    with pytest.raises(ValueError, match="intervention_strength"):
        load_experiment_config(path)


def test_invalid_decoding_and_replicate_values_are_rejected(tmp_path: Path) -> None:
    text = (
        CONFIG.read_text(encoding="utf-8")
        .replace("temperature = 0.0", "temperature = -1.0")
        .replace("planned_replicates = 1", "planned_replicates = 0")
    )
    path = tmp_path / "bad-decoding.toml"
    path.write_text(text, encoding="utf-8")
    with pytest.raises(ValueError, match="temperature"):
        load_experiment_config(path)


def test_invalid_phase_is_rejected(tmp_path: Path) -> None:
    text = CONFIG.read_text(encoding="utf-8").replace('phase = "pilot"', 'phase = "completed"')
    path = tmp_path / "bad-phase.toml"
    path.write_text(text, encoding="utf-8")
    with pytest.raises(ValueError, match="phase"):
        load_experiment_config(path)
