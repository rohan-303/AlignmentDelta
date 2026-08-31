# Step 4.0C existing-component blocker matrix

| Requirement | Already complete | Partially complete | Missing | Implementation location | Tests | Action |
|---|---|---|---|---|---|---|
| Frozen model/direction/control identity | Yes |  |  | `configs/experiments/exploratory_qwen3b.toml`, cloud adapter | existing + cloud adapter tests | Preserve |
| Cloud model loader and technical gate |  | Yes |  | `experiments/cloud_adapter.py` | `test_cloud_adapter.py` | Keep cloud-only |
| Source hydration |  | Yes | record-count/schema validators | `prepare_cloud_data.py` | existing hydration tests | Add source validators before cloud |
| Master-run identity |  | Yes | CLI execute integration | `production_orchestrator.py`, pilot CLI | `test_production_orchestrator.py` | Wire CLI |
| 1,860 logical condition accounting | Yes |  |  | planning/config | existing pilot tests | Preserve |
| Production task records |  | Yes, fake adapter | real item provider and cloud wiring | `production_orchestrator.py` | mocked production tests | Complete before release |
| Progress/failure/resume |  | Yes, mocked complete records | real failure/retry integration | `production_orchestrator.py` | resume tests | Add explicit failures |
| Direction cache |  | Yes | cloud smoke integration | production orchestrator | `test_direction_cache.py` | Wire to smoke |
| Schema validation |  |  | Yes for real records | schemas + orchestrator | missing | Implement before release |
| Sanitized export |  | Yes, mocked | archive reopen/hash verification | orchestrator | missing | Implement verification |
| Sensitive annotation export |  | Yes, mocked | protected map and leakage audit integration | annotation + orchestrator | partial | Complete before release |
| Full CLI workflow |  | Yes, initialize/smoke flags | real execute task path | pilot CLI | missing | Wire only after gates |
| Scientific execution | No, intentionally |  |  | cloud-only path | boundary checks | Do not run locally |
