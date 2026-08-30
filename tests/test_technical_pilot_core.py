import math

import pytest
import torch

from alignmentdelta.engineering.technical_pilot_core import (
    TechnicalPilotError,
    achieved_dose,
    candidate_layers_full,
    deterministic_sample,
    pairwise_cosines,
    rank_site_rows,
    technical_alpha_valid,
    technical_manifest,
)


def _records(n: int, prefix: str) -> list[dict[str, str]]:
    return [{"id": f"{prefix}-{i:03d}", "instruction": f"opaque-{i}"} for i in range(n)]


def test_deterministic_sample_balances_and_orders_by_stable_id() -> None:
    harmful = list(reversed(_records(5, "h")))
    harmless = list(reversed(_records(7, "s")))
    selected = deterministic_sample(harmful, harmless, train_counts=(3, 3), validation_counts=(1, 1))
    assert [r["id"] for r in selected["direction_train_harmful"]] == ["h-000", "h-001", "h-002"]
    assert [r["id"] for r in selected["direction_train_harmless"]] == ["s-000", "s-001", "s-002"]
    assert selected["rng_seed"] is None


def test_deterministic_sample_rejects_insufficient_class() -> None:
    with pytest.raises(TechnicalPilotError, match="insufficient"):
        deterministic_sample(_records(1, "h"), _records(3, "s"), train_counts=(2, 2), validation_counts=(1, 1))


def test_full_candidate_layers_are_computed_not_hard_coded() -> None:
    assert candidate_layers_full(28) == list(range(22))
    assert candidate_layers_full(10) == list(range(8))


def test_pairwise_cosines_and_norm_variation_are_finite() -> None:
    vectors = [torch.tensor([1.0, 0.0]), torch.tensor([0.0, 1.0]), torch.tensor([1.0, 1.0])]
    result = pairwise_cosines(vectors)
    assert result["count"] == 3
    assert math.isclose(result["minimum"], 0.0, abs_tol=1e-12)
    assert result["norm_coefficient_of_variation"] > 0


def test_site_ranking_uses_validity_then_deterministic_ties() -> None:
    rows = [
        {"layer": 2, "score": 4.0, "accepted": True},
        {"layer": 1, "score": 4.0, "accepted": True},
        {"layer": 0, "score": 9.0, "accepted": False},
    ]
    ranked = rank_site_rows(rows)
    assert ranked[0]["layer"] == 1
    assert ranked[0]["rank"] == 1
    assert ranked[1]["layer"] == 2


def test_technical_alpha_validity_rejects_nonfinite_only() -> None:
    assert technical_alpha_valid(torch.tensor([1.0, 2.0]), torch.tensor([3.0]))
    assert not technical_alpha_valid(torch.tensor([float("nan")]), torch.tensor([1.0]))
    assert not technical_alpha_valid(torch.tensor([1.0]), torch.tensor([float("inf")]))


def test_achieved_dose_is_defined_against_baseline_rms() -> None:
    baseline = torch.tensor([[3.0, 4.0]], dtype=torch.float64)
    changed = torch.tensor([[0.0, 4.0]], dtype=torch.float64)
    metrics = achieved_dose(baseline, changed)
    assert metrics["perturbation_rms"] == pytest.approx((9 / 2) ** 0.5)
    assert metrics["baseline_rms"] == pytest.approx((25 / 2) ** 0.5)
    assert metrics["perturbation_to_baseline_rms"] == pytest.approx(0.6)


def test_technical_manifest_has_boundary_and_no_prompt_field() -> None:
    manifest = technical_manifest(run_id="x", git_commit="abc", source_ids=["rd:1"])
    assert manifest["phase"] == "technical_pilot"
    assert manifest["scientific_execution"] is False
    assert "instruction" not in str(manifest)


def test_step30_artifacts_are_not_reused_as_pilot_results() -> None:
    manifest = technical_manifest(run_id="x", git_commit="abc", source_ids=[])
    assert manifest["step_3_0_history_preserved"] is True
    assert manifest["artifact_root"] == "artifacts/pilot/step_3_1"
