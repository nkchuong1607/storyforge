"""TwistPlan CRUD, transitions, and board view."""

from __future__ import annotations

import uuid

from sqlalchemy.ext.asyncio import AsyncSession

from app.exceptions import (
    ChapterLockedError,
    InvalidPlantReferenceError,
    NotFoundError,
    PayoffAlreadyExistsError,
    TwistPaidOffImmutableError,
)
from app.models.enums import ContextAudience, TwistPlanKind, TwistPlanStatus
from app.models.project import Project
from app.models.twist import TwistPayoff, TwistPlan, TwistPlant
from app.repositories.chapter import ChapterRepository
from app.repositories.twist import TwistRepository
from app.schemas.twist import (
    TwistBoardCard,
    TwistBoardColumn,
    TwistBoardResponse,
    TwistFairnessState,
    TwistPayoffCreateRequest,
    TwistPayoffUpdateRequest,
    TwistPlanCreateRequest,
    TwistPlanListResponse,
    TwistPlantCreateRequest,
    TwistPlantListResponse,
    TwistPlantUpdateRequest,
    TwistPlanUpdateRequest,
    TwistTransitionRequest,
    twist_payoff_from_model,
    twist_plan_from_model,
    twist_plant_from_model,
)
from app.schemas.twist import (
    TwistPayoff as TwistPayoffSchema,
)
from app.schemas.twist import (
    TwistPlan as TwistPlanSchema,
)
from app.schemas.twist import (
    TwistPlant as TwistPlantSchema,
)
from app.services.chapter_status import is_chapter_locked
from app.services.continuity.foreshadow import (
    ForeshadowPayoffContext,
    ForeshadowPlantContext,
    ForeshadowTwistContext,
    evaluate_payoff_fairness,
)
from app.utils.pagination import PageParams, paginated
from app.utils.twist_status import (
    status_after_first_plant,
    status_after_payoff,
    validate_twist_transition,
)


class TwistService:
    def __init__(self, session: AsyncSession) -> None:
        self.session = session
        self.twists = TwistRepository(session)
        self.chapters = ChapterRepository(session)

    async def _chapter_number(self, chapter_id: uuid.UUID) -> int:
        chapter = await self.chapters.get_by_id(chapter_id)
        if chapter is None:
            raise NotFoundError()
        return chapter.number

    async def _ensure_chapter_in_project(
        self, project_id: uuid.UUID, chapter_id: uuid.UUID
    ) -> None:
        chapter = await self.chapters.get(project_id, chapter_id)
        if chapter is None:
            raise NotFoundError()

    async def _ensure_chapter_unlocked(self, project_id: uuid.UUID, chapter_id: uuid.UUID) -> None:
        chapter = await self.chapters.get(project_id, chapter_id)
        if chapter is None:
            raise NotFoundError()
        if is_chapter_locked(chapter.status):
            raise ChapterLockedError()

    async def _get_twist_or_404(self, project_id: uuid.UUID, twist_id: uuid.UUID) -> TwistPlan:
        twist = await self.twists.get_plan(project_id, twist_id)
        if twist is None:
            raise NotFoundError()
        return twist

    def _guard_paid_off(self, twist: TwistPlan) -> None:
        if twist.status == TwistPlanStatus.paid_off:
            raise TwistPaidOffImmutableError()

    async def _to_plan_schema(
        self,
        twist: TwistPlan,
        *,
        audience: ContextAudience = ContextAudience.author,
    ) -> TwistPlanSchema:
        plant_count = await self.twists.count_plants(twist.id)
        payoff = await self.twists.get_payoff(twist.project_id, twist.id)
        target_num = None
        if payoff is not None:
            target_num = await self._chapter_number(payoff.target_chapter_id)
        return twist_plan_from_model(
            twist,
            plant_count=plant_count,
            payoff=payoff,
            target_chapter_number=target_num,
            audience=audience,
        )

    async def list_twists(
        self,
        project: Project,
        page: PageParams,
        *,
        status: TwistPlanStatus | None = None,
        kind: TwistPlanKind | None = None,
        q: str | None = None,
        audience: ContextAudience = ContextAudience.author,
    ) -> TwistPlanListResponse:
        items, total = await self.twists.list_plans(project.id, page, status=status, kind=kind, q=q)
        schemas = [await self._to_plan_schema(item, audience=audience) for item in items]
        return paginated(schemas, page.page, page.page_size, total)

    async def get_twist(
        self,
        project: Project,
        twist_id: uuid.UUID,
        *,
        audience: ContextAudience = ContextAudience.author,
    ) -> TwistPlanSchema:
        twist = await self._get_twist_or_404(project.id, twist_id)
        return await self._to_plan_schema(twist, audience=audience)

    async def create_twist(
        self,
        project: Project,
        user_id: uuid.UUID,
        payload: TwistPlanCreateRequest,
    ) -> TwistPlanSchema:
        twist = TwistPlan(
            project_id=project.id,
            title=payload.title.strip(),
            secret_truth=payload.secret_truth,
            kind=payload.kind,
            misdirection=payload.misdirection,
            constraints_json=dict(payload.constraints_json or {}),
            genre_strictness=payload.genre_strictness.value if payload.genre_strictness else None,
            created_by=user_id,
        )
        created = await self.twists.create_plan(twist)
        await self.session.refresh(created)
        return await self._to_plan_schema(created)

    async def update_twist(
        self,
        project: Project,
        twist_id: uuid.UUID,
        payload: TwistPlanUpdateRequest,
    ) -> TwistPlanSchema:
        twist = await self._get_twist_or_404(project.id, twist_id)
        self._guard_paid_off(twist)
        if payload.title is not None:
            twist.title = payload.title.strip()
        if payload.secret_truth is not None:
            twist.secret_truth = payload.secret_truth
        if payload.misdirection is not None:
            twist.misdirection = payload.misdirection
        if payload.constraints_json is not None:
            twist.constraints_json = dict(payload.constraints_json)
        if payload.genre_strictness is not None:
            twist.genre_strictness = payload.genre_strictness.value
        if payload.status is not None:
            validate_twist_transition(twist.status, payload.status)
            twist.status = payload.status
        await self.twists.update_plan(twist)
        await self.session.refresh(twist)
        return await self._to_plan_schema(twist)

    async def abandon_twist(self, project: Project, twist_id: uuid.UUID) -> None:
        twist = await self._get_twist_or_404(project.id, twist_id)
        self._guard_paid_off(twist)
        validate_twist_transition(twist.status, TwistPlanStatus.abandoned)
        twist.status = TwistPlanStatus.abandoned
        await self.twists.update_plan(twist)

    async def transition_twist(
        self,
        project: Project,
        twist_id: uuid.UUID,
        payload: TwistTransitionRequest,
    ) -> TwistPlanSchema:
        twist = await self._get_twist_or_404(project.id, twist_id)
        self._guard_paid_off(twist)
        validate_twist_transition(twist.status, payload.status)
        twist.status = payload.status
        await self.twists.update_plan(twist)
        await self.session.refresh(twist)
        return await self._to_plan_schema(twist)

    async def list_plants(self, project: Project, twist_id: uuid.UUID) -> TwistPlantListResponse:
        await self._get_twist_or_404(project.id, twist_id)
        plants = await self.twists.list_plants(twist_id)
        items: list[TwistPlantSchema] = []
        for plant in plants:
            chapter_num = await self._chapter_number(plant.chapter_id)
            items.append(twist_plant_from_model(plant, chapter_num))
        return TwistPlantListResponse(items=items)

    async def create_plant(
        self,
        project: Project,
        twist_id: uuid.UUID,
        payload: TwistPlantCreateRequest,
    ) -> TwistPlantSchema:
        twist = await self._get_twist_or_404(project.id, twist_id)
        self._guard_paid_off(twist)
        await self._ensure_chapter_in_project(project.id, payload.chapter_id)
        await self._ensure_chapter_unlocked(project.id, payload.chapter_id)

        plant = TwistPlant(
            project_id=project.id,
            twist_id=twist.id,
            chapter_id=payload.chapter_id,
            beat_id=payload.beat_id,
            salience=payload.salience,
            snippet=payload.snippet,
            prose_span_start=payload.prose_span_start,
            prose_span_end=payload.prose_span_end,
            sort_order=payload.sort_order,
        )
        created = await self.twists.create_plant(plant)
        twist.status = status_after_first_plant(twist.status)
        await self.twists.update_plan(twist)
        await self.session.refresh(created)
        chapter_num = await self._chapter_number(created.chapter_id)
        return twist_plant_from_model(created, chapter_num)

    async def update_plant(
        self,
        project: Project,
        twist_id: uuid.UUID,
        plant_id: uuid.UUID,
        payload: TwistPlantUpdateRequest,
    ) -> TwistPlantSchema:
        twist = await self._get_twist_or_404(project.id, twist_id)
        self._guard_paid_off(twist)
        plant = await self.twists.get_plant(project.id, twist_id, plant_id)
        if plant is None:
            raise NotFoundError()
        await self._ensure_chapter_unlocked(project.id, plant.chapter_id)
        if payload.chapter_id is not None:
            await self._ensure_chapter_in_project(project.id, payload.chapter_id)
            await self._ensure_chapter_unlocked(project.id, payload.chapter_id)
            plant.chapter_id = payload.chapter_id
        if payload.beat_id is not None:
            plant.beat_id = payload.beat_id
        if payload.salience is not None:
            plant.salience = payload.salience
        if payload.snippet is not None:
            plant.snippet = payload.snippet
        if payload.prose_span_start is not None:
            plant.prose_span_start = payload.prose_span_start
        if payload.prose_span_end is not None:
            plant.prose_span_end = payload.prose_span_end
        if payload.sort_order is not None:
            plant.sort_order = payload.sort_order
        if payload.twist_id is not None and payload.twist_id != twist_id:
            target = await self._get_twist_or_404(project.id, payload.twist_id)
            self._guard_paid_off(target)
            plant.twist_id = payload.twist_id
        await self.session.flush()
        await self.session.refresh(plant)
        chapter_num = await self._chapter_number(plant.chapter_id)
        return twist_plant_from_model(plant, chapter_num)

    async def delete_plant(
        self, project: Project, twist_id: uuid.UUID, plant_id: uuid.UUID
    ) -> None:
        twist = await self._get_twist_or_404(project.id, twist_id)
        self._guard_paid_off(twist)
        plant = await self.twists.get_plant(project.id, twist_id, plant_id)
        if plant is None:
            raise NotFoundError()
        await self._ensure_chapter_unlocked(project.id, plant.chapter_id)
        await self.twists.delete_plant(plant)

    async def _validate_plant_refs(
        self,
        twist_id: uuid.UUID,
        required_plant_ids: list[uuid.UUID],
    ) -> None:
        if not required_plant_ids:
            return
        plants = await self.twists.list_plants(twist_id)
        owned = {p.id for p in plants}
        for plant_id in required_plant_ids:
            if plant_id not in owned:
                raise InvalidPlantReferenceError()

    async def get_payoff(self, project: Project, twist_id: uuid.UUID) -> TwistPayoffSchema:
        await self._get_twist_or_404(project.id, twist_id)
        payoff = await self.twists.get_payoff(project.id, twist_id)
        if payoff is None:
            raise NotFoundError()
        target_num = await self._chapter_number(payoff.target_chapter_id)
        return twist_payoff_from_model(payoff, target_num)

    async def create_payoff(
        self,
        project: Project,
        twist_id: uuid.UUID,
        payload: TwistPayoffCreateRequest,
    ) -> TwistPayoffSchema:
        twist = await self._get_twist_or_404(project.id, twist_id)
        self._guard_paid_off(twist)
        existing = await self.twists.get_payoff(project.id, twist_id)
        if existing is not None:
            raise PayoffAlreadyExistsError()
        await self._ensure_chapter_in_project(project.id, payload.target_chapter_id)
        await self._validate_plant_refs(twist_id, payload.required_plant_ids)

        payoff = TwistPayoff(
            project_id=project.id,
            twist_id=twist.id,
            target_chapter_id=payload.target_chapter_id,
            required_plant_ids=list(payload.required_plant_ids),
            min_plants=payload.min_plants,
        )
        created = await self.twists.create_payoff(payoff)
        twist.status = status_after_payoff(twist.status)
        await self.twists.update_plan(twist)
        await self.session.refresh(created)
        target_num = await self._chapter_number(created.target_chapter_id)
        return twist_payoff_from_model(created, target_num)

    async def update_payoff(
        self,
        project: Project,
        twist_id: uuid.UUID,
        payoff_id: uuid.UUID,
        payload: TwistPayoffUpdateRequest,
    ) -> TwistPayoffSchema:
        twist = await self._get_twist_or_404(project.id, twist_id)
        self._guard_paid_off(twist)
        payoff = await self.twists.get_payoff_by_id(project.id, twist_id, payoff_id)
        if payoff is None:
            raise NotFoundError()
        if payload.target_chapter_id is not None:
            await self._ensure_chapter_in_project(project.id, payload.target_chapter_id)
            payoff.target_chapter_id = payload.target_chapter_id
        if payload.required_plant_ids is not None:
            await self._validate_plant_refs(twist_id, payload.required_plant_ids)
            payoff.required_plant_ids = list(payload.required_plant_ids)
        if payload.min_plants is not None:
            payoff.min_plants = payload.min_plants
        await self.session.flush()
        await self.session.refresh(payoff)
        target_num = await self._chapter_number(payoff.target_chapter_id)
        return twist_payoff_from_model(payoff, target_num)

    async def delete_payoff(
        self, project: Project, twist_id: uuid.UUID, payoff_id: uuid.UUID
    ) -> None:
        twist = await self._get_twist_or_404(project.id, twist_id)
        self._guard_paid_off(twist)
        payoff = await self.twists.get_payoff_by_id(project.id, twist_id, payoff_id)
        if payoff is None:
            raise NotFoundError()
        await self.twists.delete_payoff(payoff)

    def _preview_secret(self, secret: str, max_len: int = 40) -> str:
        if len(secret) <= max_len:
            return secret
        return secret[: max_len - 1] + "…"

    async def get_board(
        self,
        project: Project,
        *,
        kind: TwistPlanKind | None = None,
        include_abandoned: bool = False,
    ) -> TwistBoardResponse:
        twists = await self.twists.list_all_plans(
            project.id, kind=kind, include_abandoned=include_abandoned
        )
        all_plants = await self.twists.list_plants_for_project(project.id)
        chapter_numbers: dict[uuid.UUID, int] = {}
        for plant in all_plants:
            if plant.chapter_id not in chapter_numbers:
                chapter_numbers[plant.chapter_id] = await self._chapter_number(plant.chapter_id)

        foreshadow_plants = [
            ForeshadowPlantContext(
                plant_id=p.id,
                twist_id=p.twist_id,
                chapter_id=p.chapter_id,
                chapter_number=chapter_numbers[p.chapter_id],
            )
            for p in all_plants
        ]

        secrets_cards: list[TwistBoardCard] = []
        plants_cards: list[TwistBoardCard] = []
        payoffs_cards: list[TwistBoardCard] = []
        revealed_cards: list[TwistBoardCard] = []

        twist_map = {t.id: t for t in twists}
        genre = project.genre_profile

        for twist in twists:
            if twist.status == TwistPlanStatus.seeded:
                plant_count = sum(1 for p in all_plants if p.twist_id == twist.id)
                secrets_cards.append(
                    TwistBoardCard(
                        card_type="twist",
                        twist_id=twist.id,
                        title=twist.title,
                        status=twist.status,
                        kind=twist.kind,
                        secret_truth_preview=self._preview_secret(twist.secret_truth),
                        plant_count=plant_count,
                        fairness=TwistFairnessState(state="ok", issue_codes=[]),
                    )
                )
            elif twist.status == TwistPlanStatus.paid_off:
                revealed_cards.append(
                    TwistBoardCard(
                        card_type="twist",
                        twist_id=twist.id,
                        title=twist.title,
                        status=twist.status,
                        kind=twist.kind,
                        plant_count=sum(1 for p in all_plants if p.twist_id == twist.id),
                    )
                )
            elif twist.status == TwistPlanStatus.armed:
                payoff = await self.twists.get_payoff(project.id, twist.id)
                if payoff is None:
                    continue
                target_num = await self._chapter_number(payoff.target_chapter_id)
                ctx = ForeshadowPayoffContext(
                    payoff_id=payoff.id,
                    twist=ForeshadowTwistContext(
                        twist_id=twist.id,
                        title=twist.title,
                        secret_truth=twist.secret_truth,
                        status=twist.status,
                        constraints_json=dict(twist.constraints_json or {}),
                        genre_strictness=twist.genre_strictness,
                    ),
                    target_chapter_id=payoff.target_chapter_id,
                    target_chapter_number=target_num,
                    min_plants=payoff.min_plants,
                    required_plant_ids=list(payoff.required_plant_ids or []),
                )
                codes, state = evaluate_payoff_fairness(
                    payoff=ctx,
                    plants=foreshadow_plants,
                    genre_profile=genre,
                )
                plant_count = count_eligible_plants(foreshadow_plants, twist.id, target_num)
                payoffs_cards.append(
                    TwistBoardCard(
                        card_type="payoff",
                        payoff_id=payoff.id,
                        twist_id=twist.id,
                        twist_title=twist.title,
                        target_chapter_number=target_num,
                        min_plants=payoff.min_plants,
                        plant_count=plant_count,
                        required_plant_ids=list(payoff.required_plant_ids or []),
                        fairness=TwistFairnessState(state=state, issue_codes=codes),
                    )
                )

        for plant in all_plants:
            twist = twist_map.get(plant.twist_id)
            if twist is None:
                continue
            if twist.status in (TwistPlanStatus.abandoned, TwistPlanStatus.paid_off):
                continue
            plants_cards.append(
                TwistBoardCard(
                    card_type="plant",
                    plant_id=plant.id,
                    twist_id=twist.id,
                    twist_title=twist.title,
                    chapter_number=chapter_numbers[plant.chapter_id],
                    salience=plant.salience,
                    snippet=plant.snippet,
                )
            )

        return TwistBoardResponse(
            columns=[
                TwistBoardColumn(id="secrets", label="Secrets", cards=secrets_cards),
                TwistBoardColumn(id="plants", label="Plants", cards=plants_cards),
                TwistBoardColumn(id="payoffs", label="Payoffs", cards=payoffs_cards),
                TwistBoardColumn(id="revealed", label="Revealed", cards=revealed_cards),
            ]
        )


def count_eligible_plants(
    plants: list[ForeshadowPlantContext],
    twist_id: uuid.UUID,
    target_chapter_number: int,
) -> int:
    from app.services.continuity.foreshadow import count_eligible_plants as _count

    return _count(plants, twist_id, target_chapter_number)
