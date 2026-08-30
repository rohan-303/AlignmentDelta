# HarmBench classifier decision — Step 2.4

Official HarmBench documentation identifies three classifier releases. This audit compares the two relevant text classifiers:

| Model | Revision | Architecture | BF16 parameters | Official role |
|---|---|---|---:|---|
| `cais/HarmBench-Llama-2-13b-cls` | `bda705349d1144fa618770bea64d99ce54e3835b` | `LlamaForCausalLM` | 13,015,864,320 | standard/contextual classifier |
| `cais/HarmBench-Mistral-7b-val-cls` | `51182c7cdaf9b2e5f05b745b81b047b67e7384a1` | `MistralForCausalLM` | 7,241,732,096 | validation classifier |

Both are public and ungated in HF metadata, with MIT metadata and classifier-style Yes/No scoring. The Mistral checkpoint is explicitly a validation classifier. It is rejected as confirmatory primary scoring because its validation role can create development/evaluator-role bias, not because of size.

Selected future plan: **PLAN_A**, the official 13B classifier cloud-only. No classifier weights were downloaded.
