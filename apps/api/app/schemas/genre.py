"""Genre rule pack schemas."""

import uuid
from datetime import datetime
from typing import Any

from pydantic import BaseModel, Field

from app.models.enums import GenreProfile


class GenreRulePackPatch(BaseModel):
    pack: dict[str, Any] = Field(default_factory=dict)


class GenreRulePackResponse(BaseModel):
    project_id: uuid.UUID
    genre_profile: GenreProfile
    pack: dict[str, Any]
    updated_at: datetime
