# Technical-pilot execution amendments

This document records only implementation and computational changes for Step 3.1. It does not authorize scientific outcomes or change any scientific endpoint.

## Amendment 1 — source sampling

- **BEFORE:** frozen AlignmentDelta direction extraction used a reduced 8+8 engineering subset; the underlying source protocol retained an imbalanced 208 harmful / 15,034 harmless direction-train split.
- **AFTER:** technical pilot uses all 208 harmful direction-train IDs and the first deterministic 208 harmless direction-train IDs, plus a fixed 12+12 validation subset.
- **TECHNICAL REASON:** the pinned original method samples equal class counts (`n_train=128`), while the large harmless pool would otherwise dominate compute and accumulation. Stable IDs preserve reproducibility and prevent outcome-dependent selection.
- **SCIENTIFIC CONSEQUENCE:** Step 3.1 is not a powered scientific sample and cannot support RQ1/RQ2. Confirmatory sampling remains separately frozen.

## Amendment 2 — batching

- **BEFORE:** the source implementation defaulted to batch size 32; Step 3.0 found that variable-length left-padded Qwen refusal-score batches were not numerically equivalent to batch size 1.
- **AFTER:** batch size 1 remains the trusted default. Equal-token-length, unpadded buckets may be adopted only after fixed-subset refusal-score, activation, and direction-cosine checks pass predeclared tolerances. Variable-length left padding remains prohibited unless independently revalidated.
- **TECHNICAL REASON:** preserve final-token semantics and avoid padding-induced model-runtime discrepancies.
- **SCIENTIFIC CONSEQUENCE:** no scientific measurement is changed; correctness is preferred over throughput.

## Amendment 3 — activation memory

- **BEFORE:** no full-pilot activation accumulation path existed.
- **AFTER:** all direction extraction uses streaming float64 sums and discards per-record activations after accumulation; no persistent full activation corpus is created.
- **TECHNICAL REASON:** bound host/GPU memory while retaining numerical precision.
- **SCIENTIFIC CONSEQUENCE:** only the predeclared source policy is used; no outcome-dependent memory reduction is permitted.

## Amendment 4 — alpha diagnostics

- **BEFORE:** Step 3.0 validated a reduced alpha set.
- **AFTER:** Step 3.1 validates the frozen technical grid `{-0.5, 0, 0.25, 0.5, 0.75, 1.0, 1.25}` for the refusal direction and exactly four controls using activation-dose and finite-logit diagnostics.
- **TECHNICAL REASON:** exercise the full signed operator range before any later scientific phase.
- **SCIENTIFIC CONSEQUENCE:** no alpha is selected or revised based on refusal behavior, utility, calibration, or any scientific outcome.
