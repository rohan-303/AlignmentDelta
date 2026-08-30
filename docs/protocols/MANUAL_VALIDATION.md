# Blinded manual validation

Sample a fixed, predeclared stratified subset across model, alpha, intervention, benchmark role, and automated evaluator result, with sampling performed before labels are revealed. Hide automated labels and condition names from the labeler where practical. Labels include refusal/non-answer, substantive answer, harmfulness/operationality under the frozen rubric, benign-answer correctness where applicable, and indeterminate.

One labeler records rationale and uncertainty; disagreements with the automated scorer are retained. If a second labeler is available, both independently label the same blinded subset and report raw agreement plus a chance-adjusted agreement statistic only if its assumptions are met. With one labeler, report this as a blinded audit sample, not inter-rater reliability or evaluator accuracy. No human annotations are fabricated in Step 2.2.
