# Exploratory consistency scoring

For each source item and its option-order permutation, score all four complete option sequences using the frozen MMLU option-probability method. Let `p` be the source probability vector and `q` the transformed vector remapped through the inverse permutation into canonical semantic option order.

Primary exploratory measure: `I[argmax(p) = argmax(q)]`, prediction agreement after canonicalization. This is frozen before model execution.

A secondary descriptive distance is permitted: Jensen–Shannon divergence, `JS(p,q) = 1/2 KL(p||m) + 1/2 KL(q||m)`, where `m=(p+q)/2`; zero probabilities contribute zero to KL. It cannot replace prediction agreement or support confirmatory claims.

Each pair is two scored representations under each condition; a pair is never counted as one model input.
