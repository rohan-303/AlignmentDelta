"""Direction subset loading, estimation, and sanitized artifact metadata."""

from __future__ import annotations

import hashlib
import json
from pathlib import Path
from typing import Any, cast

import torch

from .capture import OnlineMeanDifference

CACHE = Path.home() / ".cache" / "alignmentdelta" / "source_data" / "refusal_direction"
SOURCE_FILES = {"harmful": "harmful_train.json", "harmless": "harmless_train.json"}


def stable_id(record: dict[str, Any]) -> str:
    canonical = json.dumps(record, sort_keys=True, separators=(",", ":"), ensure_ascii=False).encode()
    return "rd:" + hashlib.sha256(canonical).hexdigest()[:24]


def engineering_subset() -> dict[str, list[dict[str, Any]]]:
    selected: dict[str, list[dict[str, Any]]] = {}
    for role, filename in SOURCE_FILES.items():
        records = json.loads((CACHE / filename).read_text(encoding="utf-8"))
        indexed = sorted(((stable_id(record), record) for record in records), key=lambda pair: pair[0])
        selected[role] = [record for _, record in indexed[:16]]
    return {
        "direction_train": selected["harmful"][:8] + selected["harmless"][:8],
        "direction_validation": selected["harmful"][8:12] + selected["harmless"][8:12],
    }


def render_messages(tokenizer: Any, record: dict[str, Any]) -> str:
    instruction = str(record["instruction"])
    rendered = tokenizer.apply_chat_template(
        [{"role": "user", "content": instruction}], tokenize=False, add_generation_prompt=True
    )
    return cast(str, rendered)


def estimate_direction(activations: list[tuple[torch.Tensor, bool]], hidden_size: int) -> tuple[torch.Tensor, float]:
    accumulator = OnlineMeanDifference(hidden_size)
    for values, harmful in activations:
        accumulator.add(values, harmful=harmful)
    return accumulator.direction()
