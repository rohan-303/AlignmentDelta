"""Explicit, revision-pinned model loading."""

from __future__ import annotations

import hashlib
import json
from dataclasses import dataclass
from pathlib import Path
from typing import Any, cast

import torch
from transformers import AutoModelForCausalLM, AutoTokenizer

from .model_registry import ModelSpec, validate_spec


@dataclass(slots=True)
class LoadedModel:
    spec: ModelSpec
    model: Any
    tokenizer: Any
    device: torch.device
    dtype: torch.dtype
    metadata: dict[str, Any]


def _template_hash(tokenizer: Any) -> str:
    template = tokenizer.chat_template or ""
    return hashlib.sha256(template.encode()).hexdigest()


def _dtype(name: str) -> torch.dtype:
    if name == "bf16":
        return torch.bfloat16
    if name == "fp16":
        return torch.float16
    raise ValueError(f"unsupported engineering dtype: {name}")


def load_model(spec: ModelSpec, device: str = "cuda:0", dtype_name: str = "bf16") -> LoadedModel:
    validate_spec(spec)
    if not torch.cuda.is_available() or device != "cuda:0":
        raise RuntimeError("Step 3.0 requires CUDA device cuda:0")
    dtype = _dtype(dtype_name)
    tokenizer = cast(Any, AutoTokenizer.from_pretrained(
        spec.model_id, revision=spec.tokenizer_revision, trust_remote_code=False  # type: ignore[no-untyped-call]
    ))
    model = cast(Any, AutoModelForCausalLM.from_pretrained(
        spec.model_id,
        revision=spec.revision,
        trust_remote_code=False,
        dtype=dtype,
        device_map=None,
        low_cpu_mem_usage=True,
    ))
    model.to(torch.device(device))
    model.eval()
    first = next(model.parameters())
    if first.device != torch.device(device) or first.dtype != dtype:
        raise RuntimeError(f"unexpected model placement: {first.device}/{first.dtype}")
    parameter_count = sum(parameter.numel() for parameter in model.parameters())
    metadata = {
        "model_class": type(model).__name__,
        "parameter_count": parameter_count,
        "device": str(first.device),
        "dtype": str(first.dtype),
        "tokenizer_class": type(tokenizer).__name__,
        "vocab_size": len(tokenizer),
        "chat_template_hash": _template_hash(tokenizer),
        "trust_remote_code": False,
        "revision": spec.revision,
        "tokenizer_revision": spec.tokenizer_revision,
    }
    return LoadedModel(spec, model, tokenizer, torch.device(device), dtype, metadata)


def file_hashes(snapshot: Path) -> dict[str, dict[str, Any]]:
    result: dict[str, dict[str, Any]] = {}
    for path in sorted(snapshot.rglob("*")):
        if path.is_file():
            digest = hashlib.sha256(path.read_bytes()).hexdigest()
            result[str(path.relative_to(snapshot))] = {"bytes": path.stat().st_size, "sha256": digest}
    return result


def write_json(path: Path, value: dict[str, Any]) -> None:
    path.parent.mkdir(parents=True, exist_ok=True)
    payload = json.dumps(value, indent=2, sort_keys=True) + "\n"
    temporary = path.with_suffix(path.suffix + ".tmp")
    temporary.write_text(payload, encoding="utf-8")
    temporary.replace(path)
