"""Character request/response schemas."""

import uuid
from datetime import datetime
from typing import Any

from pydantic import BaseModel, ConfigDict, Field

from app.utils.pagination import PaginatedResponse, PaginationMeta


class Character(BaseModel):
    model_config = ConfigDict(from_attributes=True)

    id: uuid.UUID
    project_id: uuid.UUID
    display_name: str
    role_one_liner: str | None = None
    tier: int = Field(default=0)
    psyche_card: dict[str, Any] = Field(default_factory=dict)
    created_at: datetime
    updated_at: datetime


class CharacterListResponse(PaginatedResponse[Character]):
    pagination: PaginationMeta
