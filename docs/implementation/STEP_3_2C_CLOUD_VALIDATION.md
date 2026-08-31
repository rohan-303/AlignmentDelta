# Step 3.2C — Primary Qwen 3B cloud technical validation

## Decision

**VERIFIED_PRIMARY_QWEN_TECHNICAL_PASS**

This is a technical-pipeline completion decision only. It is not scientific evidence, does not establish an intervention effect, and does not authorize Step 3.3 execution.

## Provenance

- Cloud provider: Google Colab
- Cloud run ID: `step3.2-2f3998401d96`
- Code revision that generated measurements: `c1148ab9fef7006485dc3bedf578c16f3d286dc5`
- Model: `Qwen/Qwen2.5-3B-Instruct`
- Model/tokenizer revision: `aa8e72537993ba99e69dfaafa59ed015b17504d1`
- Phase: `technical_pilot`
- Execution profile: `cloud_gpu`
- `scientific_execution`: `false`
- Run-manifest SHA-256: `ca7a3752fc2f73c5772152812379791074a2dcee6cf428de2e66c4fb4bddfa55`
- Export archive SHA-256: `9d3dc34c417d20517dfd7abd4c1616818929307c75ce876bcdcf766bf4f10371`

The later local documentation commit, if created, is not the code revision that generated the cloud measurements.

## Evidence and integrity

Supplied evidence was preserved unchanged. The two downloaded export archives were byte-identical, as were the two downloaded cloud logs. The verified archive contained 34 sanitized files and no actual model-weight files, cache directories, credentials, secrets, or raw prompt-text fields. Model-weight filenames and hashes appear only as metadata in the snapshot manifest; the weight bytes themselves were not imported.

The archive was extracted into an external temporary validation directory before import. Extracted files were copied into the ignored `artifacts/pilot/step_3_2/` directory without regenerating numeric contents. The exact supplied archive, full cloud log, and notebook were preserved as source evidence copies. Import verification recorded `import_verified=true`.

## Cloud environment and model load

Verified environment values:

- GPU: Tesla T4
- Total GPU memory: `15,637,086,208` bytes
- CUDA available: true
- BF16 supported: true
- PyTorch: `2.7.1+cu126`
- CUDA runtime: `12.6`
- Python: `3.11.16`
- Transformers/Accelerate: not recorded in the supplied manifest
- Free disk at gate: `63,941,935,104` bytes
- Eligibility: `eligible_cloud_gpu`

The gate passed the frozen 12-GB VRAM requirement. The observed runtime metadata records `Qwen2ForCausalLM`, `Qwen2TokenizerFast`, `torch.bfloat16`, `cuda:0`, vocabulary size `151,665`, and `trust_remote_code=false`. The technical hook path was `model.model.layers[layer] forward output`. No quantization, CPU offload, or automatic device-map workaround is recorded. The model snapshot contained two weight shards whose metadata totals `6,171,926,992` bytes; no weights were imported locally. Model-load time as a distinct measurement was unavailable.

## Frozen source and token checks

The cloud source-selection manifest matched the local Step 3.1 source-selection manifest semantically and by source hash `e3cbaab8ed4bc44b03d71f710e033d06af0b9b89df0254af32d56de26e7c08dc`. It records direction revision `9d852fae1a9121c78b29142de733cb1340770cc3`, stable-ID ordering, 208 harmful and 208 harmless direction-training items, and 12 harmful and 12 harmless technical-validation items. No raw prompt text was required or imported.

The recorded tokenizer checks were exactly `I -> [40]` and `As -> [2121]`.

## Technical diagnostics

- Hidden dimension: `2048`
- Eligible/completed direction layers: `28/28` (layers 0–27)
- Failed direction layers: `0`
- Direction extraction: `94.227913` seconds; 416 forwards
- Stability seeds: `3101, 3102, 3103`; three resamples per eligible layer
- Stability pairwise-cosine range across recorded diagnostics: approximately `0.5809–0.9662`
- Site candidates searched: 28
- Valid candidates: 8
- Selected technical site: layer 27
- Selected direction hash: `5a8983bcbe4402096210485f8f9b0191eb35b3de84f46624e2dd9811fd09a3fe`

> **Erratum (Step 4.0A-R):** An earlier transcription omitted two hexadecimal characters from this digest. The immutable Step 3.2C cloud artifacts, cloud log, and notebook record the 64-character value shown above.
- Selection score: `8.892019586485093`
- Top-two score margin: `0.06773119247185377`
- Site constraints: harmless KL ≤ 0.1 and nonnegative harmless refusal-addition diagnostic
- Random controls: exactly four, seeds `20260830–20260833`, hidden dimension 2048, unit norm and orthogonality checks recorded
- Alpha grid: `[-0.5, 0, 0.25, 0.5, 0.75, 1.0, 1.25]`
- Alpha configurations: 35 (`1` refusal direction + `4` controls × `7` alphas)
- Technically valid configurations: `35/35`
- Alpha decision: `GRID_TECHNICALLY_VALID`

These values are engineering diagnostics. They are not safety outcomes, capability outcomes, effect estimates, or paper findings.

## Integrity and runtime

The manifest records hooks clean, baseline restored, sentinel hashes unchanged, and model weights unchanged. Runtime records 477.153630 seconds total, 1,720,651,776 bytes CPU RSS, and 12,367,265,654 bytes disk-cache usage. Peak recorded CUDA allocation was 6,378,318,848 bytes and peak reserved memory was 6,947,864,576 bytes. Direction and alpha runtimes were 94.227913 and 63.118118 seconds respectively. Separate stability and model-load timings were unavailable.

## Evidence cross-check

The full cloud log contained no `Traceback`, CUDA OOM, `RuntimeError`, `FAILED`, or `ERROR` markers. Its final JSON reported the same run ID, code commit, model revision, profile, `GRID_TECHNICALLY_VALID`, `PRIMARY_QWEN_TECHNICAL_PASS`, and archive hash. The notebook corroborated the Tesla T4, exact checkout, source-cache hydration, a later `85 passed` test run, the actual Step 3.2C invocation, archive generation, and final decisions. It also contains an earlier failed test caused by missing source-cache hydration; the later successful test output and cloud run supersede that setup-stage failure without being silently omitted.

## Scientific boundary and limitations

No XSTest, HarmBench scientific evaluation/classifier, MMLU evaluation, calibration, consistency analysis, paper hypothesis test, paper figure, or cross-family behavioral comparison was run. This validation does not support claims about refusal behavior, alignment removal, safety, utility, capability, calibration, or generalization. The local Step 3.1 Qwen 1.5B record may be used only for compute-only context, never behavioral comparison.

Confirmatory readiness remains blocked by unresolved Llama access, Gemma access, HarmBench 13B classifier feasibility, authoritative MMLU retrieval/item-manifest status, consistency-pair materialization, and the final cross-family model matrix. These gates were not solved here.

## Import status

- Imported root: `artifacts/pilot/step_3_2/`
- Sanitized artifact files imported: 33
- Original evidence copies preserved: archive, full log, notebook
- Import identity: verified
- Step 3.3: not executed
