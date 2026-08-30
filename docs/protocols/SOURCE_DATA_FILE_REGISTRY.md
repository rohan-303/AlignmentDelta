# Source-data file registry

Machine-readable registry: `artifacts/data_audit/source_data_registry.json`.

Materialized outside Git under `~/.cache/alignmentdelta/source_data/`:

| Source | Files | Counts | Status |
|---|---|---:|---|
| `andyrdt/refusal_direction` | harmful train/val/test; harmless train/val/test | 260 / 39 / 572; 18,793 / 6,264 / 6,266 | materialized |
| `paul-rottger/xstest` | `xstest_prompts.csv` | 450 | materialized |
| `centerforaisafety/HarmBench` | all/test/val behavior CSVs | 400 / 320 / 80 | materialized |
| `hendrycks/test` | official `data.tar` | not available | blocked by source-host timeout |

For every materialized file the registry records repository revision, path, byte size, SHA-256, count, stable-ID strategy, and terms status. It records no raw prompt text.

MMLU was not replaced by a mirror. Its official repository README links to an archive hosted at `people.eecs.berkeley.edu`; repeated retrieval attempts timed out. Exact MMLU hashes and item IDs therefore remain blocked.
