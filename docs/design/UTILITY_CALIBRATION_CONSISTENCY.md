# Utility, calibration, and consistency design

## Utility/calibration task

Use a compact, fixed multiple-choice subset from an established known-answer benchmark, with final dataset and license selection completed before pilot freeze. MMLU is the leading candidate because it supplies objective multi-choice correctness, but its exact release/license terms must be verified before redistribution or use. No benchmark is silently treated as cleared.

For an item with valid options A–D, compute each option's sequence log-probability under teacher forcing, normalize across the four valid option strings, and use the probability of the correct option as confidence. Correctness is exact option identity. Brier score, NLL, and accuracy then come from the same prediction; verbal self-confidence is not required.

## Selection constraints

- fixed subject/item manifest and revision;
- no training overlap checks where feasible;
- same prompt template across models;
- no chain-of-thought requirement;
- enough items for item-level uncertainty, without freezing a count before the release is verified.

## Consistency

Construct paired variants only from an established paraphrase/pair source or a frozen template-controlled transformation protocol. Human or separately validated review must establish semantic equivalence and preserve answerability. Do not generate thousands of unverified LLM paraphrases. Primary statistic is within-pair category agreement; probability/answer agreement is secondary.
