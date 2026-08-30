# AlignmentDelta

## Status

Step 2.0 structured literature audit is in progress/completed as documented under `docs/literature/`; novelty remains provisional and model/benchmark selection is deferred to Step 2.1.

**Research infrastructure / reproducible ML runtime (Step 1.1).** No scientific experiments, model downloads, datasets, findings, or result files exist yet.

## Objective

AlignmentDelta is a research project studying behavioral drift under controlled safety-alignment removal in large language models. The project will begin from one exact aligned model checkpoint and apply controlled transformations to that same checkpoint, rather than primarily comparing arbitrary community checkpoints labeled “aligned” and “uncensored.”

The foundational intervention framing is:

```text
M -> T(M)
```

Later work may vary intervention strength (`M -> T_alpha(M)`) and, only where technically meaningful, study a defensible inverse/restoration procedure.

## Repository layout

- `src/alignmentdelta/` — minimal Python package
- `tests/` — package and infrastructure tests
- `configs/` — version-controlled configurations; execution profiles are separate from scientific experiment configs
- `docs/protocols/` — pre-specified scientific protocols
- `docs/decisions/` — architecture and research decision records
- `experiments/` — version-controlled orchestration definitions
- `artifacts/` — generated diagnostics and reproducibility artifacts
- `results/` — actual scientific results only after execution
- `data/` — external benchmark/model-derived data and provenance

## Requirements and setup

Python 3.11 is required. This repository uses `uv` when available:

```bash
uv sync --extra dev
```

The fallback is a local virtual environment, without global tool installation:

```bash
python -m venv .venv
.venv/Scripts/python -m pip install -e ".[dev]"
```

The lightweight bootstrap remains available with `uv sync --extra dev`. The reproducible ML runtime is opt-in with `uv sync --extra ml --extra dev`; it includes Torch, Transformers, Datasets, Accelerate, Hugging Face Hub, Safetensors, NumPy, Pandas, SciPy, scikit-learn, and psutil. Sentence-Transformers and bitsandbytes are not installed. No model or benchmark is downloaded by this step.

## Development commands

```bash
uv run --extra dev pytest
uv run --extra dev ruff check .
uv run --extra dev mypy src
uv build
```

## Experiment-contract commands

Validate the sanitized, non-executable schema example without network access:

```bash
uv run --extra dev python -m alignmentdelta.experiments.validate_config configs/experiments/example.schema.toml
```

Create only an auditable `planned` run manifest under `artifacts/`:

```bash
uv run --extra dev python -m alignmentdelta.experiments.dry_run configs/experiments/example.schema.toml
```

A scientific experiment configuration describes a condition; an execution profile describes runtime behavior. The stable `experiment_condition_id` identifies the scientific condition, while every concrete execution receives a unique `run_id`. The repository still contains no AlignmentDelta scientific results.


All future scientific runs must be traceable to their Git commit, configuration, exact model revision, and environment metadata. Failed and invalidated runs remain auditable. Synthetic/mock data is permitted only inside tests and must never enter scientific result directories. See [`docs/RESEARCH_INTEGRITY.md`](docs/RESEARCH_INTEGRITY.md).

This repository currently contains no scientific results. It is research infrastructure, not a validated safety or capability claim.
