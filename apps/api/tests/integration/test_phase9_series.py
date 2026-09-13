"""Phase 9 series integration tests."""

import pytest
from httpx import AsyncClient
from sqlalchemy.ext.asyncio import AsyncSession

from app.models.series import SeriesBibleSlice
from tests.factories import blank_project_payload, project_create_payload


@pytest.mark.integration
async def test_series_create_attach_inherit(
    client: AsyncClient,
    user_a_headers: dict[str, str],
    session: AsyncSession,
) -> None:
    series_resp = await client.post(
        "/series",
        json={
            "title": "Thiên Kiếm — bộ ba",
            "slug": "thien-kiem-trilogy",
            "create_hub_project": True,
        },
        headers=user_a_headers,
    )
    assert series_resp.status_code == 201
    series_id = series_resp.json()["id"]

    child = await client.post(
        "/projects", json=blank_project_payload(title="Book 2"), headers=user_a_headers
    )
    child_id = child.json()["id"]

    attach = await client.post(
        f"/series/{series_id}/projects",
        json={"project_id": child_id, "book_order": 2},
        headers=user_a_headers,
    )
    assert attach.status_code == 201

    slice_row = SeriesBibleSlice(
        series_id=series_id,
        version=2,
        slice_json={"world": {"rules": {"cultivation_realms": ["Luyện Khí"]}}},
        inherited_sections=["world", "glossary"],
    )
    session.add(slice_row)
    await session.commit()

    inherited = await client.get(
        f"/projects/{child_id}/series/inherited-slice",
        headers=user_a_headers,
    )
    assert inherited.status_code == 200
    body = inherited.json()
    assert body["slice_version"] == 2
    assert body["drift_warning"] is True

    override = await client.post(
        f"/projects/{child_id}/series/overrides",
        json={
            "overrides_series_key": "world.rules.cultivation_realms",
            "section": "world",
            "title": "Book 2 extension",
            "content_md": "Kim Đan added",
            "override_reason": "Book 2 power creep",
        },
        headers=user_a_headers,
    )
    assert override.status_code == 201
    assert override.json()["metadata"]["series_override"] is True


@pytest.mark.integration
async def test_detach_series_project(
    client: AsyncClient,
    user_a_headers: dict[str, str],
) -> None:
    series_resp = await client.post(
        "/series",
        json={"title": "Detach test", "slug": "detach-series", "create_hub_project": False},
        headers=user_a_headers,
    )
    series_id = series_resp.json()["id"]
    child = await client.post(
        "/projects", json=project_create_payload(title="Child"), headers=user_a_headers
    )
    child_id = child.json()["id"]
    await client.post(
        f"/series/{series_id}/projects",
        json={"project_id": child_id},
        headers=user_a_headers,
    )
    detach = await client.delete(
        f"/series/{series_id}/projects/{child_id}",
        headers=user_a_headers,
    )
    assert detach.status_code == 204
