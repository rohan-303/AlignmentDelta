# ADR-0007: Restrict engineering scorer batches after padding probe

- **Status:** accepted for Step 3.0 engineering validation
- **Date:** 2026-08-30
- **Decision:** The engineering runner uses batch size 1 for validation inputs. Batched technical scorer checks use duplicated equal-length, unpadded inputs. The frozen scorer continues to read the final sequence position (`-1`).

## Evidence

A real pinned Qwen run compared two validation inputs independently and in a left-padded batch. The left-padded batch changed the final-token refusal score, with a maximum absolute difference of approximately 0.0779. A duplicated equal-length unpadded batch matched the corresponding single-item score within an explicit engineering tolerance of 2e-3; the observed maximum difference was approximately 0.001585. The left-padded discrepancy remained approximately 0.0779.

## Consequence

The runner does not silently treat left-padding as score-equivalent for this model/runtime. Variable-length padded batches are not used for engineering scorer validation. This is a technical execution constraint, not a scientific result or benchmark claim.
