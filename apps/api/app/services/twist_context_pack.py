"""Twist context pack builder — plants only, never secret_truth."""

from __future__ import annotations

from typing import Any

from sqlalchemy.ext.asyncio import AsyncSession

from app.exceptions import NotFoundError
from app.models.enums import ContextAudience
from app.models.project import Project
from app.repositories.chapter import ChapterRepository
from app.repositories.twist import TwistRepository
from app.schemas.twist import (
    TwistContextPackRequest,
    TwistContextPackResponse,
    TwistContextPlantEntry,
)


def json_has_secret_truth_key(obj: Any) -> bool:
    """Recursive scan for secret_truth key (used in tests)."""
    if isinstance(obj, dict):
        if "secret_truth" in obj:
            return True
        return any(json_has_secret_truth_key(v) for v in obj.values())
    if isinstance(obj, list):
        return any(json_has_secret_truth_key(item) for item in obj)
    return False


class TwistContextPackService:
    def __init__(self, session: AsyncSession) -> None:
        self.session = session
        self.chapters = ChapterRepository(session)
        self.twists = TwistRepository(session)

    async def build_context_pack(
        self,
        project: Project,
        payload: TwistContextPackRequest,
    ) -> TwistContextPackResponse:
        chapter = await self.chapters.get(project.id, payload.chapter_id)
        if chapter is None:
            raise NotFoundError()
        if chapter.number != payload.chapter_number:
            raise NotFoundError(message="Chapter number mismatch")

        rows = await self.twists.list_active_plants_for_context(
            project.id,
            payload.chapter_number,
            payload.max_plants,
        )
        entries: list[TwistContextPlantEntry] = []
        for plant, twist, plant_chapter in rows:
            entries.append(
                TwistContextPlantEntry(
                    plant_id=plant.id,
                    twist_id=twist.id,
                    twist_title=twist.title,
                    chapter_number=plant_chapter.number,
                    salience=plant.salience,
                    snippet=plant.snippet,
                )
            )

        audience = payload.audience
        stripped = audience == ContextAudience.writer
        return TwistContextPackResponse(
            twist_relevant=entries,
            meta={
                "audience": audience.value,
                "secret_truth_stripped": stripped,
                "plant_count": len(entries),
            },
        )
