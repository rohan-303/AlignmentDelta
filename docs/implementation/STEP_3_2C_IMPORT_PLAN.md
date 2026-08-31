# Step 3.2C cloud-evidence import plan

## Attachment discovery

Enumerate the supplied Downloads paths and classify files by detected content, not filename. Record byte size, type, and SHA-256. Do not alter originals.

## Preservation and extraction

Keep originals in place. Validate any archive in an external temporary validation workspace under `.tmp/step_3_2c_validation/`, never directly in tracked source. Extract only after structural inspection.

## Provenance validation

The canonical run must use code commit `c1148ab9fef7006485dc3bedf578c16f3d286dc5`, model `Qwen/Qwen2.5-3B-Instruct`, revision `aa8e72537993ba99e69dfaafa59ed015b17504d1`, phase `technical_pilot`, `scientific_execution=false`, and profile `cloud_gpu`. A mismatch blocks import/completion.

## Manifest, log, and notebook validation

Prefer the run manifest inside a verified archive. Compare any separate manifest byte-for-byte or semantically. Use the complete cloud log as execution evidence and the Colab notebook only as corroboration. Cross-check identity, environment, stages, final decisions, and warnings across all sources.

## Archive and content policy

Recompute any external archive hash when available. Validate every listed file path, byte count, and SHA-256. Reject weights, caches, secrets, credentials, raw harmful text, and unexplained files. If no external archive hash is recorded, state that explicitly and rely on internal file hashes.

## Import policy

Import only verified sanitized technical artifacts into ignored `artifacts/pilot/step_3_2/`. Never copy weights, caches, secrets, raw prompts, or regenerated local equivalents. Preserve original cloud run ID and provenance.

## Tracked summary and Git policy

Only if the evidence supports `VERIFIED_PRIMARY_QWEN_TECHNICAL_PASS`, create the sanitized tracked summary `docs/implementation/STEP_3_2C_CLOUD_VALIDATION.md`, run all repository checks, and commit only documentation/metadata with `Step 3.2C: record primary Qwen cloud technical validation`. Do not commit bulky generated artifacts.

## Step 3.3 boundary

Do not execute Step 3.3. Create `STEP_3_3_SCOPE.md` only after a complete independently validated Step 3.2C pass. Confirmatory readiness remains separately gated and is not inferred from technical validation.
