"""Research notes persistence."""

import uuid

from sqlalchemy import func, select, text
from sqlalchemy.ext.asyncio import AsyncSession

from app.models.research import ResearchNote, ResearchNoteLink
from app.utils.pagination import PageParams


class ResearchRepository:
    def __init__(self, session: AsyncSession) -> None:
        self.session = session

    async def create_note(self, note: ResearchNote) -> ResearchNote:
        self.session.add(note)
        await self.session.flush()
        return note

    async def get_note(self, project_id: uuid.UUID, note_id: uuid.UUID) -> ResearchNote | None:
        return await self.session.scalar(
            select(ResearchNote).where(
                ResearchNote.project_id == project_id,
                ResearchNote.id == note_id,
            )
        )

    async def list_notes(
        self,
        project_id: uuid.UUID,
        *,
        status: str | None,
        tag: str | None,
        page: PageParams,
    ) -> tuple[list[ResearchNote], int]:
        query = select(ResearchNote).where(ResearchNote.project_id == project_id)
        if status:
            query = query.where(ResearchNote.status == status)
        if tag:
            query = query.where(ResearchNote.tags.contains([tag]))
        total = await self.session.scalar(select(func.count()).select_from(query.subquery())) or 0
        rows = await self.session.scalars(
            query.order_by(ResearchNote.updated_at.desc()).offset(page.offset).limit(page.page_size)
        )
        return list(rows.all()), int(total)

    async def search_notes(
        self,
        project_id: uuid.UUID,
        *,
        query_text: str,
        status: str | None,
        tag: str | None,
        page: PageParams,
    ) -> tuple[list[tuple[ResearchNote, float, str | None]], int]:
        tsquery = " & ".join(part for part in query_text.split() if part.strip())
        if not tsquery:
            tsquery = query_text

        base = select(
            ResearchNote,
            func.ts_rank(
                ResearchNote.search_vector, func.plainto_tsquery("simple", query_text)
            ).label("rank"),
            func.ts_headline(
                "simple",
                ResearchNote.body_md,
                func.plainto_tsquery("simple", query_text),
                "MaxWords=20, MinWords=5",
            ).label("snippet"),
        ).where(
            ResearchNote.project_id == project_id,
            ResearchNote.search_vector.op("@@")(func.plainto_tsquery("simple", query_text)),
        )
        if status:
            base = base.where(ResearchNote.status == status)
        if tag:
            base = base.where(ResearchNote.tags.contains([tag]))

        count_q = select(func.count()).select_from(base.subquery())
        total = await self.session.scalar(count_q) or 0
        rows = await self.session.execute(
            base.order_by(text("rank DESC")).offset(page.offset).limit(page.page_size)
        )
        hits = [(row[0], float(row[1] or 0), row[2]) for row in rows.all()]
        return hits, int(total)

    async def update_note(self, note: ResearchNote) -> ResearchNote:
        await self.session.flush()
        return note

    async def list_links(self, note_id: uuid.UUID) -> list[ResearchNoteLink]:
        rows = await self.session.scalars(
            select(ResearchNoteLink)
            .where(ResearchNoteLink.note_id == note_id)
            .order_by(ResearchNoteLink.created_at)
        )
        return list(rows.all())

    async def create_link(self, link: ResearchNoteLink) -> ResearchNoteLink:
        self.session.add(link)
        await self.session.flush()
        return link

    async def get_link(
        self, project_id: uuid.UUID, note_id: uuid.UUID, link_id: uuid.UUID
    ) -> ResearchNoteLink | None:
        return await self.session.scalar(
            select(ResearchNoteLink).where(
                ResearchNoteLink.project_id == project_id,
                ResearchNoteLink.note_id == note_id,
                ResearchNoteLink.id == link_id,
            )
        )

    async def delete_link(self, link: ResearchNoteLink) -> None:
        await self.session.delete(link)
        await self.session.flush()

    async def list_all_links_for_project(self, project_id: uuid.UUID) -> list[ResearchNoteLink]:
        rows = await self.session.scalars(
            select(ResearchNoteLink).where(ResearchNoteLink.project_id == project_id)
        )
        return list(rows)
