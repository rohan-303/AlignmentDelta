# Intervention-site selection — executable freeze

Candidate sites are `(position, layer)` pairs where `position` is one of the pinned end-of-instruction positions and `layer` ranges from `0` through `floor(0.80 * n_layers) - 1`. The final 20% of layers are pruned, matching the pinned source selector's `prune_layer_percentage=0.20`.

For each candidate, using only `direction_validation`:

```text
R(logits) = log(p_refusal + 1e-8) - log(1 - p_refusal + 1e-8)
S(p,l) = mean_i[R_i_baseline - R_i_ablated(p,l)]
```

The candidate intervention is evaluated at the single AlignmentDelta residual-stream block-output site. Harmless refusal addition and harmless KL divergence are validity diagnostics:

- KL ceiling: `0.1`;
- harmless refusal-addition floor: `0.0`;
- direction norm floor: `1e-12`.

Reject nonfinite scores, shape/dimension failures, norm failures, KL above `0.1`, refusal-addition below `0.0`, and candidates in the pruned final 20%. Select the maximum `S`. Ties break by smallest layer, earliest position, then lexical hook name.

No calibration, MMLU, consistency, utility, primary evaluation, or confirmatory outcome enters selection. If no candidate survives, the engineering gate fails.
