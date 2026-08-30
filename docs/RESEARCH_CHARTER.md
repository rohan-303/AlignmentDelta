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

## Step 2.1 draft outcome focus

1. Safety discrimination: harmful-request refusal versus benign safety-adjacent assistance
2. Epistemic calibration on objective known-answer tasks
3. Semantic/behavioral consistency across validated equivalent prompts

Objective utility/capability and validated attempt-versus-success measures remain supporting outcomes where their validators are defensible. These dimensions are design targets only; no outcome has been measured.

## Final draft research questions

- **RQ1:** How do non-refusal behavioral outcomes—especially objective calibration and semantic consistency—change as the strength of a controlled refusal-direction intervention varies on fixed aligned checkpoints?
- **RQ2:** Are those response curves distinguishable from matched orthogonal generic representation perturbations, and how do the curves vary across the sampled model families?

Restoration is not a headline research question. A signed counter-steering condition may be retained as an exploratory diagnostic, but disabling an inference hook or restoring original weights is not treated as scientifically meaningful restoration.

## Scope boundary for Step 2.1

Step 2.1 freezes a draft experimental design and feasibility plan only. It does not implement the intervention, download model weights or benchmark datasets, extract directions, run inference or scoring, generate scientific observations, or produce paper results. Confirmatory model and benchmark inclusion remain subject to the documented pilot gates.

## Design records

The design rationale, model metadata, dose grid, controls, outcomes, statistical plan, feasibility analysis, claim boundary, and pilot rules are documented under `docs/design/`. ADR-0005 records the decision to drop restoration as a headline contribution and to center the study on controlled response-curve interactions.
