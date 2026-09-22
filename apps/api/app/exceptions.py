"""Application exceptions and error response helpers."""

from typing import Any

from fastapi import Request
from fastapi.exceptions import RequestValidationError
from fastapi.responses import JSONResponse
from starlette.exceptions import HTTPException as StarletteHTTPException


class AppError(Exception):
    """Base application error with HTTP mapping."""

    def __init__(
        self,
        *,
        status_code: int,
        code: str,
        message: str,
        details: list[dict[str, Any]] | None = None,
    ) -> None:
        self.status_code = status_code
        self.code = code
        self.message = message
        self.details = details or []
        super().__init__(message)


class NotFoundError(AppError):
    def __init__(self, message: str = "Resource not found") -> None:
        super().__init__(status_code=404, code="not_found", message=message)


class UnauthorizedError(AppError):
    def __init__(self, message: str = "X-User-Id header is required") -> None:
        super().__init__(status_code=401, code="unauthorized", message=message)


class ValidationAppError(AppError):
    def __init__(self, message: str, details: list[dict[str, Any]] | None = None) -> None:
        super().__init__(
            status_code=400,
            code="validation_error",
            message=message,
            details=details,
        )


class SlugConflictError(AppError):
    def __init__(self, slug: str, suggested_slug: str) -> None:
        super().__init__(
            status_code=409,
            code="slug_conflict",
            message=f"Slug '{slug}' already exists",
            details=[{"suggested_slug": suggested_slug}],
        )


class EntryKeyConflictError(AppError):
    def __init__(self, entry_key: str) -> None:
        super().__init__(
            status_code=409,
            code="entry_key_conflict",
            message=f"Entry key '{entry_key}' already exists",
        )


class ChapterNumberConflictError(AppError):
    def __init__(self, number: int) -> None:
        super().__init__(
            status_code=409,
            code="chapter_number_conflict",
            message=f"Chapter number {number} already exists",
        )


class ChapterLockedError(AppError):
    def __init__(self, message: str = "Chapter is locked after settle") -> None:
        super().__init__(status_code=409, code="chapter_locked", message=message)


class InvalidChapterStatusTransitionError(AppError):
    def __init__(self, message: str = "Invalid chapter status transition") -> None:
        super().__init__(
            status_code=409,
            code="invalid_chapter_status_transition",
            message=message,
        )


class ContinuityFailBlocksSettleError(AppError):
    def __init__(self, details: list[dict[str, Any]] | None = None) -> None:
        super().__init__(
            status_code=409,
            code="continuity_fail_blocks_settle",
            message="Unresolved continuity FAIL blocks settle",
            details=details,
        )


class ContinuityCheckRequiredError(AppError):
    def __init__(self, message: str = "Continuity check required before settle") -> None:
        super().__init__(
            status_code=422,
            code="continuity_check_required",
            message=message,
        )


class BeatKeyConflictError(AppError):
    def __init__(self, beat_key: str) -> None:
        super().__init__(
            status_code=409,
            code="beat_key_conflict",
            message=f"Beat key '{beat_key}' already exists",
        )


class CharacterArchivedError(AppError):
    def __init__(self, message: str = "Character is archived") -> None:
        super().__init__(status_code=409, code="character_archived", message=message)


class DuplicateDisplayNameError(AppError):
    def __init__(self, display_name: str) -> None:
        super().__init__(
            status_code=409,
            code="duplicate_display_name",
            message=f"Display name '{display_name}' already exists",
        )


class ProvisionalAlreadyResolvedError(AppError):
    def __init__(self, message: str = "Provisional mention already resolved") -> None:
        super().__init__(
            status_code=409,
            code="provisional_already_resolved",
            message=message,
        )


class AlreadyMaxTierError(AppError):
    def __init__(self, message: str = "Character is already at tier 3") -> None:
        super().__init__(status_code=409, code="already_max_tier", message=message)


class TierRequirementsNotMetError(AppError):
    def __init__(self, message: str, details: list[dict[str, Any]] | None = None) -> None:
        super().__init__(
            status_code=422,
            code="tier_requirements_not_met",
            message=message,
            details=details,
        )


class InvalidMergeRequestError(AppError):
    def __init__(
        self, message: str = "Provide target_character_id or create_new, not both"
    ) -> None:
        super().__init__(status_code=422, code="invalid_merge_request", message=message)


class NotImplementedFeatureError(AppError):
    def __init__(self, message: str = "Feature not implemented") -> None:
        super().__init__(status_code=501, code="not_implemented", message=message)


class TwistPaidOffImmutableError(AppError):
    def __init__(self, message: str = "Paid-off twist is immutable") -> None:
        super().__init__(status_code=409, code="twist_paid_off_immutable", message=message)


class InvalidTwistStatusTransitionError(AppError):
    def __init__(self, message: str = "Invalid twist status transition") -> None:
        super().__init__(
            status_code=409,
            code="invalid_twist_status_transition",
            message=message,
        )


class PayoffAlreadyExistsError(AppError):
    def __init__(self, message: str = "Payoff already exists for this twist") -> None:
        super().__init__(status_code=422, code="payoff_already_exists", message=message)


class InvalidPlantReferenceError(AppError):
    def __init__(self, message: str = "Invalid plant reference for payoff") -> None:
        super().__init__(status_code=422, code="invalid_plant_reference", message=message)


class InvalidPsycheCardError(AppError):
    def __init__(
        self,
        message: str = "Invalid psyche card shape",
        details: list[dict[str, Any]] | None = None,
    ) -> None:
        super().__init__(
            status_code=422,
            code="invalid_psyche_card",
            message=message,
            details=details,
        )


class PsychStateImmutableError(AppError):
    def __init__(self, message: str = "Settled psych state cannot be modified") -> None:
        super().__init__(status_code=409, code="psych_state_immutable", message=message)


class PsychStateAlreadySettledError(AppError):
    def __init__(
        self, message: str = "Psych state already settled for this character and chapter"
    ) -> None:
        super().__init__(
            status_code=409,
            code="psych_state_already_settled",
            message=message,
        )


class RankInUseError(AppError):
    def __init__(self, message: str = "Rank is referenced by techniques") -> None:
        super().__init__(status_code=409, code="rank_in_use", message=message)


class PowerSystemDisabledError(AppError):
    def __init__(self, message: str = "Power system module is disabled") -> None:
        super().__init__(status_code=409, code="power_system_disabled", message=message)


class InvalidRankLadderError(AppError):
    def __init__(self, message: str = "Invalid rank ladder ordering") -> None:
        super().__init__(status_code=422, code="invalid_rank_ladder", message=message)


class InvalidGenreRulePackError(AppError):
    def __init__(self, message: str = "Invalid genre rule pack") -> None:
        super().__init__(status_code=422, code="invalid_genre_rule_pack", message=message)


class CraftPackGenreIncompatibleError(AppError):
    def __init__(self, craft_pack_id: str, genre_profile: str) -> None:
        super().__init__(
            status_code=409,
            code="genre_incompatible",
            message=(
                f"Craft pack '{craft_pack_id}' is not compatible with "
                f"genre profile '{genre_profile}'"
            ),
        )


class LLMProviderError(AppError):
    def __init__(self, message: str = "LLM provider error") -> None:
        super().__init__(status_code=502, code="llm_provider_error", message=message)


class PromptEditRateLimitedError(AppError):
    def __init__(self, message: str = "Prompt edit rate limit exceeded") -> None:
        super().__init__(status_code=429, code="prompt_edit_rate_limited", message=message)


class PromptEditAlreadyAppliedError(AppError):
    def __init__(self, message: str = "Turn already applied") -> None:
        super().__init__(status_code=409, code="prompt_edit_already_applied", message=message)


class InvalidRelationshipPairError(AppError):
    def __init__(self, message: str = "Invalid relationship character pair") -> None:
        super().__init__(status_code=422, code="invalid_relationship_pair", message=message)


class RelationshipExistsError(AppError):
    def __init__(self, message: str = "Relationship already exists for character pair") -> None:
        super().__init__(status_code=409, code="relationship_exists", message=message)


class RelationshipEventImmutableError(AppError):
    def __init__(self, message: str = "Settled relationship event cannot be modified") -> None:
        super().__init__(status_code=409, code="relationship_event_immutable", message=message)


class InvalidStakesLevelError(AppError):
    def __init__(self, message: str = "stakes_level must be between 0 and 5") -> None:
        super().__init__(status_code=422, code="invalid_stakes_level", message=message)


class InvalidActNumberError(AppError):
    def __init__(self, message: str = "act_number exceeds act_count") -> None:
        super().__init__(status_code=422, code="invalid_act_number", message=message)


class InvalidSceneTypeError(AppError):
    def __init__(self, scene_type: str) -> None:
        super().__init__(
            status_code=422,
            code="invalid_scene_type",
            message=f"Unknown scene_type '{scene_type}'",
        )


class SceneMissingOutcomeError(AppError):
    def __init__(self, message: str = "Completed beat requires outcome") -> None:
        super().__init__(status_code=422, code="scene_missing_outcome", message=message)


class SceneLLMAuditorError(AppError):
    def __init__(self, message: str = "Scene LLM auditor error") -> None:
        super().__init__(status_code=502, code="scene_llm_auditor_error", message=message)


class NoteNotEditableError(AppError):
    def __init__(self, message: str = "Note is not editable") -> None:
        super().__init__(status_code=409, code="note_not_editable", message=message)


class NoteAlreadyPromotedError(AppError):
    def __init__(self, message: str = "Note already promoted") -> None:
        super().__init__(status_code=409, code="note_already_promoted", message=message)


class ResearchLinkDuplicateError(AppError):
    def __init__(self, message: str = "Link already exists") -> None:
        super().__init__(status_code=409, code="link_duplicate", message=message)


class InvalidLinkTargetError(AppError):
    def __init__(self, message: str = "Link type/target mismatch") -> None:
        super().__init__(status_code=422, code="invalid_link_target", message=message)


class InvalidBibleSectionError(AppError):
    def __init__(self, message: str = "Invalid bible section for promote") -> None:
        super().__init__(status_code=422, code="invalid_bible_section", message=message)


class ProjectAlreadyInSeriesError(AppError):
    def __init__(self, message: str = "Project already belongs to a series") -> None:
        super().__init__(status_code=409, code="project_already_in_series", message=message)


class SeriesNotAttachedError(AppError):
    def __init__(self, message: str = "Project is not attached to a series") -> None:
        super().__init__(status_code=422, code="series_not_attached", message=message)


class InvalidExportOptionsError(AppError):
    def __init__(self, message: str = "Invalid export options") -> None:
        super().__init__(status_code=422, code="invalid_export_options", message=message)


class ExportJobNotDoneError(AppError):
    def __init__(self, message: str = "Export job is not done") -> None:
        super().__init__(status_code=409, code="export_job_not_done", message=message)


class ExportJobRunningError(AppError):
    def __init__(self, message: str = "Export job is running") -> None:
        super().__init__(status_code=409, code="export_job_running", message=message)


class InvalidRealityAnchorsError(AppError):
    def __init__(self, message: str = "Unknown reality_anchors mode") -> None:
        super().__init__(status_code=422, code="invalid_reality_anchors", message=message)


class InvalidClaimCategoryError(AppError):
    def __init__(self, message: str = "Unknown claim category") -> None:
        super().__init__(status_code=422, code="invalid_claim_category", message=message)


class FactCheckRunPendingError(AppError):
    def __init__(self, message: str = "Fact-check run already pending for prose version") -> None:
        super().__init__(status_code=409, code="fact_check_run_pending", message=message)


class FactCheckRunNotDoneError(AppError):
    def __init__(self, message: str = "Fact-check run is not done") -> None:
        super().__init__(status_code=409, code="fact_check_run_not_done", message=message)


class ClaimNoProposedCorrectionError(AppError):
    def __init__(self, message: str = "Claim has no proposed correction") -> None:
        super().__init__(status_code=409, code="claim_no_proposed_correction", message=message)


class ClaimNoCitationsError(AppError):
    def __init__(self, message: str = "Claim has no citations") -> None:
        super().__init__(status_code=409, code="claim_no_citations", message=message)


class ClaimAlreadyPromotedError(AppError):
    def __init__(self, message: str = "Claim evidence already promoted") -> None:
        super().__init__(status_code=409, code="claim_already_promoted", message=message)


class FactCheckFailBlocksSettleError(AppError):
    def __init__(self, details: list[dict[str, Any]] | None = None) -> None:
        super().__init__(
            status_code=409,
            code="fact_check_fail_blocks_settle",
            message="Unresolved fact-check FAIL blocks settle (project setting enabled)",
            details=details,
        )


def error_body(
    code: str, message: str, details: list[dict[str, Any]] | None = None
) -> dict[str, Any]:
    payload: dict[str, Any] = {"error": {"code": code, "message": message}}
    if details:
        payload["error"]["details"] = details
    return payload


async def app_error_handler(_request: Request, exc: AppError) -> JSONResponse:
    return JSONResponse(
        status_code=exc.status_code,
        content=error_body(exc.code, exc.message, exc.details or None),
    )


async def http_exception_handler(_request: Request, exc: StarletteHTTPException) -> JSONResponse:
    if isinstance(exc.detail, dict) and "error" in exc.detail:
        return JSONResponse(status_code=exc.status_code, content=exc.detail)
    code = "not_found" if exc.status_code == 404 else "validation_error"
    return JSONResponse(
        status_code=exc.status_code,
        content=error_body(code, str(exc.detail)),
    )


async def validation_exception_handler(
    _request: Request, exc: RequestValidationError
) -> JSONResponse:
    details = [
        {"loc": list(err["loc"]), "msg": err["msg"], "type": err["type"]} for err in exc.errors()
    ]
    return JSONResponse(
        status_code=400,
        content=error_body("validation_error", "Request validation failed", details),
    )
