from __future__ import annotations

import json
from pathlib import Path

import pytest

from alignmentdelta.experiments.production_orchestrator import (
    CONTROL_SHA256,
    DIRECTION_SHA256,
    MODEL_ID,
    MODEL_REVISION,
    initialize_master_run,
    validate_technical_gate,
)


def _gate(tmp_path: Path) -> tuple[Path, dict]:
    manifest = initialize_master_run(tmp_path, repo_root=Path.cwd(), master_run_id="gate-test")
    gate = {
        "model_id": MODEL_ID,
        "model_revision": MODEL_REVISION,
        "scientific_code_commit": manifest["scientific_code_commit"],
        "protocol_hashes": manifest["protocol_hashes"],
        "direction_sha256": DIRECTION_SHA256,
        "layer": 27,
        "hidden_dimension": 2048,
        "status": "PRE_SCIENCE_TECHNICAL_GATE_PASS",
        "controls": {str(seed): {"sha256": digest} for seed, digest in CONTROL_SHA256.items()},
    }
    path = tmp_path / "manifests" / "technical_pre_science_gate.json"
    path.parent.mkdir(parents=True, exist_ok=True)
    path.write_text(json.dumps(gate), encoding="utf-8")
    return path, manifest


@pytest.mark.parametrize(
    ("field", "value"),
    [("scientific_code_commit", "stale"), ("model_revision", "stale"), ("direction_sha256", "stale")],
)
def test_technical_gate_rejects_stale_identity(tmp_path: Path, field: str, value: str) -> None:
    path, manifest = _gate(tmp_path)
    gate = json.loads(path.read_text())
    gate[field] = value
    path.write_text(json.dumps(gate), encoding="utf-8")
    with pytest.raises(RuntimeError, match="PRE_SCIENCE_GATE_REQUIRED"):
        validate_technical_gate(tmp_path, manifest)


def test_technical_gate_rejects_stale_protocol_hashes(tmp_path: Path) -> None:
    path, manifest = _gate(tmp_path)
    gate = json.loads(path.read_text())
    gate["protocol_hashes"][next(iter(gate["protocol_hashes"]))] = "stale"
    path.write_text(json.dumps(gate), encoding="utf-8")
    with pytest.raises(RuntimeError, match="PRE_SCIENCE_GATE_REQUIRED"):
        validate_technical_gate(tmp_path, manifest)


def test_technical_gate_rejects_stale_controls(tmp_path: Path) -> None:
    path, manifest = _gate(tmp_path)
    gate = json.loads(path.read_text())
    gate["controls"]["20260830"]["sha256"] = "stale"
    path.write_text(json.dumps(gate), encoding="utf-8")
    with pytest.raises(RuntimeError, match="PRE_SCIENCE_GATE_REQUIRED"):
        validate_technical_gate(tmp_path, manifest)
