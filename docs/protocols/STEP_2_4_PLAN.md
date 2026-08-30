# Step 2.4 plan — close data/evaluator gates and authorize engineering pilot

## Scope

Step 2.4 is a pre-execution gate-closing milestone. It may materialize pinned source data outside Git for hashes, IDs, manifests, and overlap checks. It must not download target-model or evaluator weights, run inference, extract a real direction, execute benchmarks, or create scientific results.

## Step 2.3 blockers and resolution plan

| Blocker | Resolution/evidence | Engineering impact | Confirmatory impact | Files | Validation |
|---|---|---:|---:|---|---|
| Llama/Gemma gated metadata and terms | Check non-secret HF authentication state; if absent record `access_not_granted`; if present run config/tokenizer checks with `trust_remote_code=False` | false | true | readiness/tracker/model audit | no token output; no weights |
| HarmBench classifier access/resource feasibility | Reinspect official classifier collection, 13B and 7B metadata, revisions, templates, terms, and validation-role implications | false for Qwen engineering | true | evaluator protocols | metadata-only, arithmetic only |
| Direction/evaluation item overlap | Materialize permitted source files outside Git; hash, canonicalize, compare exact normalized text and stable IDs without echoing text | false for technical Qwen checks | true | audit artifacts/manifests | machine-readable counts and hashes |
| Consistency artifact absent | Build deterministic option permutations and wrapper variants from source IDs; validate mappings without model outputs | false | true | consistency manifest/protocol/tests | deterministic synthetic/source-ID tests |
| Larger source-file counts/hashes not materialized | Download only permitted source data files to ignored cache and register metadata | false | true | source registry/manifests | SHA-256 and count reconciliation |

## Engineering readiness work

1. Reconfirm Qwen 1.5B revision, access/terms, config/tokenizer behavior, architecture, and budget.
2. Freeze refusal score and Qwen refusal-token construction without optimizing on model outcomes.
3. Freeze the Step 3 engineering-only scope.
4. Update readiness tracker with engineering/confirmatory impact.

## Confirmatory readiness work

1. Build source-only manifests and overlap summaries.
2. Re-evaluate XSTest, HarmBench, MMLU, evaluator, and consistency gates.
3. Preserve `CONFIRMATORY_BLOCKED` if any required paper-data gate remains blocked.

## Expected files

- `docs/protocols/STEP_2_4_PLAN.md`
- `docs/protocols/READINESS_LEVELS.md`
- updated `PRE_EXECUTION_GATE_TRACKER.md`, `SITE_SELECTION.md`, and related protocols
- `docs/protocols/SOURCE_DATA_FILE_REGISTRY.md`
- `docs/protocols/REFUSAL_SCORE.md`
- `docs/protocols/ITEM_OVERLAP_AUDIT.md`
- `docs/protocols/CONSISTENCY_ARTIFACT_VALIDATION.md`
- `docs/implementation/STEP_3_SCOPE.md`
- `configs/manifests/*.toml`
- non-sensitive summaries under `artifacts/data_audit/`
- Step 2.4 integrity tests

## Validation

Run deterministic manifest and overlap tests, full pytest, Ruff, mypy, package build, dependency check, `git diff --check`, secret/model-weight/results scans, and protected-repository verification. Source-data caches must remain outside Git and unstaged.

## Explicit stop boundary

Even with `ENGINEERING_GO`, Step 2.4 ends before target-model weight download, target inference, real direction extraction, intervention execution, benchmark scoring, scientific observations, or paper results.
