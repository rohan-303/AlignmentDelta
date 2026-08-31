from __future__ import annotations

import pytest
import torch
from torch import nn

from alignmentdelta.experiments.cloud_adapter import (
    EXPECTED_MODEL_REVISION,
    QwenScientificAdapter,
    verify_runtime_identity,
)


class FakeBlock(nn.Module):
    def forward(self, x: torch.Tensor) -> torch.Tensor:
        return x


class FakeDecoder(nn.Module):
    def __init__(self) -> None:
        super().__init__()
        self.layers = nn.ModuleList([FakeBlock() for _ in range(36)])
        self.hidden_size = 2048


class FakeModel(nn.Module):
    def __init__(self) -> None:
        super().__init__()
        self.model = FakeDecoder()
        self.weight = nn.Parameter(torch.ones(1))

    def forward(self, x: torch.Tensor) -> torch.Tensor:
        return self.model.layers[27](x)


def test_runtime_identity_rejects_wrong_revision_and_architecture() -> None:
    with pytest.raises(RuntimeError, match="MODEL_RUNTIME_IDENTITY_MISMATCH"):
        verify_runtime_identity("OtherModel", EXPECTED_MODEL_REVISION, 2048, 36)
    with pytest.raises(RuntimeError, match="MODEL_RUNTIME_IDENTITY_MISMATCH"):
        verify_runtime_identity("Qwen2ForCausalLM", "main", 2048, 36)
    verify_runtime_identity("Qwen2ForCausalLM", EXPECTED_MODEL_REVISION, 2048, 36)


def test_intervention_hook_is_removed_and_baseline_has_no_hook() -> None:
    model = FakeModel()
    adapter = QwenScientificAdapter(model, layer=27)
    baseline = torch.ones(1, 2, 2048)
    adapter.forward(baseline)
    assert adapter.hook_count == 0
    direction = torch.zeros(2048)
    direction[0] = 1
    adapter.forward(baseline, direction=direction, alpha=1.0)
    assert adapter.hook_count == 0
    assert model.model.layers[27]._forward_hooks == {}


def test_adapter_rejects_wrong_hidden_dimension() -> None:
    with pytest.raises(RuntimeError, match="MODEL_RUNTIME_IDENTITY_MISMATCH"):
        QwenScientificAdapter(FakeModel(), layer=27, hidden_size=7)
