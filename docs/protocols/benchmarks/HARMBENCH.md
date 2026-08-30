# HarmBench final behavior manifest — Step 2.4

Repository: `https://github.com/centerforaisafety/HarmBench`.

Revision: `8e1604d1171fe8a48d8febecd22f600e462bdcdd`.

Materialized behavior files:

- all: 400 rows;
- official text test: 320 rows;
- official text validation: 80 rows.

The official text-test manifest is represented by `configs/manifests/harmbench.toml`, with BehaviorID values, source revision, file hash, and no target outcomes. Functional and semantic category counts are recorded in the source registry. Auto-generated attack prompts are not used.

Status: `cleared_with_restrictions` for source manifest construction. The automated evaluator remains a separate confirmatory gate. No behavior was run through a model.
