from __future__ import annotations

import json
from pathlib import Path

import pytest

from alignmentdelta.experiments import cloud_adapter, production_orchestrator
from alignmentdelta.experiments.intervention_identity import (
    CONTROL_SEEDS,
    CONTROL_SHA256,
    DIRECTION_SHA256,
    HIDDEN_DIMENSION,
    LAYER,
    MODEL_ID,
    MODEL_REVISION,
)
from alignmentdelta.experiments.production_orchestrator import initialize_master_run, validate_technical_gate
from alignmentdelta.experiments.technical_gate_validator import validate_gate_artifact

OLD_DIRECTION_SHA256 = "5a8983bcbe4402096210485f8f9b0191eb35b3de84f46624e2dd9811fd09a3fe"


def _gate(tmp_path: Path) -> tuple[Path, dict[str, object]]:
    manifest = initialize_master_run(tmp_path, repo_root=Path.cwd(), master_run_id="step4l-gate")
    gate = {
        "model_id": MODEL_ID,
        "model_revision": MODEL_REVISION,
        "scientific_code_commit": manifest["scientific_code_commit"],
        "protocol_hashes": manifest["protocol_hashes"],
        "direction_sha256": DIRECTION_SHA256,
        "layer": LAYER,
        "hidden_dimension": HIDDEN_DIMENSION,
        "status": "PRE_SCIENCE_TECHNICAL_GATE_PASS",
        "controls": {
            str(seed): {"sha256": digest, "norm": 1.0, "absolute_dot": 0.0}
            for seed, digest in CONTROL_SHA256.items()
        },
    }
    path = tmp_path / "manifests" / "technical_pre_science_gate.json"
    path.parent.mkdir(parents=True, exist_ok=True)
    path.write_text(json.dumps(gate), encoding="utf-8")
    return path, manifest


def test_active_experiment_config_uses_canonical_identity() -> None:
    import tomllib

    config = tomllib.loads((Path.cwd() / "configs/experiments/exploratory_qwen3b.toml").read_text(encoding="utf-8"))
    assert config["expected_direction_sha256"] == DIRECTION_SHA256
    assert config["control_seeds"] == list(CONTROL_SEEDS)
    assert config["control_sha256"] == [CONTROL_SHA256[seed] for seed in CONTROL_SEEDS]


def test_one_canonical_identity_is_shared_by_cloud_and_orchestrator() -> None:
    assert cloud_adapter.EXPECTED_MODEL_ID == MODEL_ID == production_orchestrator.MODEL_ID
    assert cloud_adapter.EXPECTED_MODEL_REVISION == MODEL_REVISION == production_orchestrator.MODEL_REVISION
    assert cloud_adapter.EXPECTED_DIRECTION_SHA256 == DIRECTION_SHA256 == production_orchestrator.DIRECTION_SHA256
    assert cloud_adapter.EXPECTED_CONTROL_SHA256 == CONTROL_SHA256 == production_orchestrator.CONTROL_SHA256
    assert production_orchestrator.CONTROL_SEEDS == CONTROL_SEEDS


def test_new_master_manifest_and_matching_gate_use_canonical_identity(tmp_path: Path) -> None:
    path, manifest = _gate(tmp_path)
    assert manifest["direction_expected_sha256"] == DIRECTION_SHA256
    assert manifest["control_seeds"] == list(CONTROL_SEEDS)
    assert validate_technical_gate(tmp_path, manifest)["status"] == "PRE_SCIENCE_TECHNICAL_GATE_PASS"

    validate_gate_artifact(
        path,
        expected_manifest=manifest,
        expected_code_commit=str(manifest["scientific_code_commit"]),
    )


def test_historical_identity_fails_gate_validation(tmp_path: Path) -> None:
    path, manifest = _gate(tmp_path)
    gate = json.loads(path.read_text(encoding="utf-8"))
    gate["direction_sha256"] = OLD_DIRECTION_SHA256
    path.write_text(json.dumps(gate), encoding="utf-8")
    with pytest.raises(RuntimeError, match="PRE_SCIENCE_GATE_REQUIRED"):
        validate_technical_gate(tmp_path, manifest)
    with pytest.raises(RuntimeError, match="DIRECTION_IDENTITY_MISMATCH"):
        validate_gate_artifact(
            path,
            expected_manifest=manifest,
            expected_code_commit=str(manifest["scientific_code_commit"]),
        )
