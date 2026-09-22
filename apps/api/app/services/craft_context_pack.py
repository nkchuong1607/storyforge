"""Craft context pack for Prompt Edit and Writer agents."""

from __future__ import annotations

import uuid

from sqlalchemy.ext.asyncio import AsyncSession

from app.exceptions import NotFoundError
from app.models.enums import ContextAudience
from app.models.project import Project
from app.repositories.chapter import ChapterRepository
from app.repositories.craft_pack import CraftPackRepository
from app.repositories.twist import TwistRepository
from app.schemas.craft_pack import (
    CraftBeatEntry,
    CraftChecklistOpenItem,
    CraftClueEntry,
    CraftContextPackRequest,
    CraftContextPackResponse,
    CraftMisdirectionEntry,
)
from app.services.continuity.craft import parse_checklist, run_craft_checks
from app.services.continuity.foreshadow import (
    ForeshadowPayoffContext,
    ForeshadowPlantContext,
    ForeshadowTwistContext,
)
from app.services.craft_defaults import MYSTERY_FAIR_PLAY_V1_ID
from app.services.genre_defaults import merged_genre_pack
from app.services.twist_context_pack import json_has_secret_truth_key


class CraftContextPackService:
    def __init__(self, session: AsyncSession) -> None:
        self.session = session
        self.chapters = ChapterRepository(session)
        self.twists = TwistRepository(session)
        self.craft = CraftPackRepository(session)

    async def build_context_pack(
        self,
        project: Project,
        payload: CraftContextPackRequest,
    ) -> CraftContextPackResponse:
        chapter = await self.chapters.get(project.id, payload.chapter_id)
        if chapter is None:
            raise NotFoundError()
        if chapter.number != payload.chapter_number:
            raise NotFoundError(message="Chapter number mismatch")

        binding = await self.craft.get_active_binding(project.id)
        if binding is None:
            raise NotFoundError(message="No active craft pack on project")
        catalog = await self.craft.get_catalog_pack(binding.craft_pack_id)
        if catalog is None:
            raise NotFoundError(message="Craft pack catalog entry missing")

        pack_json = catalog.pack_json
        structure = pack_json.get("structure") or {}
        beats_raw = structure.get("beats") or []
        craft_beats = [
            CraftBeatEntry(
                key=str(b.get("key")),
                act=int(b.get("act", 1)),
                required=bool(b.get("required", False)),
            )
            for b in beats_raw
            if isinstance(b, dict) and b.get("key")
        ]

        all_plants = await self.twists.list_plants_for_project(project.id)
        chapter_numbers: dict[uuid.UUID, int] = {}
        for plant in all_plants:
            if plant.chapter_id not in chapter_numbers:
                ch = await self.chapters.get(project.id, plant.chapter_id)
                if ch:
                    chapter_numbers[plant.chapter_id] = ch.number

        foreshadow_plants = [
            ForeshadowPlantContext(
                plant_id=p.id,
                twist_id=p.twist_id,
                chapter_id=p.chapter_id,
                chapter_number=chapter_numbers.get(p.chapter_id, 999),
            )
            for p in all_plants
        ]

        all_twists = await self.twists.list_all_plans(project.id, include_abandoned=True)
        foreshadow_twists = [
            ForeshadowTwistContext(
                twist_id=t.id,
                title=t.title,
                secret_truth=t.secret_truth,
                status=t.status,
                constraints_json=dict(t.constraints_json or {}),
                genre_strictness=t.genre_strictness,
                misdirection=t.misdirection,
            )
            for t in all_twists
        ]

        payoff_rows = await self.twists.list_payoffs_with_twists_for_chapter(project.id, chapter.id)
        foreshadow_payoffs: list[ForeshadowPayoffContext] = []
        for payoff, twist in payoff_rows:
            target_ch = await self.chapters.get(project.id, payoff.target_chapter_id)
            if target_ch is None:
                continue
            foreshadow_payoffs.append(
                ForeshadowPayoffContext(
                    payoff_id=payoff.id,
                    twist=ForeshadowTwistContext(
                        twist_id=twist.id,
                        title=twist.title,
                        secret_truth=twist.secret_truth,
                        status=twist.status,
                        constraints_json=dict(twist.constraints_json or {}),
                        genre_strictness=twist.genre_strictness,
                        misdirection=twist.misdirection,
                    ),
                    target_chapter_id=payoff.target_chapter_id,
                    target_chapter_number=target_ch.number,
                    min_plants=payoff.min_plants,
                    required_plant_ids=list(payoff.required_plant_ids or []),
                )
            )

        prose_row = None
        from app.repositories.prose import ProseRepository

        prose_repo = ProseRepository(self.session)
        prose_row = await prose_repo.get_latest(chapter.id)
        prose = prose_row.content if prose_row else ""

        genre_pack = merged_genre_pack(project.genre_rule_pack_json or {}, project.genre_profile)
        open_issues = run_craft_checks(
            chapter_id=chapter.id,
            chapter_number=chapter.number,
            prose=prose,
            genre_profile=project.genre_profile,
            pack_json=pack_json,
            payoffs=foreshadow_payoffs,
            plants=foreshadow_plants,
            all_twists=foreshadow_twists,
            genre_pack=genre_pack,
        )
        open_codes = {issue.code for issue in open_issues}
        checklist_open = [
            CraftChecklistOpenItem(
                id=item.item_id,
                code=item.code,
                description=item.description or None,
            )
            for item in parse_checklist(pack_json)
            if item.code in open_codes
        ]

        plant_rows = await self.twists.list_active_plants_for_context(
            project.id, payload.chapter_number, 20
        )
        active_clues = [
            CraftClueEntry(
                plant_id=plant.id,
                twist_id=twist.id,
                twist_title=twist.title,
                chapter_number=plant_chapter.number,
                snippet=plant.snippet,
            )
            for plant, twist, plant_chapter in plant_rows
        ]

        active_misdirections = [
            CraftMisdirectionEntry(
                twist_id=t.id,
                twist_title=t.title,
                misdirection=t.misdirection or "",
            )
            for t in all_twists
            if (t.misdirection or "").strip() and t.status.value in ("planted", "armed", "seeded")
        ]

        audience = payload.audience
        stripped = audience == ContextAudience.writer
        response = CraftContextPackResponse(
            craft_pack_id=pack_json.get("id") or MYSTERY_FAIR_PLAY_V1_ID,
            craft_beats=craft_beats,
            craft_checklist_open=checklist_open,
            active_clues=active_clues,
            active_misdirections=active_misdirections,
            meta={
                "audience": audience.value,
                "canon_secrets_stripped": stripped,
                "open_checklist_count": len(checklist_open),
            },
        )
        if stripped and json_has_secret_truth_key(response.model_dump()):
            raise RuntimeError("craft context pack leaked secret_truth")
        return response
