"""Power system business logic."""

from __future__ import annotations

import uuid
from datetime import UTC, datetime

from sqlalchemy.ext.asyncio import AsyncSession

from app.exceptions import (
    InvalidRankLadderError,
    NotFoundError,
    PowerSystemDisabledError,
    RankInUseError,
)
from app.models.power_system import PowerRank, PowerSystemSettings, PowerTechnique
from app.models.project import Project
from app.repositories.power import PowerRepository
from app.schemas.power import (
    PowerRank as PowerRankSchema,
)
from app.schemas.power import (
    PowerRankCreateRequest,
    PowerRankListResponse,
    PowerRankReorderRequest,
    PowerRankUpdateRequest,
    PowerSystemSettingsUpdate,
    PowerTechniqueCreateRequest,
    PowerTechniqueListResponse,
    PowerTechniqueUpdateRequest,
)
from app.schemas.power import (
    PowerSystemSettings as PowerSystemSettingsSchema,
)
from app.schemas.power import (
    PowerTechnique as PowerTechniqueSchema,
)


class PowerService:
    def __init__(self, session: AsyncSession) -> None:
        self.session = session
        self.power = PowerRepository(session)

    async def _require_enabled(self, project_id: uuid.UUID) -> PowerSystemSettings:
        settings = await self.power.ensure_settings(project_id)
        if not settings.enabled:
            raise PowerSystemDisabledError()
        return settings

    def _rank_schema(self, rank: PowerRank) -> PowerRankSchema:
        sub_stages = rank.sub_stages or []
        return PowerRankSchema(
            id=rank.id,
            rank_key=rank.rank_key,
            display_name=rank.display_name,
            sort_order=rank.sort_order,
            sub_stages=sub_stages,
            constraints_md=rank.constraints_md or "",
        )

    def _technique_schema(
        self, technique: PowerTechnique, rank_names: dict[uuid.UUID, str]
    ) -> PowerTechniqueSchema:
        return PowerTechniqueSchema(
            id=technique.id,
            technique_key=technique.technique_key,
            display_name=technique.display_name,
            min_rank_id=technique.min_rank_id,
            min_rank_display_name=rank_names.get(technique.min_rank_id),
            sect_requirement=technique.sect_requirement,
            lineage_requirement=technique.lineage_requirement,
            resource_cost=technique.resource_cost or {},
            notes_md=technique.notes_md or "",
        )

    async def get_settings(self, project: Project) -> PowerSystemSettingsSchema:
        settings = await self.power.ensure_settings(project.id)
        return PowerSystemSettingsSchema.model_validate(settings)

    async def update_settings(
        self, project: Project, payload: PowerSystemSettingsUpdate
    ) -> PowerSystemSettingsSchema:
        settings = await self.power.ensure_settings(project.id)
        if payload.enabled is not None:
            settings.enabled = payload.enabled
        if payload.priority_gap is not None:
            settings.priority_gap = payload.priority_gap
        if payload.max_rank_jump_per_chapter is not None:
            settings.max_rank_jump_per_chapter = payload.max_rank_jump_per_chapter
        if payload.require_breakthrough_event is not None:
            settings.require_breakthrough_event = payload.require_breakthrough_event
        settings.updated_at = datetime.now(UTC)
        await self.session.flush()
        await self.session.refresh(settings)
        return PowerSystemSettingsSchema.model_validate(settings)

    async def list_ranks(self, project: Project) -> PowerRankListResponse:
        ranks = await self.power.list_ranks(project.id)
        return PowerRankListResponse(items=[self._rank_schema(r) for r in ranks])

    async def create_rank(
        self, project: Project, payload: PowerRankCreateRequest
    ) -> PowerRankSchema:
        await self._require_enabled(project.id)
        sort_order = payload.sort_order
        if sort_order is None:
            sort_order = await self.power.max_sort_order(project.id) + 1
        rank = PowerRank(
            project_id=project.id,
            rank_key=payload.rank_key,
            display_name=payload.display_name,
            sort_order=sort_order,
            sub_stages=[s.model_dump() for s in payload.sub_stages],
            constraints_md=payload.constraints_md,
        )
        created = await self.power.create_rank(rank)
        return self._rank_schema(created)

    async def update_rank(
        self, project: Project, rank_id: uuid.UUID, payload: PowerRankUpdateRequest
    ) -> PowerRankSchema:
        await self._require_enabled(project.id)
        rank = await self.power.get_rank(project.id, rank_id)
        if rank is None:
            raise NotFoundError()
        if payload.rank_key is not None:
            rank.rank_key = payload.rank_key
        if payload.display_name is not None:
            rank.display_name = payload.display_name
        if payload.sub_stages is not None:
            rank.sub_stages = [s.model_dump() for s in payload.sub_stages]
        if payload.constraints_md is not None:
            rank.constraints_md = payload.constraints_md
        if payload.sort_order is not None and payload.sort_order != rank.sort_order:
            await self._reorder_single(rank, payload.sort_order)
        rank.updated_at = datetime.now(UTC)
        await self.session.flush()
        await self.session.refresh(rank)
        return self._rank_schema(rank)

    async def _reorder_single(self, rank: PowerRank, new_order: int) -> None:
        ranks = await self.power.list_ranks(rank.project_id)
        old_order = rank.sort_order
        for r in ranks:
            if r.id == rank.id:
                r.sort_order = new_order
            elif old_order < new_order and old_order < r.sort_order <= new_order:
                r.sort_order -= 1
            elif old_order > new_order and new_order <= r.sort_order < old_order:
                r.sort_order += 1
        await self._validate_ladder(ranks)

    async def _validate_ladder(self, ranks: list[PowerRank]) -> None:
        orders = sorted(r.sort_order for r in ranks)
        if orders != list(range(len(ranks))):
            raise InvalidRankLadderError()

    async def reorder_ranks(
        self, project: Project, payload: PowerRankReorderRequest
    ) -> PowerRankListResponse:
        await self._require_enabled(project.id)
        ranks = await self.power.list_ranks(project.id)
        rank_map = {r.id: r for r in ranks}
        if set(payload.rank_ids) != set(rank_map.keys()):
            raise InvalidRankLadderError(message="rank_ids must be a full permutation")
        # Avoid UNIQUE (project_id, sort_order) violations during in-place reorder.
        for rank in ranks:
            rank.sort_order = -(rank.sort_order + 1)
        await self.session.flush()
        for idx, rank_id in enumerate(payload.rank_ids):
            rank_map[rank_id].sort_order = idx
        await self.session.flush()
        return await self.list_ranks(project)

    async def delete_rank(self, project: Project, rank_id: uuid.UUID) -> None:
        await self._require_enabled(project.id)
        rank = await self.power.get_rank(project.id, rank_id)
        if rank is None:
            raise NotFoundError()
        in_use = await self.power.count_techniques_for_rank(project.id, rank_id)
        if in_use > 0:
            raise RankInUseError()
        await self.power.delete_rank(rank)

    async def list_techniques(self, project: Project) -> PowerTechniqueListResponse:
        ranks = await self.power.list_ranks(project.id)
        rank_names = {r.id: r.display_name for r in ranks}
        techniques = await self.power.list_techniques(project.id)
        return PowerTechniqueListResponse(
            items=[self._technique_schema(t, rank_names) for t in techniques]
        )

    async def create_technique(
        self, project: Project, payload: PowerTechniqueCreateRequest
    ) -> PowerTechniqueSchema:
        await self._require_enabled(project.id)
        min_rank = await self.power.get_rank(project.id, payload.min_rank_id)
        if min_rank is None:
            raise NotFoundError(message="Min rank not found")
        technique = PowerTechnique(
            project_id=project.id,
            technique_key=payload.technique_key,
            display_name=payload.display_name,
            min_rank_id=payload.min_rank_id,
            sect_requirement=payload.sect_requirement,
            lineage_requirement=payload.lineage_requirement,
            resource_cost=payload.resource_cost,
            notes_md=payload.notes_md,
        )
        created = await self.power.create_technique(technique)
        return self._technique_schema(created, {min_rank.id: min_rank.display_name})

    async def update_technique(
        self, project: Project, technique_id: uuid.UUID, payload: PowerTechniqueUpdateRequest
    ) -> PowerTechniqueSchema:
        await self._require_enabled(project.id)
        technique = await self.power.get_technique(project.id, technique_id)
        if technique is None:
            raise NotFoundError()
        if payload.technique_key is not None:
            technique.technique_key = payload.technique_key
        if payload.display_name is not None:
            technique.display_name = payload.display_name
        if payload.min_rank_id is not None:
            min_rank = await self.power.get_rank(project.id, payload.min_rank_id)
            if min_rank is None:
                raise NotFoundError(message="Min rank not found")
            technique.min_rank_id = payload.min_rank_id
        if payload.sect_requirement is not None:
            technique.sect_requirement = payload.sect_requirement
        if payload.lineage_requirement is not None:
            technique.lineage_requirement = payload.lineage_requirement
        if payload.resource_cost is not None:
            technique.resource_cost = payload.resource_cost
        if payload.notes_md is not None:
            technique.notes_md = payload.notes_md
        technique.updated_at = datetime.now(UTC)
        await self.session.flush()
        ranks = await self.power.list_ranks(project.id)
        rank_names = {r.id: r.display_name for r in ranks}
        await self.session.refresh(technique)
        return self._technique_schema(technique, rank_names)

    async def delete_technique(self, project: Project, technique_id: uuid.UUID) -> None:
        await self._require_enabled(project.id)
        technique = await self.power.get_technique(project.id, technique_id)
        if technique is None:
            raise NotFoundError()
        await self.power.delete_technique(technique)
