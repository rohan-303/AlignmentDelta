# Step 1.1 runtime architecture

## Baseline runtime

The required ML runtime is an optional `ml` dependency group in `pyproject.toml`, resolved by `uv.lock`. PyTorch is sourced from the official PyTorch CUDA 12.6 wheel index for Windows/Linux. The driver-reported CUDA version and the CUDA runtime bundled with the Torch wheel are recorded separately.

Sentence-Transformers, bitsandbytes, DeepSpeed, FlashAttention, vLLM, PEFT, and TRL are not baseline dependencies. Quantization is not a baseline scientific condition; it may be considered later for development/pilot runs only and must be recorded in metadata.

## Execution profiles

`configs/execution/` contains compute-only profiles:

```bash
python -c "from alignmentdelta.execution import load_profile; print(load_profile('cpu_test'))"
```

- `local_dev` uses conservative GPU settings and permits, but does not enable, later quantization.
- `cloud_gpu` does not assume a GPU model, BF16 support, or quantization.
- `cpu_test` is CUDA-independent and intended for infrastructure tests.

Profiles do not identify models or define scientific conditions.

## Environment diagnostic and manifest

Run the diagnostic without model or dataset access:

```bash
python -m alignmentdelta.diagnostics.environment --profile cpu_test
python -m alignmentdelta.diagnostics.environment --profile local_dev --json-output artifacts/diagnostics/environment.json
```

The JSON manifest records host, Git, Python, package, Torch/CUDA/GPU, profile, reproducibility, precision, and quantization state. A diagnostic manifest belongs under `artifacts/diagnostics/`, not `results/`, and is not a scientific observation.

## Precision and reproducibility

`auto` resolves to BF16 only when the actual CUDA backend reports BF16 support; otherwise CUDA resolves to FP16 and CPU resolves to FP32. Explicit unsupported BF16 requests fail rather than silently falling back. Seed utilities cover Python, NumPy, Torch CPU, and visible CUDA devices. Deterministic Torch algorithms can reduce performance and may reject unsupported operations; reproducibility is not guaranteed across hardware, drivers, CUDA/cuDNN, or Torch versions.

## Cloud GPU workflow

See [`CLOUD_GPU.md`](CLOUD_GPU.md) for Kaggle and Colab instructions. Credentials must be supplied through notebook/environment secrets and are never printed or written to manifests. Preserve artifacts before an ephemeral notebook session ends.
