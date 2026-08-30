"""Cloud-only entry point for Step 3.2 primary Qwen technical validation."""

from __future__ import annotations

import argparse
import json
from pathlib import Path

from .artifact_transfer import create_archive
from .cloud_gate import classify_environment, inspect_cloud_environment, validate_cloud_cli_args
from .model_registry import QWEN25_3B
from .technical_pilot import run

ARTIFACT_ROOT = Path("artifacts/pilot/step_3_2")


def main() -> int:
    parser = argparse.ArgumentParser(description="Run Step 3.2 on an eligible cloud GPU only")
    parser.add_argument("--model", default="qwen2.5-3b")
    parser.add_argument("--profile", default="cloud_gpu")
    parser.add_argument("--artifact-root", type=Path, default=ARTIFACT_ROOT)
    parser.add_argument("--archive", type=Path)
    args = parser.parse_args()
    try:
        validate_cloud_cli_args(args.model, args.profile)
    except ValueError as error:
        parser.error(str(error))
    report = inspect_cloud_environment(args.profile, path=args.artifact_root.parent)
    gate = classify_environment(report)
    args.artifact_root.mkdir(parents=True, exist_ok=True)
    (args.artifact_root / "environment_gate.json").write_text(
        json.dumps({**report, "gate": gate}, indent=2, sort_keys=True) + "\n", encoding="utf-8"
    )
    if gate["classification"] != "eligible_cloud_gpu":
        print("CLOUD_GPU_REQUIRED")
        return 2
    result = run(
        model_spec=QWEN25_3B,
        artifact_root=args.artifact_root,
        allow_download=True,
        schema_version="3.2.0",
        artifact_root_name="artifacts/pilot/step_3_2",
    )
    result["schema_version"] = "3.2.0"
    result["artifact_root"] = "artifacts/pilot/step_3_2"
    result["run_id"] = result["run_id"].replace("step3.1-", "step3.2-", 1)
    result["execution_profile"] = args.profile
    result["primary_qwen_technical_decision"] = (
        "PRIMARY_QWEN_TECHNICAL_PASS"
        if result["alpha_decision"] == "GRID_TECHNICALLY_VALID"
        else "PRIMARY_QWEN_TECHNICAL_BLOCKED"
    )
    (args.artifact_root / "run_manifest.json").write_text(
        json.dumps(result, indent=2, sort_keys=True) + "\n", encoding="utf-8"
    )
    if args.archive:
        manifest = create_archive(args.artifact_root, args.archive)
        print(json.dumps({"status": result["primary_qwen_technical_decision"], "archive": manifest}, sort_keys=True))
    else:
        print(
            json.dumps(
                {"status": result["primary_qwen_technical_decision"], "run_id": result["run_id"]}, sort_keys=True
            )
        )
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
