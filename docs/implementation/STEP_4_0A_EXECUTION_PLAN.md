# Step 4.0A — Exploratory Scientific Execution Plan

Status: implementation and validation stage only; scientific execution is prohibited in this milestone.

## Scope

Build a cloud-ready, explicitly gated exploratory runner for the frozen Qwen 3B pilot. Local validation is limited to dry-run and synthetic execution. No Qwen weights, benchmark inference, XSTest responses, MMLU outcomes, consistency outcomes, HarmBench execution, or scientific results may be produced.

## Gates

1. Verify repository identity, branch, exact starting commit, clean tree, required manifests/protocols, and protected-repository isolation.
2. Audit Step 3.2C artifacts for an exact serialized refusal direction; otherwise implement deterministic reconstruction from the pinned refusal-direction source and require the frozen direction hash before any item.
3. Freeze model, revision, layer, intervention, controls, alpha grid, generation, scoring, lifecycle, and scientific phase identities.
4. Independently account for representations, logical conditions, generations, option sequences, and actual forward calls; document any correction without changing scientific conditions.
5. Implement explicit cloud-only real execution requiring `--execute --profile cloud_gpu`, exact revision enforcement, CUDA/BF16/VRAM/disk gates, integrity hooks, resumability, atomic outputs, deterministic chunking, manifest locks, run identity, and safe exports.
6. Implement synthetic end-to-end execution without CUDA, Hugging Face downloads, model weights, or scientific model outcomes.
7. Add tests first for safety gates, accounting, deduplication, integrity, resumability, schemas, blinding, chunking, exports, and CLI behavior; run focused and full validation.
8. Create the cloud hydration command and Colab runbook without executing the runbook.
9. Verify tracked-file safety, zero local scientific inference, clean repository, commit the exact code, push `origin/main`, and verify local/remote identity.

## Required final boundary

If all gates pass: `STEP_4_0_EXECUTION_READY`, `SCIENTIFIC_EXECUTION_NOT_STARTED`, and `READY_FOR_CLOUD_STEP_4_0`.

If any gate remains unresolved: `STEP_4_0_EXECUTION_BLOCKED`. No scientific execution may begin from this milestone.
