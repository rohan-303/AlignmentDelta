# Utility and calibration task

Primary source: MMLU from `hendrycks/test`, pinned repository revision `4450500f923c49f1fb1dd3d99108a0bd9717b660`.

Use the standard test split and preserve the repository’s subject/file labels and answer encoding. The pilot item-selection algorithm is: sort eligible source IDs lexicographically within subject; choose a fixed predeclared number of subjects using seed `20260830` and a domain-stratified subject list; choose a fixed predeclared number of IDs per selected subject using the same deterministic ordering; never inspect model outputs when selecting items.

Exact item IDs are generated only when the pinned files are made available in the data stage. The repository reports MIT metadata, but selected-file hashes and redistribution terms must be attached before use. Status: `cleared_with_restrictions`.
