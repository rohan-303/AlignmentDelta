"""Stable scientific condition canonicalization and identity helpers."""

from __future__ import annotations

import hashlib
import json
from copy import deepcopy
from typing import Any

from .config import ExperimentConfig


def canonical_condition_payload(config: ExperimentConfig) -> dict[str, Any]:
    """Return the scientific fields used for condition identity.

    Execution profile and planned replicate count describe execution planning,
    not the scientific condition. Hardware, host, cache, timestamps, and run
    identity are not present in ExperimentConfig and are never hashed here.
    Seeds remain included because the seed policy can affect stochastic studies.
    """
    payload = deepcopy(config.to_dict())
    reproducibility = payload["reproducibility"]
    reproducibility.pop("execution_profile", None)
    reproducibility.pop("planned_replicates", None)
    return payload


def canonical_condition_json(config: ExperimentConfig) -> str:
    """Serialize condition fields deterministically for hashing."""
    return json.dumps(canonical_condition_payload(config), sort_keys=True, separators=(",", ":"), ensure_ascii=True)


def experiment_condition_id(config: ExperimentConfig) -> str:
    """Return a readable SHA-256 identity for a scientific condition."""
    digest = hashlib.sha256(canonical_condition_json(config).encode("utf-8")).hexdigest()[:16]
    return f"condition-{digest}"


def experiment_configuration_hash(config: ExperimentConfig) -> str:
    """Hash the complete parsed scientific configuration for provenance."""
    serialized = json.dumps(config.to_dict(), sort_keys=True, separators=(",", ":"), ensure_ascii=True)
    return f"sha256:{hashlib.sha256(serialized.encode('utf-8')).hexdigest()}"
