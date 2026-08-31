# Step 4.0 Operation Accounting

This document separates logical experimental states from model operations. The frozen pilot has 24 XSTest representations, 12 MMLU calibration representations, and 12 consistency pairs represented twice, for 60 representations. Each representation has one canonical alpha=0 baseline plus five directions at six nonzero alpha values: 31 logical condition states.

| Quantity | Count | Meaning |
|---|---:|---|
| Item representations | 60 | 24 XSTest + 12 MMLU + 24 consistency |
| Logical condition states | 1,860 | 60 × 31 |
| Unique baselines | 60 | One per representation; no control alpha=0 pseudoreplication |
| XSTest generations | 744 | 24 × 31 |
| MMLU option-score sequences | 1,488 | 12 × 31 × 4 |
| Consistency original option-score sequences | 1,488 | 12 × 31 × 4 |
| Consistency transformed option-score sequences | 1,488 | 12 × 31 × 4 |
| Estimated forward calls | 5,208 | 744 generation calls + 4,464 option-sequence calls |

The prior Step 3.4 values of 372 for each consistency side were logical condition counts, not four full option-text forward calls per representation. No scientific outcome had been observed, no experimental condition changed, and only compute-operation accounting was corrected.
