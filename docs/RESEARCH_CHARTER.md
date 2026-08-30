# AlignmentDelta research charter

## Project

**AlignmentDelta**

**Working framing:** A controlled study of behavioral drift under safety-alignment removal in large language models.

This is a provisional research direction, not a claim that any hypothesis has been proven.

## Core principle

The primary design is not a comparison of arbitrary community checkpoints labeled “aligned” and “uncensored.” Experiments should begin from the same aligned model checkpoint `M` and apply a controlled transformation:

```text
M -> T(M)
```

Later experiments may vary controlled intervention intensity:

```text
M -> T_alpha(M)
```

where `alpha` denotes intervention strength. Where technically meaningful and scientifically defensible, a later study may examine reversibility:

```text
M -> T(M) -> T_inverse(T(M))
```

The inverse question is conditional on a technically valid restoration procedure; it must not be assumed merely because an intervention has been defined.

## Provisional behavioral outcome families

1. Safety discrimination
2. General utility/capability
3. Epistemic calibration
4. Behavioral robustness / decision consistency
5. Attempt rate versus validated success rate

These dimensions are provisional and may be narrowed after literature review and pilot work. Their inclusion here does not imply that the project has measured them.

## Provisional research questions

- **RQ1:** How do controlled safety-alignment removal interventions alter model behavior beyond refusal frequency?
- **RQ2:** Do different alignment-removal mechanisms produce distinct behavioral drift profiles when applied to the same source checkpoint?
- **RQ3:** How does intervention strength affect refusal behavior, validated task performance, calibration, and robustness?
- **RQ4:** Does increased willingness to answer correspond to increased validated competence, or primarily to increased attempt rate?
- **RQ5 (conditional):** Where technically reversible interventions exist, are collateral behavioral changes reversible when the intervention is reversed? This question is conditional on the technical validity of an inverse/restoration procedure.

## Scope boundary for Step 1.0

This bootstrap creates research infrastructure only. It does not implement alignment removal, download models or datasets, run evaluations, or produce scientific results.
