# Calibration scoring

For choices `c_1...c_k`, score the complete answer sequence (option text, not assumed single-token labels) under the model tokenizer. For option `i`, with tokens `t_1...t_m`, use `score_i = sum_t log p(t | prompt, previous answer tokens)`. Space-prefixed and multi-token forms are preserved exactly as tokenized. Normalize with a stable log-sum-exp: `p_i = exp(score_i - logsumexp(score))`.

Primary metrics are accuracy (`argmax_i p_i == y`), multiclass Brier score `sum_i (p_i - 1[i=y])^2`, and NLL `-log(p_y)`. Invalid, missing, nonfinite, or tokenizer-inconsistent scores invalidate that item/condition and are reported; they are not imputed or retried with a different scoring representation. Generation decoding parameters are irrelevant to this teacher-forced probability score but the model/template/tokenizer revisions are recorded.
