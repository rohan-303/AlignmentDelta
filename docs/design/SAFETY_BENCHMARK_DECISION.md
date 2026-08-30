# Safety benchmark decision

## Decision

Use **XSTest** for benign-boundary/over-refusal discrimination and **HarmBench standard behaviors** for harmful-request refusal/compliance, with no automatic red-team generation. This is the minimum selected pair that covers the two required safety dimensions without running all four candidate suites.

XSTest's established safe and unsafe prompt distinctions are directly relevant to exaggerated safety. HarmBench supplies a standardized harmful-behavior framework and an official open-source evaluation pipeline with a Transformers-compatible path. HarmBench's classifier model is a separate artifact and must be version-pinned and evaluated for access before use.

## Candidates reviewed

- **StrongREJECT:** useful harmfulness rubric and fine-tuned evaluator options, but the official documentation exposes an API-dependent rubric evaluator and a gated Gemma-based evaluator; source datasets include mixed licensing, including no-license inputs. Retain as an optional sensitivity analysis, not a primary dependency.
- **OR-Bench:** directly targets over-refusal, but the official repository workflow generates/rewrites prompts with external APIs and uses model-based moderation/checking. This adds an avoidable evaluator and provenance dependency; do not make it primary.
- **XSTest:** selected for boundary discrimination; exact release revision and redistribution terms remain an access/license gate.
- **HarmBench:** selected for harmful behavior; use only its fixed standard behavior set, not generated attacks, to keep workload and exposure bounded.

## Scoring rules

- Harmful prompts: distinguish refusal from substantive assistance; report evaluator uncertainty and never call willingness “capability” without an objective validator.
- Benign prompts: score answerability/appropriate assistance, not merely non-refusal.
- Use the same prompt formatting, generation limits, and evaluator version across alpha and control conditions.

No benchmark files were downloaded. Dataset sizes, revisions, and license permissions remain recorded as verification gates rather than guessed values.
