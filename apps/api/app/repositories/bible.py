"""Bible data access."""

import uuid

from sqlalchemy import func, select
from sqlalchemy.ext.asyncio import AsyncSession

from app.models.bible import BibleEntryStaging, BibleVersion
from app.models.enums import BibleSection
from app.utils.pagination import PageParams


class BibleRepository:
    def __init__(self, session: AsyncSession) -> None:
        self.session = session

    async def create_version(self, version: BibleVersion) -> BibleVersion:
        self.session.add(version)
        await self.session.flush()
        return version

    async def create_staging_entry(self, entry: BibleEntryStaging) -> BibleEntryStaging:
        self.session.add(entry)
        await self.session.flush()
        return entry

    async def get_staging_entry(
        self, project_id: uuid.UUID, entry_id: uuid.UUID
    ) -> BibleEntryStaging | None:
        return await self.session.scalar(
            select(BibleEntryStaging).where(
                BibleEntryStaging.id == entry_id,
                BibleEntryStaging.project_id == project_id,
            )
        )

    async def entry_key_exists(self, project_id: uuid.UUID, entry_key: str) -> bool:
        result = await self.session.scalar(
            select(BibleEntryStaging.id).where(
                BibleEntryStaging.project_id == project_id,
                BibleEntryStaging.entry_key == entry_key,
            )
        )
        return result is not None

    async def list_staging_entries(
        self,
        project_id: uuid.UUID,
        *,
        section: BibleSection | None,
        page: PageParams,
    ) -> tuple[list[BibleEntryStaging], int]:
        filters = [BibleEntryStaging.project_id == project_id]
        if section is not None:
            filters.append(BibleEntryStaging.section == section)

        base = (
            select(BibleEntryStaging)
            .where(*filters)
            .order_by(BibleEntryStaging.section, BibleEntryStaging.title)
        )
        total = int(
            await self.session.scalar(
                select(func.count()).select_from(BibleEntryStaging).where(*filters)
            )
            or 0
        )
        rows = await self.session.scalars(base.offset(page.offset).limit(page.page_size))
        return list(rows.all()), total

    async def update_staging_entry(self, entry: BibleEntryStaging) -> BibleEntryStaging:
        await self.session.flush()
        return entry

    async def delete_staging_entry(self, entry: BibleEntryStaging) -> None:
        await self.session.delete(entry)
        await self.session.flush()

    async def list_versions(
        self, project_id: uuid.UUID, page: PageParams
    ) -> tuple[list[BibleVersion], int]:
        base = (
            select(BibleVersion)
            .where(BibleVersion.project_id == project_id)
            .order_by(BibleVersion.version.desc())
        )
        total = int(
            await self.session.scalar(
                select(func.count())
                .select_from(BibleVersion)
                .where(BibleVersion.project_id == project_id)
            )
            or 0
        )
        rows = await self.session.scalars(base.offset(page.offset).limit(page.page_size))
        return list(rows.all()), total

    async def get_version(self, project_id: uuid.UUID, version: int) -> BibleVersion | None:
        return await self.session.scalar(
            select(BibleVersion).where(
                BibleVersion.project_id == project_id,
                BibleVersion.version == version,
            )
        )

    async def get_version_snapshot_entry_count(self, snapshot_json: dict) -> int:
        entries = snapshot_json.get("entries", [])
        return len(entries) if isinstance(entries, list) else 0

    async def list_all_staging(self, project_id: uuid.UUID) -> list[BibleEntryStaging]:
        rows = await self.session.scalars(
            select(BibleEntryStaging).where(BibleEntryStaging.project_id == project_id)
        )
        return list(rows.all())
