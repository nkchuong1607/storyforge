"""Psyche card and PsychState timeline services."""

from __future__ import annotations

import uuid
from datetime import UTC, datetime

from sqlalchemy.ext.asyncio import AsyncSession

from app.exceptions import (
    InvalidPsycheCardError,
    NotFoundError,
    PsychStateImmutableError,
    TierRequirementsNotMetError,
)
from app.models.character import Character
from app.models.project import Project
from app.repositories.chapter import ChapterRepository
from app.repositories.character import CharacterRepository
from app.repositories.psych_state import PsychStateRepository
from app.schemas.psychology import (
    PsycheCard,
    PsycheCardResponse,
    PsycheCardUpdateRequest,
    PsychStateListResponse,
    PsychStateSchema,
    psyche_card_from_character,
)
from app.utils.pagination import PageParams, paginated
from app.utils.psyche_validation import merge_psyche_card, validate_psyche_card_for_tier


class PsychologyService:
    def __init__(self, session: AsyncSession) -> None:
        self.session = session
        self.characters = CharacterRepository(session)
        self.chapters = ChapterRepository(session)
        self.psych_states = PsychStateRepository(session)

    async def _get_character(self, project_id: uuid.UUID, character_id: uuid.UUID) -> Character:
        character = await self.characters.get_by_id(project_id, character_id)
        if character is None:
            raise NotFoundError()
        return character

    async def get_psyche_card(
        self, project: Project, character_id: uuid.UUID
    ) -> PsycheCardResponse:
        character = await self._get_character(project.id, character_id)
        return PsycheCardResponse(
            character_id=character.id,
            project_id=project.id,
            tier=character.tier,
            psyche_card=psyche_card_from_character(character),
            updated_at=character.updated_at,
        )

    async def update_psyche_card(
        self,
        project: Project,
        character_id: uuid.UUID,
        payload: PsycheCardUpdateRequest,
    ) -> PsycheCardResponse:
        character = await self._get_character(project.id, character_id)
        merged = merge_psyche_card(character.psyche_card, payload.psyche_card)
        details = validate_psyche_card_for_tier(tier=character.tier, psyche_card=merged)
        if details:
            if character.tier >= 3:
                raise InvalidPsycheCardError(
                    "T3 characters must retain value_hierarchy and moral_boundaries",
                    details,
                )
            raise TierRequirementsNotMetError(
                "Psyche card does not meet tier requirements",
                details,
            )
        character.psyche_card = merged
        character.updated_at = datetime.now(UTC)
        await self.session.flush()
        await self.session.refresh(character)
        return PsycheCardResponse(
            character_id=character.id,
            project_id=project.id,
            tier=character.tier,
            psyche_card=PsycheCard.model_validate(merged),
            updated_at=character.updated_at,
        )

    async def list_psych_states(
        self,
        project: Project,
        character_id: uuid.UUID,
        page: PageParams,
        *,
        from_chapter_number: int | None = None,
        to_chapter_number: int | None = None,
    ) -> PsychStateListResponse:
        await self._get_character(project.id, character_id)
        rows, total = await self.psych_states.list_timeline(
            project.id,
            character_id,
            page,
            from_chapter_number=from_chapter_number,
            to_chapter_number=to_chapter_number,
        )
        items = [
            PsychStateSchema.from_model(row, chapter_number=chapter_number)
            for row, chapter_number in rows
        ]
        return paginated(items, page.page, page.page_size, total)

    async def get_psych_state_by_chapter(
        self,
        project: Project,
        character_id: uuid.UUID,
        chapter_id: uuid.UUID,
    ) -> PsychStateSchema:
        await self._get_character(project.id, character_id)
        chapter = await self.chapters.get(project.id, chapter_id)
        if chapter is None:
            raise NotFoundError()
        row = await self.psych_states.get_by_character_chapter(project.id, character_id, chapter_id)
        if row is None:
            raise NotFoundError(message="No settled psych state for this chapter")
        return PsychStateSchema.from_model(row, chapter_number=chapter.number)

    async def attempt_update_psych_state(
        self,
        project: Project,
        character_id: uuid.UUID,
        psych_state_id: uuid.UUID,
        *,
        stress_level: int,
    ) -> None:
        """Reject mutation of settled psych states (409 psych_state_immutable)."""
        character = await self._get_character(project.id, character_id)
        row = await self.psych_states.get_by_id(project.id, psych_state_id)
        if row is None or row.character_id != character.id:
            raise NotFoundError()
        self.psych_states.assert_immutable(row)
        row.stress_level = stress_level
        raise PsychStateImmutableError()
