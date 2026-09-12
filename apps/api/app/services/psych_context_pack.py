"""Psych context pack for scene cast."""

from __future__ import annotations

import uuid
from typing import Literal

from sqlalchemy.ext.asyncio import AsyncSession

from app.exceptions import NotFoundError
from app.models.character import Character
from app.models.project import Project
from app.repositories.beat import BeatRepository
from app.repositories.chapter import ChapterRepository
from app.repositories.character import CharacterRepository
from app.repositories.psych_state import PsychStateRepository
from app.schemas.psychology import (
    PsychContextPackEntry,
    PsychContextPackRequest,
    PsychContextPackResponse,
    psyche_card_from_character,
    psyche_summary_from_card,
)
from app.utils.character_extractor import extract_mentions_from_text


class PsychContextPackService:
    def __init__(self, session: AsyncSession) -> None:
        self.session = session
        self.chapters = ChapterRepository(session)
        self.beats = BeatRepository(session)
        self.characters = CharacterRepository(session)
        self.psych_states = PsychStateRepository(session)

    async def build_context_pack(
        self,
        project: Project,
        payload: PsychContextPackRequest,
    ) -> PsychContextPackResponse:
        chapter = await self.chapters.get(project.id, payload.chapter_id)
        if chapter is None:
            raise NotFoundError()

        IncludedReason = Literal["scene_beat", "pov", "t3_principal", "explicit"]
        included: dict[uuid.UUID, IncludedReason] = {}
        truncated = False

        def add_character(character: Character, reason: IncludedReason) -> None:
            if character.id in included:
                return
            included[character.id] = reason

        beats = await self.beats.list_for_chapter(payload.chapter_id)
        if payload.beat_ids:
            beat_id_set = set(payload.beat_ids)
            beats = [beat for beat in beats if beat.id in beat_id_set]

        for beat in beats:
            for mention in extract_mentions_from_text(beat.summary):
                match = await self.characters.find_by_name_or_alias(project.id, mention)
                if match:
                    add_character(match, "scene_beat")

        for character_id in payload.character_ids:
            character = await self.characters.get_by_id(project.id, character_id)
            if character:
                add_character(character, "explicit")

        if len(included) > 20:
            truncated = True

        entries: list[PsychContextPackEntry] = []
        for character_id, reason in included.items():
            character = await self.characters.get_by_id(project.id, character_id)
            if character is None:
                continue
            card = psyche_card_from_character(character)
            psyche_summary = psyche_summary_from_card(card) if payload.include_psyche_card else None
            latest = await self.psych_states.get_latest_before_chapter(
                project.id, character_id, chapter.number
            )
            latest_payload = None
            if latest and payload.psych_history_limit > 0:
                psych_state, chapter_number = latest
                latest_payload = {
                    "chapter_number": chapter_number,
                    "stress_level": psych_state.stress_level,
                    "dominant_emotion": psych_state.dominant_emotion,
                    "active_goal": psych_state.active_goal,
                }
            entries.append(
                PsychContextPackEntry(
                    character_id=character.id,
                    display_name=character.display_name,
                    tier=character.tier,
                    psyche_summary=psyche_summary,
                    latest_psych_state=latest_payload,
                    included_reason=reason,
                )
            )

        entries.sort(key=lambda entry: (-entry.tier, entry.display_name))
        return PsychContextPackResponse(entries=entries, truncated=truncated)
