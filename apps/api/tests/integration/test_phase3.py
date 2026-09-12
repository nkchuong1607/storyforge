"""Phase 3 integration tests — characters, provisionals, extract, context packs."""

import uuid

import pytest
from httpx import AsyncClient
from sqlalchemy import select
from sqlalchemy.ext.asyncio import AsyncSession

from app.models.enums import ChapterStatus
from app.models.ledger_event import LedgerEvent
from tests.factories import project_create_payload


async def _setup_project(client: AsyncClient, headers: dict[str, str]) -> tuple[str, str]:
    create_resp = await client.post("/projects", json=project_create_payload(), headers=headers)
    assert create_resp.status_code == 201
    project_id = create_resp.json()["id"]
    chapters_resp = await client.get(f"/projects/{project_id}/chapters", headers=headers)
    chapter_id = chapters_resp.json()["items"][0]["id"]
    return project_id, chapter_id


@pytest.mark.integration
async def test_create_and_list_characters_with_tier_filter(
    client: AsyncClient,
    user_a_headers: dict[str, str],
) -> None:
    project_id, _ = await _setup_project(client, user_a_headers)

    create_resp = await client.post(
        f"/projects/{project_id}/characters",
        json={
            "display_name": "Vân Thương",
            "role_one_liner": "Sư muội",
            "tier": 0,
        },
        headers=user_a_headers,
    )
    assert create_resp.status_code == 201
    assert create_resp.json()["status"] == "established"

    list_resp = await client.get(
        f"/projects/{project_id}/characters?tier=0",
        headers=user_a_headers,
    )
    assert list_resp.status_code == 200
    names = [item["display_name"] for item in list_resp.json()["items"]]
    assert "Vân Thương" in names


@pytest.mark.integration
async def test_patch_character_updates_aliases_preserves_id(
    client: AsyncClient,
    user_a_headers: dict[str, str],
) -> None:
    project_id, _ = await _setup_project(client, user_a_headers)
    chars_resp = await client.get(f"/projects/{project_id}/characters", headers=user_a_headers)
    char = next(c for c in chars_resp.json()["items"] if c["display_name"] == "Lý Phong")
    char_id = char["id"]

    patch_resp = await client.patch(
        f"/projects/{project_id}/characters/{char_id}",
        json={"aliases": ["Phong", "Lý đại ca"]},
        headers=user_a_headers,
    )
    assert patch_resp.status_code == 200
    body = patch_resp.json()
    assert body["id"] == char_id
    assert "Phong" in body["aliases"]


@pytest.mark.integration
async def test_promote_tier_rules(
    client: AsyncClient,
    user_a_headers: dict[str, str],
) -> None:
    project_id, _ = await _setup_project(client, user_a_headers)
    create_resp = await client.post(
        f"/projects/{project_id}/characters",
        json={"display_name": "Tier Test", "role_one_liner": "Seed", "tier": 0},
        headers=user_a_headers,
    )
    char_id = create_resp.json()["id"]

    t1_fail = await client.post(
        f"/projects/{project_id}/characters/{char_id}/promote-tier",
        headers=user_a_headers,
    )
    assert t1_fail.status_code == 422

    await client.patch(
        f"/projects/{project_id}/characters/{char_id}",
        json={"metadata": {"voice_hint": "trầm"}},
        headers=user_a_headers,
    )
    t1_ok = await client.post(
        f"/projects/{project_id}/characters/{char_id}/promote-tier",
        headers=user_a_headers,
    )
    assert t1_ok.status_code == 200
    assert t1_ok.json()["tier"] == 1

    await client.patch(
        f"/projects/{project_id}/characters/{char_id}",
        json={"psyche_card": {"traits": ["kiên định"]}},
        headers=user_a_headers,
    )
    t2_resp = await client.post(
        f"/projects/{project_id}/characters/{char_id}/promote-tier",
        headers=user_a_headers,
    )
    assert t2_resp.status_code == 200
    assert t2_resp.json()["tier"] == 2

    t3_fail = await client.post(
        f"/projects/{project_id}/characters/{char_id}/promote-tier",
        headers=user_a_headers,
    )
    assert t3_fail.status_code == 422

    await client.patch(
        f"/projects/{project_id}/characters/{char_id}",
        json={
            "psyche_card": {
                "traits": ["kiên định"],
                "moral_boundaries": ["không giết vô tội"],
            },
            "metadata": {"voice_hint": "trầm", "arc_note": "báo thù"},
        },
        headers=user_a_headers,
    )
    t3_ok = await client.post(
        f"/projects/{project_id}/characters/{char_id}/promote-tier",
        json={"confirm_t3": True},
        headers=user_a_headers,
    )
    assert t3_ok.status_code == 200
    assert t3_ok.json()["tier"] == 3


@pytest.mark.integration
async def test_extract_characters_creates_provisionals(
    client: AsyncClient,
    user_a_headers: dict[str, str],
) -> None:
    project_id, chapter_id = await _setup_project(client, user_a_headers)
    await client.post(
        f"/projects/{project_id}/chapters/{chapter_id}/prose-versions",
        json={"content": 'Lý Phong gặp @Hắc Y Nhân tại cổng. "Ma Vương" cười.'},
        headers=user_a_headers,
    )
    extract_resp = await client.post(
        f"/projects/{project_id}/chapters/{chapter_id}/extract-characters",
        json={"include_beats": False},
        headers=user_a_headers,
    )
    assert extract_resp.status_code == 200
    body = extract_resp.json()
    assert body["created_count"] >= 1
    mention_texts = [p["mention_text"] for p in body["provisionals"]]
    assert "Hắc Y Nhân" in mention_texts or "Ma Vương" in mention_texts


@pytest.mark.integration
async def test_extract_on_locked_chapter_409(
    client: AsyncClient,
    user_a_headers: dict[str, str],
    session: AsyncSession,
) -> None:
    project_id, chapter_id = await _setup_project(client, user_a_headers)
    from app.models.chapter import Chapter

    chapter = await session.scalar(select(Chapter).where(Chapter.id == uuid.UUID(chapter_id)))
    assert chapter is not None
    chapter.status = ChapterStatus.locked
    await session.commit()

    resp = await client.post(
        f"/projects/{project_id}/chapters/{chapter_id}/extract-characters",
        headers=user_a_headers,
    )
    assert resp.status_code == 409
    assert resp.json()["error"]["code"] == "chapter_locked"


@pytest.mark.integration
async def test_merge_provisional_into_existing_and_idempotency(
    client: AsyncClient,
    user_a_headers: dict[str, str],
) -> None:
    project_id, chapter_id = await _setup_project(client, user_a_headers)
    chars_resp = await client.get(f"/projects/{project_id}/characters", headers=user_a_headers)
    target = next(c for c in chars_resp.json()["items"] if c["display_name"] == "Lý Phong")

    await client.post(
        f"/projects/{project_id}/chapters/{chapter_id}/prose-versions",
        json={"content": "Xuất hiện Hắc Y Nhân bất ngờ."},
        headers=user_a_headers,
    )
    extract_resp = await client.post(
        f"/projects/{project_id}/chapters/{chapter_id}/extract-characters",
        json={"include_beats": False},
        headers=user_a_headers,
    )
    provisional = extract_resp.json()["provisionals"][0]
    prov_id = provisional["id"]

    merge_resp = await client.post(
        f"/projects/{project_id}/characters/provisionals/{prov_id}/merge",
        json={"target_character_id": target["id"]},
        headers=user_a_headers,
    )
    assert merge_resp.status_code == 200
    assert merge_resp.json()["idempotent"] is False
    assert merge_resp.json()["provisional"]["status"] == "merged"
    assert provisional["mention_text"] in merge_resp.json()["character"]["aliases"]

    retry_resp = await client.post(
        f"/projects/{project_id}/characters/provisionals/{prov_id}/merge",
        json={"target_character_id": target["id"]},
        headers=user_a_headers,
    )
    assert retry_resp.status_code == 200
    assert retry_resp.json()["idempotent"] is True


@pytest.mark.integration
async def test_merge_promote_new_character(
    client: AsyncClient,
    user_a_headers: dict[str, str],
) -> None:
    project_id, chapter_id = await _setup_project(client, user_a_headers)
    await client.post(
        f"/projects/{project_id}/chapters/{chapter_id}/prose-versions",
        json={"content": "Ma Vương xuất hiện."},
        headers=user_a_headers,
    )
    extract_resp = await client.post(
        f"/projects/{project_id}/chapters/{chapter_id}/extract-characters",
        json={"include_beats": False},
        headers=user_a_headers,
    )
    prov = next(p for p in extract_resp.json()["provisionals"] if p["mention_text"] == "Ma Vương")

    merge_resp = await client.post(
        f"/projects/{project_id}/characters/provisionals/{prov['id']}/merge",
        json={
            "create_new": True,
            "display_name": "Ma Vương",
            "initial_tier": 0,
            "mark_established": True,
        },
        headers=user_a_headers,
    )
    assert merge_resp.status_code == 200
    character = merge_resp.json()["character"]
    assert character["display_name"] == "Ma Vương"
    assert character["merged_from_provisional_id"] == prov["id"]


@pytest.mark.integration
async def test_reject_provisional_and_merge_after_reject_409(
    client: AsyncClient,
    user_a_headers: dict[str, str],
) -> None:
    project_id, chapter_id = await _setup_project(client, user_a_headers)
    await client.post(
        f"/projects/{project_id}/chapters/{chapter_id}/prose-versions",
        json={"content": "Thành phố Thanh Vân."},
        headers=user_a_headers,
    )
    extract_resp = await client.post(
        f"/projects/{project_id}/chapters/{chapter_id}/extract-characters",
        json={"include_beats": False},
        headers=user_a_headers,
    )
    prov = extract_resp.json()["provisionals"][0]

    reject_resp = await client.post(
        f"/projects/{project_id}/characters/provisionals/{prov['id']}/reject",
        json={"reason": "Địa danh"},
        headers=user_a_headers,
    )
    assert reject_resp.status_code == 200
    assert reject_resp.json()["status"] == "rejected"

    merge_resp = await client.post(
        f"/projects/{project_id}/characters/provisionals/{prov['id']}/merge",
        json={"create_new": True, "display_name": prov["mention_text"]},
        headers=user_a_headers,
    )
    assert merge_resp.status_code == 409


@pytest.mark.integration
async def test_cross_tenant_character_routes_404(
    client: AsyncClient,
    user_a_headers: dict[str, str],
    user_b_headers: dict[str, str],
) -> None:
    project_id, chapter_id = await _setup_project(client, user_a_headers)
    await client.post(
        f"/projects/{project_id}/chapters/{chapter_id}/prose-versions",
        json={"content": "Hắc Y Nhân xuất hiện."},
        headers=user_a_headers,
    )
    extract_resp = await client.post(
        f"/projects/{project_id}/chapters/{chapter_id}/extract-characters",
        headers=user_a_headers,
    )
    prov_id = extract_resp.json()["provisionals"][0]["id"]

    merge_resp = await client.post(
        f"/projects/{project_id}/characters/provisionals/{prov_id}/merge",
        json={"create_new": True, "display_name": "Blocked"},
        headers=user_b_headers,
    )
    assert merge_resp.status_code == 404

    extract_b = await client.post(
        f"/projects/{project_id}/chapters/{chapter_id}/extract-characters",
        headers=user_b_headers,
    )
    assert extract_b.status_code == 404

    search_b = await client.get(
        f"/projects/{project_id}/characters/search?q=Phong",
        headers=user_b_headers,
    )
    assert search_b.status_code == 404

    context_b = await client.post(
        f"/projects/{project_id}/context-packs/characters",
        json={"chapter_id": chapter_id},
        headers=user_b_headers,
    )
    assert context_b.status_code == 404


@pytest.mark.integration
async def test_search_matches_alias(
    client: AsyncClient,
    user_a_headers: dict[str, str],
) -> None:
    project_id, _ = await _setup_project(client, user_a_headers)
    chars_resp = await client.get(f"/projects/{project_id}/characters", headers=user_a_headers)
    char = next(c for c in chars_resp.json()["items"] if c["display_name"] == "Lý Phong")
    await client.patch(
        f"/projects/{project_id}/characters/{char['id']}",
        json={"aliases": ["Phong"]},
        headers=user_a_headers,
    )

    search_resp = await client.get(
        f"/projects/{project_id}/characters/search?q=Phong",
        headers=user_a_headers,
    )
    assert search_resp.status_code == 200
    assert search_resp.json()["search_mode"] == "keyword"
    assert len(search_resp.json()["items"]) >= 1


@pytest.mark.integration
async def test_context_pack_respects_max_stubs(
    client: AsyncClient,
    user_a_headers: dict[str, str],
) -> None:
    project_id, chapter_id = await _setup_project(client, user_a_headers)
    for idx in range(15):
        await client.post(
            f"/projects/{project_id}/characters",
            json={"display_name": f"Stub {idx}", "role_one_liner": "extra", "tier": 0},
            headers=user_a_headers,
        )

    pack_resp = await client.post(
        f"/projects/{project_id}/context-packs/characters",
        json={
            "chapter_id": chapter_id,
            "name_hints": [f"Stub {i}" for i in range(15)],
            "max_stubs": 3,
        },
        headers=user_a_headers,
    )
    assert pack_resp.status_code == 200
    body = pack_resp.json()
    stub_entries = [e for e in body["entries"] if e["character"]["tier"] <= 1]
    assert len(stub_entries) <= 3
    assert body["truncated"] is True


@pytest.mark.integration
async def test_no_ledger_events_on_provisional_ids(
    client: AsyncClient,
    user_a_headers: dict[str, str],
    session: AsyncSession,
) -> None:
    project_id, chapter_id = await _setup_project(client, user_a_headers)
    chars_resp = await client.get(f"/projects/{project_id}/characters", headers=user_a_headers)
    target = next(c for c in chars_resp.json()["items"] if c["display_name"] == "Lý Phong")

    await client.post(
        f"/projects/{project_id}/chapters/{chapter_id}/prose-versions",
        json={"content": "Hắc Y Nhân đến."},
        headers=user_a_headers,
    )
    extract_resp = await client.post(
        f"/projects/{project_id}/chapters/{chapter_id}/extract-characters",
        headers=user_a_headers,
    )
    prov_id = uuid.UUID(extract_resp.json()["provisionals"][0]["id"])

    await client.post(
        f"/projects/{project_id}/characters/provisionals/{prov_id}/merge",
        json={"target_character_id": target["id"]},
        headers=user_a_headers,
    )

    ledger_rows = await session.scalars(select(LedgerEvent))
    for event in ledger_rows.all():
        assert event.entity_id != prov_id


@pytest.mark.integration
async def test_list_provisionals_and_get_detail(
    client: AsyncClient,
    user_a_headers: dict[str, str],
) -> None:
    project_id, chapter_id = await _setup_project(client, user_a_headers)
    await client.post(
        f"/projects/{project_id}/chapters/{chapter_id}/prose-versions",
        json={"content": "Hắc Y Nhân xuất hiện."},
        headers=user_a_headers,
    )
    await client.post(
        f"/projects/{project_id}/chapters/{chapter_id}/extract-characters",
        headers=user_a_headers,
    )

    list_resp = await client.get(
        f"/projects/{project_id}/characters/provisionals",
        headers=user_a_headers,
    )
    assert list_resp.status_code == 200
    body = list_resp.json()
    assert body["pending_count"] >= 1
    prov_id = body["items"][0]["id"]

    detail_resp = await client.get(
        f"/projects/{project_id}/characters/provisionals/{prov_id}",
        headers=user_a_headers,
    )
    assert detail_resp.status_code == 200
    assert detail_resp.json()["chapter_number"] == 1


@pytest.mark.integration
async def test_search_vector_mode_501(
    client: AsyncClient,
    user_a_headers: dict[str, str],
) -> None:
    project_id, _ = await _setup_project(client, user_a_headers)
    resp = await client.get(
        f"/projects/{project_id}/characters/search?q=Phong&search_mode=vector",
        headers=user_a_headers,
    )
    assert resp.status_code == 501


@pytest.mark.integration
async def test_duplicate_display_name_on_create_409(
    client: AsyncClient,
    user_a_headers: dict[str, str],
) -> None:
    project_id, _ = await _setup_project(client, user_a_headers)
    resp = await client.post(
        f"/projects/{project_id}/characters",
        json={"display_name": "Lý Phong", "role_one_liner": "dup"},
        headers=user_a_headers,
    )
    assert resp.status_code == 409
    assert resp.json()["error"]["code"] == "duplicate_display_name"
