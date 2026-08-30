# Intervention-site selection

Candidate sites are residual-stream block outputs. Candidate position/layer pairs are evaluated only on `direction_validation`.

For candidate `(p,l)`, define:

`S(p,l) = mean_i [ R_i^baseline - R_i^ablated(p,l) ]`

where `R = log((sum refusal-token probabilities + epsilon)/(sum non-refusal-token probabilities + epsilon))`, and ablation is the frozen signed projection at the candidate site. Higher `S` means a larger refusal-score decrease. Report the corresponding harmless refusal-addition and harmless KL diagnostics as validity constraints, not primary outcomes.

Selection rule:

1. reject nonfinite direction/score candidates;
2. reject candidates with norm below `1e-12`;
3. reject candidates failing hidden-dimension or hook-shape checks;
4. reject candidates failing the predeclared harmless-KL ceiling or refusal-addition floor;
5. among remaining candidates, maximize `S(p,l)`;
6. tie-break by smallest layer index, then earliest position, then lexical hook name.

Candidate layers are all supported residual blocks except the final 20% only if the faithful prior selector’s predeclared pruning rule is retained. Candidate positions are the pinned end-of-instruction positions. No calibration, consistency, utility, overall effect size, or confirmatory outcome may enter the score.

If no candidate survives, the gate fails. Threshold values must be frozen in the implementation configuration before primary evaluation; they cannot be tuned on primary outcomes.
