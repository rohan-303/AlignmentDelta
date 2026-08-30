# Claim boundary

## General rule

Claims must be limited to the sampled checkpoints, intervention operator, prompts, evaluators, and observed dose range. The study cannot establish that safety alignment is globally removed, that a direction is the sole mechanism, or that results generalize to all model families.

## Scenario A — strong collateral drift

Permitted: the refusal-direction intervention was associated with measurable non-refusal changes beyond matched controls in the tested checkpoints and dose range, with uncertainty intervals and robustness checks. Prohibited: “safety alignment causes calibration degradation” universally, or causal claims beyond the controlled operator.

## Scenario B — only safety/refusal changes

Permitted: the tested intervention produced selective safety-boundary changes without detectable changes in the measured non-refusal outcomes. This is a meaningful selectivity/null-collateral result. Prohibited: “alignment was removed entirely.”

## Scenario C — random perturbations drift similarly

Permitted: collateral changes were not specific to the refusal direction under the tested perturbation matching, weakening the safety-specific mechanism interpretation. Prohibited: claiming refusal directionality from a before/after effect alone.

## Scenario D — inconsistent families

Permitted: response curves differed across the sampled checkpoints, showing that a single-family result should not be generalized. Prohibited: treating one checkpoint as a random sample of its family or forcing a common law.

## Always prohibited

- “uncensored models are more capable” without an objective capability design;
- “our intervention removes alignment entirely”;
- “reversibility proves shared representations”;
- treating evaluator willingness as validated harmful capability;
- releasing harmful raw text without a separate safety/terms review;
- inventing generalization, licenses, or benchmark permissions.
