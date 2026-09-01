from __future__ import annotations

import hashlib
import json
import sys
from pathlib import Path
from types import SimpleNamespace

import pytest

from alignmentdelta.experiments import prepare_cloud_data as hydration
from alignmentdelta.experiments.prepare_cloud_data import SourceSpec


def test_source_registry_has_explicit_backends() -> None:
    assert [(s.name, s.backend) for s in hydration.SOURCES] == [
        ("refusal_direction", "github"),
        ("xstest", "github"),
        ("mmlu", "huggingface_dataset"),
    ]


def test_github_sources_do_not_use_huggingface(monkeypatch: pytest.MonkeyPatch, tmp_path: Path) -> None:
    calls: list[str] = []

    def fake_hydrate(spec: SourceSpec, destination: Path) -> None:
        calls.append(f"github:{spec.name}")

    def fake_dataset(spec: SourceSpec, destination: Path) -> None:
        calls.append(f"dataset:{spec.name}")

    monkeypatch.setattr(hydration, "_hydrate_github", fake_hydrate)
    monkeypatch.setattr(hydration, "_hydrate_dataset", fake_dataset)
    monkeypatch.setattr(hydration, "_validate_refusal", lambda destination: {})
    monkeypatch.setattr(hydration, "_validate_xstest", lambda destination, repo_root: {})
    monkeypatch.setattr(hydration, "_materialize_mmlu", lambda destination, repo_root: {})
    monkeypatch.setattr(
        hydration,
        "_write_metadata",
        lambda destination, spec: destination.mkdir(parents=True, exist_ok=True),
    )
    hydration.hydrate(tmp_path, repo_root=Path.cwd())
    assert calls == ["github:refusal_direction", "github:xstest", "dataset:mmlu"]


def test_mmlu_backend_uses_dataset_semantics(monkeypatch: pytest.MonkeyPatch, tmp_path: Path) -> None:
    calls: list[dict[str, object]] = []

    def fake_snapshot_download(**kwargs: object) -> None:
        calls.append(kwargs)
        (Path(str(kwargs["local_dir"])) / "dataset.parquet").parent.mkdir(parents=True)
        (Path(str(kwargs["local_dir"])) / "dataset.parquet").write_bytes(b"fixture")

    monkeypatch.setitem(sys.modules, "huggingface_hub", SimpleNamespace(snapshot_download=fake_snapshot_download))
    spec = next(spec for spec in hydration.SOURCES if spec.name == "mmlu")
    hydration._hydrate_dataset(spec, tmp_path / "mmlu")
    assert calls == [
        {
            "repo_id": "cais/mmlu",
            "repo_type": "dataset",
            "revision": hydration.MMLU_REVISION,
            "local_dir": calls[0]["local_dir"],
        }
    ]


def test_verify_mode_never_hydrates_or_downloads(monkeypatch: pytest.MonkeyPatch, tmp_path: Path) -> None:
    for spec in hydration.SOURCES:
        destination = tmp_path / spec.name / spec.revision
        destination.mkdir(parents=True)
        hydration._write_metadata(destination, spec)
    monkeypatch.setattr(hydration, "_hydrate_github", lambda spec, destination: pytest.fail("network hydration"))
    monkeypatch.setattr(hydration, "_hydrate_dataset", lambda spec, destination: pytest.fail("network hydration"))
    monkeypatch.setattr(hydration, "_validate_refusal", lambda destination: {})
    monkeypatch.setattr(hydration, "_validate_xstest", lambda destination, repo_root: {})
    monkeypatch.setattr(hydration, "_verify_mmlu_materialized", lambda destination, repo_root: {})
    hydration.hydrate(tmp_path, repo_root=Path.cwd(), verify_only=True)


def test_refusal_validator_requires_nested_pinned_layout(monkeypatch: pytest.MonkeyPatch, tmp_path: Path) -> None:
    split_paths = hydration.refusal_split_paths(tmp_path)
    counts = {name: 2 for name in split_paths}
    hashes: dict[str, str] = {}
    for name, path in split_paths.items():
        path.parent.mkdir(parents=True, exist_ok=True)
        path.write_text(json.dumps([{"id": 1}, {"id": 2}]), encoding="utf-8")
        hashes[name] = hashlib.sha256(path.read_bytes()).hexdigest()
    monkeypatch.setattr(hydration, "REFUSAL_SPLIT_SHA256", hashes)
    monkeypatch.setattr(hydration, "REFUSAL_SPLIT_COUNTS", counts)
    result = hydration._validate_refusal(tmp_path)
    assert result["counts"] == counts
    assert all(relative.replace("\\", "/").startswith("dataset/splits/") for relative in result["files"])


def test_partial_mmlu_cache_rematerializes_without_redownload(monkeypatch: pytest.MonkeyPatch, tmp_path: Path) -> None:
    for spec in hydration.SOURCES:
        destination = tmp_path / spec.name / spec.revision
        destination.mkdir(parents=True)
        hydration._write_metadata(destination, spec)
    monkeypatch.setattr(hydration, "_hydrate_github", lambda spec, destination: pytest.fail("redownload"))
    monkeypatch.setattr(hydration, "_hydrate_dataset", lambda spec, destination: pytest.fail("redownload"))
    monkeypatch.setattr(hydration, "_validate_refusal", lambda destination: {})
    monkeypatch.setattr(hydration, "_validate_xstest", lambda destination, repo_root: {})
    def incomplete_materialization(destination: Path, repo_root: Path) -> dict[str, object]:
        raise RuntimeError("HYDRATED_CACHE_REQUIRED")

    monkeypatch.setattr(hydration, "_verify_mmlu_materialized", incomplete_materialization)
    repaired: list[Path] = []
    monkeypatch.setattr(
        hydration,
        "_materialize_mmlu",
        lambda destination, repo_root: repaired.append(destination) or {"repaired": True},
    )
    result = hydration.hydrate(tmp_path, repo_root=Path.cwd())
    assert result["mmlu"]["repaired"] is True
    assert repaired == [tmp_path / "mmlu" / hydration.MMLU_REVISION]


def test_mmlu_scope_excludes_aggregate_and_auxiliary_paths(tmp_path: Path) -> None:
    universe = {"abstract_algebra/dev-00000-of-00001.parquet"}
    accepted = tmp_path / "abstract_algebra" / "dev-00000-of-00001.parquet"
    aggregate = tmp_path / "all" / "dev-00000-of-00001.parquet"
    auxiliary = tmp_path / "auxiliary_train" / "train-00000-of-00001.parquet"
    assert hydration._classify_mmlu_path(accepted, tmp_path, universe) == ("abstract_algebra", "dev")
    assert hydration._classify_mmlu_path(aggregate, tmp_path, universe) is None
    assert hydration._classify_mmlu_path(auxiliary, tmp_path, universe) is None


def test_mmlu_category_manifest_is_exact_and_frozen() -> None:
    universe = hydration._mmlu_parquet_universe(Path.cwd())
    categories = hydration._mmlu_subject_categories(Path.cwd(), universe)
    assert len(categories) == 57
    assert set(categories.values()) <= {"STEM", "humanities", "social_sciences", "other"}
