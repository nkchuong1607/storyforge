"""Extended Phase 6 unit tests for coverage."""

import uuid
from datetime import UTC, datetime
from unittest.mock import AsyncMock, MagicMock, patch

import pytest

from app.exceptions import (
    InvalidGenreRulePackError,
    LLMProviderError,
    PromptEditAlreadyAppliedError,
)
from app.models.chapter import Chapter
from app.models.enums import ChapterStatus, GenreProfile, ProseSource
from app.models.power_system import PowerRank, PowerSystemSettings, PowerTechnique
from app.models.project import Project
from app.models.prompt_edit import PromptEditSession, PromptEditTurn
from app.models.prose_version import ProseVersion
from app.schemas.power import (
    PowerRankCreateRequest,
    PowerRankUpdateRequest,
    PowerTechniqueCreateRequest,
    PowerTechniqueUpdateRequest,
)
from app.schemas.prompt_edit import PromptEditApplyRequest, PromptEditRegenerateRequest
from app.services.continuity.power import (
    build_power_snapshot,
    is_power_module_enabled,
    ranks_to_context,
    techniques_to_context,
)
from app.services.genre import GenreService
from app.services.genre_defaults import validate_genre_pack
from app.services.llm import provider as llm_provider
from app.services.power import PowerService
from app.services.prompt_edit import PromptEditService


def _project() -> Project:
    project = Project(
        slug="p",
        title="P",
        genre_profile=GenreProfile.xianxia,
        created_by=uuid.uuid4(),
    )
    project.id = uuid.uuid4()
    project.genre_rule_pack_json = {}
    project.updated_at = datetime.now(tz=UTC)
    return project


def _settings(project_id: uuid.UUID, *, enabled: bool = True) -> PowerSystemSettings:
    return PowerSystemSettings(
        project_id=project_id,
        enabled=enabled,
        priority_gap=2,
        max_rank_jump_per_chapter=1,
        require_breakthrough_event=True,
        updated_at=datetime.now(tz=UTC),
    )


@pytest.mark.unit
async def test_power_create_update_technique() -> None:
    session = AsyncMock()
    service = PowerService(session)
    project = _project()
    rank = PowerRank(project_id=project.id, rank_key="qi", display_name="Luyện Khí", sort_order=0)
    rank.id = uuid.uuid4()
    technique = PowerTechnique(
        project_id=project.id,
        technique_key="sword",
        display_name="Kiếm",
        min_rank_id=rank.id,
    )
    technique.id = uuid.uuid4()
    service.power.ensure_settings = AsyncMock(return_value=_settings(project.id))
    service.power.max_sort_order = AsyncMock(return_value=-1)
    service.power.create_rank = AsyncMock(return_value=rank)
    service.power.get_rank = AsyncMock(return_value=rank)
    service.power.create_technique = AsyncMock(return_value=technique)
    service.power.list_ranks = AsyncMock(return_value=[rank])
    service.power.get_technique = AsyncMock(return_value=technique)
    service.power.list_techniques = AsyncMock(return_value=[technique])
    session.refresh = AsyncMock()
    session.flush = AsyncMock()

    created_rank = await service.create_rank(
        project, PowerRankCreateRequest(rank_key="qi", display_name="Luyện Khí")
    )
    assert created_rank.rank_key == "qi"

    updated = await service.update_rank(
        project, rank.id, PowerRankUpdateRequest(display_name="Luyện Khí cảnh")
    )
    assert updated.display_name == "Luyện Khí cảnh"

    tech = await service.create_technique(
        project,
        PowerTechniqueCreateRequest(
            technique_key="sword", display_name="Kiếm", min_rank_id=rank.id
        ),
    )
    assert tech.technique_key == "sword"

    updated_tech = await service.update_technique(
        project, technique.id, PowerTechniqueUpdateRequest(display_name="Đại Kiếm")
    )
    assert updated_tech.display_name == "Đại Kiếm"


@pytest.mark.unit
async def test_power_delete_technique() -> None:
    session = AsyncMock()
    service = PowerService(session)
    project = _project()
    technique = PowerTechnique(
        project_id=project.id,
        technique_key="s",
        display_name="S",
        min_rank_id=uuid.uuid4(),
    )
    technique.id = uuid.uuid4()
    service.power.ensure_settings = AsyncMock(return_value=_settings(project.id))
    service.power.get_technique = AsyncMock(return_value=technique)
    service.power.delete_technique = AsyncMock()
    await service.delete_technique(project, technique.id)
    service.power.delete_technique.assert_awaited_once()


@pytest.mark.unit
async def test_prompt_edit_apply_and_regenerate() -> None:
    session = AsyncMock()
    service = PromptEditService(session)
    project = _project()
    chapter = Chapter(project_id=project.id, number=1, title="Ch1", status=ChapterStatus.drafting)
    chapter.id = uuid.uuid4()
    session_row = PromptEditSession(
        project_id=project.id,
        chapter_id=chapter.id,
        base_prose_version=1,
        status="active",
        created_by=uuid.uuid4(),
    )
    session_row.id = uuid.uuid4()
    turn = PromptEditTurn(
        project_id=project.id,
        session_id=session_row.id,
        turn_index=1,
        instruction="edit",
        proposed_content="Revised.",
        model="fake-llm",
        provider="fake",
    )
    turn.id = uuid.uuid4()
    turn.created_at = datetime.now(tz=UTC)
    prose = ProseVersion(
        project_id=project.id,
        chapter_id=chapter.id,
        version=1,
        content="Original.",
        word_count=1,
        source=ProseSource.human,
        created_by=uuid.uuid4(),
    )
    created_prose = ProseVersion(
        project_id=project.id,
        chapter_id=chapter.id,
        version=2,
        content="Revised.",
        word_count=1,
        source=ProseSource.ai_editor,
        created_by=uuid.uuid4(),
        prompt_edit_turn_id=turn.id,
    )
    created_prose.created_at = datetime.now(tz=UTC)

    service.prompt_edit.get_session = AsyncMock(return_value=session_row)
    service.prompt_edit.get_turn = AsyncMock(return_value=turn)
    service.prompt_edit.prose_version_exists_for_turn = AsyncMock(return_value=False)
    service.prose.get_max_version = AsyncMock(return_value=1)
    service.prose.create = AsyncMock(return_value=created_prose)
    service.prose.get_version = AsyncMock(return_value=prose)
    service.prompt_edit.max_turn_index = AsyncMock(return_value=1)
    service.prompt_edit.create_turn = AsyncMock(
        side_effect=lambda t: (
            setattr(t, "id", uuid.uuid4()) or setattr(t, "created_at", datetime.now(tz=UTC)) or t
        )
    )
    session.refresh = AsyncMock()
    session.flush = AsyncMock()

    with patch(
        "app.services.prompt_edit.complete_prose_edit",
        AsyncMock(
            return_value=MagicMock(
                content="Revised again.",
                model="fake-llm",
                provider="fake",
                latency_ms=1,
                token_usage={},
            )
        ),
    ):
        apply_result = await service.apply(
            project,
            chapter,
            uuid.uuid4(),
            PromptEditApplyRequest(session_id=session_row.id, turn_id=turn.id),
        )
        assert apply_result.prose_version.source == "ai_editor"

        service.prompt_edit.prose_version_exists_for_turn = AsyncMock(return_value=True)
        with pytest.raises(PromptEditAlreadyAppliedError):
            await service.apply(
                project,
                chapter,
                uuid.uuid4(),
                PromptEditApplyRequest(session_id=session_row.id, turn_id=turn.id),
            )

        regen = await service.regenerate(
            project,
            chapter,
            uuid.uuid4(),
            PromptEditRegenerateRequest(session_id=session_row.id, turn_id=turn.id),
        )
        assert regen.turn.turn_index == 2


@pytest.mark.unit
async def test_prompt_edit_list_sessions() -> None:
    session = AsyncMock()
    service = PromptEditService(session)
    project = _project()
    chapter = Chapter(project_id=project.id, number=1, title="Ch1", status=ChapterStatus.drafting)
    chapter.id = uuid.uuid4()
    session_row = PromptEditSession(
        project_id=project.id,
        chapter_id=chapter.id,
        base_prose_version=1,
        status="active",
        created_by=uuid.uuid4(),
    )
    session_row.id = uuid.uuid4()
    session_row.created_at = datetime.now(tz=UTC)
    turn = PromptEditTurn(
        project_id=project.id,
        session_id=session_row.id,
        turn_index=1,
        instruction="x",
        proposed_content="y",
        model="fake-llm",
        provider="fake",
        token_usage={},
    )
    turn.id = uuid.uuid4()
    turn.created_at = datetime.now(tz=UTC)
    service.prompt_edit.list_sessions_for_chapter = AsyncMock(return_value=[session_row])
    service.prompt_edit.list_turns_for_session = AsyncMock(return_value=[turn])
    result = await service.list_sessions(project, chapter)
    assert len(result.items) == 1


@pytest.mark.unit
def test_power_snapshot_helpers() -> None:
    rank = PowerRank(project_id=uuid.uuid4(), rank_key="qi", display_name="Luyện Khí", sort_order=0)
    rank.id = uuid.uuid4()
    ctx = ranks_to_context([rank])
    assert ctx[0].display_name == "Luyện Khí"
    tech = PowerTechnique(
        project_id=rank.project_id,
        technique_key="s",
        display_name="S",
        min_rank_id=rank.id,
    )
    tech.id = uuid.uuid4()
    tech_ctx = techniques_to_context([tech], [rank])
    assert tech_ctx[0].min_rank_sort_order == 0
    snap = build_power_snapshot(_settings(rank.project_id), [rank], [tech])
    assert snap["enabled"] is True
    assert len(snap["ranks"]) == 1


@pytest.mark.unit
def test_is_power_module_enabled_requires_both() -> None:
    settings = _settings(uuid.uuid4(), enabled=False)
    pack = {"modules": {"power_system": {"enabled": True}}}
    assert is_power_module_enabled(settings, pack) is False


@pytest.mark.unit
def test_genre_invalid_pack_raises() -> None:
    with pytest.raises(ValueError):
        validate_genre_pack({"schema_version": "bad"})


@pytest.mark.unit
async def test_genre_invalid_pack_service() -> None:
    session = AsyncMock()
    service = GenreService(session)
    project = _project()
    from app.schemas.genre import GenreRulePackPatch

    with pytest.raises(InvalidGenreRulePackError):
        await service.patch_pack(project, GenreRulePackPatch(pack={"schema_version": "x"}))


@pytest.mark.unit
async def test_power_reorder_success() -> None:
    session = AsyncMock()
    service = PowerService(session)
    project = _project()
    ranks = []
    for idx, key in enumerate(["qi", "foundation", "core"]):
        rank = PowerRank(
            project_id=project.id,
            rank_key=key,
            display_name=key,
            sort_order=idx,
        )
        rank.id = uuid.uuid4()
        ranks.append(rank)
    service.power.ensure_settings = AsyncMock(return_value=_settings(project.id))
    service.power.list_ranks = AsyncMock(return_value=ranks)
    session.flush = AsyncMock()
    from app.schemas.power import PowerRankReorderRequest

    result = await service.reorder_ranks(
        project, PowerRankReorderRequest(rank_ids=[r.id for r in reversed(ranks)])
    )
    assert len(result.items) == 3


@pytest.mark.unit
async def test_power_get_settings_without_enable_check() -> None:
    session = AsyncMock()
    service = PowerService(session)
    project = _project()
    service.power.ensure_settings = AsyncMock(return_value=_settings(project.id, enabled=False))
    result = await service.get_settings(project)
    assert result.enabled is False


@pytest.mark.unit
async def test_prompt_edit_locked_chapter() -> None:
    session = AsyncMock()
    service = PromptEditService(session)
    chapter = Chapter(project_id=uuid.uuid4(), number=1, title="Ch1", status=ChapterStatus.locked)
    chapter.id = uuid.uuid4()
    from app.exceptions import ChapterLockedError

    with pytest.raises(ChapterLockedError):
        await service.instruct(
            _project(),
            chapter,
            uuid.uuid4(),
            __import__(
                "app.schemas.prompt_edit", fromlist=["PromptEditInstructRequest"]
            ).PromptEditInstructRequest(instruction="x"),
        )


@pytest.mark.unit
async def test_power_list_ranks_and_techniques() -> None:
    session = AsyncMock()
    service = PowerService(session)
    project = _project()
    rank = PowerRank(project_id=project.id, rank_key="qi", display_name="Luyện Khí", sort_order=0)
    rank.id = uuid.uuid4()
    service.power.ensure_settings = AsyncMock(return_value=_settings(project.id))
    service.power.list_ranks = AsyncMock(return_value=[rank])
    service.power.list_techniques = AsyncMock(return_value=[])
    ranks = await service.list_ranks(project)
    assert len(ranks.items) == 1
    techs = await service.list_techniques(project)
    assert techs.items == []


@pytest.mark.unit
async def test_power_delete_rank_success() -> None:
    session = AsyncMock()
    service = PowerService(session)
    project = _project()
    rank = PowerRank(project_id=project.id, rank_key="qi", display_name="Luyện Khí", sort_order=0)
    rank.id = uuid.uuid4()
    service.power.ensure_settings = AsyncMock(return_value=_settings(project.id))
    service.power.get_rank = AsyncMock(return_value=rank)
    service.power.count_techniques_for_rank = AsyncMock(return_value=0)
    service.power.delete_rank = AsyncMock()
    await service.delete_rank(project, rank.id)
    service.power.delete_rank.assert_awaited_once()


@pytest.mark.unit
async def test_genre_reset_requires_confirm() -> None:
    session = AsyncMock()
    service = GenreService(session)
    project = _project()
    from app.exceptions import ValidationAppError

    with pytest.raises(ValidationAppError):
        await service.reset_pack(project, confirm=False)


@pytest.mark.unit
async def test_litellm_provider_missing_model() -> None:
    with patch.object(llm_provider, "get_settings") as mock_settings:
        mock_settings.return_value = MagicMock(
            llm_provider="litellm", litellm_model=None, litellm_api_base=None
        )
        with pytest.raises(LLMProviderError):
            await llm_provider.complete_prose_edit(prose="x", instruction="y")
