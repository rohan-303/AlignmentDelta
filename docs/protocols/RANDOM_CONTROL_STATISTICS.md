# Random-control statistical audit

The unique refusal direction is not exchangeable with an independently sampled orthogonal random direction under the scientific null: it is selected using refusal-related data and has a distinct construction. Therefore, ordinary label permutation that swaps the refusal label with random-direction labels is not justified and is removed.

Random directions are treated as a sampled reference distribution. For each checkpoint and alpha, compute an item-clustered contrast between the refusal direction and the mean of the random controls. Preserve the random-direction index as a repeated reference factor rather than pseudo-replicating it as independent items. Bootstrap resamples prompt/item clusters and retains all conditions and control directions within each sampled cluster. A hierarchical model with a random control-direction intercept is optional and `pilot-gated`; it is not required for the primary analysis.

An empirical-null rank test is allowed only with a prespecified null bank and a statistic defined before outcomes. With `N` null directions, a one-sided rank p-value using the standard plus-one correction has resolution `1/(N+1)`. Four controls therefore permit only five possible corrected p-value levels; sixteen permit seventeen; thirty-two permit thirty-three. These are reference-resolution facts, not power claims.
