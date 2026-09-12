"""Direct service-layer unit tests."""

import uuid
from datetime import UTC, datetime
from unittest.mock import AsyncMock, MagicMock

import pytest

from app.exceptions import EntryKeyConflictError, NotFoundError
from app.models.enums import BibleSection
from app.models.project import Project
from app.schemas.bible import BibleEntryCreateRequest, BibleEntryUpdateRequest
from app.services.bible import BibleService
from app.services.project import ProjectService


def _staging_entry_mock() -> MagicMock:
    entry = MagicMock()
    entry.id = uuid.uuid4()
    entry.project_id = uuid.uuid4()
    entry.entry_key = "world_rules.test"
    entry.section = BibleSection.glossary
    entry.title = "Old"
    entry.content_md = "old"
    entry.metadata_ = {}
    entry.base_bible_version = 0
    entry.created_by = uuid.uuid4()
    entry.created_at = datetime.now(tz=UTC)
    entry.updated_at = datetime.now(tz=UTC)
    return entry


@pytest.mark.unit
async def test_bible_service_create_entry_conflict() -> None:
    session = AsyncMock()
    service = BibleService(session)
    service.bible.entry_key_exists = AsyncMock(return_value=True)
    project = Project(
        slug="p",
        title="P",
        created_by=uuid.uuid4(),
    )
    project.id = uuid.uuid4()
    project.bible_version_current = 0

    with pytest.raises(EntryKeyConflictError):
        await service.create_entry(
            project,
            uuid.uuid4(),
            BibleEntryCreateRequest(
                entry_key="a.b",
                section=BibleSection.world_rules,
                title="T",
            ),
        )


@pytest.mark.unit
async def test_bible_service_get_entry_missing() -> None:
    session = AsyncMock()
    service = BibleService(session)
    service.bible.get_staging_entry = AsyncMock(return_value=None)
    project = Project(slug="p", title="P", created_by=uuid.uuid4())
    project.id = uuid.uuid4()

    with pytest.raises(NotFoundError):
        await service.get_entry(project, uuid.uuid4())


@pytest.mark.unit
async def test_bible_service_update_entry() -> None:
    session = AsyncMock()
    service = BibleService(session)
    entry = _staging_entry_mock()
    service.bible.get_staging_entry = AsyncMock(return_value=entry)
    service.bible.update_staging_entry = AsyncMock(return_value=entry)
    session.refresh = AsyncMock()

    project = Project(slug="p", title="P", created_by=uuid.uuid4())
    project.id = uuid.uuid4()

    result = await service.update_entry(
        project,
        uuid.uuid4(),
        BibleEntryUpdateRequest(title="New", content_md="new", metadata={"x": 1}),
    )
    assert result.title == "New"


@pytest.mark.unit
async def test_project_service_suggest_slug() -> None:
    session = AsyncMock()
    service = ProjectService(session)
    service.projects.slug_exists = AsyncMock(side_effect=[True, True, False])

    suggested = await service._suggest_slug("base")
    assert suggested == "base-4"
