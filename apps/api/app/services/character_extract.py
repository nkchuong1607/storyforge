"""Character extraction from chapter prose."""

from __future__ import annotations

import uuid

from sqlalchemy.ext.asyncio import AsyncSession

from app.exceptions import ChapterLockedError, NotFoundError, NotImplementedFeatureError
from app.models.character_provisional import CharacterProvisional
from app.models.enums import ExtractorSource, ProvisionalStatus
from app.models.project import Project
from app.repositories.beat import BeatRepository
from app.repositories.chapter import ChapterRepository
from app.repositories.character import CharacterRepository
from app.repositories.prose import ProseRepository
from app.repositories.provisional import ProvisionalRepository
from app.schemas.character import (
    ExtractCharactersRequest,
    ExtractCharactersResponse,
)
from app.services.chapter_status import is_chapter_locked
from app.services.provisional import ProvisionalService
from app.utils.character_extractor import extract_mentions_from_text, extract_snippet
from app.utils.provisional_fingerprint import compute_mention_fingerprint


class CharacterExtractService:
    def __init__(self, session: AsyncSession) -> None:
        self.session = session
        self.chapters = ChapterRepository(session)
        self.prose = ProseRepository(session)
        self.beats = BeatRepository(session)
        self.characters = CharacterRepository(session)
        self.provisionals = ProvisionalRepository(session)
        self.provisional_service = ProvisionalService(session)

    async def extract_from_chapter(
        self,
        project: Project,
        chapter_id: uuid.UUID,
        payload: ExtractCharactersRequest | None = None,
    ) -> ExtractCharactersResponse:
        request = payload or ExtractCharactersRequest()
        if request.extractor_mode == "llm":
            raise NotImplementedFeatureError("LLM extractor is not enabled in Phase 3")

        chapter = await self.chapters.get(project.id, chapter_id)
        if chapter is None:
            raise NotFoundError()
        if is_chapter_locked(chapter.status):
            raise ChapterLockedError()

        prose_version = request.prose_version or chapter.current_prose_version
        if not prose_version:
            return ExtractCharactersResponse(
                created_count=0,
                skipped_count=0,
                provisionals=[],
            )

        prose = await self.prose.get_version(chapter_id, prose_version)
        if prose is None:
            raise NotFoundError(message="Prose version not found")

        mentions = extract_mentions_from_text(prose.content)
        if request.include_beats:
            beats = await self.beats.list_for_chapter(chapter_id)
            for beat in beats:
                mentions.extend(extract_mentions_from_text(beat.summary))

        # Deduplicate while preserving order
        seen: set[str] = set()
        unique_mentions: list[str] = []
        for mention in mentions:
            key = mention.strip().casefold()
            if key in seen:
                continue
            seen.add(key)
            unique_mentions.append(mention)

        created: list[CharacterProvisional] = []
        skipped_reasons: dict[str, int] = {}

        for mention in unique_mentions:
            skip_reason = await self._skip_reason(project.id, mention, chapter_id)
            if skip_reason:
                skipped_reasons[skip_reason] = skipped_reasons.get(skip_reason, 0) + 1
                continue

            fingerprint = compute_mention_fingerprint(project.id, mention, chapter_id)
            provisional = CharacterProvisional(
                project_id=project.id,
                mention_text=mention.strip(),
                mention_fingerprint=fingerprint,
                chapter_id=chapter_id,
                prose_version=prose_version,
                snippet=extract_snippet(prose.content, mention),
                proposed_fields={
                    "display_name": mention.strip(),
                    "role_one_liner": None,
                    "suggested_tier": 0,
                },
                status=ProvisionalStatus.pending,
                extractor_source=ExtractorSource.heuristic,
            )
            matched = await self.characters.find_by_name_or_alias(project.id, mention)
            if matched:
                provisional.matched_character_id = matched.id

            row = await self.provisionals.create(provisional)
            created.append(row)

        schemas = [await self.provisional_service._to_provisional_schema(row) for row in created]
        skipped_count = sum(skipped_reasons.values())
        return ExtractCharactersResponse(
            created_count=len(created),
            skipped_count=skipped_count,
            skipped_reasons=skipped_reasons,
            provisionals=schemas,
        )

    async def _skip_reason(
        self, project_id: uuid.UUID, mention: str, chapter_id: uuid.UUID
    ) -> str | None:
        existing = await self.characters.find_by_name_or_alias(project_id, mention)
        if existing is not None:
            return "duplicate_name"

        fingerprint = compute_mention_fingerprint(project_id, mention, chapter_id)
        if await self.provisionals.has_pending_fingerprint(project_id, fingerprint):
            return "already_pending"
        return None
