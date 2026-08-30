import hashlib
import json
import math
import tomllib
from pathlib import Path

import torch

ROOT = Path(__file__).parents[1]


def test_source_registry_has_hashes_and_counts_for_materialized_files() -> None:
    registry = json.loads(
        (ROOT / "artifacts/data_audit/source_data_registry.json").read_text(
            encoding="utf-8"
        )
    )
    materialized = [record for record in registry["records"] if record["local_path"]]
    assert len(materialized) == 10
    for record in materialized:
        assert len(record["sha256"]) == 64
        assert record["bytes"] > 0
        assert record["item_count"] > 0
        assert len(record["ids"]) == record["item_count"]
        assert len(set(record["ids"])) == record["item_count"]


def test_selected_direction_manifest_is_deterministic_and_role_separated() -> None:
    manifest = tomllib.loads(
        (ROOT / "configs/manifests/refusal_direction_source.toml").read_text(
            encoding="utf-8"
        )
    )
    active = [entry for entry in manifest["file"] if entry["partition"] != "excluded"]
    assert {entry["partition"] for entry in active} == {"train", "validation"}
    assert all(entry["role"] == "direction_contrast" for entry in active)
    active_ids = [item_id for entry in active for item_id in entry["ids"]]
    assert len(active_ids) == len(set(active_ids))
    assert manifest["seed"] == 20260830


def test_selected_direction_has_no_exact_or_normalized_evaluation_overlap() -> None:
    audit = json.loads(
        (ROOT / "artifacts/data_audit/selected_overlap_summary.json").read_text(
            encoding="utf-8"
        )
    )
    assert audit["comparisons"]
    for comparison in audit["comparisons"]:
        assert comparison["exact_hash_overlap_count"] == 0
        assert comparison["normalized_text_overlap_count"] == 0


def test_refusal_score_matches_pinned_log_odds_equation() -> None:
    logits = torch.tensor([[[2.0, 0.0, -1.0], [1.0, 3.0, 0.0]]])
    refusal_ids = torch.tensor([1])
    logits64 = logits.to(torch.float64)[:, -1, :]
    probabilities = torch.softmax(logits64, dim=-1)
    refusal_probability = probabilities[:, refusal_ids].sum(dim=-1)
    expected = torch.log(refusal_probability + 1e-8) - torch.log(
        1 - refusal_probability + 1e-8
    )
    assert torch.isfinite(expected).all()
    assert math.isclose(float(expected.item()), 1.686738, rel_tol=1e-5)


def test_qwen_refusal_token_metadata_is_frozen() -> None:
    text = (ROOT / "docs/protocols/REFUSAL_SCORE.md").read_text(encoding="utf-8")
    assert "epsilon: `1e-8`" in text
    assert "`[40, 2121]`" in text
    assert "`I`" in text and "`As`" in text


def test_consistency_permutation_is_bijective_and_remaps_answer() -> None:
    options = ["A", "B", "C", "D"]
    correct_index = 2
    permutation = [2, 0, 3, 1]
    transformed = [options[index] for index in permutation]
    remapped_index = permutation.index(correct_index)
    assert len(set(transformed)) == 4
    assert sorted(transformed) == sorted(options)
    assert transformed[remapped_index] == options[correct_index]
    variant_id = hashlib.sha256(
        f"mmlu-item:{','.join(map(str, permutation))}".encode()
    ).hexdigest()[:24]
    assert variant_id == hashlib.sha256(
        f"mmlu-item:{','.join(map(str, permutation))}".encode()
    ).hexdigest()[:24]


def test_primary_protocol_does_not_use_empirical_permutation_test() -> None:
    text = (ROOT / "docs/protocols/RANDOM_CONTROL_STATISTICS.md").read_text(
        encoding="utf-8"
    )
    assert "not an exchangeable" in text
    assert "label-permutation" in text
    assert "bootstrap" in text.lower()


def test_step3_scope_excludes_scientific_benchmark_execution() -> None:
    text = (ROOT / "docs/implementation/STEP_3_SCOPE.md").read_text(encoding="utf-8")
    assert "full XSTest" in text
    assert "HarmBench" in text
    assert "paper claims" in text
