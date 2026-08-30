# Data partition and leakage policy

Scientific roles are disjoint by stable source identifier wherever the source permits it:

- `direction_train`: harmful/harmless contrast examples used only to estimate candidate directions.
- `direction_validation`: held-out contrast examples used only for technical direction/site checks and dose matching.
- `pilot_evaluation`: small pre-confirmatory checks used to exercise the pipeline.
- `confirmatory_evaluation`: frozen primary outcomes.

The direction partitions must not overlap XSTest, HarmBench, utility/calibration, semantic-consistency, or confirmatory IDs. A manifest validator will reject duplicate `(source, stable_id)` pairs across incompatible roles. If a source forces reuse, the exception must be recorded with an item-level justification before execution; silent reuse is prohibited. Prompt formatting templates are versioned separately, and generated paraphrases cannot enter an evaluation role until human/source validation is recorded.
