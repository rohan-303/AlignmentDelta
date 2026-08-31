# MMLU option-scoring protocol

**Status: frozen before outcome execution; executable only after the authoritative MMLU source gate closes.**

For each option, score the complete option-text token sequence conditionally on the exact frozen question prompt. Option labels are included in the prompt wrapper; the answer continuation is the full option text, not a single-token label. Let `s_i` be the sum of token log-probabilities for option `i`; no length normalization is applied because the frozen primary score is the conditional sequence log-probability of the complete option text. Normalize with stable log-sum-exp: `p_i = exp(s_i - logsumexp(s))`.

The question template is the official MMLU multiple-choice format with the subject description, deterministic dev examples, options labeled A/B/C/D, and an `Answer:` prefix. BOS handling and token boundaries are delegated to the pinned tokenizer's normal encoding; no manual string tokenization or answer-token lookup is permitted. Scores accumulate in float64 after reading model log-probabilities. No EOS token is appended to the answer continuation unless the tokenizer's normal scoring path requires it; that choice is recorded in the run manifest.

Primary metrics: accuracy and multiclass Brier score. Secondary metric: NLL. Descriptive metric: ECE with fixed bins defined before execution. Invalid, missing, nonfinite, or tokenizer-inconsistent scores invalidate the item-condition and are reported without imputation, alternate formatting, or parameter tuning.

No calibration result has been produced because the authoritative MMLU archive was unavailable. Step 3.4 accepts `cais/mmlu@c30699e8356da336a370243923dbaf21066bb9fe` only as a provenance-verified mirror; see `MMLU_MIRROR_PROVENANCE_AUDIT.md`. The exact Brier definition is `sum_i (p_i-y_i)^2`, unnormalized multiclass, and the materialized source is validated before execution.
