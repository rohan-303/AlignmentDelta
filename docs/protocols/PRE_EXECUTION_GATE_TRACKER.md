# Pre-execution gate tracker

**Audit date:** 2026-08-30. No target weights, evaluation datasets, inference, or scientific measurements were run.

| gate_id | description | evidence required | current state | evidence source | resolution | remaining action |
|---|---|---|---|---|---|---|
| M1 | Primary model exact revision/terms | HF API, pinned metadata, license text | blocked | official HF API/cards; gated endpoints | Qwen metadata/license reviewed; Llama/Gemma access blocked | authenticated access review before use |
| M2 | No-remote-code compatibility for all included models | revision-pinned config/tokenizer load | blocked | Transformers run; HF access errors | Qwen/Smol pass; Llama/Gemma cannot be inspected anonymously | authenticated metadata check or exclude |
| M3 | Meta-device architecture for all included models | config-only empty construction | blocked | Accelerate + Transformers | Qwen/Smol pass; gated families blocked | complete gated-family inspection |
| D1 | Prior direction source pin | immutable repo commit/tree/license | resolved | official GitHub API/repository | pinned at `9d852fae1a9121c78b29142de733cb1340770cc3` | retain provenance in run |
| D2 | Direction data identity and split | source files, blob IDs, counts | resolved | pinned repository tree and loader | train/val/test filenames and available counts/blob IDs recorded; larger-file counts remain a data-stage verification | verify larger-file counts at data stage without staging text |
| D3 | AlignmentDelta leakage-safe source | disjoint source IDs and terms | blocked | prior source + benchmark provenance | source family is identified but exact cross-benchmark overlap audit is not complete | generate/verify item-level manifest before pilot |
| D4 | Executable site score | refusal-only held-out formula | resolved | pinned selector source + project protocol | formula and tie-break frozen | implement/test without primary outcomes |
| S1 | Random-direction null inference | exchangeability analysis | resolved | statistical audit | label permutation removed; sampled-reference/bootstrap plan frozen | implement planned estimator |
| S2 | Confirmatory random-direction count | empirical-null resolution and workload | resolved | exact combinatorial calculation | pilot=4; provisional confirmatory=16 | final precision plan before confirmatory freeze |
| S3 | Multiplicity | predeclared error-control method | resolved | statistical design | Holm FWER selected for three primary families | preserve in analysis config |
| X1 | XSTest exact commit/files/terms | official repo metadata | cleared_with_restrictions | `paul-rottger/xstest` commit/API | commit, file/blob, CC-BY-4.0 recorded | verify intended local-use interpretation |
| H1 | HarmBench exact commit/standard subset | official repo metadata | cleared_with_restrictions | `centerforaisafety/HarmBench` commit/API | commit and official text test file recorded | verify intended local-use interpretation |
| H2 | HarmBench classifier identity/feasibility | official evaluator docs/model metadata | blocked | HarmBench README/evaluation docs | classifier identity known; 13B resource/access gate not cleared | verify revision/terms and provision suitable GPU |
| U1 | MMLU exact revision/terms | official repo commit/files | cleared_with_restrictions | `hendrycks/test` commit/API | repo revision and MIT metadata recorded | pin exact files before data-stage use |
| C1 | Consistency construct | fixed transformations and IDs | resolved | project protocol | deterministic transformations selected | create validated item manifest |
| I1 | Step 3 implementation contracts | inputs/outputs/invariants | resolved | project specifications | contracts created in `docs/implementation/` | implement only after blocked gates close |
| B1 | Target-model weight download | access and storage budget | deferred_by_design | project safety boundary | explicitly prohibited in Step 2.3 | Step 3 only after GO review |
| B2 | Scientific inference/evaluation | all gates and frozen manifests | deferred_by_design | project safety boundary | explicitly prohibited in Step 2.3 | Step 3 only after GO review |

`resolved_with_limits` is descriptive evidence language; the formal tracker state is `resolved` only where the remaining action is administrative/data-stage verification rather than an unknown scientific method. Blocked gates prevent Step 3.0.
