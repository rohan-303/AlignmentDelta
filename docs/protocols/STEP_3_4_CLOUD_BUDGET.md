# Exploratory cloud budget

The frozen workload is counted from manifests, not throughput assumptions. With 7 alpha states (baseline plus six nonzero alpha values) and five intervention choices at each nonzero alpha (one refusal direction plus four controls), there are 31 condition states per representation.

For 24 XSTest items, 12 calibration items, and 12 consistency pairs represented twice: 60 representations and 1,860 logical condition states. This yields 744 XSTest generations, 1,488 MMLU option-sequence scores, 372 original consistency scores, and 372 transformed consistency scores: 2,976 estimated model forward operations.

Step 3.2C T4 memory/runtime measurements are engineering context only. No scientific throughput is inferred. Use predeclared chunks by outcome family and stable item order: XSTest items 1–24, calibration IDs in manifest order, and consistency pair IDs in manifest order. Do not split based on observed outcomes. Storage planning uses sanitized records plus hashes; raw response/question text remains in protected external artifacts.
