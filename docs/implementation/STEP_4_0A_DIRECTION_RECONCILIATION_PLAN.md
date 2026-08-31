# Step 4.0A-R — Direction Hash Reconciliation Plan

## Purpose

Repair the refusal-direction identity only if original Step 3.2C cloud evidence establishes one authoritative digest. This is a provenance-only stage and must not load Qwen, reconstruct a direction locally, execute benchmarks, generate responses, score MMLU, run consistency outcomes, or execute HarmBench.

## Procedure

1. Preserve and inventory the existing uncommitted Step 4.0A work.
2. Search tracked and ignored AlignmentDelta files for both candidate digests and contextual references without emitting raw benchmark text.
3. Verify the original Step 3.2C archive, run manifest, cloud log, Colab notebook, import verification, and selected layer-27 metadata.
4. Apply the declared evidence precedence: original structured cloud artifact, original cloud log, original notebook output, import verification, Step 3.2C documentation, later documentation, and task transcription.
5. Classify the result as transcription error, original-cloud conflict, or unresolved identity.
6. If and only if a single valid digest is established by original evidence, repair downstream references, add an erratum, and update the reconstruction gate.
7. Re-run tests and static validation without scientific inference.
8. Commit and push only if the hash is authoritatively reconciled and all execution-readiness gates pass.

## Safety boundary

Original Step 3.2C artifacts are immutable and must not be rewritten. The protected `C:\Users\rohan\SHIFT-ICD` repository must not be modified. No scientific execution begins in this stage.
