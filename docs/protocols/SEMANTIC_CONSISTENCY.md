# Semantic consistency design

For the pilot, use a small manually validated paired set assembled from source IDs and controlled variants, not unverified mass-generated paraphrases. Each pair has an original and a meaning-preserving variant, a source rationale, and a validation record. Pair construction is frozen before target-model outcomes; no model performance is used to retain or reject a pair.

Evaluate paired response-category agreement and answer-equivalence where an objective answer exists, separately from refusal and calibration. A pair is excluded only for a predeclared technical failure (template/rendering mismatch, invalid source label, or failed human meaning validation), never because the model disagrees. The pilot establishes pipeline behavior; final pair count and confirmatory manifest remain frozen later under the confirmatory boundary.
