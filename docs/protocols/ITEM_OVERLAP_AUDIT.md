# Item-level overlap audit

The audit compares the refusal-direction source, XSTest, HarmBench, and the newly materialized MMLU source using exact canonical text hashes and lowercase/whitespace/punctuation-normalized hashes. Stable IDs are used where a source supplies them. Raw prompt/question text is retained only in memory or protected cache.

MMLU subject/split source IDs are generated from canonical question/options/answer hashes. The selected 12 calibration and 12 consistency source IDs are disjoint. No target-model embeddings or outcomes are used. Exact and normalized overlap counts, affected IDs, and exclusion decisions are recorded in the generated ignored audit artifact `artifacts/data_audit/step_3_4_overlap_summary.json`; no harmful text is retained in tracked output.

Existing refusal-source harmful validation/test overlap with HarmBench remains excluded from the refusal-direction role. Any optional fuzzy candidate is only flagged, never automatically excluded.
