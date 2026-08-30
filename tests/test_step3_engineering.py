
import pytest
import torch
from torch import nn

from alignmentdelta.engineering.artifacts import direction_artifact, write_artifact
from alignmentdelta.engineering.capture import OnlineMeanDifference, ResidualCapture
from alignmentdelta.engineering.controls import orthogonal_control
from alignmentdelta.engineering.direction import engineering_subset, stable_id
from alignmentdelta.engineering.model_registry import QWEN25_1P5B, get_model_spec
from alignmentdelta.engineering.projection import signed_projection, transform_block_output
from alignmentdelta.engineering.qwen_adapter import Qwen2Adapter
from alignmentdelta.engineering.refusal import refusal_score
from alignmentdelta.engineering.site_selection import SiteDiagnostic, candidate_layers, select_site


def test_registry_is_pinned_engineering_qwen() -> None:
    assert get_model_spec() == QWEN25_1P5B
    assert QWEN25_1P5B.trust_remote_code is False
    assert QWEN25_1P5B.expected_layers == 28


def test_qwen_adapter_resolves_actual_wrapper_path() -> None:
    class Decoder(nn.Module):
        def __init__(self) -> None:
            super().__init__()
            self.layers = nn.ModuleList([nn.Linear(4, 4) for _ in range(2)])
            self.hidden_size = 4

    class FakeQwen(nn.Module):
        def __init__(self) -> None:
            super().__init__()
            self.model = Decoder()

    model = FakeQwen()
    model.__class__.__name__ = "Qwen2ForCausalLM"
    adapter = Qwen2Adapter(model)
    assert adapter.block_count() == 2
    assert adapter.hidden_size == 4
    assert adapter.architecture.block_path == "model.model.layers"


def test_final_nonpadding_positions_for_left_and_right_padding() -> None:
    left = torch.tensor([[0, 0, 1, 1], [0, 1, 1, 1]])
    right = torch.tensor([[1, 1, 0, 0], [1, 1, 1, 0]])
    assert torch.equal(Qwen2Adapter.final_nonpadding_positions(left), torch.tensor([3, 3]))
    assert torch.equal(Qwen2Adapter.final_nonpadding_positions(right), torch.tensor([1, 2]))


def test_adapter_preserves_tuple_output() -> None:
    class Decoder(nn.Module):
        def __init__(self) -> None:
            super().__init__()
            self.layers = nn.ModuleList([nn.Linear(4, 4)])
            self.hidden_size = 4

    class FakeQwen(nn.Module):
        def __init__(self) -> None:
            super().__init__()
            self.model = Decoder()

    model = FakeQwen()
    model.__class__.__name__ = "Qwen2ForCausalLM"
    adapter = Qwen2Adapter(model)
    hidden = torch.zeros(1, 2, 4)
    replacement = torch.ones_like(hidden)
    output = adapter.replace_hidden((hidden, "cache"), replacement)
    assert isinstance(output, tuple)
    assert torch.equal(output[0], replacement)
    assert output[1] == "cache"


def test_residual_capture_installs_and_removes_hook() -> None:
    layer = nn.Linear(3, 3)
    capture = ResidualCapture(layer)
    capture.install()
    layer(torch.ones(1, 2, 3))
    result = capture.result()
    capture.remove()
    assert result.value.shape == (1, 3)
    assert result.calls == 1
    assert result.output_kind == "Tensor"


def test_online_difference_mean_and_normalization() -> None:
    acc = OnlineMeanDifference(2)
    acc.add(torch.tensor([[2.0, 0.0]]), harmful=True)
    acc.add(torch.tensor([[0.0, 1.0]]), harmful=False)
    direction, norm = acc.direction()
    assert norm > 0
    assert torch.allclose(torch.linalg.vector_norm(direction), torch.tensor(1.0, dtype=torch.float64))


def test_near_zero_direction_rejected() -> None:
    acc = OnlineMeanDifference(2)
    acc.add(torch.zeros(1, 2), harmful=True)
    acc.add(torch.zeros(1, 2), harmful=False)
    with pytest.raises(ValueError, match="below"):
        acc.direction()


def test_refusal_score_matches_frozen_equation() -> None:
    logits = torch.zeros(1, 1, 2122, dtype=torch.float32)
    logits[0, 0, 40] = 10.0
    logits[0, 0, 2121] = 10.0
    score = refusal_score(logits)
    assert score.dtype == torch.float64
    assert float(score.item()) > 0


def test_controls_are_deterministic_and_orthogonal() -> None:
    direction = torch.tensor([1.0, 0.0, 0.0], dtype=torch.float64)
    first, diagnostic = orthogonal_control(direction, 20260830)
    second, _ = orthogonal_control(direction, 20260830)
    assert torch.equal(first, second)
    assert diagnostic.absolute_dot <= 1e-6
    assert abs(float(torch.linalg.vector_norm(first)) - 1.0) <= 1e-12


def test_projection_alpha_invariants_and_structured_output() -> None:
    direction = torch.tensor([1.0, 0.0], dtype=torch.float32)
    hidden = torch.tensor([[2.0, 3.0]])
    assert torch.equal(signed_projection(hidden, direction, 0.0), hidden)
    assert torch.allclose(signed_projection(hidden, direction, 1.0), torch.tensor([[0.0, 3.0]]))
    assert torch.allclose(signed_projection(hidden, direction, 0.5), torch.tensor([[1.0, 3.0]]))
    assert torch.allclose(signed_projection(hidden, direction, -0.5), torch.tensor([[3.0, 3.0]]))
    output = transform_block_output((hidden, "aux"), direction, 1.0)
    assert output[1] == "aux"
    assert torch.allclose(output[0], torch.tensor([[0.0, 3.0]]))


def test_subset_is_deterministic_and_sanitized() -> None:
    first = engineering_subset()
    second = engineering_subset()
    first_ids = [[stable_id(x) for x in first[key]] for key in first]
    second_ids = [[stable_id(x) for x in second[key]] for key in second]
    assert first_ids == second_ids
    assert len(first["direction_train"]) == 16
    assert len(first["direction_validation"]) == 8


def test_site_layer_reduction_and_selection() -> None:
    assert candidate_layers(28) == [0, 14, 21]
    chosen = select_site([SiteDiagnostic(0, 1.0, 0.01, 0.1, True), SiteDiagnostic(14, 2.0, 0.01, 0.1, True)])
    assert chosen.layer == 14


def test_direction_artifact_is_sanitized_and_deterministic(tmp_path) -> None:
    direction = torch.tensor([1.0, 0.0], dtype=torch.float64)
    kwargs = {
        "model_id": "Qwen/Qwen2.5-1.5B-Instruct",
        "revision": "revision",
        "tokenizer_revision": "revision",
        "template_hash": "template",
        "source_manifest_hash": "source",
        "subset_hash": "subset",
        "layer": 1,
        "position_rule": "final non-padding token",
        "raw_norm": 2.0,
        "direction": direction,
        "git_commit": "commit",
        "environment_reference": "environment",
    }
    first = direction_artifact(**kwargs)
    second = direction_artifact(**kwargs)
    assert first == second
    assert first["phase"] == "engineering"
    assert first["scientific_execution"] is False
    assert first["selected_site"] == "engineering_only"
    write_artifact(tmp_path / "direction.json", first)
    assert (tmp_path / "direction.json").exists()
