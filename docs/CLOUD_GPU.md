# Cloud GPU workflow

The same AlignmentDelta entry points are used locally, in Kaggle, and in Google Colab. This document does not download a model or benchmark.

## Kaggle

In a notebook:

```bash
!git clone https://github.com/rohan-303/AlignmentDelta.git
%cd AlignmentDelta
!pip install uv
!uv sync --extra ml --extra dev
!uv run --extra ml --extra dev python -m alignmentdelta.diagnostics.environment --profile cloud_gpu --json-output artifacts/diagnostics/kaggle_environment.json
```

Store a Hugging Face token in Kaggle Secrets, expose it only to the process that needs authentication, and never print it or write it to Git, manifests, or notebook output.

## Google Colab

```bash
!git clone https://github.com/rohan-303/AlignmentDelta.git
%cd AlignmentDelta
!pip install uv
!uv sync --extra ml --extra dev
!uv run --extra ml --extra dev python -m alignmentdelta.diagnostics.environment --profile cloud_gpu --json-output artifacts/diagnostics/colab_environment.json
```

Use Colab Secrets or an environment variable for Hugging Face authentication. Do not paste tokens into cells, command history, source files, manifests, or commits.

## Portability rules

- The `cloud_gpu` profile does not enable quantization or assume a particular GPU or BF16 capability.
- Inspect the diagnostic before selecting precision or device-dependent settings.
- Save diagnostics, logs, configurations, and any future run artifacts to persistent storage before the session ends.
- Cloud runtime resets and failures must not be represented as completed scientific runs.
- Model and benchmark downloads remain outside Step 1.1.
