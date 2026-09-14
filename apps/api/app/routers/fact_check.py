"""Fact-check routes."""

import uuid

from fastapi import APIRouter, Query, status

from app.deps import ChapterAccess, CurrentUserId, DbSession, ProjectAccess
from app.schemas.fact_check import (
    FactCheckRunCreateRequest,
    FactCheckRunDetail,
    FactCheckRunListResponse,
    FactClaim,
    FactClaimAcceptFixRequest,
    FactClaimAcceptFixResponse,
    FactClaimDispositionRequest,
    FactClaimPromoteEvidenceRequest,
    FactClaimPromoteEvidenceResponse,
)
from app.services.fact_check_service import FactCheckService
from app.utils.pagination import PageParams

router = APIRouter(prefix="/projects/{project_id}", tags=["FactCheck"])


@router.get(
    "/chapters/{chapter_id}/fact-check/runs",
    response_model=FactCheckRunListResponse,
)
async def list_fact_check_runs(
    project: ProjectAccess,
    chapter: ChapterAccess,
    session: DbSession,
    page: int = Query(default=1, ge=1),
    page_size: int = Query(default=20, ge=1, le=100),
) -> FactCheckRunListResponse:
    params = PageParams(page=page, page_size=page_size)
    return await FactCheckService(session).list_runs(project, chapter.id, params)


@router.post(
    "/chapters/{chapter_id}/fact-check/runs",
    response_model=FactCheckRunDetail,
    status_code=status.HTTP_202_ACCEPTED,
)
async def enqueue_fact_check_run(
    project: ProjectAccess,
    chapter: ChapterAccess,
    user_id: CurrentUserId,
    session: DbSession,
    payload: FactCheckRunCreateRequest | None = None,
) -> FactCheckRunDetail:
    return await FactCheckService(session).enqueue_run(project, chapter.id, user_id, payload)


@router.get(
    "/chapters/{chapter_id}/fact-check/runs/{run_id}",
    response_model=FactCheckRunDetail,
)
async def get_fact_check_run(
    project: ProjectAccess,
    chapter: ChapterAccess,
    run_id: uuid.UUID,
    session: DbSession,
) -> FactCheckRunDetail:
    run = await FactCheckService(session).get_run(project, run_id)
    if run.chapter_id != chapter.id:
        from app.exceptions import NotFoundError

        raise NotFoundError()
    return run


@router.get("/fact-check/runs/{run_id}", response_model=FactCheckRunDetail)
async def get_fact_check_run_by_project(
    project: ProjectAccess,
    run_id: uuid.UUID,
    session: DbSession,
) -> FactCheckRunDetail:
    return await FactCheckService(session).get_run(project, run_id)


@router.post("/fact-check/claims/{claim_id}/disposition", response_model=FactClaim)
async def set_fact_claim_disposition(
    project: ProjectAccess,
    claim_id: uuid.UUID,
    user_id: CurrentUserId,
    session: DbSession,
    payload: FactClaimDispositionRequest,
) -> FactClaim:
    return await FactCheckService(session).set_disposition(project, user_id, claim_id, payload)


@router.post(
    "/fact-check/claims/{claim_id}/accept-fix",
    response_model=FactClaimAcceptFixResponse,
)
async def accept_fact_claim_fix(
    project: ProjectAccess,
    claim_id: uuid.UUID,
    user_id: CurrentUserId,
    session: DbSession,
    payload: FactClaimAcceptFixRequest | None = None,
) -> FactClaimAcceptFixResponse:
    return await FactCheckService(session).accept_fix(project, user_id, claim_id, payload)


@router.post(
    "/fact-check/claims/{claim_id}/promote-evidence",
    response_model=FactClaimPromoteEvidenceResponse,
    status_code=status.HTTP_201_CREATED,
)
async def promote_fact_claim_evidence(
    project: ProjectAccess,
    claim_id: uuid.UUID,
    user_id: CurrentUserId,
    session: DbSession,
    payload: FactClaimPromoteEvidenceRequest | None = None,
) -> FactClaimPromoteEvidenceResponse:
    return await FactCheckService(session).promote_evidence(project, user_id, claim_id, payload)
