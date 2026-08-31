from __future__ import annotations

import json
from pathlib import Path

from alignmentdelta.experiments.production_orchestrator import (
    EXPECTED_LOGICAL_CONDITIONS,
    FakeScientificAdapter,
    initialize_master_run,
    run_mocked_production,
    validate_master_manifest,
)


def test_initialize_master_run_freezes_protocol_identity(tmp_path: Path) -> None:
    manifest = initialize_master_run(tmp_path, repo_root=Path.cwd(), master_run_id="master-test")
    assert manifest["master_run_id"] == "master-test"
    assert manifest["status"] == "planned"
    assert manifest["scientific_execution"] is True
    assert manifest["logical_condition_count"] == EXPECTED_LOGICAL_CONDITIONS
    assert len(manifest["protocol_hashes"]) >= 5
    assert (tmp_path / "master_manifest.json").exists()
    validate_master_manifest(tmp_path, repo_root=Path.cwd())


def test_full_mocked_production_has_frozen_cardinalities_and_exports(tmp_path: Path) -> None:
    result = run_mocked_production(tmp_path, repo_root=Path.cwd(), adapter=FakeScientificAdapter())
    assert result["logical_condition_count"] == 1860
    assert result["record_count"] == 1488
    assert result["xstest_records"] == 744
    assert result["mmlu_records"] == 372
    assert result["consistency_records"] == 372
    assert result["status"] == "completed"
    assert (tmp_path / "step_4_0_sanitized_export.tar.gz").exists()
    assert (tmp_path / "step_4_0_sensitive_annotation_export.tar.gz").exists()
    records = [json.loads(line) for line in (tmp_path / "sanitized" / "records.jsonl").read_text().splitlines()]
    assert len(records) == 1488
    assert all("response_text" not in row and "question" not in row for row in records)


def test_mock_resume_does_not_duplicate_records(tmp_path: Path) -> None:
    first = run_mocked_production(tmp_path, repo_root=Path.cwd(), adapter=FakeScientificAdapter(), stop_after=17)
    assert first["status"] == "running"
    second = run_mocked_production(tmp_path, repo_root=Path.cwd(), adapter=FakeScientificAdapter(), resume=True)
    assert second["status"] == "completed"
    assert second["record_count"] == 1488
    rows = (tmp_path / "sanitized" / "records.jsonl").read_text().splitlines()
    assert len(rows) == len({json.loads(row)["condition_key"] for row in rows})
