"""Twist schema and context pack strip unit tests."""

import uuid
from datetime import UTC, datetime

from app.models.enums import (
    ContextAudience,
    TwistPlanKind,
    TwistPlanStatus,
)
from app.models.twist import TwistPlan as TwistPlanModel
from app.schemas.twist import strip_writer_secrets, twist_plan_from_model
from app.services.twist_context_pack import json_has_secret_truth_key


def test_writer_audience_strips_secrets() -> None:
    twist = TwistPlanModel(
        id=uuid.uuid4(),
        project_id=uuid.uuid4(),
        title="Secret",
        secret_truth="Truth hidden",
        status=TwistPlanStatus.seeded,
        kind=TwistPlanKind.twist,
        misdirection="False trail",
        constraints_json={
            "min_plants_before_payoff": 1,
            "constrained_facts": [{"key": "killer"}],
        },
        genre_strictness=None,
        created_by=uuid.uuid4(),
        created_at=datetime.now(UTC),
        updated_at=datetime.now(UTC),
    )
    schema = twist_plan_from_model(twist, plant_count=0, audience=ContextAudience.writer)
    assert schema.secret_truth is None
    assert schema.misdirection is None
    assert "constrained_facts" not in schema.constraints_json


def test_strip_writer_secrets_helper() -> None:
    result = strip_writer_secrets({"constrained_facts": [], "min_plants_before_payoff": 2})
    assert "constrained_facts" not in result
    assert result["min_plants_before_payoff"] == 2


def test_json_has_secret_truth_key_recursive() -> None:
    assert json_has_secret_truth_key({"meta": {"secret_truth": "x"}})
    assert not json_has_secret_truth_key({"twist_title": "ok", "plants": []})
