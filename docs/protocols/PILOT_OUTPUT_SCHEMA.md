# Pilot output schema

Each future row/run manifest must include: model identifier and immutable revision; tokenizer identifier/revision; Git commit; environment-manifest hash; direction source/revision/split and direction hash; selected layer/hook/token position; alpha; intervention type; random-control seed; achieved activation/RMS/projection metrics; source and stable item ID; prompt-template revision; decoding parameters; generated-output hash; evaluator identifier/revision/result; raw-score components; exclusion/retry reason if any; and run status.

Potentially harmful raw text is stored only under the safety-output protocol, access-controlled and hash-linked. Reports should prefer hashes and structured labels. No pilot output rows are created in Step 2.2.
