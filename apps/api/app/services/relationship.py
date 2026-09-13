"""Relationship business logic."""

from __future__ import annotations

import uuid
from datetime import UTC, datetime

from sqlalchemy.ext.asyncio import AsyncSession

from app.exceptions import (
    InvalidRelationshipPairError,
    NotFoundError,
    RelationshipEventImmutableError,
    RelationshipExistsError,
)
from app.models.project import Project
from app.models.relationship import Relationship
from app.models.relationship_event import RelationshipEvent
from app.repositories.character import CharacterRepository
from app.repositories.relationship import RelationshipRepository
from app.schemas.relationship import (
    Relationship as RelationshipSchema,
)
from app.schemas.relationship import (
    RelationshipCreateRequest,
    RelationshipEventListResponse,
    RelationshipGraphEdge,
    RelationshipGraphMeta,
    RelationshipGraphNode,
    RelationshipGraphResponse,
    RelationshipListResponse,
    RelationshipUpdateRequest,
)
from app.schemas.relationship import (
    RelationshipEvent as RelationshipEventSchema,
)
from app.services.continuity.relationship import compute_intensity, normalize_pair
from app.utils.pagination import clamp_page_params


class RelationshipService:
    MAX_CONTEXT_EDGES = 8
    MAX_EVENTS_PER_EDGE = 3

    def __init__(self, session: AsyncSession) -> None:
        self.session = session
        self.relationships = RelationshipRepository(session)
        self.characters = CharacterRepository(session)

    async def _to_schema(self, rel: Relationship) -> RelationshipSchema:
        char_a = await self.characters.get_by_id(rel.project_id, rel.character_a_id)
        char_b = await self.characters.get_by_id(rel.project_id, rel.character_b_id)
        events = await self.relationships.list_events(rel.project_id, rel.id)
        settled = [e for e in events if e.settled_at is not None]
        intensity = compute_intensity(rel.baseline_intensity, settled)
        return RelationshipSchema(
            id=rel.id,
            project_id=rel.project_id,
            character_a_id=rel.character_a_id,
            character_b_id=rel.character_b_id,
            character_a_name=char_a.display_name if char_a else None,
            character_b_name=char_b.display_name if char_b else None,
            relation_type=rel.relation_type,
            custom_label=rel.custom_label,
            baseline_intensity=rel.baseline_intensity,
            current_intensity=intensity,
            notes_md=rel.notes_md or "",
            event_count=len(settled),
            created_at=rel.created_at,
            updated_at=rel.updated_at,
        )

    async def list_relationships(
        self,
        project: Project,
        *,
        page: int = 1,
        page_size: int = 50,
    ) -> RelationshipListResponse:
        params = clamp_page_params(page, page_size)
        rows, total = await self.relationships.list_for_project(
            project.id, offset=params.offset, limit=params.page_size
        )
        items = [await self._to_schema(row) for row in rows]
        return RelationshipListResponse(items=items, page=page, page_size=page_size, total=total)

    async def create_relationship(
        self, project: Project, payload: RelationshipCreateRequest
    ) -> RelationshipSchema:
        try:
            a_id, b_id = normalize_pair(payload.character_a_id, payload.character_b_id)
        except ValueError as exc:
            raise InvalidRelationshipPairError() from exc

        for cid in (a_id, b_id):
            char = await self.characters.get_by_id(project.id, cid)
            if char is None:
                raise NotFoundError(message="Character not found")

        existing = await self.relationships.get_by_pair(project.id, a_id, b_id)
        if existing is not None:
            raise RelationshipExistsError()

        rel = Relationship(
            project_id=project.id,
            character_a_id=a_id,
            character_b_id=b_id,
            relation_type=payload.relation_type.value
            if hasattr(payload.relation_type, "value")
            else payload.relation_type,
            custom_label=payload.custom_label,
            baseline_intensity=payload.baseline_intensity,
            notes_md=payload.notes_md or "",
        )
        created = await self.relationships.create(rel)
        await self.session.refresh(created)
        return await self._to_schema(created)

    async def get_relationship(
        self, project: Project, relationship_id: uuid.UUID
    ) -> RelationshipSchema:
        rel = await self.relationships.get(project.id, relationship_id)
        if rel is None:
            raise NotFoundError()
        return await self._to_schema(rel)

    async def update_relationship(
        self,
        project: Project,
        relationship_id: uuid.UUID,
        payload: RelationshipUpdateRequest,
    ) -> RelationshipSchema:
        rel = await self.relationships.get(project.id, relationship_id)
        if rel is None:
            raise NotFoundError()
        data = payload.model_dump(exclude_unset=True)
        if "relation_type" in data and data["relation_type"] is not None:
            data["relation_type"] = (
                data["relation_type"].value
                if hasattr(data["relation_type"], "value")
                else data["relation_type"]
            )
        for key, value in data.items():
            setattr(rel, key, value)
        rel.updated_at = datetime.now(UTC)
        await self.relationships.update(rel)
        await self.session.refresh(rel)
        return await self._to_schema(rel)

    async def delete_relationship(self, project: Project, relationship_id: uuid.UUID) -> None:
        rel = await self.relationships.get(project.id, relationship_id)
        if rel is None:
            raise NotFoundError()
        await self.relationships.delete(rel)

    async def list_events(
        self, project: Project, relationship_id: uuid.UUID
    ) -> RelationshipEventListResponse:
        rel = await self.relationships.get(project.id, relationship_id)
        if rel is None:
            raise NotFoundError()
        events = await self.relationships.list_events(project.id, relationship_id)
        items = [RelationshipEventSchema.model_validate(e) for e in events]
        return RelationshipEventListResponse(items=items)

    async def get_graph(
        self,
        project: Project,
        *,
        character_ids: list[uuid.UUID] | None = None,
        act_number: int | None = None,
        min_intensity: int | None = None,
        relation_types: list[str] | None = None,
    ) -> RelationshipGraphResponse:
        all_rels = await self.relationships.list_all_for_project(project.id)
        settled_events = await self.relationships.list_settled_events_for_project(project.id)
        events_by_rel: dict[uuid.UUID, list[RelationshipEvent]] = {}
        for event in settled_events:
            if act_number is not None:
                from app.repositories.stakes import StakesRepository
                from app.services.continuity.stakes import resolve_act_for_chapter

                stakes_repo = StakesRepository(self.session)
                settings = await stakes_repo.ensure_settings(project.id)
                _, _, act_end = resolve_act_for_chapter(event.chapter_number, settings)
                act_num, _, _ = resolve_act_for_chapter(event.chapter_number, settings)
                if act_num > act_number:
                    continue
            events_by_rel.setdefault(event.relationship_id, []).append(event)

        char_ids_set = set(character_ids or [])
        nodes_map: dict[uuid.UUID, RelationshipGraphNode] = {}
        edges: list[RelationshipGraphEdge] = []

        for rel in all_rels:
            if char_ids_set and not (
                rel.character_a_id in char_ids_set or rel.character_b_id in char_ids_set
            ):
                continue
            if relation_types and rel.relation_type not in relation_types:
                continue
            events = events_by_rel.get(rel.id, [])
            intensity = compute_intensity(rel.baseline_intensity, events)
            if min_intensity is not None and intensity < min_intensity:
                continue

            for cid in (rel.character_a_id, rel.character_b_id):
                if cid not in nodes_map:
                    char = await self.characters.get_by_id(project.id, cid)
                    if char:
                        nodes_map[cid] = RelationshipGraphNode(
                            id=cid,
                            display_name=char.display_name,
                            tier=char.tier,
                            degree=0,
                        )

            last_event = events[-1] if events else None
            edges.append(
                RelationshipGraphEdge(
                    id=rel.id,
                    source_id=rel.character_a_id,
                    target_id=rel.character_b_id,
                    relation_type=rel.relation_type,
                    intensity=intensity,
                    event_count=len(events),
                    last_event={
                        "chapter_number": last_event.chapter_number,
                        "event_type": last_event.event_type,
                        "intensity_delta": last_event.intensity_delta,
                    }
                    if last_event
                    else None,
                )
            )

        for edge in edges:
            for cid in (edge.source_id, edge.target_id):
                if cid in nodes_map:
                    nodes_map[cid].degree += 1

        return RelationshipGraphResponse(
            nodes=list(nodes_map.values()),
            edges=edges,
            meta=RelationshipGraphMeta(
                filtered_character_ids=list(char_ids_set),
                act_number=act_number,
                generated_at=datetime.now(UTC),
            ),
        )

    async def assert_event_mutable(self, event: RelationshipEvent) -> None:
        if event.settled_at is not None:
            raise RelationshipEventImmutableError()
