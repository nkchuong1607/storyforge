"""Power, genre, and prompt-edit service unit tests."""

import uuid
from datetime import UTC, datetime
from unittest.mock import AsyncMock

import pytest

from app.exceptions import InvalidRankLadderError, PowerSystemDisabledError, RankInUseError
from app.models.chapter import Chapter
from app.models.enums import ChapterStatus, GenreProfile, ProseSource
from app.models.power_system import PowerRank, PowerSystemSettings
from app.models.project import Project
from app.models.prose_version import ProseVersion
from app.schemas.genre import GenreRulePackPatch
from app.schemas.power import (
    PowerRankCreateRequest,
    PowerRankReorderRequest,
    PowerSystemSettingsUpdate,
)
from app.schemas.prompt_edit import PromptEditInstructRequest
from app.services.genre import GenreService
from app.services.power import PowerService
from app.services.prompt_edit import PromptEditService


def _project(**kwargs) -> Project:
    project = Project(
        slug="p",
        title="P",
        genre_profile=GenreProfile.xianxia,
        created_by=uuid.uuid4(),
    )
    project.id = kwargs.get("id", uuid.uuid4())
    project.genre_rule_pack_json = kwargs.get("genre_rule_pack_json", {})
    project.updated_at = datetime.now(tz=UTC)
    return project


@pytest.mark.unit
async def test_power_settings_update() -> None:
    session = AsyncMock()
    service = PowerService(session)
    project = _project()
    settings = PowerSystemSettings(
        project_id=project.id,
        enabled=False,
        priority_gap=2,
        max_rank_jump_per_chapter=1,
        require_breakthrough_event=True,
    )
    service.power.ensure_settings = AsyncMock(return_value=settings)
    session.flush = AsyncMock()
    session.refresh = AsyncMock()

    result = await service.update_settings(
        project, PowerSystemSettingsUpdate(enabled=True, priority_gap=3)
    )
    assert result.enabled is True
    assert result.priority_gap == 3


@pytest.mark.unit
async def test_create_rank_when_disabled_raises() -> None:
    session = AsyncMock()
    service = PowerService(session)
    project = _project()
    service.power.ensure_settings = AsyncMock(
        return_value=PowerSystemSettings(project_id=project.id, enabled=False)
    )
    with pytest.raises(PowerSystemDisabledError):
        await service.create_rank(
            project, PowerRankCreateRequest(rank_key="qi", display_name="Luyện Khí")
        )


@pytest.mark.unit
async def test_reorder_invalid_permutation() -> None:
    session = AsyncMock()
    service = PowerService(session)
    project = _project()
    rank = PowerRank(
        project_id=project.id,
        rank_key="qi",
        display_name="Luyện Khí",
        sort_order=0,
    )
    rank.id = uuid.uuid4()
    service.power.ensure_settings = AsyncMock(
        return_value=PowerSystemSettings(project_id=project.id, enabled=True)
    )
    service.power.list_ranks = AsyncMock(return_value=[rank])
    with pytest.raises(InvalidRankLadderError):
        await service.reorder_ranks(project, PowerRankReorderRequest(rank_ids=[uuid.uuid4()]))


@pytest.mark.unit
async def test_delete_rank_in_use() -> None:
    session = AsyncMock()
    service = PowerService(session)
    project = _project()
    rank = PowerRank(project_id=project.id, rank_key="qi", display_name="Luyện Khí", sort_order=0)
    rank.id = uuid.uuid4()
    service.power.ensure_settings = AsyncMock(
        return_value=PowerSystemSettings(project_id=project.id, enabled=True)
    )
    service.power.get_rank = AsyncMock(return_value=rank)
    service.power.count_techniques_for_rank = AsyncMock(return_value=1)
    with pytest.raises(RankInUseError):
        await service.delete_rank(project, rank.id)


@pytest.mark.unit
async def test_genre_patch_and_reset() -> None:
    session = AsyncMock()
    service = GenreService(session)
    project = _project()
    session.flush = AsyncMock()
    session.refresh = AsyncMock()

    patched = await service.patch_pack(
        project, GenreRulePackPatch(pack={"promises": ["Test promise"]})
    )
    assert "Test promise" in patched.pack["promises"]

    reset = await service.reset_pack(project, confirm=True)
    assert reset.pack["schema_version"] == 1


@pytest.mark.unit
async def test_prompt_edit_instruct(monkeypatch: pytest.MonkeyPatch) -> None:
    session = AsyncMock()
    service = PromptEditService(session)
    project = _project()
    chapter = Chapter(project_id=project.id, number=1, title="Ch1", status=ChapterStatus.drafting)
    chapter.id = uuid.uuid4()
    prose = ProseVersion(
        project_id=project.id,
        chapter_id=chapter.id,
        version=1,
        content="Original prose.",
        word_count=2,
        source=ProseSource.human,
        created_by=uuid.uuid4(),
    )
    service.prose.get_latest = AsyncMock(return_value=prose)
    service.prompt_edit.create_session = AsyncMock(
        side_effect=lambda s: setattr(s, "id", uuid.uuid4()) or s
    )
    service.prompt_edit.create_turn = AsyncMock(
        side_effect=lambda t: (
            setattr(t, "id", uuid.uuid4()) or setattr(t, "created_at", datetime.now(tz=UTC)) or t
        )
    )
    session.refresh = AsyncMock()

    from app.services.llm import fake_llm

    monkeypatch.setattr(
        fake_llm,
        "fake_complete",
        lambda **_: fake_llm.LLMCompletionResult(
            content="Edited prose.\n\n[AI_EDIT: abc]",
            model="fake-llm",
            provider="fake",
            latency_ms=5,
            token_usage={"prompt_tokens": 10, "completion_tokens": 20},
        ),
    )
    monkeypatch.setattr(
        "app.services.prompt_edit.complete_prose_edit",
        AsyncMock(
            return_value=fake_llm.LLMCompletionResult(
                content="Edited prose.\n\n[AI_EDIT: abc]",
                model="fake-llm",
                provider="fake",
                latency_ms=5,
                token_usage={"prompt_tokens": 10, "completion_tokens": 20},
            )
        ),
    )

    result = await service.instruct(
        project,
        chapter,
        uuid.uuid4(),
        PromptEditInstructRequest(instruction="Tăng tension"),
    )
    assert result.turn.provider == "fake"
    assert result.base_prose_version == 1
