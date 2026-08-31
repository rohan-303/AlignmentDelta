# Step 4.0B execution flow

The real cloud path is intentionally separate from planning and synthetic execution.

1. `exploratory_pilot --technical-smoke --profile cloud_gpu` calls `run_cloud_technical_smoke`.
2. `cloud_preflight` records `environment_gate.json`, checks CUDA/BF16/VRAM/disk/profile, then requires a clean Git tree.
3. `prepare_cloud_data.hydrate` downloads the three immutable source revisions outside Git and records file manifests.
4. `load_qwen_model` lazily imports Transformers, loads `Qwen/Qwen2.5-3B-Instruct` at the pinned revision with BF16/CUDA/unquantized settings, and verifies the Qwen2 architecture.
5. `reconstruct_direction` reuses `ResidualCapture` and `OnlineMeanDifference` with stable 208/208 source records at layer 27.
6. Direction and all four controls pass exact SHA-256, dimension, finite, norm, and orthogonality gates.
7. `technical_smoke` runs only the benign diagnostic and verifies hook cleanup and parameter sentinels.
8. Only after that gate may a future task runner enter XSTest, MMLU, or consistency paths.

The current CLI does not claim Step 4.0 readiness: `--execute` remains blocked until the benchmark condition registry, durable progress protocol, schema validation, and both archive exporters are wired to these real adapter primitives. No local invocation of either cloud entry point was performed.
