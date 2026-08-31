# Step 4.0E — Cloud Hydration Hotfix

## Observed failure

The first Colab hydration attempt failed while resolving
`andyrdt/refusal_direction` through the Hugging Face model API. No model was
loaded, no scientific run was initialized, and no scientific outputs existed.
The failure is not treated as an authentication request: the source registry
sent a GitHub repository through a model-oriented Hugging Face call.

## Repair

`prepare_cloud_data` now uses explicit source backends:

- `andyrdt/refusal_direction` — pinned GitHub commit;
- `paul-rottger/xstest` — pinned GitHub commit;
- `cais/mmlu` — pinned Hugging Face dataset revision with `repo_type="dataset"`.

GitHub sources are cloned into temporary directories, detached at the exact
commit, verified with `git rev-parse HEAD`, copied without `.git`, and promoted
atomically. MMLU calibration items and the frozen consistency pairs are
materialized from the pinned parquet source using frozen IDs and pair metadata.

Normal hydration reuses verified caches and rebuilds corrupt caches. `--verify`
is network-free and read-only. It validates source metadata, refusal/XSTest
counts, MMLU structure, and the frozen materialized IDs.

## Direction parity

Cloud direction reconstruction now reuses the canonical `stable_id`,
`render_messages`, and `deterministic_sample` helpers from the technical-pilot
pipeline. The frozen 208/208 training selection and chat rendering therefore
have one implementation.

## Validation boundary

All local tests remain model-free. Qwen loading, technical smoke, benchmark
execution, HarmBench, and scientific outcome generation remain cloud-only and
were not run during this hotfix.
