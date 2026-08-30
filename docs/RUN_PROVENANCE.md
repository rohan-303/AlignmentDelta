# Run provenance and state policy

A run manifest is separate from the Step 1.1 environment manifest. It links one concrete execution to its experiment condition, configuration hash/reference, Git state, environment manifest reference, execution profile, seed, output directory, status, and any failure/invalidation record. It never contains model-generated observations.

## Status state machine

The transient `running` state is useful because a process can be interrupted or fail after starting; it prevents an unstarted `planned` run from being mislabeled as completed.

```text
planned -> running
running -> pilot | completed | failed
pilot -> invalidated
completed -> invalidated
```

`failed` and `invalidated` are terminal for that run ID. A failed execution must not be changed into `completed`; retry by creating a new run ID. `pilot` is an exploratory terminal outcome, not a shortcut to confirmatory evidence.

## Structured records

Failures record category, concise message, stage, timestamp, exception type when applicable, and retry guidance. Invalidation records include category, explanation, timestamp, discovering Git commit when available, and whether the data is excluded from primary analysis. Secret-bearing environment dumps are prohibited.

## Atomic writes

Manifest JSON is written to a temporary file in the destination directory, flushed and synchronized, then atomically replaced. Scientific result files are not created by validation or dry-run commands.
