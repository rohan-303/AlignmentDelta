# Direction-estimation protocol — Step 2.4 freeze

## Original source

Repository: `andyrdt/refusal_direction`; commit `9d852fae1a9121c78b29142de733cb1340770cc3`; Apache-2.0.

The source has six harmful/harmless train/validation/test JSON files. Its original validation/test partitions overlap HarmBench, so AlignmentDelta does not use those files for direction estimation.

## AlignmentDelta source choice

AlignmentDelta uses Option B: a deterministic split of only the pinned `harmful_train.json` and `harmless_train.json` files. IDs are sorted lexicographically; the first `floor(0.80*n)` IDs are direction-train and the remainder are direction-validation. This is a leakage correction, not an outcome-driven change.

Counts:

- harmful train source: 260; direction train 208; direction validation 52;
- harmless train source: 18,793; direction train 15,034; direction validation 3,759.

The original harmful/harmless validation and test files are provenance-only and excluded from the AlignmentDelta direction role.

## Direction construction

For each candidate end-of-instruction position `p` and residual block `l`:

```text
r_raw[l,p] = mean(direction_train_harmful[l,p]) - mean(direction_train_harmless[l,p])
```

Activation accumulation is float64. Nonfinite values, dimension mismatches, missing masks, and norms below `1e-12` fail the artifact. Normalization occurs only after these checks.

The pinned source uses multiple end-of-instruction positions and model-specific wrappers. AlignmentDelta records the exact tokenizer/template hash and position rule in the direction artifact.

No real target-model direction has been extracted in Step 2.4.
