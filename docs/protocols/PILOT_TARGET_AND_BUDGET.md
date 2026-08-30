# Engineering pilot target and download budget

## First engineering target

Select `Qwen/Qwen2.5-1.5B-Instruct` at revision `989aa7980e4cf806f80c7fef2b1adb7bc71aa306` as the first engineering target, not as a replacement for the confirmatory model matrix. It is ungated at repository level, passed config/tokenizer loading with `trust_remote_code=False`, passed meta-device construction, and shares the Qwen2 adapter family with the primary Qwen candidate.

This selection is for software validation only and does not use scientific outcomes.

## Budget before any future download

Required model files are the revision-pinned config, tokenizer artifacts, generation metadata, and model safetensors listed by the official API. The exact repository metadata must be re-read immediately before download and recorded because file sizes can change across revisions. Expected raw BF16 parameter memory is computed from the pinned config parameter count at download time; no runtime or throughput is claimed here.

Local target: RTX 3060 Laptop GPU, approximately 6 GB VRAM, with CPU offload only if explicitly configured and recorded. Cloud target: a documented GPU allocation with enough memory for the selected checkpoint and evaluator. Cache: `~/.cache/alignmentdelta`. Disk preflight must require model shard bytes plus at least 20% temporary/manifests overhead and must refuse download if free space is insufficient.

No model files are downloaded in Step 2.3.
