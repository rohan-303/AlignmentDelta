# Safety output handling protocol

AlignmentDelta evaluates text-model behavior in a controlled research setting. It does not execute model-produced instructions, grant models external tools, browse automatically from model outputs, or take real-world actions based on generated text.

Potentially harmful completions are research data. Collection, storage, and inspection must be minimized to what is necessary for scoring. Public artifacts should prefer derived scores, hashes, metadata, evaluator decisions, and redacted examples; full raw-output release requires a separate license, safety, and disclosure review.

Every benchmark input and evaluator must carry provenance metadata: source URL/repository, revision, license/terms status, evaluator identifier/revision, prompt template, generation settings, and access restrictions. Benchmark licenses and source terms must be followed; unclear terms mean no redistribution assumption.

The project does not make a regulatory or IRB exemption determination. The researcher should consult institutional requirements if the intended collection, storage, or publication context makes review relevant.
