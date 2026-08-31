# Step 4.0A Direction Availability — Reconciled

## Identity

The refusal-direction identity is authoritatively established as:

```text
5a8983bcbe4402096210485f8f9b0191eb35b3de84f46624e2dd9811fd09a3fe
```

The original cloud metadata, original cloud log, original Colab notebook output, and verified export archive agree. The malformed 62-character transcription was corrected as an erratum; original imported artifacts remain unchanged.

## Availability

No serialized 2,048-dimensional tensor is present in the imported Step 3.2C artifacts. The cloud runner must reconstruct it before processing any XSTest, MMLU, or consistency item.

## Reconstruction identity

- Model: `Qwen/Qwen2.5-3B-Instruct`
- Model revision: `aa8e72537993ba99e69dfaafa59ed015b17504d1`
- Source: `andyrdt/refusal_direction`
- Source revision: `9d852fae1a9121c78b29142de733cb1340770cc3`
- Training sample: 208 harmful + 208 harmless
- Ordering: stable-ID lexicographic
- Capture: Qwen layer 27 block output, final non-padding token
- Batch size: 1
- Hidden size: 2048
- Implementation: same frozen implementation used by Step 3.2C

## Hard gate

Before any scientific item, reconstruction must verify finite values, dimension 2048, unit norm, and exact equality to the authoritative digest above.

- Match: `DIRECTION_RECONSTRUCTION_VERIFIED`
- Mismatch: `DIRECTION_RECONSTRUCTION_MISMATCH`; generate no scientific output and terminate as blocked.
