# Statistical analysis plan

> **DRAFT — TO BE FROZEN BEFORE CONFIRMATORY RUNS**

## Unit and dependence

The observation is an item × prompt-variant × model × direction × alpha result. Repeated measurements from the same item and semantic pair are not independent. Random directions are sampled control units, not independent models.

## Primary models

For continuous calibration/utility outcomes, fit a mixed-effects regression with signed/achieved dose, intervention type, model/checkpoint, and their interactions; item and semantic-pair intercepts are random effects where identifiable. For binary safety decisions, use a generalized mixed model with the same fixed effects. If convergence or sparsity fails, use paired item-level contrasts and bootstrap intervals rather than an overparameterized model.

The primary causal contrast is refusal-direction versus orthogonal-control dose response within the same checkpoint. The family term is descriptive/inferential only for the sampled checkpoints: one checkpoint per family cannot support a random-effect claim about all models in that family.

## Dose and nonlinearity

Plot outcome(alpha) and outcome(achieved-dose). Fit a prespecified linear interaction as the floor. Add a low-degree quadratic term only if pilot sample support and technical range justify it; do not use flexible splines for a small grid. Report turning/saturation behavior only with uncertainty and only inside the observed range.

## Uncertainty and multiplicity

Report effect estimates, 95% bootstrap confidence intervals, and paired permutation sensitivity checks. The three primary outcome families are tested under a stated multiplicity procedure (Holm or a clearly justified hierarchical gate) frozen before confirmatory runs. Secondary and diagnostic outcomes are labeled exploratory.

Missing evaluator outputs, invalid formats, and failed runs are reported with reasons; they are not silently imputed. The analysis code and manifest will record exclusions.
