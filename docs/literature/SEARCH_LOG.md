# Structured literature audit search log

- Search date: 2026-08-30 UTC; exact runtime check: 2026-08-30T15:41:42Z.
- Method: structured literature audit, not a PRISMA systematic review.
- Sources: arXiv abstract/API/HTML, ACL Anthology, NeurIPS official pages, OpenReview discovery, publisher/index pages, and official code pages.
- Primary-source rule: snippets were discovery-only; evidence came from abstracts/full text/official proceedings or ACL metadata.

## Query families

Exact-title searches covered all nine required seeds. Expansion terms included: safety alignment removal LLM; safety ablation; refusal direction/ablation; uncensored LLMs; abliteration; representation engineering; activation steering; de-alignment; harmful fine-tuning; behavioral drift; calibration; robustness; capability degradation; refusal versus capability; compliance versus competence; safety-capability tradeoff; reversible refusal; dose-response activation steering; intervention strength.

## Screening and counts

- Core: 9 required seed works inspected and included.
- Secondary/background: 3 adjacent works inspected (SCANS, SafeMERGE, and related refusal/over-refusal submissions); not promoted to core because their primary questions are mitigation/preservation or mechanistic refinement.
- Excluded from core: practitioner abliteration commentary and generic jailbreak-only work.
- These counts are audit-screening counts, not a complete database search or PRISMA flow.

## Unresolved

The Preprints.org page for *Uncensored AI in the Wild* returned HTTP 403; authors, DOI, and full methods were not promoted to verified metadata. Dose-response and reversibility searches found direct evidence in *Ablating Safety* and refusal-direction work, but no independently verified paper establishing cross-family restoration of collateral behavior. This is a search limitation, not proof of absence.
