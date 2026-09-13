"""Relationship routes."""

import uuid

from fastapi import APIRouter, Query, Response, status

from app.deps import DbSession, ProjectAccess
from app.schemas.relationship import (
    Relationship,
    RelationshipCreateRequest,
    RelationshipEventListResponse,
    RelationshipGraphResponse,
    RelationshipListResponse,
    RelationshipUpdateRequest,
)
from app.services.relationship import RelationshipService

router = APIRouter(prefix="/projects/{project_id}/relationships", tags=["Relationships"])


@router.get("", response_model=RelationshipListResponse)
async def list_relationships(
    project: ProjectAccess,
    session: DbSession,
    page: int = Query(default=1, ge=1),
    page_size: int = Query(default=50, ge=1, le=100),
) -> RelationshipListResponse:
    return await RelationshipService(session).list_relationships(
        project, page=page, page_size=page_size
    )


@router.post("", response_model=Relationship, status_code=status.HTTP_201_CREATED)
async def create_relationship(
    payload: RelationshipCreateRequest,
    project: ProjectAccess,
    session: DbSession,
) -> Relationship:
    return await RelationshipService(session).create_relationship(project, payload)


@router.get("/graph", response_model=RelationshipGraphResponse)
async def get_relationship_graph(
    project: ProjectAccess,
    session: DbSession,
    character_ids: list[uuid.UUID] | None = Query(default=None),
    act_number: int | None = Query(default=None, ge=1),
    min_intensity: int | None = Query(default=None, ge=-5, le=5),
    relation_types: list[str] | None = Query(default=None),
) -> RelationshipGraphResponse:
    return await RelationshipService(session).get_graph(
        project,
        character_ids=character_ids,
        act_number=act_number,
        min_intensity=min_intensity,
        relation_types=relation_types,
    )


@router.get("/{relationship_id}", response_model=Relationship)
async def get_relationship(
    relationship_id: uuid.UUID,
    project: ProjectAccess,
    session: DbSession,
) -> Relationship:
    return await RelationshipService(session).get_relationship(project, relationship_id)


@router.patch("/{relationship_id}", response_model=Relationship)
async def update_relationship(
    relationship_id: uuid.UUID,
    payload: RelationshipUpdateRequest,
    project: ProjectAccess,
    session: DbSession,
) -> Relationship:
    return await RelationshipService(session).update_relationship(project, relationship_id, payload)


@router.delete("/{relationship_id}", status_code=status.HTTP_204_NO_CONTENT)
async def delete_relationship(
    relationship_id: uuid.UUID,
    project: ProjectAccess,
    session: DbSession,
) -> Response:
    await RelationshipService(session).delete_relationship(project, relationship_id)
    return Response(status_code=status.HTTP_204_NO_CONTENT)


@router.get("/{relationship_id}/events", response_model=RelationshipEventListResponse)
async def list_relationship_events(
    relationship_id: uuid.UUID,
    project: ProjectAccess,
    session: DbSession,
) -> RelationshipEventListResponse:
    return await RelationshipService(session).list_events(project, relationship_id)
