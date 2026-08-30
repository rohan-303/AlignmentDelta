# Direction artifact specification

A future artifact contains schema version, model ID/revision, tokenizer revision, chat-template hash, direction-source repository/revision/blob IDs, train/validation manifest hashes, position rule, selected layer/site, raw norm, normalized vector, dtype, hidden dimension, creation Git commit, environment-manifest hash, and SHA-256 hash.

The vector is normalized only after finite/nonzero checks. Artifacts must be written atomically and never overwrite a different hash. Synthetic vectors in tests must be labelled `synthetic_test_only=true`; no model-derived direction artifact is created in Step 2.3.
