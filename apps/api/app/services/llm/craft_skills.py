"""FakeLLM craft skill stubs for Mystery fair-play pack."""

from __future__ import annotations

from dataclasses import dataclass
from typing import Any


@dataclass
class CraftSkillResult:
    skill: str
    suggestion: str
    severity: str
    evidence: dict[str, Any]


def mystery_clue_plant(*, prose: str, twist_title: str) -> CraftSkillResult:
    """Suggest planting a clue — deterministic stub."""
    hint = f'Consider planting a fair-play clue for "{twist_title}" before the reveal.'
    if "clue" in prose.lower() or "man mối" in prose.lower():
        hint = f'Existing clue language detected for "{twist_title}" — verify chapter order.'
    return CraftSkillResult(
        skill="mystery_clue_plant",
        suggestion=hint,
        severity="warn",
        evidence={"twist_title": twist_title, "prose_length": len(prose)},
    )


def mystery_reveal_align(*, prose: str, open_checklist_codes: list[str]) -> CraftSkillResult:
    """Align reveal with planted clues — deterministic stub."""
    codes = ",".join(open_checklist_codes) if open_checklist_codes else "none"
    return CraftSkillResult(
        skill="mystery_reveal_align",
        suggestion=f"Open craft checklist codes: {codes}. Ensure reveal maps to prior plants.",
        severity="warn",
        evidence={"open_codes": open_checklist_codes},
    )


def mystery_red_herring(*, prose: str, has_misdirection_label: bool) -> CraftSkillResult:
    """Red herring labeling hint — deterministic stub."""
    if not has_misdirection_label and (
        "red herring" in prose.lower() or "nghi phạm giả" in prose.lower()
    ):
        suggestion = "Label misdirection on TwistPlan when prose uses red-herring markers."
        severity = "warn"
    else:
        suggestion = "Misdirection labeling looks consistent with TwistPlan."
        severity = "pass"
    return CraftSkillResult(
        skill="mystery_red_herring",
        suggestion=suggestion,
        severity=severity,
        evidence={"has_misdirection_label": has_misdirection_label},
    )


def run_craft_skill(
    skill_name: str,
    *,
    prose: str,
    twist_title: str = "",
    open_checklist_codes: list[str] | None = None,
    has_misdirection_label: bool = False,
) -> CraftSkillResult:
    """Dispatch craft skill by name."""
    if skill_name == "mystery_clue_plant":
        return mystery_clue_plant(prose=prose, twist_title=twist_title)
    if skill_name == "mystery_reveal_align":
        return mystery_reveal_align(prose=prose, open_checklist_codes=open_checklist_codes or [])
    if skill_name == "mystery_red_herring":
        return mystery_red_herring(prose=prose, has_misdirection_label=has_misdirection_label)
    return CraftSkillResult(
        skill=skill_name,
        suggestion="Unknown craft skill",
        severity="warn",
        evidence={},
    )


def run_pack_craft_skills(
    pack_json: dict[str, Any],
    *,
    prose: str,
    twist_title: str = "",
    open_checklist_codes: list[str] | None = None,
    has_misdirection_label: bool = False,
) -> list[CraftSkillResult]:
    """Run all prompt_edit_skills from pack hooks."""
    hooks = pack_json.get("prompt_hooks") or {}
    skills = hooks.get("prompt_edit_skills") or []
    if not isinstance(skills, list):
        return []
    return [
        run_craft_skill(
            name,
            prose=prose,
            twist_title=twist_title,
            open_checklist_codes=open_checklist_codes,
            has_misdirection_label=has_misdirection_label,
        )
        for name in skills
        if isinstance(name, str)
    ]
