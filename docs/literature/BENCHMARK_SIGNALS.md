# Provisional benchmark signals (not freeze)

| Resource | Measure/size from primary source | Evaluation | Access/license | Cost/limitation |
|---|---|---|---|---|
| HarmBench | Automated red teaming/robust refusal; 18 methods and 33 target LLMs/defenses | Attack generation plus harmfulness/refusal evaluation | Official code; license later verify | Expensive; not general competence |
| StrongREJECT | Forbidden prompts targeting specific harmful information | Automated usefulness-of-harm score with human agreement | Documentation code/data; license later verify | Jailbreak-focused; no calibration/restoration |
| XSTest | 250 safe prompts/10 types and 200 unsafe contrasts | Refusal classification | ACL record/artifacts; license later verify | Compact over-refusal test, not causal |
| OR-Bench | 80,000 over-refusal, ~1,000 hard, 600 toxic prompts | Large-scale refusal measurement | Code/data links; license later verify | Large; no validated competence |
| Utility benchmarks | MMLU/BBH/HumanEval-style tasks named by *Ablating Safety* | Answer or unit-test scoring | Version/license later verify | Generic scores may not be safety competence |
| Calibration tasks | Known-label classification/multiple choice; ACL 2026 uses certainty | Accuracy plus Brier/ECE protocol to define later | Dataset-specific | Self-reported certainty is not automatically probability |
| Robustness/paraphrase | Paired semantic/paraphrase/persona perturbations | Agreement and behavior consistency | Resource-specific | Requires semantic-equivalence checks |

No resource is downloaded or frozen in Step 2.0.
