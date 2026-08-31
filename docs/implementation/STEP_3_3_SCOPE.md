# Step 3.3 scope — decision deferred

**Status: scope only. Step 3.3 is not executed.**

Step 3.2C technical validation is complete for the pinned Qwen 3B checkpoint, but confirmatory readiness remains blocked. An external review must occur before any outcome collection.

## Branch A — Cross-family technical validation

Validate at least one additional architecture/model family using an independently selected technical site and the same frozen engineering boundaries.

- Scientific advantage: tests whether the technical procedure is portable beyond Qwen.
- Risk: additional model access, architecture-adapter, memory, and reproducibility failures.
- Compute requirement: at least one eligible GPU runtime, plus model-specific storage and execution time.
- Dependency: approved model access, adapter validation, frozen source identity, and independent site selection.
- Claim supported: the technical pipeline has been exercised on more than one model family if completed.
- Does not support: cross-family behavioral or scientific conclusions without the separate scientific protocol.

## Branch B — Qwen exploratory scientific pilot

Run the first very small, explicitly exploratory AlignmentDelta outcome pilot on the technically validated Qwen checkpoint.

- Scientific advantage: obtains preliminary outcome data on a technically validated checkpoint.
- Risk: exploratory results may be underpowered, model-specific, and vulnerable to evaluator or benchmark limitations.
- Compute requirement: additional cloud GPU runs for baseline, refusal-direction, random-control, and signed-alpha conditions.
- Dependency: explicit exploratory protocol approval, authoritative evaluation manifests, leakage checks, and confirmation that no result will be treated as confirmatory.
- Claim supported: only narrowly scoped exploratory observations under the frozen protocol.
- Does not support: general safety, capability, alignment, or cross-family claims.

## Branch C — Resolve confirmatory gates first

Close outstanding model-access, evaluator, MMLU, consistency-pair, and final cross-family-matrix blockers before collecting outcome data.

- Scientific advantage: strengthens the validity and interpretability of later outcome work.
- Risk: delays outcome collection and may require additional engineering or access work.
- Compute requirement: depends on model-access and evaluator feasibility; no outcome run is required initially.
- Dependency: Llama access, Gemma access, HarmBench 13B classifier feasibility, authoritative MMLU retrieval and item manifest, consistency-pair materialization, and a final cross-family model matrix.
- Claim supported: improved confirmatory readiness only after every gate is independently closed.
- Does not support: any scientific outcome or intervention-effect claim by itself.

## Decision boundary

No branch is selected by this document. Step 3.3 must remain unexecuted until external review chooses a branch and the applicable protocol is separately frozen.
