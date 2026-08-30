# Step 3.2 plan — cloud technical validation of primary Qwen 3B

## Boundary

Step 3.2 is technical validation only. Every execution must record `phase=technical_pilot` and `scientific_execution=false`. The only authorized model is `Qwen/Qwen2.5-3B-Instruct` at revision `aa8e72537993ba99e69dfaafa59ed015b17504d1`, loaded with `trust_remote_code=False`, BF16, CUDA, no quantization, no CPU offload, and batch size 1.

## Cloud/environment detection

Add a pure environment report and gate that records platform, Python, Torch/CUDA, CUDA availability, GPU count/name/total VRAM, BF16 support, free disk, Git commit, and execution profile. The gate requires CUDA, at least 12 GiB total usable GPU memory, BF16 support, and adequate free disk. The local RTX 3060 must produce `CLOUD_GPU_REQUIRED`; it must not attempt model loading or downloading.

## Cloud bootstrap

Provide repository-native Kaggle and Colab instructions: clone, checkout the exact code commit, install `uv`, sync locked dependencies, provide Hugging Face authentication only through notebook secrets/environment variables, run the environment diagnostic, pass the GPU gate, execute the shared technical CLI, and export artifacts before teardown. No secrets are printed or embedded.

## Exact model/download/load

The cloud CLI verifies the model ID/revision before downloading the official snapshot to an external cache. It records file names, sizes, SHA-256 hashes, config/tokenizer hashes, parameter count, architecture metadata, and cache path. It loads BF16 on CUDA with `device_map=None`, no quantization, no offload, and `trust_remote_code=False`. OOM is recorded as an insufficient environment rather than repaired by changing precision or placement.

## Shared technical procedure

Reuse the Step 3.1 Qwen adapter, frozen 208+208 direction sample and 12+12 validation IDs, final-20%-pruned candidate-layer calculation, float64 streaming direction extraction, independent 3B site search, four deterministic controls, frozen seven-alpha technical grid, achieved-dose metrics, and integrity checks. No Qwen 1.5B direction, site, or controls are reused.

## Artifacts and transfer

Write only to `artifacts/pilot/step_3_2/`. Include manifests, technical summaries, hashes, runtime records, and direction metadata; never include model weights, cache contents, secrets, or raw harmful text. Provide an archive command that excludes weights/cache and records the archive SHA-256. Provide import-back verification for archive hash, run commit, model revision, environment manifest, and original run ID.

## Failure/recovery

- Local or insufficient cloud GPU: stop before download/load and return `CLOUD_GPU_REQUIRED`.
- Missing BF16/CUDA/disk: stop before model load and record the gate failure.
- Snapshot mismatch: stop and do not substitute a revision.
- OOM: record exact failure and require a larger GPU; do not quantize/offload.
- Adapter mismatch or nonfinite state: record technical block and preserve logs/artifacts.
- Cloud teardown: export the artifact archive before termination.

## Validation and prohibitions

Add unit tests for the gate, VRAM threshold, no-local-run policy, registry, CLI validation, shared adapter contract, sample reuse, archive manifest, and import-back verification. Run ordinary repository validation locally. Do not run Qwen 3B locally. A complete Step 3.2 CLI run is permitted only on an eligible cloud GPU and is not executed in this local session. No XSTest, HarmBench, classifier, MMLU, calibration, consistency, paper statistics/figures, or cross-family scientific comparison is permitted.

## Step 3.3 criterion

Step 3.3 may be scoped only after an eligible cloud run validates the exact Qwen 3B checkpoint, adapter, directions, site, controls, alpha grid, integrity, runtime, and reproducible artifact export. This local blocked gate does not authorize Step 3.3.
