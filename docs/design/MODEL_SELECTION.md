# Model selection

## Criteria fixed before selection

A finalist must have: an official/open repository; an exact identifier; an obtainable immutable revision; an instruction/chat checkpoint; standard Transformers loading; exposed residual-stream states; documented safety/refusal behavior sufficient for pilot testing; feasible memory; and license/access terms compatible with the intended research and artifact plan. Manual-gated or nonstandard licenses are access risks, not silently treated as open redistribution permission.

## Verified finalist metadata (Hugging Face API, 2026-08-30)

| Role | Identifier | Revision returned by API | Architecture | Params reported by API | Dtype/storage signal | License/access | Chat/remote-code signal |
|---|---|---|---|---:|---|---|---|
| Primary | `Qwen/Qwen2.5-3B-Instruct` | `aa8e72537993ba99e69dfaafa59ed015b17504d1` | `Qwen2ForCausalLM` | 3,085,938,688 BF16 parameters | BF16; API used storage 6,171,926,992 bytes | `qwen-research`; ungated; terms require review | chat template present; AutoModelForCausalLM; no auto_map returned |
| Primary | `meta-llama/Llama-3.2-3B-Instruct` | `0cb88a4f764b7a12671c53f0838cd831a0843b95` | `LlamaForCausalLM` | 3,212,749,824 BF16 parameters | BF16; API used storage 12,853,298,144 bytes | Llama 3.2 Community License; manual gated | chat template present; AutoModelForCausalLM; no auto_map returned |
| Primary | `google/gemma-2-2b-it` | `299a8560bedf22ed1c72a8a11e7dce4a7f9f51f8` | `Gemma2ForCausalLM` | 2,614,341,888 BF16 parameters | BF16; API used storage 5,288,159,306 bytes | Gemma license; manual gated | chat template present; AutoModelForCausalLM; no auto_map returned |
| Fallback | `Qwen/Qwen2.5-1.5B-Instruct` | `989aa7980e4cf806f80c7fef2b1adb7bc71aa306` | `Qwen2ForCausalLM` | 1,543,714,304 BF16 parameters | BF16; API used storage 10,208,517,569 bytes | Apache-2.0; ungated | chat template present; AutoModelForCausalLM; no auto_map returned |
| Fallback | `meta-llama/Llama-3.2-1B-Instruct` | `9213176726f574b556790deb65791e0c5aa438b6` | `LlamaForCausalLM` | 1,235,814,400 BF16 parameters | BF16; API used storage 4,945,498,882 bytes | Llama 3.2 Community License; manual gated | chat template present; AutoModelForCausalLM; no auto_map returned |
| Fallback | `HuggingFaceTB/SmolLM2-1.7B-Instruct` | `31b70e2e869a7173562077fd711b654946d38674` | `LlamaForCausalLM` | 1,711,376,384 BF16 parameters | BF16; API used storage 47,826,596,336 bytes | Apache-2.0; ungated | chat template present; AutoModelForCausalLM; no auto_map returned |
| Rejected fallback | `microsoft/Phi-3.5-mini-instruct` | `2fe192450127e6a83f7441aef6e3ca586c338b77` | `Phi3ForCausalLM` | 3,821,079,552 BF16 parameters | BF16; API used storage 7,642,681,603 bytes | MIT; ungated | `auto_map`/custom code returned; implementation risk |
| Rejected scale candidate | `mistralai/Mistral-7B-Instruct-v0.3` | `c170c708c41dac9275d15a8fff4eca08d52bab71` | `MistralForCausalLM` | 7,248,023,552 BF16 parameters | BF16; API used storage 28,992,746,844 bytes | Apache-2.0; ungated | standard architecture, but raw BF16 memory exceeds local/cloud-low-budget target |

The parameter counts and storage values above are metadata observations, not measured runtime requirements. “Used storage” can include repository variants and is not treated as raw-weight size.

## Selection decision

The primary matrix is Qwen2.5-3B-Instruct, Llama-3.2-3B-Instruct, and Gemma-2-2B-it. This supplies three genuinely distinct families and prior refusal-direction relevance, subject to access/license gates. The fallback is Qwen2.5-1.5B-Instruct, Llama-3.2-1B-Instruct, and SmolLM2-1.7B-Instruct, all with revisions recorded in `MODEL_FAMILY_SIGNALS`-derived metadata only after a pilot-stage access check.

No weights were downloaded. Final confirmatory eligibility still requires license review, immutable revision retrieval, baseline refusal pilot, and hook validation.
