"""Project reality settings schemas."""

import uuid
from datetime import datetime

from pydantic import BaseModel, ConfigDict, Field

from app.models.enums import FactClaimCategory, RealityAnchorsMode


class ProjectRealitySettings(BaseModel):
    model_config = ConfigDict(from_attributes=True)

    project_id: uuid.UUID
    reality_anchors: RealityAnchorsMode
    enabled_categories: list[FactClaimCategory] = Field(default_factory=list)
    fact_check_blocks_settle: bool = False
    auto_run_on_save: bool = False
    include_research_notes: bool = True
    updated_at: datetime


class ProjectRealitySettingsUpdate(BaseModel):
    reality_anchors: RealityAnchorsMode | None = None
    enabled_categories: list[FactClaimCategory] | None = None
    fact_check_blocks_settle: bool | None = None
    auto_run_on_save: bool | None = None
    include_research_notes: bool | None = None
