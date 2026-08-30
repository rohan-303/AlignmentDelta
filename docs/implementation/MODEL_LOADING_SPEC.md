# Model loading specification

Inputs: ID, immutable revision, cache path, execution profile, dtype policy, and `trust_remote_code=False`.

Preconditions: access/license gate passed; exact config/tokenizer metadata recorded; no floating branch; cache/disk preflight passed.

Outputs: model/tokenizer handles and manifest containing IDs, revisions, classes, template hash, dtype/device map, and retrieved file list. `AutoConfig`/`AutoTokenizer` checks are metadata-only; `AutoModel` is not called before Step 3 authorization. Errors are terminal and secrets are excluded from messages. Remote code requests are rejected.
