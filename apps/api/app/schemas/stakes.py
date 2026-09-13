"""Stakes ledger schemas."""

import uuid
from datetime import datetime

from pydantic import BaseModel, ConfigDict, Field

from app.models.enums import StakesEntryStatus


class ActChapterBoundary(BaseModel):
    act_number: int
    start_chapter: int
    end_chapter: int
    label: str | None = None


class ActStructureSettings(BaseModel):
    model_config = ConfigDict(from_attributes=True)

    project_id: uuid.UUID
    act_count: int = Field(ge=1, le=7)
    chapters_per_act: list[ActChapterBoundary] = Field(default_factory=list)
    enabled: bool
    flat_middle_window_chapters: int
    updated_at: datetime


class ActStructureSettingsUpdateRequest(BaseModel):
    act_count: int | None = Field(default=None, ge=1, le=7)
    chapters_per_act: list[ActChapterBoundary] | None = None
    enabled: bool | None = None
    flat_middle_window_chapters: int | None = Field(default=None, ge=1)


class StakesLedgerEntry(BaseModel):
    model_config = ConfigDict(from_attributes=True)

    id: uuid.UUID
    project_id: uuid.UUID
    act_number: int
    checkpoint_key: str
    title: str
    description_md: str = ""
    target_level: int = Field(ge=0, le=5)
    status: StakesEntryStatus
    plant_chapter_id: uuid.UUID | None = None
    resolve_chapter_id: uuid.UUID | None = None
    linked_twist_id: uuid.UUID | None = None
    sort_order: int = 0
    created_at: datetime
    updated_at: datetime


class StakesEntryCreateRequest(BaseModel):
    act_number: int = Field(ge=1)
    checkpoint_key: str
    title: str
    description_md: str = ""
    target_level: int = Field(ge=0, le=5)
    sort_order: int = 0
    linked_twist_id: uuid.UUID | None = None


class StakesEntryUpdateRequest(BaseModel):
    title: str | None = None
    description_md: str | None = None
    target_level: int | None = Field(default=None, ge=0, le=5)
    status: StakesEntryStatus | None = None
    plant_chapter_id: uuid.UUID | None = None
    resolve_chapter_id: uuid.UUID | None = None
    linked_twist_id: uuid.UUID | None = None
    sort_order: int | None = None


class StakesEntryListResponse(BaseModel):
    items: list[StakesLedgerEntry]


class StakesBoardActColumn(BaseModel):
    act_number: int
    label: str | None = None
    start_chapter: int | None = None
    end_chapter: int | None = None
    entries: list[StakesLedgerEntry]


class StakesBoardWarnings(BaseModel):
    flat_middle: bool = False
    open_fail_count: int = 0


class StakesBoardResponse(BaseModel):
    settings: dict
    acts: list[StakesBoardActColumn]
    warnings: StakesBoardWarnings


class StakesContextPackRequest(BaseModel):
    chapter_id: uuid.UUID


class StakesContextPackCheckpoint(BaseModel):
    checkpoint_key: str
    target_level: int
    status: StakesEntryStatus


class StakesContextPackResponse(BaseModel):
    act_number: int
    current_peak_level: int | None = None
    checkpoints: list[StakesContextPackCheckpoint]
