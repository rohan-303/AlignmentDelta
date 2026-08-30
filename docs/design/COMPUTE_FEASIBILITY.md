# Compute and memory feasibility

## Verified host

The observed development host is an NVIDIA RTX 3060 Laptop GPU with approximately 6 GB VRAM and approximately 32 GB system RAM. CUDA smoke testing passed in Step 1.1. These are host observations, not throughput benchmarks.

## Calculated raw BF16 weight memory

Using the API-reported BF16 parameter counts and 2 bytes/parameter:

| Model | Raw BF16 GiB (calculated) | Local unquantized pilot |
|---|---:|---|
| Qwen2.5-3B-Instruct | 5.748 | too tight once runtime overhead is included |
| Llama-3.2-3B-Instruct | 5.984 | too tight once runtime overhead is included |
| Gemma-2-2B-it | 4.870 | technically tight; cloud preferred |
| Qwen2.5-1.5B-Instruct | 2.876 | candidate for local development |
| Llama-3.2-1B-Instruct | 2.302 | candidate for local development |
| SmolLM2-1.7B-Instruct | 3.188 | candidate for local development |

These estimates exclude allocator overhead, activations, temporary tensors, tokenizer memory, and KV cache. KV cache depends on context length, batch size, layers, heads, and dtype and is therefore not asserted here.

## Workload equation

For `M` models, `A` alpha levels, `D` direction conditions, `P` safety/utility prompts, `V` validated variants, `R` generation replicates, and `G` generated tokens, generation workload is approximately `M × A × D × (P × V) × R` prompt-condition generations and `... × G` generated tokens. Teacher-forced calibration adds forward passes proportional to the number of item-option sequences and is not interchangeable with generation count.

Unknowns requiring pilot measurement: peak VRAM, tokens/s, context limits, hook overhead, evaluator runtime, failed-generation rate, and cloud queue/availability.

Unquantized primary measurements should use the same dtype/loading policy across models. Quantized inference is allowed only for software-development feasibility, not silently mixed into confirmatory scores.
