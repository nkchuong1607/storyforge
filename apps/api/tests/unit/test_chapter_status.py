"""Chapter status FSM unit tests."""

import pytest

from app.exceptions import InvalidChapterStatusTransitionError
from app.models.enums import ChapterStatus
from app.services.chapter_status import (
    is_chapter_locked,
    validate_status_transition,
)


@pytest.mark.unit
def test_same_status_noop() -> None:
    validate_status_transition(ChapterStatus.drafting, ChapterStatus.drafting)


@pytest.mark.unit
def test_planned_to_drafting_allowed() -> None:
    validate_status_transition(ChapterStatus.planned, ChapterStatus.drafting)


@pytest.mark.unit
def test_drafting_to_reviewing_allowed() -> None:
    validate_status_transition(ChapterStatus.drafting, ChapterStatus.reviewing)


@pytest.mark.unit
def test_reviewing_to_drafting_allowed() -> None:
    validate_status_transition(ChapterStatus.reviewing, ChapterStatus.drafting)


@pytest.mark.unit
def test_reviewing_to_locked_allowed() -> None:
    validate_status_transition(ChapterStatus.reviewing, ChapterStatus.locked)


@pytest.mark.unit
def test_locked_blocks_transition() -> None:
    with pytest.raises(InvalidChapterStatusTransitionError):
        validate_status_transition(ChapterStatus.locked, ChapterStatus.drafting)


@pytest.mark.unit
def test_planned_to_locked_rejected() -> None:
    with pytest.raises(InvalidChapterStatusTransitionError):
        validate_status_transition(ChapterStatus.planned, ChapterStatus.locked)


@pytest.mark.unit
def test_is_chapter_locked() -> None:
    assert is_chapter_locked(ChapterStatus.locked) is True
    assert is_chapter_locked(ChapterStatus.drafting) is False
