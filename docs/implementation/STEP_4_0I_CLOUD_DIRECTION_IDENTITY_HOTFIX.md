# Step 4.0I — cloud direction-identity hotfix

**Status:** implementation pending local and fresh-cloud validation.

## Trigger

The Step 4.0H released cloud technical-smoke gate loaded the pinned Qwen checkpoint but stopped before any benchmark task with `DIRECTION_RECONSTRUCTION_MISMATCH`.

## Verified remote diagnostic

Environment: one NVIDIA RTX 4090, released commit `5813525c14b7807b5877a6ecdd2e0bd441b09101`, pinned Qwen revision `aa8e72537993ba99e69dfaafa59ed015b17504d1`, pinned hydrated sources. Two independent reconstruction runs produced the same finite, unit-normalized 2,048-dimensional direction:

- direction SHA-256: `286147ed00c828028d6856e5cab4e87ed5730e1e2f6f6fff047f2d3bb71a84b1`
- control SHA-256 values:
  - `20260830`: `baea625387eee599d64fc5cc36ba19347908bb8ee89843dd5c51ccfa77c4e1dd`
  - `20260831`: `8a2bddd84b3e61e713e47b7cd22b78c9013b6316fca3eb9df65feed53955f6f9`
  - `20260832`: `381c985be766eb3b416b5fb49efba17e7de92f01d21131d4c85f29132537864a`
  - `20260833`: `120d1b40884bf919536f6fea3d653f6ecd5f133e30d43b9b2263ddaf6eba4984`

## Repair

Replace only stale strict expected identity constants in the cloud adapter and execution engine. Preserve the identity gates and add a regression assertion for the verified direction hash.

## Boundary

The failed technical-gate attempts produced no benchmark responses, scores, or scientific outcomes. The next fresh-cloud technical smoke must pass before any `--execute` task is considered.
