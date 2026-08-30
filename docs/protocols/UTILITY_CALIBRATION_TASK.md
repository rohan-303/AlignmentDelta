# Utility and calibration task

**Decision:** use standard MMLU rather than MMLU-Pro for the pilot because its original public repository and known-answer multiple-choice format are simpler to audit and support direct probability extraction. MMLU-Pro remains a possible confirmatory alternative only after a separate protocol amendment.

Source: `hendrycks/test`, `master`, GitHub-reported MIT license. Freeze the exact commit/file hashes before use. Use a predeclared compact subject-stratified pilot subset and a confirmatory item manifest generated from source IDs without looking at model performance; do not choose subjects after scoring.

The pilot manifest records source revision, split, subjects, item IDs, answer labels, and file hash. The exact item count is a protocol parameter bounded before execution, not an observed dataset fact. No MMLU data are downloaded in Step 2.2. License and redistribution status must be rechecked before any copy leaves the source environment.
