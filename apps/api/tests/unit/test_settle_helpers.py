"""Settle helper unit tests."""

import uuid
from unittest.mock import AsyncMock, MagicMock

import pytest

from app.models.bible import BibleEntryStaging
from app.models.enums import BibleSection
from app.services.settle import SettleService


@pytest.mark.unit
async def test_reconcile_staging_deletes_merged_rows() -> None:
    service = SettleService(AsyncMock())
    row = BibleEntryStaging(
        project_id=uuid.uuid4(),
        entry_key="world_rules.test",
        section=BibleSection.world_rules,
        title="T",
        content_md="same",
        base_bible_version=0,
        created_by=uuid.uuid4(),
    )
    service.bible.list_all_staging = AsyncMock(return_value=[row])
    service.bible.delete_staging_entry = AsyncMock()
    snapshot = {
        "entries": [
            {"entry_key": "world_rules.test", "content_md": "same"},
        ]
    }
    await service._reconcile_staging(row.project_id, snapshot, 1)
    service.bible.delete_staging_entry.assert_awaited_once_with(row)


@pytest.mark.unit
async def test_settle_cached_idempotency() -> None:
    from datetime import UTC, datetime

    from app.models.enums import ChapterStatus
    from app.schemas.continuity import SettleChapterResponse

    service = SettleService(AsyncMock())
    chapter_id = uuid.uuid4()
    key = uuid.uuid4()
    cached = MagicMock()
    cached.response_json = SettleChapterResponse(
        chapter_id=chapter_id,
        status=ChapterStatus.locked,
        bible_version_before=0,
        bible_version_after=1,
        ledger_events_appended=0,
        settled_at=datetime.now(UTC),
    ).model_dump(mode="json")
    service.continuity.get_idempotency = AsyncMock(return_value=cached)
    result = await service._get_cached_response(chapter_id, key)
    assert result is not None
    assert result.status == ChapterStatus.locked
