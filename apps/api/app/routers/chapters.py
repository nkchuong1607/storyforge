"""Chapter routes."""

import uuid

from fastapi import APIRouter, Header, HTTPException, Query, Response, status

from app.deps import ChapterAccess, CurrentUserId, DbSession, ProjectAccess
from app.exceptions import AppError
from app.schemas.beat import (
    SceneBeat,
    SceneBeatCreateRequest,
    SceneBeatListResponse,
    SceneBeatUpdateRequest,
)
from app.schemas.chapter import (
    Chapter,
    ChapterCreateRequest,
    ChapterListResponse,
    ChapterUpdateRequest,
)
from app.schemas.character import ExtractCharactersRequest, ExtractCharactersResponse
from app.schemas.continuity import (
    ContinuityCheckRequest,
    ContinuityOverride,
    ContinuityOverrideCreateRequest,
    ContinuityReport,
    SettleChapterRequest,
    SettleChapterResponse,
    StateDiff,
)
from app.schemas.prose import (
    ProseVersionCompareResponse,
    ProseVersionCreateRequest,
    ProseVersionDetail,
    ProseVersionListResponse,
)
from app.services.beat import BeatService
from app.services.chapter import ChapterService
from app.services.character_extract import CharacterExtractService
from app.services.continuity_service import ContinuityService
from app.services.prose import ProseService
from app.services.settle import SettleService
from app.utils.pagination import clamp_page_params

router = APIRouter(prefix="/projects/{project_id}/chapters", tags=["Chapters"])


@router.get("", response_model=ChapterListResponse)
async def list_chapters(
    project: ProjectAccess,
    session: DbSession,
    page: int = Query(default=1, ge=1),
    page_size: int = Query(default=20, ge=1, le=100),
) -> ChapterListResponse:
    service = ChapterService(session)
    page_params = clamp_page_params(page, page_size)
    return await service.list_chapters(project, page_params)


@router.post("", response_model=Chapter, status_code=status.HTTP_201_CREATED)
async def create_chapter(
    payload: ChapterCreateRequest,
    project: ProjectAccess,
    session: DbSession,
) -> Chapter:
    service = ChapterService(session)
    return await service.create_chapter(project, payload)


@router.get("/{chapter_id}", response_model=Chapter)
async def get_chapter(
    project: ProjectAccess,
    chapter: ChapterAccess,
    session: DbSession,
) -> Chapter:
    service = ChapterService(session)
    return await service.get_chapter(project, chapter.id)


@router.patch("/{chapter_id}", response_model=Chapter)
async def update_chapter(
    payload: ChapterUpdateRequest,
    project: ProjectAccess,
    chapter: ChapterAccess,
    session: DbSession,
) -> Chapter:
    service = ChapterService(session)
    return await service.update_chapter(project, chapter.id, payload)


@router.get("/{chapter_id}/beats", response_model=SceneBeatListResponse)
async def list_scene_beats(
    chapter: ChapterAccess,
    session: DbSession,
) -> SceneBeatListResponse:
    service = BeatService(session)
    items = await service.list_beats(chapter)
    return SceneBeatListResponse(items=items)


@router.post("/{chapter_id}/beats", response_model=SceneBeat, status_code=status.HTTP_201_CREATED)
async def create_scene_beat(
    payload: SceneBeatCreateRequest,
    chapter: ChapterAccess,
    session: DbSession,
) -> SceneBeat:
    service = BeatService(session)
    return await service.create_beat(chapter, payload)


@router.patch("/{chapter_id}/beats/{beat_id}", response_model=SceneBeat)
async def update_scene_beat(
    beat_id: uuid.UUID,
    payload: SceneBeatUpdateRequest,
    chapter: ChapterAccess,
    session: DbSession,
) -> SceneBeat:
    service = BeatService(session)
    return await service.update_beat(chapter, beat_id, payload)


@router.delete("/{chapter_id}/beats/{beat_id}", status_code=status.HTTP_204_NO_CONTENT)
async def delete_scene_beat(
    beat_id: uuid.UUID,
    chapter: ChapterAccess,
    session: DbSession,
) -> Response:
    service = BeatService(session)
    await service.delete_beat(chapter, beat_id)
    return Response(status_code=status.HTTP_204_NO_CONTENT)


@router.get("/{chapter_id}/prose-versions", response_model=ProseVersionListResponse)
async def list_prose_versions(
    chapter: ChapterAccess,
    session: DbSession,
    page: int = Query(default=1, ge=1),
    page_size: int = Query(default=20, ge=1, le=100),
) -> ProseVersionListResponse:
    service = ProseService(session)
    page_params = clamp_page_params(page, page_size)
    return await service.list_versions(chapter, page_params)


@router.post(
    "/{chapter_id}/prose-versions",
    response_model=ProseVersionDetail,
    status_code=status.HTTP_201_CREATED,
)
async def create_prose_version(
    payload: ProseVersionCreateRequest,
    project: ProjectAccess,
    chapter: ChapterAccess,
    session: DbSession,
    user_id: CurrentUserId,
) -> ProseVersionDetail:
    service = ProseService(session)
    return await service.create_version(project, chapter, user_id, payload)


@router.get("/{chapter_id}/prose-versions/compare", response_model=ProseVersionCompareResponse)
async def compare_prose_versions(
    chapter: ChapterAccess,
    session: DbSession,
    from_version: int = Query(alias="from", ge=1),
    to_version: int = Query(alias="to", ge=1),
) -> ProseVersionCompareResponse:
    service = ProseService(session)
    return await service.compare_versions(chapter, from_version, to_version)


@router.get("/{chapter_id}/prose-versions/{version}", response_model=ProseVersionDetail)
async def get_prose_version(
    version: int,
    chapter: ChapterAccess,
    session: DbSession,
) -> ProseVersionDetail:
    service = ProseService(session)
    return await service.get_version(chapter, version)


@router.post("/{chapter_id}/continuity-check", response_model=ContinuityReport)
async def run_continuity_check(
    project: ProjectAccess,
    chapter: ChapterAccess,
    session: DbSession,
    user_id: CurrentUserId,
    payload: ContinuityCheckRequest | None = None,
) -> ContinuityReport:
    service = ContinuityService(session)
    return await service.run_check(project, chapter, user_id, payload)


@router.get("/{chapter_id}/continuity-reports/latest", response_model=ContinuityReport)
async def get_latest_continuity_report(
    chapter: ChapterAccess,
    session: DbSession,
) -> ContinuityReport:
    service = ContinuityService(session)
    return await service.get_latest_report(chapter)


@router.get("/{chapter_id}/continuity-reports/{report_id}", response_model=ContinuityReport)
async def get_continuity_report(
    report_id: uuid.UUID,
    chapter: ChapterAccess,
    session: DbSession,
) -> ContinuityReport:
    service = ContinuityService(session)
    return await service.get_report(chapter, report_id)


@router.post(
    "/{chapter_id}/continuity-overrides",
    response_model=ContinuityOverride,
    status_code=status.HTTP_201_CREATED,
)
async def create_continuity_override(
    payload: ContinuityOverrideCreateRequest,
    project: ProjectAccess,
    chapter: ChapterAccess,
    session: DbSession,
    user_id: CurrentUserId,
) -> ContinuityOverride:
    service = ContinuityService(session)
    return await service.create_override(project, chapter, user_id, payload)


@router.get("/{chapter_id}/state-diff", response_model=StateDiff)
async def get_state_diff(
    chapter: ChapterAccess,
    session: DbSession,
    prose_version: int | None = Query(default=None, ge=1),
) -> StateDiff:
    service = ContinuityService(session)
    return await service.get_state_diff(chapter, prose_version)


@router.post("/{chapter_id}/settle", response_model=SettleChapterResponse)
async def settle_chapter(
    project: ProjectAccess,
    chapter: ChapterAccess,
    session: DbSession,
    payload: SettleChapterRequest | None = None,
    idempotency_key: uuid.UUID | None = Header(default=None, alias="Idempotency-Key"),
) -> SettleChapterResponse:
    service = SettleService(session)
    try:
        return await service.settle_chapter(project, chapter, payload, idempotency_key)
    except AppError:
        raise
    except Exception as exc:
        await session.rollback()
        raise HTTPException(status_code=500, detail=str(exc)) from exc


@router.post("/{chapter_id}/extract-characters", response_model=ExtractCharactersResponse)
async def extract_characters(
    project: ProjectAccess,
    chapter: ChapterAccess,
    session: DbSession,
    payload: ExtractCharactersRequest | None = None,
) -> ExtractCharactersResponse:
    service = CharacterExtractService(session)
    return await service.extract_from_chapter(project, chapter.id, payload)
