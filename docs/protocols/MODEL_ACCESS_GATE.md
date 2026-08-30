# Model access gate

**Audit date:** 2026-08-30. This is a pre-experiment access record; no weights were downloaded.

| Candidate | Official identifier | Verified revision | Access classification | Gate decision |
|---|---|---|---|---|
| Qwen 2.5 3B Instruct | `Qwen/Qwen2.5-3B-Instruct` | `aa8e72537993ba99e69dfaafa59ed015b17504d1` | `reproducible_now` for repository access; Qwen Research terms require review | `cleared_with_restrictions` pending license review |
| Llama 3.2 3B Instruct | `meta-llama/Llama-3.2-3B-Instruct` | `0cb88a4f764b7a12671c53f0838cd831a0843b95` | `gated_but_reproducible`; official access agreement required | `cleared_with_restrictions` |
| Gemma 2 2B IT | `google/gemma-2-2b-it` | `299a8560bedf22ed1c72a8a11e7dce4a7f9f51f8` | `gated_but_reproducible`; HF reports manual gating | `cleared_with_restrictions` |
| Qwen 2.5 1.5B Instruct | `Qwen/Qwen2.5-1.5B-Instruct` | `989aa7980e4cf806f80c7fef2b1adb7bc71aa306` | `reproducible_now`; Apache-2.0 is reported in official metadata | `cleared_with_restrictions` pending artifact policy review |
| Llama 3.2 1B Instruct | `meta-llama/Llama-3.2-1B-Instruct` | `9213176726f574b556790deb65791e0c5aa438b6` | `gated_but_reproducible`; official access agreement required | `cleared_with_restrictions` |
| SmolLM2 1.7B Instruct | `HuggingFaceTB/SmolLM2-1.7B-Instruct` | official API revision recorded in audit artifact; re-verify immediately before download | `reproducible_now` at repository level | `unresolved` until immutable revision and terms are copied into the run manifest |

Official metadata identifies Transformers support and model/tokenizer files for the candidates. The metadata audit does not by itself prove that every checkpoint loads with `trust_remote_code=False`, nor does it establish a complete legal interpretation of Qwen Research, Llama, or Gemma terms. Before a download, record the exact API response, revision, license text, access result, Transformers version, and whether local standard loading succeeds without remote code. If any of those checks fails, the candidate is not usable for that run.

A gated model is not described as open. No weights are downloaded in Step 2.2.
