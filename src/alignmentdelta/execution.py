"""Typed execution-profile loading."""

from __future__ import annotations

import tomllib
from dataclasses import dataclass
from pathlib import Path

_ALLOWED_DEVICES = {"auto", "cpu", "cuda"}
_ALLOWED_PRECISIONS = {"auto", "fp32", "fp16", "bf16"}


@dataclass(frozen=True, slots=True)
class ExecutionProfile:
    name: str
    preferred_device: str
    allow_quantization: bool
    preferred_precision: str
    deterministic: bool
    seed: int
    batch_size: int
    num_workers: int
    cache_path: str | None


def load_profile(name: str, directory: Path | None = None) -> ExecutionProfile:
    """Load and validate one version-controlled execution profile."""
    profile_dir = directory or Path(__file__).parents[2] / "configs" / "execution"
    path = profile_dir / f"{name}.toml"
    if not path.is_file():
        raise ValueError(f"profile not found: {name}")
    with path.open("rb") as handle:
        raw = tomllib.load(handle)
    values = raw.get("profile")
    if not isinstance(values, dict):
        raise ValueError("profile section is required")
    required = {
        "name",
        "preferred_device",
        "allow_quantization",
        "preferred_precision",
        "deterministic",
        "seed",
        "batch_size",
        "num_workers",
    }
    missing = required - values.keys()
    if missing:
        raise ValueError(f"profile fields required: {', '.join(sorted(missing))}")
    unknown = set(values) - required - {"cache_path"}
    if unknown:
        raise ValueError(f"unknown profile fields: {', '.join(sorted(unknown))}")
    if values["name"] != name:
        raise ValueError("profile name does not match filename")
    if values["preferred_device"] not in _ALLOWED_DEVICES:
        raise ValueError("preferred_device must be auto, cpu, or cuda")
    if values["preferred_precision"] not in _ALLOWED_PRECISIONS:
        raise ValueError("preferred_precision must be auto, fp32, fp16, or bf16")
    if not isinstance(values["allow_quantization"], bool) or not isinstance(values["deterministic"], bool):
        raise ValueError("boolean profile fields must be booleans")
    if not isinstance(values["seed"], int) or values["seed"] < 0:
        raise ValueError("seed must be a non-negative integer")
    if not isinstance(values["batch_size"], int) or values["batch_size"] < 1:
        raise ValueError("batch_size must be a positive integer")
    if not isinstance(values["num_workers"], int) or values["num_workers"] < 0:
        raise ValueError("num_workers must be a non-negative integer")
    cache_path = values.get("cache_path")
    if cache_path is not None and not isinstance(cache_path, str):
        raise ValueError("cache_path must be a string or null")
    return ExecutionProfile(cache_path=cache_path, **{key: values[key] for key in required})
