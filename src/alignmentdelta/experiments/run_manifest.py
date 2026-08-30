"""Auditable run metadata, status transitions, and failure records."""

from __future__ import annotations

from dataclasses import asdict, dataclass
from datetime import UTC, datetime
from enum import StrEnum
from typing import Any


class RunStatus(StrEnum):
    PLANNED = "planned"
    RUNNING = "running"
    PILOT = "pilot"
    COMPLETED = "completed"
    FAILED = "failed"
    INVALIDATED = "invalidated"


_ALLOWED_TRANSITIONS: dict[RunStatus, frozenset[RunStatus]] = {
    RunStatus.PLANNED: frozenset({RunStatus.RUNNING}),
    RunStatus.RUNNING: frozenset({RunStatus.PILOT, RunStatus.COMPLETED, RunStatus.FAILED}),
    RunStatus.PILOT: frozenset({RunStatus.INVALIDATED}),
    RunStatus.COMPLETED: frozenset({RunStatus.INVALIDATED}),
    RunStatus.FAILED: frozenset(),
    RunStatus.INVALIDATED: frozenset(),
}


def transition_status(current: RunStatus | str, target: RunStatus | str) -> RunStatus:
    """Validate and return a legal next status; failures are terminal."""
    current_status = RunStatus(current)
    target_status = RunStatus(target)
    if target_status not in _ALLOWED_TRANSITIONS[current_status]:
        raise ValueError(f"illegal run status transition: {current_status.value} -> {target_status.value}")
    return target_status


def utc_now() -> str:
    return datetime.now(UTC).isoformat().replace("+00:00", "Z")


@dataclass(frozen=True, slots=True)
class FailureRecord:
    category: str
    message: str
    stage: str
    timestamp_utc: str
    retry_appropriate: bool
    exception_type: str | None = None

    def __post_init__(self) -> None:
        for name in ("category", "message", "stage", "timestamp_utc"):
            if not getattr(self, name).strip():
                raise ValueError(f"{name} must be nonempty")


@dataclass(frozen=True, slots=True)
class InvalidationRecord:
    reason_category: str
    explanation: str
    timestamp_utc: str
    exclude_from_primary_analysis: bool
    discovery_git_commit: str | None = None

    def __post_init__(self) -> None:
        if not self.reason_category.strip() or not self.explanation.strip() or not self.timestamp_utc.strip():
            raise ValueError("invalidation category, explanation, and timestamp must be nonempty")


@dataclass(frozen=True, slots=True)
class RunManifest:
    schema_version: str
    run_id: str
    experiment_condition_id: str
    created_at_utc: str
    status: RunStatus
    experiment_config_reference: str
    experiment_config_hash: str
    git_commit: str
    git_dirty: bool
    environment_manifest_reference: str
    execution_profile: str
    process_seed: int
    output_directory: str
    started_at_utc: str | None = None
    completed_at_utc: str | None = None
    failure: FailureRecord | None = None
    invalidation: InvalidationRecord | None = None
    scientific_execution: bool = False

    def __post_init__(self) -> None:
        for name in (
            "schema_version",
            "run_id",
            "experiment_condition_id",
            "created_at_utc",
            "experiment_config_reference",
            "experiment_config_hash",
            "git_commit",
            "environment_manifest_reference",
            "execution_profile",
            "output_directory",
        ):
            if not getattr(self, name).strip():
                raise ValueError(f"{name} must be nonempty")
        if self.process_seed < 0:
            raise ValueError("process_seed must be non-negative")
        if self.status == RunStatus.FAILED and self.failure is None:
            raise ValueError("failed runs require a failure record")
        if self.status == RunStatus.INVALIDATED and self.invalidation is None:
            raise ValueError("invalidated runs require an invalidation record")
        if self.status in {RunStatus.COMPLETED, RunStatus.PILOT} and self.completed_at_utc is None:
            raise ValueError("completed and pilot runs require completed_at_utc")

    def to_dict(self) -> dict[str, Any]:
        data = asdict(self)
        data["status"] = self.status.value
        return data
