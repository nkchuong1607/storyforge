"""Phase 3 service unit tests with mocked repositories."""

import uuid
from datetime import UTC, datetime
from unittest.mock import AsyncMock, MagicMock

import pytest

from app.exceptions import (
    AlreadyMaxTierError,
    CharacterArchivedError,
    DuplicateDisplayNameError,
    InvalidMergeRequestError,
    NotFoundError,
    NotImplementedFeatureError,
    ProvisionalAlreadyResolvedError,
    TierRequirementsNotMetError,
)
from app.models.chapter import Chapter
from app.models.character import Character
from app.models.character_provisional import CharacterProvisional
from app.models.enums import (
    ChapterStatus,
    CharacterStatus,
    ExtractorSource,
    ProvisionalStatus,
)
from app.models.project import Project
from app.models.prose_version import ProseVersion
from app.models.scene_beat import SceneBeat
from app.repositories.character import CharacterRepository
from app.repositories.provisional import ProvisionalRepository
from app.schemas.character import (
    CharacterContextPackRequest,
    CharacterCreateRequest,
    CharacterProvisionalMergeRequest,
    CharacterProvisionalRejectRequest,
    CharacterUpdateRequest,
    ExtractCharactersRequest,
)
from app.services.character import CharacterService
from app.services.character_extract import CharacterExtractService
from app.services.context_pack import CharacterContextPackService
from app.services.provisional import ProvisionalService
from app.utils.pagination import PageParams


def _project(**kwargs) -> Project:
    project = Project(slug="p", title="P", created_by=uuid.uuid4())
    project.id = kwargs.get("id", uuid.uuid4())
    return project


def _character(**kwargs) -> Character:
    character = Character(
        project_id=kwargs.get("project_id", uuid.uuid4()),
        display_name=kwargs.get("display_name", "Lý Phong"),
        role_one_liner=kwargs.get("role_one_liner", "Hero"),
        tier=kwargs.get("tier", 0),
        aliases=kwargs.get("aliases", []),
        status=kwargs.get("status", CharacterStatus.established),
        psyche_card=kwargs.get("psyche_card"),
        metadata_=kwargs.get("metadata", {}),
    )
    character.id = kwargs.get("id", uuid.uuid4())
    character.appearance_count = kwargs.get("appearance_count", 0)
    character.first_seen_chapter_id = kwargs.get("first_seen_chapter_id")
    character.last_seen_chapter_id = kwargs.get("last_seen_chapter_id")
    character.created_at = datetime.now(tz=UTC)
    character.updated_at = datetime.now(tz=UTC)
    return character


def _provisional(**kwargs) -> CharacterProvisional:
    row = CharacterProvisional(
        project_id=kwargs.get("project_id", uuid.uuid4()),
        mention_text=kwargs.get("mention_text", "Hắc Y Nhân"),
        mention_fingerprint=kwargs.get("mention_fingerprint", "abc"),
        chapter_id=kwargs.get("chapter_id", uuid.uuid4()),
        prose_version=1,
        snippet="...",
        proposed_fields=kwargs.get("proposed_fields", {}),
        status=kwargs.get("status", ProvisionalStatus.pending),
        extractor_source=ExtractorSource.heuristic,
    )
    row.id = kwargs.get("id", uuid.uuid4())
    row.merged_character_id = kwargs.get("merged_character_id")
    row.created_at = datetime.now(tz=UTC)
    return row


@pytest.mark.unit
async def test_character_service_create_duplicate_name() -> None:
    service = CharacterService(AsyncMock())
    service.characters.name_exists_for_project = AsyncMock(return_value=True)
    with pytest.raises(DuplicateDisplayNameError):
        await service.create_character(
            _project(),
            CharacterCreateRequest(display_name="Dup", role_one_liner="x"),
        )


@pytest.mark.unit
async def test_character_service_update_archived() -> None:
    service = CharacterService(AsyncMock())
    service.characters.get_by_id = AsyncMock(
        return_value=_character(status=CharacterStatus.archived)
    )
    with pytest.raises(CharacterArchivedError):
        await service.update_character(
            _project(), uuid.uuid4(), CharacterUpdateRequest(display_name="X")
        )


@pytest.mark.unit
async def test_character_service_promote_max_tier() -> None:
    service = CharacterService(AsyncMock())
    service.characters.get_by_id = AsyncMock(return_value=_character(tier=3))
    with pytest.raises(AlreadyMaxTierError):
        await service.promote_tier(_project(), uuid.uuid4())


@pytest.mark.unit
async def test_character_service_promote_tier_success() -> None:
    session = AsyncMock()
    service = CharacterService(session)
    character = _character(tier=0, metadata={"voice_hint": "trầm"})
    service.characters.get_by_id = AsyncMock(return_value=character)
    session.refresh = AsyncMock()
    result = await service.promote_tier(_project(), character.id)
    assert result.tier == 1


@pytest.mark.unit
async def test_character_service_search_vector_not_implemented() -> None:
    service = CharacterService(AsyncMock())
    with pytest.raises(NotImplementedFeatureError):
        await service.search_characters(_project(), "Phong", search_mode="vector")


@pytest.mark.unit
async def test_character_service_record_chapter_appearance() -> None:
    session = AsyncMock()
    service = CharacterService(session)
    chapter_id = uuid.uuid4()
    character = _character(aliases=[], last_seen_chapter_id=None)
    updated = await service.record_chapter_appearance(character, chapter_id, "Hắc Y Nhân")
    assert updated.appearance_count == 1
    assert "Hắc Y Nhân" in updated.aliases


@pytest.mark.unit
async def test_provisional_service_invalid_merge_request() -> None:
    service = ProvisionalService(AsyncMock())
    with pytest.raises(InvalidMergeRequestError):
        await service.merge_provisional(
            _project(),
            uuid.uuid4(),
            CharacterProvisionalMergeRequest(
                target_character_id=uuid.uuid4(),
                create_new=True,
            ),
            uuid.uuid4(),
        )


@pytest.mark.unit
async def test_provisional_service_merge_idempotent() -> None:
    session = AsyncMock()
    service = ProvisionalService(session)
    character = _character()
    prov = _provisional(
        status=ProvisionalStatus.merged,
        merged_character_id=character.id,
    )
    service.provisionals.get_by_id = AsyncMock(return_value=prov)
    service.characters.get_by_id = AsyncMock(return_value=character)
    service.chapters.get = AsyncMock(
        return_value=Chapter(project_id=prov.project_id, number=1, title="T", id=prov.chapter_id)
    )
    result = await service.merge_provisional(
        _project(id=prov.project_id),
        prov.id,
        CharacterProvisionalMergeRequest(target_character_id=character.id),
        uuid.uuid4(),
    )
    assert result.idempotent is True


@pytest.mark.unit
async def test_provisional_service_reject_non_pending() -> None:
    service = ProvisionalService(AsyncMock())
    service.provisionals.get_by_id = AsyncMock(
        return_value=_provisional(status=ProvisionalStatus.merged)
    )
    with pytest.raises(ProvisionalAlreadyResolvedError):
        await service.reject_provisional(
            _project(), uuid.uuid4(), CharacterProvisionalRejectRequest(), uuid.uuid4()
        )


@pytest.mark.unit
async def test_extract_service_llm_mode_501() -> None:
    service = CharacterExtractService(AsyncMock())
    with pytest.raises(NotImplementedFeatureError):
        await service.extract_from_chapter(
            _project(),
            uuid.uuid4(),
            ExtractCharactersRequest(extractor_mode="llm"),
        )


@pytest.mark.unit
async def test_extract_service_no_prose_version() -> None:
    service = CharacterExtractService(AsyncMock())
    chapter = Chapter(project_id=uuid.uuid4(), number=1, title="T")
    chapter.id = uuid.uuid4()
    chapter.current_prose_version = None
    service.chapters.get = AsyncMock(return_value=chapter)
    result = await service.extract_from_chapter(_project(id=chapter.project_id), chapter.id)
    assert result.created_count == 0


@pytest.mark.unit
async def test_context_pack_service_builds_entries() -> None:
    session = AsyncMock()
    service = CharacterContextPackService(session)
    project = _project()
    chapter = Chapter(project_id=project.id, number=1, title="T")
    chapter.id = uuid.uuid4()
    character = _character(project_id=project.id, tier=2)
    beat = SceneBeat(
        project_id=project.id,
        chapter_id=chapter.id,
        beat_key="1.1",
        summary="Lý Phong đi tu",
        sort_order=1,
    )
    service.chapters.get = AsyncMock(return_value=chapter)
    service.beats.list_for_chapter = AsyncMock(return_value=[beat])
    service.characters.find_by_name_or_alias = AsyncMock(return_value=character)
    service.characters.get_by_id = AsyncMock(return_value=character)
    service.characters.list_t3_for_project = AsyncMock(return_value=[])
    service.characters.search_keyword = AsyncMock(return_value=[])
    service.ledger.list_tail_for_entity = AsyncMock(return_value=[])

    result = await service.build_context_pack(
        project,
        CharacterContextPackRequest(chapter_id=chapter.id, include_ledger_tail=False),
    )
    assert len(result.entries) == 1
    assert result.entries[0].included_reason == "scene_beat"


@pytest.mark.unit
async def test_character_repository_filters() -> None:
    session = AsyncMock()
    repo = CharacterRepository(session)
    character = _character()
    session.scalars = AsyncMock(return_value=MagicMock(all=lambda: [character]))
    session.scalar = AsyncMock(return_value=1)
    items, total = await repo.list_for_project(
        character.project_id,
        PageParams(page=1, page_size=20),
        tier=0,
        q="Lý",
    )
    assert total == 1
    assert items[0].display_name == "Lý Phong"


@pytest.mark.unit
async def test_provisional_repository_pending_fingerprint() -> None:
    session = AsyncMock()
    repo = ProvisionalRepository(session)
    session.scalar = AsyncMock(return_value=_provisional())
    assert await repo.has_pending_fingerprint(uuid.uuid4(), "fp") is True
    pending = await repo.get_pending_by_fingerprint(uuid.uuid4(), "fp")
    assert pending is not None


@pytest.mark.unit
async def test_character_service_get_not_found() -> None:
    service = CharacterService(AsyncMock())
    service.characters.get_by_id = AsyncMock(return_value=None)
    with pytest.raises(NotFoundError):
        await service.get_character(_project(), uuid.uuid4())


@pytest.mark.unit
async def test_character_service_create_success() -> None:
    session = AsyncMock()
    service = CharacterService(session)
    service.characters.name_exists_for_project = AsyncMock(return_value=False)

    async def create_char(character: Character) -> Character:
        character.id = uuid.uuid4()
        character.appearance_count = 0
        character.created_at = datetime.now(tz=UTC)
        character.updated_at = datetime.now(tz=UTC)
        return character

    service.characters.create = AsyncMock(side_effect=create_char)
    session.refresh = AsyncMock()
    result = await service.create_character(
        _project(),
        CharacterCreateRequest(display_name="New", role_one_liner="r"),
    )
    assert result.display_name == "New"


@pytest.mark.unit
async def test_character_service_list_and_search_keyword() -> None:
    service = CharacterService(AsyncMock())
    character = _character(aliases=["Phong"])
    service.characters.list_for_project = AsyncMock(return_value=([character], 1))
    listed = await service.list_characters(_project(), PageParams(page=1, page_size=20))
    assert listed.pagination.total_items == 1

    service.characters.search_keyword = AsyncMock(return_value=[character])
    search = await service.search_characters(_project(), "Lý")
    assert search.items[0].match_type == "display_name"


@pytest.mark.unit
async def test_character_service_update_duplicate_name() -> None:
    service = CharacterService(AsyncMock())
    character = _character()
    service.characters.get_by_id = AsyncMock(return_value=character)
    service.characters.name_exists_for_project = AsyncMock(return_value=True)
    with pytest.raises(DuplicateDisplayNameError):
        await service.update_character(
            _project(), character.id, CharacterUpdateRequest(display_name="Dup")
        )


@pytest.mark.unit
async def test_character_service_promote_tier_requirements_fail() -> None:
    service = CharacterService(AsyncMock())
    service.characters.get_by_id = AsyncMock(return_value=_character(tier=0))
    with pytest.raises(TierRequirementsNotMetError):
        await service.promote_tier(_project(), uuid.uuid4())


@pytest.mark.unit
async def test_provisional_service_merge_into_existing() -> None:
    session = AsyncMock()
    service = ProvisionalService(session)
    project = _project()
    chapter_id = uuid.uuid4()
    target = _character(project_id=project.id)
    prov = _provisional(project_id=project.id, chapter_id=chapter_id)
    service.provisionals.get_by_id = AsyncMock(return_value=prov)
    service.characters.get_by_id = AsyncMock(return_value=target)
    service.chapters.get = AsyncMock(
        return_value=Chapter(project_id=project.id, number=1, title="T", id=chapter_id)
    )
    session.flush = AsyncMock()
    result = await service.merge_provisional(
        project,
        prov.id,
        CharacterProvisionalMergeRequest(target_character_id=target.id),
        uuid.uuid4(),
    )
    assert result.idempotent is False
    assert prov.status == ProvisionalStatus.merged


@pytest.mark.unit
async def test_provisional_service_promote_new() -> None:
    session = AsyncMock()
    service = ProvisionalService(session)
    project = _project()
    prov = _provisional(project_id=project.id)
    service.provisionals.get_by_id = AsyncMock(return_value=prov)
    service.characters.name_exists_for_project = AsyncMock(return_value=False)

    async def create_char(character: Character) -> Character:
        character.id = uuid.uuid4()
        character.created_at = datetime.now(tz=UTC)
        character.updated_at = datetime.now(tz=UTC)
        return character

    service.characters.create = AsyncMock(side_effect=create_char)
    service.chapters.get = AsyncMock(
        return_value=Chapter(project_id=project.id, number=1, title="T", id=prov.chapter_id)
    )
    session.flush = AsyncMock()
    session.refresh = AsyncMock()
    result = await service.merge_provisional(
        project,
        prov.id,
        CharacterProvisionalMergeRequest(create_new=True, display_name="New Hero"),
        uuid.uuid4(),
    )
    assert result.character.display_name == "New Hero"


@pytest.mark.unit
async def test_provisional_service_reject_success() -> None:
    session = AsyncMock()
    service = ProvisionalService(session)
    prov = _provisional()
    service.provisionals.get_by_id = AsyncMock(return_value=prov)
    service.chapters.get = AsyncMock(
        return_value=Chapter(project_id=prov.project_id, number=1, title="T", id=prov.chapter_id)
    )
    session.flush = AsyncMock()
    result = await service.reject_provisional(
        _project(id=prov.project_id),
        prov.id,
        CharacterProvisionalRejectRequest(reason="noise"),
        uuid.uuid4(),
    )
    assert result.status == ProvisionalStatus.rejected


@pytest.mark.unit
async def test_extract_service_creates_provisionals(monkeypatch: pytest.MonkeyPatch) -> None:
    session = AsyncMock()
    service = CharacterExtractService(session)
    project = _project()
    chapter = Chapter(
        project_id=project.id,
        number=1,
        title="T",
        status=ChapterStatus.drafting,
    )
    chapter.id = uuid.uuid4()
    chapter.current_prose_version = 1
    prose = ProseVersion(
        project_id=project.id,
        chapter_id=chapter.id,
        version=1,
        content="ignored",
        word_count=5,
        created_by=uuid.uuid4(),
    )
    service.chapters.get = AsyncMock(return_value=chapter)
    service.prose.get_version = AsyncMock(return_value=prose)
    service.characters.find_by_name_or_alias = AsyncMock(return_value=None)
    service.provisionals.has_pending_fingerprint = AsyncMock(return_value=False)

    async def assign_id(prov: CharacterProvisional) -> CharacterProvisional:
        prov.id = uuid.uuid4()
        return prov

    service.provisionals.create = AsyncMock(side_effect=assign_id)

    async def schema_from_row(row, **_):
        return _provisional(
            id=row.id,
            project_id=row.project_id,
            mention_text=row.mention_text,
            chapter_id=row.chapter_id,
        )

    service.provisional_service._to_provisional_schema = AsyncMock(side_effect=schema_from_row)
    monkeypatch.setattr(
        "app.services.character_extract.extract_mentions_from_text",
        lambda _text: ["Hắc Y Nhân"],
    )

    result = await service.extract_from_chapter(
        project, chapter.id, ExtractCharactersRequest(include_beats=False)
    )
    assert result.created_count == 1


@pytest.mark.unit
async def test_context_pack_includes_t3_and_name_hints() -> None:
    session = AsyncMock()
    service = CharacterContextPackService(session)
    project = _project()
    chapter = Chapter(project_id=project.id, number=1, title="T")
    chapter.id = uuid.uuid4()
    t3 = _character(project_id=project.id, tier=3, last_seen_chapter_id=chapter.id)
    hint_char = _character(project_id=project.id, display_name="Hint", tier=0)
    service.chapters.get = AsyncMock(return_value=chapter)
    service.beats.list_for_chapter = AsyncMock(return_value=[])
    service.characters.list_t3_for_project = AsyncMock(return_value=[t3])
    service.characters.search_keyword = AsyncMock(return_value=[hint_char])

    async def resolve_character(pid, cid):
        return t3 if cid == t3.id else hint_char

    service.characters.get_by_id = AsyncMock(side_effect=resolve_character)
    service.ledger.list_tail_for_entity = AsyncMock(return_value=[])

    result = await service.build_context_pack(
        project,
        CharacterContextPackRequest(
            chapter_id=chapter.id,
            name_hints=["Hint"],
            max_stubs=1,
            include_ledger_tail=False,
        ),
    )
    reasons = {entry.included_reason for entry in result.entries}
    assert "t3_principal" in reasons
    assert "name_hint" in reasons


@pytest.mark.unit
async def test_character_repository_search_and_find() -> None:
    session = AsyncMock()
    repo = CharacterRepository(session)
    character = _character(display_name="Alpha", aliases=["Beta"])
    session.scalars = AsyncMock(return_value=MagicMock(all=lambda: [character]))
    found = await repo.search_keyword(character.project_id, "Al", limit=5)
    assert found == [character]

    session.scalars = AsyncMock(return_value=MagicMock(all=lambda: [character]))
    by_alias = await repo.find_by_name_or_alias(character.project_id, "beta")
    assert by_alias is character

    session.scalar = AsyncMock(return_value=1)
    assert await repo.name_exists_for_project(character.project_id, "Alpha") is True


@pytest.mark.unit
async def test_extract_service_skip_duplicate_name(monkeypatch: pytest.MonkeyPatch) -> None:
    session = AsyncMock()
    service = CharacterExtractService(session)
    project = _project()
    chapter = Chapter(
        project_id=project.id,
        number=1,
        title="T",
        status=ChapterStatus.drafting,
    )
    chapter.id = uuid.uuid4()
    chapter.current_prose_version = 1
    service.chapters.get = AsyncMock(return_value=chapter)
    service.prose.get_version = AsyncMock(
        return_value=ProseVersion(
            project_id=project.id,
            chapter_id=chapter.id,
            version=1,
            content="x",
            word_count=1,
            created_by=uuid.uuid4(),
        )
    )
    service.characters.find_by_name_or_alias = AsyncMock(return_value=_character())
    monkeypatch.setattr(
        "app.services.character_extract.extract_mentions_from_text",
        lambda _text: ["Known"],
    )
    result = await service.extract_from_chapter(
        project, chapter.id, ExtractCharactersRequest(include_beats=False)
    )
    assert result.skipped_count == 1
    assert result.skipped_reasons["duplicate_name"] == 1


@pytest.mark.unit
async def test_character_service_search_alias_match_type() -> None:
    service = CharacterService(AsyncMock())
    character = _character(display_name="Lý Phong", aliases=["Phong"])
    service.characters.search_keyword = AsyncMock(return_value=[character])
    search = await service.search_characters(_project(), "Phong")
    assert search.items[0].match_type == "alias"
    assert search.items[0].matched_alias == "Phong"


@pytest.mark.unit
async def test_provisional_service_list_provisionals() -> None:
    service = ProvisionalService(AsyncMock())
    prov = _provisional()
    service.provisionals.list_for_project = AsyncMock(return_value=([prov], 1))
    service.provisionals.count_pending = AsyncMock(return_value=1)
    service.chapters.get = AsyncMock(
        return_value=Chapter(project_id=prov.project_id, number=1, title="T", id=prov.chapter_id)
    )
    result = await service.list_provisionals(
        _project(id=prov.project_id),
        PageParams(page=1, page_size=20),
    )
    assert result.pending_count == 1
    assert result.items[0].chapter_number == 1
