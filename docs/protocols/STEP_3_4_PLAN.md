# Step 3.4 plan — resolve MMLU provenance and authorize the exploratory pilot

## Scope and safety boundary

Step 3.4 closes pre-execution data and scoring gates only. It may retrieve and validate public benchmark data, build manifests/subsets/pairs, validate synthetic scoring, and run a zero-inference dry-run. It must not load Qwen weights, generate XSTest responses, score MMLU with Qwen, execute consistency outcomes, run HarmBench, or perform scientific analysis.

## Gate plan

1. Retry the exact original MMLU URL over HTTPS with a user-agent, bounded connect/read timeout, streamed temporary download, retry/backoff, response logging, archive validation, and SHA-256. Accept as `ORIGINAL_AUTHOR_ARCHIVE` only after structure checks.
2. If the original URL fails, audit `cais/mmlu`: owner, card citations, license, revision history, historical loaders/conversion metadata, split/schema compatibility, subject structure, and immutable revision. Accept only as `provenance_verified_mirror`; never call it byte-identical without proof.
3. If neither source meets the acceptance standard, retain `MMLU_SOURCE_BLOCKED`, do not fabricate data, and keep exploratory readiness blocked.
4. For an accepted source, materialize raw data under `~/.cache/alignmentdelta/source_data/mmlu/`, outside Git; record source, revision, files, bytes, hashes, schema, subjects, splits, and malformed records.
5. Freeze the original subject-to-broad-domain mapping with provenance, deterministic content-hash item IDs, and a complete MMLU manifest.
6. Run an outcome-independent overlap audit against direction data, XSTest, HarmBench, and MMLU using exact and normalized text keys; record counts and exclusions without raw harmful text.
7. Select exactly 12 calibration items by deterministic broad-domain stratification and exactly 12 additional disjoint consistency source items when valid data permit. Freeze IDs before inference.
8. Construct one deterministic bijective option-order permutation for each consistency source item; remap answers automatically; validate pair integrity and source/calibration disjointness.
9. Freeze consistency agreement after canonical option remapping. Validate option scoring, Brier, NLL, ECE, and nonfinite handling with synthetic logits only.
10. Operationalize blinded XSTest annotation using opaque IDs whose mapping remains in ignored run artifacts; test that alpha, intervention, direction, and control metadata do not leak.
11. Update the dry-run planner to distinguish logical conditions, unique baselines, XSTest generation operations, MMLU option-sequence operations, consistency original/transformed operations, and estimated forward operations. Keep alpha-zero as one canonical baseline.
12. Run the final dry-run with zero model loading/inference, validate manifests/hashes/disjointness/blinding, and decide readiness strictly from the checklist.

## Readiness criteria

`EXPLORATORY_PILOT_GO` requires the accepted MMLU source, complete manifest, 12 calibration items, 12 disjoint consistency items, 12 validated pairs, scoring/annotation/blinding validation, and a passing zero-inference dry-run. Otherwise the result is `EXPLORATORY_PILOT_BLOCKED`.

Confirmatory status remains independent and cannot become GO from Qwen-only preparation.
