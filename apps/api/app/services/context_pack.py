"""Character context pack builder for agent subsets."""

from __future__ import annotations

import uuid
from typing import Literal

from sqlalchemy.ext.asyncio import AsyncSession

from app.exceptions import NotFoundError
from app.models.character import Character
from app.models.enums import CharacterStatus, LedgerEntityType
from app.models.project import Project
from app.repositories.beat import BeatRepository
from app.repositories.chapter import ChapterRepository
from app.repositories.character import CharacterRepository
from app.repositories.ledger import LedgerRepository
from app.schemas.character import (
    Character as CharacterSchema,
)
from app.schemas.character import (
    CharacterContextPackEntry,
    CharacterContextPackRequest,
    CharacterContextPackResponse,
)
from app.utils.character_extractor import extract_mentions_from_text


class CharacterContextPackService:
    def __init__(self, session: AsyncSession) -> None:
        self.session = session
        self.chapters = ChapterRepository(session)
        self.beats = BeatRepository(session)
        self.characters = CharacterRepository(session)
        self.ledger = LedgerRepository(session)

    async def build_context_pack(
        self,
        project: Project,
        payload: CharacterContextPackRequest,
    ) -> CharacterContextPackResponse:
        chapter = await self.chapters.get(project.id, payload.chapter_id)
        if chapter is None:
            raise NotFoundError()

        IncludedReason = Literal["scene_beat", "pov", "t3_principal", "name_hint", "search_match"]
        included: dict[uuid.UUID, IncludedReason] = {}
        stub_count = 0
        truncated = False

        def add_character(character: Character, reason: IncludedReason) -> None:
            nonlocal stub_count, truncated
            if character.id in included:
                return
            if character.status == CharacterStatus.archived:
                return
            if character.tier <= 1 and reason in {"name_hint", "search_match", "scene_beat"}:
                if stub_count >= payload.max_stubs:
                    truncated = True
                    return
                stub_count += 1
            included[character.id] = reason

        # Scene beats — resolve mentions in summaries

        beats = await self.beats.list_for_chapter(payload.chapter_id)
        if payload.beat_ids:
            beat_id_set = set(payload.beat_ids)
            beats = [beat for beat in beats if beat.id in beat_id_set]

        for beat in beats:
            for mention in extract_mentions_from_text(beat.summary):
                match = await self.characters.find_by_name_or_alias(project.id, mention)
                if match:
                    add_character(match, "scene_beat")

        # T3 principals linked to chapter
        t3_rows = await self.characters.list_t3_for_project(project.id)
        for character in t3_rows:
            if character.last_seen_chapter_id == payload.chapter_id:
                add_character(character, "t3_principal")
            elif character.first_seen_chapter_id == payload.chapter_id:
                add_character(character, "t3_principal")

        # Name hints via keyword search
        for hint in payload.name_hints:
            matches = await self.characters.search_keyword(project.id, hint, limit=3)
            for match in matches:
                add_character(match, "name_hint")

        entries: list[CharacterContextPackEntry] = []
        for character_id, reason in included.items():
            character = await self.characters.get_by_id(project.id, character_id)
            if character is None:
                continue
            ledger_tail: list[dict] = []
            if payload.include_ledger_tail and payload.ledger_tail_limit > 0:
                events = await self.ledger.list_tail_for_entity(
                    project.id,
                    LedgerEntityType.character,
                    character_id,
                    limit=payload.ledger_tail_limit,
                )
                ledger_tail = [
                    {
                        "event_type": event.event_type.value,
                        "chapter_number": event.chapter_number,
                        "payload": dict(event.payload or {}),
                    }
                    for event in events
                ]
            entries.append(
                CharacterContextPackEntry(
                    character=CharacterSchema.from_model(character),
                    included_reason=reason,
                    ledger_tail=ledger_tail,
                )
            )

        entries.sort(key=lambda entry: (-entry.character.tier, entry.character.display_name))
        return CharacterContextPackResponse(
            entries=entries,
            truncated=truncated,
            search_mode="keyword",
        )
