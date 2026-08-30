# Item-level overlap audit

Machine-readable outputs:

- `artifacts/data_audit/item_overlap_summary.json` — all materialized source-file comparisons;
- `artifacts/data_audit/selected_overlap_summary.json` — the selected AlignmentDelta direction split against evaluation files.

Normalization: lowercase, non-alphanumeric runs collapsed to spaces. Exact comparison uses SHA-256 of the selected text fields; stable-ID comparison uses the source IDs or deterministic record IDs. Raw text is retained only in memory during the audit.

The original refusal-source harmful validation/test partitions overlap HarmBench. Therefore they are excluded from the AlignmentDelta direction role. The selected deterministic split of harmful/harmless source-train files has zero exact and normalized overlap with XSTest and HarmBench test/validation files.

Near-duplicate detection was not run. No near-duplicate candidate is treated as proven duplicate. Exact or normalized overlap must be excluded from one role before any future evaluation.
