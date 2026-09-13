"""Relationship context pack service."""

from __future__ import annotations

import uuid

from sqlalchemy.ext.asyncio import AsyncSession

from app.exceptions import NotFoundError
from app.models.project import Project
from app.repositories.beat import BeatRepository
from app.repositories.chapter import ChapterRepository
from app.repositories.character import CharacterRepository
from app.repositories.relationship import RelationshipRepository
from app.schemas.relationship import (
    RelationshipContextPackEdge,
    RelationshipContextPackRequest,
    RelationshipContextPackResponse,
)
from app.services.continuity.relationship import compute_intensity
from app.services.relationship import RelationshipService


class RelationshipContextPackService:
    def __init__(self, session: AsyncSession) -> None:
        self.session = session
        self.chapters = ChapterRepository(session)
        self.characters = CharacterRepository(session)
        self.beats = BeatRepository(session)
        self.relationships = RelationshipRepository(session)

    async def build_context_pack(
        self, project: Project, payload: RelationshipContextPackRequest
    ) -> RelationshipContextPackResponse:
        chapter = await self.chapters.get(project.id, payload.chapter_id)
        if chapter is None:
            raise NotFoundError()

        cast_ids = set(payload.character_ids)
        beats = await self.beats.list_for_chapter(payload.chapter_id)
        for beat in beats:
            if beat.pov_character_id:
                cast_ids.add(beat.pov_character_id)

        all_rels = await self.relationships.list_all_for_project(project.id)
        settled = await self.relationships.list_settled_events_for_project(project.id)
        events_by_rel: dict[uuid.UUID, list] = {}
        for event in settled:
            events_by_rel.setdefault(event.relationship_id, []).append(event)

        edges: list[RelationshipContextPackEdge] = []
        for rel in all_rels:
            if cast_ids and not (rel.character_a_id in cast_ids or rel.character_b_id in cast_ids):
                continue
            if cast_ids and not (rel.character_a_id in cast_ids and rel.character_b_id in cast_ids):
                if not (rel.character_a_id in cast_ids or rel.character_b_id in cast_ids):
                    continue
            rel_events = events_by_rel.get(rel.id, [])
            visible_events = []
            for event in reversed(rel_events):
                payload_data = event.payload or {}
                if payload_data.get("visibility") == "secret":
                    knows = payload_data.get("knows") or []
                    pov_ids = {str(i) for i in cast_ids}
                    if not pov_ids.intersection(knows):
                        continue
                visible_events.append(
                    {
                        "event_type": event.event_type,
                        "intensity_delta": event.intensity_delta,
                        "chapter_number": event.chapter_number,
                    }
                )
                if len(visible_events) >= RelationshipService.MAX_EVENTS_PER_EDGE:
                    break
            edges.append(
                RelationshipContextPackEdge(
                    relation_type=rel.relation_type,
                    intensity=compute_intensity(rel.baseline_intensity, rel_events),
                    recent_events=list(reversed(visible_events)),
                )
            )
            if len(edges) >= RelationshipService.MAX_CONTEXT_EDGES:
                break

        return RelationshipContextPackResponse(edges=edges)
