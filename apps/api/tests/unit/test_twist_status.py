"""Twist status transition unit tests."""

import pytest

from app.exceptions import InvalidTwistStatusTransitionError
from app.models.enums import TwistPlanStatus
from app.utils.twist_status import (
    status_after_first_plant,
    status_after_payoff,
    validate_twist_transition,
)


def test_seeded_to_planted_on_first_plant() -> None:
    assert status_after_first_plant(TwistPlanStatus.seeded) == TwistPlanStatus.planted
    assert status_after_first_plant(TwistPlanStatus.planted) == TwistPlanStatus.planted


def test_payoff_arms_twist() -> None:
    assert status_after_payoff(TwistPlanStatus.seeded) == TwistPlanStatus.armed
    assert status_after_payoff(TwistPlanStatus.planted) == TwistPlanStatus.armed
    assert status_after_payoff(TwistPlanStatus.armed) == TwistPlanStatus.armed


def test_paid_off_is_terminal() -> None:
    with pytest.raises(InvalidTwistStatusTransitionError):
        validate_twist_transition(TwistPlanStatus.paid_off, TwistPlanStatus.abandoned)


def test_valid_abandon_from_armed() -> None:
    validate_twist_transition(TwistPlanStatus.armed, TwistPlanStatus.abandoned)


def test_invalid_transition_planted_to_paid_off() -> None:
    with pytest.raises(InvalidTwistStatusTransitionError):
        validate_twist_transition(TwistPlanStatus.planted, TwistPlanStatus.paid_off)


def test_same_status_no_op() -> None:
    validate_twist_transition(TwistPlanStatus.planted, TwistPlanStatus.planted)
