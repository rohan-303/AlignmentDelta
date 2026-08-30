# Technical-pilot direction sample freeze

**Phase:** `technical_pilot`

**Scientific execution:** `false`

**Source:** `andyrdt/refusal_direction`, commit `9d852fae1a9121c78b29142de733cb1340770cc3`

## Frozen policy

1. Read only the pinned `harmful_train.json` and `harmless_train.json` source files already materialized in the AlignmentDelta source-data cache.
2. Derive each record ID as `rd:` plus the first 24 hexadecimal characters of the SHA-256 digest of canonical UTF-8 JSON (`sort_keys=true`, compact separators).
3. Sort each class independently by stable ID.
4. Direction train: select all 208 harmful records from the frozen 80% harmful direction-train partition and the first 208 harmless records from the frozen 80% harmless direction-train partition.
5. Direction validation: select the first 12 harmful and first 12 harmless records from the frozen direction-validation partitions, using stable-ID ordering.
6. Preserve class labels and concatenate records in deterministic role order: harmful records followed by harmless records within each role.
7. No RNG is used for the primary selection (`rng_seed = null`). No output, score, norm, or site diagnostic may alter membership.

## Counts

| Role | Harmful | Harmless | Total |
|---|---:|---:|---:|
| Direction train | 208 | 208 | 416 |
| Direction validation | 12 | 12 | 24 |

## Rationale

The original method randomly samples equal class counts with `n_train=128`, whereas AlignmentDelta's frozen source protocol uses a deterministic 80/20 split to avoid the original validation/test overlap with HarmBench. The technical pilot retains all available harmful direction-train items and an equal deterministic harmless count. This controls the large class imbalance without selecting sample sizes from direction quality or refusal behavior. The bounded 12+12 validation subset follows the existing pilot protocol's technical validation range and keeps full layer/site diagnostics computationally feasible.

## Exact membership and ordering

The exact stable IDs are recorded in the generated machine-readable artifacts under `artifacts/pilot/step_3_1/`:

- `source_selection_manifest.json`: complete selected IDs, source counts, source hashes, algorithm, and ordering;
- `run_manifest.json`: immutable copy of the selection metadata and manifest hash.

Raw instructions are not included in this protocol or either artifact.

## Scientific boundary

This is a technical-pilot sampling policy only. It is not a powered scientific sample, does not define a confirmatory cohort, and does not authorize any benchmark or outcome analysis.
