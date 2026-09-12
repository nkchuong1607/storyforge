"""Continuity rule engine unit tests."""

import uuid

import pytest

from app.models.bible import BibleEntryStaging
from app.models.character import Character
from app.models.enums import BibleSection, ContinuityResult, ContinuitySeverity
from app.services.continuity.engine import (
    check_bible_staging_conflicts_settled,
    check_character_deceased_appears_alive,
    run_continuity_checks,
)


def _character(name: str) -> Character:
    char = Character(project_id=uuid.uuid4(), display_name=name, tier=0)
    char.id = uuid.uuid4()
    return char


@pytest.mark.unit
def test_character_deceased_appears_alive_fail() -> None:
    char = _character("Lý Phong")
    ledger = [
        {
            "entity_id": str(char.id),
            "event_type": "status_change",
            "payload": {"from": "alive", "to": "deceased"},
        }
    ]
    prose = "Lý Phong nói với sư phụ rằng anh sẽ tu luyện."
    issue = check_character_deceased_appears_alive(
        character=char,
        prose=prose,
        chapter_number=1,
        ledger_tail=ledger,
    )
    assert issue is not None
    assert issue.code == "character_deceased_appears_alive"
    assert issue.severity == ContinuitySeverity.FAIL.value


@pytest.mark.unit
def test_character_deceased_flashback_skipped() -> None:
    char = _character("Lý Phong")
    ledger = [
        {
            "entity_id": str(char.id),
            "event_type": "status_change",
            "payload": {"from": "alive", "to": "deceased"},
        }
    ]
    prose = "Trong hồi tưởng, Lý Phong nói với sư phụ."
    issue = check_character_deceased_appears_alive(
        character=char,
        prose=prose,
        chapter_number=1,
        ledger_tail=ledger,
    )
    assert issue is None


@pytest.mark.unit
def test_bible_staging_conflict_fail() -> None:
    staging = BibleEntryStaging(
        project_id=uuid.uuid4(),
        entry_key="world_rules.test",
        section=BibleSection.world_rules,
        title="Test",
        content_md="Changed content",
        base_bible_version=0,
        created_by=uuid.uuid4(),
    )
    snapshot = {
        "entries": [
            {
                "entry_key": "world_rules.test",
                "content_md": "Original content",
                "metadata": {"status": "active"},
            }
        ]
    }
    issues = check_bible_staging_conflicts_settled(
        staging_rows=[staging],
        snapshot_json=snapshot,
        bible_version_current=1,
        chapter_number=1,
    )
    assert len(issues) == 1
    assert issues[0].code == "bible_staging_conflicts_settled"


@pytest.mark.unit
def test_run_continuity_checks_warn_only() -> None:
    issues, _state_diff, stats, result = run_continuity_checks(
        prose="Một câu chuyện bình thường không có nhân vật.",
        chapter_number=1,
        characters=[],
        ledger_tail=[],
        staging_rows=[],
        snapshot_json={"entries": []},
        bible_version_current=0,
        beats=[],
        active_override_fingerprints=set(),
    )
    assert result in (ContinuityResult.PASS, ContinuityResult.WARN)
    assert stats["errors"] == 0


@pytest.mark.unit
def test_override_skips_fingerprint_on_rerun() -> None:
    char = _character("Lý Phong")
    ledger = [
        {
            "entity_id": str(char.id),
            "event_type": "status_change",
            "payload": {"from": "alive", "to": "deceased"},
        }
    ]
    prose = "Lý Phong nói với sư phụ."
    issue = check_character_deceased_appears_alive(
        character=char, prose=prose, chapter_number=1, ledger_tail=ledger
    )
    assert issue is not None
    issues, _, _, result = run_continuity_checks(
        prose=prose,
        chapter_number=1,
        characters=[char],
        ledger_tail=ledger,
        staging_rows=[],
        snapshot_json={"entries": []},
        bible_version_current=0,
        beats=[],
        active_override_fingerprints={issue.fingerprint},
    )
    assert all(i["fingerprint"] != issue.fingerprint for i in issues)
    assert result != ContinuityResult.FAIL or stats_errors_zero(issues)


def stats_errors_zero(issues: list) -> bool:
    return not any(i.get("severity") == "fail" for i in issues)
