import json
from pathlib import Path

import pytest

from alignmentdelta.engineering.artifact_transfer import (
    archive_manifest,
    create_archive,
    verify_archive_hash,
    verify_import_manifest,
)
from alignmentdelta.engineering.cloud_gate import (
    MIN_VRAM_BYTES,
    classify_environment,
    validate_cloud_cli_args,
)
from alignmentdelta.engineering.model_registry import QWEN25_3B, get_model_spec


def test_qwen3b_registry_is_exact_and_non_remote() -> None:
    assert get_model_spec("qwen2.5-3b") == QWEN25_3B
    assert QWEN25_3B.model_id == "Qwen/Qwen2.5-3B-Instruct"
    assert QWEN25_3B.revision == "aa8e72537993ba99e69dfaafa59ed015b17504d1"
    assert QWEN25_3B.trust_remote_code is False
    assert QWEN25_3B.role == "primary_technical"


def test_cloud_gate_requires_cuda_bf16_vram_and_disk() -> None:
    report = {
        "cuda_available": True,
        "bf16_supported": True,
        "total_vram_bytes": MIN_VRAM_BYTES,
        "free_disk_bytes": 12 * 1024**3,
    }
    result = classify_environment(report)
    assert result["classification"] == "eligible_cloud_gpu"
    blocked = classify_environment({**report, "total_vram_bytes": MIN_VRAM_BYTES - 1})
    assert blocked["classification"] == "insufficient_gpu"
    assert "vram_below_minimum" in blocked["reasons"]


def test_local_profile_is_never_allowed_to_run_qwen3b() -> None:
    report = {
        "profile": "local_dev",
        "cuda_available": True,
        "bf16_supported": True,
        "total_vram_bytes": 24 * 1024**3,
        "free_disk_bytes": 24 * 1024**3,
    }
    result = classify_environment(report)
    assert result["classification"] == "insufficient_gpu"
    assert "local_profile_forbidden" in result["reasons"]


def test_cloud_cli_rejects_wrong_model_or_profile() -> None:
    with pytest.raises(ValueError, match="model"):
        validate_cloud_cli_args("qwen2.5-1.5b", "cloud_gpu")
    with pytest.raises(ValueError, match="profile"):
        validate_cloud_cli_args("qwen2.5-3b", "local_dev")
    validate_cloud_cli_args("qwen2.5-3b", "cloud_gpu")


def test_archive_manifest_excludes_weights_and_verifies_import(tmp_path: Path) -> None:
    source = tmp_path / "pilot"
    source.mkdir()
    (source / "run_manifest.json").write_text(
        json.dumps({"run_id": "run-1", "git_commit": "abc", "model": {"revision": "rev-1"}}),
        encoding="utf-8",
    )
    (source / "model.safetensors").write_bytes(b"must not archive")
    manifest = archive_manifest(source)
    assert manifest["included_files"] == ["run_manifest.json"]
    verify_import_manifest(manifest, {"run_id": "run-1", "git_commit": "abc", "model_revision": "rev-1"})
    archive = tmp_path / "step_3_2.tar.gz"
    exported = create_archive(source, archive)
    verify_archive_hash(archive, exported["archive_sha256"])
    with pytest.raises(ValueError, match="commit"):
        verify_import_manifest(manifest, {"run_id": "run-1", "git_commit": "wrong", "model_revision": "rev-1"})
