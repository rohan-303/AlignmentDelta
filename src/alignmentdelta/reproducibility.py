"""Central random-seeding helper."""

from __future__ import annotations

import random
from typing import Any

import numpy as np


def seed_everything(seed: int, *, deterministic: bool = False) -> dict[str, Any]:
    """Seed available random generators and report Torch limitations honestly."""
    if seed < 0:
        raise ValueError("seed must be non-negative")
    random.seed(seed)
    np.random.seed(seed)
    result: dict[str, Any] = {
        "seed": seed,
        "torch_available": False,
        "cuda_seeded": False,
        "deterministic_requested": deterministic,
    }
    try:
        import torch
    except ImportError:
        return result
    torch.manual_seed(seed)
    result["torch_available"] = True
    if torch.cuda.is_available():
        torch.cuda.manual_seed_all(seed)
        result["cuda_seeded"] = True
    if deterministic:
        torch.use_deterministic_algorithms(True)
        result["deterministic_algorithms_enabled"] = True
        result["determinism_note"] = "Determinism can reduce performance and unsupported operators may still fail."
    else:
        result["deterministic_algorithms_enabled"] = False
    return result
