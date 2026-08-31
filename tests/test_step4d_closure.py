from __future__ import annotations

import json
from pathlib import Path

import pytest

from alignmentdelta.experiments.production_orchestrator import (
    FakeScientificAdapter,
    run_mocked_production,
    verify_archive,
)


class TransientAdapter(FakeScientificAdapter):
    def __init__(self) -> None:
        self.calls = 0

    def _once(self) -> None:
        self.calls += 1
        if self.calls == 1:
            raise RuntimeError("transient model boundary failure")

    def generate(self, item: dict, condition: dict) -> dict:
        self._once()
        return super().generate(item, condition)

    def score_options(self, item: dict, condition: dict) -> list[float]:
        self._once()
        return super().score_options(item, condition)

    def score_consistency(self, pair: dict, condition: dict) -> tuple[list[float], list[float]]:
        self._once()
        return super().score_consistency(pair, condition)


def test_real_orchestrator_retries_transient_condition(tmp_path: Path) -> None:
    result = run_mocked_production(tmp_path, repo_root=Path.cwd(), adapter=TransientAdapter(), stop_after=1)
    assert result["record_count"] == 1
    progress = json.loads((tmp_path / "progress.json").read_text())
    assert any(item["attempt_count"] == 2 for item in progress["conditions"] if item["lifecycle_state"] == "completed")


def test_resume_rejects_corrupt_completed_record(tmp_path: Path) -> None:
    run_mocked_production(tmp_path, repo_root=Path.cwd(), adapter=FakeScientificAdapter(), stop_after=1)
    path = tmp_path / "sanitized" / "records.jsonl"
    row = json.loads(path.read_text().splitlines()[0])
    row["condition_key"] = "tampered"
    path.write_text(json.dumps(row) + "\n")
    result = run_mocked_production(
        tmp_path, repo_root=Path.cwd(), adapter=FakeScientificAdapter(), resume=True, stop_after=1
    )
    assert result["record_count"] == 1
    failures = json.loads((tmp_path / "failures.json").read_text())
    assert failures[0]["safe_error_type"] == "CORRUPT_ARTIFACT"




class AlwaysFailAdapter(FakeScientificAdapter):
    def generate(self, item: dict, condition: dict) -> dict:
        raise ValueError("malformed generation")

    def score_options(self, item: dict, condition: dict) -> list[float]:
        raise ValueError("malformed scores")

    def score_consistency(self, pair: dict, condition: dict) -> tuple[list[float], list[float]]:
        raise ValueError("malformed consistency")


def test_repeated_failure_persists_failed_lifecycle(tmp_path: Path) -> None:
    with pytest.raises(RuntimeError, match="CONDITION_FAILED"):
        run_mocked_production(tmp_path, repo_root=Path.cwd(), adapter=AlwaysFailAdapter(), stop_after=1)
    progress = json.loads((tmp_path / "progress.json").read_text())
    assert progress["status"] == "failed"
    assert progress["conditions"][-1]["lifecycle_state"] == "failed"
    assert progress["conditions"][-1]["attempt_count"] == 2


def test_archive_verification_rejects_hash_mismatch(tmp_path: Path) -> None:
    run_mocked_production(tmp_path, repo_root=Path.cwd(), adapter=FakeScientificAdapter())
    archive = tmp_path / "step_4_0_sanitized_export.tar.gz"
    manifest = json.loads((tmp_path / "manifests" / "archive_manifest.json").read_text())
    manifest[0]["sha256"] = "0" * 64
    with pytest.raises(RuntimeError, match="EXPORT_VERIFICATION_FAILED"):
        verify_archive(archive, manifest)
