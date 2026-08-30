# Intervention selection

## Decision

**Primary intervention:** inference-time signed directional projection derived from a refusal-related difference-in-means direction. For hidden state `h` and unit direction `r`, use the explicitly defined operator:

`h' = (I - alpha r r^T) h`.

`alpha=0` is the untouched baseline; `alpha=1` removes the current component along `r`; positive fractional alpha partially removes it; alpha below zero amplifies that component. Negative alpha is a mathematically defined counter-steering condition, not evidence of restoration.

The primary refusal-direction paper defines the direction as harmful-minus-harmless mean activations, selects a layer/token candidate on validation data, and reports directional ablation over residual-stream activations across layers and token positions. It also reports activation addition at a selected layer. The paper does not establish a broad signed-alpha response-curve study across collateral outcomes.

## Implementation constraints for Step 3

- Estimate directions from a disjoint contrast set.
- Select direction/layer rules without inspecting confirmatory outcomes.
- Record token positions and intervention sites explicitly.
- Apply the same operator family to every finalist; do not silently substitute weight orthogonalization.
- Validate shape, finiteness, norm, and hook placement before measurement.
- Treat model-specific layer mapping as a protocol parameter, not an after-the-fact optimization.

## Alternatives rejected for the main paper

- **Weight orthogonalization:** permanent checkpoint edit, harder to audit as a reversible laboratory intervention, and already directly described in prior work.
- **LoRA de-alignment:** training and data choices add a second causal intervention; *Ablating Safety* already covers this family.
- **Activation addition alone:** prior work reports it, and its scale is not directly equivalent to projection ablation.
- **Prompt-only reframing:** useful baseline, but not safety-alignment removal.
- **Sparse feature/SAE intervention:** promising but adds representation-learning and feature-selection dependencies not needed for the narrow question.

## Cross-architecture caveat

The operator is architecture-compatible only when a standard residual-stream state of fixed model width is exposed. The pilot must reject any model whose implementation requires opaque remote code or whose chat template/hidden-state hook cannot be audited.
