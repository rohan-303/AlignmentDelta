# Step 4.0H — Cloud Test/Path Parity Hotfix

## Summary

Step 4.0G cloud hydration and offline verification were successful, but a fresh cloud pytest run exposed two integration defects:

1. MMLU calibration artifacts lacked the frozen `broad_category` field.
2. Engineering and historical technical-pilot loaders still expected obsolete flat refusal files.

No Qwen model was loaded, no technical smoke was run, and no scientific inference or outcomes were produced.

## Fixes

- Integrated `configs/manifests/mmlu_subject_categories.toml` as the sole category authority.
- Validated exactly 57 subjects and the four allowed categories.
- Added `broad_category` to every canonical MMLU row, calibration item, and consistency pair.
- Added calibration category validation and frozen 3/3/3/3 coverage checks.
- Added revision constants and `refusal_revision_root(...)` to the shared source-layout contract.
- Updated `engineering_subset()` and the technical-pilot loader to use the exact revisioned nested refusal checkout.
- Added explicit cache-root and `ALIGNMENTDELTA_CACHE` support.
- Removed only the six obsolete flat local cache files; no duplicate source files were created.
- Kept model/Hugging Face imports lazy in `technical_pilot.py`, allowing source-loader validation without model imports.

## Verification

Real pinned MMLU materialization:

```text
subjects = 57
total = 15,858
dev = 285
validation = 1,531
test = 14,042
duplicate stable IDs = 0
calibration IDs = 12/12
consistency source IDs = 12/12
category coverage = STEM 3, humanities 3, social_sciences 3, other 3
```

Real nested refusal cache:

```text
harmful_train = 260
harmless_train = 18,793
engineering direction_train = 16
direction_validation = 8
technical-pilot loader resolved both canonical nested files
```

Direction source-ID parity against the Step 3.2 manifest passed exactly.

Final test and quality checks:

```text
134 tests passed
Ruff passed
mypy passed
uv pip check passed
uv build passed
more exact cloud tests passed
model-free dry-run passed
```

Dry-run remained:

```text
representations = 60
logical_condition_states = 1,860
xstest_generations = 744
mmlu_option_scoring_operations = 1,488
consistency_original_scoring_operations = 1,488
consistency_transformed_scoring_operations = 1,488
total_forward_operation_estimate = 5,208
model_inference = 0
model_weights_loaded = 0
```

## Boundary

No Qwen model was loaded. No technical smoke was executed. No master scientific run was initialized. No scientific inference or scientific outcomes occurred.
