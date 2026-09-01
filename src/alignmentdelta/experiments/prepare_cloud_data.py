"""Hydrate and verify immutable Step 4 cloud source data.

GitHub sources are fetched by pinned commit; MMLU is fetched as a pinned
Hugging Face dataset.  Hydration never prints source rows or benchmark text.
"""

from __future__ import annotations

import argparse
import csv
import hashlib
import json
import os
import shutil
import subprocess
import tempfile
from dataclasses import asdict, dataclass
from pathlib import Path
from typing import Any

from alignmentdelta.experiments.source_layout import REFUSAL_SPLIT_COUNTS, REFUSAL_SPLIT_SHA256, refusal_split_paths

REFUSAL_REVISION = "9d852fae1a9121c78b29142de733cb1340770cc3"
XSTEST_REVISION = "d7bb5bd738c1fcbc36edd83d5e7d1b71a3e2d84d"
MMLU_REVISION = "c30699e8356da336a370243923dbaf21066bb9fe"

FROZEN_PAIRS = {
    "mmlu:abstract_algebra:validation:0:71f2e99c0471b412": (
        "mmlu-pair:85393a0849a61791",
        "mmlu:variant:abstract_algebra:validation:0:0f24878e1ae949f9",
        [3, 1, 0, 2],
    ),
    "mmlu:abstract_algebra:validation:10:a3df520d7e394fb2": (
        "mmlu-pair:94329ec32cbd7555",
        "mmlu:variant:abstract_algebra:validation:10:4f681df728c753e9",
        [1, 0, 2, 3],
    ),
    "mmlu:abstract_algebra:validation:1:dc0da27beada68be": (
        "mmlu-pair:03d97cfcc77240a6",
        "mmlu:variant:abstract_algebra:validation:1:8f92937f14a46111",
        [1, 2, 3, 0],
    ),
    "mmlu:formal_logic:validation:0:4ed34a08d34bf2bf": (
        "mmlu-pair:daeeace10ff53d6b",
        "mmlu:variant:formal_logic:validation:0:6b7a4f08df82cfc0",
        [0, 3, 1, 2],
    ),
    "mmlu:formal_logic:validation:10:7ca8c2bc29a09d32": (
        "mmlu-pair:ed1056365f05917a",
        "mmlu:variant:formal_logic:validation:10:97a5f1007582fc11",
        [3, 0, 2, 1],
    ),
    "mmlu:formal_logic:validation:11:6c1cbab2eb785e31": (
        "mmlu-pair:58f21546d4e3e200",
        "mmlu:variant:formal_logic:validation:11:a9cb416d7dd4e17f",
        [2, 3, 0, 1],
    ),
    "mmlu:anatomy:validation:0:0b77500a5a8cd01b": (
        "mmlu-pair:5ff3c846c920fdac",
        "mmlu:variant:anatomy:validation:0:6307f076702f181d",
        [1, 2, 3, 0],
    ),
    "mmlu:anatomy:validation:10:33ff1089cc7b7f51": (
        "mmlu-pair:5e0847e4be5b2fde",
        "mmlu:variant:anatomy:validation:10:ca3749efb32d5f2b",
        [2, 3, 0, 1],
    ),
    "mmlu:anatomy:validation:11:4c75f1cdf17c5e08": (
        "mmlu-pair:0e65712ae0063e55",
        "mmlu:variant:anatomy:validation:11:3abaf65118924ba3",
        [1, 0, 2, 3],
    ),
    "mmlu:econometrics:validation:0:9b94b2a2997d1582": (
        "mmlu-pair:060d1c42d76e0658",
        "mmlu:variant:econometrics:validation:0:27a71315e73662a0",
        [1, 0, 3, 2],
    ),
    "mmlu:econometrics:validation:10:7366fceef7757c18": (
        "mmlu-pair:9d6d5ca64f8cd01c",
        "mmlu:variant:econometrics:validation:10:3c1b66d8dce28391",
        [3, 2, 0, 1],
    ),
    "mmlu:econometrics:validation:11:c446a1c15248330a": (
        "mmlu-pair:bafcf903699a8819",
        "mmlu:variant:econometrics:validation:11:4f1639c5e8af4352",
        [1, 0, 2, 3],
    ),
}


@dataclass(frozen=True)
class SourceSpec:
    name: str
    backend: str
    repository: str
    revision: str


SOURCES = (
    SourceSpec("refusal_direction", "github", "andyrdt/refusal_direction", REFUSAL_REVISION),
    SourceSpec("xstest", "github", "paul-rottger/xstest", XSTEST_REVISION),
    SourceSpec("mmlu", "huggingface_dataset", "cais/mmlu", MMLU_REVISION),
)


def _digest(path: Path) -> dict[str, Any]:
    digest = hashlib.sha256()
    size = 0
    with path.open("rb") as handle:
        for block in iter(lambda: handle.read(1024 * 1024), b""):
            digest.update(block)
            size += len(block)
    return {"bytes": size, "sha256": digest.hexdigest()}


def _canonical_hash(question: str, options: list[str], answer: int) -> str:
    payload = json.dumps(
        {"question": question, "options": options, "answer": answer},
        ensure_ascii=False,
        separators=(",", ":"),
    )
    return hashlib.sha256(payload.encode("utf-8")).hexdigest()


def _atomic_promote(source: Path, destination: Path) -> None:
    destination.parent.mkdir(parents=True, exist_ok=True)
    temporary = destination.parent / f".{destination.name}.staging"
    backup = destination.parent / f".{destination.name}.old"
    if temporary.exists():
        shutil.rmtree(temporary)
    if backup.exists():
        shutil.rmtree(backup)
    shutil.copytree(source, temporary, ignore=shutil.ignore_patterns(".git"))
    if destination.exists():
        destination.replace(backup)
    try:
        temporary.replace(destination)
    except BaseException:
        if backup.exists() and not destination.exists():
            backup.replace(destination)
        raise
    if backup.exists():
        shutil.rmtree(backup)


def _hydrate_github(spec: SourceSpec, destination: Path) -> None:
    with tempfile.TemporaryDirectory(prefix=f"alignmentdelta-{spec.name}-") as work:
        checkout = Path(work) / "checkout"
        url = f"https://github.com/{spec.repository}.git"
        try:
            subprocess.run(
                ("git", "clone", "--no-tags", url, str(checkout)), check=True, capture_output=True, text=True
            )
            subprocess.run(
                ("git", "-C", str(checkout), "checkout", "--detach", spec.revision),
                check=True,
                capture_output=True,
                text=True,
            )
            actual = subprocess.check_output(("git", "-C", str(checkout), "rev-parse", "HEAD"), text=True).strip()
        except (OSError, subprocess.CalledProcessError) as exc:
            raise RuntimeError("SOURCE_HYDRATION_FAILED") from exc
        if actual != spec.revision:
            raise RuntimeError("SOURCE_REVISION_MISMATCH")
        _atomic_promote(checkout, destination)


def _hydrate_dataset(spec: SourceSpec, destination: Path) -> None:
    try:
        from huggingface_hub import snapshot_download

        with tempfile.TemporaryDirectory(prefix="alignmentdelta-mmlu-") as work:
            snapshot_download(
                repo_id=spec.repository,
                repo_type="dataset",
                revision=spec.revision,
                local_dir=Path(work) / "dataset",
            )
            _atomic_promote(Path(work) / "dataset", destination)
    except (OSError, RuntimeError, ValueError, ImportError) as exc:
        if isinstance(exc, RuntimeError) and str(exc).startswith("SOURCE_"):
            raise
        raise RuntimeError("SOURCE_HYDRATION_FAILED") from exc


def _materialized_meta(destination: Path, spec: SourceSpec) -> Path:
    return destination / ".alignmentdelta_source.json"


def _write_metadata(destination: Path, spec: SourceSpec) -> None:
    files = {
        str(path.relative_to(destination)): _digest(path)
        for path in sorted(destination.rglob("*"))
        if path.is_file() and path.name != ".alignmentdelta_source.json"
    }
    _materialized_meta(destination, spec).write_text(
        json.dumps({**asdict(spec), "files": files}, indent=2, sort_keys=True) + "\n", encoding="utf-8"
    )


def _verify_metadata(destination: Path, spec: SourceSpec) -> None:
    path = _materialized_meta(destination, spec)
    if not path.exists():
        raise RuntimeError("HYDRATED_CACHE_REQUIRED")
    metadata = json.loads(path.read_text(encoding="utf-8"))
    if any(metadata.get(key) != value for key, value in asdict(spec).items()):
        raise RuntimeError("SOURCE_REVISION_MISMATCH")
    for relative, expected in metadata.get("files", {}).items():
        actual_path = destination / relative
        if not actual_path.exists() or _digest(actual_path) != expected:
            raise RuntimeError("HYDRATED_CACHE_CORRUPT")


def _load_manifest(root: Path, relative: str) -> dict[str, Any]:
    import tomllib

    with (root / relative).open("rb") as handle:
        return tomllib.load(handle)


def _validate_refusal(destination: Path) -> dict[str, Any]:
    expected = REFUSAL_SPLIT_COUNTS
    files: dict[str, Any] = {}
    for name, count in expected.items():
        path = refusal_split_paths(destination)[name]
        if not path.exists():
            raise RuntimeError("HYDRATED_REFUSAL_SOURCE_MISSING")
        rows = json.loads(path.read_text(encoding="utf-8"))
        if not isinstance(rows, list) or len(rows) != count:
            raise RuntimeError("HYDRATED_REFUSAL_SOURCE_COUNT_MISMATCH")
        if _digest(path)["sha256"] != REFUSAL_SPLIT_SHA256[name]:
            raise RuntimeError("HYDRATED_REFUSAL_SOURCE_HASH_MISMATCH")
        files[str(path.relative_to(destination))] = _digest(path)
    return {"files": files, "counts": expected}


def _validate_xstest(destination: Path, repo_root: Path) -> dict[str, Any]:
    manifest = _load_manifest(repo_root, "configs/manifests/xstest_exploratory_pilot.toml")
    paths = sorted(destination.rglob("xstest_prompts.csv"))
    if len(paths) != 1:
        raise RuntimeError("HYDRATED_XSTEST_SOURCE_MISSING")
    with paths[0].open(encoding="utf-8", newline="") as handle:
        rows = list(csv.DictReader(handle))
    if len(rows) != 450:
        raise RuntimeError("HYDRATED_XSTEST_COUNT_MISMATCH")
    labels = [str(row.get("label", "")).lower() for row in rows]
    if labels.count("safe") != 250 or labels.count("unsafe") != 200:
        raise RuntimeError("HYDRATED_XSTEST_LABEL_COUNT_MISMATCH")
    ids = {str(row.get("id", row.get("ID", ""))) for row in rows}
    frozen = set(manifest["safe"]["ids"]) | set(manifest["unsafe"]["ids"])
    if not frozen <= ids:
        raise RuntimeError("HYDRATED_XSTEST_ITEM_MISSING")
    return {"rows": len(rows), "safe": 250, "unsafe": 200, "file": _digest(paths[0])}


def _iter_mmlu_rows(destination: Path) -> list[dict[str, Any]]:
    try:
        import pandas as pd  # type: ignore[import-untyped]
    except ImportError as exc:
        raise RuntimeError("MMLU_DATASET_READER_REQUIRED") from exc
    rows: list[dict[str, Any]] = []
    for path in sorted(destination.rglob("*.parquet")):
        split = path.name.split("-", 1)[0]
        subject = path.parent.name
        for index, row in pd.read_parquet(path).iterrows():
            options = list(row["choices"])
            answer = int(row["answer"])
            question = str(row["question"])
            if len(options) != 4 or not all(isinstance(x, str) for x in options) or not 0 <= answer < 4:
                raise RuntimeError("MMLU_SOURCE_RECORD_INVALID")
            full_hash = _canonical_hash(question, options, answer)
            rows.append(
                {
                    "stable_id": f"mmlu:{subject}:{split}:{index}:{full_hash[:16]}",
                    "subject": subject,
                    "split": split,
                    "source_index": int(index),
                    "content_hash": full_hash,
                    "answer": answer,
                    "question": question,
                    "options": options,
                }
            )
    return rows


def _materialize_mmlu(destination: Path, repo_root: Path) -> dict[str, Any]:
    cal_manifest = _load_manifest(repo_root, "configs/manifests/mmlu_exploratory_pilot.toml")
    pair_manifest = _load_manifest(repo_root, "configs/manifests/consistency_pairs.toml")
    rows = _iter_mmlu_rows(destination)
    by_id = {row["stable_id"]: row for row in rows}
    calibration = [by_id.get(item_id) for item_id in cal_manifest["ids"]]
    if any(item is None for item in calibration):
        raise RuntimeError("MMLU_PILOT_MATERIALIZATION_MISMATCH")
    calibration_rows = [dict(item) for item in calibration if item is not None]
    pairs: list[dict[str, Any]] = []
    for source_id, pair_id in zip(pair_manifest["source_ids"], pair_manifest["pair_ids"], strict=True):
        source = by_id.get(source_id)
        if source is None:
            raise RuntimeError("CONSISTENCY_MATERIALIZATION_MISMATCH")
        frozen = FROZEN_PAIRS.get(source_id)
        if frozen is None or pair_id != frozen[0]:
            raise RuntimeError("CONSISTENCY_MATERIALIZATION_MISMATCH")
        variant_id, permutation = frozen[1], list(frozen[2])
        variant_options = [source["options"][i] for i in permutation]
        variant_answer = permutation.index(source["answer"])
        variant_hash = _canonical_hash(source["question"], variant_options, variant_answer)
        if variant_hash[:16] != variant_id.rsplit(":", 1)[-1]:
            raise RuntimeError("CONSISTENCY_MATERIALIZATION_MISMATCH")
        pairs.append(
            {
                "pair_id": pair_id,
                "source_id": source_id,
                "variant_id": variant_id,
                "permutation": permutation,
                "source_hash": source["content_hash"],
                "variant_hash": variant_hash,
                "subject": source["subject"],
                "split": source["split"],
                "source_index": source["source_index"],
                "source_answer": source["answer"],
                "variant_answer": variant_answer,
                "question": source["question"],
                "source_options": source["options"],
                "variant_options": variant_options,
            }
        )
    (destination / "calibration_items.json").write_text(
        json.dumps(calibration_rows, indent=2, sort_keys=True) + "\n", encoding="utf-8"
    )
    (destination / "consistency_pairs.json").write_text(
        json.dumps(pairs, indent=2, sort_keys=True) + "\n", encoding="utf-8"
    )
    return {
        "subjects": len({row["subject"] for row in rows}),
        "total": len(rows),
        "calibration": len(calibration_rows),
        "pairs": len(pairs),
    }


def _verify_mmlu_materialized(destination: Path, repo_root: Path) -> dict[str, Any]:
    rows = _iter_mmlu_rows(destination)
    if (
        len({row["subject"] for row in rows}) != 57
        or len(rows) != 15858
        or sum(row["split"] == "dev" for row in rows) != 285
        or sum(row["split"] == "validation" for row in rows) != 1531
        or sum(row["split"] == "test" for row in rows) != 14042
    ):
        raise RuntimeError("MMLU_SOURCE_STRUCTURE_MISMATCH")
    cal_manifest = _load_manifest(repo_root, "configs/manifests/mmlu_exploratory_pilot.toml")
    pair_manifest = _load_manifest(repo_root, "configs/manifests/consistency_pairs.toml")
    cal_path = destination / "calibration_items.json"
    pair_path = destination / "consistency_pairs.json"
    if not cal_path.exists() or not pair_path.exists():
        raise RuntimeError("HYDRATED_CACHE_REQUIRED")
    calibration = json.loads(cal_path.read_text(encoding="utf-8"))
    pairs = json.loads(pair_path.read_text(encoding="utf-8"))
    if [item.get("stable_id") for item in calibration] != cal_manifest["ids"]:
        raise RuntimeError("MMLU_PILOT_MATERIALIZATION_MISMATCH")
    if [item.get("pair_id") for item in pairs] != pair_manifest["pair_ids"]:
        raise RuntimeError("CONSISTENCY_MATERIALIZATION_MISMATCH")
    return {"subjects": 57, "total": len(rows), "calibration": len(calibration), "pairs": len(pairs)}


def hydrate(cache_root: Path, repo_root: Path | None = None, verify_only: bool = False) -> dict[str, Any]:
    repo_root = repo_root or Path(__file__).resolve().parents[3]
    result: dict[str, Any] = {}
    for spec in SOURCES:
        destination = cache_root / spec.name / spec.revision
        reused = False
        try:
            if destination.exists():
                try:
                    _verify_metadata(destination, spec)
                    reused = True
                except RuntimeError:
                    if verify_only:
                        raise
                    shutil.rmtree(destination)
                    if spec.backend == "github":
                        _hydrate_github(spec, destination)
                    elif spec.backend == "huggingface_dataset":
                        _hydrate_dataset(spec, destination)
                    else:
                        raise RuntimeError("SOURCE_BACKEND_UNSUPPORTED") from None
            elif verify_only:
                raise RuntimeError("HYDRATED_CACHE_REQUIRED")
            else:
                if spec.backend == "github":
                    _hydrate_github(spec, destination)
                elif spec.backend == "huggingface_dataset":
                    _hydrate_dataset(spec, destination)
                else:
                    raise RuntimeError("SOURCE_BACKEND_UNSUPPORTED")
                _write_metadata(destination, spec)
            if spec.name == "refusal_direction":
                validation = _validate_refusal(destination)
            elif spec.name == "xstest":
                validation = _validate_xstest(destination, repo_root)
            elif reused:
                validation = _verify_mmlu_materialized(destination, repo_root)
            else:
                validation = _materialize_mmlu(destination, repo_root)
            if not verify_only:
                _write_metadata(destination, spec)
            result[spec.name] = {**asdict(spec), "root": str(destination), **validation}
        except RuntimeError:
            raise
        except (OSError, ValueError, KeyError, TypeError) as exc:
            raise RuntimeError("SOURCE_HYDRATION_FAILED") from exc
    return result


def main(argv: list[str] | None = None) -> int:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument(
        "--cache-root",
        type=Path,
        default=Path(os.environ.get("ALIGNMENTDELTA_CACHE", Path.home() / ".cache" / "alignmentdelta" / "source_data")),
    )
    parser.add_argument("--verify", action="store_true")
    parser.add_argument("--repo-root", type=Path, default=None)
    args = parser.parse_args(argv)
    result = hydrate(args.cache_root, repo_root=args.repo_root, verify_only=args.verify)
    print(
        json.dumps(
            {name: {k: value for k, value in item.items() if k not in {"files"}} for name, item in result.items()},
            sort_keys=True,
        )
    )
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
