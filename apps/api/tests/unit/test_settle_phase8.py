"""Settle Phase 8 relationship and stakes append tests."""

import uuid
from types import SimpleNamespace
from unittest.mock import AsyncMock, MagicMock

import pytest

from app.models.chapter import Chapter
from app.models.enums import ChapterStatus
from app.models.project import Project
from app.models.relationship import Relationship
from app.models.stakes_ledger_entry import StakesLedgerEntry
from app.schemas.continuity import SettleChapterRequest
from app.services.settle import SettleService


@pytest.mark.unit
async def test_settle_appends_relationship_and_stakes_events(
    monkeypatch: pytest.MonkeyPatch,
) -> None:
    project = MagicMock(spec=Project)
    project.id = uuid.uuid4()
    project.bible_version_current = 0
    chapter = MagicMock(spec=Chapter)
    chapter.id = uuid.uuid4()
    chapter.project_id = project.id
    chapter.number = 1
    chapter.status = ChapterStatus.reviewing

    rel_id = uuid.uuid4()
    entry_id = uuid.uuid4()
    report = SimpleNamespace(
        prose_version=1,
        issues_json=[],
        state_diff_json={
            "ledger_proposals": [],
            "bible_patch_candidates": [],
            "relationship_event_proposals": [
                {
                    "relationship_id": str(rel_id),
                    "event_type": "betrayal",
                    "intensity_delta": -2,
                    "relation_type_after": "enemy",
                    "payload": {},
                }
            ],
            "stakes_ledger_proposals": [
                {
                    "entry_id": str(entry_id),
                    "status": "planted",
                    "target_level": 4,
                }
            ],
        },
    )

    rel = Relationship(
        project_id=project.id,
        character_a_id=uuid.uuid4(),
        character_b_id=uuid.uuid4(),
        relation_type="rival",
        baseline_intensity=0,
    )
    rel.id = rel_id
    entry = StakesLedgerEntry(
        project_id=project.id,
        act_number=1,
        checkpoint_key="k",
        title="t",
        target_level=2,
        status="planned",
    )
    entry.id = entry_id

    service = SettleService(AsyncMock())
    service.continuity.get_idempotency = AsyncMock(return_value=None)
    service.continuity.get_latest_report = AsyncMock(return_value=report)
    service.continuity.active_override_fingerprints = AsyncMock(return_value=set())
    service.bible.get_version = AsyncMock(return_value=MagicMock(snapshot_json={"entries": []}))
    service.bible.list_all_staging = AsyncMock(return_value=[])
    service.bible.create_version = AsyncMock()
    service.ledger.create = AsyncMock()
    service.relationships.get = AsyncMock(return_value=rel)
    service.relationships.list_events = AsyncMock(return_value=[])
    service.relationships.create_event = AsyncMock()
    service.stakes.get_entry = AsyncMock(return_value=entry)
    service.stakes.update_entry = AsyncMock()
    service.stakes.ensure_settings = AsyncMock(return_value=MagicMock(enabled=True, act_count=3))
    service.stakes.list_entries = AsyncMock(return_value=[entry])
    service.twists.mark_payoffs_revealed_for_chapter = AsyncMock()
    service.power.ensure_settings = AsyncMock(return_value=MagicMock(enabled=False))
    service.power.list_ranks = AsyncMock(return_value=[])
    service.power.list_techniques = AsyncMock(return_value=[])

    async def _fake_insert(*_args, **_kwargs):
        return MagicMock()

    monkeypatch.setattr("app.services.settle.insert_bible_version", _fake_insert)

    response = await service.settle_chapter(
        project, chapter, SettleChapterRequest(approve_state_diff=True), None
    )
    assert response.relationship_events_appended == 1
    assert response.stakes_entries_updated == 1
    assert "world.stakes" in response.snapshot_includes
