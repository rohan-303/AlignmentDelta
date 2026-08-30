# Step 3.2 scope — primary Qwen 3B technical deployment

## Authorization boundary

Step 3.2 is authorized only to validate the primary checkpoint:

- Model: `Qwen/Qwen2.5-3B-Instruct`
- Revision: `aa8e72537993ba99e69dfaafa59ed015b17504d1`
- Loading: `trust_remote_code=False`
- Precision: BF16, unquantized
- Phase: `engineering`
- `scientific_execution`: `false`

This scope does not authorize XSTest, HarmBench, the HarmBench classifier, MMLU, calibration, consistency outcomes, paper statistics, paper figures, or confirmatory model-matrix execution.

## Deployment decision

Step 3.1 measured the Qwen 1.5B runtime on the local RTX 3060 Laptop GPU and calculated that the 3B BF16 weights plus projected runtime overhead exceed the local 6 GB VRAM budget. Qwen 3B should therefore run in a reproducible cloud environment, not be downloaded locally by Step 3.1.

Minimum practical cloud requirement:

- 12 GB usable VRAM minimum, with BF16 support;
- 16 GB preferred for headroom and allocator variability;
- at least 12 GB free disk for the pinned model snapshot, cache metadata, artifacts, and temporary files;
- no quantization and no CPU layer offload;
- isolated `uv` environment with pinned dependencies;
- exact model revision and complete snapshot file hashes recorded before loading.

Kaggle/Colab-class BF16-capable GPUs are preferred where they satisfy these requirements; provider availability must be verified at execution time rather than assumed.

## Permitted Step 3.2 work

1. Verify the cloud image, GPU, BF16 support, disk, dependency lock, and reproducibility manifest.
2. Download only the pinned Qwen 3B snapshot and record file hashes.
3. Load and benign-forward the model with `trust_remote_code=False`.
4. Validate the Qwen runtime adapter and residual capture.
5. Extract the Qwen 3B direction under its independently frozen source policy.
6. Run independent frozen site selection and technical alpha validation.
7. Measure runtime, memory, hook reversibility, and state integrity.

No full scientific outcomes may be run until the separate access, terms, evaluator, dataset, and item-closure gates are explicitly closed.
