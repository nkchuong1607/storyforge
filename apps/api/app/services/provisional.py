"""Provisional inbox business logic — merge and reject."""

from __future__ import annotations

import uuid
from datetime import UTC, datetime

from sqlalchemy.ext.asyncio import AsyncSession

from app.exceptions import (
    CharacterArchivedError,
    DuplicateDisplayNameError,
    InvalidMergeRequestError,
    NotFoundError,
    ProvisionalAlreadyResolvedError,
)
from app.models.character import Character
from app.models.enums import CharacterStatus, ProvisionalStatus
from app.models.project import Project
from app.repositories.chapter import ChapterRepository
from app.repositories.character import CharacterRepository
from app.repositories.provisional import ProvisionalRepository
from app.schemas.character import (
    Character as CharacterSchema,
)
from app.schemas.character import (
    CharacterProvisional as ProvisionalSchema,
)
from app.schemas.character import (
    CharacterProvisionalListResponse,
    CharacterProvisionalMergeRequest,
    CharacterProvisionalMergeResponse,
    CharacterProvisionalRejectRequest,
)
from app.services.character import CharacterService
from app.utils.pagination import PageParams, paginated


class ProvisionalService:
    def __init__(self, session: AsyncSession) -> None:
        self.session = session
        self.provisionals = ProvisionalRepository(session)
        self.characters = CharacterRepository(session)
        self.chapters = ChapterRepository(session)
        self.character_service = CharacterService(session)

    async def _to_provisional_schema(
        self, provisional, *, chapter_number: int | None = None
    ) -> ProvisionalSchema:
        if chapter_number is None:
            chapter = await self.chapters.get(provisional.project_id, provisional.chapter_id)
            chapter_number = chapter.number if chapter else None
        return ProvisionalSchema(
            id=provisional.id,
            project_id=provisional.project_id,
            mention_text=provisional.mention_text,
            mention_fingerprint=provisional.mention_fingerprint,
            chapter_id=provisional.chapter_id,
            chapter_number=chapter_number,
            prose_version=provisional.prose_version,
            snippet=provisional.snippet,
            proposed_fields=dict(provisional.proposed_fields or {}),
            status=provisional.status,
            extractor_source=provisional.extractor_source,
            matched_character_id=provisional.matched_character_id,
            merged_character_id=provisional.merged_character_id,
            resolved_at=provisional.resolved_at,
            created_at=provisional.created_at,
        )

    async def list_provisionals(
        self,
        project: Project,
        page: PageParams,
        *,
        status: ProvisionalStatus | None = ProvisionalStatus.pending,
        chapter_id: uuid.UUID | None = None,
    ) -> CharacterProvisionalListResponse:
        items, total = await self.provisionals.list_for_project(
            project.id, page, status=status, chapter_id=chapter_id
        )
        pending_count = await self.provisionals.count_pending(project.id)
        rows = [await self._to_provisional_schema(item) for item in items]
        base = paginated(rows, page.page, page.page_size, total)
        return CharacterProvisionalListResponse(
            items=base.items,
            pagination=base.pagination,
            pending_count=pending_count,
        )

    async def get_provisional(
        self, project: Project, provisional_id: uuid.UUID
    ) -> ProvisionalSchema:
        provisional = await self.provisionals.get_by_id(project.id, provisional_id)
        if provisional is None:
            raise NotFoundError()
        return await self._to_provisional_schema(provisional)

    async def merge_provisional(
        self,
        project: Project,
        provisional_id: uuid.UUID,
        payload: CharacterProvisionalMergeRequest,
        user_id: uuid.UUID,
    ) -> CharacterProvisionalMergeResponse:
        has_target = payload.target_character_id is not None
        if payload.create_new and has_target:
            raise InvalidMergeRequestError()
        if not payload.create_new and not has_target:
            raise InvalidMergeRequestError("Provide target_character_id or create_new=true")

        provisional = await self.provisionals.get_by_id(project.id, provisional_id)
        if provisional is None:
            raise NotFoundError()

        if provisional.status == ProvisionalStatus.rejected:
            raise ProvisionalAlreadyResolvedError()

        if provisional.status == ProvisionalStatus.merged:
            if provisional.merged_character_id is None:
                raise ProvisionalAlreadyResolvedError()
            if has_target and payload.target_character_id != provisional.merged_character_id:
                raise ProvisionalAlreadyResolvedError(
                    "Provisional already merged to a different character"
                )
            character = await self.characters.get_by_id(project.id, provisional.merged_character_id)
            if character is None:
                raise NotFoundError()
            return CharacterProvisionalMergeResponse(
                provisional=await self._to_provisional_schema(provisional),
                character=CharacterSchema.from_model(character),
                idempotent=True,
            )

        if payload.create_new:
            return await self._promote_new(project, provisional, payload, user_id)

        assert payload.target_character_id is not None
        return await self._merge_into_existing(
            project, provisional, payload.target_character_id, user_id
        )

    async def _merge_into_existing(
        self,
        project: Project,
        provisional,
        target_character_id: uuid.UUID,
        user_id: uuid.UUID,
    ) -> CharacterProvisionalMergeResponse:
        character = await self.characters.get_by_id(project.id, target_character_id)
        if character is None:
            raise NotFoundError()
        if character.status == CharacterStatus.archived:
            raise CharacterArchivedError()

        updated = await self.character_service.record_chapter_appearance(
            character,
            provisional.chapter_id,
            provisional.mention_text,
        )

        now = datetime.now(UTC)
        provisional.status = ProvisionalStatus.merged
        provisional.merged_character_id = updated.id
        provisional.resolved_by = user_id
        provisional.resolved_at = now
        await self.session.flush()

        return CharacterProvisionalMergeResponse(
            provisional=await self._to_provisional_schema(provisional),
            character=CharacterSchema.from_model(updated),
            idempotent=False,
        )

    async def _promote_new(
        self,
        project: Project,
        provisional,
        payload: CharacterProvisionalMergeRequest,
        user_id: uuid.UUID,
    ) -> CharacterProvisionalMergeResponse:
        display_name = (payload.display_name or provisional.mention_text).strip()
        if await self.characters.name_exists_for_project(project.id, display_name):
            raise DuplicateDisplayNameError(display_name)

        status = (
            CharacterStatus.established if payload.mark_established else CharacterStatus.provisional
        )
        character = Character(
            project_id=project.id,
            display_name=display_name,
            role_one_liner=provisional.proposed_fields.get("role_one_liner"),
            tier=payload.initial_tier,
            aliases=[],
            status=status,
            psyche_card=None,
            first_seen_chapter_id=provisional.chapter_id,
            last_seen_chapter_id=provisional.chapter_id,
            appearance_count=1,
            merged_from_provisional_id=provisional.id,
        )
        created = await self.characters.create(character)

        now = datetime.now(UTC)
        provisional.status = ProvisionalStatus.merged
        provisional.merged_character_id = created.id
        provisional.resolved_by = user_id
        provisional.resolved_at = now
        await self.session.flush()
        await self.session.refresh(created)

        return CharacterProvisionalMergeResponse(
            provisional=await self._to_provisional_schema(provisional),
            character=CharacterSchema.from_model(created),
            idempotent=False,
        )

    async def reject_provisional(
        self,
        project: Project,
        provisional_id: uuid.UUID,
        payload: CharacterProvisionalRejectRequest | None,
        user_id: uuid.UUID,
    ) -> ProvisionalSchema:
        provisional = await self.provisionals.get_by_id(project.id, provisional_id)
        if provisional is None:
            raise NotFoundError()

        if provisional.status != ProvisionalStatus.pending:
            raise ProvisionalAlreadyResolvedError()

        if payload and payload.reason:
            fields = dict(provisional.proposed_fields or {})
            fields["reject_reason"] = payload.reason
            provisional.proposed_fields = fields

        provisional.status = ProvisionalStatus.rejected
        provisional.resolved_by = user_id
        provisional.resolved_at = datetime.now(UTC)
        await self.session.flush()
        return await self._to_provisional_schema(provisional)
