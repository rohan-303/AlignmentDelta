"""Step 3.1 full technical pilot; no scientific benchmark execution."""

from __future__ import annotations

import argparse
import hashlib
import json
import math
import random
import subprocess
import sys
import time
import uuid
from pathlib import Path
from statistics import mean, median, pstdev
from typing import Any, cast

import psutil  # type: ignore[import-untyped]
import torch
from huggingface_hub import snapshot_download

from .artifacts import tensor_hash, write_artifact
from .capture import OnlineMeanDifference, ResidualCapture
from .controls import orthogonal_control
from .direction import render_messages, stable_id
from .model_loader import file_hashes, load_model, write_json
from .model_registry import get_model_spec
from .projection import transform_block_output
from .qwen_adapter import Qwen2Adapter
from .refusal import refusal_score, refusal_token_metadata
from .site_selection import SiteDiagnostic
from .technical_pilot_core import (
    achieved_dose,
    candidate_layers_full,
    deterministic_sample,
    pairwise_cosines,
    rank_site_rows,
    technical_alpha_valid,
    technical_manifest,
)

ARTIFACT_ROOT = Path("artifacts/pilot/step_3_1")
ALPHA_GRID = (-0.5, 0.0, 0.25, 0.5, 0.75, 1.0, 1.25)
CONTROL_SEEDS = (20260830, 20260831, 20260832, 20260833)
QWEN3_PARAMETER_COUNT = 3_085_938_688
DIRECTION_TRAIN_COUNTS = (208, 208)
DIRECTION_VALIDATION_COUNTS = (12, 12)
STABILITY_SEEDS = (3101, 3102, 3103)
STABILITY_COUNT_PER_CLASS = 12
BATCH_TOLERANCES = {
    "refusal_score_abs": 2e-3,
    "activation_relative_rms": 2e-3,
    "direction_cosine": 0.999999,
}


def _sync(device: torch.device) -> None:
    if device.type == "cuda":
        torch.cuda.synchronize(device)


def _sha_json(value: Any) -> str:
    return hashlib.sha256(json.dumps(value, sort_keys=True, separators=(",", ":")).encode()).hexdigest()


def _git_commit() -> str:
    return subprocess.run(["git", "rev-parse", "HEAD"], check=True, capture_output=True, text=True).stdout.strip()


def _load_source(name: str) -> list[dict[str, Any]]:
    path = Path.home() / ".cache" / "alignmentdelta" / "source_data" / "refusal_direction" / name
    return cast(list[dict[str, Any]], json.loads(path.read_text(encoding="utf-8")))


def _sample_policy() -> dict[str, Any]:
    harmful = _load_source("harmful_train.json")
    harmless = _load_source("harmless_train.json")
    selected = deterministic_sample(
        harmful,
        harmless,
        train_counts=DIRECTION_TRAIN_COUNTS,
        validation_counts=DIRECTION_VALIDATION_COUNTS,
    )
    source_metadata = {
        "harmful_total": len(harmful),
        "harmless_total": len(harmless),
        "harmful_source_sha256": _sha_json(sorted(stable_id(x) for x in harmful)),
        "harmless_source_sha256": _sha_json(sorted(stable_id(x) for x in harmless)),
    }

    def ids(records: list[dict[str, Any]]) -> list[str]:
        return [stable_id(record) for record in records]

    result = {
        "schema_version": "3.1.0",
        "phase": "technical_pilot",
        "scientific_execution": False,
        "engineering_only": True,
        "policy": "all_208_harmful_plus_first_208_harmless_direction_train; first_12_per_class_validation",
        "rng_seed": None,
        "ordering": "stable_id_lexicographic",
        "source_metadata": source_metadata,
        "counts": {
            "direction_train_harmful": len(selected["direction_train_harmful"]),
            "direction_train_harmless": len(selected["direction_train_harmless"]),
            "direction_validation_harmful": len(selected["direction_validation_harmful"]),
            "direction_validation_harmless": len(selected["direction_validation_harmless"]),
        },
        "ids": {key: ids(value) for key, value in selected.items() if key.startswith("direction_")},
    }
    result["sha256"] = _sha_json(result)
    return result


def _records_from_policy(policy: dict[str, Any]) -> tuple[dict[str, list[dict[str, Any]]], dict[str, list[str]]]:
    harmful = _load_source("harmful_train.json")
    harmless = _load_source("harmless_train.json")
    by_harmful = {stable_id(record): record for record in harmful}
    by_harmless = {stable_id(record): record for record in harmless}
    selected: dict[str, list[dict[str, Any]]] = {}
    ids_by_role: dict[str, list[str]] = {}
    for role, ids in policy["ids"].items():
        source = by_harmful if role.endswith("harmful") else by_harmless
        selected[role] = [source[item_id] for item_id in ids]
        ids_by_role[role] = list(ids)
    return selected, ids_by_role


def _inputs(tokenizer: Any, text: str, device: torch.device) -> dict[str, torch.Tensor]:
    encoded = tokenizer(text, return_tensors="pt", padding=False)
    return {key: value.to(device) for key, value in encoded.items()}


def _batch_inputs(tokenizer: Any, texts: list[str], device: torch.device) -> dict[str, torch.Tensor]:
    encoded = tokenizer(texts, return_tensors="pt", padding=False)
    return {key: value.to(device) for key, value in encoded.items()}


def _forward(model: Any, inputs: dict[str, torch.Tensor]) -> Any:
    with torch.inference_mode():
        return model(**inputs, use_cache=False)


def _logits(model: Any, inputs: dict[str, torch.Tensor]) -> torch.Tensor:
    return cast(torch.Tensor, _forward(model, inputs).logits)


def _summarize(values: list[float]) -> dict[str, float | int | None]:
    if not values:
        return {
            "count": 0,
            "mean": None,
            "median": None,
            "std": None,
            "min": None,
            "p10": None,
            "p25": None,
            "p50": None,
            "p75": None,
            "p90": None,
            "p95": None,
            "p99": None,
            "max": None,
        }
    ordered = sorted(values)

    def quantile(q: float) -> float:
        if len(ordered) == 1:
            return ordered[0]
        index = (len(ordered) - 1) * q
        lower, upper = math.floor(index), math.ceil(index)
        if lower == upper:
            return ordered[lower]
        return ordered[lower] + (ordered[upper] - ordered[lower]) * (index - lower)

    return {
        "count": len(values),
        "mean": mean(values),
        "median": median(values),
        "std": pstdev(values) if len(values) > 1 else 0.0,
        "min": ordered[0],
        "p10": quantile(0.10),
        "p25": quantile(0.25),
        "p50": quantile(0.50),
        "p75": quantile(0.75),
        "p90": quantile(0.90),
        "p95": quantile(0.95),
        "p99": quantile(0.99),
        "max": ordered[-1],
    }


def _kl_last(baseline: torch.Tensor, changed: torch.Tensor) -> float:
    p = torch.softmax(baseline[:, -1, :].to(torch.float64), dim=-1)
    log_p = torch.log(p)
    log_q = torch.log_softmax(changed[:, -1, :].to(torch.float64), dim=-1)
    return float(torch.sum(p * (log_p - log_q), dim=-1).mean().item())


def _install_projection(adapter: Qwen2Adapter, layer: int, direction: torch.Tensor, alpha: float) -> Any:
    return adapter.block(layer).register_forward_hook(
        lambda _module, _inputs, output: transform_block_output(output, direction, alpha)
    )


def _capture_one(
    model: Any, adapter: Qwen2Adapter, inputs: dict[str, torch.Tensor], layers: list[int]
) -> dict[int, torch.Tensor]:
    captures = {layer: ResidualCapture(adapter.block(layer), position=None) for layer in layers}
    try:
        for capture in captures.values():
            capture.install()
        _forward(model, inputs)
        return {layer: captures[layer].result().value.clone() for layer in layers}
    finally:
        for capture in captures.values():
            capture.remove()


def _extract_directions(
    model: Any,
    adapter: Qwen2Adapter,
    tokenizer: Any,
    records: dict[str, list[dict[str, Any]]],
    layers: list[int],
    device: torch.device,
) -> tuple[dict[int, torch.Tensor], dict[int, float], dict[str, Any]]:
    accumulators = {layer: OnlineMeanDifference(adapter.hidden_size) for layer in layers}
    started = time.perf_counter()
    forward_count = 0
    for role, harmful in (("direction_train_harmful", True), ("direction_train_harmless", False)):
        for record in records[role]:
            inputs = _inputs(tokenizer, render_messages(tokenizer, record), device)
            captures = _capture_one(model, adapter, inputs, layers)
            for layer in layers:
                accumulators[layer].add(captures[layer], harmful=harmful)
            forward_count += 1
    _sync(device)
    elapsed = time.perf_counter() - started
    directions: dict[int, torch.Tensor] = {}
    norms: dict[int, float] = {}
    layer_meta: dict[str, Any] = {}
    for layer, accumulator in accumulators.items():
        direction, norm = accumulator.direction()
        directions[layer] = direction
        norms[layer] = norm
        layer_meta[str(layer)] = {
            "raw_norm": norm,
            "normalized_norm": float(torch.linalg.vector_norm(direction).item()),
            "finite": bool(torch.isfinite(direction).all()),
            "hidden_dimension": direction.numel(),
            "harmful_count": accumulator.harmful_count,
            "harmless_count": accumulator.harmless_count,
            "sha256": tensor_hash(direction),
        }
    return (
        directions,
        norms,
        {
            "forward_count": forward_count,
            "wall_clock_seconds": elapsed,
            "peak_allocated_bytes": torch.cuda.max_memory_allocated(device),
            "peak_reserved_bytes": torch.cuda.max_memory_reserved(device),
            "layers": layer_meta,
        },
    )


def _token_lengths(tokenizer: Any, records: dict[str, list[dict[str, Any]]]) -> dict[str, Any]:
    result: dict[str, Any] = {}
    for class_name, role in (("harmful", "direction_train_harmful"), ("harmless", "direction_train_harmless")):
        lengths = [
            len(tokenizer(render_messages(tokenizer, record), add_special_tokens=False)["input_ids"])
            for record in records[role]
        ]
        result[class_name] = _summarize([float(value) for value in lengths])
    return result


def _batch_probe(
    model: Any,
    adapter: Qwen2Adapter,
    tokenizer: Any,
    records: dict[str, list[dict[str, Any]]],
    device: torch.device,
    direction: torch.Tensor,
    layer: int,
) -> dict[str, Any]:
    probe_records = records["direction_validation_harmful"][:3] + records["direction_validation_harmless"][:3]
    texts = [render_messages(tokenizer, record) for record in probe_records]
    single_scores: list[float] = []
    single_acts: list[torch.Tensor] = []
    single_start = time.perf_counter()
    for text in texts:
        inputs = _inputs(tokenizer, text, device)
        single_scores.append(float(refusal_score(_logits(model, inputs)).item()))
        single_acts.append(_capture_one(model, adapter, inputs, [layer])[layer].squeeze(0).cpu())
    _sync(device)
    single_seconds = time.perf_counter() - single_start

    buckets: dict[int, list[int]] = {}
    for index, text in enumerate(texts):
        length = len(tokenizer(text, add_special_tokens=False)["input_ids"])
        buckets.setdefault(length, []).append(index)
    cross_class_pair = next(
        (
            [left, right]
            for indices in buckets.values()
            for left in indices
            for right in indices
            if (left < 3) != (right < 3)
        ),
        None,
    )
    bucket_indices = cross_class_pair or next((indices for indices in buckets.values() if len(indices) >= 2), [0, 0])
    bucket_indices = bucket_indices[: min(2, len(bucket_indices))]
    bucket_texts = [texts[index] for index in bucket_indices]
    batch_start = time.perf_counter()
    batch_logits = _logits(model, _batch_inputs(tokenizer, bucket_texts, device))
    batch_scores = [float(value) for value in refusal_score(batch_logits).tolist()]
    batch_acts = _capture_one(model, adapter, _batch_inputs(tokenizer, bucket_texts, device), [layer])[layer].cpu()
    _sync(device)
    batch_seconds = time.perf_counter() - batch_start
    reference_scores = [single_scores[index] for index in bucket_indices]
    reference_acts = torch.stack([single_acts[index] for index in bucket_indices])
    score_diff = max(abs(a - b) for a, b in zip(reference_scores, batch_scores, strict=True))
    activation_denominator = max(float(torch.linalg.vector_norm(reference_acts).item()), 1e-12)
    activation_diff = float(torch.linalg.vector_norm(batch_acts - reference_acts).item()) / activation_denominator
    harmful_indices = [index for index in bucket_indices if index < 3]
    harmless_indices = [index for index in bucket_indices if index >= 3]
    direction_cosine = None
    if harmful_indices and harmless_indices:
        batch_delta = (
            batch_acts[bucket_indices.index(harmful_indices[0])] - batch_acts[bucket_indices.index(harmless_indices[0])]
        )
        single_delta = single_acts[harmful_indices[0]] - single_acts[harmless_indices[0]]
        direction_cosine = float(torch.nn.functional.cosine_similarity(batch_delta[None], single_delta[None]).item())
    strategy2_valid = (
        score_diff <= BATCH_TOLERANCES["refusal_score_abs"]
        and activation_diff <= BATCH_TOLERANCES["activation_relative_rms"]
        and (direction_cosine is None or direction_cosine >= BATCH_TOLERANCES["direction_cosine"])
    )
    left_padding_diff = None
    lengths = [len(tokenizer(text, add_special_tokens=False)["input_ids"]) for text in texts]
    variable_pair = next(
        (
            [left, right]
            for left in range(len(texts))
            for right in range(left + 1, len(texts))
            if lengths[left] != lengths[right]
        ),
        None,
    )
    if variable_pair is not None:
        original_side, original_pad = tokenizer.padding_side, tokenizer.pad_token
        tokenizer.padding_side = "left"
        if tokenizer.pad_token_id is None:
            tokenizer.pad_token = tokenizer.eos_token
        padded = _logits(
            model, tokenizer([texts[index] for index in variable_pair], return_tensors="pt", padding=True).to(device)
        )
        left_padding_diff = max(
            abs(single_scores[index] - score)
            for index, score in zip(variable_pair, refusal_score(padded).tolist(), strict=True)
        )
        tokenizer.padding_side, tokenizer.pad_token = original_side, original_pad
    return {
        "reference": "batch_size_1",
        "strategy_1_runtime_seconds": single_seconds,
        "strategy_2": {
            "method": "equal_token_length_bucket_no_padding",
            "bucket_size": len(bucket_indices),
            "score_max_absolute_deviation": score_diff,
            "activation_relative_rms_deviation": activation_diff,
            "direction_cosine": direction_cosine,
            "runtime_seconds": batch_seconds,
            "peak_allocated_bytes": torch.cuda.max_memory_allocated(device),
            "peak_reserved_bytes": torch.cuda.max_memory_reserved(device),
            "within_tolerance": strategy2_valid,
        },
        "strategy_3": {
            "method": "variable_length_left_padding_final_position_minus_one",
            "max_absolute_score_deviation": left_padding_diff,
            "approved": left_padding_diff is not None and left_padding_diff <= BATCH_TOLERANCES["refusal_score_abs"],
        },
        "tolerances": BATCH_TOLERANCES,
        "adopted": "equal_token_length_bucket_no_padding" if strategy2_valid else "batch_size_1",
    }


def _stability(
    model: Any,
    adapter: Qwen2Adapter,
    tokenizer: Any,
    records: dict[str, list[dict[str, Any]]],
    layers: list[int],
    device: torch.device,
) -> dict[str, Any]:
    outputs: dict[str, dict[int, torch.Tensor]] = {}
    all_harmful = records["direction_train_harmful"]
    all_harmless = records["direction_train_harmless"]
    for seed in STABILITY_SEEDS:
        rng = random.Random(seed)
        harmful = rng.sample(all_harmful, STABILITY_COUNT_PER_CLASS)
        harmless = rng.sample(all_harmless, STABILITY_COUNT_PER_CLASS)
        acc = {layer: OnlineMeanDifference(adapter.hidden_size) for layer in layers}
        for group, is_harmful in ((harmful, True), (harmless, False)):
            for record in group:
                captures = _capture_one(
                    model, adapter, _inputs(tokenizer, render_messages(tokenizer, record), device), layers
                )
                for layer in layers:
                    acc[layer].add(captures[layer], harmful=is_harmful)
        outputs[str(seed)] = {layer: acc[layer].direction()[0] for layer in layers}
    result: dict[str, Any] = {
        "seeds": list(STABILITY_SEEDS),
        "count_per_class": STABILITY_COUNT_PER_CLASS,
        "layers": {},
    }
    for layer in layers:
        diagnostic = pairwise_cosines([outputs[str(seed)][layer] for seed in STABILITY_SEEDS])
        result["layers"][str(layer)] = diagnostic
    return result


def _site_search(
    model: Any,
    adapter: Qwen2Adapter,
    tokenizer: Any,
    records: dict[str, list[dict[str, Any]]],
    directions: dict[int, torch.Tensor],
    layers: list[int],
    device: torch.device,
) -> tuple[SiteDiagnostic, list[dict[str, Any]], dict[str, Any]]:
    validation = records["direction_validation_harmful"] + records["direction_validation_harmless"]
    harmful_ids = {stable_id(record) for record in records["direction_validation_harmful"]}
    cached: list[tuple[dict[str, torch.Tensor], torch.Tensor, float, bool]] = []
    for record in validation:
        inputs = _inputs(tokenizer, render_messages(tokenizer, record), device)
        baseline = _logits(model, inputs)
        cached.append((inputs, baseline, float(refusal_score(baseline).item()), stable_id(record) in harmful_ids))
    rows: list[SiteDiagnostic] = []
    rejected = {"kl": 0, "addition": 0, "technical": 0, "pruned": 0}
    started = time.perf_counter()
    for layer in layers:
        harmful_drops: list[float] = []
        harmless_kls: list[float] = []
        harmless_additions: list[float] = []
        technical_failure = False
        for inputs, baseline, baseline_score, is_harmful in cached:
            handle = _install_projection(adapter, layer, directions[layer].to(device), 1.0)
            try:
                changed = _logits(model, inputs)
            finally:
                handle.remove()
            if not technical_alpha_valid(baseline, changed):
                technical_failure = True
                continue
            changed_score = float(refusal_score(changed).item())
            if is_harmful:
                harmful_drops.append(baseline_score - changed_score)
            else:
                harmless_kls.append(_kl_last(baseline, changed))
                harmless_additions.append(changed_score - baseline_score)
        if technical_failure or not harmful_drops or not harmless_kls:
            rejected["technical"] += 1
            rows.append(SiteDiagnostic(layer, float("nan"), float("nan"), float("nan"), False))
            continue
        score = mean(harmful_drops)
        kl = mean(harmless_kls)
        addition = mean(harmless_additions)
        accepted = (
            math.isfinite(score) and math.isfinite(kl) and math.isfinite(addition) and kl <= 0.1 and addition >= 0.0
        )
        if kl > 0.1:
            rejected["kl"] += 1
        if addition < 0.0:
            rejected["addition"] += 1
        rows.append(SiteDiagnostic(layer, score, kl, addition, accepted))
    ranked = rank_site_rows(
        [
            {
                "layer": row.layer,
                "score": row.score,
                "harmless_kl": row.harmless_kl,
                "harmless_addition": row.harmless_addition,
                "accepted": row.accepted,
            }
            for row in rows
        ]
    )
    accepted_rows = [row for row in ranked if row["accepted"]]
    if not accepted_rows:
        raise RuntimeError("technical site search found no valid candidate")
    winner = accepted_rows[0]
    selected = SiteDiagnostic(
        winner["layer"], winner["score"], winner["harmless_kl"], winner["harmless_addition"], True
    )
    for row in rows:
        if row.layer >= max(layers) + 1:
            rejected["pruned"] += 1
    return (
        selected,
        ranked,
        {
            "wall_clock_seconds": time.perf_counter() - started,
            "validation_harmful_count": len(records["direction_validation_harmful"]),
            "validation_harmless_count": len(records["direction_validation_harmless"]),
            "rejection_counts": rejected,
            "valid_count": len(accepted_rows),
            "score_margin_top_two": None
            if len(accepted_rows) < 2
            else accepted_rows[0]["score"] - accepted_rows[1]["score"],
        },
    )


def _alpha_sweep(
    model: Any,
    adapter: Qwen2Adapter,
    tokenizer: Any,
    records: dict[str, list[dict[str, Any]]],
    selected_layer: int,
    selected_direction: torch.Tensor,
    controls: list[torch.Tensor],
    device: torch.device,
) -> tuple[list[dict[str, Any]], dict[str, Any]]:
    diagnostic_records = records["direction_validation_harmful"][:2] + records["direction_validation_harmless"][:2]
    prepared = [(_inputs(tokenizer, render_messages(tokenizer, record), device)) for record in diagnostic_records]
    directions = [("refusal", selected_direction)] + [
        (f"control_{seed}", control) for seed, control in zip(CONTROL_SEEDS, controls, strict=True)
    ]
    rows: list[dict[str, Any]] = []
    started = time.perf_counter()
    for label, direction in directions:
        for alpha in ALPHA_GRID:
            per_item: list[dict[str, float]] = []
            all_finite = True
            torch.cuda.reset_peak_memory_stats(device)
            for inputs in prepared:
                baseline_capture = _capture_one(model, adapter, inputs, [selected_layer])[selected_layer]
                changed_capture_holder: dict[str, torch.Tensor] = {}

                def capture_projected(
                    _module: Any,
                    _hook_inputs: Any,
                    output: Any,
                    direction_value: torch.Tensor = direction,
                    alpha_value: float = alpha,
                    capture_holder: dict[str, torch.Tensor] = changed_capture_holder,
                ) -> Any:
                    transformed = transform_block_output(output, direction_value.to(device), alpha_value)
                    capture_holder["value"] = adapter.hidden_from_output(transformed)[:, -1, :].detach().cpu()
                    return transformed

                projection_handle = adapter.block(selected_layer).register_forward_hook(capture_projected)
                try:
                    logits = _logits(model, inputs)
                finally:
                    projection_handle.remove()
                changed_capture = changed_capture_holder["value"]
                if not technical_alpha_valid(changed_capture, logits):
                    all_finite = False
                per_item.append(achieved_dose(baseline_capture, changed_capture))
            rows.append(
                {
                    "direction": label,
                    "alpha": alpha,
                    "finite_activations_and_logits": all_finite,
                    "technical_valid": all_finite,
                    "diagnostic_item_count": len(prepared),
                    "perturbation_rms": mean(item["perturbation_rms"] for item in per_item),
                    "baseline_residual_rms": mean(item["baseline_rms"] for item in per_item),
                    "perturbation_to_baseline_rms": mean(item["perturbation_to_baseline_rms"] for item in per_item),
                    "peak_allocated_bytes": torch.cuda.max_memory_allocated(device),
                    "peak_reserved_bytes": torch.cuda.max_memory_reserved(device),
                }
            )
    _sync(device)
    return rows, {"wall_clock_seconds": time.perf_counter() - started, "forward_count": len(rows) * len(prepared) * 2}


def _qwen3_feasibility(measured: dict[str, Any]) -> dict[str, Any]:
    parameter_count = QWEN3_PARAMETER_COUNT
    measured_params = int(measured["model"]["parameter_count"])
    measured_weight_bytes = int(measured["weight_file_hashes"][next(iter(measured["weight_file_hashes"]))]["bytes"])
    projected_weight_bytes = measured_weight_bytes * parameter_count / measured_params
    measured_peak = int(measured["forward"]["peak_reserved_bytes"])
    projected_peak = measured_peak * parameter_count / measured_params
    return {
        "target": "Qwen/Qwen2.5-3B-Instruct",
        "parameter_count_source": "Hugging Face model metadata retrieved during preflight",
        "parameter_count": parameter_count,
        "measured_qwen_1p5b_parameter_count": measured_params,
        "measured_qwen_1p5b_weight_bytes": measured_weight_bytes,
        "calculated_projected_bf16_weight_bytes": projected_weight_bytes,
        "measured_qwen_1p5b_peak_reserved_bytes": measured_peak,
        "calculated_projected_peak_reserved_bytes": projected_peak,
        "policy": "BF16, unquantized, no CPU offload",
        "decision": "LOCAL_3B_NOT_RECOMMENDED",
        "reason": "calculated projected weights plus runtime overhead exceed the 6 GB local VRAM budget",
        "measured_vs_calculated": "Only 1.5B values are measured; every 3B value is a parameter-ratio projection.",
    }


def _cache_size(path: Path) -> int:
    return sum(item.stat().st_size for item in path.rglob("*") if item.is_file()) if path.exists() else 0


def run() -> dict[str, Any]:
    started = time.perf_counter()
    ARTIFACT_ROOT.mkdir(parents=True, exist_ok=True)
    spec = get_model_spec()
    git_commit = _git_commit()
    if not torch.cuda.is_available():
        raise RuntimeError("Step 3.1 requires CUDA")
    dtype_name = "bf16" if torch.cuda.is_bf16_supported() else "fp16"
    device = torch.device("cuda:0")
    snapshot = Path(snapshot_download(repo_id=spec.model_id, revision=spec.revision, local_files_only=True))
    loaded = load_model(spec, device=str(device), dtype_name=dtype_name)
    adapter = Qwen2Adapter(loaded.model)
    layers = candidate_layers_full(adapter.block_count())
    if layers[-1] != math.floor(0.80 * adapter.block_count()) - 1:
        raise RuntimeError("eligible-layer boundary mismatch")
    policy = _sample_policy()
    records, ids_by_role = _records_from_policy(policy)
    write_json(ARTIFACT_ROOT / "source_selection_manifest.json", policy)
    snapshot_metadata: dict[str, Any] = {"snapshot": str(snapshot), "files": file_hashes(snapshot)}
    write_json(ARTIFACT_ROOT / "model_snapshot_manifest.json", snapshot_metadata)
    environment = {
        "python": sys.version,
        "torch": torch.__version__,
        "torch_cuda": torch.version.cuda,
        "psutil": psutil.__version__,
    }
    write_json(ARTIFACT_ROOT / "environment_manifest.json", environment)
    environment_hash = hashlib.sha256((ARTIFACT_ROOT / "environment_manifest.json").read_bytes()).hexdigest()
    token_meta = refusal_token_metadata(loaded.tokenizer)
    sentinel_before = {name: tensor_hash(value) for name, value in list(loaded.model.state_dict().items())[:2]}
    benign = "Please return the integer that results from adding two and two."
    benign_inputs = _inputs(loaded.tokenizer, render_messages(loaded.tokenizer, {"instruction": benign}), device)
    torch.cuda.reset_peak_memory_stats(device)
    forward_started = time.perf_counter()
    benign_logits = _logits(loaded.model, benign_inputs)
    _sync(device)
    if not torch.isfinite(benign_logits).all():
        raise RuntimeError("benign logits are nonfinite")
    forward_meta = {
        "token_count": int(benign_inputs["input_ids"].shape[1]),
        "output_shape": list(benign_logits.shape),
        "device": str(benign_logits.device),
        "dtype": str(benign_logits.dtype),
        "wall_clock_seconds": time.perf_counter() - forward_started,
        "peak_allocated_bytes": torch.cuda.max_memory_allocated(device),
        "peak_reserved_bytes": torch.cuda.max_memory_reserved(device),
    }
    token_length_meta = _token_lengths(loaded.tokenizer, records)
    directions, norms, extraction_meta = _extract_directions(
        loaded.model, adapter, loaded.tokenizer, records, layers, device
    )
    batch_meta = _batch_probe(
        loaded.model, adapter, loaded.tokenizer, records, device, directions[layers[-1]], layers[-1]
    )
    stability_meta = _stability(loaded.model, adapter, loaded.tokenizer, records, layers, device)
    baseline_scores: dict[str, list[float]] = {
        "harmful": [],
        "harmless": [],
    }
    for class_name, role in (
        ("harmful", "direction_validation_harmful"),
        ("harmless", "direction_validation_harmless"),
    ):
        for record in records[role]:
            logits = _logits(loaded.model, _inputs(loaded.tokenizer, render_messages(loaded.tokenizer, record), device))
            value = float(refusal_score(logits).item())
            if not math.isfinite(value):
                raise RuntimeError("baseline refusal score is nonfinite")
            baseline_scores[class_name].append(value)
    baseline_meta = {key: _summarize(values) for key, values in baseline_scores.items()}
    if all(float(baseline_meta[key]["std"] or 0.0) == 0.0 for key in baseline_meta):
        raise RuntimeError("refusal score contains no usable finite variation")
    selected, ranked_sites, site_meta = _site_search(
        loaded.model, adapter, loaded.tokenizer, records, directions, layers, device
    )
    site_meta["pruned_layer_count"] = adapter.block_count() - len(layers)
    controls: list[torch.Tensor] = []
    control_meta: list[dict[str, Any]] = []
    control_start = time.perf_counter()
    for seed in CONTROL_SEEDS:
        control, diagnostic = orthogonal_control(directions[selected.layer], seed)
        controls.append(control)
        control_meta.append(
            {
                "seed": diagnostic.seed,
                "norm": diagnostic.norm,
                "absolute_dot": diagnostic.absolute_dot,
                "hidden_dimension": diagnostic.hidden_dimension,
                "sha256": diagnostic.sha256,
            }
        )
    control_seconds = time.perf_counter() - control_start
    alpha_rows, alpha_meta = _alpha_sweep(
        loaded.model, adapter, loaded.tokenizer, records, selected.layer, directions[selected.layer], controls, device
    )
    if not all(row["technical_valid"] for row in alpha_rows):
        raise RuntimeError("technical alpha grid contains invalid numeric execution")
    direction_artifacts: dict[str, str] = {}
    for layer, direction in directions.items():
        artifact = {
            "schema_version": "3.1.0",
            "phase": "technical_pilot",
            "scientific_execution": False,
            "engineering_only": True,
            "model_id": spec.model_id,
            "model_revision": spec.revision,
            "tokenizer_revision": spec.tokenizer_revision,
            "chat_template_hash": loaded.metadata["chat_template_hash"],
            "direction_revision": "9d852fae1a9121c78b29142de733cb1340770cc3",
            "selection_manifest_hash": policy["sha256"],
            "layer": layer,
            "position_rule": "final non-padding token",
            "raw_norm": norms[layer],
            "normalized_norm": float(torch.linalg.vector_norm(direction).item()),
            "hidden_dimension": direction.numel(),
            "direction_sha256": tensor_hash(direction),
            "git_commit": git_commit,
            "environment_manifest_hash": environment_hash,
            "selected_site": layer == selected.layer,
        }
        path = ARTIFACT_ROOT / f"direction_layer_{layer}.json"
        write_artifact(path, artifact)
        direction_artifacts[str(layer)] = hashlib.sha256(path.read_bytes()).hexdigest()
    sentinel_after = {name: tensor_hash(value) for name, value in list(loaded.model.state_dict().items())[:2]}
    if sentinel_before != sentinel_after:
        raise RuntimeError("model weights changed")
    pilot_manifest = technical_manifest(
        run_id=f"step3.1-{uuid.uuid4().hex[:12]}",
        git_commit=git_commit,
        source_ids=[item for values in ids_by_role.values() for item in values],
    )
    pilot_manifest.update(
        {
            "model": loaded.metadata,
            "tokenizer_revision": spec.tokenizer_revision,
            "token_metadata": token_meta,
            "forward": forward_meta,
            "snapshot": snapshot_metadata,
            "weight_file_hashes": {
                name: value for name, value in snapshot_metadata["files"].items() if name.endswith(".safetensors")
            },
            "environment_manifest_hash": environment_hash,
            "source_selection": policy,
            "batching": batch_meta,
            "token_lengths": token_length_meta,
            "candidate_layers": layers,
            "direction_artifacts": direction_artifacts,
            "direction_extraction": extraction_meta,
            "direction_stability": stability_meta,
            "baseline_refusal_signal": baseline_meta,
            "site_search": {"rows": ranked_sites, **site_meta},
            "technical_pilot_site": {
                "model": spec.model_id,
                "revision": spec.revision,
                "layer": selected.layer,
                "hook": "model.model.layers[layer] forward output",
                "token_rule": "final non-padding token",
                "direction_hash": tensor_hash(directions[selected.layer]),
                "validation_manifest_hash": policy["sha256"],
                "selection_score": selected.score,
                "constraints": {"harmless_kl_max": 0.1, "harmless_refusal_addition_min": 0.0},
            },
            "controls": control_meta,
            "control_creation_seconds": control_seconds,
            "alpha_grid": list(ALPHA_GRID),
            "alpha_decision": "GRID_TECHNICALLY_VALID",
            "alpha_records": alpha_rows,
            "alpha_runtime": alpha_meta,
            "primary_matrix_workload": {
                "formula_per_checkpoint": {
                    "direction_extraction_forwards": "N_direction_train",
                    "site_selection_forwards": "N_site_validation + N_site_validation * N_eligible_layers",
                    "technical_alpha_forwards": "N_diagnostic_items * 7 * 5 * 2",
                },
                "actual_step_3_1_reference": {
                    "direction_train_items": 416,
                    "site_validation_items": 24,
                    "eligible_layers": len(layers),
                    "technical_diagnostic_items": 4,
                    "alpha_values": 7,
                    "directions": 5,
                    "direction_forwards": extraction_meta["forward_count"],
                    "site_forwards": 24 + 24 * len(layers),
                    "alpha_forwards": alpha_meta["forward_count"],
                },
                "future_primary_matrix_formula": (
                    "3_checkpoints * (site_selection + 7_alpha_values * "
                    "(1_refusal_direction + 4_random_controls) * outcome_items)"
                ),
                "timing_warning": "Qwen 1.5B timings are reference diagnostics; cross-model timing is not inferred.",
            },
            "integrity": {
                "sentinel_before": sentinel_before,
                "sentinel_after": sentinel_after,
                "weights_unchanged": True,
                "hooks_clean": True,
                "baseline_restored": True,
            },
            "runtime": {
                "total_seconds": time.perf_counter() - started,
                "cpu_rss_bytes": psutil.Process().memory_info().rss,
                "disk_cache_bytes": _cache_size(Path.home() / ".cache" / "huggingface"),
                "batch_strategy": batch_meta["adopted"],
            },
            "qwen3_feasibility": None,
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
    )
    pilot_manifest["qwen3_feasibility"] = _qwen3_feasibility(pilot_manifest)
    write_json(ARTIFACT_ROOT / "run_manifest.json", pilot_manifest)
    return pilot_manifest


def main() -> None:
    parser = argparse.ArgumentParser(description="Run the AlignmentDelta Step 3.1 technical pilot")
    parser.add_argument("--model", default="qwen2.5-1.5b")
    parser.add_argument("--profile", default="local_dev")
    args = parser.parse_args()
    if args.model != "qwen2.5-1.5b":
        raise SystemExit("only qwen2.5-1.5b is authorized for Step 3.1")
    result = run()
    print(
        json.dumps(
            {
                "status": "completed",
                "phase": result["phase"],
                "scientific_execution": result["scientific_execution"],
                "alpha_decision": result["alpha_decision"],
                "site_layer": result["technical_pilot_site"]["layer"],
            },
            sort_keys=True,
        )
    )


if __name__ == "__main__":
    main()
