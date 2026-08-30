# HarmBench classifier findings

Official HarmBench documentation identifies:

- model ID: `cais/HarmBench-Llama-2-13b-cls`;
- official API revision observed: `bda705349d1144fa618770bea64d99ce54e3835b`;
- architecture metadata: `LlamaForCausalLM`, model type `llama`;
- six safetensors shards and tokenizer/config files;
- repository/API license metadata: MIT;
- official notebook dtype: bfloat16;
- official prompt: Llama-2 `[INST]` classifier prompt with behavior and generation fields;
- scoring: deterministic generation of one token, interpreted as `Yes`/`No`.

The model is described by HarmBench as a Llama-2 13B classifier. The exact parameter count is not independently read from the config in this audit; the model name supplies the approximate 13B label but is not treated as a precise count. Raw BF16 weight memory is therefore recorded as an estimate of approximately `13e9 * 2` bytes before overhead, not a measured footprint. The official docs require sufficient GPU resources and show a GPU-oriented workflow.

No classifier weights were downloaded. Local RTX 3060 feasibility is blocked: raw-memory arithmetic alone does not establish fit, and no runtime/OOM test is authorized in Step 2.3. Exact classifier terms, dependencies beyond the official requirements, and revision-pinned tokenizer/config checks remain pre-execution gates.
