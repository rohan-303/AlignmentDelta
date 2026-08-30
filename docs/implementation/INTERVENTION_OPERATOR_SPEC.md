# Intervention operator specification

For hidden state `h[..., d]` and unit direction `r[d]`, compute:

`h_prime = h - alpha * r * sum_d(r[d] * h[..., d])`.

Use the last axis as hidden dimension; broadcast `r` over batch and sequence axes; compute the dot product in at least float32 and retain the model activation dtype for the returned tensor. Apply only at one selected residual-stream block output site, across all sequence positions unless the protocol explicitly records a selected-position scope. Preserve tuple/structured block outputs.

Intervention is inference-only, runs under `torch.no_grad()`, validates finite alpha/vector/tensor and hidden dimension, and raises a typed error on mismatch. This is not the original repository’s all-layer block/attention/MLP hook construction; the difference is recorded in `METHOD_DIFFERENCE_TABLE.md`.
