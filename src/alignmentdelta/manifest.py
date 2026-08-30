"""Machine-readable environment manifest primitives."""

from __future__ import annotations

from dataclasses import asdict, dataclass
from datetime import UTC, datetime
from importlib.metadata import PackageNotFoundError, version
from typing import Any


def _package_version(name: str) -> str | None:
    try:
        return version(name)
    except PackageNotFoundError:
        return None


@dataclass(frozen=True, slots=True)
class EnvironmentManifest:
    schema_version: str
    created_at_utc: str
    git: dict[str, Any]
    host: dict[str, Any]
    python: dict[str, Any]
    packages: dict[str, str | None]
    pytorch: dict[str, Any]
    cuda: dict[str, Any]
    gpus: list[dict[str, Any]]
    execution_profile: str
    reproducibility: dict[str, Any]
    quantization: dict[str, Any]

    @classmethod
    def minimal(
        cls, execution_profile: str, seed: int, deterministic: bool, quantization_enabled: bool
    ) -> EnvironmentManifest:
        packages = {
            name: _package_version(name)
            for name in (
                "torch",
                "transformers",
                "accelerate",
                "datasets",
                "huggingface-hub",
                "safetensors",
                "numpy",
                "pandas",
                "scipy",
                "scikit-learn",
                "psutil",
                "bitsandbytes",
            )
        }
        return cls(
            schema_version="1.0",
            created_at_utc=datetime.now(UTC).isoformat(),
            git={},
            host={},
            python={},
            packages=packages,
            pytorch={},
            cuda={},
            gpus=[],
            execution_profile=execution_profile,
            reproducibility={
                "seed": seed,
                "deterministic": deterministic,
                "requested_device": "cpu",
                "resolved_device": "cpu",
                "requested_precision": "fp32",
                "resolved_precision": "fp32",
            },
            quantization={"enabled": quantization_enabled, "method": None},
        )

    def to_dict(self) -> dict[str, Any]:
        return asdict(self)


def package_versions() -> dict[str, str | None]:
    """Return versions without importing optional ML packages."""
    return {
        name: _package_version(name)
        for name in (
            "torch",
            "transformers",
            "accelerate",
            "datasets",
            "huggingface-hub",
            "safetensors",
            "numpy",
            "pandas",
            "scipy",
            "scikit-learn",
            "psutil",
            "bitsandbytes",
        )
    }
