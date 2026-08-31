from __future__ import annotations

import hashlib
from pathlib import Path

import pytest
import torch

from alignmentdelta.experiments.production_orchestrator import (
    cache_direction,
    load_cached_direction,
)


def test_direction_cache_round_trip_validates_identity(tmp_path: Path) -> None:
    direction = torch.zeros(2048, dtype=torch.float32)
    direction[0] = 1.0
    digest = hashlib.sha256(direction.numpy().tobytes()).hexdigest()
    cache_direction(
        tmp_path,
        direction,
        model_id="model",
        model_revision="rev",
        source_revision="source",
        source_manifest_hash="manifest",
        code_commit="commit",
        expected_sha256=digest,
    )
    loaded = load_cached_direction(
        tmp_path,
        expected={
            "sha256": digest,
            "model_id": "model",
            "model_revision": "rev",
            "source_revision": "source",
            "source_manifest_hash": "manifest",
            "code_commit": "commit",
            "layer": 27,
            "hidden_dimension": 2048,
        },
    )
    assert torch.equal(loaded, direction)


def test_direction_cache_rejects_tampered_tensor(tmp_path: Path) -> None:
    direction = torch.zeros(2048, dtype=torch.float32)
    direction[0] = 1.0
    digest = hashlib.sha256(direction.numpy().tobytes()).hexdigest()
    cache_direction(
        tmp_path,
        direction,
        model_id="model",
        model_revision="rev",
        source_revision="source",
        source_manifest_hash="manifest",
        code_commit="commit",
        expected_sha256=digest,
    )
    torch.save(torch.ones(2048), tmp_path / "refusal_direction.pt")
    with pytest.raises(RuntimeError, match="DIRECTION_CACHE_INVALID"):
        load_cached_direction(
            tmp_path,
            expected={
                "sha256": digest,
                "model_id": "model",
                "model_revision": "rev",
                "source_revision": "source",
                "source_manifest_hash": "manifest",
                "code_commit": "commit",
                "layer": 27,
                "hidden_dimension": 2048,
            },
        )
