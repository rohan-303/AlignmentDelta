# Step 4.0F — Refusal-Direction Cache Layout Hotfix

## Cloud failure

The fresh Colab hydration run reached `_validate_refusal(destination)` after the pinned GitHub clone and checkout succeeded. It failed with `HYDRATED_REFUSAL_SOURCE_MISSING`; no authentication error occurred and no scientific execution was started.

## Root cause

The released validator searched for split files at the cache root, while the pinned commit `9d852fae1a9121c78b29142de733cb1340770cc3` stores them under `dataset/splits/`. The exact frozen layout is now shared by hydration validation and direction reconstruction through `experiments/source_layout.py`. The repository is not flattened and no duplicate root-level files are created.

## Pinned upstream evidence

The public pinned checkout was independently inspected. All six files exist at the nested paths and match the historical counts and SHA-256 values:

| File | Count | SHA-256 |
|---|---:|---|
| `dataset/splits/harmful_train.json` | 260 | `8f5c0eac0efd2a7f99084bbe8d0de2c465e31b1997184783c917969d9de9ece1` |
| `dataset/splits/harmful_val.json` | 39 | `305f1d1e6dfa6c50a32d24a18ef815f42b5441eb83e6d7767d242107162fd9f4` |
| `dataset/splits/harmful_test.json` | 572 | `5e12ae102c3791dee083a69ab6269a78e033411c629bc3f66f75d2fde196d9ef` |
| `dataset/splits/harmless_train.json` | 18,793 | `86623b1f8a25aa35df153fc97a556dbcebb6a7c881538ae43ee479ca17f2e002` |
| `dataset/splits/harmless_val.json` | 6,264 | `772010758e7d771ef4c7e5e4acdfd7598dcece1a6f383f20d382f640913a2a4d` |
| `dataset/splits/harmless_test.json` | 6,266 | `1b5930ce5e855ada758b3116ce7c4aaea9b9d05f8cdd77b385511d4c84173b19` |

## Validation and boundary

The validator now requires those exact relative paths, counts, and hashes. Metadata records nested relative paths. The nested-layout regression fixture, mocked hydration flow, provider tests, and offline verification checks pass.

No Qwen model was loaded, no technical smoke was executed, and no scientific inference or scientific outcome was produced.
