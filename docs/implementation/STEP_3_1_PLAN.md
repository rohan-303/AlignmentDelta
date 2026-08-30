# Step 3.1 plan — full technical pilot and pilot-protocol freeze

**Phase:** `technical_pilot`

**Scientific execution:** `false`

**Primary model:** `Qwen/Qwen2.5-1.5B-Instruct`

**Pinned revision:** `989aa7980e4cf806f80c7fef2b1adb7bc71aa306`

## Purpose and boundary

Step 3.1 validates the complete AlignmentDelta intervention procedure as a reproducible, computationally bounded technical pilot. It may measure activation, refusal-score, perturbation, runtime, memory, and state-integrity diagnostics. It is not a paper experiment and produces no scientific benchmark, utility, calibration, consistency, or confirmatory result.

Every generated artifact is written below `artifacts/pilot/step_3_1/` and records `phase = technical_pilot`, `scientific_execution = false`, and `engineering_only = true`. `results/` is prohibited. Harmful prompt text and model responses are never printed or serialized.

## Pre-implementation audit

The pinned original `andyrdt/refusal_direction` implementation at commit `9d852fae1a9121c78b29142de733cb1340770cc3`:

- randomly samples equal `n_train=128` harmful and harmless training items with seed 42;
- optionally filters training and validation records using the refusal score;
- accumulates float64 means over all model layers and multiple end-of-instruction positions;
- defaults to batch size 32;
- selects using harmful ablation refusal score, harmless activation-addition refusal score, and harmless KL, pruning the final 20% of layers.

AlignmentDelta's frozen source protocol materially differs in sampling: it uses only the pinned harmful/harmless train files, stable lexicographic IDs, and an 80/20 direction train/validation split. This is retained because the original validation/test files overlap HarmBench and because reproducible provenance/leakage control takes priority over reproducing an outcome-oriented sample. Step 3.1 will freeze a technical computational policy over this already-frozen source rather than tune counts from observed outcomes.

## Direction-source policy

The technical pilot will use all 208 frozen direction-train harmful IDs and a deterministic equal-count harmless sample of 208 IDs, selected by the already-frozen stable-ID ordering from the 15,034 harmless direction-train pool. This is the smallest policy that preserves every harmful source item while preventing the 72:1 class imbalance from causing the harmless mean to dominate compute and numerical accumulation. The unused harmless IDs remain reserved and are not selected retrospectively.

Direction validation will use a deterministic 12 harmful + 12 harmless technical subset from the frozen validation pools. The exact IDs and ordering will be written to `docs/protocols/TECHNICAL_PILOT_DIRECTION_SAMPLE.md` and the run manifest.

## Batching policy

Strategy 1, batch size 1, is the trusted reference because Step 3.0 observed variable-length left-padding discrepancies. Step 3.1 will compare it against:

1. equal-token-length buckets with no padding;
2. an explicitly gathered final non-padding position only if the Qwen runtime proves equivalence.

The comparison uses a small fixed technical subset and records refusal-score deviation, selected-layer activation deviation, direction cosine, runtime, and peak VRAM. Tolerances are predeclared: refusal-score absolute deviation `<= 2e-3` under BF16; activation relative RMS deviation `<= 2e-3`; direction cosine `>= 0.999999`; no nonfinite values. Variable-length left-padding is prohibited unless independently proven equivalent. If no candidate passes, batch size 1 remains frozen.

## Token lengths

The exact pinned tokenizer and chat template will produce token-length summaries separately for harmful and harmless pilot direction data: minimum, median, p90, p95, p99, and maximum. Prompt text is not printed or stored.

## Full candidate-layer extraction

Compute the eligible layer boundary programmatically as `floor(0.80 * n_layers) - 1`, then extract directions for every eligible layer in shared forward passes where practical. Use float64 streaming sums, no persistent activation corpus, and the frozen sampling/batching policy. For every layer record raw norm, normalized norm, finite status, sample counts, direction hash, extraction time, and peak memory.

## Direction stability

Use three deterministic resamples of the frozen balanced technical direction source. Resampling is by stable IDs with predeclared seeds and fixed counts, without looking at scores or effects. Record pairwise cosine similarities and norm variation per candidate layer as an engineering numerical-stability diagnostic only.

## Baseline and site selection

Run finite refusal-score distribution summaries on the technical validation data only. Search every eligible layer using the frozen refusal-only site-selection rule, KL ceiling `0.1`, harmless refusal-addition floor `0.0`, finite/shape/norm checks, final-20%-layer pruning, and deterministic tie breaking. Record all diagnostics, valid/rejected counts, top candidate, second valid candidate, score margin, and rejection reasons. No calibration, consistency, utility, XSTest, HarmBench, MMLU, or generated completion enters selection.

## Random controls and alpha grid

Construct exactly the four frozen controls with seeds `20260830` through `20260833`. Use the full technical alpha grid:

```text
{-0.5, 0, 0.25, 0.5, 0.75, 1.0, 1.25}
```

For the selected refusal direction and each control, run only a small fixed technical diagnostic set. Record finite status, achieved projection removal, perturbation RMS, perturbation-to-baseline RMS, logit finiteness, peak VRAM, and wall-clock time. No responses are generated or retained. Alpha validity is purely numerical/operational; the grid is not revised because of any score behavior.

## Integrity and profiling

Repeat baseline, complete intervention sweep, hook removal, and baseline restoration. Verify sentinel parameter hashes, on-disk Safetensors hashes, empty hook registry, and deterministic baseline restoration. Record tokenizer preparation, extraction, site selection, control creation, alpha sweep, total runtime, forward counts, batch strategy, peak allocated/reserved GPU memory, readily measurable CPU RSS, and model cache size.

## Qwen 3B feasibility

Do not download Qwen 3B. Use the verified Qwen 3B parameter count and measured Qwen 1.5B memory quantities to calculate a conservative local 6-GB feasibility estimate. Clearly label projections as calculated, not measured. If local execution is borderline or unsafe under BF16/no-quantization, define minimum cloud requirements for Step 3.2.

## Failure and stopping rules

Block on missing or mismatched revision, unauthorized remote code, nonfinite values, failed shape/dimension checks, failed batch equivalence for the adopted strategy, failed direction stability due to numerical corruption, no valid site, failed orthogonality, invalid alpha numerics, hook contamination, weight mutation, baseline restoration failure, or incomplete provenance. Do not stop or revise protocol because refusal scores, direction norms, or perturbation metrics look weak or uninteresting.

## Step 3.2 gate

Step 3.2 is authorized only if all technical questions are answered, the complete pilot artifacts are reproducible, no integrity gate fails, and no scientific benchmark or outcome-driven protocol change occurred. If so, create `docs/implementation/STEP_3_2_SCOPE.md` authorizing only technical validation of the separately pinned Qwen 3B checkpoint. Do not download or execute Step 3.2 during Step 3.1.
