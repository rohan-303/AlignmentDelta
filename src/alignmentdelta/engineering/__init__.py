"""Real-model engineering validation components."""

from .controls import ControlDiagnostic, orthogonal_control
from .model_registry import QWEN25_1P5B, ModelSpec, get_model_spec
from .projection import signed_projection, transform_block_output
from .refusal import refusal_score, refusal_token_metadata

__all__ = [
    "ControlDiagnostic",
    "ModelSpec",
    "QWEN25_1P5B",
    "get_model_spec",
    "orthogonal_control",
    "refusal_score",
    "refusal_token_metadata",
    "signed_projection",
    "transform_block_output",
]
