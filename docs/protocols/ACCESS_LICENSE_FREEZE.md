# Access and license freeze — Step 2.4

| Asset | Source/revision | Final status | Resolution/remaining condition |
|---|---|---|---|
| Qwen2.5-3B-Instruct | HF `aa8e72537993ba99e69dfaafa59ed015b17504d1` | `cleared_with_restrictions` | metadata/tokenizer verified; Qwen research terms and attribution apply |
| Qwen2.5-1.5B-Instruct | HF `989aa7980e4cf806f80c7fef2b1adb7bc71aa306` | `cleared_with_restrictions` | Apache-2.0 metadata; engineering target; terms remain recorded in provenance |
| Llama-3.2-3B-Instruct | HF `0cb88a4f764b7a12671c53f0838cd831a0843b95` | `blocked` | gated access not granted; config/tokenizer and full terms review not completed |
| Gemma-2-2B-it | HF `299a8560bedf22ed1c72a8a11e7dce4a7f9f51f8` | `blocked` | gated access not granted; direct terms review required |
| Qwen2.5-1.5B-Instruct fallback role | HF `989aa7980e4cf806f80c7fef2b1adb7bc71aa306` | `cleared_with_restrictions` | same checkpoint is engineering target, not a replacement paper family |
| Llama-3.2-1B-Instruct | HF `9213176726f574b556790deb65791e0c5aa438b6` | `blocked` | gated access not granted |
| SmolLM2-1.7B-Instruct | HF `31b70e2e869a7173562077fd711b654946d38674` | `cleared_with_restrictions` | metadata/config/tokenizer verified; official terms remain recorded |
| Refusal-direction source | `andyrdt/refusal_direction` `9d852fae1a9121c78b29142de733cb1340770cc3` | `cleared_with_restrictions` | Apache-2.0; source data cached outside Git and not redistributed |
| XSTest | `paul-rottger/xstest` `d7bb5bd738c1fcbc36edd83d5e7d1b71a3e2d84d` | `cleared_with_restrictions` | CC-BY-4.0 metadata; local manifest recorded; redistribution not assumed |
| HarmBench behavior source | `centerforaisafety/HarmBench` `8e1604d1171fe8a48d8febecd22f600e462bdcdd` | `cleared_with_restrictions` | behavior files hashed outside Git; evaluator terms separate |
| HarmBench 13B classifier | `cais/HarmBench-Llama-2-13b-cls` `bda705349d1144fa618770bea64d99ce54e3835b` | `blocked` | PLAN_A selected; cloud resource and final execution preflight required |
| HarmBench 7B validation classifier | `cais/HarmBench-Mistral-7b-val-cls` `51182c7cdaf9b2e5f05b745b81b047b67e7384a1` | `cleared_with_restrictions` | metadata verified; not confirmatory primary because it is a validation classifier |
| MMLU | `hendrycks/test` `4450500f923c49f1fb1dd3d99108a0bd9717b660` | `blocked` | official archive host timed out; no mirror substituted |
| Consistency artifact | project manifest based on MMLU IDs | `blocked` | transformation rules frozen; source item IDs unavailable |

AlignmentDelta does not redistribute third-party model weights. Derived scores and local data use remain subject to the applicable terms and institutional review; this is not legal advice.
