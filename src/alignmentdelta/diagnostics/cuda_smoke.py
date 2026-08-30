"""Harmless CUDA numerical infrastructure diagnostic."""

from __future__ import annotations

from typing import Any


def run_cuda_smoke_test() -> dict[str, Any]:
    try:
        import torch
    except ImportError:
        return {"status": "unavailable", "reason": "PyTorch is not installed"}
    if not torch.cuda.is_available():
        return {"status": "unavailable", "reason": "CUDA is not available"}
    try:
        device = torch.device("cuda:0")
        left = torch.arange(4, dtype=torch.float32, device=device).reshape(2, 2)
        right = torch.eye(2, dtype=torch.float32, device=device)
        actual = left @ right
        torch.cuda.synchronize(device)
        expected = left.cpu() @ right.cpu()
        passed = bool(torch.allclose(actual.cpu(), expected, rtol=1e-5, atol=1e-6))
        return {
            "status": "passed" if passed else "failed",
            "device": torch.cuda.get_device_name(0),
            "dtype": str(actual.dtype),
            "shape": list(actual.shape),
            "passed": passed,
        }
    except Exception as exc:  # pragma: no cover - hardware-dependent
        return {"status": "failed", "error_type": type(exc).__name__, "error": str(exc)}
