"""Twist plan status transition validation."""

from app.exceptions import InvalidTwistStatusTransitionError
from app.models.enums import TwistPlanStatus

ALLOWED_TRANSITIONS: dict[TwistPlanStatus, set[TwistPlanStatus]] = {
    TwistPlanStatus.seeded: {
        TwistPlanStatus.planted,
        TwistPlanStatus.armed,
        TwistPlanStatus.abandoned,
    },
    TwistPlanStatus.planted: {
        TwistPlanStatus.armed,
        TwistPlanStatus.abandoned,
    },
    TwistPlanStatus.armed: {
        TwistPlanStatus.paid_off,
        TwistPlanStatus.abandoned,
    },
    TwistPlanStatus.paid_off: set(),
    TwistPlanStatus.abandoned: set(),
}


def validate_twist_transition(current: TwistPlanStatus, target: TwistPlanStatus) -> None:
    if current == target:
        return
    if current == TwistPlanStatus.paid_off:
        raise InvalidTwistStatusTransitionError("Paid-off twist cannot change status")
    allowed = ALLOWED_TRANSITIONS.get(current, set())
    if target not in allowed:
        raise InvalidTwistStatusTransitionError(
            f"Cannot transition from {current.value} to {target.value}"
        )


def status_after_first_plant(current: TwistPlanStatus) -> TwistPlanStatus:
    if current == TwistPlanStatus.seeded:
        return TwistPlanStatus.planted
    return current


def status_after_payoff(current: TwistPlanStatus) -> TwistPlanStatus:
    if current in (TwistPlanStatus.seeded, TwistPlanStatus.planted):
        return TwistPlanStatus.armed
    return current
