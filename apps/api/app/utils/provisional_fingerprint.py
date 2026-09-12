"""Provisional mention fingerprint."""

from __future__ import annotations

import hashlib
import uuid


def compute_mention_fingerprint(
    project_id: uuid.UUID, mention_text: str, chapter_id: uuid.UUID
) -> str:
    normalized = mention_text.strip().casefold()
    payload = f"{project_id}:{normalized}:{chapter_id}"
    return hashlib.sha256(payload.encode("utf-8")).hexdigest()
