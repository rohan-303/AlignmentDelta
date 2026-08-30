"""Validate an experiment configuration without network or model access."""

from __future__ import annotations

import argparse
from pathlib import Path

from .canonical import canonical_condition_json, experiment_condition_id
from .config import load_experiment_config


def main(argv: list[str] | None = None) -> int:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("config", type=Path)
    args = parser.parse_args(argv)
    config = load_experiment_config(args.config)
    print(f"valid: {args.config}")
    print(f"experiment: {config.study.name}")
    print(f"phase: {config.phase}")
    print(f"protocol: {config.study.protocol_version}")
    print(f"experiment_condition_id: {experiment_condition_id(config)}")
    print(f"canonical_bytes: {len(canonical_condition_json(config).encode('utf-8'))}")
    print("scientific_execution: false")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
