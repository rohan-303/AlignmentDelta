# Consistency pair rule

The pilot construct is **behavioral consistency under meaning-preserving perturbations**. It uses deterministic transformations rather than unpublished generated paraphrases.

For utility items, apply a deterministic option-order permutation generated from seed `20260830`, update the answer index, and retain the same option text. For benign safety-adjacent prompts, apply only a versioned wrapper-format transformation that preserves substantive content. Pair IDs are `source_id + transformation_name + transformation_version`; ordering is lexicographic by source ID then transformation name. Exclude only malformed source rows, invalid answer remapping, or template-rendering failure. Acceptance cannot depend on target-model outcomes. Human validation is required before any broader transformation is added.
