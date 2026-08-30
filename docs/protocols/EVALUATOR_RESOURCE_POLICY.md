# Evaluator resource policy

PLAN_A is selected: `cais/HarmBench-Llama-2-13b-cls`, cloud-only for confirmatory scoring.

Raw BF16 parameter memory estimates:

- 13B classifier: approximately 26.0 GB (`13,015,864,320 × 2` bytes), before runtime overhead;
- 7B validation classifier: approximately 14.5 GB (`7,241,732,096 × 2` bytes), before runtime overhead.

The local RTX 3060 has approximately 6 GB VRAM and is not feasible for the unquantized 13B classifier. The 7B validation classifier is not adopted for confirmatory primary scoring; no claim is made that it fits locally. Confirmatory use requires a cloud GPU with sufficient memory for the unquantized model and runtime overhead, preferably a documented 40 GB-class allocation.

No throughput or runtime is invented. Quantization is not permitted for confirmatory scoring unless separately validated against the unquantized reference.
