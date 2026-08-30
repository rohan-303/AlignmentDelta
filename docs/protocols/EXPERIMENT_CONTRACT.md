# AlignmentDelta experiment contract

**Protocol status: `0.1-draft`.** This contract defines metadata and identity before any model, benchmark, inference, or alignment intervention is introduced. It is not a completed scientific protocol.

## Experimental unit

A future scientific run combines:

```text
source checkpoint M + transformation T + evaluation condition E + environment H -> observations
```

- **Source model:** the model identifier selected as the starting checkpoint.
- **Model revision:** an immutable repository revision or digest when available.
- **Transformation:** the named intervention applied to the source checkpoint.
- **Transformation parameters:** the exact parameter object supplied to that implementation.
- **Intervention strength:** a validated numeric intensity in `[0, 1]`; its meaning must be defined by the transformation protocol.
- **Evaluation task/benchmark:** the task and benchmark identifier being evaluated.
- **Benchmark revision:** the immutable benchmark release or revision.
- **Prompt/template condition:** chat-template, system-prompt, and formatting identifiers.
- **Decoding condition:** deterministic/stochastic setting and generation parameters.
- **Execution environment:** runtime, operating system, hardware, software, and environment manifest.
- **Random seed:** the recorded seed policy for a concrete execution.
- **Run:** one concrete execution attempt of one scientific condition.
- **Replicate:** a planned or executed repeated run of the same condition under a declared seed policy; every execution still gets a new run ID.
- **Observation:** a recorded output-derived measurement produced by an actually executed evaluator and linked to exactly one run. A raw model output is not automatically an observation.
- **Aggregate result:** a derived summary across observations or runs. It is not a run and cannot replace run-level provenance.

A process that exits successfully is not automatically a scientifically valid run: protocol checks, provenance, evaluator execution, and output completeness must also pass.

## Condition versus run identity

`experiment_condition_id` identifies the scientific condition. It is SHA-256 over canonical JSON containing the parsed experiment configuration's scientific fields, with sorted keys, compact separators, and UTF-8 encoding. It includes model/revision, transformation and parameters, intervention strength, benchmark/revision, prompting, decoding, and seed policy.

The execution profile and planned replicate count are excluded because they are execution planning metadata. Hostname, GPU model, cache paths, timestamps, environment manifests, Git dirtiness, and run IDs are never part of the condition payload. They belong to the concrete run manifest.

A `run_id` identifies one execution and has timestamp plus UUID entropy, for example `run-<UTC timestamp>-<uuid fragment>`. Reruns receive new run IDs while retaining the same condition ID where the scientific condition is unchanged.

## Result-directory contract

Future scientific outputs use:

```text
results/raw/<experiment_condition_id>/<run_id>/
```

A completed run may contain `run_manifest.json`, `environment_manifest.json`, evaluator logs, and observation files. Failed and invalidated runs remain represented by their manifests and failure/invalidation records. Status metadata, not directory names alone, is authoritative. Dry-run metadata belongs under `artifacts/runs/` and must never create `results/` files.

## Provenance chain

```text
scientific configuration
  -> experiment_condition_id
  -> run_id
  -> source Git commit
  -> environment manifest
  -> future observations
  -> aggregate result
```

A paper claim must be traceable back through this chain to the exact configuration and execution.

## Phase and protocol version

The configuration phase is either `pilot` or `confirmatory`.

- **Pilot:** debugging, runtime estimation, adapter validation, and technical exploration. Pilot data cannot silently become confirmatory data.
- **Confirmatory:** executed under a frozen protocol and configuration. Changes after inspecting confirmatory results require explicit versioning and documentation.

`0.1-draft` is intentionally provisional. Changing evaluation criteria, transformation definitions, benchmark preprocessing, or outcome definitions may require a protocol-version change. Nothing in Step 1.2 is confirmatory.
