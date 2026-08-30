"""Residual hooks and online float64 activation accumulation."""

from __future__ import annotations

from dataclasses import dataclass
from typing import Any

import torch
from torch import nn


@dataclass(slots=True)
class CaptureResult:
    value: torch.Tensor
    calls: int
    position: int
    output_kind: str


class ResidualCapture:
    def __init__(self, layer: nn.Module, position: int | None = None) -> None:
        self.layer = layer
        self.position = position
        self.calls = 0
        self._value: torch.Tensor | None = None
        self.output_kind = "unknown"
        self._handle: Any = None

    def _hook(self, _module: nn.Module, _inputs: tuple[Any, ...], output: Any) -> Any:
        self.output_kind = type(output).__name__
        hidden = output if isinstance(output, torch.Tensor) else output[0]
        if not isinstance(hidden, torch.Tensor) or hidden.ndim != 3:
            raise TypeError("residual hook expected [batch, sequence, hidden] tensor")
        pos = self.position if self.position is not None else hidden.shape[1] - 1
        self._value = hidden[:, pos, :].detach().to(device="cpu")
        self.calls += 1
        return output

    def install(self) -> None:
        if self._handle is not None:
            raise RuntimeError("capture hook already installed")
        self._handle = self.layer.register_forward_hook(self._hook)

    def remove(self) -> None:
        if self._handle is not None:
            self._handle.remove()
            self._handle = None

    def result(self) -> CaptureResult:
        if self._value is None:
            raise RuntimeError("capture hook has not observed a forward pass")
        position = self.position if self.position is not None else -1
        return CaptureResult(self._value, self.calls, position, self.output_kind)

    def __enter__(self) -> ResidualCapture:
        self.install()
        return self

    def __exit__(self, _type: Any, _value: Any, _traceback: Any) -> None:
        self.remove()


class OnlineMeanDifference:
    def __init__(self, hidden_size: int) -> None:
        self.harmful_sum = torch.zeros(hidden_size, dtype=torch.float64)
        self.harmless_sum = torch.zeros(hidden_size, dtype=torch.float64)
        self.harmful_count = 0
        self.harmless_count = 0

    def add(self, activations: torch.Tensor, *, harmful: bool) -> None:
        values = activations.detach().to(device="cpu", dtype=torch.float64)
        if values.ndim != 2 or values.shape[-1] != self.harmful_sum.shape[0]:
            raise ValueError("activation shape mismatch")
        if not torch.isfinite(values).all():
            raise ValueError("activation contains nonfinite values")
        if harmful:
            self.harmful_sum += values.sum(dim=0)
            self.harmful_count += values.shape[0]
        else:
            self.harmless_sum += values.sum(dim=0)
            self.harmless_count += values.shape[0]

    def direction(self) -> tuple[torch.Tensor, float]:
        if not self.harmful_count or not self.harmless_count:
            raise ValueError("both contrast groups require observations")
        raw = self.harmful_sum / self.harmful_count - self.harmless_sum / self.harmless_count
        if not torch.isfinite(raw).all():
            raise ValueError("direction contains nonfinite values")
        norm = float(torch.linalg.vector_norm(raw).item())
        if norm < 1e-12:
            raise ValueError("direction norm is below 1e-12")
        return raw / norm, norm
