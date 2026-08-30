# HarmBench gate

**Verified fact:** the official repository is `centerforaisafety/HarmBench`, default branch `main`, GitHub-reported MIT repository license. HarmBench provides standardized harmful-behavior evaluation materials and an official automated evaluation framework.

**Project decision:** use only the pinned standard behavior subset approved before confirmatory evaluation. Record category labels, item IDs, repository commit, file hashes, and the exact evaluator source/revision. Refusal/compliance is not treated as validated harmful capability.

**Evaluator gate:** the official classifier/evaluator identifier, revision, model size, access/gating, dependency set, and local RTX 3060 feasibility must be verified from the official implementation before use. A repository license alone does not prove that model weights or dependencies have compatible terms. No HarmBench data or classifier is downloaded in Step 2.2. Status: `unresolved` pending this verification.
