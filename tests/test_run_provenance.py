from pathlib import Path

import pytest

from alignmentdelta.experiments.atomic import atomic_write_json
from alignmentdelta.experiments.run_manifest import (
    FailureRecord,
    InvalidationRecord,
    RunManifest,
    RunPhase,
    RunStatus,
    transition_status,
)


def manifest(status: RunStatus = RunStatus.PLANNED, **kwargs: object) -> RunManifest:
    defaults: dict[str, object] = {
        "schema_version": "0.1",
        "run_id": "run-placeholder-001",
        "experiment_condition_id": "condition-placeholder-001",
        "created_at_utc": "2026-01-01T00:00:00Z",
        "status": status,
        "phase": RunPhase.EXPLORATORY_PILOT,
        "experiment_config_reference": "configs/experiments/example.schema.toml",
        "experiment_config_hash": "sha256:placeholder",
        "git_commit": "placeholder-commit",
        "git_dirty": False,
        "environment_manifest_reference": "artifacts/diagnostics/environment.json",
        "execution_profile": "cpu_test",
        "process_seed": 0,
        "output_directory": "artifacts/runs/condition-placeholder-001/run-placeholder-001",
    }
    defaults.update(kwargs)
    return RunManifest(**defaults)  # type: ignore[arg-type]


def test_run_manifest_serializes_without_observations() -> None:
    data = manifest().to_dict()
    assert data["status"] == "planned"
    assert "observations" not in data
    assert data["scientific_execution"] is False


def test_status_transitions_are_explicit() -> None:
    assert transition_status("planned", "running") == RunStatus.RUNNING
    assert transition_status("running", "failed") == RunStatus.FAILED
    assert transition_status("completed", "invalidated") == RunStatus.INVALIDATED
    with pytest.raises(ValueError, match="illegal"):
        transition_status("failed", "completed")


def test_run_phase_is_separate_from_lifecycle_status() -> None:
    assert {phase.value for phase in RunPhase} == {
        "engineering",
        "technical_pilot",
        "exploratory_pilot",
        "confirmatory",
    }
    assert {status.value for status in RunStatus} == {
        "planned",
        "running",
        "completed",
        "failed",
        "invalidated",
    }
    assert manifest().to_dict()["phase"] == "exploratory_pilot"


def test_failure_and_invalidation_records_serialize() -> None:
    failure = FailureRecord(
        "configuration_error", "placeholder failure", "validation", "2026-01-01T00:00:00Z", True, "ValueError"
    )
    failed = manifest(RunStatus.FAILED, failure=failure)
    assert failed.to_dict()["failure"]["exception_type"] == "ValueError"
    invalidation = InvalidationRecord(
        "protocol_violation", "placeholder explanation", "2026-01-01T00:00:00Z", True, "placeholder-commit"
    )
    invalidated = manifest(RunStatus.INVALIDATED, invalidation=invalidation)
    assert invalidated.to_dict()["invalidation"]["exclude_from_primary_analysis"] is True


def test_atomic_json_write_replaces_destination(tmp_path: Path) -> None:
    path = tmp_path / "nested" / "manifest.json"
    atomic_write_json(path, {"status": "planned", "scientific_execution": False})
    assert path.read_text(encoding="utf-8") == '{\n  "scientific_execution": false,\n  "status": "planned"\n}\n'
    assert not list(path.parent.glob("*.tmp"))


def test_completed_and_invalidated_records_require_their_record() -> None:
    with pytest.raises(ValueError, match="failure"):
        manifest(RunStatus.FAILED)
    with pytest.raises(ValueError, match="invalidation"):
        manifest(RunStatus.INVALIDATED)
