# Direction artifact schema

Required fields:

```text
schema_version, synthetic_test_only, model_id, model_revision,
tokenizer_revision, chat_template_hash, direction_source, direction_revision,
direction_blob_ids, train_manifest_hash, validation_manifest_hash,
selected_layer, selected_site, token_position_rule, raw_norm,
normalized_direction, direction_dtype, hidden_dimension, git_commit,
environment_manifest_hash, artifact_sha256
```

All identifiers and hashes are nonempty; `normalized_direction` length equals `hidden_dimension`; `synthetic_test_only` must be false for real artifacts and true for test fixtures. Actual model-derived artifacts remain prohibited in Step 2.3.
