# Pre-execution gate tracker — Step 2.4

**Audit date:** 2026-08-30. No target-model or evaluator weights, inference, completions, benchmark scoring, or scientific results were produced.

Formal statuses are limited to `resolved`, `blocked`, `deferred_to_engineering_validation`, and `deferred_to_confirmatory_freeze`.

| gate_id | description | evidence required | current state | affects_engineering | affects_confirmatory | evidence source | resolution | remaining action |
|---|---|---|---|---:|---:|---|---|---|
| M1 | Qwen 1.5B exact revision/access/terms | immutable revision and terms | resolved | true | true | HF metadata/model card | revision `989aa7980e4cf806f80c7fef2b1adb7bc71aa306`; Apache-2.0 metadata; metadata access passed | retain terms in run provenance |
| M2 | Llama/Gemma matrix access | authenticated metadata and terms | blocked | false | true | official gated HF endpoints | anonymous access not granted; no credentials bypassed | user must accept official model terms and authenticate through HF before inspection |
| M3 | Qwen no-remote-code compatibility | config/tokenizer load | resolved | true | true | Transformers run | Qwen config/tokenizer passed with `trust_remote_code=False`; no `auto_map` | rerun as Step 3 preflight |
| M4 | Meta architecture validation | config-only construction | resolved | true | true | Accelerate/Transformers | Qwen2 meta construction passed | rerun as Step 3 preflight |
| D1 | Refusal source pin | immutable repo/tree/license | resolved | true | true | GitHub source | commit `9d852fae1a9121c78b29142de733cb1340770cc3`, Apache-2.0 | retain provenance |
| D2 | Direction source files/counts/hashes | materialized source metadata | resolved | true | true | ignored source cache and registry | six files materialized; counts/hashes/IDs recorded | do not stage raw data |
| D3 | Leakage-safe direction split | deterministic role manifest | resolved | true | true | overlap audit/manifests | train-only source files split by sorted IDs at 80/20; source val/test excluded | preserve manifest |
| D4 | Refusal score/tokens | pinned code and tokenizer encoding | resolved | true | true | source code + Qwen tokenizer | epsilon, float64, final-position log-odds, IDs `[40,2121]` frozen | implement/test in engineering |
| D5 | Site selection | executable held-out formula | resolved | true | true | pinned selector + protocol | refusal-only score, KL threshold, pruning, tie-break frozen | implement/test in engineering |
| S1 | Random-control inference | nonexchangeability audit | resolved | true | true | statistical protocol | no ordinary label permutation; cluster bootstrap/reference factor frozen | implement in engineering |
| S2 | Direction counts | workload/resolution calculation | resolved | true | true | statistical protocol | pilot=4; provisional confirmatory=16; precision review required | confirmatory precision freeze |
| S3 | Multiplicity | fixed correction | resolved | false | true | statistical protocol | Holm FWER across three primary families | retain |
| X1 | XSTest source | exact file/hash/count/terms | resolved | false | true | materialized CSV/registry | 450 items; IDs/hash/CC-BY-4.0 recorded | final use-terms check |
| H1 | HarmBench behavior source | exact file/hash/count/terms | resolved | false | true | materialized CSV/registry | official test file has 320 items; IDs/hash recorded | final use-terms check |
| H2 | HarmBench classifier | official identity/validity/terms | resolved | false | true | HF API and HarmBench README | PLAN_A candidate pinned; 13B standard/contextual classifier selected | cloud resource and final terms preflight |
| H3 | HarmBench resource feasibility | sufficient unquantized GPU | blocked | false | true | parameter/storage metadata | local 6GB RTX 3060 unsuitable; cloud allocation not provisioned | obtain documented suitable cloud GPU |
| U1 | MMLU source | official archive/hash/items/terms | blocked | false | true | `hendrycks/test` README + archive URL | archive host timed out; no mirror substituted | retrieve authoritative archive |
| C1 | Consistency transformations | source items and deterministic pair records | blocked | false | true | consistency protocol + MMLU gate | transformation rules frozen; source items unavailable | materialize MMLU, build/validate pair manifest |
| I1 | Step 3 implementation contracts | inputs/outputs/invariants | resolved | true | true | `docs/implementation/` | contracts complete | execute only within Step 3 scope |
| B1 | Target model weights | explicit authorization | deferred_to_engineering_validation | true | false | project safety boundary | permitted only after separate Step 3 authorization | do not download in Step 2.4 |
| B2 | Target inference | explicit authorization | deferred_to_engineering_validation | true | false | project safety boundary | technical checks only after Step 3 authorization | no scientific inference |
| B3 | Confirmatory data collection | all final gates | deferred_to_confirmatory_freeze | false | true | project safety boundary | withheld until confirmatory gates close | no benchmark scoring |

## Readiness result

- `ENGINEERING_GO`: all required engineering gates are resolved.
- `CONFIRMATORY_BLOCKED`: Llama/Gemma access, HarmBench cloud resources, MMLU archive, and consistency artifact remain blocked.

The Step 2.3 blockers remain visible and are classified by readiness impact rather than silently removed.
