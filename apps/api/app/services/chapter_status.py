"""Chapter status finite state machine."""

from app.exceptions import InvalidChapterStatusTransitionError
from app.models.enums import ChapterStatus

ALLOWED_TRANSITIONS: dict[ChapterStatus, set[ChapterStatus]] = {
    ChapterStatus.planned: {ChapterStatus.drafting},
    ChapterStatus.drafting: {ChapterStatus.reviewing},
    ChapterStatus.reviewing: {ChapterStatus.drafting, ChapterStatus.locked},
    ChapterStatus.settled: set(),
    ChapterStatus.locked: set(),
}


def validate_status_transition(current: ChapterStatus, target: ChapterStatus) -> None:
    """Raise if transition from current to target is not allowed."""
    if current == target:
        return
    if current == ChapterStatus.locked:
        raise InvalidChapterStatusTransitionError("Cannot transition out of locked status")
    allowed = ALLOWED_TRANSITIONS.get(current, set())
    if target not in allowed:
        raise InvalidChapterStatusTransitionError(
            f"Cannot transition from {current.value} to {target.value}"
        )


def is_chapter_locked(status: ChapterStatus) -> bool:
    return status == ChapterStatus.locked
