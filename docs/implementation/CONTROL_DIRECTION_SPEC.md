# Control-direction specification

Inputs: normalized refusal direction, hidden dimension, seed list, and tolerance. Draw standard-normal vectors from a named PyTorch CPU generator, project out the refusal component, normalize, reject near-zero/nonfinite results, and verify absolute dot product <= `1e-6` in float64. Return direction, seed, generator specification, norm, and orthogonality diagnostic. Never rescale controls from primary outcomes.
