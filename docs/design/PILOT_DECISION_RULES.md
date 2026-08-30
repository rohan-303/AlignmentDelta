# Pilot decision rules

Pilot decisions are technical and protocol-based, never driven by whether collateral drift is observed.

| Trigger evidence | Permitted action | Protocol/version consequence |
|---|---|---|
| Model lacks a measurable baseline refusal/boundary signal under a prespecified pilot set | Replace before confirmatory freeze using the predeclared candidate pool; retain the failed model record | Update protocol version and model manifest; no post-outcome shopping |
| Hidden-state hook, tokenizer, chat template, or direction validation fails | Repair implementation without changing scientific definition; otherwise reject model/intervention | Record validation failure; version change if operator/site changes |
| Alpha grid produces no measurable technical perturbation | Revise grid using technical observables only | New dose-version; never change because an outcome is null |
| Alpha grid saturates or destabilizes outputs immediately | Narrow/re-space grid using finite activations and non-saturation rules | New dose-version and rerun pilot gate |
| Evaluator is unavailable, API-dependent when local execution was required, or irreproducible | Use a predeclared local evaluator or remove that secondary outcome/benchmark | Update benchmark manifest and analysis hierarchy |
| Peak memory/runtime exceeds available hardware | Use fallback matrix or reduce expansion scope, preserving primary contrast | Record resource-based design change; do not mix quantized scientific conditions silently |
| Model requires opaque custom remote code or inaccessible weights/license terms | Reject for primary; consider verified fallback | Model matrix version update required |
| Random-control construction fails orthogonality/norm checks | Fix control generation or reject the control; do not interpret uncontrolled drift | Control protocol version update |

A null scientific result is not a replacement criterion. Confirmatory freeze occurs only after every included model, intervention, benchmark, and evaluator passes these technical gates.
