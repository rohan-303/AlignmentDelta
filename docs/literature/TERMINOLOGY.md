# Terminology audit

- **Safety alignment:** training/system modifications intended to make behavior safer while retaining helpfulness.
- **Refusal:** observable decline behavior; not synonymous with alignment.
- **Uncensored:** ambiguous community/deployment label covering different post-training histories or edits.
- **De-alignment:** underspecified; avoid without defining the operation.
- **Alignment removal:** controlled intervention intended to weaken a specified safety behavior with checkpoint/operator/strength defined.
- **Safety modification:** neutral umbrella for strengthening or weakening safety behavior.
- **Abliteration:** inconsistent practitioner term for projection, weight edits, or released “uncensored” models.
- **Representation intervention:** hidden-state edit, projection, addition, or gate at inference.
- **Jailbreak:** input/interaction attempt to elicit policy-inconsistent behavior; not model transformation.
- **Harmful fine-tuning:** fine-tuning on harmful or policy-violating behavior; not synonymous with activation ablation.

## Recommendation

Use **controlled safety-behavior weakening** or **controlled safety-alignment intervention**. Define the operator mathematically; reserve “uncensored” for source labels; report refusal, validated success, utility, calibration, robustness, and spillover separately.
