"""Genre rule pack routes."""

from fastapi import APIRouter, Query

from app.deps import DbSession, ProjectAccess
from app.schemas.genre import GenreRulePackPatch, GenreRulePackResponse
from app.services.genre import GenreService

router = APIRouter(prefix="/projects/{project_id}/genre-rule-pack", tags=["Genre"])


@router.get("", response_model=GenreRulePackResponse)
async def get_genre_rule_pack(
    project: ProjectAccess,
    session: DbSession,
) -> GenreRulePackResponse:
    return await GenreService(session).get_pack(project)


@router.patch("", response_model=GenreRulePackResponse)
async def patch_genre_rule_pack(
    payload: GenreRulePackPatch,
    project: ProjectAccess,
    session: DbSession,
) -> GenreRulePackResponse:
    return await GenreService(session).patch_pack(project, payload)


@router.post("/reset", response_model=GenreRulePackResponse)
async def reset_genre_rule_pack(
    project: ProjectAccess,
    session: DbSession,
    confirm: bool = Query(...),
) -> GenreRulePackResponse:
    return await GenreService(session).reset_pack(project, confirm=confirm)
