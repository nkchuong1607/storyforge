"""Test data factories."""

from typing import Any

from app.models.enums import GenreProfile, ProjectLanguage, ProjectTemplate


def project_create_payload(
    *,
    title: str = "Kiếm Lai",
    template: str = "xianxia_starter",
    genre_profile: str = "xianxia",
) -> dict[str, Any]:
    return {
        "title": title,
        "description": "Hành trình tu tiên",
        "language": ProjectLanguage.vi.value,
        "genre_profile": genre_profile,
        "template": template,
    }


def blank_project_payload(*, title: str = "Blank Project") -> dict[str, Any]:
    return {
        "title": title,
        "language": ProjectLanguage.en.value,
        "genre_profile": GenreProfile.custom.value,
        "template": ProjectTemplate.blank.value,
    }
