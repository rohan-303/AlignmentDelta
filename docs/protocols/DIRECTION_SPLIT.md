# Direction split — Step 2.4 final

AlignmentDelta uses only `harmful_train.json` and `harmless_train.json` from the pinned refusal-direction repository for direction estimation. The original source validation/test files are provenance-only because the audit found overlap with HarmBench.

Algorithm:

1. derive stable record IDs as SHA-256 of the canonical sorted JSON record, truncated to 24 hexadecimal characters;
2. sort IDs lexicographically;
3. assign the first `floor(0.80*n)` items to `direction_train`;
4. assign the remainder to `direction_validation`;
5. preserve harmful/harmless roles;
6. prohibit any outcome-dependent reassignment.

Resulting counts:

| Source | Total | Direction train | Direction validation |
|---|---:|---:|---:|
| harmful train | 260 | 208 | 52 |
| harmless train | 18,793 | 15,034 | 3,759 |

The exact IDs are version-controlled in `configs/manifests/refusal_direction_source.toml`. Raw prompts remain outside Git.
