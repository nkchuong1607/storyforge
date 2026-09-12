"""Phase 2 integration tests."""

import uuid

import pytest
from httpx import AsyncClient
from sqlalchemy import select
from sqlalchemy.ext.asyncio import AsyncSession

from app.models.bible import BibleVersion
from app.models.chapter import Chapter
from app.models.enums import ChapterStatus
from app.models.ledger_event import LedgerEvent
from app.models.project import Project
from tests.factories import project_create_payload


async def _setup_chapter(client: AsyncClient, headers: dict[str, str]) -> tuple[str, str]:
    create_resp = await client.post("/projects", json=project_create_payload(), headers=headers)
    assert create_resp.status_code == 201
    project_id = create_resp.json()["id"]
    chapters_resp = await client.get(f"/projects/{project_id}/chapters", headers=headers)
    chapter_id = chapters_resp.json()["items"][0]["id"]
    return project_id, chapter_id


@pytest.mark.integration
async def test_prose_version_updates_word_count(
    client: AsyncClient,
    user_a_headers: dict[str, str],
) -> None:
    project_id, chapter_id = await _setup_chapter(client, user_a_headers)
    prose_resp = await client.post(
        f"/projects/{project_id}/chapters/{chapter_id}/prose-versions",
        json={"content": "Hàn Lập đứng trên vách núi nhìn xuống thung lũng."},
        headers=user_a_headers,
    )
    assert prose_resp.status_code == 201
    assert prose_resp.json()["version"] == 1
    assert prose_resp.json()["word_count"] > 0

    chapter_resp = await client.get(
        f"/projects/{project_id}/chapters/{chapter_id}", headers=user_a_headers
    )
    body = chapter_resp.json()
    assert body["word_count"] == prose_resp.json()["word_count"]
    assert body["current_prose_version"] == 1
    assert body["status"] == "drafting"
    assert body["bible_version_at_draft"] == 0


@pytest.mark.integration
async def test_beats_crud_locked_chapter_409(
    client: AsyncClient,
    user_a_headers: dict[str, str],
    session: AsyncSession,
) -> None:
    project_id, chapter_id = await _setup_chapter(client, user_a_headers)

    create_beat = await client.post(
        f"/projects/{project_id}/chapters/{chapter_id}/beats",
        json={"beat_key": "1.1", "summary": "Mở đầu", "sort_order": 1},
        headers=user_a_headers,
    )
    assert create_beat.status_code == 201

    chapter = await session.scalar(select(Chapter).where(Chapter.id == uuid.UUID(chapter_id)))
    assert chapter is not None
    chapter.status = ChapterStatus.locked
    await session.commit()

    locked_resp = await client.post(
        f"/projects/{project_id}/chapters/{chapter_id}/beats",
        json={"beat_key": "1.2", "summary": "Blocked", "sort_order": 2},
        headers=user_a_headers,
    )
    assert locked_resp.status_code == 409
    assert locked_resp.json()["error"]["code"] == "chapter_locked"


@pytest.mark.integration
async def test_continuity_check_sets_reviewing(
    client: AsyncClient,
    user_a_headers: dict[str, str],
) -> None:
    project_id, chapter_id = await _setup_chapter(client, user_a_headers)
    await client.post(
        f"/projects/{project_id}/chapters/{chapter_id}/prose-versions",
        json={"content": "Lý Phong tu luyện trên núi."},
        headers=user_a_headers,
    )
    check_resp = await client.post(
        f"/projects/{project_id}/chapters/{chapter_id}/continuity-check",
        headers=user_a_headers,
    )
    assert check_resp.status_code == 200
    assert "report_id" in check_resp.json()

    chapter_resp = await client.get(
        f"/projects/{project_id}/chapters/{chapter_id}", headers=user_a_headers
    )
    assert chapter_resp.json()["status"] == "reviewing"


@pytest.mark.integration
async def test_fail_blocks_settle(
    client: AsyncClient,
    user_a_headers: dict[str, str],
    session: AsyncSession,
) -> None:
    project_id, chapter_id = await _setup_chapter(client, user_a_headers)

    characters_resp = await client.get(f"/projects/{project_id}/characters", headers=user_a_headers)
    char_id = next(
        c["id"] for c in characters_resp.json()["items"] if c["display_name"] == "Lý Phong"
    )

    await client.post(
        f"/projects/{project_id}/chapters/{chapter_id}/prose-versions",
        json={"content": "Lý Phong nói với sư phụ về con đường tu luyện."},
        headers=user_a_headers,
    )

    from datetime import UTC, datetime

    from app.models.enums import LedgerEntityType, LedgerEventType

    chapter = await session.scalar(select(Chapter).where(Chapter.id == uuid.UUID(chapter_id)))
    project = await session.scalar(select(Project).where(Project.id == uuid.UUID(project_id)))
    assert chapter and project
    session.add(
        LedgerEvent(
            project_id=project.id,
            entity_type=LedgerEntityType.character,
            entity_id=uuid.UUID(char_id),
            event_type=LedgerEventType.status_change,
            payload={"from": "alive", "to": "deceased"},
            chapter_id=chapter.id,
            chapter_number=1,
            prose_version=1,
            settled_at=datetime.now(UTC),
        )
    )
    chapter.status = ChapterStatus.drafting
    await session.commit()

    check_resp = await client.post(
        f"/projects/{project_id}/chapters/{chapter_id}/continuity-check",
        headers=user_a_headers,
    )
    assert check_resp.status_code == 200
    assert check_resp.json()["result"] == "fail"

    settle_resp = await client.post(
        f"/projects/{project_id}/chapters/{chapter_id}/settle",
        headers={**user_a_headers, "Idempotency-Key": str(uuid.uuid4())},
    )
    assert settle_resp.status_code == 409
    assert settle_resp.json()["error"]["code"] == "continuity_fail_blocks_settle"


@pytest.mark.integration
async def test_override_allows_settle(
    client: AsyncClient,
    user_a_headers: dict[str, str],
    session: AsyncSession,
) -> None:
    project_id, chapter_id = await _setup_chapter(client, user_a_headers)
    characters_resp = await client.get(f"/projects/{project_id}/characters", headers=user_a_headers)
    char_id = next(
        c["id"] for c in characters_resp.json()["items"] if c["display_name"] == "Lý Phong"
    )

    await client.post(
        f"/projects/{project_id}/chapters/{chapter_id}/prose-versions",
        json={"content": "Lý Phong nói với sư phụ."},
        headers=user_a_headers,
    )

    from datetime import UTC, datetime

    from app.models.enums import LedgerEntityType, LedgerEventType

    chapter = await session.scalar(select(Chapter).where(Chapter.id == uuid.UUID(chapter_id)))
    project = await session.scalar(select(Project).where(Project.id == uuid.UUID(project_id)))
    assert chapter and project
    session.add(
        LedgerEvent(
            project_id=project.id,
            entity_type=LedgerEntityType.character,
            entity_id=uuid.UUID(char_id),
            event_type=LedgerEventType.status_change,
            payload={"from": "alive", "to": "deceased"},
            chapter_id=chapter.id,
            chapter_number=1,
            prose_version=1,
            settled_at=datetime.now(UTC),
        )
    )
    await session.commit()

    check_resp = await client.post(
        f"/projects/{project_id}/chapters/{chapter_id}/continuity-check",
        headers=user_a_headers,
    )
    report = check_resp.json()
    fail_issue = next(i for i in report["issues"] if i["severity"] == "fail")

    override_resp = await client.post(
        f"/projects/{project_id}/chapters/{chapter_id}/continuity-overrides",
        json={
            "issue_fingerprint": fail_issue["fingerprint"],
            "reason": "Nhân vật chỉ xuất hiện trong hồi tưởng — cố ý",
        },
        headers=user_a_headers,
    )
    assert override_resp.status_code == 201

    settle_resp = await client.post(
        f"/projects/{project_id}/chapters/{chapter_id}/settle",
        headers={**user_a_headers, "Idempotency-Key": str(uuid.uuid4())},
    )
    assert settle_resp.status_code == 200
    assert settle_resp.json()["status"] == "locked"
    assert settle_resp.json()["bible_version_after"] == 1


@pytest.mark.integration
async def test_successful_settle_bumps_bible_and_locks(
    client: AsyncClient,
    user_a_headers: dict[str, str],
    session: AsyncSession,
) -> None:
    project_id, chapter_id = await _setup_chapter(client, user_a_headers)
    await client.post(
        f"/projects/{project_id}/chapters/{chapter_id}/prose-versions",
        json={"content": "Diệp Vân tu luyện yên bình."},
        headers=user_a_headers,
    )
    await client.post(
        f"/projects/{project_id}/chapters/{chapter_id}/continuity-check",
        headers=user_a_headers,
    )
    settle_resp = await client.post(
        f"/projects/{project_id}/chapters/{chapter_id}/settle",
        headers={**user_a_headers, "Idempotency-Key": str(uuid.uuid4())},
    )
    assert settle_resp.status_code == 200
    body = settle_resp.json()
    assert body["bible_version_before"] == 0
    assert body["bible_version_after"] == 1

    version = await session.scalar(
        select(BibleVersion).where(
            BibleVersion.project_id == uuid.UUID(project_id),
            BibleVersion.version == 1,
        )
    )
    assert version is not None
    assert version.settled_from_chapter_id == uuid.UUID(chapter_id)

    chapter_resp = await client.get(
        f"/projects/{project_id}/chapters/{chapter_id}", headers=user_a_headers
    )
    assert chapter_resp.json()["status"] == "locked"
    assert chapter_resp.json()["settled_at"] is not None


@pytest.mark.integration
async def test_cross_tenant_chapter_settle_denied(
    client: AsyncClient,
    user_a_headers: dict[str, str],
    user_b_headers: dict[str, str],
) -> None:
    project_id, chapter_id = await _setup_chapter(client, user_b_headers)
    response = await client.post(
        f"/projects/{project_id}/chapters/{chapter_id}/settle",
        headers={**user_a_headers, "Idempotency-Key": str(uuid.uuid4())},
    )
    assert response.status_code == 404


@pytest.mark.integration
async def test_locked_chapter_prose_post_409(
    client: AsyncClient,
    user_a_headers: dict[str, str],
    session: AsyncSession,
) -> None:
    project_id, chapter_id = await _setup_chapter(client, user_a_headers)
    chapter = await session.scalar(select(Chapter).where(Chapter.id == uuid.UUID(chapter_id)))
    assert chapter is not None
    chapter.status = ChapterStatus.locked
    await session.commit()

    response = await client.post(
        f"/projects/{project_id}/chapters/{chapter_id}/prose-versions",
        json={"content": "Should fail"},
        headers=user_a_headers,
    )
    assert response.status_code == 409
    assert response.json()["error"]["code"] == "chapter_locked"


@pytest.mark.integration
async def test_settle_idempotency(
    client: AsyncClient,
    user_a_headers: dict[str, str],
) -> None:
    project_id, chapter_id = await _setup_chapter(client, user_a_headers)
    await client.post(
        f"/projects/{project_id}/chapters/{chapter_id}/prose-versions",
        json={"content": "Diệp Vân tu luyện."},
        headers=user_a_headers,
    )
    await client.post(
        f"/projects/{project_id}/chapters/{chapter_id}/continuity-check",
        headers=user_a_headers,
    )
    key = str(uuid.uuid4())
    headers = {**user_a_headers, "Idempotency-Key": key}
    first = await client.post(
        f"/projects/{project_id}/chapters/{chapter_id}/settle",
        headers=headers,
    )
    assert first.status_code == 200
    second = await client.post(
        f"/projects/{project_id}/chapters/{chapter_id}/settle",
        headers=headers,
    )
    assert second.status_code == 200
    assert second.json() == first.json()


@pytest.mark.integration
async def test_settle_rollback_on_bible_insert_failure(
    client: AsyncClient,
    user_a_headers: dict[str, str],
    session: AsyncSession,
    monkeypatch: pytest.MonkeyPatch,
) -> None:
    project_id, chapter_id = await _setup_chapter(client, user_a_headers)
    await client.post(
        f"/projects/{project_id}/chapters/{chapter_id}/prose-versions",
        json={"content": "Diệp Vân tu luyện."},
        headers=user_a_headers,
    )
    await client.post(
        f"/projects/{project_id}/chapters/{chapter_id}/continuity-check",
        headers=user_a_headers,
    )

    async def _raise(*_args, **_kwargs):
        raise RuntimeError("Simulated bible insert failure")

    monkeypatch.setattr("app.services.settle.insert_bible_version", _raise)

    project = await session.scalar(select(Project).where(Project.id == uuid.UUID(project_id)))
    assert project is not None
    before_version = project.bible_version_current

    response = await client.post(
        f"/projects/{project_id}/chapters/{chapter_id}/settle",
        headers={**user_a_headers, "Idempotency-Key": str(uuid.uuid4())},
    )
    assert response.status_code >= 500

    await session.refresh(project)
    assert project.bible_version_current == before_version

    ledger_count = await session.scalar(
        select(LedgerEvent).where(LedgerEvent.chapter_id == uuid.UUID(chapter_id))
    )
    assert ledger_count is None
