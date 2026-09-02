from __future__ import annotations

import json
from pathlib import Path

import pytest

from alignmentdelta.experiments.execution_engine import (
    ALPHAS,
    CONTROL_SEEDS,
    EXPECTED_DIRECTION_SHA256,
    ExecutionConfig,
    atomic_write_json,
    build_conditions,
    chunk_conditions,
    direction_hash_gate,
    export_run,
    run_synthetic,
    validate_manifest_hashes,
    validate_sha256_identity,
)


def test_condition_expansion_has_one_baseline_and_31_states() -> None:
    conditions = build_conditions(["item-a"])
    assert len(conditions) == 31
    assert sum(c.intervention == "baseline" for c in conditions) == 1
    assert sum(c.intervention == "refusal" for c in conditions) == 6
    assert sum(c.intervention == "control" for c in conditions) == 24
    assert {c.alpha for c in conditions} == set(ALPHAS)
    assert {c.seed for c in conditions if c.intervention == "control"} == set(CONTROL_SEEDS)


def test_operation_accounting_counts_option_sequences_not_logical_states() -> None:
    from alignmentdelta.experiments.execution_engine import operation_accounting

    counts = operation_accounting(24, 12, 12)
    assert counts == {
        "representations": 60,
        "logical_condition_states": 1860,
        "unique_baseline_states": 60,
        "xstest_generations": 744,
        "mmlu_option_score_sequences": 1488,
        "consistency_original_option_score_sequences": 1488,
        "consistency_transformed_option_score_sequences": 1488,
        "actual_forward_calls": 5208,
    }


def test_direction_hash_gate_rejects_task_hash_mismatch() -> None:
    with pytest.raises(RuntimeError, match="DIRECTION_RECONSTRUCTION_MISMATCH"):
        direction_hash_gate("0" * 64)
    assert EXPECTED_DIRECTION_SHA256 == "286147ed00c828028d6856e5cab4e87ed5730e1e2f6f6fff047f2d3bb71a84b1"


def test_sha256_identity_fields_reject_malformed_values() -> None:
    validate_sha256_identity("a" * 64)
    with pytest.raises(ValueError):
        validate_sha256_identity("a" * 62)
    with pytest.raises(ValueError):
        validate_sha256_identity("g" * 64)


def test_manifest_hash_lock_rejects_changed_protocol(tmp_path: Path) -> None:
    manifest = tmp_path / "manifest.toml"
    manifest.write_text("x = 1\n", encoding="utf-8")
    with pytest.raises(RuntimeError, match="PROTOCOL_MANIFEST_MISMATCH"):
        validate_manifest_hashes({"manifest.toml": "bad"}, {"manifest.toml": manifest})


def test_synthetic_run_is_resumable_and_has_no_duplicate_keys(tmp_path: Path) -> None:
    config = ExecutionConfig.make_synthetic(tmp_path)
    first = run_synthetic(config)
    second = run_synthetic(config, resume=True)
    assert first["completed_count"] == second["completed_count"]
    records = [json.loads(line) for line in (tmp_path / "sanitized" / "records.jsonl").read_text().splitlines()]
    keys = [record["condition_key"] for record in records]
    assert len(keys) == len(set(keys))
    assert first["scientific_model_inference"] == 0


def test_atomic_write_and_safe_export_exclude_raw_and_weights(tmp_path: Path) -> None:
    path = tmp_path / "nested" / "record.json"
    atomic_write_json(path, {"ok": True})
    assert json.loads(path.read_text()) == {"ok": True}
    config = ExecutionConfig.make_synthetic(tmp_path)
    run_synthetic(config)
    archive = export_run(tmp_path, tmp_path / "export.tar.gz")
    assert archive.exists()
    import tarfile

    with tarfile.open(archive, "r:gz") as tar:
        names = tar.getnames()
    assert all("raw" not in name and "weights" not in name for name in names)


def test_chunking_is_deterministic() -> None:
    conditions = build_conditions(["b", "a"])
    assert chunk_conditions(conditions, 1, 3) == chunk_conditions(conditions, 1, 3)
    assert set(sum((chunk_conditions(conditions, i, 3) for i in range(3)), [])) == set(conditions)


def test_real_execution_requires_explicit_cloud_profile() -> None:
    from alignmentdelta.experiments.execution_engine import require_real_execution

    require_real_execution(False, None)
    with pytest.raises(RuntimeError, match="cloud_gpu"):
        require_real_execution(True, None)
