# Harmful-output evaluator feasibility — Step 2.4

Selected plan: **PLAN_A — official 13B classifier, cloud-only**.

Model: `cais/HarmBench-Llama-2-13b-cls`, revision `bda705349d1144fa618770bea64d99ce54e3835b`.

The HF metadata reports 13,015,864,320 BF16 parameters and approximately 26.0 GB of raw BF16 parameter memory/storage scale before runtime overhead. The local RTX 3060 has approximately 6 GB VRAM, so unquantized local execution is not feasible. No throughput or runtime estimate is claimed.

Confirmatory use requires a documented cloud allocation with sufficient memory for the unquantized model and runtime overhead; a 40 GB-class GPU is the planning target. Quantization is not allowed for confirmatory scoring unless agreement with the unquantized reference is separately validated.

The 7B Mistral `val-cls` model is not selected as confirmatory primary scoring because it is explicitly a validation classifier. Blinded manual scoring remains a secondary audit, not a silent substitute.
