"""Hydrate immutable cloud data sources outside Git.

Network access occurs only when this command is explicitly invoked in a cloud
session. It prints identifiers and validation summaries, never dataset rows.
"""

from __future__ import annotations

import argparse
import hashlib
import json
import os
from pathlib import Path
from typing import Any

SOURCES = {
    "refusal_direction": ("andyrdt/refusal_direction", "9d852fae1a9121c78b29142de733cb1340770cc3"),
    "mmlu": ("cais/mmlu", "c30699e8356da336a370243923dbaf21066bb9fe"),
    "xstest": ("paul-rottger/xstest", "d7bb5bd738c1fcbc36edd83d5e7d1b71a3e2d84d"),
}


def _digest(path: Path) -> dict[str, Any]:
    digest = hashlib.sha256()
    size = 0
    with path.open("rb") as handle:
        for block in iter(lambda: handle.read(1024 * 1024), b""):
            digest.update(block)
            size += len(block)
    return {"bytes": size, "sha256": digest.hexdigest()}


def hydrate(cache_root: Path, verify_only: bool = False) -> dict[str, Any]:
    try:
        from huggingface_hub import snapshot_download
    except ImportError as exc:
        raise RuntimeError("cloud hydration requires the optional ml environment") from exc
    result: dict[str, Any] = {}
    for name, (repo_id, revision) in SOURCES.items():
        destination = cache_root / name / revision
        if not verify_only:
            snapshot_download(repo_id=repo_id, revision=revision, local_dir=destination)
        if not destination.exists():
            raise RuntimeError(f"missing hydrated source: {name}")
        files = {
            str(path.relative_to(destination)): _digest(path)
            for path in sorted(destination.rglob("*"))
            if path.is_file()
        }
        result[name] = {
            "repo_id": repo_id,
            "revision": revision,
            "root": str(destination),
            "file_count": len(files),
            "files": files,
        }
    return result


def main(argv: list[str] | None = None) -> int:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument(
        "--cache-root",
        type=Path,
        default=Path(os.environ.get("ALIGNMENTDELTA_CACHE", Path.home() / ".cache" / "alignmentdelta" / "source_data")),
    )
    parser.add_argument("--verify", action="store_true")
    args = parser.parse_args(argv)
    result = hydrate(args.cache_root, args.verify)
    print(
        json.dumps(
            {name: {k: value for k, value in item.items() if k != "files"} for name, item in result.items()},
            sort_keys=True,
        )
    )
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
