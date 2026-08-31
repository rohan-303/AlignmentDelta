"""Model-agnostic production orchestration for the exploratory pilot.

This layer owns run identity, protocol locks, condition/progress registries,
resume, validation, and exports. A cloud adapter supplies model operations;
the fake adapter is test-only and never claims scientific execution.
"""

from __future__ import annotations

import hashlib
import json
import os
import subprocess
import tarfile
import tempfile
import time
import uuid
from collections.abc import Callable
from pathlib import Path
from typing import Any, Protocol, cast

MODEL_ID = "Qwen/Qwen2.5-3B-Instruct"
MODEL_REVISION = "aa8e72537993ba99e69dfaafa59ed015b17504d1"
DIRECTION_SHA256 = "5a8983bcbe4402096210485f8f9b0191eb35b3de84f46624e2dd9811fd09a3fe"
CONTROL_SEEDS = (20260830, 20260831, 20260832, 20260833)
CONTROL_SHA256 = {
    20260830: "38d450a630cdef7e0c7345987bcc984b5c28297402578bd9186100b5b33209f0",
    20260831: "009fa16cf1e3c536431bf04ff1b236ac684d640cd6a38069ded5327e93149720",
    20260832: "f7f113762e73c16fbd84b9f9d784f1dae42412b92dac49c51db97a77838a992f",
    20260833: "517b821e3aa16de00f89f61b9a7f5892d3fb530fbd7d199f80106d1cfb69a8dc",
}
ALPHAS = (-0.5, 0.0, 0.25, 0.5, 0.75, 1.0, 1.25)
NONZERO_ALPHAS = tuple(alpha for alpha in ALPHAS if alpha != 0.0)
EXPECTED_LOGICAL_CONDITIONS = 1860
EXPECTED_RECORDS = 1488
PROTOCOL_FILES = (
    "configs/experiments/exploratory_qwen3b.toml",
    "configs/manifests/xstest_exploratory_pilot.toml",
    "configs/manifests/mmlu_exploratory_pilot.toml",
    "configs/manifests/consistency_pairs.toml",
    "configs/manifests/mmlu.toml",
)


class ScientificAdapter(Protocol):
    def score_options(self, item: dict[str, Any], condition: dict[str, Any]) -> list[float]: ...
    def score_consistency(self, pair: dict[str, Any], condition: dict[str, Any]) -> tuple[list[float], list[float]]: ...


def sha256_file(path: Path) -> str:
    digest = hashlib.sha256()
    with path.open("rb") as handle:
        for block in iter(lambda: handle.read(1024 * 1024), b""):
            digest.update(block)
    return digest.hexdigest()


def atomic_json(path: Path, value: Any) -> None:
    path.parent.mkdir(parents=True, exist_ok=True)
    fd, temporary = tempfile.mkstemp(prefix=f".{path.name}.", dir=path.parent)
    try:
        with os.fdopen(fd, "w", encoding="utf-8", newline="\n") as handle:
            json.dump(value, handle, indent=2, sort_keys=True)
            handle.write("\n")
            handle.flush()
            os.fsync(handle.fileno())
        os.replace(temporary, path)
    finally:
        if os.path.exists(temporary):
            os.unlink(temporary)


def git_state(root: Path) -> tuple[str, bool]:
    commit = subprocess.check_output(("git", "rev-parse", "HEAD"), cwd=root, text=True).strip()
    dirty = bool(subprocess.check_output(("git", "status", "--porcelain"), cwd=root, text=True).strip())
    return commit, dirty


def protocol_hashes(root: Path) -> dict[str, str]:
    result: dict[str, str] = {}
    for relative in PROTOCOL_FILES:
        path = root / relative
        if not path.exists():
            raise RuntimeError(f"PROTOCOL_MANIFEST_MISMATCH: missing {relative}")
        result[relative] = sha256_file(path)
    return result


def cache_direction(
    root: Path,
    direction: Any,
    *,
    model_id: str,
    model_revision: str,
    source_revision: str,
    source_manifest_hash: str,
    code_commit: str,
    expected_sha256: str,
) -> None:
    import torch

    if not isinstance(direction, torch.Tensor) or direction.ndim != 1 or direction.numel() != 2048:
        raise RuntimeError("DIRECTION_CACHE_INVALID")
    vector = direction.detach().cpu().contiguous()
    if not bool(torch.isfinite(vector).all()) or not torch.isclose(
        torch.linalg.vector_norm(vector), torch.tensor(1.0), atol=1e-6
    ):
        raise RuntimeError("DIRECTION_CACHE_INVALID")
    digest = hashlib.sha256(vector.numpy().tobytes()).hexdigest()
    if digest != expected_sha256:
        raise RuntimeError("DIRECTION_CACHE_INVALID")
    root.mkdir(parents=True, exist_ok=True)
    tensor_path = root / "refusal_direction.pt"
    fd, temporary = tempfile.mkstemp(prefix=".refusal_direction.", dir=root)
    os.close(fd)
    try:
        torch.save(vector, temporary)
        os.replace(temporary, tensor_path)
    finally:
        if os.path.exists(temporary):
            os.unlink(temporary)
    atomic_json(
        root / "refusal_direction_metadata.json",
        {
            "sha256": digest,
            "model_id": model_id,
            "model_revision": model_revision,
            "source_revision": source_revision,
            "source_manifest_hash": source_manifest_hash,
            "code_commit": code_commit,
            "layer": 27,
            "hidden_dimension": 2048,
            "norm": float(torch.linalg.vector_norm(vector).item()),
        },
    )


def load_cached_direction(root: Path, *, expected: dict[str, Any]) -> Any:
    import torch

    try:
        metadata = json.loads((root / "refusal_direction_metadata.json").read_text(encoding="utf-8"))
        direction = torch.load(root / "refusal_direction.pt", map_location="cpu", weights_only=True)
        if metadata != {**metadata, **{key: metadata.get(key) for key in expected}}:
            raise RuntimeError("DIRECTION_CACHE_INVALID")
        if any(metadata.get(key) != value for key, value in expected.items()):
            raise RuntimeError("DIRECTION_CACHE_INVALID")
        if not isinstance(direction, torch.Tensor) or direction.ndim != 1 or direction.numel() != 2048:
            raise RuntimeError("DIRECTION_CACHE_INVALID")
        if not bool(torch.isfinite(direction).all()) or not torch.isclose(
            torch.linalg.vector_norm(direction), torch.tensor(1.0), atol=1e-6
        ):
            raise RuntimeError("DIRECTION_CACHE_INVALID")
        if hashlib.sha256(direction.numpy().tobytes()).hexdigest() != expected["sha256"]:
            raise RuntimeError("DIRECTION_CACHE_INVALID")
        return direction
    except Exception as exc:
        if isinstance(exc, RuntimeError) and str(exc) == "DIRECTION_CACHE_INVALID":
            raise
        raise RuntimeError("DIRECTION_CACHE_INVALID") from exc


def _condition_key(master_id: str, task: str, item_id: str, intervention: str, seed: int | None, alpha: float) -> str:
    payload = json.dumps([master_id, task, item_id, intervention, seed, alpha], separators=(",", ":"))
    return hashlib.sha256(payload.encode()).hexdigest()


def build_registry(master_id: str) -> list[dict[str, Any]]:
    registry: list[dict[str, Any]] = []
    definitions = [
        ("xstest", [f"xstest:{i:02d}" for i in range(24)]),
        ("mmlu", [f"mmlu:{i:02d}" for i in range(12)]),
        ("consistency", [f"pair:{i:02d}" for i in range(12)]),
    ]
    for task, item_ids in definitions:
        for item_id in item_ids:
            states: list[tuple[str, int | None, float]] = []
            states.append(("baseline", None, 0.0))
            states.extend(("refusal", None, alpha) for alpha in NONZERO_ALPHAS)
            states += [("control", seed, alpha) for alpha in NONZERO_ALPHAS for seed in CONTROL_SEEDS]
            for intervention, seed, alpha in states:
                key = _condition_key(master_id, task, item_id, intervention, seed, alpha)
                registry.append(
                    {
                        "condition_key": key,
                        "master_run_id": master_id,
                        "task": task,
                        "item_id": item_id,
                        "condition_id": f"{task}:{item_id}:{intervention}:{seed}:{alpha}",
                        "intervention": intervention,
                        "control_seed": seed,
                        "alpha": alpha,
                        "status": "planned",
                    }
                )
    return sorted(registry, key=lambda row: row["condition_key"])


def initialize_master_run(output_root: Path, *, repo_root: Path, master_run_id: str | None = None) -> dict[str, Any]:
    output_root.mkdir(parents=True, exist_ok=True)
    commit, dirty = git_state(repo_root)
    locks = protocol_hashes(repo_root)
    master_id = master_run_id or f"step4.0-{uuid.uuid4().hex[:16]}"
    registry = build_registry(master_id)
    manifest = {
        "schema_version": "step4.0c.v1",
        "master_run_id": master_id,
        "phase": "exploratory_pilot",
        "scientific_execution": True,
        "status": "planned",
        "model_id": MODEL_ID,
        "model_revision": MODEL_REVISION,
        "scientific_code_commit": commit,
        "git_tree_dirty_at_initialization": dirty,
        "protocol_hashes": locks,
        "direction_expected_sha256": DIRECTION_SHA256,
        "control_seeds": list(CONTROL_SEEDS),
        "alpha_grid": list(ALPHAS),
        "task_plan": {"xstest_items": 24, "mmlu_items": 12, "consistency_pairs": 12},
        "logical_condition_count": EXPECTED_LOGICAL_CONDITIONS,
        "record_count": EXPECTED_RECORDS,
        "operation_counts": {
            "xstest_generations": 744,
            "mmlu_option_sequences": 1488,
            "consistency_original_option_sequences": 1488,
            "consistency_transformed_option_sequences": 1488,
            "physical_forward_estimate": 5208,
        },
        "created_unix": time.time(),
        "output_root": str(output_root),
    }
    atomic_json(output_root / "master_manifest.json", manifest)
    atomic_json(output_root / "condition_registry.json", registry)
    atomic_json(
        output_root / "progress.json",
        {
            "master_run_id": master_id,
            "status": "planned",
            "planned": [row["condition_key"] for row in registry],
            "complete": [],
            "failed": [],
        },
    )
    atomic_json(output_root / "failures.json", [])
    return manifest


def validate_master_manifest(output_root: Path, *, repo_root: Path, require_clean: bool = False) -> dict[str, Any]:
    manifest = json.loads((output_root / "master_manifest.json").read_text(encoding="utf-8"))
    commit, dirty = git_state(repo_root)
    if manifest["scientific_code_commit"] != commit:
        raise RuntimeError("SCIENTIFIC_CODE_COMMIT_MISMATCH")
    if require_clean and dirty:
        raise RuntimeError("CLOUD_EXECUTION_REQUIRES_CLEAN_GIT_TREE")
    if manifest["protocol_hashes"] != protocol_hashes(repo_root):
        raise RuntimeError("PROTOCOL_MANIFEST_MISMATCH")
    if manifest["logical_condition_count"] != EXPECTED_LOGICAL_CONDITIONS:
        raise RuntimeError("PROTOCOL_MANIFEST_MISMATCH")
    return cast(dict[str, Any], manifest)


def bind_intervention_identity(row: dict[str, Any], technical_state: dict[str, Any]) -> dict[str, Any]:
    """Attach the verified intervention identity to one immutable condition."""
    bound = dict(row)
    intervention = row["intervention"]
    if intervention == "baseline":
        bound.update({"direction_sha256": None, "layer": None, "hidden_dimension": None, "control_sha256": None})
    elif intervention == "refusal":
        bound.update({"direction": technical_state.get("direction"), "direction_sha256": DIRECTION_SHA256, "layer": 27, "hidden_dimension": 2048, "control_sha256": None})  # noqa: E501
    elif intervention == "control":
        seed = row.get("control_seed")
        if seed not in CONTROL_SHA256:
            raise RuntimeError("CONTROL_IDENTITY_MISMATCH")
        controls = technical_state.get("controls", {})
        if technical_state and seed not in controls:
            raise RuntimeError("CONTROL_IDENTITY_MISMATCH")
        bound.update({"direction": controls.get(seed), "direction_sha256": DIRECTION_SHA256, "layer": 27, "hidden_dimension": 2048, "control_sha256": CONTROL_SHA256[seed]})  # noqa: E501
    else:
        raise RuntimeError("INTERVENTION_IDENTITY_MISMATCH")
    expected = technical_state
    if expected.get("direction_sha256") not in (None, DIRECTION_SHA256):
        raise RuntimeError("DIRECTION_IDENTITY_MISMATCH")
    if expected.get("layer", 27) != 27 or expected.get("hidden_dimension", 2048) != 2048:
        raise RuntimeError("INTERVENTION_IDENTITY_MISMATCH")
    return bound


def validate_technical_gate(output_root: Path, manifest: dict[str, Any]) -> dict[str, Any]:
    path = output_root / "manifests" / "technical_pre_science_gate.json"
    if not path.exists():
        raise RuntimeError("PRE_SCIENCE_GATE_REQUIRED")
    gate = cast(dict[str, Any], json.loads(path.read_text(encoding="utf-8")))
    expected = {
        "model_id": manifest["model_id"],
        "model_revision": manifest["model_revision"],
        "scientific_code_commit": manifest["scientific_code_commit"],
        "protocol_hashes": manifest["protocol_hashes"],
        "direction_sha256": manifest["direction_expected_sha256"],
        "layer": 27,
        "hidden_dimension": 2048,
        "status": "PRE_SCIENCE_TECHNICAL_GATE_PASS",
    }
    for key, value in expected.items():
        if gate.get(key) != value:
            raise RuntimeError("PRE_SCIENCE_GATE_REQUIRED")
    if gate.get("controls") != {str(k): {"sha256": v} for k, v in CONTROL_SHA256.items()} and gate.get("control_sha256") != CONTROL_SHA256:  # noqa: E501
        controls = gate.get("controls", {})
        if {int(k): value.get("sha256") for k, value in controls.items() if isinstance(value, dict)} != CONTROL_SHA256:
            raise RuntimeError("PRE_SCIENCE_GATE_REQUIRED")
    return gate


def _probabilities(scores: list[float]) -> list[float]:
    import math

    if len(scores) != 4 or not all(math.isfinite(value) for value in scores):
        raise ValueError("CONDITION_FAILED: invalid option scores")
    pivot = max(scores)
    weights = [math.exp(value - pivot) for value in scores]
    total = sum(weights)
    return [weight / total for weight in weights]


def _sanitized_record(
    adapter: ScientificAdapter, row: dict[str, Any], item: dict[str, Any], raw_root: Path
) -> dict[str, Any]:
    task = row["task"]
    if task == "xstest":
        generate_item = getattr(adapter, "generate_item", None)
        generated = generate_item(item, row) if generate_item is not None else cast(Any, adapter).generate(item, row)
        response = str(generated["text"])
        response_id = f"response-{hashlib.sha256((row['condition_key'] + response).encode()).hexdigest()[:24]}"
        raw_path = raw_root / f"{response_id}.json"
        atomic_json(raw_path, {"response_id": response_id, "item_id": row["item_id"], "response_text": response})
        return {
            **row,
            "status": "complete",
            "response_id": response_id,
            "response_hash": hashlib.sha256(response.encode()).hexdigest(),
            "input_token_count": int(generated["input_token_count"]),
            "output_token_count": int(generated["output_token_count"]),
            "finish_reason": generated.get("finish_reason", "unknown"),
            "model_revision": MODEL_REVISION,
            "generation_settings_hash": generated.get("generation_settings_hash", "frozen"),
            "raw_artifact": str(raw_path.relative_to(raw_root.parent.parent)),
        }
    if task == "mmlu":
        scores = adapter.score_options(item, row)
        probabilities = _probabilities(scores)
        gold = int(item.get("gold_answer", 0))
        return {
            **row,
            "status": "complete",
            "option_log_scores": scores,
            "option_probabilities": probabilities,
            "predicted_answer": probabilities.index(max(probabilities)),
            "gold_answer": gold,
            "correctness": probabilities.index(max(probabilities)) == gold,
            "brier": sum((p - (i == gold)) ** 2 for i, p in enumerate(probabilities)),
            "nll": -__import__("math").log(probabilities[gold]),
            "model_revision": MODEL_REVISION,
        }
    original, transformed = adapter.score_consistency(item, row)
    original_prob = _probabilities(original)
    transformed_prob = _probabilities(transformed)
    permutation = item.get("permutation", [0, 1, 2, 3])
    canonical = [0.0] * 4
    for transformed_index, original_index in enumerate(permutation):
        canonical[original_index] = transformed_prob[transformed_index]
    return {
        **row,
        "status": "complete",
        "original_option_log_scores": original,
        "transformed_option_log_scores": transformed,
        "original_probabilities": original_prob,
        "transformed_canonical_probabilities": canonical,
        "original_prediction": original_prob.index(max(original_prob)),
        "transformed_canonical_prediction": canonical.index(max(canonical)),
        "prediction_agreement": original_prob.index(max(original_prob)) == canonical.index(max(canonical)),
        "jensen_shannon_divergence": _js(original_prob, canonical),
        "model_revision": MODEL_REVISION,
    }


def validate_sanitized_record(task: str, record: dict[str, Any]) -> None:
    """Validate finite, leakage-safe output before it becomes complete."""
    import math

    if record.get("status") != "complete" or not record.get("condition_key"):
        raise RuntimeError("CONDITION_FAILED: record lifecycle invalid")
    if task == "xstest":
        if "response_text" in record or "question" in record or not record.get("response_hash"):
            raise RuntimeError("CONDITION_FAILED: raw XSTest content leaked")
        return
    if task == "mmlu":
        scores = record.get("option_log_scores")
        probabilities = record.get("option_probabilities")
    else:
        scores = record.get("original_option_log_scores")
        probabilities = record.get("original_probabilities")
        transformed = record.get("transformed_canonical_probabilities")
        if not isinstance(transformed, list) or len(transformed) != 4:
            raise RuntimeError("CONDITION_FAILED: consistency probabilities invalid")
        if not all(isinstance(value, (int, float)) and math.isfinite(value) for value in transformed):
            raise RuntimeError("CONDITION_FAILED: consistency probabilities non-finite")
    if not isinstance(scores, list) or len(scores) != 4 or not all(math.isfinite(float(value)) for value in scores):
        raise RuntimeError("CONDITION_FAILED: option scores invalid")
    if not isinstance(probabilities, list) or len(probabilities) != 4 or not all(math.isfinite(float(value)) for value in probabilities):  # noqa: E501
        raise RuntimeError("CONDITION_FAILED: probabilities invalid")
    if not math.isclose(sum(probabilities), 1.0, rel_tol=0.0, abs_tol=1e-9):
        raise RuntimeError("CONDITION_FAILED: probabilities do not normalize")


def _record_digest(record: dict[str, Any]) -> str:
    payload = {key: value for key, value in record.items() if key != "record_sha256"}
    return hashlib.sha256(json.dumps(payload, sort_keys=True, separators=(",", ":")).encode()).hexdigest()


def _js(left: list[float], right: list[float]) -> float:
    import math

    midpoint = [(a + b) / 2 for a, b in zip(left, right, strict=True)]
    return 0.5 * sum(a * math.log(a / m) for a, m in zip(left, midpoint, strict=True) if a > 0) + 0.5 * sum(
        b * math.log(b / m) for b, m in zip(right, midpoint, strict=True) if b > 0
    )


def _mark_condition_failed(
    output_root: Path,
    manifest: dict[str, Any],
    row: dict[str, Any],
    attempt: int,
    error: Exception,
) -> None:
    failure = {
        "master_run_id": manifest["master_run_id"],
        "chunk_id": row.get("chunk_id"),
        "task": row["task"],
        "condition_key": row["condition_key"],
        "attempt": attempt,
        "failure_class": "CONDITION_FAILED",
        "safe_error_type": type(error).__name__,
        "safe_error_summary": str(error)[:240],
        "timestamp": time.time(),
        "recoverable": False,
    }
    failures_path = output_root / "failures.json"
    failures = json.loads(failures_path.read_text(encoding="utf-8")) if failures_path.exists() else []
    failures.append(failure)
    atomic_json(failures_path, failures)
    progress_path = output_root / "progress.json"
    progress = json.loads(progress_path.read_text(encoding="utf-8")) if progress_path.exists() else {}
    conditions = [item for item in progress.get("conditions", []) if item.get("condition_key") != row["condition_key"]]
    conditions.append(
        {
            "condition_key": row["condition_key"],
            "task": row["task"],
            "item_or_pair_id": row["item_id"],
            "lifecycle_state": "failed",
            "attempt_count": attempt,
            "output_path": None,
            "output_sha256": None,
            "chunk_id": row.get("chunk_id"),
            "started_at": None,
            "completed_at": None,
            "safe_failure_code": "CONDITION_FAILED",
        }
    )
    progress.update(
        {
            "master_run_id": manifest["master_run_id"],
            "status": "failed",
            "failed": [row["condition_key"]],
            "conditions": conditions,
        }
    )
    atomic_json(progress_path, progress)
    manifest["status"] = "failed"
    atomic_json(output_root / "master_manifest.json", manifest)


def _write_records(root: Path, records: dict[str, dict[str, Any]]) -> None:
    path = root / "sanitized" / "records.jsonl"
    path.parent.mkdir(parents=True, exist_ok=True)
    fd, temporary = tempfile.mkstemp(prefix=".records.", dir=path.parent)
    try:
        with os.fdopen(fd, "w", encoding="utf-8", newline="\n") as handle:
            for key in sorted(records):
                handle.write(json.dumps(records[key], sort_keys=True) + "\n")
            handle.flush()
            os.fsync(handle.fileno())
        os.replace(temporary, path)
    finally:
        if os.path.exists(temporary):
            os.unlink(temporary)


def run_production(
    output_root: Path,
    *,
    repo_root: Path,
    adapter: ScientificAdapter,
    item_provider: Callable[[dict[str, Any]], dict[str, Any]] | None = None,
    resume: bool = False,
    stop_after: int | None = None,
    technical_state: dict[str, Any] | None = None,
    task: str | None = None,
    chunk_index: int = 0,
    chunk_count: int = 1,
) -> dict[str, Any]:
    manifest_path = output_root / "master_manifest.json"
    if not manifest_path.exists():
        initialize_master_run(output_root, repo_root=repo_root)
    manifest = validate_master_manifest(output_root, repo_root=repo_root)
    if not isinstance(adapter, FakeScientificAdapter):
        validate_technical_gate(output_root, manifest)
    technical_state = technical_state or {}
    registry = json.loads((output_root / "condition_registry.json").read_text(encoding="utf-8"))
    if chunk_count < 1 or not 0 <= chunk_index < chunk_count:
        raise RuntimeError("CHUNK_IDENTITY_MISMATCH")
    all_registry = registry
    if task is not None:
        registry = [row for row in registry if row["task"] == task]
    chunk_id = f"{manifest['master_run_id']}:{task or 'all'}:{chunk_index}:{chunk_count}"
    registry = [row for row in registry if int(row["condition_key"][:8], 16) % chunk_count == chunk_index]
    records_path = output_root / "sanitized" / "records.jsonl"
    records: dict[str, dict[str, Any]] = {}
    invalidated: list[dict[str, Any]] = []
    if resume and records_path.exists():
        for line in records_path.read_text(encoding="utf-8").splitlines():
            row = json.loads(line)
            if row["condition_key"] in records or row.get("status") != "complete":
                raise RuntimeError("invalid or duplicate condition record")
            if row.get("master_run_id") != manifest["master_run_id"]:
                raise RuntimeError("RUN_IDENTITY_MISMATCH")
            if row.get("record_sha256") != _record_digest(row):
                invalidated.append(
                    {
                        "master_run_id": manifest["master_run_id"],
                        "condition_key": row["condition_key"],
                        "failure_class": "RUN_INVALIDATED",
                        "safe_error_type": "CORRUPT_ARTIFACT",
                        "safe_error_summary": "record digest mismatch; recomputing",
                        "recoverable": True,
                    }
                )
                continue
            validate_sanitized_record(str(row["task"]), row)
            records[row["condition_key"]] = row
    raw_root = output_root / "protected" / "raw" / "xstest"
    processed = 0
    for row in registry:
        row = {**row, "chunk_id": chunk_id}
        if row["condition_key"] in records:
            continue
        if stop_after is not None and processed >= stop_after:
            break
        row = bind_intervention_identity(row, technical_state)
        if item_provider is None and not isinstance(adapter, FakeScientificAdapter):
            raise RuntimeError("REAL_DATA_PROVIDER_REQUIRED")
        item = (
            item_provider(row)
            if item_provider is not None
            else {
                "id": row["item_id"],
                "prompt": "mock",
                "question": "mock",
                "options": ["A", "B", "C", "D"],
                "gold_answer": 0,
                "permutation": [2, 0, 3, 1],
            }
        )
        last_error: Exception | None = None
        for attempt in range(1, 3):
            try:
                completed = _sanitized_record(adapter, row, item, raw_root)
                validate_sanitized_record(str(row["task"]), completed)
                completed["lifecycle_state"] = "completed"
                completed["attempt_count"] = attempt
                completed["started_at"] = completed.get("started_at", time.time())
                completed["completed_at"] = time.time()
                completed["output_path"] = "sanitized/records.jsonl"
                completed["source_item_id"] = item.get("id", item.get("pair_id"))
                completed["source_revision"] = item.get("source_revision")
                completed["source_content_hash"] = item.get("content_hash", item.get("text_hash"))
                completed["record_sha256"] = _record_digest(completed)
                records[row["condition_key"]] = completed
                break
            except (RuntimeError, ValueError, KeyError, TypeError) as exc:
                last_error = exc
                if attempt == 2:
                    _mark_condition_failed(output_root, manifest, row, attempt, exc)
                    raise RuntimeError("CONDITION_FAILED") from exc
        if row["condition_key"] not in records and last_error is not None:
            raise RuntimeError("CONDITION_FAILED") from last_error
        processed += 1
        _write_records(output_root, records)
    atomic_json(output_root / "failures.json", invalidated)
    status = "completed" if len(records) == len(all_registry) else "running"
    manifest["status"] = status
    atomic_json(output_root / "master_manifest.json", manifest)
    atomic_json(
        output_root / "progress.json",
        {
            "master_run_id": manifest["master_run_id"],
            "status": status,
            "planned_count": len(registry),
            "complete": sorted(records),
            "failed": [],
            "conditions": [
                {
                    "condition_key": row["condition_key"],
                    "task": row["task"],
                    "item_or_pair_id": row["item_id"],
                    "lifecycle_state": "completed" if row["condition_key"] in records else "planned",
                    "attempt_count": records.get(row["condition_key"], {}).get("attempt_count", 0),
                    "output_path": records.get(row["condition_key"], {}).get("output_path"),
                    "output_sha256": (
                        sha256_file(records_path)
                        if row["condition_key"] in records and records_path.exists()
                        else None
                    ),
                    "chunk_id": row.get("chunk_id", "chunk-00000-of-00001"),
                    "started_at": records.get(row["condition_key"], {}).get("started_at"),
                    "completed_at": records.get(row["condition_key"], {}).get("completed_at"),
                    "safe_failure_code": None,
                }
                for row in registry
            ],
        },
    )
    if status == "completed":
        export_sanitized(output_root, output_root / "step_4_0_sanitized_export.tar.gz")
        export_sensitive_annotation(output_root, output_root / "step_4_0_sensitive_annotation_export.tar.gz")
    counts = {
        "xstest_records": sum(row["task"] == "xstest" for row in records.values()),
        "mmlu_records": sum(row["task"] == "mmlu" for row in records.values()),
        "consistency_records": sum(row["task"] == "consistency" for row in records.values()),
    }
    return {
        "status": status,
        "logical_condition_count": EXPECTED_LOGICAL_CONDITIONS,
        "record_count": len(records),
        **counts,
    }


class FakeScientificAdapter:
    def generate(self, item: dict[str, Any], condition: dict[str, Any]) -> dict[str, Any]:
        key = condition["condition_key"]
        return {
            "text": f"fake-response-{key}",
            "input_token_count": 3,
            "output_token_count": 2,
            "finish_reason": "fake",
        }

    def score_options(self, item: dict[str, Any], condition: dict[str, Any]) -> list[float]:
        return [0.0, -1.0, -2.0, -3.0]

    def score_consistency(self, pair: dict[str, Any], condition: dict[str, Any]) -> tuple[list[float], list[float]]:
        return [0.0, -1.0, -2.0, -3.0], [-1.0, -3.0, 0.0, -2.0]


def run_mocked_production(
    output_root: Path,
    *,
    repo_root: Path,
    adapter: ScientificAdapter,
    resume: bool = False,
    stop_after: int | None = None,
) -> dict[str, Any]:
    return run_production(output_root, repo_root=repo_root, adapter=adapter, resume=resume, stop_after=stop_after)


def _archive(root: Path, archive: Path, folders: tuple[str, ...]) -> None:
    manifest: list[dict[str, Any]] = []
    for folder in folders:
        path = root / folder
        if path.exists():
            for file_path in sorted(path.rglob("*")):
                if file_path.is_file() and file_path.name != "archive_manifest.json":
                    manifest.append(
                        {
                            "path": str(file_path.relative_to(root)).replace("\\", "/"),
                            "bytes": file_path.stat().st_size,
                            "sha256": sha256_file(file_path),
                        }
                    )
    atomic_json(root / "manifests" / "archive_manifest.json", manifest)
    with tarfile.open(archive, "w:gz") as tar:
        for folder in folders:
            path = root / folder
            if path.exists():
                tar.add(path, arcname=folder, filter=lambda info: info if info.name.rsplit("/", 1)[-1] != "archive_manifest.json" else None)  # noqa: E501
    verify_archive(archive, manifest)


def verify_archive(archive: Path, manifest: list[dict[str, Any]]) -> None:
    expected = {entry["path"]: entry for entry in manifest}
    with tarfile.open(archive, "r:gz") as tar:
        members = {member.name: member for member in tar.getmembers() if member.isfile()}
        if set(members) != set(expected):
            raise RuntimeError("EXPORT_VERIFICATION_FAILED")
        for name, entry in expected.items():
            extracted = tar.extractfile(members[name])
            if extracted is None:
                raise RuntimeError("EXPORT_VERIFICATION_FAILED")
            data = extracted.read()
            if len(data) != entry["bytes"] or hashlib.sha256(data).hexdigest() != entry["sha256"]:
                raise RuntimeError("EXPORT_VERIFICATION_FAILED")


def export_sanitized(root: Path, archive: Path) -> None:
    _archive(root, archive, ("sanitized", "manifests", "logs"))
    scan_sanitized_export(archive)


def scan_sanitized_export(archive: Path) -> None:
    forbidden_names = ("unblinding", "weights", ".env", "raw", "benchmark_cache", "hf_cache")
    forbidden_content = ("api_key", "access_token", "password", "response_text")
    with tarfile.open(archive, "r:gz") as tar:
        for member in tar.getmembers():
            lowered = member.name.lower()
            if any(token in lowered for token in forbidden_names):
                raise RuntimeError("SANITIZED_EXPORT_LEAKAGE")
            if member.isfile():
                handle = tar.extractfile(member)
                content = handle.read().decode("utf-8", errors="ignore").lower() if handle else ""
                if any(token in content for token in forbidden_content):
                    raise RuntimeError("SANITIZED_EXPORT_LEAKAGE")


def export_sensitive_annotation(root: Path, archive: Path) -> None:
    target = root / "annotation"
    target.mkdir(parents=True, exist_ok=True)
    records = []
    unblinding: list[dict[str, Any]] = []
    scientific_by_response: dict[str, dict[str, Any]] = {}
    records_path = root / "sanitized" / "records.jsonl"
    if records_path.exists():
        for line in records_path.read_text(encoding="utf-8").splitlines():
            record = json.loads(line)
            if record.get("response_id"):
                scientific_by_response[record["response_id"]] = record
    for path in sorted((root / "protected" / "raw" / "xstest").glob("*.json")):
        raw = json.loads(path.read_text(encoding="utf-8"))
        annotation_id = "ann-" + raw["response_id"].split("-", 1)[-1]
        records.append(
            {
                "annotation_id": annotation_id,
                "response_text": raw["response_text"],
                "annotation_label": None,
                "annotation_status": "pending",
                "annotator_notes": None,
            }
        )
        scientific = scientific_by_response.get(raw["response_id"], {})
        unblinding.append(
            {
                "annotation_id": annotation_id,
                "response_id": raw["response_id"],
                "protected_raw_path": str(path.relative_to(root)),
                "condition_key": scientific.get("condition_key"),
                "condition_id": scientific.get("condition_id"),
                "intervention": scientific.get("intervention"),
                "alpha": scientific.get("alpha"),
                "control_seed": scientific.get("control_seed"),
            }
        )
    payload = "\n".join(json.dumps(row, sort_keys=True) for row in records) + ("\n" if records else "")
    forbidden = ("condition_id", "intervention", "control_seed", "alpha", "direction", "unblinding")
    if any(field in payload.lower() for field in forbidden):
        raise RuntimeError("ANNOTATION_BLINDING_VIOLATION")
    (target / "annotation_records.jsonl").write_text(payload, encoding="utf-8")
    atomic_json(root / "protected" / "unblinding_map.json", unblinding)
    _archive(root, archive, ("annotation",))
