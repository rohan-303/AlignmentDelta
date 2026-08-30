# Pilot protocol freeze

## Purpose and sizes

The pilot is technical, not powered for paper effects. Per model, use bounded strata: at least 4 and at most 16 direction-validation items per contrast class; at least 4 and at most 12 baseline refusal checks; at least 4 and at most 12 technical dose checks; at least 4 and at most 12 utility/calibration checks; and at least 4 and at most 12 paired consistency checks. Exact IDs come from the frozen manifest. Evaluator validation is a fixed small stratified subset, never selected by output.

## Alpha grid

**ACCEPT:** `{-0.5, 0, 0.25, 0.5, 0.75, 1.0, 1.25}`. This follows the signed projection semantics and includes baseline, partial removal, full nominal removal, overshoot, and counter-steering. It is not changed for predicted effect size.

## Execution order

1. access/revision/license gate; 2. model load; 3. chat-template check; 4. hidden-state/hook shape check; 5. direction estimation; 6. technical direction/site validation; 7. seeded random controls; 8. finite/nontrivial alpha sweep; 9. baseline safety check; 10. evaluator smoke test; 11. integrated pilot.

## Stop/accept rules

Stop for OOM, nonfinite activations/scores, invalid hook dimensions, near-zero direction, failed orthogonality, template/tokenizer inconsistency, unavailable evaluator, unsuitable baseline signal, or numerically pathological alpha. Continue only when artifacts and provenance are complete, technical checks pass, and evaluator outputs are reproducible. A null calibration or consistency effect is not a stopping reason.
