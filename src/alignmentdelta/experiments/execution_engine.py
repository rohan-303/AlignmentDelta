"""Step 4.0A execution safety core and synthetic end-to-end runner.

This module deliberately imports no torch, transformers, datasets, or model weights.
Real execution is a separate explicitly gated path and is never entered without
``--execute --profile cloud_gpu``.
"""

from __future__ import annotations

import argparse
import hashlib
import json
import math
import os
import secrets
import tarfile
import tempfile
from collections.abc import Iterable
from dataclasses import dataclass
from pathlib import Path
from typing import Any

ALPHAS = (-0.5, 0.0, 0.25, 0.5, 0.75, 1.0, 1.25)
CONTROL_SEEDS = (20260830, 20260831, 20260832, 20260833)
MODEL_ID = "Qwen/Qwen2.5-3B-Instruct"
MODEL_REVISION = "aa8e72537993ba99e69dfaafa59ed015b17504d1"
LAYER = 27
EXPECTED_DIRECTION_SHA256 = "286147ed00c828028d6856e5cab4e87ed5730e1e2f6f6fff047f2d3bb71a84b1"


@dataclass(frozen=True, slots=True)
class Condition:
    item_id: str
    intervention: str
    alpha: float
    seed: int | None
    condition_id: str
    baseline_id: str


@dataclass(frozen=True, slots=True)
class ExecutionConfig:
    root: Path
    master_run_id: str
    task: str = "all"
    chunk_index: int = 0
    chunk_count: int = 1
    synthetic_mode: bool = False

    @classmethod
    def make_synthetic(cls, root: Path) -> ExecutionConfig:
        return cls(root=root, master_run_id="synthetic-step4a", synthetic_mode=True)


def validate_sha256_identity(value: str) -> None:
    if (
        not isinstance(value, str)
        or len(value) != 64
        or any(character not in "0123456789abcdefABCDEF" for character in value)
    ):
        raise ValueError("SHA-256 identity must be exactly 64 hexadecimal characters")


def build_conditions(item_ids: Iterable[str]) -> list[Condition]:
    result: list[Condition] = []
    for item_id in sorted(set(item_ids)):
        baseline_id = f"baseline:{item_id}"
        result.append(Condition(item_id, "baseline", 0.0, None, baseline_id, baseline_id))
        for alpha in ALPHAS:
            if alpha == 0.0:
                continue
            result.append(Condition(item_id, "refusal", alpha, None, f"refusal:{item_id}:{alpha}", baseline_id))
            for seed in CONTROL_SEEDS:
                result.append(
                    Condition(item_id, "control", alpha, seed, f"control:{item_id}:{seed}:{alpha}", baseline_id)
                )
    assert len([c for c in result if c.item_id == next(iter(sorted(set(item_ids))))]) == 31
    assert len({c.baseline_id for c in result}) == len(set(item_ids))
    return result


def operation_accounting(xstest_items: int, mmlu_items: int, consistency_pairs: int) -> dict[str, int]:
    states = 31
    representations = xstest_items + mmlu_items + 2 * consistency_pairs
    return {
        "representations": representations,
        "logical_condition_states": representations * states,
        "unique_baseline_states": representations,
        "xstest_generations": xstest_items * states,
        "mmlu_option_score_sequences": mmlu_items * states * 4,
        "consistency_original_option_score_sequences": consistency_pairs * states * 4,
        "consistency_transformed_option_score_sequences": consistency_pairs * states * 4,
        "actual_forward_calls": xstest_items * states + mmlu_items * states * 4 + consistency_pairs * states * 8,
    }


def direction_hash_gate(actual_sha256: str) -> None:
    validate_sha256_identity(actual_sha256)
    if actual_sha256 != EXPECTED_DIRECTION_SHA256:
        raise RuntimeError("DIRECTION_RECONSTRUCTION_MISMATCH")


def validate_controls(direction: list[float], controls: dict[int, list[float]]) -> None:
    if len(direction) != 2048 or not all(math.isfinite(x) for x in direction):
        raise RuntimeError("invalid refusal direction")
    direction_norm = math.sqrt(sum(x * x for x in direction))
    if not math.isclose(direction_norm, 1.0, abs_tol=1e-6):
        raise RuntimeError("invalid refusal direction norm")
    for seed in CONTROL_SEEDS:
        control = controls.get(seed)
        if control is None or len(control) != 2048 or not all(math.isfinite(x) for x in control):
            raise RuntimeError(f"invalid control: {seed}")
        norm = math.sqrt(sum(x * x for x in control))
        dot = abs(sum(a * b for a, b in zip(direction, control, strict=True)))
        if not math.isclose(norm, 1.0, abs_tol=1e-6) or dot > 1e-6:
            raise RuntimeError(f"invalid control geometry: {seed}")


def atomic_write_json(path: Path, value: Any) -> None:
    path.parent.mkdir(parents=True, exist_ok=True)
    payload = (json.dumps(value, indent=2, sort_keys=True) + "\n").encode()
    fd, temporary = tempfile.mkstemp(prefix=f".{path.name}.", dir=path.parent)
    try:
        with os.fdopen(fd, "wb") as handle:
            handle.write(payload)
            handle.flush()
            os.fsync(handle.fileno())
        os.replace(temporary, path)
    finally:
        if os.path.exists(temporary):
            os.unlink(temporary)


def validate_manifest_hashes(expected: dict[str, str], files: dict[str, Path]) -> None:
    for name, digest in expected.items():
        path = files.get(name)
        actual = hashlib.sha256(path.read_bytes()).hexdigest() if path and path.exists() else None
        if actual != digest:
            raise RuntimeError("PROTOCOL_MANIFEST_MISMATCH")


def chunk_conditions(conditions: list[Condition], index: int, count: int) -> list[Condition]:
    if count < 1 or not 0 <= index < count:
        raise ValueError("invalid chunk selection")
    ordered = sorted(conditions, key=lambda c: c.condition_id)
    return [condition for position, condition in enumerate(ordered) if position % count == index]


def _key(config: ExecutionConfig, task: str, condition: Condition) -> str:
    raw = f"{config.master_run_id}|{task}|{condition.condition_id}".encode()
    return hashlib.sha256(raw).hexdigest()


def _record(config: ExecutionConfig, task: str, condition: Condition) -> dict[str, Any]:
    key = _key(config, task, condition)
    record: dict[str, Any] = {
        "schema_version": "step4a.synthetic.v1",
        "master_run_id": config.master_run_id,
        "task": task,
        "condition_key": key,
        "item_id": condition.item_id,
        "condition_id": condition.condition_id,
        "status": "COMPLETE",
        "model_weights_loaded": 0,
        "scientific_model_inference": 0,
    }
    if task == "xstest":
        response = f"synthetic-response:{key}"
        record.update(
            {
                "response_id": f"response:{key[:16]}",
                "response_sha256": hashlib.sha256(response.encode()).hexdigest(),
                "token_count": 1,
                "finish_reason": "synthetic",
            }
        )
    elif task == "mmlu":
        scores = [0.0, -1.0, -2.0, -3.0]
        weights = [math.exp(x) for x in scores]
        total = sum(weights)
        probabilities = [x / total for x in weights]
        record.update(
            {
                "option_log_scores": scores,
                "option_probabilities": probabilities,
                "predicted_answer": 0,
                "gold_answer": 0,
                "correctness": True,
                "brier": sum((p - (i == 0)) ** 2 for i, p in enumerate(probabilities)),
                "nll": -math.log(probabilities[0]),
            }
        )
    else:
        record.update(
            {
                "original_probabilities": [0.25] * 4,
                "transformed_canonical_probabilities": [0.25] * 4,
                "original_prediction": 0,
                "transformed_canonical_prediction": 0,
                "prediction_agreement": True,
                "jensen_shannon_divergence": 0.0,
            }
        )
    return record


def _load_records(path: Path) -> dict[str, dict[str, Any]]:
    if not path.exists():
        return {}
    records: dict[str, dict[str, Any]] = {}
    for line in path.read_text(encoding="utf-8").splitlines():
        if not line.strip():
            continue
        item = json.loads(line)
        key = item.get("condition_key")
        if not key or key in records or item.get("status") != "COMPLETE":
            raise RuntimeError("invalid or duplicate condition record")
        records[key] = item
    return records


def run_synthetic(config: ExecutionConfig, resume: bool = False) -> dict[str, Any]:
    if not config.synthetic_mode:
        raise RuntimeError("synthetic runner requires synthetic configuration")
    root = config.root
    sanitized = root / "sanitized"
    sanitized.mkdir(parents=True, exist_ok=True)
    path = sanitized / "records.jsonl"
    records = _load_records(path) if resume else {}
    tasks = [
        ("xstest", [f"xstest:{i}" for i in range(24)]),
        ("mmlu", [f"mmlu:{i}" for i in range(12)]),
        ("consistency", [f"pair:{i}:original" for i in range(12)] + [f"pair:{i}:transformed" for i in range(12)]),
    ]
    pending: list[dict[str, Any]] = []
    for task, ids in tasks:
        for condition in chunk_conditions(build_conditions(ids), config.chunk_index, config.chunk_count):
            key = _key(config, task, condition)
            if key not in records:
                record = _record(config, task, condition)
                records[key] = record
                pending.append(record)
    ordered = [records[key] for key in sorted(records)]
    payload = "".join(json.dumps(record, sort_keys=True) + "\n" for record in ordered)
    path.parent.mkdir(parents=True, exist_ok=True)
    temporary = path.with_suffix(path.suffix + ".tmp")
    temporary.write_text(payload, encoding="utf-8")
    temporary.replace(path)
    atomic_write_json(
        root / "manifests" / "progress.json",
        {
            "master_run_id": config.master_run_id,
            "completed_condition_keys": sorted(records),
            "completed_count": len(records),
            "planned_count": len(records),
        },
    )
    atomic_write_json(
        root / "manifests" / "run_manifest.json",
        {
            "master_run_id": config.master_run_id,
            "chunk_id": f"{config.task}:{config.chunk_index}/{config.chunk_count}",
            "task": config.task,
            "model_revision": MODEL_REVISION,
            "synthetic": True,
            "model_weights_loaded": 0,
            "scientific_model_inference": 0,
            "records_added_this_call": len(pending),
        },
    )
    return {
        "completed_count": len(records),
        "records_added": len(pending),
        "scientific_model_inference": 0,
        "model_weights_loaded": 0,
    }


def export_run(root: Path, archive: Path) -> Path:
    archive.parent.mkdir(parents=True, exist_ok=True)
    with tarfile.open(archive, "w:gz") as tar:
        for folder in ("sanitized", "manifests", "logs", "annotation"):
            path = root / folder
            if path.exists():
                tar.add(path, arcname=folder)
    return archive


def require_real_execution(execute: bool, profile: str | None) -> None:
    if not execute:
        return
    if profile != "cloud_gpu":
        raise RuntimeError("real scientific execution requires --profile cloud_gpu")


def main(argv: list[str] | None = None) -> int:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--dry-run", action="store_true")
    parser.add_argument("--execute", action="store_true")
    parser.add_argument("--synthetic", action="store_true")
    parser.add_argument("--resume", action="store_true")
    parser.add_argument("--profile")
    parser.add_argument("--task", choices=("xstest", "mmlu", "consistency", "all"), default="all")
    parser.add_argument("--output-root", type=Path, default=Path("artifacts/runs/step_4_0"))
    parser.add_argument("--chunk-index", type=int, default=0)
    parser.add_argument("--chunk-count", type=int, default=1)
    args = parser.parse_args(argv)
    require_real_execution(args.execute, args.profile)
    if args.execute and not args.synthetic:
        raise RuntimeError("real Qwen execution is cloud-only and must use the dedicated cloud execution adapter")
    if args.synthetic:
        result = run_synthetic(
            ExecutionConfig(
                args.output_root, secrets.token_hex(8), args.task, args.chunk_index, args.chunk_count, True
            ),
            args.resume,
        )
        print(json.dumps(result, sort_keys=True))
    else:
        print("model_weights_loaded: 0\nscientific_model_inference: 0\ndecision: SAFE_DRY_RUN")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
