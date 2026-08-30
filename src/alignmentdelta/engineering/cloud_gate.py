"""Hardware gate for the cloud-only primary Qwen technical run."""

from __future__ import annotations

import argparse
import json
import platform
import shutil
import subprocess
import sys
from pathlib import Path
from typing import Any

MIN_VRAM_BYTES = 12 * 1024**3
MIN_FREE_DISK_BYTES = 12 * 1024**3


def _git_commit() -> str | None:
    try:
        return subprocess.run(("git", "rev-parse", "HEAD"), check=True, capture_output=True, text=True).stdout.strip()
    except (OSError, subprocess.CalledProcessError):
        return None


def inspect_cloud_environment(profile: str, *, path: Path | str = ".") -> dict[str, Any]:
    """Collect actual hardware facts without loading or downloading a model."""
    root = Path(path)
    free_disk = shutil.disk_usage(root).free
    report: dict[str, Any] = {
        "profile": profile,
        "platform": platform.platform(),
        "python": sys.version,
        "python_executable": sys.executable,
        "git_commit": _git_commit(),
        "free_disk_bytes": free_disk,
        "torch_version": None,
        "torch_cuda_runtime": None,
        "cuda_available": False,
        "gpu_count": 0,
        "gpus": [],
        "bf16_supported": False,
    }
    try:
        import torch
    except ImportError:
        return report
    report.update(
        {
            "torch_version": torch.__version__,
            "torch_cuda_runtime": torch.version.cuda,
            "cuda_available": bool(torch.cuda.is_available()),
        }
    )
    if not report["cuda_available"]:
        return report
    report["gpu_count"] = torch.cuda.device_count()
    report["bf16_supported"] = bool(torch.cuda.is_bf16_supported())
    for index in range(torch.cuda.device_count()):
        properties = torch.cuda.get_device_properties(index)
        report["gpus"].append(
            {
                "index": index,
                "name": properties.name,
                "total_vram_bytes": properties.total_memory,
                "bf16_supported": bool(torch.cuda.is_bf16_supported()),
                "allocated_vram_bytes": torch.cuda.memory_allocated(index),
                "reserved_vram_bytes": torch.cuda.memory_reserved(index),
            }
        )
    return report


def classify_environment(report: dict[str, Any]) -> dict[str, Any]:
    """Apply the frozen cloud eligibility policy deterministically."""
    reasons: list[str] = []
    if report.get("profile") == "local_dev":
        reasons.append("local_profile_forbidden")
    if not report.get("cuda_available", False):
        reasons.append("cuda_unavailable")
    if int(report.get("total_vram_bytes", 0) or 0) < MIN_VRAM_BYTES:
        gpu_values = [int(gpu.get("total_vram_bytes", 0) or 0) for gpu in report.get("gpus", [])]
        if gpu_values:
            maximum = max(gpu_values)
        else:
            maximum = int(report.get("total_vram_bytes", 0) or 0)
        if maximum < MIN_VRAM_BYTES:
            reasons.append("vram_below_minimum")
    if not report.get("bf16_supported", False):
        reasons.append("bf16_unsupported")
    if int(report.get("free_disk_bytes", 0) or 0) < MIN_FREE_DISK_BYTES:
        reasons.append("free_disk_below_minimum")
    return {
        "classification": "eligible_cloud_gpu" if not reasons else "insufficient_gpu",
        "reasons": reasons,
        "minimum_vram_bytes": MIN_VRAM_BYTES,
        "minimum_free_disk_bytes": MIN_FREE_DISK_BYTES,
    }


def gate_report(report: dict[str, Any]) -> dict[str, Any]:
    return {**report, "gate": classify_environment(report)}


def validate_cloud_cli_args(model: str, profile: str) -> None:
    if model.lower() not in {"qwen2.5-3b", "qwen/qwen2.5-3b-instruct"}:
        raise ValueError("model must be the pinned qwen2.5-3b target")
    if profile != "cloud_gpu":
        raise ValueError("profile must be cloud_gpu; local 3B execution is forbidden")


def main() -> int:
    parser = argparse.ArgumentParser(description="Inspect and gate a cloud GPU without loading a model")
    parser.add_argument("--profile", default="cloud_gpu")
    parser.add_argument("--json-output", type=Path)
    parser.add_argument("--require-eligible", action="store_true")
    args = parser.parse_args()
    result = gate_report(inspect_cloud_environment(args.profile))
    payload = json.dumps(result, indent=2, sort_keys=True)
    print(payload)
    if args.json_output:
        args.json_output.parent.mkdir(parents=True, exist_ok=True)
        args.json_output.write_text(payload + "\n", encoding="utf-8")
    if args.require_eligible and result["gate"]["classification"] != "eligible_cloud_gpu":
        print("CLOUD_GPU_REQUIRED")
        return 2
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
