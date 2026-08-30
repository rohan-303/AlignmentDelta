# Architecture adapter specification

| Family | Transformers class | Block path | Residual hook contract | Risks |
|---|---|---|---|---|
| Qwen2 | `Qwen2ForCausalLM` | `model.model.layers` | installed runtime observed a Tensor block output; adapter also preserves the leading hidden tensor and auxiliary fields for structured outputs | Qwen chat-template/padding conventions; do not use remote code |
| Llama | `LlamaForCausalLM` | `model.model.layers` | residual stream is the block output; adapter must preserve structured outputs | gated access; Meta template and BOS/EOS handling |
| Gemma2 | `Gemma2ForCausalLM` | `model.model.layers` | inspect exact block output structure from installed Transformers before implementation | gated access; Gemma normalization/attention details |

All adapters select the final non-padding token from `attention_mask`, not the last padded index. Hooks must replace only the hidden-state tensor field and preserve tuple/Cache structures. Attention masks are passed unchanged. Qwen and Llama share practical block-path conventions only where verified; they remain separate adapters. Gemma remains blocked until authenticated config inspection.
