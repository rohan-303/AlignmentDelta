# HarmBench evaluator smoke scope

**Status: future confirmatory gate only; not run in Step 3.3.**

Evaluator: `cais/HarmBench-Llama-2-13b-cls`, revision `bda705349d1144fa618770bea64d99ce54e3835b`.

Required checks: parameter count and unquantized BF16 memory; license/access; exact classifier template; scoring semantics; small fixed validation set; >=40-GB-class GPU preferred; no hidden CPU offload; and blinded manual audit. A smoke test must record immutable revision, environment, finite outputs, scorer schema, and manual-audit agreement before confirmatory use. HarmBench is excluded from the first exploratory pilot.
