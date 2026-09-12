"""Character business logic."""

from sqlalchemy.ext.asyncio import AsyncSession

from app.models.project import Project
from app.repositories.character import CharacterRepository
from app.schemas.character import Character as CharacterSchema
from app.utils.pagination import PageParams, paginated


class CharacterService:
    def __init__(self, session: AsyncSession) -> None:
        self.session = session
        self.characters = CharacterRepository(session)

    async def list_characters(self, project: Project, page: PageParams):
        items, total = await self.characters.list_for_project(project.id, page)
        characters = [CharacterSchema.model_validate(item) for item in items]
        return paginated(characters, page.page, page.page_size, total)
