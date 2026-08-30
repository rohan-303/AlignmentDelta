# ADR-0002: Reproducible ML execution runtime

- **Status:** accepted
- **Date:** 2026-08-30

## Decision

Use `uv` and a locked optional `ml` dependency group for the ML runtime. Resolve PyTorch through the official CUDA 12.6 wheel index rather than treating the NVIDIA driver's reported CUDA capability as the Torch runtime. Keep compute execution profiles separate from scientific experiment configurations. Do not include quantization in the baseline and support the same diagnostic entry point in local and cloud GPU environments.

## Rationale

`uv` is already the project manager and produces a reproducible lockfile. A PyTorch wheel supplies its own compatible CUDA runtime; the driver version and Torch runtime are related but distinct observations. Profiles express operational constraints, while experiments must independently specify scientific conditions. Quantization can change execution behavior and is therefore a recorded confound, not an invisible default. Cloud portability protects against dependence on one local machine. Model downloads are deferred until a protocol, provenance, and evaluation design exist.

## Consequences

The runtime adds substantial dependencies and requires a platform-specific Torch source. The diagnostic must record both driver-side and PyTorch-side information. No model can be evaluated by this milestone.
