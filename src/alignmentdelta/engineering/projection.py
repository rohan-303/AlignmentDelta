"""Numerically explicit engineering operators."""

from __future__ import annotations

from typing import Any

import torch


def signed_projection(hidden: torch.Tensor, direction: torch.Tensor, alpha: float) -> torch.Tensor:
    """Apply h' = h - alpha*r*(r^T h) over the last hidden dimension."""
    if hidden.ndim < 1 or direction.ndim != 1 or hidden.shape[-1] != direction.shape[0]:
        raise ValueError("hidden/direction dimensions do not match")
    finite_alpha = torch.isfinite(torch.tensor(alpha))
    if not torch.isfinite(hidden).all() or not torch.isfinite(direction).all() or not finite_alpha:
        raise ValueError("projection inputs must be finite")
    direction_work = direction.to(device=hidden.device, dtype=torch.float32)
    hidden_work = hidden.to(dtype=torch.float32)
    dot = torch.sum(hidden_work * direction_work, dim=-1, keepdim=True)
    changed = hidden_work - float(alpha) * dot * direction_work
    return changed.to(dtype=hidden.dtype)


def transform_block_output(output: Any, direction: torch.Tensor, alpha: float) -> Any:
    """Transform only the hidden tensor while preserving tuple/list structure."""
    if isinstance(output, torch.Tensor):
        return signed_projection(output, direction, alpha)
    if isinstance(output, tuple):
        if not output or not isinstance(output[0], torch.Tensor):
            raise TypeError("block tuple has no leading hidden tensor")
        return (signed_projection(output[0], direction, alpha), *output[1:])
    if isinstance(output, list):
        if not output or not isinstance(output[0], torch.Tensor):
            raise TypeError("block list has no leading hidden tensor")
        return [signed_projection(output[0], direction, alpha), *output[1:]]
    raise TypeError(f"unsupported block output: {type(output).__name__}")
