# ADR-0001: Minimal bootstrap before ML execution

- **Status:** accepted
- **Date:** 2026-08-30

## Decision

Begin AlignmentDelta with a minimal src-layout Python package, lightweight development tooling, research charter, integrity policy, status taxonomy, and explicit directory roles. Defer Torch, Transformers, datasets, model downloads, alignment interventions, and benchmarks to a later execution-foundation milestone.

## Rationale

A small, independently versioned repository makes the scientific scope and audit rules explicit before model or benchmark code can obscure them. Heavy ML dependencies are not needed to validate this bootstrap.

## Consequences

The repository cannot run model experiments yet. That limitation is intentional and must remain visible in the README and charter.
