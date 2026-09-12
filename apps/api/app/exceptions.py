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
