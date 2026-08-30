# Generic perturbation control

For each checkpoint, generate multiple independent random directions in the same residual dimension, orthogonalize each to the refusal direction with Gram-Schmidt, and unit-normalize. Apply the same signed projection operator and nominal alpha grid at the same intervention sites.

Match controls using baseline calibration activations: report both unit-vector operator semantics and the achieved perturbation RMS relative to baseline residual RMS. If matching requires a scalar, determine it from a disjoint calibration set and freeze it before outcomes. Use at least four independent random directions per checkpoint as a provisional minimum; the exact seed list is a protocol parameter.

The primary contrast is refusal-direction curve versus the distribution of random-control curves at matched achieved dose. This tests whether collateral change is specific to the safety-related direction rather than a generic activation perturbation. Random-control variability is retained in the analysis, not collapsed into one pseudo-replicate.

Optional different-layer and unrelated-semantic controls are deferred unless the pilot reveals a specific localization confound. They are not part of the minimum matrix.
