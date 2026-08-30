# Step 3.2 cloud GPU workflow

Step 3.2 is a **technical pilot only**. The cloud entrypoint uses the shared AlignmentDelta intervention implementation and records `phase=technical_pilot` and `scientific_execution=false`. It does not run scientific benchmarks or generate model completions.

## Frozen requirements

- Model: `Qwen/Qwen2.5-3B-Instruct`
- Revision: `aa8e72537993ba99e69dfaafa59ed015b17504d1`
- Code: checkout the exact commit used by the run and record it in the manifest
- CUDA GPU with at least 12 GiB total usable VRAM, BF16 support, and at least 12 GiB free disk
- BF16, unquantized, `device_map=None`, no CPU offload, `trust_remote_code=False`, batch size 1
- Do not assume a Kaggle/Colab GPU type; inspect the actual machine first

A local or insufficient GPU stops before snapshot download/model load and returns `CLOUD_GPU_REQUIRED`.

## Kaggle

1. Enable a GPU accelerator and create persistent output/storage as appropriate.
2. Store the Hugging Face token in Kaggle Secrets only if the pinned snapshot requires authentication. Never paste it into a cell or print it.
3. Run:

```bash
!git clone https://github.com/rohan-303/AlignmentDelta.git
%cd AlignmentDelta
!git checkout <EXACT_RUN_COMMIT>
!python -m pip install uv
!uv sync --locked --extra ml --extra dev
!env -u PYTHONPATH uv run --extra ml --extra dev python -m alignmentdelta.engineering.cloud_gate --profile cloud_gpu --require-eligible --json-output artifacts/pilot/step_3_2/environment_gate.json
!env -u PYTHONPATH uv run --extra ml --extra dev python -m alignmentdelta.engineering.qwen3b_technical --profile cloud_gpu --archive /kaggle/working/step_3_2_artifacts.tar.gz
```

Copy `/kaggle/working/step_3_2_artifacts.tar.gz` to persistent Kaggle output before terminating the session.

## Google Colab

1. Select a CUDA runtime and use Colab Secrets for `HF_TOKEN` only when required.
2. Run:

```bash
!git clone https://github.com/rohan-303/AlignmentDelta.git
%cd AlignmentDelta
!git checkout <EXACT_RUN_COMMIT>
!python -m pip install uv
!uv sync --locked --extra ml --extra dev
!env -u PYTHONPATH uv run --extra ml --extra dev python -m alignmentdelta.engineering.cloud_gate --profile cloud_gpu --require-eligible --json-output artifacts/pilot/step_3_2/environment_gate.json
!env -u PYTHONPATH uv run --extra ml --extra dev python -m alignmentdelta.engineering.qwen3b_technical --profile cloud_gpu --archive /content/step_3_2_artifacts.tar.gz
```

Download `/content/step_3_2_artifacts.tar.gz` before the runtime is deleted. Authentication, when needed, must be provided by the notebook secret/environment mechanism and must not appear in command output, manifests, archives, or Git.

## Import back into the canonical repository

Do not copy model weights or the Hugging Face cache. Copy only the archive into the local repository, verify its SHA-256 against the cloud-provided value, inspect the included `run_manifest.json`, and verify the cloud run ID, exact Git commit, exact model revision, and environment manifest before extracting into `artifacts/pilot/step_3_2/`. Preserve the original cloud run ID; never regenerate observations locally and label them as the cloud run.

The export code excludes weight extensions, cache/weights/secrets path components, and raw harmful text. Generated artifacts remain ignored by repository policy.

## Scope prohibition

Step 3.2 does not run XSTest, HarmBench, the HarmBench classifier, MMLU, calibration, consistency evaluation, paper statistics, paper figures, or cross-family scientific comparisons. A successful technical grid is not a scientific outcome.
