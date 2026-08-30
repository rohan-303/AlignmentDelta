# Consistency artifact validation

The consistency artifact is currently blocked because the official MMLU source archive was unavailable from its authoritative host.

The frozen transformation contract is:

1. select MMLU items by deterministic subject-stratified sampling with seed `20260830`;
2. permute answer options with a deterministic seed derived from the stable item ID;
3. remap the correct-answer label through the same bijection;
4. require four unique options, a bijection, one preserved correct semantic option, and a stable variant ID;
5. generate wrapper variants only by changing structural formatting, never substantive question content;
6. reject any transformation not guaranteed meaning-preserving by construction.

No model output can accept or reject a pair.
