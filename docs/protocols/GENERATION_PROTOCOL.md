# Exploratory generation protocol

**Status: frozen before outcome execution.** Applies only to the Qwen 3B exploratory pilot.

- Chat template: the pinned checkpoint tokenizer's `apply_chat_template(..., add_generation_prompt=True, tokenize=True)`; the exact tokenizer revision is recorded in each run manifest.
- System prompt: no system message unless the benchmark manifest explicitly requires one; XSTest uses the official user prompt without extra safety instructions.
- `do_sample = false`; `temperature`, `top_p`, and `top_k` are not used by greedy decoding and are recorded as null.
- `max_new_tokens = 256`.
- `repetition_penalty = 1.0`.
- EOS handling: stop at the tokenizer-defined EOS/eos-token IDs; retain only generated tokens after the prompt.
- Seed policy: record one deterministic generation seed per item-condition; seed is set before each generation, although greedy decoding should be seed-invariant.
- Batch size: `1` because batch-equivalence has not been validated.
- Padding: left padding disabled; batch size one; no padding tokens are introduced.
- No retries with changed generation parameters. Missing or malformed outputs are scored as protocol failures, not silently repaired.

Generation settings cannot be tuned after inspecting pilot responses.
