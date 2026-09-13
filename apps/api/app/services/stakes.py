"""Stakes ledger business logic."""

from __future__ import annotations

import uuid
from datetime import UTC, datetime

from sqlalchemy.ext.asyncio import AsyncSession

from app.exceptions import InvalidActNumberError, NotFoundError
from app.models.project import Project
from app.models.stakes_ledger_entry import StakesLedgerEntry
from app.repositories.chapter import ChapterRepository
from app.repositories.stakes import StakesRepository
from app.schemas.stakes import (
    ActStructureSettings as ActStructureSettingsSchema,
)
from app.schemas.stakes import (
    ActStructureSettingsUpdateRequest,
    StakesBoardActColumn,
    StakesBoardResponse,
    StakesBoardWarnings,
    StakesEntryCreateRequest,
    StakesEntryListResponse,
    StakesEntryUpdateRequest,
)
from app.schemas.stakes import (
    StakesLedgerEntry as StakesLedgerEntrySchema,
)
from app.services.continuity.stakes import resolve_act_for_chapter


class StakesService:
    def __init__(self, session: AsyncSession) -> None:
        self.session = session
        self.stakes = StakesRepository(session)
        self.chapters = ChapterRepository(session)

    async def get_settings(self, project: Project) -> ActStructureSettingsSchema:
        row = await self.stakes.ensure_settings(project.id)
        return ActStructureSettingsSchema.model_validate(row)

    async def update_settings(
        self, project: Project, payload: ActStructureSettingsUpdateRequest
    ) -> ActStructureSettingsSchema:
        row = await self.stakes.ensure_settings(project.id)
        data = payload.model_dump(exclude_unset=True)
        if "chapters_per_act" in data and data["chapters_per_act"] is not None:
            data["chapters_per_act"] = [
                item.model_dump() for item in payload.chapters_per_act or []
            ]
        for key, value in data.items():
            setattr(row, key, value)
        row.updated_at = datetime.now(UTC)
        await self.session.flush()
        await self.session.refresh(row)
        return ActStructureSettingsSchema.model_validate(row)

    def _validate_act_number(self, act_number: int, settings_row) -> None:
        if act_number < 1 or act_number > settings_row.act_count:
            raise InvalidActNumberError()

    async def list_entries(self, project: Project) -> StakesEntryListResponse:
        rows = await self.stakes.list_entries(project.id)
        return StakesEntryListResponse(
            items=[StakesLedgerEntrySchema.model_validate(r) for r in rows]
        )

    async def create_entry(
        self, project: Project, payload: StakesEntryCreateRequest
    ) -> StakesLedgerEntrySchema:
        settings = await self.stakes.ensure_settings(project.id)
        self._validate_act_number(payload.act_number, settings)
        existing = await self.stakes.get_by_checkpoint(
            project.id, payload.act_number, payload.checkpoint_key
        )
        if existing is not None:
            from app.exceptions import ValidationAppError

            raise ValidationAppError(
                message=(
                    f"Checkpoint {payload.checkpoint_key} already exists "
                    f"for act {payload.act_number}"
                )
            )
        entry = StakesLedgerEntry(
            project_id=project.id,
            act_number=payload.act_number,
            checkpoint_key=payload.checkpoint_key,
            title=payload.title,
            description_md=payload.description_md or "",
            target_level=payload.target_level,
            sort_order=payload.sort_order,
            linked_twist_id=payload.linked_twist_id,
        )
        created = await self.stakes.create_entry(entry)
        await self.session.refresh(created)
        return StakesLedgerEntrySchema.model_validate(created)

    async def get_entry(self, project: Project, entry_id: uuid.UUID) -> StakesLedgerEntrySchema:
        entry = await self.stakes.get_entry(project.id, entry_id)
        if entry is None:
            raise NotFoundError()
        return StakesLedgerEntrySchema.model_validate(entry)

    async def update_entry(
        self,
        project: Project,
        entry_id: uuid.UUID,
        payload: StakesEntryUpdateRequest,
    ) -> StakesLedgerEntrySchema:
        entry = await self.stakes.get_entry(project.id, entry_id)
        if entry is None:
            raise NotFoundError()
        data = payload.model_dump(exclude_unset=True)
        if "status" in data and data["status"] is not None:
            data["status"] = (
                data["status"].value if hasattr(data["status"], "value") else data["status"]
            )
        for key, value in data.items():
            if key.endswith("_chapter_id") and value is not None:
                chapter = await self.chapters.get(project.id, value)
                if chapter is None:
                    raise NotFoundError(message="Chapter not found")
            setattr(entry, key, value)
        entry.updated_at = datetime.now(UTC)
        await self.stakes.update_entry(entry)
        await self.session.refresh(entry)
        return StakesLedgerEntrySchema.model_validate(entry)

    async def delete_entry(self, project: Project, entry_id: uuid.UUID) -> None:
        entry = await self.stakes.get_entry(project.id, entry_id)
        if entry is None:
            raise NotFoundError()
        await self.stakes.delete_entry(entry)

    async def get_board(self, project: Project) -> StakesBoardResponse:
        settings = await self.stakes.ensure_settings(project.id)
        entries = await self.stakes.list_entries(project.id)
        acts: list[StakesBoardActColumn] = []
        boundaries = settings.chapters_per_act or []

        for act_num in range(1, settings.act_count + 1):
            label = None
            start_ch = None
            end_ch = None
            for item in boundaries:
                if int(item.get("act_number", 0)) == act_num:
                    label = item.get("label")
                    start_ch = item.get("start_chapter")
                    end_ch = item.get("end_chapter")
                    break
            act_entries = [e for e in entries if e.act_number == act_num]
            acts.append(
                StakesBoardActColumn(
                    act_number=act_num,
                    label=label,
                    start_chapter=start_ch,
                    end_chapter=end_ch,
                    entries=[StakesLedgerEntrySchema.model_validate(e) for e in act_entries],
                )
            )

        flat_middle = any(
            e.status == "planned"
            for e in entries
            if e.act_number == max(1, settings.act_count // 2)
        )
        open_fail = sum(
            1 for e in entries if e.status == "planted" and e.resolve_chapter_id is None
        )

        return StakesBoardResponse(
            settings={"act_count": settings.act_count, "enabled": settings.enabled},
            acts=acts,
            warnings=StakesBoardWarnings(flat_middle=flat_middle, open_fail_count=open_fail),
        )

    async def act_for_chapter(self, project: Project, chapter_number: int) -> int:
        settings = await self.stakes.ensure_settings(project.id)
        act_number, _, _ = resolve_act_for_chapter(chapter_number, settings)
        return act_number
