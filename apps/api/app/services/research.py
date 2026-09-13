"""Research notes business logic."""

from __future__ import annotations

import uuid
from datetime import UTC, datetime

from sqlalchemy.exc import IntegrityError
from sqlalchemy.ext.asyncio import AsyncSession

from app.exceptions import (
    InvalidBibleSectionError,
    InvalidLinkTargetError,
    NoteNotEditableError,
    NotFoundError,
    ResearchLinkDuplicateError,
)
from app.models.bible import BibleEntryStaging
from app.models.enums import Phase9BibleSection, ResearchNoteLinkType, ResearchNoteStatus
from app.models.project import Project
from app.models.research import ResearchNote, ResearchNoteLink
from app.repositories.bible import BibleRepository
from app.repositories.chapter import ChapterRepository
from app.repositories.character import CharacterRepository
from app.repositories.research import ResearchRepository
from app.schemas.research import (
    ResearchNote as ResearchNoteSchema,
)
from app.schemas.research import (
    ResearchNoteCreateRequest,
    ResearchNoteDetail,
    ResearchNoteLinkCreateRequest,
    ResearchNoteSearchHit,
    ResearchNoteSearchResponse,
    ResearchNoteUpdateRequest,
    ResearchPromoteRequest,
    ResearchPromoteResponse,
)
from app.schemas.research import (
    ResearchNoteLink as ResearchNoteLinkSchema,
)
from app.utils.pagination import PageParams, paginated
from app.utils.phase9_bible import (
    build_entry_key,
    phase9_section_to_bible_section,
    validate_bible_key,
)


class ResearchService:
    def __init__(self, session: AsyncSession) -> None:
        self.session = session
        self.research = ResearchRepository(session)
        self.bible = BibleRepository(session)
        self.characters = CharacterRepository(session)
        self.chapters = ChapterRepository(session)

    def _note_schema(self, note: ResearchNote) -> ResearchNoteSchema:
        return ResearchNoteSchema(
            id=note.id,
            project_id=note.project_id,
            title=note.title,
            body_md=note.body_md,
            source_url=note.source_url,
            tags=list(note.tags or []),
            status=ResearchNoteStatus(note.status),
            promoted_to_staging_id=note.promoted_to_staging_id,
            promoted_at=note.promoted_at,
            created_at=note.created_at,
            updated_at=note.updated_at,
        )

    async def list_notes(
        self,
        project: Project,
        *,
        status: ResearchNoteStatus | None,
        tag: str | None,
        page: PageParams,
    ):
        items, total = await self.research.list_notes(
            project.id, status=status.value if status else None, tag=tag, page=page
        )
        return paginated([self._note_schema(n) for n in items], page.page, page.page_size, total)

    async def create_note(
        self, project: Project, payload: ResearchNoteCreateRequest
    ) -> ResearchNoteSchema:
        note = ResearchNote(
            project_id=project.id,
            title=payload.title,
            body_md=payload.body_md,
            source_url=payload.source_url,
            tags=payload.tags,
            status=ResearchNoteStatus.active.value,
        )
        created = await self.research.create_note(note)
        await self.session.refresh(created)
        return self._note_schema(created)

    async def get_note(self, project: Project, note_id: uuid.UUID) -> ResearchNoteDetail:
        note = await self.research.get_note(project.id, note_id)
        if note is None:
            raise NotFoundError()
        links = await self.research.list_links(note_id)
        detail = ResearchNoteDetail(**self._note_schema(note).model_dump())
        detail.links = [
            ResearchNoteLinkSchema(
                id=link.id,
                note_id=link.note_id,
                link_type=ResearchNoteLinkType(link.link_type),
                character_id=link.character_id,
                bible_key=link.bible_key,
                chapter_id=link.chapter_id,
                created_at=link.created_at,
            )
            for link in links
        ]
        return detail

    async def update_note(
        self, project: Project, note_id: uuid.UUID, payload: ResearchNoteUpdateRequest
    ) -> ResearchNoteSchema:
        note = await self.research.get_note(project.id, note_id)
        if note is None:
            raise NotFoundError()
        if note.status != ResearchNoteStatus.active.value:
            raise NoteNotEditableError()
        if payload.title is not None:
            note.title = payload.title
        if payload.body_md is not None:
            note.body_md = payload.body_md
        if payload.source_url is not None:
            note.source_url = payload.source_url
        if payload.tags is not None:
            note.tags = payload.tags
        updated = await self.research.update_note(note)
        await self.session.refresh(updated)
        return self._note_schema(updated)

    async def archive_note(self, project: Project, note_id: uuid.UUID) -> None:
        note = await self.research.get_note(project.id, note_id)
        if note is None:
            raise NotFoundError()
        if note.status == ResearchNoteStatus.promoted.value:
            raise NoteNotEditableError()
        note.status = ResearchNoteStatus.archived.value
        await self.research.update_note(note)

    async def search_notes(
        self,
        project: Project,
        *,
        query: str,
        status: ResearchNoteStatus | None,
        tag: str | None,
        page: PageParams,
    ):
        hits, total = await self.research.search_notes(
            project.id,
            query_text=query,
            status=status.value if status else None,
            tag=tag,
            page=page,
        )
        items = [
            ResearchNoteSearchHit(note=self._note_schema(note), rank=rank, snippet=snippet)
            for note, rank, snippet in hits
        ]
        return ResearchNoteSearchResponse(
            query=query,
            items=items,
            page=page.page,
            page_size=page.page_size,
            total=total,
        )

    async def _validate_link(
        self, project: Project, payload: ResearchNoteLinkCreateRequest
    ) -> None:
        if payload.link_type == ResearchNoteLinkType.character:
            if payload.character_id is None:
                raise InvalidLinkTargetError("character_id required for character link")
            char = await self.characters.get_by_id(project.id, payload.character_id)
            if char is None:
                raise NotFoundError()
        elif payload.link_type in (ResearchNoteLinkType.place, ResearchNoteLinkType.fact):
            if not payload.bible_key or not validate_bible_key(payload.bible_key):
                raise InvalidLinkTargetError("Valid bible_key required for place/fact link")
        elif payload.link_type == ResearchNoteLinkType.chapter:
            if payload.chapter_id is None:
                raise InvalidLinkTargetError("chapter_id required for chapter link")
            chapter = await self.chapters.get(project.id, payload.chapter_id)
            if chapter is None:
                raise NotFoundError()
        else:
            raise InvalidLinkTargetError()

    async def add_link(
        self,
        project: Project,
        note_id: uuid.UUID,
        payload: ResearchNoteLinkCreateRequest,
    ) -> ResearchNoteLinkSchema:
        note = await self.research.get_note(project.id, note_id)
        if note is None:
            raise NotFoundError()
        await self._validate_link(project, payload)
        link = ResearchNoteLink(
            project_id=project.id,
            note_id=note_id,
            link_type=payload.link_type.value,
            character_id=payload.character_id,
            bible_key=payload.bible_key,
            chapter_id=payload.chapter_id,
        )
        try:
            created = await self.research.create_link(link)
        except IntegrityError as exc:
            raise ResearchLinkDuplicateError() from exc
        await self.session.refresh(created)
        return ResearchNoteLinkSchema(
            id=created.id,
            note_id=created.note_id,
            link_type=ResearchNoteLinkType(created.link_type),
            character_id=created.character_id,
            bible_key=created.bible_key,
            chapter_id=created.chapter_id,
            created_at=created.created_at,
        )

    async def remove_link(self, project: Project, note_id: uuid.UUID, link_id: uuid.UUID) -> None:
        link = await self.research.get_link(project.id, note_id, link_id)
        if link is None:
            raise NotFoundError()
        await self.research.delete_link(link)

    async def promote_note(
        self,
        project: Project,
        user_id: uuid.UUID,
        note_id: uuid.UUID,
        payload: ResearchPromoteRequest,
    ) -> ResearchPromoteResponse:
        note = await self.research.get_note(project.id, note_id)
        if note is None:
            raise NotFoundError()
        if note.status == ResearchNoteStatus.promoted.value and note.promoted_to_staging_id:
            return ResearchPromoteResponse(
                note_id=note.id,
                staging_entry_id=note.promoted_to_staging_id,
            )
        if note.status != ResearchNoteStatus.active.value:
            raise NoteNotEditableError()

        try:
            phase9_section = Phase9BibleSection(payload.section)
        except ValueError as exc:
            raise InvalidBibleSectionError() from exc

        bible_section = phase9_section_to_bible_section(phase9_section)
        content_md = payload.content_md if payload.content_md is not None else note.body_md

        if payload.staging_entry_id:
            entry = await self.bible.get_staging_entry(project.id, payload.staging_entry_id)
            if entry is None:
                raise NotFoundError()
            entry.title = payload.title
            entry.content_md = content_md
            metadata = dict(entry.metadata_ or {})
            metadata["source_research_note_id"] = str(note.id)
            entry.metadata_ = metadata
            staging_entry = await self.bible.update_staging_entry(entry)
        else:
            entry_key = build_entry_key(phase9_section, payload.title)
            if await self.bible.entry_key_exists(project.id, entry_key):
                entry_key = f"{entry_key}_{note.id.hex[:8]}"
            staging = BibleEntryStaging(
                project_id=project.id,
                entry_key=entry_key,
                section=bible_section,
                title=payload.title,
                content_md=content_md,
                metadata_={"source_research_note_id": str(note.id)},
                base_bible_version=project.bible_version_current,
                created_by=user_id,
            )
            staging_entry = await self.bible.create_staging_entry(staging)

        note.status = ResearchNoteStatus.promoted.value
        note.promoted_to_staging_id = staging_entry.id
        note.promoted_at = datetime.now(UTC)
        await self.research.update_note(note)
        await self.session.refresh(staging_entry)

        return ResearchPromoteResponse(
            note_id=note.id,
            staging_entry_id=staging_entry.id,
        )
