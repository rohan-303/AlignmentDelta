# Step 4.0B — Real Qwen Cloud Scientific Adapter Plan

## Scope

Complete the real cloud execution path while preserving the existing uncommitted Step 4.0A work. Local validation remains model-free: no Qwen download, model load, benchmark item, scientific outcome, or HarmBench execution.

## Implementation sequence

1. Add lazy cloud-only model loading with exact model/revision, CUDA/BF16/VRAM/disk gates, clean-Git provenance, architecture checks, snapshot/tokenizer hashes, and sentinel weight integrity.
2. Reuse the validated direction and control algorithms; add cloud reconstruction, cache verification, exact direction/control hashes, and pre-science technical smoke.
3. Add real XSTest generation, MMLU option-sequence scoring, consistency remapping/scoring, hook lifecycle cleanup, and protected raw/sanitized separation.
4. Add master-run initialization, protocol hash locks, deterministic chunking, progress/resume/failure semantics, atomic writes, and both export modes.
5. Add mocked integration tests for every real-adapter boundary and static-audit the `--execute` control flow to ensure it reaches real adapter code rather than a placeholder.
6. Run only dry-run, synthetic, mocked, static, and quality validation locally. Do not run `--execute` or `--technical-smoke` locally.
7. Commit and push only if every readiness criterion passes and no essential real path remains incomplete.

## Safety invariants

- Real execution requires `--execute --profile cloud_gpu`.
- Dry-run and synthetic paths import no Qwen model frameworks or weights.
- Direction/control hash mismatch stops before benchmark items.
- Original Step 3.2C artifacts remain immutable.
- `SHIFT-ICD` remains untouched.

## Current status

Implemented and locally validated: lazy pinned Qwen loader, cloud preflight, clean-Git provenance, source hydration entry point, layer-27 direction reconstruction primitive, exact direction/control gates, temporary hooks, sentinel integrity, benign technical-smoke primitive, CLI wiring, and execution-flow documentation.

Still blocked before release: end-to-end benchmark orchestration, master-run initialization, real durable progress/resume integration, schema-validated sanitized records, and sanitized/sensitive archive exporters. No commit or push is authorized.
