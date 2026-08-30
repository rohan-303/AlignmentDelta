# XSTest gate

**Verified fact:** the official repository is `paul-rottger/xstest`, default branch `main`, GitHub-reported license `CC-BY-4.0`, and the associated work is XSTest: A Test Suite for Identifying Exaggerated Safety Behaviours in Large Language Models. The repository and paper identify safe/unsafe prompt categories and prompt IDs; the exact file and immutable commit must be recorded before use.

**Project decision:** use XSTest only for benign-boundary/over-refusal discrimination. Primary classification is the original rule-based refusal/response procedure reproduced from the pinned source, with prompt-level labels preserved. A fixed blinded manual subset audits automated classifications.

**Unresolved issue:** exact immutable release commit, exact item count/file hash, redistribution terms for every included file, and any evaluator dependency were not fully established in this pre-download audit. Status: `usable_no_redistribution` only if the source can be accessed under its terms; otherwise `unresolved`. No XSTest data are downloaded here.
