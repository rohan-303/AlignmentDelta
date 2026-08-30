# Evaluator feasibility decision

Decision: `unresolved` is not carried into the final gate table; the operational status is **blocked**.

The official HarmBench classifier is the preferred scientific scorer in principle, but its 13B scale, bfloat16 requirement, six-shard distribution, gated/terms provenance, and unknown local peak memory make the 6 GB RTX 3060 path unverified. A free-cloud GPU may be suitable, but no specific free allocation or runtime is guaranteed. Raw BF16 weight memory is approximately 26 GB before runtime overhead; this is arithmetic, not a measured feasibility claim.

No smaller substitute is adopted without a published validation source and a pre-outcome protocol amendment. Manual validation remains secondary, not a silent replacement for the automated primary scorer. Therefore the HarmBench evaluator gate blocks Step 3.0.
