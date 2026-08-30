"""Tests for the Step 1.1 runtime foundation."""

from __future__ import annotations

import json
import random
from pathlib import Path

import numpy as np
import pytest

from alignmentdelta.diagnostics.cuda_smoke import run_cuda_smoke_test
from alignmentdelta.diagnostics.environment import _git_info
from alignmentdelta.execution import load_profile
from alignmentdelta.manifest import EnvironmentManifest
from alignmentdelta.precision import resolve_precision
from alignmentdelta.reproducibility import seed_everything

ROOT = Path(__file__).parents[1]


def test_profiles_load_and_are_immutable() -> None:
    profile = load_profile("cpu_test", ROOT / "configs" / "execution")
    assert profile.name == "cpu_test"
    assert profile.preferred_device == "cpu"
    assert profile.allow_quantization is False
    with pytest.raises(AttributeError):
        profile.name = "changed"  # type: ignore[misc]


def test_invalid_profile_is_rejected(tmp_path: Path) -> None:
    (tmp_path / "bad.toml").write_text('[profile]\nname = "bad"\n', encoding="utf-8")
    with pytest.raises(ValueError, match="required"):
        load_profile("bad", tmp_path)


def test_precision_resolution_is_explicit_for_cpu() -> None:
    assert resolve_precision("auto", device="cpu", cuda_bf16_supported=False) == "fp32"
    assert resolve_precision("fp16", device="cpu", cuda_bf16_supported=False) == "fp16"


def test_manifest_serializes_required_fields() -> None:
    manifest = EnvironmentManifest.minimal(
        execution_profile="cpu_test",
        seed=123,
        deterministic=True,
        quantization_enabled=False,
    )
    payload = manifest.to_dict()
    assert set(
        (
            "schema_version",
            "created_at_utc",
            "git",
            "host",
            "python",
            "packages",
            "pytorch",
            "cuda",
            "gpus",
            "execution_profile",
            "reproducibility",
            "quantization",
        )
    ).issubset(payload)
    assert payload["quantization"] == {"enabled": False, "method": None}
    json.dumps(payload)


def test_seed_reproducibility_for_python_and_numpy() -> None:
    seed_everything(42, deterministic=False)
    first = (random.random(), float(np.random.random()))
    seed_everything(42, deterministic=False)
    second = (random.random(), float(np.random.random()))
    assert first == second


def test_missing_bitsandbytes_is_not_an_error(monkeypatch: pytest.MonkeyPatch) -> None:
    monkeypatch.setitem(__import__("sys").modules, "bitsandbytes", None)
    manifest = EnvironmentManifest.minimal("cpu_test", 1, False, False)
    assert manifest.packages["bitsandbytes"] is None


def test_cuda_smoke_reports_unavailable_when_torch_is_missing(monkeypatch: pytest.MonkeyPatch) -> None:
    monkeypatch.setitem(__import__("sys").modules, "torch", None)
    assert run_cuda_smoke_test()["status"] == "unavailable"


def test_git_metadata_has_auditable_state() -> None:
    metadata = _git_info()
    assert metadata["root"] == str(ROOT).replace("\\", "/")
    assert isinstance(metadata["commit"], str)
    assert isinstance(metadata["dirty"], bool)
