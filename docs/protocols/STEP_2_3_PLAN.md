# Step 2.3 implementation/research plan

## Purpose

Resolve every Step 2.2 open gate that can be resolved without target-model weight downloads, target-model inference, benchmark execution, direction extraction from real weights, or scientific observations. Any gate that cannot be resolved from official metadata/source inspection is retained as `blocked`, with a predeclared replacement or explicit Step 3 prerequisite.

## Gate-by-gate approach

| Step 2.2 issue | Resolution method | Evidence source | Metadata-only? | Expected disposition/files |
|---|---|---|---|---|
| Model revision, config, tokenizer, architecture, chat template, and custom-code metadata | Re-query official Hugging Face API and revision-pinned metadata files | Hugging Face official API/model repositories | Yes; config/tokenizer metadata allowed | Resolve or block per candidate; update model registry and gate tracker |
| Model license and access terms | Read official LICENSE/model-card terms; distinguish research use, publication, redistribution, and attribution | Official model cards and license files | Yes | Record restrictions; no legal guarantee; update access/license freeze |
| `trust_remote_code=False` compatibility | Use revision-pinned `AutoConfig` and `AutoTokenizer` only; do not call `AutoModel` | Installed Transformers plus official metadata files | Yes, with tokenizer/config retrieval | Resolve accessible candidates; mark gated candidates blocked if authentication prevents inspection |
| Meta-device architecture compatibility | Construct config-only empty architecture with `accelerate.init_empty_weights` where access allows | Installed Transformers/Accelerate and official config | Yes; no real parameter materialization | Create architecture inspection record and adapter specification |
| Refusal-direction source pin | Resolve official repository, immutable commit, source files, and license | Paper, official code repository, GitHub commit/tree/API | Yes | Freeze source provenance and method-difference table |
| Direction datasets/counts/splits/formatting | Inspect pinned code/data metadata and source manifests; do not copy prompt text | Official refusal-direction repository/data metadata | Yes | Resolve only ascertainable fields; block unknowns rather than infer |
| AlignmentDelta direction source | Select a traceable, non-overlapping source or keep blocked if source terms/IDs cannot be verified | Pinned prior source and official benchmark metadata | Yes | Freeze source manifest specification without prompt text |
| Direction split | Define deterministic ID-sort plus seeded split independent of outcomes | Project protocol | Yes | Resolve algorithm; exact IDs remain data-stage artifact |
| Site score | Use a refusal-only held-out score with executable formula and fixed tie-break | Paper/code audit plus protocol decision | Yes | Freeze technical score; no primary outcomes |
| Random-control inference | Audit exchangeability; replace invalid label permutation if necessary | Statistical reasoning and protocol | Yes | Create random-control statistics protocol; update statistical freeze |
| Number of random directions | Compare 4/8/16/32 using workload and empirical-null resolution only | Combinatorial calculation | Yes | Freeze pilot count and provisional confirmatory count |
| Multiplicity | Compare Holm, BH, and hierarchical procedures for three primary families | Statistical design reasoning | Yes | Freeze one procedure without outcome dependence |
| XSTest | Pin repository commit/files/IDs/terms from official source without running prompts | Official GitHub repository and paper | Yes | Clear with restrictions or block with replacement |
| HarmBench | Pin standard behavior files/categories/terms without inference | Official GitHub repository/source | Yes | Clear with restrictions or block |
| HarmBench classifier | Identify exact model/revision/architecture/size/dtype/template/scoring from official code | Official HarmBench implementation/model metadata | Yes | Resolve identity; feasibility remains theoretical until permitted execution |
| Harmful-output evaluator feasibility | Compare raw weight-memory bounds and documented requirements; no runtime claims | Official evaluator metadata and project hardware record | Yes | Select official, alternative, manual, or unresolved |
| MMLU | Pin repository commit/files/split/labels/terms without using items in a model | Official MMLU repository | Yes | Clear with restrictions or block |
| MMLU pilot selection | Freeze deterministic subject/item procedure independent of performance | Project protocol | Yes | Resolve algorithm; IDs generated only in pilot stage |
| Semantic consistency | Compare manual pairs with deterministic meaning-preserving transformations | Existing project protocol and reproducibility criteria | Yes | Freeze the least-confounded construct and pair rule |
| Step 3 contracts | Write input/output/invariant/error/provenance contracts | Project design and prior protocols | Yes | Create implementation specifications |

## Files expected

- `docs/protocols/PRE_EXECUTION_GATE_TRACKER.md`
- updated `docs/protocols/ACCESS_LICENSE_FREEZE.md`
- updated `docs/protocols/DIRECTION_ESTIMATION.md`, `SITE_SELECTION.md`, and `STATISTICAL_FREEZE.md`
- benchmark gate records under `docs/protocols/benchmarks/`
- `docs/protocols/RANDOM_CONTROL_STATISTICS.md`
- `docs/protocols/CONSISTENCY_PAIR_RULE.md`
- `docs/implementation/ARCHITECTURE_ADAPTER_SPEC.md`
- `docs/implementation/MODEL_LOADING_SPEC.md`
- `docs/implementation/RESIDUAL_CAPTURE_SPEC.md`
- `docs/implementation/DIRECTION_ARTIFACT_SPEC.md`
- `docs/implementation/INTERVENTION_OPERATOR_SPEC.md`
- `docs/implementation/CONTROL_DIRECTION_SPEC.md`
- `docs/implementation/PILOT_RUNNER_SPEC.md`
- `docs/implementation/METHOD_DIFFERENCE_TABLE.md`
- `docs/implementation/DIRECTION_ARTIFACT_SCHEMA.md`
- lightweight tests for synthetic/non-scientific contracts.

## Validation strategy

Run full pytest, Ruff, mypy, package build, dependency checks, `git diff --check`, secret scan, model-weight scan, benchmark-data scan, and results-directory hygiene. Review staged file names and complete staged diff before a separate Step 2.3 commit. Verify `SHIFT-ICD` status and HEAD independently.

## Prohibited work

No target-model weight shards, benchmark evaluation data, target-model inference, real direction extraction, intervention execution, harmful generated text, benchmark scoring, pilot measurements, scientific observations, confirmatory experiments, or paper results will be created in Step 2.3.
