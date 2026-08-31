from __future__ import annotations

import math
import os
import subprocess
import sys

import pytest

from alignmentdelta.experiments.exploratory_pilot import (
    ALPHAS,
    RANDOM_CONTROL_SEEDS,
    brier_score,
    expand_conditions,
    nll,
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
