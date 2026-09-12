"""Genre rule pack business logic."""

from __future__ import annotations

from datetime import UTC, datetime

from sqlalchemy.ext.asyncio import AsyncSession

from app.exceptions import InvalidGenreRulePackError, ValidationAppError
from app.models.project import Project
from app.schemas.genre import GenreRulePackPatch, GenreRulePackResponse
from app.services.genre_defaults import (
    deep_merge,
    default_genre_rule_pack,
    merged_genre_pack,
    validate_genre_pack,
)


class GenreService:
    def __init__(self, session: AsyncSession) -> None:
        self.session = session

    def _response(self, project: Project) -> GenreRulePackResponse:
        pack = merged_genre_pack(project.genre_rule_pack_json or {}, project.genre_profile)
        return GenreRulePackResponse(
            project_id=project.id,
            genre_profile=project.genre_profile,
            pack=pack,
            updated_at=project.updated_at,
        )

    async def get_pack(self, project: Project) -> GenreRulePackResponse:
        return self._response(project)

    async def patch_pack(
        self, project: Project, payload: GenreRulePackPatch
    ) -> GenreRulePackResponse:
        try:
            validate_genre_pack(payload.pack)
        except ValueError as exc:
            raise InvalidGenreRulePackError(str(exc)) from exc
        current = project.genre_rule_pack_json or {}
        project.genre_rule_pack_json = deep_merge(current, payload.pack)
        project.updated_at = datetime.now(UTC)
        await self.session.flush()
        await self.session.refresh(project)
        return self._response(project)

    async def reset_pack(self, project: Project, *, confirm: bool) -> GenreRulePackResponse:
        if not confirm:
            raise ValidationAppError(message="confirm=true required to reset genre rule pack")
        project.genre_rule_pack_json = default_genre_rule_pack(project.genre_profile)
        project.updated_at = datetime.now(UTC)
        await self.session.flush()
        await self.session.refresh(project)
        return self._response(project)
