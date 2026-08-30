"""Step 3.0 real-model engineering validation CLI."""

from __future__ import annotations

import argparse
import hashlib
import importlib.metadata
import json
import subprocess
import sys
import time
from dataclasses import asdict
from pathlib import Path
from typing import Any, cast

import torch
from huggingface_hub import snapshot_download

from .artifacts import direction_artifact, tensor_hash, write_artifact
from .capture import OnlineMeanDifference, ResidualCapture
from .controls import orthogonal_control
from .direction import engineering_subset, render_messages, stable_id
from .model_loader import file_hashes, load_model, write_json
from .model_registry import get_model_spec
from .projection import transform_block_output
from .qwen_adapter import Qwen2Adapter
from .refusal import refusal_score, refusal_token_metadata
from .site_selection import SiteDiagnostic, candidate_layers, select_site

ARTIFACT_ROOT = Path("artifacts/engineering/step_3_0")
ALPHAS = (0.0, 0.5, 1.0, -0.5, 1.25)
CONTROL_SEEDS = (20260830, 20260831, 20260832, 20260833)


def _sha_json(value: Any) -> str:
    return hashlib.sha256(json.dumps(value, sort_keys=True, separators=(",", ":")).encode()).hexdigest()


def _inputs(tokenizer: Any, text: str, device: torch.device) -> dict[str, torch.Tensor]:
    encoded = tokenizer(text, return_tensors="pt", padding=False)
    return {key: value.to(device) for key, value in encoded.items()}


def _forward(model: Any, inputs: dict[str, torch.Tensor]) -> Any:
    with torch.inference_mode():
        return model(**inputs, use_cache=False)


def _logits(model: Any, inputs: dict[str, torch.Tensor]) -> torch.Tensor:
    return cast(torch.Tensor, _forward(model, inputs).logits)


def _kl_at_last(baseline: torch.Tensor, changed: torch.Tensor) -> float:
    p = torch.softmax(baseline[:, -1, :].to(torch.float64), dim=-1)
    log_p = torch.log(p)
    log_q = torch.log_softmax(changed[:, -1, :].to(torch.float64), dim=-1)
    return float(torch.sum(p * (log_p - log_q), dim=-1).mean().item())


def _install_projection(adapter: Qwen2Adapter, layer: int, direction: torch.Tensor, alpha: float) -> Any:
    block = adapter.block(layer)
    return block.register_forward_hook(
        lambda _module, _inputs, output: transform_block_output(output, direction, alpha)
    )


def _sentinels(model: Any) -> dict[str, str]:
    parameters = list(model.state_dict().items())
    selected = parameters[:2] + parameters[-2:]
    return {name: tensor_hash(value) for name, value in selected}


def _subset_manifest(subset: dict[str, list[dict[str, Any]]]) -> dict[str, Any]:
    records = []
    for role, values in subset.items():
        for record in values:
            records.append({"role": role, "stable_id": stable_id(record), "source_field": "instruction"})
    records.sort(key=lambda item: (item["role"], item["stable_id"]))
    return {
        "schema_version": "3.0.0",
        "phase": "engineering",
        "scientific_execution": False,
        "engineering_only": True,
        "records": records,
        "sha256": _sha_json(records),
    }


def _environment_manifest() -> dict[str, Any]:
    packages = {}
    for name in ("torch", "transformers", "accelerate", "datasets", "safetensors"):
        try:
            packages[name] = importlib.metadata.version(name)
        except importlib.metadata.PackageNotFoundError:
            packages[name] = "unavailable"
    return {
        "python": sys.version,
        "packages": packages,
        "torch_cuda": torch.version.cuda,
        "torch_version": torch.__version__,
    }


def run() -> dict[str, Any]:
    started = time.perf_counter()
    ARTIFACT_ROOT.mkdir(parents=True, exist_ok=True)
    spec = get_model_spec()
    preflight = json.loads((ARTIFACT_ROOT / "pre_download_manifest.json").read_text(encoding="utf-8"))
    if preflight["revision"] != spec.revision or not preflight["revision_verified"]:
        raise RuntimeError("pre-download revision gate failed")
    if not torch.cuda.is_available():
        raise RuntimeError("CUDA is unavailable; Step 3.0 requires cuda:0")
    if not torch.cuda.is_bf16_supported():
        dtype_name = "fp16"
        dtype_deviation = "bf16 unavailable; FP16 selected for engineering only"
    else:
        dtype_name = "bf16"
        dtype_deviation = None
    device = torch.device("cuda:0")
    gpu = torch.cuda.get_device_properties(device)
    snapshot = Path(
        snapshot_download(
            repo_id=spec.model_id,
            revision=spec.revision,
            allow_patterns=[
                "config.json", "generation_config.json", "merges.txt", "model.safetensors",
                "tokenizer.json", "tokenizer_config.json", "vocab.json",
            ],
            local_files_only=True,
        )
    )
    loaded = load_model(spec, device=str(device), dtype_name=dtype_name)
    adapter = Qwen2Adapter(loaded.model)
    if adapter.block_count() != spec.expected_layers or adapter.hidden_size != spec.hidden_size:
        raise RuntimeError("runtime architecture does not match pinned registry")
    token_meta = refusal_token_metadata(loaded.tokenizer)
    subset = engineering_subset()
    subset_meta = _subset_manifest(subset)
    write_json(ARTIFACT_ROOT / "engineering_subset_manifest.json", subset_meta)
    model_snapshot_metadata: dict[str, Any] = {
        "snapshot": str(snapshot), "files": file_hashes(snapshot)
    }
    write_json(ARTIFACT_ROOT / "model_snapshot_manifest.json", model_snapshot_metadata)
    environment = _environment_manifest()
    environment_path = ARTIFACT_ROOT / "environment_manifest.json"
    write_json(environment_path, environment)
    environment_hash = hashlib.sha256(environment_path.read_bytes()).hexdigest()
    git_commit = subprocess.run(
        ["git", "rev-parse", "HEAD"], check=True, capture_output=True, text=True
    ).stdout.strip()
    weight_hashes = {
        name: value for name, value in model_snapshot_metadata["files"].items()
        if name.endswith(".safetensors")
    }
    sentinels_before = _sentinels(loaded.model)

    benign = "Please return the integer that results from adding two and two."
    benign_inputs = _inputs(loaded.tokenizer, render_messages(loaded.tokenizer, {"instruction": benign}), device)
    torch.cuda.reset_peak_memory_stats(device)
    forward_start = time.perf_counter()
    benign_logits = _logits(loaded.model, benign_inputs)
    forward_seconds = time.perf_counter() - forward_start
    if not torch.isfinite(benign_logits).all():
        raise RuntimeError("benign logits are nonfinite")
    forward_meta = {
        "token_count": int(benign_inputs["input_ids"].shape[1]),
        "output_shape": list(benign_logits.shape),
        "logits_device": str(benign_logits.device),
        "logits_dtype": str(benign_logits.dtype),
        "wall_clock_seconds": forward_seconds,
        "peak_allocated_bytes": torch.cuda.max_memory_allocated(device),
        "peak_reserved_bytes": torch.cuda.max_memory_reserved(device),
    }

    layers = candidate_layers(adapter.block_count())
    accumulators = {layer: OnlineMeanDifference(adapter.hidden_size) for layer in layers}
    capture_start = time.perf_counter()
    observed_output_kind = "unknown"
    train_records = subset["direction_train"]
    # The subset loader returns a combined list; source role is reconstructed by stable membership.
    harmful_ids = {stable_id(record) for record in subset["direction_train"][:8]}

    for record in train_records:
        record_id = stable_id(record)
        harmful = record_id in harmful_ids
        text = render_messages(loaded.tokenizer, record)
        inputs = _inputs(loaded.tokenizer, text, device)
        captures = {layer: ResidualCapture(adapter.block(layer), position=None) for layer in layers}
        try:
            for capture in captures.values():
                capture.install()
            _forward(loaded.model, inputs)
            for layer, capture in captures.items():
                capture_result = capture.result()
                observed_output_kind = capture_result.output_kind
                accumulators[layer].add(capture_result.value, harmful=harmful)
        finally:
            for capture in captures.values():
                capture.remove()
    direction_seconds = time.perf_counter() - capture_start
    directions: dict[int, torch.Tensor] = {}
    norms: dict[int, float] = {}
    for layer, accumulator in accumulators.items():
        directions[layer], norms[layer] = accumulator.direction()

    validation_records = subset["direction_validation"]
    harmful_val_ids = {stable_id(record) for record in validation_records[:4]}
    score_single = []
    for record in validation_records[:2]:
        inputs = _inputs(loaded.tokenizer, render_messages(loaded.tokenizer, record), device)
        score_single.append(float(refusal_score(_logits(loaded.model, inputs)).item()))
    batch_text = render_messages(loaded.tokenizer, validation_records[0])
    batch_encoded = loaded.tokenizer([batch_text, batch_text], return_tensors="pt", padding=True)
    batch_inputs = {key: value.to(device) for key, value in batch_encoded.items()}
    score_batch = [float(value) for value in refusal_score(_logits(loaded.model, batch_inputs)).tolist()]
    equal_length_diffs = [abs(score_single[0] - value) for value in score_batch]
    left_padding_diff = None
    original_padding_side = loaded.tokenizer.padding_side
    original_pad_token = loaded.tokenizer.pad_token
    loaded.tokenizer.padding_side = "left"
    if loaded.tokenizer.pad_token_id is None:
        loaded.tokenizer.pad_token = loaded.tokenizer.eos_token
    batch_texts = [render_messages(loaded.tokenizer, record) for record in validation_records[:2]]
    padded_encoded = loaded.tokenizer(batch_texts, return_tensors="pt", padding=True)
    padded_inputs = {key: value.to(device) for key, value in padded_encoded.items()}
    padded_scores = [float(value) for value in refusal_score(_logits(loaded.model, padded_inputs)).tolist()]
    left_padding_diff = max(abs(a - b) for a, b in zip(score_single, padded_scores, strict=True))
    loaded.tokenizer.padding_side = original_padding_side
    loaded.tokenizer.pad_token = original_pad_token
    score_consistency = {
        "items": len(score_batch),
        "comparison": "duplicated equal-length unpadded batch",
        "max_absolute_difference": max(equal_length_diffs),
        "within_tolerance": max(equal_length_diffs) <= 2e-3,
        "tolerance": 2e-3,
        "left_padding_max_absolute_difference": left_padding_diff,
        "padding_resolution": "batch_size_1_or_equal_length_unpadded",
    }
    if not score_consistency["within_tolerance"]:
        raise RuntimeError("batch/single refusal score inconsistency")
    site_rows: list[SiteDiagnostic] = []
    site_start = time.perf_counter()
    for layer in layers:
        harmful_drops = []
        harmless_kls = []
        harmless_additions = []
        for record in validation_records:
            harmful = stable_id(record) in harmful_val_ids
            inputs = _inputs(loaded.tokenizer, render_messages(loaded.tokenizer, record), device)
            baseline = _logits(loaded.model, inputs)
            baseline_score = float(refusal_score(baseline).item())
            handle = _install_projection(adapter, layer, directions[layer].to(device), 1.0)
            try:
                changed = _logits(loaded.model, inputs)
            finally:
                handle.remove()
            changed_score = float(refusal_score(changed).item())
            if harmful:
                harmful_drops.append(baseline_score - changed_score)
            else:
                harmless_kls.append(_kl_at_last(baseline, changed))
                harmless_additions.append(changed_score - baseline_score)
        score = float(sum(harmful_drops) / len(harmful_drops))
        kl = float(sum(harmless_kls) / len(harmless_kls))
        addition = float(sum(harmless_additions) / len(harmless_additions))
        site_rows.append(SiteDiagnostic(layer, score, kl, addition, kl <= 0.1 and addition >= 0.0))
    site_seconds = time.perf_counter() - site_start
    selected = select_site(site_rows)

    selected_direction = directions[selected.layer]
    controls = []
    for seed in CONTROL_SEEDS:
        _, diagnostic = orthogonal_control(selected_direction, seed)
        controls.append({
            "seed": diagnostic.seed,
            "norm": diagnostic.norm,
            "absolute_dot": diagnostic.absolute_dot,
            "hidden_dimension": diagnostic.hidden_dimension,
            "sha256": diagnostic.sha256,
        })

    alpha_rows = []
    intervention_start = time.perf_counter()
    baseline_before = _logits(loaded.model, benign_inputs).detach().cpu()
    for alpha in ALPHAS:
        projection: list[float] = []
        def hook(
            _module: Any,
            _inputs: Any,
            output: Any,
            alpha_value: float = alpha,
            projection_values: list[float] = projection,
        ) -> Any:
            hidden = adapter.hidden_from_output(output)
            final = hidden[:, -1, :].detach().to(torch.float64)
            r = selected_direction.to(hidden.device, dtype=torch.float64)
            before = torch.sum(final * r, dim=-1).mean().item()
            transformed = transform_block_output(
                output, selected_direction.to(hidden.device), alpha_value
            )
            hidden_after = adapter.hidden_from_output(transformed)
            after = torch.sum(hidden_after[:, -1, :].to(torch.float64) * r, dim=-1).mean().item()
            projection_values.extend([before, after])
            return transformed
        handle = adapter.block(selected.layer).register_forward_hook(hook)
        torch.cuda.reset_peak_memory_stats(device)
        try:
            changed = _logits(loaded.model, benign_inputs)
        finally:
            handle.remove()
        if not torch.isfinite(changed).all() or len(projection) != 2:
            raise RuntimeError("real intervention invariant failed")
        before, after = projection
        expected_after = before * (1.0 - alpha)
        if abs(after - expected_after) > max(1e-3, abs(before) * 2e-3):
            raise RuntimeError(f"real projection invariant failed at alpha={alpha}")
        alpha_rows.append({
            "alpha": alpha,
            "hook_removed": True,
            "finite_logits": True,
            "pre_projection": before,
            "post_projection": after,
            "achieved_fraction_removed": None if before == 0 else 1.0 - after / before,
            "peak_allocated_bytes": torch.cuda.max_memory_allocated(device),
            "peak_reserved_bytes": torch.cuda.max_memory_reserved(device),
        })
    intervention_seconds = time.perf_counter() - intervention_start
    baseline_after = _logits(loaded.model, benign_inputs).detach().cpu()
    if not torch.allclose(baseline_before, baseline_after, rtol=1e-3, atol=1e-3):
        raise RuntimeError("baseline changed after hook cleanup")
    sentinels_after = _sentinels(loaded.model)
    if sentinels_before != sentinels_after:
        raise RuntimeError("model sentinel weights changed")

    direction_artifacts: dict[str, str] = {}
    for layer, direction in directions.items():
        artifact = direction_artifact(
            model_id=spec.model_id, revision=spec.revision, tokenizer_revision=spec.tokenizer_revision,
            template_hash=loaded.metadata["chat_template_hash"], source_manifest_hash=subset_meta["sha256"],
            subset_hash=subset_meta["sha256"], layer=layer, position_rule="final non-padding token",
            raw_norm=norms[layer], direction=direction, git_commit=git_commit,
            environment_reference=environment_hash,
        )
        artifact_path = ARTIFACT_ROOT / f"direction_layer_{layer}.json"
        write_artifact(artifact_path, artifact)
        direction_artifacts[str(layer)] = hashlib.sha256(artifact_path.read_bytes()).hexdigest()

    architecture_metadata = asdict(adapter.architecture)
    architecture_metadata["output_kind"] = observed_output_kind
    result = {
        "schema_version": "3.0.0", "phase": "engineering", "scientific_execution": False, "engineering_only": True,
        "status": "completed", "git_commit": git_commit, "model": loaded.metadata,
        "architecture": architecture_metadata,
        "environment_manifest_hash": environment_hash,
        "dtype_policy": {
            "selected": dtype_name,
            "cuda_bf16_supported": torch.cuda.is_bf16_supported(),
            "deviation": dtype_deviation,
        },
        "hardware": {"device": str(device), "gpu_name": gpu.name, "total_vram_bytes": gpu.total_memory},
        "token_metadata": token_meta, "subset": subset_meta, "snapshot": model_snapshot_metadata,
        "weight_file_hashes": weight_hashes, "sentinels_before": sentinels_before, "sentinels_after": sentinels_after,
        "forward": forward_meta, "candidate_layers": layers, "direction_norms": norms,
        "score_consistency": score_consistency,
        "direction_artifacts": direction_artifacts,
        "timings": {
            "direction_subset_seconds": direction_seconds,
            "site_selection_seconds": site_seconds,
            "intervention_seconds": intervention_seconds,
            "total_seconds": time.perf_counter() - started,
        },
        "sites": [asdict(row) for row in site_rows],
        "selected_site": {"layer": selected.layer, "engineering_only": True},
        "controls": controls, "intervention": alpha_rows, "baseline_restored": True, "weights_unchanged": True,
        "prohibitions": {
            "generation": False,
            "xstest": False,
            "harmbench": False,
            "mmlu": False,
            "scientific_analysis": False,
        },
    }
    write_json(ARTIFACT_ROOT / "run_manifest.json", result)
    return result


def main() -> None:
    parser = argparse.ArgumentParser(description="Run the AlignmentDelta Step 3 engineering validation")
    parser.add_argument("--model", default="qwen2.5-1.5b")
    parser.add_argument("--profile", default="local_dev")
    args = parser.parse_args()
    if args.model != "qwen2.5-1.5b":
        raise SystemExit("only qwen2.5-1.5b is authorized for Step 3.0")
    result = run()
    print(json.dumps({
        "status": result["status"],
        "phase": result["phase"],
        "scientific_execution": result["scientific_execution"],
        "selected_layer": result["selected_site"]["layer"],
    }, sort_keys=True))


if __name__ == "__main__":
    main()
