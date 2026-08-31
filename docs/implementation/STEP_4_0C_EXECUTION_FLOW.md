# Step 4.0C execution flow

Safe CLI planning and initialization are model-free:

```text
--dry-run
  -> frozen manifest validation
  -> operation accounting
  -> zero model inference

--initialize-run
  -> Git/protocol hash capture
  -> master manifest (planned)
  -> canonical condition registry
  -> zero model inference
```

The intended real path is:

```text
--execute --profile cloud_gpu
  -> protocol/code/master validation
  -> fresh pre-science gate
  -> cloud Qwen adapter
  -> hydrated item provider
  -> condition orchestrator
  -> schema validation
  -> atomic records/progress/failures
  -> resume/reconciliation
  -> sanitized and blinded exports
```

The production orchestrator, strict hydrated providers, fresh-gate binding, task-specific validation, retry/corruption handling, and archive verification are implemented. The real CLI path is cloud-only and was not invoked locally. No local Qwen model load or scientific inference was performed.
