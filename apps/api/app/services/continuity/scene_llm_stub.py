"""Optional FakeLLM scene auditor stub."""

from __future__ import annotations

import json
import uuid
from pathlib import Path

from app.models.enums import ContinuityCategory, ContinuitySeverity
from app.models.scene_beat import SceneBeat
from app.services.continuity.engine import ContinuityIssue

FIXTURE_PATH = Path(__file__).resolve().parents[3] / "tests" / "fixtures" / "scene_llm_audit.json"


async def run_scene_llm_auditor(
    beats: list[SceneBeat], chapter_id: uuid.UUID
) -> list[ContinuityIssue]:
    if not FIXTURE_PATH.exists():
        return []
    data = json.loads(FIXTURE_PATH.read_text(encoding="utf-8"))
    issues: list[ContinuityIssue] = []
    for item in data.get("issues", []):
        beat_id = item.get("beat_id")
        entity_ids = [str(beat_id)] if beat_id else []
        issues.append(
            ContinuityIssue(
                fingerprint=item.get(
                    "fingerprint", f"scene_structure:{chapter_id}:scene_llm_weak_turn"
                ),
                severity=ContinuitySeverity.WARN.value,
                category=ContinuityCategory.scene_structure.value,
                code=item.get("code", "scene_llm_weak_turn"),
                message=item.get("message", "Scene turn weak (stub)"),
                chapter_refs=item.get("chapter_refs", []),
                entity_ids=entity_ids,
                evidence=item.get("evidence", {}),
            )
        )
    return issues
