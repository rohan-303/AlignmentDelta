"""Create an auditable planned-run manifest without scientific execution."""

from __future__ import annotations

import argparse
import subprocess
from pathlib import Path

from .atomic import atomic_write_json
from .canonical import experiment_condition_id, experiment_configuration_hash
from .config import load_experiment_config
from .ids import new_run_id
from .run_manifest import RunManifest, RunPhase, RunStatus, utc_now


def _git_value(root: Path, *args: str, fallback: str) -> str:
    try:
        return subprocess.run(["git", *args], cwd=root, check=True, capture_output=True, text=True).stdout.strip()
    except (OSError, subprocess.CalledProcessError):
        return fallback


def main(argv: list[str] | None = None) -> int:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("config", type=Path)
    parser.add_argument("--output-dir", type=Path, default=Path("artifacts") / "runs")
    args = parser.parse_args(argv)
    config_path = args.config.resolve()
    config = load_experiment_config(config_path)
    output_root = args.output_dir.resolve()
    repository_root = Path(_git_value(config_path.parent, "rev-parse", "--show-toplevel", fallback=str(Path.cwd())))
    if "results" in {part.lower() for part in output_root.parts}:
        raise ValueError("dry-run output must not be under results/")
    condition_id = experiment_condition_id(config)
    run_id = new_run_id()
    run_directory = output_root / condition_id / run_id

    def display_path(path: Path) -> str:
        try:
            return str(path.relative_to(repository_root))
        except ValueError:
            return str(path)

    manifest = RunManifest(
        schema_version="0.1",
        run_id=run_id,
        experiment_condition_id=condition_id,
        created_at_utc=utc_now(),
        status=RunStatus.PLANNED,
        phase=RunPhase(config.phase),
        experiment_config_reference=str(config_path.relative_to(repository_root)),
        experiment_config_hash=experiment_configuration_hash(config),
        git_commit=_git_value(repository_root, "rev-parse", "HEAD", fallback="unknown"),
        git_dirty=_git_value(repository_root, "status", "--porcelain", fallback="unknown") != "",
        environment_manifest_reference="<NOT_GENERATED_BY_DRY_RUN>",
        execution_profile=config.reproducibility.execution_profile,
        process_seed=config.reproducibility.seeds[0],
        output_directory=display_path(run_directory),
        scientific_execution=False,
    )
    manifest_path = run_directory / "run_manifest.json"
    atomic_write_json(manifest_path, manifest.to_dict())
    print(f"planned_run_manifest: {manifest_path}")
    print(f"run_id: {run_id}")
    print(f"experiment_condition_id: {condition_id}")
    print("status: planned")
    print("scientific_execution: false")
    print("no model, benchmark, inference, or observations were accessed")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
