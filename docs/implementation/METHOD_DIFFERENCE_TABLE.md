# Method difference table

| Dimension | Original refusal-direction method | AlignmentDelta method | Reason for difference | Scientific consequence |
|---|---|---|---|---|
| Direction data | Pinned repository harmful/harmless split files and wrapper datasets | Pinned, leakage-audited source manifest disjoint from primary outcomes | prevent evaluation leakage | direction estimates are not automatically exact paper replicas |
| Positions | Multiple end-of-instruction positions from `eoi_toks` | same multi-position source rule unless adapter validation requires a predeclared position subset | preserve source behavior | position is recorded as an estimand component |
| Site selection | harmful ablation + harmless addition + harmless KL; late-layer pruning | refusal-only held-out score with fixed validity constraints | localize the primary operator and prevent primary-outcome selection | not a claim of identical reproduction |
| Normalization | generator saves mean differences; downstream code handles direction use | normalize after finite/nonzero validation | required by project operator | alpha has unit-vector semantics |
| Operator sites | hooks across all block inputs and attention/MLP outputs | one selected residual-stream block output | isolate a controlled site and avoid silent all-layer intervention | narrower, different causal intervention |
| Alpha | source code uses its own ablation/addition conventions | signed projection coefficient grid | explicit dose-response design | nominal alpha is not cross-model physical dose |
| Formatting | model wrapper-specific formatting, including explicit Qwen/Llama templates | verified native chat template with hash | avoid architecture improvisation | formatting becomes provenance |
