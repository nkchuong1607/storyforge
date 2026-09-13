"""Settle psych state append unit tests."""

import uuid
from unittest.mock import AsyncMock, MagicMock

import pytest

from app.models.chapter import Chapter
from app.models.continuity import ContinuityReport
from app.models.enums import ChapterStatus, ContinuityResult
from app.models.project import Project
from app.schemas.continuity import SettleChapterRequest
from app.services.settle import SettleService


@pytest.mark.unit
async def test_settle_appends_psych_states(monkeypatch: pytest.MonkeyPatch) -> None:
    project = MagicMock(spec=Project)
    project.id = uuid.uuid4()
    project.bible_version_current = 0
    chapter = MagicMock(spec=Chapter)
    chapter.id = uuid.uuid4()
    chapter.project_id = project.id
    chapter.number = 1
    chapter.title = "Ch1"
    chapter.status = ChapterStatus.reviewing
    char_id = uuid.uuid4()

    report = ContinuityReport(
        id=uuid.uuid4(),
        project_id=project.id,
        chapter_id=chapter.id,
        prose_version=1,
        result=ContinuityResult.PASS,
        issues_json=[],
        state_diff_json={
            "ledger_proposals": [],
            "bible_patch_candidates": [],
            "psyche_card_patches": [
                {
                    "character_id": str(char_id),
                    "patch": {"arc_flags": {"current_arc_beat": "beat1"}},
                }
            ],
            "psych_state_proposals": [
                {
                    "character_id": str(char_id),
                    "chapter_id": str(chapter.id),
                    "stress_level": 6,
                    "dominant_emotion": "anger",
                    "active_goal": "fight",
                    "belief_updates": [],
                    "relationship_stance": [],
                    "trigger_event_refs": ["beat:1"],
                }
            ],
        },
        stats_json={"passed": 1, "warnings": 0, "errors": 0},
        rule_pack_version="test",
        created_by=uuid.uuid4(),
    )

    character = MagicMock()
    character.id = char_id
    character.psyche_card = {"drive": "x"}

    service = SettleService(AsyncMock())
    service.continuity.get_idempotency = AsyncMock(return_value=None)
    service.continuity.get_latest_report = AsyncMock(return_value=report)
    service.continuity.active_override_fingerprints = AsyncMock(return_value=set())
    service.bible.get_version = AsyncMock(return_value=MagicMock(snapshot_json={"entries": []}))
    service.bible.list_all_staging = AsyncMock(return_value=[])
    service.bible.create_version = AsyncMock()
    service.ledger.create = AsyncMock()
    service.characters.get_by_id = AsyncMock(return_value=character)
    service.psych_states.create = AsyncMock()
    service.twists.mark_payoffs_revealed_for_chapter = AsyncMock()
    power_settings = MagicMock(enabled=False)
    service.power.ensure_settings = AsyncMock(return_value=power_settings)
    stakes_settings = MagicMock(enabled=False, act_count=3)
    service.stakes.ensure_settings = AsyncMock(return_value=stakes_settings)
    service.stakes.list_entries = AsyncMock(return_value=[])

    async def fake_insert(*_args, **_kwargs):
        return MagicMock()

    monkeypatch.setattr("app.services.settle.insert_bible_version", fake_insert)

    result = await service.settle_chapter(project, chapter, SettleChapterRequest(), None)
    assert result.psych_states_appended == 1
    service.psych_states.create.assert_awaited_once()
    assert character.psyche_card.get("arc_flags", {}).get("current_arc_beat") == "beat1"
