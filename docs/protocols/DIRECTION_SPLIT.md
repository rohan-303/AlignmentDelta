# Deterministic direction train/validation split

The original pinned repository already supplies train/validation/test files. AlignmentDelta does not re-split by observed behavior. It uses the source train partition for `direction_train` and source validation partition for `direction_validation`, preserving source categories and IDs.

If a source requires a project-level split, construct it deterministically: canonicalize stable IDs, sort lexicographically by `(source, stable_id)`, apply a seeded PyTorch/CPU-independent hash assignment with seed `20260830`, and allocate 80% train/20% validation within each source category. No model outputs enter the assignment. The resulting item manifest records the exact IDs and SHA-256 hash. A duplicate or overlap with any evaluation role is a hard failure.

This preserves the paper’s explicit source split where available and gives a deterministic, outcome-independent rule for any additional approved source.
