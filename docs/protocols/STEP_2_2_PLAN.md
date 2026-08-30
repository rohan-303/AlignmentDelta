# Step 2.2 plan: close experimental gates and freeze the pilot protocol

## Purpose

Verify the Step 2.1 commit and close access, provenance, leakage, intervention-site, evaluator, and pilot-protocol gates without downloading target-model weights or benchmark data and without running target-model inference.

## Work sequence

1. Recover and verify the Step 2.1 commit and clean tree.
2. Re-query official Hugging Face metadata for all primary and fallback models; classify access reproducibility.
3. Re-check the primary refusal-direction paper and official implementation, separating stated method from code behavior.
4. Freeze direction data partitions, estimator, site selection, random controls, and achieved-dose matching.
5. Resolve XSTest, HarmBench, and utility/calibration source gates; record unclear terms rather than guessing.
6. Define evaluator, manual-validation, pilot manifest, execution order, stopping, output, and confirmatory-freeze protocols.
7. Add integrity checks and validate the repository.

## Scientific invariants

The Step 2.1 primary question, signed projection intervention, matched orthogonal random controls, and primary outcome hierarchy remain unchanged unless a verified technical flaw requires a documented protocol revision.

## Prohibited actions

No model weights, benchmark files, target-model loading, target-model direction extraction, intervention hooks, inference, benchmark scoring, GPU pilot measurements, scientific observations, or paper results.
