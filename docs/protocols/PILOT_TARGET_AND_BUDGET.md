# Engineering target and budget — Step 2.4

Engineering target:

```text
Qwen/Qwen2.5-1.5B-Instruct
revision = 989aa7980e4cf806f80c7fef2b1adb7bc71aa306
```

Config/tokenizer loading with `trust_remote_code=False` and meta-device construction passed. Qwen2.5 refusal strings `I` and `As` encode as `[40]` and `[2121]` under the pinned tokenizer.

The target is an engineering checkpoint, not a replacement for the confirmatory model matrix. Step 3 may download only this target after separate authorization. The local RTX 3060 is reserved for engineering validation; no throughput or scientific feasibility claim is made here.
