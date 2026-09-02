"""Real cloud-only Qwen scientific adapter.

The module is not imported by dry-run or synthetic execution. Model-framework
imports are lazy and every real entry point requires the cloud profile gate.
"""

from __future__ import annotations

import hashlib
import json
import math
import subprocess
from pathlib import Path
from typing import Any, cast

EXPECTED_MODEL_ID = "Qwen/Qwen2.5-3B-Instruct"
EXPECTED_MODEL_REVISION = "aa8e72537993ba99e69dfaafa59ed015b17504d1"
EXPECTED_ARCHITECTURE = "Qwen2ForCausalLM"
EXPECTED_HIDDEN_SIZE = 2048
EXPECTED_BLOCKS = 36
LAYER = 27
EXPECTED_DIRECTION_SHA256 = "286147ed00c828028d6856e5cab4e87ed5730e1e2f6f6fff047f2d3bb71a84b1"
EXPECTED_CONTROL_SHA256 = {
    20260830: "baea625387eee599d64fc5cc36ba19347908bb8ee89843dd5c51ccfa77c4e1dd",
    20260831: "8a2bddd84b3e61e713e47b7cd22b78c9013b6316fca3eb9df65feed53955f6f9",
    20260832: "381c985be766eb3b416b5fb49efba17e7de92f01d21131d4c85f29132537864a",
    20260833: "120d1b40884bf919536f6fea3d653f6ecd5f133e30d43b9b2263ddaf6eba4984",
}


def verify_runtime_identity(model_class: str, revision: str, hidden_size: int, block_count: int) -> None:
    if (
        model_class != EXPECTED_ARCHITECTURE
        or revision != EXPECTED_MODEL_REVISION
        or hidden_size != EXPECTED_HIDDEN_SIZE
        or block_count != EXPECTED_BLOCKS
    ):
        raise RuntimeError("MODEL_RUNTIME_IDENTITY_MISMATCH")


def git_provenance(root: Path) -> dict[str, Any]:
    commit = subprocess.check_output(("git", "rev-parse", "HEAD"), cwd=root, text=True).strip()
    dirty = bool(subprocess.check_output(("git", "status", "--porcelain"), cwd=root, text=True).strip())
    if dirty:
        raise RuntimeError("CLOUD_EXECUTION_REQUIRES_CLEAN_GIT_TREE")
    return {"commit": commit, "clean": True}


def load_qwen_model(
    model_id: str = EXPECTED_MODEL_ID, revision: str = EXPECTED_MODEL_REVISION, device: str = "cuda:0"
) -> tuple[Any, Any, dict[str, Any]]:
    """Load the pinned model only; callers must have passed cloud gates first."""
    if model_id != EXPECTED_MODEL_ID or revision != EXPECTED_MODEL_REVISION or device != "cuda:0":
        raise RuntimeError("MODEL_RUNTIME_IDENTITY_MISMATCH")
    import torch
    from transformers import AutoModelForCausalLM, AutoTokenizer

    if not torch.cuda.is_available() or not torch.cuda.is_bf16_supported():
        raise RuntimeError("CLOUD_GPU_REQUIRED")
    tokenizer = cast(Any, AutoTokenizer).from_pretrained(model_id, revision=revision, trust_remote_code=False)
    model = cast(Any, AutoModelForCausalLM).from_pretrained(
        model_id,
        revision=revision,
        trust_remote_code=False,
        torch_dtype=torch.bfloat16,
        device_map=None,
        low_cpu_mem_usage=True,
    )
    model.to(torch.device(device))
    model.eval()
    decoder = getattr(model, "model", None)
    layers = getattr(decoder, "layers", None)
    hidden_size = int(getattr(decoder, "hidden_size", getattr(getattr(model, "config", None), "hidden_size", -1)))
    block_count = len(layers) if layers is not None else -1
    verify_runtime_identity(type(model).__name__, revision, hidden_size, block_count)
    first = next(model.parameters())
    if first.device.type != "cuda" or first.dtype != torch.bfloat16:
        raise RuntimeError("MODEL_RUNTIME_IDENTITY_MISMATCH")
    metadata = {
        "model_id": model_id,
        "requested_revision": revision,
        "resolved_revision": revision,
        "model_class": type(model).__name__,
        "tokenizer_class": type(tokenizer).__name__,
        "hidden_size": hidden_size,
        "block_count": block_count,
        "vocab_size": len(tokenizer),
        "dtype": str(first.dtype),
        "device": str(first.device),
        "trust_remote_code": False,
        "quantization": "none",
        "device_map": None,
    }
    return model, tokenizer, metadata


def parameter_sentinels(model: Any) -> dict[str, str]:
    result: dict[str, str] = {}
    names = (
        "model.embed_tokens.weight",
        "model.layers.0.self_attn.q_proj.weight",
        "model.layers.27.self_attn.q_proj.weight",
    )
    named = dict(model.named_parameters())
    for name in names:
        parameter = named.get(name)
        if parameter is not None:
            result[name] = hashlib.sha256(parameter.detach().cpu().contiguous().numpy().tobytes()).hexdigest()
    if len(result) < 3:
        raise RuntimeError("MODEL_RUNTIME_IDENTITY_MISMATCH")
    return result


def verify_direction_tensor(direction: Any) -> str:
    import torch

    if not isinstance(direction, torch.Tensor) or direction.ndim != 1 or direction.numel() != EXPECTED_HIDDEN_SIZE:
        raise RuntimeError("DIRECTION_RECONSTRUCTION_MISMATCH")
    if not bool(torch.isfinite(direction).all()) or not math.isclose(
        float(torch.linalg.vector_norm(direction).item()), 1.0, abs_tol=1e-6
    ):
        raise RuntimeError("DIRECTION_RECONSTRUCTION_MISMATCH")
    digest = hashlib.sha256(direction.detach().cpu().contiguous().numpy().tobytes()).hexdigest()
    if digest != EXPECTED_DIRECTION_SHA256:
        raise RuntimeError("DIRECTION_RECONSTRUCTION_MISMATCH")
    return digest


def verify_controls(direction: Any) -> dict[int, dict[str, Any]]:
    from alignmentdelta.engineering.controls import orthogonal_control

    result: dict[int, dict[str, Any]] = {}
    for seed, expected in EXPECTED_CONTROL_SHA256.items():
        control, diagnostic = orthogonal_control(direction, seed)
        if diagnostic.sha256 != expected:
            raise RuntimeError("CONTROL_RECONSTRUCTION_MISMATCH")
        result[seed] = {
            "sha256": diagnostic.sha256,
            "norm": diagnostic.norm,
            "absolute_dot": diagnostic.absolute_dot,
            "dimension": diagnostic.hidden_dimension,
        }
    return result


def reconstruct_direction(model: Any, tokenizer: Any, source_root: Path) -> Any:
    """Reconstruct using the validated layer-27 final-token capture convention."""
    import torch

    from alignmentdelta.engineering.capture import OnlineMeanDifference, ResidualCapture
    from alignmentdelta.engineering.direction import render_messages, stable_id
    from alignmentdelta.engineering.technical_pilot_core import deterministic_sample
    from alignmentdelta.experiments.source_layout import refusal_split_paths

    split_paths = refusal_split_paths(source_root)
    paths = {
        "harmful": split_paths["harmful_train"],
        "harmless": split_paths["harmless_train"],
    }
    if any(not path.exists() for path in paths.values()):
        raise RuntimeError("DIRECTION_SOURCE_MISSING")
    records: dict[str, list[dict[str, Any]]] = {
        role: json.loads(path.read_text(encoding="utf-8")) for role, path in paths.items()
    }
    sample = deterministic_sample(
        records["harmful"], records["harmless"], train_counts=(208, 208), validation_counts=(12, 12)
    )
    selected = {
        "harmful": sample["direction_train_harmful"],
        "harmless": sample["direction_train_harmless"],
    }
    accumulator = OnlineMeanDifference(EXPECTED_HIDDEN_SIZE)
    adapter = QwenScientificAdapter(model, layer=LAYER)
    for role, harmful in (("harmful", True), ("harmless", False)):
        for record in selected[role]:
            if stable_id(record) not in {stable_id(item) for item in selected[role]}:
                raise RuntimeError("DIRECTION_SAMPLE_PARITY_MISMATCH")
            rendered = render_messages(tokenizer, record)
            encoded = tokenizer(rendered, return_tensors="pt").to(model.device)
            capture = ResidualCapture(adapter.block)
            capture.install()
            try:
                with torch.inference_mode():
                    model(**encoded)
                accumulator.add(capture.result().value, harmful=harmful)
            finally:
                capture.remove()
    direction, _ = accumulator.direction()
    return direction


def cloud_preflight(root: Path, profile: str, output_root: Path) -> dict[str, Any]:
    from alignmentdelta.engineering.cloud_gate import classify_environment, inspect_cloud_environment

    if profile != "cloud_gpu":
        raise RuntimeError("CLOUD_GPU_REQUIRED")
    report = inspect_cloud_environment(profile, path=root)
    report["gate"] = classify_environment(report)
    if report["gate"]["classification"] != "eligible_cloud_gpu":
        raise RuntimeError("CLOUD_GPU_REQUIRED")
    write_gate(output_root / "manifests" / "environment_gate.json", report)
    git_provenance(root)
    return report


def technical_smoke(model: Any, tokenizer: Any, direction: Any, controls: dict[int, Any]) -> dict[str, Any]:
    import torch

    adapter = QwenScientificAdapter(model)
    before = parameter_sentinels(model)
    encoded = tokenizer("A benign engineering diagnostic.", return_tensors="pt").to(model.device)
    baseline = adapter.forward(**encoded)
    if not bool(torch.isfinite(baseline.logits).all()):
        raise RuntimeError("PRE_SCIENCE_TECHNICAL_GATE_FAIL")
    direction_hash = verify_direction_tensor(direction)
    verify_controls(direction)
    adapter.forward(**encoded, direction=direction, alpha=0.0)
    adapter.sentinel_check(before)
    return {
        "status": "PRE_SCIENCE_TECHNICAL_GATE_PASS",
        "direction_sha256": direction_hash,
        "control_count": len(controls),
        "hook_count": adapter.hook_count,
    }


class QwenScientificAdapter:
    """Run one forward/generation under a temporary layer-27 intervention."""

    def __init__(
        self, model: Any, layer: int = LAYER, hidden_size: int = EXPECTED_HIDDEN_SIZE, tokenizer: Any | None = None
    ) -> None:
        import torch.nn as nn

        decoder = getattr(model, "model", None)
        layers = getattr(decoder, "layers", None)
        actual_hidden = int(getattr(decoder, "hidden_size", hidden_size))
        if (
            layers is None
            or not isinstance(layers, nn.ModuleList)
            or len(layers) != EXPECTED_BLOCKS
            or actual_hidden != hidden_size
        ):
            raise RuntimeError("MODEL_RUNTIME_IDENTITY_MISMATCH")
        self.model = model
        self.block = layers[layer]
        self.hidden_size = hidden_size
        self.tokenizer = tokenizer
        self.hook_count = 0

    def _run(self, callable_: Any, direction: Any | None, alpha: float) -> Any:
        from alignmentdelta.engineering.projection import transform_block_output

        handle: Any = None
        if direction is not None:

            def hook(_module: Any, _inputs: tuple[Any, ...], output: Any) -> Any:
                return transform_block_output(output, direction, alpha)

            handle = self.block.register_forward_hook(hook)
            self.hook_count += 1
        try:
            return callable_()
        finally:
            if handle is not None:
                handle.remove()
                self.hook_count -= 1
            if self.hook_count != 0 or self.block._forward_hooks:
                raise RuntimeError("HOOK_REGISTRY_NOT_CLEAN")

    def forward(self, *args: Any, **inputs: Any) -> Any:
        direction = inputs.pop("direction", None)
        alpha = float(inputs.pop("alpha", 0.0))
        import torch

        with torch.inference_mode():
            return self._run(lambda: self.model(*args, **inputs), direction, alpha)

    def generate(
        self,
        tokenizer: Any,
        messages: list[dict[str, str]],
        direction: Any | None = None,
        alpha: float = 0.0,
        max_new_tokens: int = 256,
    ) -> dict[str, Any]:
        import torch

        rendered = tokenizer.apply_chat_template(messages, tokenize=False, add_generation_prompt=True)
        encoded = tokenizer(rendered, return_tensors="pt").to(self.model.device)
        with torch.inference_mode():
            output = self._run(
                lambda: self.model.generate(**encoded, do_sample=False, max_new_tokens=max_new_tokens, use_cache=True),
                direction,
                alpha,
            )
        prompt_tokens = encoded["input_ids"].shape[-1]
        text = tokenizer.decode(output[0][prompt_tokens:], skip_special_tokens=True)
        return {
            "text": text,
            "input_token_count": int(prompt_tokens),
            "output_token_count": int(output.shape[-1] - prompt_tokens),
            "finish_reason": "eos_or_length",
        }

    def generate_item(self, item: dict[str, Any], condition: dict[str, Any]) -> dict[str, Any]:
        if self.tokenizer is None:
            raise RuntimeError("TOKENIZER_REQUIRED")
        return self.generate(
            self.tokenizer,
            [{"role": "user", "content": str(item["prompt"])}],
            condition.get("direction"),
            float(condition["alpha"]),
        )

    def option_log_score(
        self, tokenizer: Any, prompt: str, option: str, direction: Any | None = None, alpha: float = 0.0
    ) -> float:
        import torch

        prompt_ids = tokenizer(prompt, return_tensors="pt")["input_ids"]
        full_ids = tokenizer(prompt + option, return_tensors="pt")["input_ids"]
        option_start = int(prompt_ids.shape[-1])
        if full_ids.shape[-1] <= option_start:
            raise ValueError("option token sequence is empty")
        inputs = {
            "input_ids": full_ids.to(self.model.device),
            "attention_mask": torch.ones_like(full_ids).to(self.model.device),
        }
        with torch.inference_mode():
            output = self._run(lambda: self.model(**inputs), direction, alpha)
        log_probs = torch.log_softmax(output.logits[0].to(torch.float64), dim=-1)
        token_ids = full_ids[0].to(self.model.device)
        positions = range(option_start - 1, full_ids.shape[-1] - 1)
        return float(sum(log_probs[position, token_ids[position + 1]].item() for position in positions))

    def score_options(self, item: dict[str, Any], condition: dict[str, Any]) -> list[float]:
        if self.tokenizer is None:
            raise RuntimeError("TOKENIZER_REQUIRED")
        prompt = str(item["question"])
        direction = condition.get("direction")
        return [
            self.option_log_score(self.tokenizer, prompt, str(option), direction, float(condition["alpha"]))
            for option in item["options"]
        ]

    def score_consistency(self, pair: dict[str, Any], condition: dict[str, Any]) -> tuple[list[float], list[float]]:
        original = {**pair, "question": pair["question"], "options": pair["source_options"]}
        transformed = {**pair, "question": pair["question"], "options": pair["variant_options"]}
        return self.score_options(original, condition), self.score_options(transformed, condition)

    def sentinel_check(self, before: dict[str, str]) -> None:
        after = parameter_sentinels(self.model)
        if after != before:
            raise RuntimeError("RUN_INVALIDATED_WEIGHT_MUTATION")


def write_gate(path: Path, report: dict[str, Any]) -> None:
    path.parent.mkdir(parents=True, exist_ok=True)
    path.write_text(json.dumps(report, indent=2, sort_keys=True) + "\n", encoding="utf-8")


def _protocol_hashes_for_cloud(root: Path) -> dict[str, str]:
    files = (
        "configs/experiments/exploratory_qwen3b.toml",
        "configs/manifests/xstest_exploratory_pilot.toml",
        "configs/manifests/mmlu_exploratory_pilot.toml",
        "configs/manifests/consistency_pairs.toml",
        "configs/manifests/mmlu.toml",
    )
    result = {}
    for relative in files:
        path = root / relative
        if not path.exists():
            raise RuntimeError("PROTOCOL_MANIFEST_MISMATCH")
        result[relative] = hashlib.sha256(path.read_bytes()).hexdigest()
    return result


def run_cloud_technical_smoke(root: Path, output_root: Path, cache_root: Path) -> dict[str, Any]:
    """Run only cloud technical gates; benchmark items are never touched."""
    from alignmentdelta.experiments.prepare_cloud_data import hydrate

    cloud_preflight(root, "cloud_gpu", output_root)
    sources = hydrate(cache_root)
    model, tokenizer, model_metadata = load_qwen_model()
    direction = reconstruct_direction(model, tokenizer, Path(sources["refusal_direction"]["root"]))
    verify_direction_tensor(direction)
    control_metadata = verify_controls(direction)
    smoke = technical_smoke(model, tokenizer, direction, control_metadata)
    payload = {
        "model": model_metadata,
        "model_id": EXPECTED_MODEL_ID,
        "model_revision": EXPECTED_MODEL_REVISION,
        "scientific_code_commit": git_provenance(root)["commit"],
        "protocol_hashes": _protocol_hashes_for_cloud(root),
        "direction_sha256": EXPECTED_DIRECTION_SHA256,
        "layer": LAYER,
        "hidden_dimension": EXPECTED_HIDDEN_SIZE,
        "controls": control_metadata,
        **smoke,
    }
    write_gate(output_root / "manifests" / "technical_pre_science_gate.json", payload)
    del model, tokenizer
    return payload
