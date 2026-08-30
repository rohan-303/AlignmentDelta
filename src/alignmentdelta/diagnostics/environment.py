"""Environment inspection and JSON diagnostic CLI."""

from __future__ import annotations

import argparse
import os
import platform
import subprocess
import sys
from datetime import UTC, datetime
from pathlib import Path
from typing import Any

from alignmentdelta.manifest import EnvironmentManifest, package_versions
from alignmentdelta.precision import resolve_precision


def _git_info() -> dict[str, Any]:
    def run(*args: str) -> str | None:
        try:
            return subprocess.run(("git", *args), capture_output=True, text=True, check=True).stdout.strip()
        except (OSError, subprocess.CalledProcessError):
            return None

    status = run("status", "--porcelain")
    return {
        "root": run("rev-parse", "--show-toplevel"),
        "commit": run("rev-parse", "HEAD"),
        "branch": run("branch", "--show-current"),
        "dirty": status is not None and bool(status),
    }


def _nvidia_smi_info() -> dict[str, Any] | None:
    try:
        completed = subprocess.run(
            ("nvidia-smi", "--query-gpu=name,driver_version,memory.total,compute_cap", "--format=csv,noheader,nounits"),
            capture_output=True,
            text=True,
            check=True,
        )
    except (OSError, subprocess.CalledProcessError):
        return None
    return {"raw": completed.stdout.strip()}


def inspect_environment(
    execution_profile: str = "cpu_test",
    *,
    seed: int = 20260830,
    deterministic: bool = True,
    quantization_enabled: bool = False,
) -> EnvironmentManifest:
    packages = package_versions()
    host: dict[str, Any] = {
        "hostname": platform.node(),
        "os": platform.platform(),
        "system": platform.system(),
        "architecture": platform.machine(),
        "python_executable": sys.executable,
        "logical_cpu_count": os.cpu_count(),
    }
    try:
        import psutil  # type: ignore[import-untyped]

        host["physical_cpu_count"] = psutil.cpu_count(logical=False)
        host["total_system_ram_bytes"] = psutil.virtual_memory().total
    except ImportError:
        host["physical_cpu_count"] = None
        host["total_system_ram_bytes"] = None
    pytorch: dict[str, Any] = {
        "installed": packages["torch"] is not None,
        "version": packages["torch"],
        "cuda_runtime": None,
        "cuda_available": False,
        "cudnn_version": None,
        "deterministic_algorithms": None,
    }
    cuda: dict[str, Any] = {"available": False, "runtime": None, "nvidia_smi": _nvidia_smi_info()}
    gpus: list[dict[str, Any]] = []
    cuda_bf16_supported = False
    try:
        import torch

        pytorch.update(
            {
                "cuda_runtime": torch.version.cuda,
                "cuda_available": torch.cuda.is_available(),
                "cudnn_version": torch.backends.cudnn.version(),  # type: ignore[no-untyped-call]
                "deterministic_algorithms": torch.are_deterministic_algorithms_enabled(),
            }
        )
        cuda.update({"available": torch.cuda.is_available(), "runtime": torch.version.cuda})
        cuda_bf16_supported = bool(torch.cuda.is_bf16_supported()) if torch.cuda.is_available() else False
        if torch.cuda.is_available():
            for index in range(torch.cuda.device_count()):
                with torch.cuda.device(index):
                    properties = torch.cuda.get_device_properties(index)
                    gpus.append(
                        {
                            "index": index,
                            "name": properties.name,
                            "compute_capability": [properties.major, properties.minor],
                            "total_memory_bytes": properties.total_memory,
                            "allocated_memory_bytes": torch.cuda.memory_allocated(index),
                            "reserved_memory_bytes": torch.cuda.memory_reserved(index),
                        }
                    )
    except ImportError:
        pass
    return EnvironmentManifest(
        schema_version="1.0",
        created_at_utc=datetime.now(UTC).isoformat(),
        git=_git_info(),
        host=host,
        python={"version": platform.python_version(), "implementation": platform.python_implementation()},
        packages=packages,
        pytorch=pytorch,
        cuda=cuda,
        gpus=gpus,
        execution_profile=execution_profile,
        reproducibility={
            "seed": seed,
            "deterministic": deterministic,
            "requested_device": "cpu" if execution_profile == "cpu_test" else "cuda",
            "resolved_device": "cuda" if cuda["available"] and execution_profile != "cpu_test" else "cpu",
            "requested_precision": "auto",
            "resolved_precision": resolve_precision(
                "auto",
                device="cuda" if cuda["available"] and execution_profile != "cpu_test" else "cpu",
                cuda_bf16_supported=cuda_bf16_supported,
            ),
        },
        quantization={"enabled": quantization_enabled, "method": None},
    )


def main() -> int:
    parser = argparse.ArgumentParser(description="Emit an actual AlignmentDelta environment diagnostic")
    parser.add_argument("--profile", default="cpu_test")
    parser.add_argument("--json-output", type=Path)
    args = parser.parse_args()
    manifest = inspect_environment(args.profile)
    import json

    payload = json.dumps(manifest.to_dict(), indent=2, sort_keys=True)
    print(payload)
    if args.json_output:
        args.json_output.parent.mkdir(parents=True, exist_ok=True)
        args.json_output.write_text(payload + "\n", encoding="utf-8")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
