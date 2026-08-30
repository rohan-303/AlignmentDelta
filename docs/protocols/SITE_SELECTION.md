# Intervention-site selection

Site selection is technical and refusal-only, never primary-outcome-driven.

1. Candidate sites are all residual-stream block outputs supported by the verified model wrapper; the exact hook names are recorded per architecture.
2. Estimate directions on `direction_train`; evaluate candidate separation and intervention refusal signal only on disjoint `direction_validation` items.
3. Select the site by a pre-registered technical score: finite normalized direction, hidden-state shape validity, and held-out refusal-direction separation/refusal-only validation score. Calibration, consistency, utility, overall effect size, and confirmatory outcomes are forbidden inputs.
4. Tie-break by lowest layer index, then lexical hook name. Record all candidate scores, not only the winner.
5. A failed or nonfinite candidate, missing hook, near-zero norm, or absent validation signal causes a protocol review/NO-GO, not outcome-driven site hunting.

The technical score and exact threshold are configuration values frozen before any primary evaluation. If implementation inspection shows the faithful prior-paper criterion is not reproducible for a candidate architecture, the model is gated out or the technical validation criterion is amended before evaluation; it is not changed after seeing primary outcomes.
