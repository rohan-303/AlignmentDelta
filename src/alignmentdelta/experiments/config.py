"""Strict, model-free experiment configuration schema and loader."""

from __future__ import annotations

import math
import tomllib
from dataclasses import asdict, dataclass
from pathlib import Path
from typing import Any


@dataclass(frozen=True, slots=True)
class StudyConfig:
    name: str
    description: str
    protocol_version: str


@dataclass(frozen=True, slots=True)
class OptionalText:
    """Preserve whether an optional text field was absent or explicitly set."""

    present: bool
    value: str | None

    def __post_init__(self) -> None:
        if self.value is not None and not self.value.strip():
            raise ValueError("optional text values must be nonempty when provided")


@dataclass(frozen=True, slots=True)
class SourceModelConfig:
    identifier: str
    revision: OptionalText
    tokenizer_identifier: str
    tokenizer_revision: OptionalText
    trust_remote_code: bool


@dataclass(frozen=True, slots=True)
class TransformationConfig:
    type: str
    implementation_version: str
    parameters: dict[str, Any]
    intervention_strength: float
    parent_source_checkpoint: str


@dataclass(frozen=True, slots=True)
class EvaluationConfig:
    benchmark_identifier: str
    benchmark_revision: str
    split: str
    evaluator_implementation_version: str


@dataclass(frozen=True, slots=True)
class PromptingConfig:
    chat_template_identifier: str
    system_prompt_identifier: str
    formatting_version: str


@dataclass(frozen=True, slots=True)
class DecodingConfig:
    deterministic: bool
    temperature: float
    top_p: float
    top_k: int | None
    max_new_tokens: int
    stop_conditions: tuple[str, ...]


@dataclass(frozen=True, slots=True)
class ReproducibilityConfig:
    seeds: tuple[int, ...]
    execution_profile: str
    planned_replicates: int


@dataclass(frozen=True, slots=True)
class ExperimentConfig:
    schema_version: str
    phase: str
    study: StudyConfig
    source_model: SourceModelConfig
    transformation: TransformationConfig
    evaluation: EvaluationConfig
    prompting: PromptingConfig
    decoding: DecodingConfig
    reproducibility: ReproducibilityConfig

    def to_dict(self) -> dict[str, Any]:
        return asdict(self)


_REQUIRED_ROOT = {
    "schema_version",
    "phase",
    "study",
    "source_model",
    "transformation",
    "evaluation",
    "prompting",
    "decoding",
    "reproducibility",
}


def _section(
    raw: dict[str, Any],
    name: str,
    required: set[str],
    optional: set[str] | None = None,
) -> dict[str, Any]:
    optional = optional or set()
    value = raw.get(name)
    if not isinstance(value, dict):
        raise ValueError(f"{name} section is required")
    missing = required - value.keys()
    if missing:
        raise ValueError(f"{name} fields required: {', '.join(sorted(missing))}")
    unknown = set(value) - required - optional
    if unknown:
        raise ValueError(f"unknown {name} fields: {', '.join(sorted(unknown))}")
    return value


def _text(value: Any, label: str) -> str:
    if not isinstance(value, str) or not value.strip():
        raise ValueError(f"{label} must be a nonempty string")
    return value.strip()


def _optional_text(value: Any, label: str) -> str | None:
    if value is None:
        return None
    return _text(value, label)


def _bool(value: Any, label: str) -> bool:
    if not isinstance(value, bool):
        raise ValueError(f"{label} must be a boolean")
    return value


def load_experiment_config(path: Path) -> ExperimentConfig:
    """Parse and validate an experiment configuration without network access."""
    with path.open("rb") as handle:
        raw = tomllib.load(handle)
    unknown_root = set(raw) - _REQUIRED_ROOT
    missing_root = _REQUIRED_ROOT - raw.keys()
    if missing_root:
        raise ValueError(f"required root fields: {', '.join(sorted(missing_root))}")
    if unknown_root:
        raise ValueError(f"unknown root fields: {', '.join(sorted(unknown_root))}")
    phase = _text(raw["phase"], "phase")
    if phase not in {"pilot", "confirmatory"}:
        raise ValueError("phase must be pilot or confirmatory")
    study = _section(raw, "study", {"name", "description", "protocol_version"})
    source = _section(
        raw,
        "source_model",
        {"identifier", "tokenizer_identifier", "trust_remote_code"},
        {"revision", "tokenizer_revision"},
    )
    transform = _section(
        raw,
        "transformation",
        {"type", "implementation_version", "parameters", "intervention_strength", "parent_source_checkpoint"},
    )
    evaluation = _section(
        raw, "evaluation", {"benchmark_identifier", "benchmark_revision", "split", "evaluator_implementation_version"}
    )
    prompting = _section(
        raw, "prompting", {"chat_template_identifier", "system_prompt_identifier", "formatting_version"}
    )
    decoding = _section(
        raw, "decoding", {"deterministic", "temperature", "top_p", "top_k", "max_new_tokens", "stop_conditions"}
    )
    reproducibility = _section(raw, "reproducibility", {"seeds", "execution_profile", "planned_replicates"})
    parameters = transform["parameters"]
    if not isinstance(parameters, dict):
        raise ValueError("transformation.parameters must be a table")
    strength = transform["intervention_strength"]
    if (
        isinstance(strength, bool)
        or not isinstance(strength, (int, float))
        or not math.isfinite(float(strength))
        or not 0 <= float(strength) <= 1
    ):
        raise ValueError("intervention_strength must be finite and between 0 and 1")
    temperature = decoding["temperature"]
    top_p = decoding["top_p"]
    if isinstance(temperature, bool) or not isinstance(temperature, (int, float)) or not 0 <= float(temperature) <= 2:
        raise ValueError("temperature must be between 0 and 2")
    if isinstance(top_p, bool) or not isinstance(top_p, (int, float)) or not 0 < float(top_p) <= 1:
        raise ValueError("top_p must be greater than 0 and at most 1")
    top_k = decoding["top_k"]
    if top_k is not None and (isinstance(top_k, bool) or not isinstance(top_k, int) or top_k < 0):
        raise ValueError("top_k must be null or a non-negative integer")
    max_new_tokens = decoding["max_new_tokens"]
    if isinstance(max_new_tokens, bool) or not isinstance(max_new_tokens, int) or max_new_tokens < 1:
        raise ValueError("max_new_tokens must be a positive integer")
    stop_conditions = decoding["stop_conditions"]
    if not isinstance(stop_conditions, list) or any(not isinstance(item, str) for item in stop_conditions):
        raise ValueError("stop_conditions must be a list of strings")
    seeds = reproducibility["seeds"]
    if (
        not isinstance(seeds, list)
        or not seeds
        or any(isinstance(seed, bool) or not isinstance(seed, int) or seed < 0 for seed in seeds)
    ):
        raise ValueError("seeds must be a nonempty list of non-negative integers")
    planned_replicates = reproducibility["planned_replicates"]
    if isinstance(planned_replicates, bool) or not isinstance(planned_replicates, int) or planned_replicates < 1:
        raise ValueError("planned_replicates must be a positive integer")
    deterministic = _bool(decoding["deterministic"], "deterministic")
    if deterministic and float(temperature) != 0:
        raise ValueError("deterministic decoding requires temperature = 0")
    return ExperimentConfig(
        schema_version=_text(raw["schema_version"], "schema_version"),
        phase=phase,
        study=StudyConfig(
            _text(study["name"], "study.name"),
            _text(study["description"], "study.description"),
            _text(study["protocol_version"], "study.protocol_version"),
        ),
        source_model=SourceModelConfig(
            _text(source["identifier"], "source_model.identifier"),
            OptionalText("revision" in source, _optional_text(source.get("revision"), "source_model.revision")),
            _text(source["tokenizer_identifier"], "source_model.tokenizer_identifier"),
            OptionalText(
                "tokenizer_revision" in source,
                _optional_text(source.get("tokenizer_revision"), "source_model.tokenizer_revision"),
            ),
            _bool(source["trust_remote_code"], "source_model.trust_remote_code"),
        ),
        transformation=TransformationConfig(
            _text(transform["type"], "transformation.type"),
            _text(transform["implementation_version"], "transformation.implementation_version"),
            dict(parameters),
            float(strength),
            _text(transform["parent_source_checkpoint"], "transformation.parent_source_checkpoint"),
        ),
        evaluation=EvaluationConfig(
            _text(evaluation["benchmark_identifier"], "evaluation.benchmark_identifier"),
            _text(evaluation["benchmark_revision"], "evaluation.benchmark_revision"),
            _text(evaluation["split"], "evaluation.split"),
            _text(evaluation["evaluator_implementation_version"], "evaluation.evaluator_implementation_version"),
        ),
        prompting=PromptingConfig(
            _text(prompting["chat_template_identifier"], "prompting.chat_template_identifier"),
            _text(prompting["system_prompt_identifier"], "prompting.system_prompt_identifier"),
            _text(prompting["formatting_version"], "prompting.formatting_version"),
        ),
        decoding=DecodingConfig(
            deterministic, float(temperature), float(top_p), top_k, max_new_tokens, tuple(stop_conditions)
        ),
        reproducibility=ReproducibilityConfig(
            tuple(seeds),
            _text(reproducibility["execution_profile"], "reproducibility.execution_profile"),
            planned_replicates,
        ),
    )
