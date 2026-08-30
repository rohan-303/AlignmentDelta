# ADR-0006: Use the installed Qwen2 runtime block path

- **Status:** accepted for Step 3.0
- **Date:** 2026-08-30
- **Decision:** The Qwen2 adapter resolves decoder blocks at `model.model.layers`. Hidden size is read from `model.model.config.hidden_size` when the decoder does not expose a direct `hidden_size` attribute. The leading hidden tensor is replaced while auxiliary tuple fields are preserved.

## Context

The pre-Step-3 prose specification named `model.transformer.h`, but the loaded pinned `Qwen2.5-1.5B-Instruct` object under Transformers 4.57.6 is a `Qwen2ForCausalLM` containing a `Qwen2Model` at `model.model` and a `ModuleList` at `model.model.layers`. The decoder exposes configuration-backed hidden size rather than a direct decoder attribute.

## Evidence

Step 3.0 runtime introspection verified 28 `Qwen2DecoderLayer` blocks, hidden size 1536, `Qwen2Model` decoder class, and a Tensor block output through a real residual hook. The adapter regression tests cover the wrapper path and structured-output preservation for tuple/list implementations.

## Consequences

The implementation is pinned to the verified installed runtime and does not add a fallback path. Llama and Gemma remain separate/specification-only adapters until their own access and runtime structures are authorized and verified.
