"""Export job routes."""

import uuid

from fastapi import APIRouter, Query, Response, status

from app.deps import CurrentUserId, DbSession, ProjectAccess
from app.schemas.export import ExportJob, ExportJobCreateRequest, ExportJobListResponse
from app.services.export_service import ExportService
from app.utils.pagination import PageParams

router = APIRouter(prefix="/projects/{project_id}/export", tags=["Export"])


@router.get("/jobs", response_model=ExportJobListResponse)
async def list_export_jobs(
    project: ProjectAccess,
    session: DbSession,
    page: int = Query(default=1, ge=1),
    page_size: int = Query(default=20, ge=1, le=100),
) -> ExportJobListResponse:
    params = PageParams(page=page, page_size=page_size)
    return await ExportService(session).list_jobs(project, params)


@router.post("/jobs", response_model=ExportJob, status_code=status.HTTP_202_ACCEPTED)
async def enqueue_export_job(
    payload: ExportJobCreateRequest,
    project: ProjectAccess,
    user_id: CurrentUserId,
    session: DbSession,
) -> ExportJob:
    return await ExportService(session).enqueue_job(project, user_id, payload)


@router.get("/jobs/{job_id}", response_model=ExportJob)
async def get_export_job(
    job_id: uuid.UUID,
    project: ProjectAccess,
    session: DbSession,
) -> ExportJob:
    return await ExportService(session).get_job(project, job_id)


@router.delete("/jobs/{job_id}", status_code=status.HTTP_204_NO_CONTENT)
async def cancel_export_job(
    job_id: uuid.UUID,
    project: ProjectAccess,
    session: DbSession,
) -> Response:
    await ExportService(session).cancel_job(project, job_id)
    return Response(status_code=status.HTTP_204_NO_CONTENT)


@router.get("/jobs/{job_id}/download")
async def download_export_job(
    job_id: uuid.UUID,
    project: ProjectAccess,
    session: DbSession,
):
    return await ExportService(session).download_artifact(project, job_id)
