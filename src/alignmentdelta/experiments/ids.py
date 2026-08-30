"""Unique concrete execution identities."""

from __future__ import annotations

from datetime import UTC, datetime
from uuid import uuid4


def new_run_id() -> str:
    """Create a human-readable ID with timestamp and UUID entropy."""
    timestamp = datetime.now(UTC).strftime("%Y%m%dT%H%M%S%fZ")
    return f"run-{timestamp}-{uuid4().hex[:12]}"
