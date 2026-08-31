# MMLU source decision

**Decision: `MMLU_PROVENANCE_VERIFIED_MIRROR`.**

The original pinned source remains `hendrycks/test` at revision `4450500f923c49f1fb1dd3d99108a0bd9717b660`; its README points to `https://people.eecs.berkeley.edu/~hendrycks/data.tar`. Three bounded HTTPS retrieval attempts on 2026-08-31 timed out before headers and received zero bytes.

The accepted fallback is `cais/mmlu` at immutable revision `c30699e8356da336a370243923dbaf21066bb9fe`. Its card identifies MMLU, cites the original Hendrycks et al. benchmark, exposes the standard 57-subject question/choices/answer schema, and declares the original source dataset. Its full history shows the original loader/source archive lineage followed by a Parquet conversion. It is a provenance-equivalent mirror, not the original archive and not claimed byte-identical.

The materialized subject files contain actual validated split counts and hashes in `configs/manifests/mmlu_source_files.json`; raw question text remains in the external cache. The exploratory calibration and consistency manifests are now complete and disjoint. The separate mirror audit records the remaining byte-identity limitation.
