# Residual capture specification

Inputs: verified model adapter, rendered prompts, attention masks, candidate layer/position, and capture dtype.

Capture the residual-stream tensor at the adapter-defined block output or pre-hook location without changing model outputs. Select positions from the final non-padding index unless the direction artifact explicitly records a multi-position end-of-instruction rule. Validate batch/sequence/hidden dimensions, finite values, device, dtype, and hook invocation count. Preserve tuple/structured outputs and remove hooks in `finally` blocks. Outputs are synthetic-testable activation artifacts plus provenance; no generated text is required.
