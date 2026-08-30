# ADR-0004: Freeze literature before model selection

- Status: accepted for Step 2.0
- Date: 2026-08-30

AlignmentDelta’s initial framing overlaps rapidly changing work on refusal mechanisms, uncensored models, safety/utility tradeoffs, and behavioral evaluation. Selecting models or benchmarks first would risk building a novelty claim around convenient resources.

Decision: conduct a structured literature audit before model or benchmark selection. Prefer official proceedings/publisher pages, ACL Anthology, PMLR, OpenReview, then arXiv and official code. Evaluate novelty contribution-by-contribution with explicit threat statuses, not a binary novel/not-novel label.

Treat “uncensored” cautiously: it may describe different post-training histories, community edits, or deployment labels rather than a causal intervention. Keep model-family and benchmark signals separate from later selection and freeze decisions.

Consequence: the audit records metadata, evidence locations, limitations, and provisional gaps. It may drop or narrow ideas. No weights, datasets, inference, transformations, or scientific results are permitted in this stage.
