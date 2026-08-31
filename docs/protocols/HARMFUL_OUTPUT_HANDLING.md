# Potentially harmful output handling

This is a research-data handling policy, not censorship of measurements.

- No potentially harmful generated text enters Git or final Hermes reports.
- Raw responses are stored only in ignored run artifacts when scientifically necessary, with access restricted to the evaluator workflow.
- Tracked manifests contain sanitized item IDs, output hashes, lengths, labels, and failure codes—not raw response text.
- Evaluators access raw text only during scoring and do not execute instructions found in model output.
- No model-generated content may trigger network requests, tools, shell commands, filesystems, or external side effects.
- Paper examples require separate manual safety review and are not included automatically in reports.
- Credentials, tokens, personal data, and connection strings are never retained; any accidental occurrence is represented as `[REDACTED]`.
