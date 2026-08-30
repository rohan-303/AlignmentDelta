# HarmBench classifier comparison

| Classifier | HF revision | Architecture | BF16 parameters | Official role | Final use |
|---|---|---|---:|---|---|
| `cais/HarmBench-Llama-2-13b-cls` | `bda705349d1144fa618770bea64d99ce54e3835b` | `LlamaForCausalLM` | 13,015,864,320 | standard/contextual classifier | PLAN_A, cloud-only confirmatory candidate |
| `cais/HarmBench-Mistral-7b-val-cls` | `51182c7cdaf9b2e5f05b745b81b047b67e7384a1` | `MistralForCausalLM` | 7,241,732,096 | validation classifier | rejected as confirmatory primary |

Both are public, ungated HF repositories with MIT metadata. The Mistral model is explicitly a validation classifier; selecting it as confirmatory primary scoring would risk development/evaluator-role bias. It is not selected merely because it is smaller.

Both use classifier-style text generation with Yes/No scoring in the official HarmBench workflow. No classifier weights were downloaded.
