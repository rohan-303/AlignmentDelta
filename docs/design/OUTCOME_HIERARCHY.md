# Outcome hierarchy

## Primary outcomes

1. **Safety discrimination:** paired performance on harmful prompts (appropriate refusal) and benign safety-adjacent prompts (appropriate assistance), reported separately and as a prespecified boundary-discrimination composite. Refusal rate alone is not primary.
2. **Epistemic calibration:** on the same objective multiple-choice items used for utility, score correctness and normalized probability assigned to the valid answer choices. Primary calibration statistic is Brier score; NLL is secondary. ECE is descriptive because binning is sample-sensitive.
3. **Semantic consistency:** paired-item agreement across manually validated meaning-preserving variants, with safety decision agreement primary and answer/probability agreement secondary.

## Secondary outcomes

- Objective utility accuracy on the same known-answer task.
- Response length and invalid-format rate as diagnostics.
- Attempt versus validated success only where an objective validator exists; it is not a novelty claim.

## Diagnostic outcomes

- refusal style categories;
- per-item log probabilities and margins;
- activation perturbation and projection removal;
- evaluator disagreement and missingness;
- harmful text exposure counts.

All primary outcomes and their directionless contrasts are specified before confirmatory runs. No result is promoted to primary after inspection.
