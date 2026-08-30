# Direction-estimation protocol

## Verified prior method

The inspected official implementation for *Refusal in Language Models Is Mediated by a Single Direction* computes mean residual-stream activations for harmful and harmless instruction lists, then returns:

`mean_diff = mean_activations_harmful - mean_activations_harmless`.

The code accumulates activations in `float64`, uses the final token position by default (`positions=[-1]`), scans all transformer block indices, and uses a batch size default of 32. The inspected function calls the tokenizer-formatting callback supplied by the model wrapper; the repository therefore does not make one universal natural-language prompt template by itself. The implementation computes mean differences but does not normalize them in `generate_directions.py`; later intervention code may normalize or otherwise scale them. The official repository is the source of truth for the exact commit and wrapper-specific formatting.

The paper describes the contrast-direction approach, but code-level details above are reported separately. The audit did not establish a paper/code discrepancy on the mean-difference sign. Dataset identity, item counts, split logic, and all wrapper-specific formatting must be copied from the pinned implementation/data commit before execution; they are not inferred here.

## AlignmentDelta frozen procedure

For each model and candidate layer `l`, tokenize the pinned direction examples with the model's verified chat template. Record the rendered prompt and tokenizer/template revision in a provenance manifest. Capture the residual-stream activation at the selected hook and the final non-padding token position. Accumulate in float64:

`mu_h,l = (1/n_h) sum_i h_h,i,l`, `mu_s,l = (1/n_s) sum_j h_s,j,l`, `r_raw,l = mu_h,l - mu_s,l`.

Do not center across the pooled two-class sample beyond the stated difference of means. Normalize only after checking finite values and nonzero norm: `r_l = r_raw,l / ||r_raw,l||_2`. Store dtype, shape, counts, source revisions, split, token-position rule, hook name, and SHA-256 hash. Any nonfinite activation, inconsistent hidden dimension, missing padding mask, or norm below the configured numerical threshold invalidates the candidate and stops the gate; it is not silently repaired.

No real target-model direction is extracted in Step 2.2.
