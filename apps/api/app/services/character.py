"""Character business logic — CRUD, search, tier promotion."""

from __future__ import annotations

import uuid
from datetime import UTC, datetime

from sqlalchemy.ext.asyncio import AsyncSession

from app.exceptions import (
    AlreadyMaxTierError,
    CharacterArchivedError,
    DuplicateDisplayNameError,
    NotFoundError,
    NotImplementedFeatureError,
    TierRequirementsNotMetError,
)
from app.models.character import Character
from app.models.enums import CharacterStatus
from app.models.project import Project
from app.repositories.character import CharacterRepository
from app.schemas.character import (
    Character as CharacterSchema,
)
from app.schemas.character import (
    CharacterCreateRequest,
    CharacterListResponse,
    CharacterPromoteTierRequest,
    CharacterSearchResponse,
    CharacterSearchResult,
    CharacterUpdateRequest,
)
from app.utils.character_aliases import normalize_name
from app.utils.pagination import PageParams, paginated
from app.utils.tier_validation import TierRequirementsError, validate_tier_promotion


class CharacterService:
    RECURRENCE_THRESHOLD = 3

    def __init__(self, session: AsyncSession) -> None:
        self.session = session
        self.characters = CharacterRepository(session)

    def _to_schema(self, character: Character) -> CharacterSchema:
        return CharacterSchema.from_model(character)

    async def list_characters(
        self,
        project: Project,
        page: PageParams,
        *,
        tier: int | None = None,
        status: CharacterStatus | None = None,
        q: str | None = None,
    ) -> CharacterListResponse:
        exclude_archived = status is None
        items, total = await self.characters.list_for_project(
            project.id,
            page,
            tier=tier,
            status=status,
            exclude_archived=exclude_archived,
            q=q,
        )
        characters = [self._to_schema(item) for item in items]
        return paginated(characters, page.page, page.page_size, total)

    async def get_character(self, project: Project, character_id: uuid.UUID) -> CharacterSchema:
        character = await self.characters.get_by_id(project.id, character_id)
        if character is None:
            raise NotFoundError()
        return self._to_schema(character)

    async def create_character(
        self, project: Project, payload: CharacterCreateRequest
    ) -> CharacterSchema:
        if payload.tier > 2:
            raise TierRequirementsNotMetError("Cannot create character at tier 3")
        if await self.characters.name_exists_for_project(project.id, payload.display_name):
            raise DuplicateDisplayNameError(payload.display_name)

        character = Character(
            project_id=project.id,
            display_name=payload.display_name.strip(),
            role_one_liner=payload.role_one_liner,
            tier=payload.tier,
            aliases=list(payload.aliases),
            status=payload.status,
            psyche_card=None,
        )
        created = await self.characters.create(character)
        await self.session.refresh(created)
        return self._to_schema(created)

    async def update_character(
        self,
        project: Project,
        character_id: uuid.UUID,
        payload: CharacterUpdateRequest,
    ) -> CharacterSchema:
        character = await self.characters.get_by_id(project.id, character_id)
        if character is None:
            raise NotFoundError()
        if character.status == CharacterStatus.archived:
            raise CharacterArchivedError()

        if payload.display_name is not None:
            if await self.characters.name_exists_for_project(
                project.id, payload.display_name, exclude_id=character.id
            ):
                raise DuplicateDisplayNameError(payload.display_name)
            character.display_name = payload.display_name.strip()
        if payload.role_one_liner is not None:
            character.role_one_liner = payload.role_one_liner
        if payload.aliases is not None:
            character.aliases = list(payload.aliases)
        if payload.psyche_card is not None:
            character.psyche_card = payload.psyche_card
        if payload.status is not None:
            character.status = payload.status
        if payload.metadata is not None:
            character.metadata_ = payload.metadata

        character.updated_at = datetime.now(UTC)
        await self.session.flush()
        await self.session.refresh(character)
        return self._to_schema(character)

    async def promote_tier(
        self,
        project: Project,
        character_id: uuid.UUID,
        payload: CharacterPromoteTierRequest | None = None,
    ) -> CharacterSchema:
        character = await self.characters.get_by_id(project.id, character_id)
        if character is None:
            raise NotFoundError()
        if character.status == CharacterStatus.archived:
            raise CharacterArchivedError()
        if character.tier >= 3:
            raise AlreadyMaxTierError()

        confirm_t3 = payload.confirm_t3 if payload else False
        metadata = dict(character.metadata_ or {})
        try:
            next_tier = validate_tier_promotion(
                current_tier=character.tier,
                role_one_liner=character.role_one_liner,
                psyche_card=character.psyche_card,
                metadata=metadata,
                confirm_t3=confirm_t3,
            )
        except TierRequirementsError as exc:
            raise TierRequirementsNotMetError(exc.message, exc.details) from exc

        character.tier = next_tier
        metadata.pop("tier_suggest", None)
        character.metadata_ = metadata
        character.updated_at = datetime.now(UTC)
        await self.session.flush()
        await self.session.refresh(character)
        return self._to_schema(character)

    async def search_characters(
        self,
        project: Project,
        query: str,
        *,
        limit: int = 20,
        search_mode: str = "keyword",
    ) -> CharacterSearchResponse:
        if search_mode == "vector":
            raise NotImplementedFeatureError("Vector search requires pgvector stub population")

        rows = await self.characters.search_keyword(project.id, query, limit=limit)
        normalized_query = normalize_name(query)
        results: list[CharacterSearchResult] = []
        for row in rows:
            match_type = "display_name"
            matched_alias = None
            if not row.display_name.strip().casefold().startswith(normalized_query):
                match_type = "alias"
                for alias in row.aliases or []:
                    if str(alias).strip().casefold().startswith(normalized_query):
                        matched_alias = str(alias)
                        break
                    if normalize_name(str(alias)) == normalized_query:
                        matched_alias = str(alias)
                        break
            results.append(
                CharacterSearchResult(
                    character=self._to_schema(row),
                    match_type=match_type,
                    matched_alias=matched_alias,
                    score=1.0,
                )
            )
        return CharacterSearchResponse(items=results, search_mode="keyword")

    async def record_chapter_appearance(
        self,
        character: Character,
        chapter_id: uuid.UUID,
        mention_text: str | None = None,
    ) -> Character:
        """Update chapter refs and aliases after merge/extract link."""
        from app.utils.character_aliases import append_alias_if_distinct

        if mention_text:
            character.aliases = append_alias_if_distinct(
                list(character.aliases or []),
                mention_text,
                character.display_name,
            )

        if character.first_seen_chapter_id is None:
            character.first_seen_chapter_id = chapter_id
            character.appearance_count += 1
        elif character.last_seen_chapter_id != chapter_id:
            character.appearance_count += 1

        character.last_seen_chapter_id = chapter_id
        character.updated_at = datetime.now(UTC)
        await self.session.flush()
        return character
