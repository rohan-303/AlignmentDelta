# Step 4.0 cloud handoff

After an authorized cloud exploratory run, download only:

1. `step_4_0_sanitized_export.tar.gz`;
2. `step_4_0_sensitive_annotation_export.tar.gz` through the approved protected channel;
3. the cloud execution log with safe metadata only;
4. the Colab notebook, if used, after removing credentials and raw benchmark dumps.

Verify each archive SHA-256 against its recorded archive manifest before transferring it. Do not download or commit Qwen weights, Hugging Face caches, raw benchmark caches, raw XSTest responses outside the approved sensitive archive, unblinding maps, credentials, tokens, or connection strings.
