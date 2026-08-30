"""Hardware-aware precision selection without model loading."""

from __future__ import annotations


def resolve_precision(requested: str, *, device: str, cuda_bf16_supported: bool) -> str:
    """Resolve a requested precision using explicit device capabilities."""
    if requested not in {"auto", "fp32", "fp16", "bf16"}:
        raise ValueError("precision must be auto, fp32, fp16, or bf16")
    if requested == "auto":
        if device == "cuda":
            return "bf16" if cuda_bf16_supported else "fp16"
        return "fp32"
    if requested == "bf16" and device == "cuda" and not cuda_bf16_supported:
        raise ValueError("bf16 requested but CUDA BF16 support is unavailable")
    return requested
