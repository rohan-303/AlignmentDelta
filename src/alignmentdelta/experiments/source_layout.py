"""Canonical pinned source-tree layouts used by cloud experiments."""

from __future__ import annotations

import os
from pathlib import Path

REFUSAL_REVISION = "9d852fae1a9121c78b29142de733cb1340770cc3"
XSTEST_REVISION = "d7bb5bd738c1fcbc36edd83d5e7d1b71a3e2d84d"
MMLU_REVISION = "c30699e8356da336a370243923dbaf21066bb9fe"

REFUSAL_SPLIT_FILES = {
    "harmful_train": "dataset/splits/harmful_train.json",
    "harmful_val": "dataset/splits/harmful_val.json",
    "harmful_test": "dataset/splits/harmful_test.json",
    "harmless_train": "dataset/splits/harmless_train.json",
    "harmless_val": "dataset/splits/harmless_val.json",
    "harmless_test": "dataset/splits/harmless_test.json",
}

REFUSAL_SPLIT_SHA256 = {
    "harmful_train": "8f5c0eac0efd2a7f99084bbe8d0de2c465e31b1997184783c917969d9de9ece1",
    "harmful_val": "305f1d1e6dfa6c50a32d24a18ef815f42b5441eb83e6d7767d242107162fd9f4",
    "harmful_test": "5e12ae102c3791dee083a69ab6269a78e033411c629bc3f66f75d2fde196d9ef",
    "harmless_train": "86623b1f8a25aa35df153fc97a556dbcebb6a7c881538ae43ee479ca17f2e002",
    "harmless_val": "772010758e7d771ef4c7e5e4acdfd7598dcece1a6f383f20d382f640913a2a4d",
    "harmless_test": "1b5930ce5e855ada758b3116ce7c4aaea9b9d05f8cdd77b385511d4c84173b19",
}

REFUSAL_SPLIT_COUNTS = {
    "harmful_train": 260,
    "harmful_val": 39,
    "harmful_test": 572,
    "harmless_train": 18793,
    "harmless_val": 6264,
    "harmless_test": 6266,
}


def refusal_split_paths(source_root: Path) -> dict[str, Path]:
    """Return the exact frozen refusal split paths under a hydrated checkout."""
    return {name: source_root / relative for name, relative in REFUSAL_SPLIT_FILES.items()}


def refusal_revision_root(cache_root: Path | None = None) -> Path:
    default = Path.home() / ".cache" / "alignmentdelta" / "source_data"
    root = cache_root or Path(os.environ.get("ALIGNMENTDELTA_CACHE", default))
    return root / "refusal_direction" / REFUSAL_REVISION
