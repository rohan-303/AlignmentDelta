# Step 2.3 GO/NO-GO decision

**Decision: BLOCKED**

Step 2.3 resolved the implementation methodology that can be frozen without experiments, including model metadata for accessible candidates, the refusal-direction source pin, deterministic split rule, refusal-only site score, random-control statistics, multiplicity, architecture adapters, artifact schemas, and pilot target/budget.

Step 3.0 remains blocked by the following core gates:

1. Llama 3.2 and Gemma 2 config/tokenizer compatibility and full license/use-policy review require authenticated access; anonymous metadata retrieval returned the official restricted-access error.
2. The official HarmBench classifier is `cais/HarmBench-Llama-2-13b-cls`; its exact evaluator revision/terms and resource-feasible execution path are not closed. Raw BF16 memory arithmetic is approximately 26 GB before overhead, and no runtime/OOM test is authorized here.
3. Exact item-level overlap and terms checks between the pinned refusal-direction source and all future primary evaluation manifests must be performed when source manifests are materialized. This cannot be honestly completed from repository metadata alone.
4. The consistency source requires validated item records before it can become a cleared pilot artifact.

The first engineering target is specified as Qwen2.5-1.5B-Instruct, but selecting an engineering target does not authorize model-weight download or target inference. No claim of scientific readiness, evaluator accuracy, model behavior, or publication validity follows from this decision.
