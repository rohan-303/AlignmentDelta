"""Safe packaging and import-back verification for cloud technical artifacts."""

from __future__ import annotations

import hashlib
import json
import tarfile
from pathlib import Path
from typing import Any

_FORBIDDEN_SUFFIXES = {".safetensors", ".bin", ".ckpt", ".pt", ".pth", ".onnx"}
_FORBIDDEN_PARTS = {".cache", "huggingface", "weights", "secrets"}


def _allowed(path: Path) -> bool:
    lowered = {part.lower() for part in path.parts}
    name = path.name.lower()
    secret_name = name == ".env" or name.startswith(".env.") or name in {"credentials.json", "token.txt"}
    return (
        path.suffix.lower() not in _FORBIDDEN_SUFFIXES
        and not lowered.intersection(_FORBIDDEN_PARTS)
        and not secret_name
    )


def archive_manifest(source: Path) -> dict[str, Any]:
    """Return a deterministic manifest of exportable files, excluding model/cache data."""
    files = sorted(path for path in source.rglob("*") if path.is_file() and _allowed(path.relative_to(source)))
    entries = [
        {
            "path": str(path.relative_to(source)).replace("\\", "/"),
            "bytes": path.stat().st_size,
            "sha256": hashlib.sha256(path.read_bytes()).hexdigest(),
        }
        for path in files
    ]
    result: dict[str, Any] = {
        "schema_version": "3.2.0",
        "artifact_root": "artifacts/pilot/step_3_2",
        "included_files": [entry["path"] for entry in entries],
        "files": entries,
        "exclusions": ["model weights", "Hugging Face cache", "secrets", "raw harmful text"],
    }
    run_manifest_path = source / "run_manifest.json"
    if run_manifest_path.is_file():
        result["run_manifest"] = json.loads(run_manifest_path.read_text(encoding="utf-8"))
    return result


def create_archive(source: Path, destination: Path) -> dict[str, Any]:
    manifest = archive_manifest(source)
    destination.parent.mkdir(parents=True, exist_ok=True)
    with tarfile.open(destination, "w:gz") as archive:
        for relative in manifest["included_files"]:
            archive.add(source / relative, arcname=relative, recursive=False)
    manifest["archive"] = str(destination)
    manifest["archive_sha256"] = hashlib.sha256(destination.read_bytes()).hexdigest()
    return manifest


def verify_archive_hash(archive: Path, expected_sha256: str) -> None:
    actual = hashlib.sha256(archive.read_bytes()).hexdigest()
    if actual != expected_sha256:
        raise ValueError("cloud artifact archive SHA-256 mismatch")


def verify_import_manifest(manifest: dict[str, Any], expected: dict[str, str]) -> None:
    """Verify identity fields before copying a cloud run into the canonical repository."""
    run_manifest = manifest.get("run_manifest", manifest)
    checks = {
        "run_id": run_manifest.get("run_id"),
        "git_commit": run_manifest.get("git_commit"),
        "model_revision": run_manifest.get("model_revision") or run_manifest.get("model", {}).get("revision"),
    }
    for key, expected_value in expected.items():
        if checks.get(key) != expected_value:
            raise ValueError(f"import identity mismatch for {key.replace('_', ' ')}")
    if not run_manifest.get("run_id"):
        raise ValueError("cloud run_id is required")
