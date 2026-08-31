from __future__ import annotations

import math
import os
import subprocess
import sys

import pytest

from alignmentdelta.experiments.annotation import (
    annotation_export,
    blind_response,
    unblind_labels,
)
from alignmentdelta.experiments.exploratory_pilot import (
    ALPHAS,
    RANDOM_CONTROL_SEEDS,
    brier_score,
    expand_conditions,
    nll,
    operation_counts,
    permute_options,
    remap_answer,
    stable_probabilities,
)


def test_option_scoring_normalizes_and_metrics_are_stable() -> None:
    probabilities = stable_probabilities([0.0, -1.0, -2.0, -3.0])
    assert math.isclose(sum(probabilities), 1.0)
    assert brier_score(probabilities, 0) >= 0
    assert nll(probabilities, 0) >= 0


def test_option_scoring_rejects_invalid_probabilities() -> None:
    with pytest.raises(ValueError):
        brier_score([0.5, 0.6], 0)
    with pytest.raises(ValueError):
        nll([0.0, 1.0], 0)


def test_consistency_permutation_and_answer_remapping() -> None:
    permutation = [2, 0, 3, 1]
    assert permute_options(["A", "B", "C", "D"], permutation) == ["C", "A", "D", "B"]
    assert remap_answer(2, permutation) == 0
    with pytest.raises(ValueError):
        permute_options(["A", "B"], [0, 0])


def test_baseline_is_unique_and_alpha_zero_is_not_control_replicated() -> None:
    conditions = expand_conditions({"xstest_safety": ["1"]})
    baselines = [c for c in conditions if c.alpha == 0.0]
    assert len(baselines) == 1
    assert baselines[0].intervention_type == "baseline"
    assert len([c for c in conditions if c.intervention_type == "refusal_direction"]) == len(ALPHAS) - 1
    assert len([c for c in conditions if c.intervention_type == "random_control"]) == (
        (len(ALPHAS) - 1) * len(RANDOM_CONTROL_SEEDS)
    )


def test_random_controls_are_not_checkpoints() -> None:
    conditions = expand_conditions({"xstest_safety": ["1"]})
    assert {c.checkpoint for c in conditions} == {"Qwen/Qwen2.5-3B-Instruct"}
    assert {c.control_seed for c in conditions if c.intervention_type == "random_control"} == set(RANDOM_CONTROL_SEEDS)


def test_dry_run_module_does_not_import_model_frameworks() -> None:
    code = "import sys\nimport alignmentdelta.experiments.exploratory_pilot\n"
    code += "print('torch' in sys.modules or 'transformers' in sys.modules)"
    result = subprocess.run(
        [sys.executable, "-c", code],
        check=True,
        capture_output=True,
        text=True,
        env={**os.environ, "PYTHONPATH": "src"},
    )
    assert result.stdout.strip() == "False"


def test_operation_counts_distinguish_generation_and_option_scoring() -> None:
    counts = operation_counts(24, 12, 12)
    assert counts == {
        "representations": 60,
        "logical_condition_states": 1860,
        "unique_baseline_states": 60,
        "xstest_generations": 744,
        "mmlu_option_scoring_operations": 1488,
        "consistency_original_scoring_operations": 1488,
        "consistency_transformed_scoring_operations": 1488,
        "total_forward_operation_estimate": 5208,
    }


def test_materialized_mmlu_subsets_are_frozen_and_disjoint() -> None:
    import json
    from pathlib import Path

    cache = (
        Path.home() / ".cache" / "alignmentdelta" / "source_data" / "mmlu" / "c30699e8356da336a370243923dbaf21066bb9fe"
    )
    calibration = json.loads((cache / "calibration_items.json").read_text(encoding="utf-8"))
    pairs = json.loads((cache / "consistency_pairs.json").read_text(encoding="utf-8"))
    assert len(calibration) == 12
    assert len(pairs) == 12
    assert not {item["stable_id"] for item in calibration} & {pair["source_id"] for pair in pairs}
    assert {item["broad_category"] for item in calibration} == {"STEM", "humanities", "social_sciences", "other"}
    assert all(len(pair["source_options"]) == len(pair["variant_options"]) == 4 for pair in pairs)


def test_blinding_export_hides_condition_metadata_and_unblinds_deterministically() -> None:
    response, mapping = blind_response("alpha-1.25-refusal", "xstest:1", "safe response")
    exported = annotation_export(response)
    assert not {"condition_id", "alpha", "intervention_type", "control_seed"} & set(exported)
    exported["annotation_label"] = "full refusal"
    exported["annotation_status"] = "final"
    first = unblind_labels([exported], [mapping])
    second = unblind_labels([exported], [mapping])
    assert first == second
    assert first[0]["condition_id"] == "alpha-1.25-refusal"
