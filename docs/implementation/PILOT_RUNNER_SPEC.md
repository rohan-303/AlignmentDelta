# Pilot runner specification

The runner is a gate-driven state machine: access/revision -> config/tokenizer -> meta architecture -> hook shape -> direction source/artifact -> site validation -> controls -> technical alpha sweep -> evaluator smoke test -> integrated pilot.

Each gate emits a provenance manifest and terminal failure reason. The runner refuses to enter evaluation if a required gate is blocked, if any artifact hash is missing, if a manifest role overlaps, or if output would enter `results/` before scientific execution is authorized. It never executes model-produced instructions or grants models external tools/browsing.
