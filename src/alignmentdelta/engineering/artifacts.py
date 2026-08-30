"""Engineering run metadata and deterministic artifact serialization."""

from __future__ import annotations

import hashlib
import json
from pathlib import Path
from typing import Any

import torch


def tensor_hash(tensor: torch.Tensor) -> str:
    value = tensor.detach().to(device="cpu", dtype=torch.float64).contiguous().numpy().tobytes()
    return hashlib.sha256(value).hexdigest()


def direction_artifact(
    *, model_id: str, revision: str, tokenizer_revision: str, template_hash: str,
    source_manifest_hash: str, subset_hash: str, layer: int, position_rule: str,
    raw_norm: float, direction: torch.Tensor, git_commit: str, environment_reference: str,
) -> dict[str, Any]:
    normalized = direction.detach().to(device="cpu", dtype=torch.float64).tolist()
    artifact: dict[str, Any] = {
        "schema_version": "3.0.0",
        "synthetic_test_only": False,
        "phase": "engineering",
        "scientific_execution": False,
        "model_id": model_id,
        "model_revision": revision,
        "tokenizer_revision": tokenizer_revision,
        "chat_template_hash": template_hash,
        "direction_source": "andyrdt/refusal_direction",
        "direction_revision": "9d852fae1a9121c78b29142de733cb1340770cc3",
        "train_manifest_hash": source_manifest_hash,
        "validation_manifest_hash": source_manifest_hash,
        "engineering_subset_hash": subset_hash,
        "selected_layer": layer,
        "selected_site": "engineering_only",
        "token_position_rule": position_rule,
        "raw_norm": raw_norm,
        "normalized_direction": normalized,
        "direction_dtype": "float64",
        "hidden_dimension": direction.numel(),
        "git_commit": git_commit,
        "environment_manifest_hash": environment_reference,
    }
    canonical = json.dumps(artifact, sort_keys=True, separators=(",", ":")).encode()
    artifact["artifact_sha256"] = hashlib.sha256(canonical).hexdigest()
    return artifact


def write_artifact(path: Path, artifact: dict[str, Any]) -> None:
    path.parent.mkdir(parents=True, exist_ok=True)
    temporary = path.with_suffix(path.suffix + ".tmp")
    temporary.write_text(json.dumps(artifact, indent=2, sort_keys=True) + "\n", encoding="utf-8")
    temporary.replace(path)
