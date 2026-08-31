# Exploratory pilot stopping and invalidation rules

Freeze before execution.

STOP and invalidate the affected run or experiment for: wrong model revision; wrong direction/site artifact; scorer failure; nonfinite activations, logits, probabilities, or metrics; output-schema corruption; unexpected hook persistence; weight mutation; manifest mismatch; excessive missing evaluator labels; or execution under an alpha not in the frozen grid.

Do not stop because effects are weak, null, or scientifically disappointing. Retries must preserve the same frozen configuration and receive a new run ID; changing a scientific setting invalidates the original run.
