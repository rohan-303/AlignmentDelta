# Pinned model metadata registry

Official Hugging Face API metadata and revision-pinned config/tokenizer checks were performed on 2026-08-30. No weight files were requested.

| ID | Revision | Config | Tokenizer artifacts | Tokenizer class | Architecture/model type | Hidden/layers | dtype | chat template | auto_map/custom code | gated | license/URL |
|---|---|---|---|---|---|---|---|---|---|---|---|
| Qwen/Qwen2.5-3B-Instruct | `aa8e72537993ba99e69dfaafa59ed015b17504d1` | `config.json` | `tokenizer.json`, `tokenizer_config.json`, `merges.txt`, `vocab.json` | `Qwen2TokenizerFast` (verified) | `Qwen2ForCausalLM` / `qwen2` | 2048 / 36 | bfloat16 | tokenizer_config | absent; no remote code requested | false | Qwen Research; official LICENSE URL |
| meta-llama/Llama-3.2-3B-Instruct | `0cb88a4f764b7a12671c53f0838cd831a0843b95` | `config.json` listed; retrieval blocked | tokenizer files listed; retrieval blocked | blocked | API metadata: `LlamaForCausalLM` / `llama` | blocked | blocked | tokenizer_config listed | API metadata absent; compatibility blocked | manual | `llama3.2`; official model card/license gated |
| google/gemma-2-2b-it | `299a8560bedf22ed1c72a8a11e7dce4a7f9f51f8` | `config.json` listed; retrieval blocked | tokenizer files listed; retrieval blocked | blocked | API metadata: `Gemma2ForCausalLM` / `gemma2` | blocked | blocked | tokenizer_config listed | API metadata absent; compatibility blocked | manual | `gemma`; official terms gated |
| Qwen/Qwen2.5-1.5B-Instruct | `989aa7980e4cf806f80c7fef2b1adb7bc71aa306` | `config.json` | `tokenizer.json`, `tokenizer_config.json`, `merges.txt`, `vocab.json` | `Qwen2TokenizerFast` (verified) | `Qwen2ForCausalLM` / `qwen2` | 1536 / 28 | bfloat16 | tokenizer_config | absent; no remote code requested | false | Apache-2.0; official LICENSE URL |
| meta-llama/Llama-3.2-1B-Instruct | `9213176726f574b556790deb65791e0c5aa438b6` | listed; retrieval blocked | listed; retrieval blocked | blocked | API metadata: `LlamaForCausalLM` / `llama` | blocked | blocked | tokenizer_config listed | compatibility blocked | manual | `llama3.2`; official model card/license gated |
| HuggingFaceTB/SmolLM2-1.7B-Instruct | `31b70e2e869a7173562077fd711b654946d38674` | `config.json` | `tokenizer.json`, `tokenizer_config.json`, tokenizer files | `GPT2TokenizerFast` (verified) | `LlamaForCausalLM` / `llama` | 2048 / 24 | bfloat16 | tokenizer_config | absent; no remote code requested | false | API reports Apache-2.0; repository license path requires recheck |

For gated candidates, “listed” means official API metadata exposed the file name, not that the file was anonymously retrievable. No entry silently updates a previously pinned revision.
