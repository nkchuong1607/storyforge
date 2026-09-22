"""Extended craft rule unit tests."""

import uuid

from app.models.enums import GenreProfile, TwistPlanStatus
from app.services.continuity.craft import parse_checklist, run_craft_checks
from app.services.continuity.foreshadow import ForeshadowTwistContext
from app.services.craft_defaults import mystery_fair_play_v1


def test_reader_spoiler_knowledge_wall() -> None:
    twist = ForeshadowTwistContext(
        twist_id=uuid.uuid4(),
        title="Secret",
        secret_truth="Butler did it",
        status=TwistPlanStatus.planted,
        constraints_json={
            "knowledge_walls": [{"before_chapter": 5, "character_id": str(uuid.uuid4())}]
        },
        genre_strictness=None,
        misdirection=None,
    )
    issues = run_craft_checks(
        chapter_id=uuid.uuid4(),
        chapter_number=3,
        prose="The Butler did it was revealed.",
        genre_profile=GenreProfile.mystery,
        pack_json=mystery_fair_play_v1(),
        payoffs=[],
        plants=[],
        all_twists=[twist],
    )
    assert any(i.code == "craft_mystery_reader_spoiler" for i in issues)


def test_parse_checklist_skips_invalid_entries() -> None:
    pack = {"checklist": [{"id": 1}, {"code": "x"}, {"id": "ok", "code": "craft_x"}]}
    items = parse_checklist(pack)
    assert len(items) == 1
    assert items[0].item_id == "ok"
