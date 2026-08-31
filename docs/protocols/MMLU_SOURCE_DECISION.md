# MMLU source decision

**Decision: `MMLU_SOURCE_BLOCKED`.**

The pinned source is `hendrycks/test` at revision `4450500f923c49f1fb1dd3d99108a0bd9717b660`; its README points to `https://people.eecs.berkeley.edu/~hendrycks/data.tar`. HTTPS retrieval attempts on 2026-08-31 used two 20-second attempts with a two-second backoff and both timed out without receiving archive bytes. The pinned repository contains evaluation code but not the archive contents.

No random mirror was accepted. A future retry may use a network environment that reaches the exact official URL. A mirror may be adopted only after proving provenance and byte/content identity strongly enough for paper use. No MMLU-Pro, CMMLU, or derivative dataset may substitute without a separately approved protocol amendment.

Because exact MMLU items, labels, archive hash, split counts, and overlap audit are unavailable, the MMLU manifest and consistency-pair manifest remain blocked.
