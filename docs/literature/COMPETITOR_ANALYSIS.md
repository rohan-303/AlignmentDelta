# Direct competitor analyses

## Ablating Safety

| Dimension | Prior work | AlignmentDelta proposed after audit |
|---|---|---|
| Domains/tasks | Authorized cybersecurity: vulnerability triage, patch analysis, secure repair; 60-prompt Security-AR | Must not claim generic task scope; use a distinct question or domain only if justified |
| Models/families | Four-model projection pilot including Qwen2.5 and SmolLM2; three Qwen2.5 LoRA checkpoints | Cross-family interaction is a possible differentiator, not a selection decision |
| Transformations | Prompt baseline, refusal-direction projection, rank-4 subspace, representation controls, LoRA | Avoid reproducing this menu without a new causal purpose |
| Strength | Alpha `{0,.5,1,1.5,2}` and rank sweeps | Prior work already establishes a dose signal; any extension needs normalized, uncertainty-aware curves |
| Refusal/unsafe compliance | Both separated and reported | Already overlapping |
| Attempt/validated success | Explicitly separated; secure-repair validators | Already overlapping |
| Utility | General score and authorized security score | Already overlapping |
| Calibration | Not reported in inspected abstract/full sections | Potential dimension, but ACL 2026 studies calibration in a different deployed comparison |
| Robustness | Instability/robustness and seed/subset checks | Already overlapping at a broad level |
| Cross-family design | Pilot across four models, LoRA across three Qwen checkpoints | A full cross-family response-curve interaction may remain open |
| Reversibility | Activation intervention is reversible as an inference path | Collateral restoration is not established |
| Statistics | Prompt-bootstrap intervals and limited seeds | Any successor needs stronger pre-specified inferential design |

**Assessment:** overlap is severe for C1–C5 and C8. AlignmentDelta should not present controlled evaluation, attempt-versus-success, utility/spillover, or alpha sweeps as standalone innovations.

## Confident, Calibrated, or Complicit (ACL 2026)

The ACL Anthology record and arXiv abstract explicitly describe a **deployed-model setting** comparing models with minimal safety alignment (“uncensored”) to more heavily aligned (“censored”) counterparts, including political personas. The inspected evidence therefore supports a separately sourced/deployed-model comparison, not a same-source-checkpoint intervention. It establishes relevant outcome dimensions—accuracy, robustness/persona influence, fairness disparities, and overconfidence—but cannot identify whether safety alignment caused the differences. It is a strong measurement and confounding warning, not a direct controlled-removal competitor.

The exact pairing/history of every checkpoint should still be checked from the full paper before experimental design; the available primary abstract is sufficient to reject the inference that it is a controlled transformation study.
