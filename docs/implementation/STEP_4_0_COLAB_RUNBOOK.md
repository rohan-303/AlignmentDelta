# Step 4.0 Colab Runbook

Do not run this document on a local workstation. The real Qwen commands are cloud-only and require the released commit.

1. GPU preflight: confirm CUDA, BF16 capability, at least 12 GiB usable VRAM, adequate disk, and no active competing jobs.
2. Clone: `git clone https://github.com/rohan-303/AlignmentDelta.git && cd AlignmentDelta`.
3. Checkout the exact released code commit: `git checkout STEP_4_0_SCIENTIFIC_CODE_COMMIT`.
4. Install the locked environment: `uv sync --extra ml --extra dev`.
5. Hydrate pinned sources (GitHub sources use detached commits; MMLU uses dataset semantics): `uv run python -m alignmentdelta.experiments.prepare_cloud_data --cache-root "$HOME/.cache/alignmentdelta/source_data"`.
6. Verify the hydrated cache without network access: `uv run python -m alignmentdelta.experiments.prepare_cloud_data --verify --cache-root "$HOME/.cache/alignmentdelta/source_data"`.
7. Run tests: `env -u PYTHONPATH uv run pytest -q`.
8. Validate the safe plan: `env -u PYTHONPATH uv run python -m alignmentdelta.experiments.exploratory_pilot --dry-run --root .`.
9. Initialize one master run: `env -u PYTHONPATH uv run python -m alignmentdelta.experiments.exploratory_pilot --initialize-run --profile cloud_gpu --root . --output-root artifacts/runs/step_4_0`.
10. Run the cloud-only technical gate: `uv run python -m alignmentdelta.experiments.exploratory_pilot --technical-smoke --profile cloud_gpu --root . --output-root artifacts/runs/step_4_0`.
11. Inspect the gate for `PRE_SCIENCE_TECHNICAL_GATE_PASS`, exact direction/control identities, current master commit, and protocol locks.
12. Execute one task using the same master run ID: `uv run python -m alignmentdelta.experiments.exploratory_pilot --execute --profile cloud_gpu --root . --output-root artifacts/runs/step_4_0 --master-run-id <ID> --task xstest --resume` (use `mmlu` or `consistency` for the other tasks).
13. Split a task deterministically with `--chunk-index N --chunk-count M`; resume using the same master run ID and chunk identity.
14. Reconcile master completion, create sanitized and sensitive annotation exports separately, verify archive manifests and SHA-256 values, and download only approved artifacts.

Current status: the production CLI path is wired. Execute only from the released clean cloud commit after the technical gate passes; no local Qwen execution is authorized.
