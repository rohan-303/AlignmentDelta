from __future__ import annotations

import csv
import json
import shutil
from pathlib import Path

from alignmentdelta.experiments.providers import MMLU_REVISION, XSTEST_REVISION, make_production_provider

# Fixture literals mirror the frozen manifest rows.
# ruff: noqa: E501


def _token(line: str) -> str:
    return line.strip().rstrip(",").strip('"')


def test_strict_hydrated_providers_load_frozen_subsets(tmp_path: Path) -> None:
    repo = tmp_path / "repo"
    manifests = repo / "configs" / "manifests"
    manifests.mkdir(parents=True)
    source_root = Path.cwd() / "configs" / "manifests"
    for name in ("xstest_exploratory_pilot.toml", "mmlu_exploratory_pilot.toml", "consistency_pairs.toml", "mmlu.toml"):
        shutil.copy2(source_root / name, manifests / name)
    cache = tmp_path / "cache" / "xstest" / XSTEST_REVISION
    cache.mkdir(parents=True)
    ids = ["201", "51", "326", "1", "251", "401", "376", "276", "151", "101", "202", "52", "226", "301", "76", "351", "26", "426", "176", "126", "227", "302", "77", "352"]
    with (cache / "xstest_prompts.csv").open("w", newline="", encoding="utf-8") as handle:
        writer = csv.DictWriter(handle, fieldnames=["id", "label", "category", "prompt"])
        writer.writeheader()
        for index, item_id in enumerate(ids):
            writer.writerow({"id": item_id, "label": "safe" if index < 12 else "unsafe", "category": "cat", "prompt": f"item-{item_id}"})
    mmlu_cache = tmp_path / "cache" / "mmlu" / MMLU_REVISION
    mmlu_cache.mkdir(parents=True)
    calibration_ids = [_token(line) for line in (manifests / "mmlu_exploratory_pilot.toml").read_text().splitlines() if line.strip().startswith('"mmlu:')]
    calibration = [{"id": item_id, "subject": item_id.split(":")[1], "split": "dev", "source_index": int(item_id.split(":")[3]), "question": "q", "options": ["a", "b", "c", "d"], "answer": 0} for item_id in calibration_ids]
    (mmlu_cache / "calibration_items.json").write_text(json.dumps(calibration), encoding="utf-8")
    pair_ids = [_token(line) for line in (manifests / "consistency_pairs.toml").read_text().splitlines() if line.strip().startswith('"mmlu-pair:')]
    source_ids = [_token(line) for line in (manifests / "consistency_pairs.toml").read_text().splitlines() if line.strip().startswith('"mmlu:')]
    pairs = [{"pair_id": pair_id, "source_id": source_id, "permutation": [1, 0, 2, 3], "remapped_answer": 1, "question": "q", "source_options": ["a", "b", "c", "d"], "variant_options": ["b", "a", "c", "d"]} for pair_id, source_id in zip(pair_ids, source_ids, strict=True)]
    (mmlu_cache / "consistency_pairs.json").write_text(json.dumps(pairs), encoding="utf-8")
    provider = make_production_provider(tmp_path / "cache", repo)
    assert provider({"task": "xstest", "item_id": "xstest:00"})["source_revision"] == XSTEST_REVISION
    assert provider({"task": "mmlu", "item_id": "mmlu:00"})["split"] == "dev"
    assert provider({"task": "consistency", "item_id": "pair:00"})["permutation"] == [1, 0, 2, 3]
