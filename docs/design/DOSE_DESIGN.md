# Dose and strength design

## Operator semantics

For unit direction `r`, the primary operator is `h'=(I-alpha rr^T)h`. Alpha is a projection coefficient: alpha 0 leaves the state unchanged and alpha 1 removes its current projection along `r`. Alpha below zero amplifies the component; this is counter-steering, not restoration.

## Provisional pilot grid

Use the ordered grid `{-0.5, 0, 0.25, 0.5, 0.75, 1.0, 1.25}`. These levels are chosen from operator semantics—counter-steering, baseline, partial removal, full projection, and modest overshoot—not copied from the competitor’s values. The pilot must record achieved refusal-direction projection change and activation perturbation ratios.

## Normalization

Unit-normalize each direction. For every model/layer, report:

1. direction norm before normalization;
2. baseline RMS activation norm;
3. baseline RMS projection `r^T h`;
4. achieved perturbation RMS divided by baseline activation RMS;
5. fraction of the baseline projection removed.

Alpha values have a common mathematical interpretation as a fraction of the current direction component, but equal alpha values are not assumed to be equal physical perturbation doses across families. Primary curve comparisons must therefore include an achieved-dose axis or explicitly report that cross-family alpha equivalence is limited.

## Confirmatory grid rule

Do not choose levels after inspecting scientific outcomes. Retain the pilot grid if it spans measurable partial response without immediate saturation or numerical instability. If the grid is technically invalid, revise the protocol version before confirmatory work using a rule based only on hook validity, finite activations, and non-saturated technical range. Do not expand or shift the range because a desired behavioral effect was absent.

## Controls

Apply the same grid and achieved-dose reporting to each matched random/orthogonal direction. Generate multiple independent random directions per checkpoint, orthogonalize them to `r`, and match the baseline projection/perturbation norm. Their variability is part of the null distribution.
