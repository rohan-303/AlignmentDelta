"""Runtime-verified Qwen2 adapter."""

from __future__ import annotations

from dataclasses import dataclass
from typing import Any, cast

import torch
from torch import nn


@dataclass(frozen=True, slots=True)
class RuntimeArchitecture:
    top_level_class: str
    decoder_class: str
    block_path: str
    block_class: str
    block_count: int
    hidden_size: int
    output_kind: str
    hidden_tensor_position: int | None
    normalization_modules: tuple[str, ...]


class Qwen2Adapter:
    """Access the actual Qwen2 wrapper path without architecture hacks."""

    block_path = "model.model.layers"

    def __init__(self, model: nn.Module) -> None:
        self.model = model
        if type(model).__name__ != "Qwen2ForCausalLM":
            raise TypeError(f"expected Qwen2ForCausalLM, got {type(model).__name__}")
        decoder = getattr(model, "model", None)
        blocks = getattr(decoder, "layers", None)
        if decoder is None or blocks is None:
            raise AttributeError("runtime Qwen2 model.model.layers path is unavailable")
        if not isinstance(blocks, nn.ModuleList):
            raise TypeError("Qwen2 decoder layers must be a ModuleList")
        self.decoder: nn.Module = decoder
        self.blocks = blocks
        hidden_size = getattr(decoder, "hidden_size", None)
        if hidden_size is None:
            config = getattr(decoder, "config", None)
            hidden_size = getattr(config, "hidden_size", None)
        if hidden_size is None:
            raise AttributeError("Qwen2 runtime has no hidden-size metadata")
        self.hidden_size = int(hidden_size)
        self.architecture = self._introspect()

    def _introspect(self) -> RuntimeArchitecture:
        block = self.blocks[0]
        norms = tuple(
            name for name in ("input_layernorm", "post_attention_layernorm", "ln_1", "ln_2") if hasattr(block, name)
        )
        with torch.no_grad():
            params = list(block.parameters())
        del params
        return RuntimeArchitecture(
            top_level_class=type(self.model).__name__,
            decoder_class=type(self.decoder).__name__,
            block_path=self.block_path,
            block_class=type(block).__name__,
            block_count=len(self.blocks),
            hidden_size=self.hidden_size,
            output_kind="runtime_probe_required",
            hidden_tensor_position=0,
            normalization_modules=norms,
        )

    def block(self, index: int) -> nn.Module:
        if not 0 <= index < len(self.blocks):
            raise IndexError(index)
        return self.blocks[index]

    def block_count(self) -> int:
        return len(self.blocks)

    def hidden_from_output(self, output: Any) -> torch.Tensor:
        if isinstance(output, torch.Tensor):
            hidden = output
        elif isinstance(output, (tuple, list)) and output and isinstance(output[0], torch.Tensor):
            hidden = output[0]
        else:
            raise TypeError(f"unsupported Qwen2 block output: {type(output).__name__}")
        if hidden.ndim != 3 or hidden.shape[-1] != self.hidden_size:
            raise ValueError(f"unexpected hidden shape: {tuple(hidden.shape)}")
        return hidden

    def replace_hidden(self, output: Any, hidden: torch.Tensor) -> Any:
        self.hidden_from_output(output)
        if hidden.ndim != 3 or hidden.shape[-1] != self.hidden_size:
            raise ValueError(f"replacement hidden shape mismatch: {tuple(hidden.shape)}")
        if isinstance(output, torch.Tensor):
            return hidden
        if isinstance(output, tuple):
            return (hidden, *output[1:])
        if isinstance(output, list):
            return [hidden, *output[1:]]
        raise TypeError(f"cannot preserve output type: {type(output).__name__}")

    @staticmethod
    def final_nonpadding_positions(attention_mask: torch.Tensor) -> torch.Tensor:
        if attention_mask.ndim != 2 or attention_mask.shape[1] == 0:
            raise ValueError("attention_mask must have shape [batch, sequence] and nonzero length")
        mask = attention_mask.to(dtype=torch.bool)
        if not torch.all(mask.any(dim=1)):
            raise ValueError("each sequence needs at least one non-padding token")
        positions = mask.shape[1] - 1 - torch.flip(mask, dims=[1]).to(torch.int64).argmax(dim=1)
        return cast(torch.Tensor, positions)
