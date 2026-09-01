# Step 4.0G — MMLU Parquet Materialization Hotfix

## Cloud failure

The pinned `cais/mmlu` snapshot downloaded successfully, then the broad Parquet reader failed at `row["choices"]` with `KeyError: choices`. Offline verification failed at the same reader. No Qwen model, technical smoke, scientific inference, or master run was started.

## Pinned inventory

The sanitized inventory is recorded in `STEP_4_0G_MMLU_PARQUET_INVENTORY.json`. The revision contains 176 Parquet files: 171 canonical subject/split files, four aggregate `all/*` files, and one `auxiliary_train/train-00000-of-00001.parquet` file.

The exact first offending file is `auxiliary_train/train-00000-of-00001.parquet`; its only column is `train` and it has 99,842 rows. It is intentionally excluded. Aggregate `all/*` files are also excluded to prevent duplicate ingestion.

## Fix

The reader now reuses the tracked 171-file `configs/manifests/mmlu_source_files.json` universe. It accepts only canonical `subject/{dev,validation,test}-*.parquet` paths, validates `question`, `choices`, and `answer`, checks optional subject columns, sorts shards deterministically, assigns per-subject/split source indices, and rejects duplicate stable IDs or source keys.

Normal hydration repairs a valid raw snapshot with missing or corrupt derived artifacts without redownloading. `--verify` remains network-free and nonmutating and fails clearly when derived artifacts are incomplete. Final metadata is written only after successful materialization and hashes the final cache state.

## Real pinned-snapshot evidence

The corrected reader and materializer were run against the real pinned snapshot:

```text
subjects = 57
total = 15,858
dev = 285
validation = 1,531
test = 14,042
duplicate stable IDs = 0
calibration IDs resolved = 12/12
consistency source IDs resolved = 12/12
```

Derived calibration and consistency artifacts were recreated and verified successfully.

## Boundary

No model weights were loaded. No technical smoke or scientific execution occurred. No benchmark outcomes were produced.
