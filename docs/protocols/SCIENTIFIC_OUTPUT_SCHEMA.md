# Sanitized scientific output schema

XSTest records contain `item_id`, `condition_id`, opaque `response_id`, `response_hash`, generation settings/seed, annotation label, and annotation status. Raw response text is protected and ignored.

MMLU records contain `item_id`, `condition_id`, four option log scores, normalized probabilities, predicted answer, gold answer, correctness, Brier, and NLL.

Consistency records contain `pair_id`, `condition_id`, original probabilities, transformed probabilities remapped to canonical order, prediction agreement, and optional predeclared Jensen–Shannon distance. Raw question/options are not tracked. No paper-interpretation fields belong in raw records.
