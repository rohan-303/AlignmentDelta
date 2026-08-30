# Direction-estimation protocol

## Prior implementation audit

Official repository: `https://github.com/andyrdt/refusal_direction`, pinned commit `9d852fae1a9121c78b29142de733cb1340770cc3`, repository license Apache-2.0.

`dataset/load_dataset.py` defines `train`, `val`, and `test` splits for `harmful` and `harmless` JSON files. The pinned tree identifies:

- `harmful_train.json`, blob `5ca6b46750e06bc401ebd93171a6b0dc0590cdd8`, 260 records;
- `harmful_val.json`, blob `c3128d37e8b255e765f4f51f1a6715572595e3e7`, 39 records;
- `harmful_test.json`, blob `2dc705dc1a50e7773efca46fedab71229169b3bb`;
- `harmless_train.json`, blob `700a497bd1d20ab074fcc576e9bd79ac604543c5`;
- `harmless_val.json`, blob `6b9ee6e9c789799354b618a046758276da445bd8`;
- `harmless_test.json`, blob `6033b711a3c0bf3d49fb88a4824fdac8be792f25`.

The larger JSON files are pinned by blob ID; their full contents are not copied into AlignmentDelta. The source objects contain `instruction` and `category` fields. The repository also contains processed sources including AdvBench, HarmBench, JailbreakBench, StrongREJECT, and others; those are not automatically adopted for AlignmentDelta because overlap and terms require item-level review.

`generate_directions.py` computes harmful-minus-harmless mean residual activations in `float64`. It requests multiple end-of-instruction positions using `range(-len(eoi_toks), 0)`, not only the final position. The wrapper supplies formatting. `select_direction.py` evaluates candidate directions using harmful refusal-ablation scores, harmless refusal-addition scores, and harmless KL divergence, filters late layers and threshold failures, then sorts by harmful refusal score. Its intervention construction attaches hooks across block inputs and attention/MLP outputs for all layers, rather than only the source layer.

## AlignmentDelta contract

AlignmentDelta will use a pinned, disjoint contrast manifest. For each candidate layer and each selected end-of-instruction position, collect residual activations with the verified chat template and compute:

`r_raw[l,p] = mean(harmful[l,p]) - mean(harmless[l,p])`.

Accumulate in `float64`; reject nonfinite values, dimension mismatch, missing masks, and near-zero norms; normalize only after checks. Store source commit/blob IDs, counts, tokenizer/template hash, position rule, hook path, dtype, shape, and artifact hash.

The AlignmentDelta primary intervention is deliberately narrower than the original all-site hook construction: one selected residual-stream block output site, selected by refusal-only validation. This is an explicit extension for localization, not an unacknowledged reproduction claim.

No real target-model direction is extracted in Step 2.3.
