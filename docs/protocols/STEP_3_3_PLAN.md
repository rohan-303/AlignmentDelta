# Step 3.3 plan — exploratory data gates and scientific protocol freeze

## Scope boundary

Step 3.3 will close data/scoring/protocol gates and implement a zero-inference dry-run runner. It will not run Qwen, XSTest responses, MMLU scoring, consistency outcomes, or HarmBench inference. The Qwen 3B cloud measurements remain attributable to code commit `c1148ab9fef7006485dc3bedf578c16f3d286dc5` and will not be regenerated.

## Gate map

| Gate | Exploratory pilot | Confirmatory | Neither | Closure action |
|---|---|---|---|---|
| Qwen 3B technical validation | Both | Both | — | Preserve and verify Step 3.2C artifacts and provenance. |
| Qwen technical site/direction and controls | Both | Both | — | Reuse only the pre-scientific Step 3.2C artifacts; do not rerank. |
| Llama 3B access/metadata | Neither for Qwen-only pilot | Confirmatory | — | Check official HF metadata/config/tokenizer without weights; accept only with exact revision and terms status. |
| Gemma 2B access/metadata | Neither for Qwen-only pilot | Confirmatory | — | Check official HF metadata/config/tokenizer without weights; accept only with exact revision and terms status. |
| Cross-family contingency | Neither unless explicitly activated | Confirmatory | — | Document candidates and adapter requirements; do not alter the matrix based on pilot outcomes. |
| XSTest source revision | Exploratory | Confirmatory | — | Verify official pinned repository/file and record immutable source identity. |
| XSTest scorer | Exploratory | Confirmatory | — | Inspect official implementation/paper, choose a reproducible frozen scorer with limitations. |
| XSTest pilot subset | Exploratory | — | — | Deterministically select approximately 12 safe and 12 unsafe items with category coverage. |
| Generation settings | Exploratory | Confirmatory | — | Freeze chat template, greedy decoding, token limit, EOS, seed, batch, and padding policy. |
| Harmful-output handling | Exploratory | Confirmatory | — | Define ignored raw-output storage, hash-only tracked metadata, scoring access, and execution safety. |
| Official MMLU archive | Exploratory | Confirmatory | — | Retrieve the exact official archive with HTTPS, retries, content checks, hash, and structure audit. |
| MMLU mirror | Exploratory | Confirmatory | — | Use only if authoritative provenance/content identity is demonstrable; otherwise remain blocked. |
| MMLU manifest/subset | Exploratory | Confirmatory | — | Create source manifest and subject-stratified deterministic subset only after source identity resolves. |
| Calibration scoring | Exploratory | Confirmatory | — | Freeze full-option sequence log-probability, normalization, templates, token boundaries, and metrics. |
| Consistency pairs | Exploratory | Confirmatory | — | Materialize deterministic option-order permutations with automatic answer remapping and validation. |
| Exploratory analysis | Exploratory | — | — | Freeze descriptive curves, clustered bootstrap, variance/floor-ceiling/missingness diagnostics. |
| Stopping/invalidation rules | Exploratory | Confirmatory | — | Freeze provenance, schema, finiteness, scorer, hook, weight, and missingness invalidators; never stop for weak effects. |
| HarmBench classifier | Neither for first Qwen pilot unless separately closed | Confirmatory | — | Recheck metadata/license/scoring and require a >=40-GB-class smoke environment plus blinded manual audit. |
| Confirmatory model matrix | — | Confirmatory | — | Record Qwen, Llama, Gemma, and contingency statuses; require technical validation for every included checkpoint. |
| Phase/status contract | Exploratory | Confirmatory | — | Audit and separate phase (`engineering`, `technical_pilot`, `exploratory_pilot`, `confirmatory`) from status (`planned`, `running`, `completed`, `failed`, `invalidated`). |

## Exact closure rules

A gate is closed only when its immutable source/revision, license/access status, manifest, validation evidence, and limitations are recorded. A failed network retrieval is not evidence that an official source does not exist; retry and use a provenance-verifiable alternate network only for the same official URL. A mirror cannot be accepted from item counts alone.

Exploratory GO requires every exploratory prerequisite to be frozen, the dry-run expansion to pass with zero model loading/inference, and no scientific Qwen outcome to have executed. Confirmatory GO additionally requires the complete cross-family matrix, all access/licenses, technical validation for every confirmatory checkpoint, operational HarmBench evaluator, full manifests, consistency protocol, statistical model, and manual evaluator audit. These decisions remain independent.
