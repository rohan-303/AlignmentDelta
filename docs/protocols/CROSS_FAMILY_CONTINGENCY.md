# Cross-family contingency

**Status: contingency only; not activated.** No confirmatory matrix substitution is authorized merely because an original candidate is inconvenient.

| Candidate | Family / organization | Parameters | Architecture | License | Access | Revision | BF16 raw weight memory | Likely cloud requirement | Adapter work |
|---|---|---:|---|---|---|---|---:|---|---|
| `HuggingFaceTB/SmolLM2-1.7B-Instruct` | SmolLM2 / Hugging Face TB | 1,711,376,384 BF16 parameters | `LlamaForCausalLM` | Apache-2.0 | `ACCESS_GRANTED`, ungated metadata and files | `31b70e2e869a7173562077fd711b654946d38674` | 3,422,752,768 bytes | 16-GB-class GPU preferred for unquantized BF16 technical validation; exact gate still required | tokenizer/chat-template audit, layer-hook adapter, technical direction/site validation, independent site selection |

Selection is based only on open access, explicit license, immutable revision, standard Transformers metadata, instruct/chat capability, size, and architectural adaptability. No scientific outcome was used. This candidate does not enter the confirmatory matrix until the original gated candidates are demonstrably unavailable and the fallback activation protocol is satisfied.
