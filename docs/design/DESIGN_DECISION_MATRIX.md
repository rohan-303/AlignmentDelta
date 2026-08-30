# Design decision matrix

Scores are decision aids on a 1–10 scale, not proof of scientific quality.

| Design option | Novelty | Causal interpretation | Reproducibility | Compute feasibility | Implementation risk | Benchmark quality | Statistical defensibility | Prior-work overlap (10=high risk) | Interpretable null |
|---|---:|---:|---:|---:|---:|---:|---:|---:|---:|
| Before/after safety removal, one model | 2 | 3 | 6 | 8 | 6 | 5 | 4 | 9 | 3 |
| Three families, one checkpoint, signed dose only | 6 | 6 | 6 | 6 | 5 | 6 | 6 | 7 | 7 |
| Three families + matched orthogonal controls + calibration/consistency | 8 | 8 | 7 | 5 | 6 | 8 | 8 | 5 | 9 |
| Bidirectional restoration headline | 4 | 3 | 4 | 4 | 7 | 5 | 4 | 8 | 4 |
| Two families × two sizes | 6 | 7 | 7 | 5 | 5 | 7 | 7 | 6 | 8 |

Selected design: three families × one checkpoint with matched controls, objective calibration, and validated consistency. It is not automatically superior; it is selected because it best balances causal contrast, family diversity, and a meaningful null under the stated resource limit. `Ablating Safety` remains the primary direct competitor.
