"""Model-free validation for imported pre-science technical gates."""

from __future__ import annotations

import json
from pathlib import Path
from typing import Any, cast

from alignmentdelta.experiments.intervention_identity import (
    CONTROL_SHA256,
    DIRECTION_SHA256,
    HIDDEN_DIMENSION,
    LAYER,
    MODEL_ID,
    MODEL_REVISION,
)


def validate_gate_artifact(
    path: Path, *, expected_manifest: dict[str, Any], expected_code_commit: str
) -> dict[str, Any]:
    """Validate a sanitized technical-gate JSON without loading a model."""
    gate = json.loads(path.read_text(encoding="utf-8"))
    expected = {
        "scientific_code_commit": expected_code_commit,
        "model_id": MODEL_ID,
        "model_revision": MODEL_REVISION,
        "direction_sha256": DIRECTION_SHA256,
        "layer": LAYER,
        "hidden_dimension": HIDDEN_DIMENSION,
        "status": "PRE_SCIENCE_TECHNICAL_GATE_PASS",
    }
    if gate.get("scientific_code_commit") != expected["scientific_code_commit"]:
        raise RuntimeError("SCIENTIFIC_CODE_COMMIT_MISMATCH")
    if gate.get("direction_sha256") != DIRECTION_SHA256:
        raise RuntimeError("DIRECTION_IDENTITY_MISMATCH")
    if any(
        gate.get(key) != value
        for key, value in expected.items()
        if key not in {"scientific_code_commit", "direction_sha256"}
    ):
        raise RuntimeError("PRE_SCIENCE_GATE_REQUIRED")
    if gate.get("protocol_hashes") != expected_manifest.get("protocol_hashes"):
        raise RuntimeError("PROTOCOL_MANIFEST_MISMATCH")
    controls = gate.get("controls", {})
    observed = {
        int(seed): value.get("sha256")
        for seed, value in controls.items()
        if isinstance(value, dict) and "sha256" in value
    }
    if observed != CONTROL_SHA256:
        raise RuntimeError("CONTROL_IDENTITY_MISMATCH")
    return cast(dict[str, Any], gate)
