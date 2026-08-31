# MMLU mirror provenance audit

## Decision

The accepted source is `MMLU_PROVENANCE_VERIFIED_MIRROR`, not the original author-hosted archive and not a claim of byte identity.

- dataset: `cais/mmlu`
- immutable revision: `c30699e8356da336a370243923dbaf21066bb9fe`
- license metadata: MIT
- retrieval: HTTPS streamed Parquet downloads with explicit user-agent and timeout
- cache: `~/.cache/alignmentdelta/source_data/mmlu/c30699e8356da336a370243923dbaf21066bb9fe/`

## Evidence

The dataset card explicitly identifies MMLU, cites Hendrycks et al. (ICLR 2021), links the original benchmark paper, and declares `source_datasets: original`. The pinned metadata exposes the question/choices/answer schema, four choices, A–D labels, 57 subject configurations, and standard dev/validation/test split semantics.

The complete Hugging Face history was audited. It includes the original `hendrycks_test` loader lineage, a hosted source-data commit, and a later immutable Parquet conversion. The final pinned commit is the Parquet conversion by `justinphan3110`; it is not the original author archive. The repository history therefore provides traceable conversion lineage, but does not prove byte-for-byte identity with `data.tar`.

The pinned structure contains 57 subjects, 285 dev records, 1,531 validation records, and 14,042 test records. All materialized subject files have fields `question`, `subject`, `choices`, and `answer`; every record has exactly four choices and an integer answer in 0–3.

## Limitations

The original Berkeley archive was retried three times over HTTPS on 2026-08-31 at 15:12:33Z, 15:12:54Z, and 15:13:16Z with explicit `AlignmentDelta-research/3.4` user-agent, 20-second bounds, streamed temporary-file policy, and 1/2/4-second backoff. All three attempts timed out before HTTP response headers, received zero bytes, and accepted no archive. CAIS Parquet content is accepted as provenance-equivalent benchmark data for this exploratory pilot only. Byte identity to the unavailable original archive is not claimed. Raw questions remain outside Git in the external cache.
