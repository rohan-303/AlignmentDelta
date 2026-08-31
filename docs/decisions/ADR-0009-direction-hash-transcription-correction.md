# ADR-0009 — Direction Hash Transcription Correction

## Decision

`DIRECTION_HASH_TRANSCRIPTION_ERROR_CONFIRMED`

The authoritative refusal-direction digest is:

```text
5a8983bcbe4402096210485f8f9b0191eb35b3de84f46624e2dd9811fd09a3fe
```

## Evidence

The value appears consistently in the original Step 3.2C cloud-generated evidence:

- `artifacts/pilot/step_3_2/direction_layer_27.json`
- `artifacts/pilot/step_3_2/run_manifest.json`
- `artifacts/pilot/step_3_2/source_cloud_run.log`
- `artifacts/pilot/step_3_2/source_colab_notebook.ipynb`
- `artifacts/pilot/step_3_2/source_archive_step_3_2_export.tar.gz`

The archive SHA-256 is `9d3dc34c417d20517dfd7abd4c1616818929307c75ce876bcdcf766bf4f10371`, matching the original cloud record. The imported run manifest SHA-256 is `ca7a3752fc2f73c5772152812379791074a2dcee6cf428de2e66c4fb4bddfa55`, also matching the recorded identity.

The malformed value was:

```text
5a8983bcbe4402096210485f8f0191eb35b3de84f46624e2dd9811fd09a3fe
```

It is 62 characters and appears in later Step 3.2C documentation and the Step 4.0A task transcription, not in the original cloud-generated evidence.

## Scope and history

- Original Step 3.2C cloud artifacts were not modified.
- No scientific outcomes had been observed.
- No experimental condition changed.
- No site selection changed.
- No direction was reselected.
- No result was excluded.
- The correction occurred before scientific execution.
