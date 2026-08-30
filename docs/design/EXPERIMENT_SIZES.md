# Experiment sizes

Counts below are design variables, not observed results or benchmark-size claims.

## Minimum viable paper

Three primary checkpoints, the signed pilot-retained alpha grid, the refusal direction plus four matched orthogonal random directions, fixed XSTest/HarmBench standard inputs, a compact objective calibration/utility subset, and one validated semantic-equivalence pair set. One deterministic generation per condition is the minimum; failed/invalid runs are repeated only under a frozen retry rule.

## Preferred experiment

The same matrix with independent prompt-order/generation-seed replicates and the full pre-registered paired consistency set. Repeat random-direction controls as separate directions rather than pseudo-replicating one direction. This supports curve uncertainty and control variability without adding unrelated benchmarks.

## Expansion experiment

Only if resources permit: a second checkpoint within one or more families, an optional StrongREJECT sensitivity analysis with a locally reproducible evaluator, and a second validated paraphrase source. Expansion cannot replace a null result or be selected after seeing the primary effect.

## Planning formula

For each planned cell, record `models × alpha_levels × direction_conditions × safety_items × variants × replicates` and separately record objective calibration forward-pass count and maximum generated-token budget. The exact item counts remain blocked on release/version/license verification and must be frozen before Step 3 confirmatory runs.
