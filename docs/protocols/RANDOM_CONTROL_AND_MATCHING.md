# Random-direction controls and perturbation matching

For hidden dimension `d`, unit refusal direction `r`, and seeded PyTorch CPU generator, draw `z ~ N(0,I_d)`, compute `z_perp = z - (z^T r)r`, reject nonfinite or near-zero vectors, and normalize `q = z_perp / ||z_perp||`. Require `abs(q^T r) <= 1e-6` in float64.

Pilot uses four controls. Provisional confirmatory analysis uses sixteen controls, subject to final precision review. This is a workload/reference-resolution decision, not a power claim. Record absolute activation change, RMS change, perturbation-to-baseline RMS, projection magnitude, and refusal projection removed. Any achieved-dose scale is estimated only from direction validation, never primary outcomes.
