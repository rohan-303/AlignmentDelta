# Experiment status taxonomy

Run records use these statuses:

- **planned** — specified but not executed.
- **running** — a concrete execution has started and has not reached a terminal state.
- **pilot** — exploratory execution used to test implementation, feasibility, or protocol details; not automatically confirmatory evidence.
- **completed** — execution completed according to the declared protocol and produced auditable outputs.
- **failed** — execution did not successfully complete; failure details remain available.
- **invalidated** — execution completed but was later determined scientifically unusable for a documented reason; its record is preserved.

Legal transitions are:

```text
planned -> running
running -> pilot | completed | failed
pilot -> invalidated
completed -> invalidated
```

Failed and invalidated are terminal for a run ID. Reruns receive new run IDs. The `running` state is necessary to distinguish a started process from a merely planned run and to record interruption/failure without inventing completion.
