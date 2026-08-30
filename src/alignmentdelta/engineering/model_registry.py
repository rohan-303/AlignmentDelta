"""Pinned model registry for the Step 3 engineering target."""

from __future__ import annotations

from dataclasses import dataclass


@dataclass(frozen=True, slots=True)
class ModelSpec:
    model_id: str
    revision: str
    tokenizer_revision: str
    architecture: str
    hidden_size: int
    expected_layers: int
    trust_remote_code: bool
    role: str


QWEN25_1P5B = ModelSpec(
    model_id="Qwen/Qwen2.5-1.5B-Instruct",
    revision="989aa7980e4cf806f80c7fef2b1adb7bc71aa306",
    tokenizer_revision="989aa7980e4cf806f80c7fef2b1adb7bc71aa306",
    architecture="Qwen2ForCausalLM",
    hidden_size=1536,
    expected_layers=28,
    trust_remote_code=False,
    role="engineering",
)


QWEN25_3B = ModelSpec(
    model_id="Qwen/Qwen2.5-3B-Instruct",
    revision="aa8e72537993ba99e69dfaafa59ed015b17504d1",
    tokenizer_revision="aa8e72537993ba99e69dfaafa59ed015b17504d1",
    architecture="Qwen2ForCausalLM",
    hidden_size=2048,
    expected_layers=36,
    trust_remote_code=False,
    role="primary_technical",
)


def get_model_spec(name: str = "qwen2.5-1.5b") -> ModelSpec:
    """Return an explicitly registered technical model specification."""
    normalized = name.lower()
    if normalized in {"qwen2.5-1.5b", QWEN25_1P5B.model_id.lower()}:
        return QWEN25_1P5B
    if normalized in {"qwen2.5-3b", QWEN25_3B.model_id.lower()}:
        return QWEN25_3B
    raise ValueError(f"unsupported technical model: {name}")


def validate_spec(spec: ModelSpec) -> None:
    """Reject mutable or non-engineering model specifications."""
    if not spec.revision or spec.revision in {"main", "latest"}:
        raise ValueError("model revision must be immutable")
    if spec.trust_remote_code:
        raise ValueError("remote code is prohibited")
    if spec.role not in {"engineering", "primary_technical"}:
        raise ValueError("technical model role is not authorized")
