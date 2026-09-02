# Step 4.0L — Intervention Identity Sync

## Scope

This step is a pre-science integrity hotfix. No scientific XSTest, MMLU, consistency scoring, HarmBench, benchmark outcomes, or master scientific run was executed.

## A. Pre-flight

- Protected repository `C:\Users\rohan\SHIFT-ICD` was not accessed or modified.
- Clean implementation worktree: `C:\c\Users\rohan\AlignmentDelta-step4i`.
- Starting branch: `step4i-cloud-direction-identity`.
- Starting HEAD: `6e42e9638c70ec0778003cd0ac7b3883959ee483`.
- Required Step 4.0H/I/J/K commits are ancestors of the implementation HEAD.
- The separate canonical checkout `C:\Users\rohan\AlignmentDelta` had pre-existing dirty state and was not reset or overwritten.

## B. Remote gate artifact audit

Artifact: `C:\Users\rohan\AlignmentDelta\artifacts\remote\alignmentdelta_20260902T192610Z_1ed86fad\extracted\results\manifests\technical_pre_science_gate.json`

- `model_id`: `Qwen/Qwen2.5-3B-Instruct`
- `model_revision`: `aa8e72537993ba99e69dfaafa59ed015b17504d1`
- `direction_sha256`: `286147ed00c828028d6856e5cab4e87ed5730e1e2f6f6fff047f2d3bb71a84b1`
- `layer`: `27`
- `hidden_dimension`: `2048`
- `status`: `PRE_SCIENCE_TECHNICAL_GATE_PASS`
- Controls: four controls, seeds `20260830`, `20260831`, `20260832`, `20260833`.
- Control norms: approximately 1.0 for all four.
- Control absolute dots: approximately zero for all four.
- Control hashes match the measured Step 4.0K cloud-adapter identities.

## C. Remote gate Git provenance

- Artifact `scientific_code_commit`: `e28a85bdd1ff7d8e686c2d2bfa111590a969529e`.
- Required source commit: `6e42e9638c70ec0778003cd0ac7b3883959ee483`.
- Decision: `REMOTE_GATE_GIT_PROVENANCE_MISMATCH`.
- Cause: tracked-only packaging omitted `.git`, and task-local synthetic Git metadata was initialized remotely.
- The gate remains valid technical evidence for its measured runtime identity, but it is not provenance-matched evidence for the post-4.0L code lineage. A fresh technical smoke is required after this commit.

## D–E. Conflict and root cause

`INTERVENTION_IDENTITY_DIVERGENCE_CONFIRMED`.

Before this step, `cloud_adapter.py` used the measured Step 4.0K identity while `production_orchestrator.py` used the historical direction and four historical controls. The active exploratory TOML also contained the historical identity. The conflict was an independently maintained identity transcription, not a model or data change.

## F–I. Canonical identity and integrations

Added `src/alignmentdelta/experiments/intervention_identity.py` with one authoritative set of:

- `MODEL_ID`
- `MODEL_REVISION`
- `LAYER`
- `HIDDEN_DIMENSION`
- `DIRECTION_SHA256`
- `CONTROL_SEEDS`
- `CONTROL_SHA256`

Updated `cloud_adapter.py`, `production_orchestrator.py`, and the active exploratory configuration to use the measured Step 4.0K identity. Strict reconstruction, model, protocol, layer, dimension, and control checks remain enabled.

Added parity and master/gate contract tests. Matching canonical gates pass; historical direction identity fails closed.

## J. Imported remote-gate validator

Added `src/alignmentdelta/experiments/technical_gate_validator.py`. It validates code commit, model identity/revision, protocol hashes, direction, controls, layer, hidden dimension, and pre-science PASS status without loading a model.

## K. Scientific boundary

No master run was initialized. Tests use temporary directories only. No scientific inference or benchmark scoring occurred.

## L. Packaging provenance

The prior tracked-only archive workflow cannot preserve `git rev-parse HEAD` by itself. This step documents the defect and preserves the safe future requirement: use an exact Git bundle or clone/fetch of the published commit for future technical/scientific execution, rather than unrelated synthetic metadata. The new validator and tests make provenance mismatch explicit.

## M. Historical identity search

Old identities remain only in historical evidence and the negative regression fixture. The active production modules no longer contain the historical identity. The active exploratory configuration now uses the measured current direction and control hashes.

## N. Tests and checks

- Targeted Step 4.0L identity/gate tests: passed.
- Full pytest, Ruff, mypy, build, dependency check, diff check, and dry-run results are recorded in the final execution handoff and must be rerun after the final source edits.

## O. Dry-run boundary

Expected model-free workload remains unchanged:

- representations: 60
- logical condition states: 1860
- unique baseline states: 60
- XSTest generations: 744
- MMLU option operations: 1488
- consistency original operations: 1488
- consistency transformed operations: 1488
- total forward estimate: 5208
- model inference: 0
- model weights loaded: 0

## P–Q. Release

Commit message: `Step 4.0L: unify intervention identity`.
Push must be non-force. Final verification must prove local HEAD equals `origin/main` and the implementation worktree is clean.

## Scientific decision

`STEP_4_0L_INTERVENTION_IDENTITY_PASS` is permitted only after the final full checks and push verification pass. The resulting code commit must receive a fresh remote technical smoke before scientific execution.
