# Step 3.0 plan — real-model engineering validation

**Phase:** `engineering`

**Scientific execution:** `false`

**Target:** `Qwen/Qwen2.5-1.5B-Instruct`

**Immutable revision:** `989aa7980e4cf806f80c7fef2b1adb7bc71aa306`

## Scope

Step 3.0 proves the real-transformer software path only. It will not run XSTest, HarmBench, MMLU, calibration, confirmatory response curves, or scientific analysis. All generated output goes under `artifacts/engineering/step_3_0/`, not `results/`.

## Files/modules

Implement a small package under `src/alignmentdelta/engineering/`:

- `model_registry.py`: the pinned Qwen engineering registry entry and validation;
- `model_loader.py`: revision-pinned config/tokenizer/model loading with explicit dtype/device;
- `qwen_adapter.py`: runtime-checked Qwen2 block access, output extraction/replacement, and padding positions;
- `capture.py`: removable residual-stream hooks and online float64 accumulation;
- `direction.py`: deterministic subset loading, difference-in-means estimation, normalization, and artifact serialization;
- `refusal.py`: exact refusal-token metadata and float64 refusal score;
- `controls.py`: deterministic CPU-generator orthogonal controls;
- `projection.py`: signed projection operator and structured-output hook transformation;
- `site_selection.py`: reduced engineering-only site test;
- `run_manifest.py`: auditable engineering manifest and technical diagnostics;
- `step3.py`: one real-model engineering CLI.

Tests will use synthetic/tiny tensors wherever possible and will not repeatedly load the full model.

## Model download strategy

1. Re-query the official Hugging Face API for the pinned revision.
2. Enumerate only required config, tokenizer, generation-config, and unquantized BF16 shard files.
3. Preflight free disk space and expected bytes.
4. Download through `huggingface_hub` at the immutable revision into `~/.cache/huggingface/hub`.
5. Use `trust_remote_code=False` and no quantization, alternate revision, evaluator, Llama, or Gemma files.
6. Record snapshot paths, file sizes, hashes, and repository metadata under the engineering artifact directory.

## Cache and artifacts

- Model cache: `~/.cache/huggingface/hub/`.
- Source-data cache: existing `~/.cache/alignmentdelta/source_data/`.
- Generated engineering artifacts: `artifacts/engineering/step_3_0/`.
- `results/` is prohibited.
- Generated engineering artifacts are ignored unless a deliberately sanitized metadata fixture is needed.

## Dtype/device policy

- Target device: `cuda:0`.
- Prefer native BF16 only if `torch.cuda.is_bf16_supported()` is true.
- Otherwise use FP16 and record the engineering-only deviation.
- Never silently use FP32, CPU offload, `device_map="auto"`, bitsandbytes, or quantization.
- If unquantized BF16/FP16 loading fails due to memory, stop rather than changing the model or protocol.

## Adapter validation

After loading, inspect the actual runtime object rather than relying only on documentation. Record the top-level class, decoder path, block container/path, block count/class, output structure, hidden tensor position, and normalization modules. Compare the runtime to the existing Qwen2 specification; any discrepancy requires a specification correction, regression test, and ADR before continuing.

## Engineering subset

Use only the first IDs under the canonical stable-ID ordering from the frozen role manifest:

- direction train: first 8 harmful and first 8 harmless IDs;
- direction validation: first 4 harmful and first 4 harmless IDs.

The subset manifest will explicitly contain:

```text
phase = "engineering"
scientific_execution = false
engineering_only = true
```

Prompt text will not be printed or included in artifact metadata.

## Direction and site validation

Run online float64 activation sums over the engineering subset. Validate finite values, dimensions, counts, normalization, deterministic ordering, and artifact hashes. Run the reduced site test over layer 0, the middle eligible layer, and the highest eligible pre-pruning layer using four harmful and four harmless validation items. The selected site is engineering-only and cannot become a scientific site selection.

## Random controls

Use the frozen PyTorch CPU-generator algorithm and seeds `20260830` through `20260833`. Verify unit norm and `abs(q.T @ r) <= 1e-6` in float64. Store hashes and compact diagnostics, not verbose vectors in logs.

## Intervention validation

First validate synthetic projection invariants for alpha values `0`, `0.5`, `1.0`, `-0.5`, and `1.25`. Then apply hooks to the actual loaded model at the engineering-only site for benign diagnostic text and forward pass only. Verify finite outputs, projection removal, perturbation RMS, hook cleanup, baseline restoration, and no weight mutation.

## Measurements

Record actual engineering observations only:

- metadata and snapshot sizes;
- model load wall-clock;
- model dtype/device/class/parameter count;
- peak allocated/reserved CUDA memory;
- benign forward wall-clock and shape;
- residual-capture wall-clock and shape;
- direction-subset wall-clock;
- intervention forward wall-clock and peak memory;
- batch size and sequence length.

These are not throughput, safety, utility, calibration, or scientific results.

## Failure and rollback policy

- Stop on missing revision, hash mismatch, remote-code request, adapter disagreement, shape mismatch, nonfinite values, failed projection invariant, hook contamination, weight mutation, or unquantized OOM at batch size 1.
- For OOM only, clear safe CUDA caches and retry a smaller engineering batch if the current batch exceeds 1.
- Never install quantization tooling, switch models, silently offload, or alter the scientific protocol.
- Use atomic artifact writes and never overwrite a different hash.
- Generated artifacts remain ignored and can be removed without affecting source manifests or `results/`.

## Explicit prohibitions

Step 3.0 must not:

- run target-model benchmark evaluation;
- generate free-form completions;
- print model predictions or potentially harmful source text;
- run XSTest, HarmBench, HarmBench classifier, MMLU, calibration, or full alpha curves;
- create confirmatory tables, figures, statistical tests, or paper claims;
- modify model weights or save a modified checkpoint;
- place output under `results/`;
- modify `SHIFT-ICD`.
