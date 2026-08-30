"""Reduced engineering site-selection helpers."""

from __future__ import annotations

from dataclasses import dataclass


@dataclass(frozen=True, slots=True)
class SiteDiagnostic:
    layer: int
    score: float
    harmless_kl: float
    harmless_addition: float
    accepted: bool


def candidate_layers(block_count: int) -> list[int]:
    if block_count < 1:
        raise ValueError("block_count must be positive")
    boundary = max(0, int(0.8 * block_count) - 1)
    return sorted({0, block_count // 2, boundary})


def select_site(candidates: list[SiteDiagnostic]) -> SiteDiagnostic:
    accepted = [item for item in candidates if item.accepted]
    if not accepted:
        raise RuntimeError("no engineering site candidate passed constraints")
    return min(accepted, key=lambda item: (-item.score, item.layer))
