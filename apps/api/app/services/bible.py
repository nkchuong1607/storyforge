"""Bible staging and version business logic."""

import uuid

from sqlalchemy.ext.asyncio import AsyncSession

from app.exceptions import EntryKeyConflictError, NotFoundError
from app.models.bible import BibleEntryStaging
from app.models.enums import BibleSection
from app.models.project import Project
from app.repositories.bible import BibleRepository
from app.schemas.bible import (
    BibleEntry,
    BibleEntryCreateRequest,
    BibleEntryUpdateRequest,
    BibleVersionDetail,
    BibleVersionSummary,
)
from app.utils.pagination import PageParams, paginated


class BibleService:
    def __init__(self, session: AsyncSession) -> None:
        self.session = session
        self.bible = BibleRepository(session)

    async def list_entries(
        self,
        project: Project,
        *,
        section: BibleSection | None,
        page: PageParams,
    ):
        items, total = await self.bible.list_staging_entries(project.id, section=section, page=page)
        entries = [BibleEntry.from_orm_entry(item) for item in items]
        return paginated(entries, page.page, page.page_size, total)

    async def create_entry(
        self,
        project: Project,
        user_id: uuid.UUID,
        payload: BibleEntryCreateRequest,
    ) -> BibleEntry:
        if await self.bible.entry_key_exists(project.id, payload.entry_key):
            raise EntryKeyConflictError(payload.entry_key)

        entry = BibleEntryStaging(
            project_id=project.id,
            entry_key=payload.entry_key,
            section=payload.section,
            title=payload.title,
            content_md=payload.content_md,
            metadata_=payload.metadata,
            base_bible_version=project.bible_version_current,
            created_by=user_id,
        )
        created = await self.bible.create_staging_entry(entry)
        await self.session.refresh(created)
        return BibleEntry.from_orm_entry(created)

    async def get_entry(self, project: Project, entry_id: uuid.UUID) -> BibleEntry:
        entry = await self.bible.get_staging_entry(project.id, entry_id)
        if entry is None:
            raise NotFoundError()
        return BibleEntry.from_orm_entry(entry)

    async def update_entry(
        self,
        project: Project,
        entry_id: uuid.UUID,
        payload: BibleEntryUpdateRequest,
    ) -> BibleEntry:
        entry = await self.bible.get_staging_entry(project.id, entry_id)
        if entry is None:
            raise NotFoundError()
        if payload.title is not None:
            entry.title = payload.title
        if payload.content_md is not None:
            entry.content_md = payload.content_md
        if payload.metadata is not None:
            entry.metadata_ = payload.metadata
        if payload.section is not None:
            entry.section = payload.section
        updated = await self.bible.update_staging_entry(entry)
        await self.session.refresh(updated)
        return BibleEntry.from_orm_entry(updated)

    async def delete_entry(self, project: Project, entry_id: uuid.UUID) -> None:
        entry = await self.bible.get_staging_entry(project.id, entry_id)
        if entry is None:
            raise NotFoundError()
        await self.bible.delete_staging_entry(entry)

    async def list_versions(self, project: Project, page: PageParams):
        items, total = await self.bible.list_versions(project.id, page)
        summaries = [
            BibleVersionSummary(
                version=item.version,
                settled_from_chapter_id=item.settled_from_chapter_id,
                created_at=item.created_at,
                entry_count=await self.bible.get_version_snapshot_entry_count(item.snapshot_json),
            )
            for item in items
        ]
        return paginated(summaries, page.page, page.page_size, total)

    async def get_version(self, project: Project, version: int) -> BibleVersionDetail:
        row = await self.bible.get_version(project.id, version)
        if row is None:
            raise NotFoundError()
        entry_count = await self.bible.get_version_snapshot_entry_count(row.snapshot_json)
        return BibleVersionDetail(
            version=row.version,
            settled_from_chapter_id=row.settled_from_chapter_id,
            created_at=row.created_at,
            entry_count=entry_count,
            project_id=row.project_id,
            snapshot_json=row.snapshot_json,
        )
