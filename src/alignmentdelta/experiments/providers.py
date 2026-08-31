"""Strict providers for pinned, externally hydrated Step 4 source caches.

This module never downloads data and never fabricates an item.  Cloud setup must
hydrate the pinned cache first; production execution then reads only that cache.
"""
# The cache records intentionally keep source metadata together for auditability.
# ruff: noqa: E501
from __future__ import annotations

import csv
import hashlib
import json
import tomllib
from collections.abc import Callable
from pathlib import Path
from typing import Any, cast

XSTEST_REVISION = "d7bb5bd738c1fcbc36edd83d5e7d1b71a3e2d84d"
MMLU_REVISION = "c30699e8356da336a370243923dbaf21066bb9fe"


def _manifest(root: Path, relative: str) -> dict[str, Any]:
    with (root / relative).open("rb") as handle:
        return tomllib.load(handle)


def _hash_text(value: str) -> str:
    return hashlib.sha256(value.encode("utf-8")).hexdigest()


def _cache_dir(cache_root: Path, name: str, revision: str) -> Path:
    path = cache_root / name / revision
    if not path.is_dir():
        raise RuntimeError(f"HYDRATED_CACHE_REQUIRED: {path}")
    return path


def _json_file(root: Path, name: str) -> Any:
    paths = sorted(root.rglob(name))
    if len(paths) != 1:
        raise RuntimeError(f"HYDRATED_CACHE_FILE_AMBIGUOUS: {name}")
    return json.loads(paths[0].read_text(encoding="utf-8"))


class XSTestProvider:
    task = "xstest"

    def __init__(self, cache_root: Path, repo_root: Path) -> None:
        self.manifest = _manifest(repo_root, "configs/manifests/xstest_exploratory_pilot.toml")
        if self.manifest.get("revision") != XSTEST_REVISION:
            raise RuntimeError("PROTOCOL_MANIFEST_MISMATCH")
        expected = [*self.manifest["safe"]["ids"], *self.manifest["unsafe"]["ids"]]
        cache = _cache_dir(cache_root, "xstest", XSTEST_REVISION)
        csv_paths = sorted(cache.rglob(str(self.manifest["file"])))
        if len(csv_paths) != 1:
            raise RuntimeError("HYDRATED_CACHE_FILE_AMBIGUOUS: xstest_prompts.csv")
        with csv_paths[0].open(encoding="utf-8", newline="") as handle:
            rows = list(csv.DictReader(handle))
        by_id = {str(row.get("id", row.get("ID", ""))): row for row in rows}
        if any(item_id not in by_id for item_id in expected):
            raise RuntimeError("HYDRATED_XSTEST_ITEM_MISSING")
        self.items = []
        for item_id in expected:
            row = by_id[item_id]
            text = row.get("prompt") or row.get("text") or row.get("instruction")
            label = row.get("label") or row.get("category")
            expected_label = "safe" if item_id in self.manifest["safe"]["ids"] else "unsafe"
            if not text or not label or str(row.get("label", "")).lower() != expected_label:
                raise RuntimeError("HYDRATED_XSTEST_METADATA_MISMATCH")
            self.items.append(
                {
                    "id": item_id,
                    "prompt": text,
                    "label": label,
                    "category": row.get("category", label),
                    "source_revision": XSTEST_REVISION,
                    "text_hash": _hash_text(text),
                }
            )

    def __call__(self, row: dict[str, Any]) -> dict[str, Any]:
        index = int(str(row["item_id"]).rsplit(":", 1)[-1])
        if not 0 <= index < len(self.items):
            raise RuntimeError("HYDRATED_XSTEST_ITEM_MISSING")
        return dict(self.items[index])


class MMLUProvider:
    def __init__(self, cache_root: Path, repo_root: Path) -> None:
        self.manifest = _manifest(repo_root, "configs/manifests/mmlu_exploratory_pilot.toml")
        source = _manifest(repo_root, "configs/manifests/mmlu.toml")
        if source.get("revision") != MMLU_REVISION:
            raise RuntimeError("PROTOCOL_MANIFEST_MISMATCH")
        cache = _cache_dir(cache_root, "mmlu", MMLU_REVISION)
        data = _json_file(cache, str(self.manifest["cache_file"]))
        rows = data if isinstance(data, list) else data.get("items", data.get("records", []))
        by_id = {str(item.get("id")): item for item in rows}
        self.items = []
        for stable_id in self.manifest["ids"]:
            item = by_id.get(stable_id)
            if not isinstance(item, dict):
                raise RuntimeError("HYDRATED_MMLU_ITEM_MISSING")
            options = item.get("options")
            answer = item.get("answer", item.get("gold_answer"))
            if not item.get("subject") or item.get("split") != "dev" or not isinstance(options, list) or len(options) != 4 or answer not in range(4):
                raise RuntimeError("HYDRATED_MMLU_ITEM_INVALID")
            question = str(item.get("question", ""))
            self.items.append({"id": stable_id, "subject": item["subject"], "split": "dev", "source_index": item.get("source_index"), "question": question, "options": options, "gold_answer": answer, "content_hash": item.get("content_hash", _hash_text(question + json.dumps(options, sort_keys=True))), "source_revision": MMLU_REVISION})

    def __call__(self, row: dict[str, Any]) -> dict[str, Any]:
        index = int(str(row["item_id"]).rsplit(":", 1)[-1])
        if not 0 <= index < len(self.items):
            raise RuntimeError("HYDRATED_MMLU_ITEM_MISSING")
        return dict(self.items[index])


class ConsistencyProvider:
    def __init__(self, cache_root: Path, repo_root: Path) -> None:
        self.manifest = _manifest(repo_root, "configs/manifests/consistency_pairs.toml")
        mmlu = MMLUProvider(cache_root, repo_root)
        cache = _cache_dir(cache_root, "mmlu", MMLU_REVISION)
        data = _json_file(cache, str(self.manifest["cache_file"]))
        rows = data if isinstance(data, list) else data.get("pairs", data.get("records", []))
        by_id = {str(item.get("pair_id", item.get("id"))): item for item in rows}
        self.items = []
        for pair_id, source_id in zip(self.manifest["pair_ids"], self.manifest["source_ids"], strict=True):
            pair = by_id.get(pair_id)
            if not isinstance(pair, dict) or pair.get("source_id") != source_id:
                raise RuntimeError("HYDRATED_CONSISTENCY_PAIR_MISSING")
            if not isinstance(pair.get("permutation"), list) or sorted(pair["permutation"]) != [0, 1, 2, 3] or pair.get("remapped_answer") not in range(4):
                raise RuntimeError("HYDRATED_CONSISTENCY_PAIR_INVALID")
            self.items.append({**pair, "pair_id": pair_id, "source_revision": MMLU_REVISION})
        if len(mmlu.items) != 12:
            raise RuntimeError("PROTOCOL_MANIFEST_MISMATCH")

    def __call__(self, row: dict[str, Any]) -> dict[str, Any]:
        index = int(str(row["item_id"]).rsplit(":", 1)[-1])
        if not 0 <= index < len(self.items):
            raise RuntimeError("HYDRATED_CONSISTENCY_PAIR_MISSING")
        return dict(self.items[index])


def make_production_provider(cache_root: Path, repo_root: Path) -> Callable[[dict[str, Any]], dict[str, Any]]:
    provider_type = Callable[[dict[str, Any]], dict[str, Any]]
    providers: dict[str, provider_type] = {
        "xstest": cast(provider_type, XSTestProvider(cache_root, repo_root)),
        "mmlu": cast(provider_type, MMLUProvider(cache_root, repo_root)),
        "consistency": cast(provider_type, ConsistencyProvider(cache_root, repo_root)),
    }

    def provide(row: dict[str, Any]) -> dict[str, Any]:
        try:
            return providers[str(row["task"])](row)
        except KeyError as exc:
            raise RuntimeError("UNKNOWN_PRODUCTION_TASK") from exc

    return provide
