"""Deterministic blinded XSTest annotation export and unblinding."""

from __future__ import annotations

import hashlib
from dataclasses import dataclass
from typing import Any

LABELS = ("full compliance", "full refusal", "partial refusal")


@dataclass(frozen=True)
class BlindedResponse:
    annotation_id: str
    response_hash: str
    response_text: str


def opaque_annotation_id(condition_id: str, item_id: str, response_hash: str) -> str:
    """Derive an opaque ID; condition metadata is never encoded in the ID."""
    return "ann-" + hashlib.sha256(f"{condition_id}:{item_id}:{response_hash}".encode()).hexdigest()[:20]


def blind_response(condition_id: str, item_id: str, response_text: str) -> tuple[BlindedResponse, dict[str, str]]:
    response_hash = hashlib.sha256(response_text.encode()).hexdigest()
    annotation_id = opaque_annotation_id(condition_id, item_id, response_hash)
    return BlindedResponse(annotation_id, response_hash, response_text), {
        "annotation_id": annotation_id,
        "condition_id": condition_id,
        "item_id": item_id,
    }


def annotation_export(response: BlindedResponse) -> dict[str, str | None]:
    return {
        "annotation_id": response.annotation_id,
        "response_hash": response.response_hash,
        "annotation_label": None,
        "annotation_status": "pending",
        "annotator_notes": None,
    }


def validate_label(label: str | None) -> None:
    if label is not None and label not in LABELS:
        raise ValueError("annotation label is outside the frozen taxonomy")


def unblind_labels(exports: list[dict[str, Any]], mapping: list[dict[str, str]]) -> list[dict[str, Any]]:
    by_id = {m["annotation_id"]: m for m in mapping}
    result = []
    for row in exports:
        validate_label(row.get("annotation_label"))
        if row.get("annotation_status") != "final" or row.get("annotation_label") is None:
            raise ValueError("all labels must be final before unblinding")
        meta = by_id.get(str(row["annotation_id"]))
        if meta is None:
            raise ValueError("annotation ID missing from protected mapping")
        result.append({**row, "condition_id": meta["condition_id"], "item_id": meta["item_id"]})
    return result


def schema() -> dict[str, Any]:
    return {
        "schema_version": "3.4.0",
        "required": ["annotation_id", "response_hash", "annotation_label", "annotation_status", "annotator_notes"],
        "labels": list(LABELS),
        "statuses": ["pending", "final", "ambiguous", "missing"],
        "metadata_visibility": ["annotation_id", "response_hash", "response_text"],
        "hidden_until_final": ["alpha", "intervention_type", "control_seed", "condition_id"],
    }
