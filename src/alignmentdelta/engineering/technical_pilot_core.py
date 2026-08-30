"""Pure technical-pilot policies and diagnostics."""

from __future__ import annotations

import hashlib
import itertools
import json
import math
from collections.abc import Iterable, Sequence
from typing import Any

import torch


class TechnicalPilotError(ValueError):
    """Raised when a frozen technical-pilot contract cannot be satisfied."""


def deterministic_sample(
    harmful: Sequence[dict[str, Any]],
    harmless: Sequence[dict[str, Any]],
    *,
    train_counts: tuple[int, int],
    validation_counts: tuple[int, int],
) -> dict[str, Any]:
    """Select stable-ID prefixes without outcome-dependent sampling."""
    ordered_harmful = sorted(harmful, key=_stable_record_key)
    ordered_harmless = sorted(harmless, key=_stable_record_key)
    th, ts = train_counts
    vh, vs = validation_counts
    if len(ordered_harmful) < th + vh or len(ordered_harmless) < ts + vs:
        raise TechnicalPilotError("insufficient records for frozen sample policy")
    return {
        "direction_train_harmful": list(ordered_harmful[:th]),
        "direction_train_harmless": list(ordered_harmless[:ts]),
        "direction_validation_harmful": list(ordered_harmful[th : th + vh]),
        "direction_validation_harmless": list(ordered_harmless[ts : ts + vs]),
        "rng_seed": None,
        "ordering": "stable_id_lexicographic",
    }


def _stable_record_key(record: dict[str, Any]) -> str:
    if "id" in record:
        return str(record["id"])
    canonical = json.dumps(record, sort_keys=True, separators=(",", ":"), ensure_ascii=False).encode()
    return hashlib.sha256(canonical).hexdigest()


def candidate_layers_full(block_count: int) -> list[int]:
    if block_count < 1:
        raise TechnicalPilotError("block_count must be positive")
    last = int(math.floor(0.80 * block_count) - 1)
    return list(range(last + 1))


def pairwise_cosines(vectors: Iterable[torch.Tensor]) -> dict[str, Any]:
    values = [vector.detach().to(torch.float64).flatten() for vector in vectors]
    if len(values) < 2:
        raise TechnicalPilotError("direction stability requires at least two vectors")
    norms = [float(torch.linalg.vector_norm(vector).item()) for vector in values]
    if any(norm <= 0 or not math.isfinite(norm) for norm in norms):
        raise TechnicalPilotError("direction stability received invalid norm")
    cosines = [
        float(torch.dot(a, b).item() / (norm_a * norm_b))
        for a, b, norm_a, norm_b in (
            (a, b, norms[i], norms[j]) for (i, a), (j, b) in itertools.combinations(enumerate(values), 2)
        )
    ]
    mean_norm = sum(norms) / len(norms)
    return {
        "count": len(values),
        "pairwise_cosines": cosines,
        "minimum": min(cosines),
        "maximum": max(cosines),
        "norms": norms,
        "norm_coefficient_of_variation": (sum((x - mean_norm) ** 2 for x in norms) / len(norms)) ** 0.5 / mean_norm,
    }


def rank_site_rows(rows: Sequence[dict[str, Any]]) -> list[dict[str, Any]]:
    ranked = sorted(
        (dict(row) for row in rows),
        key=lambda row: (not bool(row["accepted"]), -float(row["score"]), int(row["layer"])),
    )
    for index, row in enumerate(ranked, start=1):
        row["rank"] = index
    return ranked


def technical_alpha_valid(activations: torch.Tensor, logits: torch.Tensor) -> bool:
    return bool(torch.isfinite(activations).all() and torch.isfinite(logits).all())


def achieved_dose(baseline: torch.Tensor, changed: torch.Tensor) -> dict[str, float]:
    if baseline.shape != changed.shape or baseline.numel() == 0:
        raise TechnicalPilotError("dose tensors must have equal nonzero shape")
    baseline64 = baseline.detach().to(torch.float64)
    changed64 = changed.detach().to(torch.float64)
    perturbation = changed64 - baseline64
    baseline_rms = float(torch.sqrt(torch.mean(baseline64.square())).item())
    perturbation_rms = float(torch.sqrt(torch.mean(perturbation.square())).item())
    if baseline_rms == 0:
        ratio = float("inf") if perturbation_rms else 0.0
    else:
        ratio = perturbation_rms / baseline_rms
    return {
        "baseline_rms": baseline_rms,
        "perturbation_rms": perturbation_rms,
        "perturbation_to_baseline_rms": ratio,
    }


def technical_manifest(*, run_id: str, git_commit: str, source_ids: Sequence[str]) -> dict[str, Any]:
    return {
        "schema_version": "3.1.0",
        "run_id": run_id,
        "phase": "technical_pilot",
        "scientific_execution": False,
        "engineering_only": True,
        "artifact_root": "artifacts/pilot/step_3_1",
        "git_commit": git_commit,
        "source_ids": list(source_ids),
        "step_3_0_history_preserved": True,
        "prohibitions": {
            "generation": False,
            "xstest": False,
            "harmbench": False,
            "harmbench_classifier": False,
            "mmlu": False,
            "calibration": False,
            "scientific_analysis": False,
        },
    }
