# Benchmark licensing and access audit

| Candidate | Primary source checked | License/terms finding | Evaluator/access finding | Decision |
|---|---|---|---|---|
| XSTest | ACL Anthology/paper and official project record | Dataset redistribution terms not clearly established by the inspected record | Requires deterministic refusal/answer scoring protocol | Primary boundary benchmark, pending terms check |
| HarmBench | Official `centerforaisafety/HarmBench` README | README describes the framework but does not itself state a dataset license; unclear | Standard classifier is an additional HF model; local Transformers path exists; revision/access must be pinned | Primary harmful benchmark, pending terms/classifier check |
| StrongREJECT | Official documentation | Documentation lists mixed upstream sources, including no-license inputs; redistribution is not assumed | Rubric evaluator requires an external LLM/API; fine-tuned evaluator requires gated Gemma access | Optional sensitivity analysis only |
| OR-Bench | Official `justincui03/or-bench` README | License not clearly stated in inspected README; unclear | Official workflow uses API-based generation, rewriting, moderation, and response checking | Not primary |

No benchmark was downloaded. “Primary” means selected for protocol design, not cleared for redistribution. Before Step 3, record exact dataset revision, item manifest, license/terms, evaluator revision, and whether raw inputs/outputs may be stored or released. If any remains unclear, use local derived artifacts only or replace the benchmark before confirmatory freeze.
