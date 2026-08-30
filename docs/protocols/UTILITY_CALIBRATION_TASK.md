# Utility/calibration task — Step 2.4 status

The intended source is the original MMLU test archive referenced by the pinned `hendrycks/test` repository at revision `4450500f923c49f1fb1dd3d99108a0bd9717b660`.

The source repository is available, but its linked archive at `https://people.eecs.berkeley.edu/~hendrycks/data.tar` timed out repeatedly during Step 2.4. No mirror or alternate dataset was substituted.

The item-selection rule is frozen independently of model outputs: deterministic subject-stratified selection with seed `20260830`, sorted source IDs, fixed items per selected subject, and no hand-picking. Exact item manifests, labels, and hashes remain blocked until the authoritative archive is retrieved.
