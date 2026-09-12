"""Exception and error handler unit tests."""

import pytest
from fastapi.exceptions import RequestValidationError
from starlette.exceptions import HTTPException

from app.exceptions import (
    AppError,
    ChapterNumberConflictError,
    EntryKeyConflictError,
    NotFoundError,
    SlugConflictError,
    UnauthorizedError,
    ValidationAppError,
    app_error_handler,
    error_body,
    http_exception_handler,
    validation_exception_handler,
)


@pytest.mark.unit
def test_error_body_with_details() -> None:
    body = error_body("test_code", "message", [{"field": "x"}])
    assert body["error"]["code"] == "test_code"
    assert body["error"]["details"] == [{"field": "x"}]


@pytest.mark.unit
@pytest.mark.parametrize(
    ("exc", "code"),
    [
        (NotFoundError(), "not_found"),
        (UnauthorizedError(), "unauthorized"),
        (ValidationAppError("bad"), "validation_error"),
        (SlugConflictError("slug", "slug-2"), "slug_conflict"),
        (EntryKeyConflictError("key"), "entry_key_conflict"),
        (ChapterNumberConflictError(1), "chapter_number_conflict"),
    ],
)
def test_app_errors_have_codes(exc: AppError, code: str) -> None:
    assert exc.code == code


@pytest.mark.unit
async def test_app_error_handler() -> None:
    response = await app_error_handler(None, NotFoundError("missing"))
    assert response.status_code == 404
    assert response.body


@pytest.mark.unit
async def test_http_exception_handler_with_dict_detail() -> None:
    exc = HTTPException(status_code=404, detail={"error": {"code": "not_found", "message": "x"}})
    response = await http_exception_handler(None, exc)
    assert response.status_code == 404


@pytest.mark.unit
async def test_http_exception_handler_with_string_detail() -> None:
    exc = HTTPException(status_code=400, detail="bad")
    response = await http_exception_handler(None, exc)
    assert response.status_code == 400


@pytest.mark.unit
async def test_validation_exception_handler() -> None:
    exc = RequestValidationError(
        errors=[{"loc": ("body", "title"), "msg": "required", "type": "missing"}]
    )
    response = await validation_exception_handler(None, exc)
    assert response.status_code == 400
