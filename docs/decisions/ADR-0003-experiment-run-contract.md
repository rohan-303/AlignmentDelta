# ADR-0003: auditable experiment run contract

- **Status:** Accepted for Step 1.2
- **Date:** 2026-08-30

## Decision

Separate scientific condition identity from concrete execution identity. Experiment TOML describes the condition; a stable SHA-256 condition ID identifies that condition; each execution receives a new timestamp-plus-UUID run ID and a separate run manifest.

Use a small typed standard-library implementation rather than a database or workflow framework. Manifests are written with a temporary file, flush, `fsync`, and atomic replacement. Status transitions are explicit and fail closed; failed runs are terminal. Completed runs may later be invalidated with a preserved reason.

Pilot and confirmatory phases remain distinct because debugging and runtime exploration must not silently become evidence under a frozen protocol. This infrastructure is implemented before model experiments so future observations can be traced to configuration, code, environment, and execution without relying on memory or directory names.

## Consequences

Condition IDs remain stable across TOML formatting and machine changes, while run manifests capture machine-specific provenance. No database is needed at this stage. The current protocol is draft (`0.1-draft`) and no scientific run is created by this ADR or Step 1.2.
