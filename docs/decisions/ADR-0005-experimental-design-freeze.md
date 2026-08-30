# ADR-0005: freeze experimental design and feasibility plan

- **Status:** Accepted for Step 2.1 draft freeze
- **Date:** 2026-08-30

## Context

Step 2.0 found substantial prior work on refusal manipulation, safety removal, utility retention, and related evaluation. *Ablating Safety* is the primary direct competitor. A broad “remove alignment and measure behavior” claim is not defensible.

## Decision

Freeze a design centered on the dose-response interaction of a refusal-related signed directional projection versus matched orthogonal generic perturbations. Use three architecture families with one exact instruction checkpoint each as the primary matrix, with a smaller fallback matrix. Prioritize safety discrimination, objective calibration, and validated semantic consistency; treat utility and validated harmful capability as secondary/supporting outcomes.

Drop restoration as a headline contribution. A hook-disabled baseline or exact weight restoration is algebraically trivial. Negative signed projection remains a counter-steering condition and may be reported as an exploratory response curve, not as proof of reversibility or restoration.

## Consequences

The design has a stronger causal null and more interpretable null findings, but one checkpoint per family limits generalization. Gated licenses, benchmark terms, evaluator access, actual throughput, and pilot baseline refusal remain explicit gates. No implementation or scientific data collection is authorized by this ADR.
