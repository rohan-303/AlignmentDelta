"""Deterministic orthogonal random controls."""

from __future__ import annotations

from dataclasses import dataclass

import torch


@dataclass(frozen=True, slots=True)
class ControlDiagnostic:
    seed: int
    norm: float
    absolute_dot: float
    hidden_dimension: int
    sha256: str


def orthogonal_control(
    direction: torch.Tensor, seed: int, tolerance: float = 1e-6
) -> tuple[torch.Tensor, ControlDiagnostic]:
    if direction.ndim != 1 or not torch.isfinite(direction).all():
        raise ValueError("direction must be a finite vector")
    r = direction.to(device="cpu", dtype=torch.float64)
    r = r / torch.linalg.vector_norm(r)
    generator = torch.Generator(device="cpu")
    generator.manual_seed(seed)
    z = torch.randn(r.shape, generator=generator, dtype=torch.float64)
    perpendicular = z - torch.dot(z, r) * r
    norm = torch.linalg.vector_norm(perpendicular)
    if not torch.isfinite(norm) or norm < 1e-12:
        raise ValueError("random control is degenerate")
    q = perpendicular / norm
    absolute_dot = float(torch.abs(torch.dot(q, r)).item())
    if absolute_dot > tolerance:
        raise ValueError(f"control is not orthogonal: {absolute_dot}")
    digest = __import__("hashlib").sha256(q.numpy().tobytes()).hexdigest()
    return q, ControlDiagnostic(seed, float(torch.linalg.vector_norm(q).item()), absolute_dot, q.numel(), digest)
