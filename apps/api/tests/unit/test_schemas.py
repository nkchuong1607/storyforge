"""Pydantic schema unit tests."""

import pytest
from pydantic import ValidationError

from app.schemas.project import ProjectCreateRequest


@pytest.mark.unit
def test_project_create_request_valid() -> None:
    payload = ProjectCreateRequest(
        title="Test",
        language="vi",
        genre_profile="xianxia",
        template="blank",
    )
    assert payload.title == "Test"


@pytest.mark.unit
def test_project_create_request_rejects_empty_title() -> None:
    with pytest.raises(ValidationError):
        ProjectCreateRequest(
            title="",
            language="vi",
            genre_profile="custom",
            template="blank",
        )


@pytest.mark.unit
def test_project_create_request_optional_slug() -> None:
    payload = ProjectCreateRequest(
        title="Test",
        language="en",
        genre_profile="custom",
        template="blank",
        slug="my-project",
    )
    assert payload.slug == "my-project"
