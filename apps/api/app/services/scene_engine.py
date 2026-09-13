"""Scene engine settings and lint service."""

from __future__ import annotations

from datetime import UTC, datetime

from sqlalchemy.ext.asyncio import AsyncSession

from app.exceptions import (
    InvalidSceneTypeError,
    InvalidStakesLevelError,
    SceneLLMAuditorError,
    SceneMissingOutcomeError,
)
from app.models.chapter import Chapter
from app.models.enums import ContinuityResult, ContinuitySeverity, SceneType
from app.models.project import Project
from app.models.scene_beat import SceneBeat
from app.repositories.beat import BeatRepository
from app.repositories.character import CharacterRepository
from app.repositories.scene_engine import SceneEngineRepository
from app.repositories.stakes import StakesRepository
from app.schemas.continuity import ContinuityIssue
from app.schemas.scene_engine import (
    SceneEngineSettings as SceneEngineSettingsSchema,
)
from app.schemas.scene_engine import (
    SceneEngineSettingsUpdateRequest,
    SceneLintResponse,
)
from app.services.continuity.scene import run_scene_structure_checks
from app.services.genre_defaults import merged_genre_pack


class SceneEngineService:
    MAX_CONTEXT_BEATS = 12

    def __init__(self, session: AsyncSession) -> None:
        self.session = session
        self.settings_repo = SceneEngineRepository(session)
        self.beats = BeatRepository(session)
        self.characters = CharacterRepository(session)
        self.stakes = StakesRepository(session)

    async def get_settings(self, project: Project) -> SceneEngineSettingsSchema:
        row = await self.settings_repo.ensure_settings(project.id)
        return SceneEngineSettingsSchema.model_validate(row)

    async def update_settings(
        self, project: Project, payload: SceneEngineSettingsUpdateRequest
    ) -> SceneEngineSettingsSchema:
        row = await self.settings_repo.ensure_settings(project.id)
        data = payload.model_dump(exclude_unset=True)
        for key, value in data.items():
            setattr(row, key, value)
        row.updated_at = datetime.now(UTC)
        await self.session.flush()
        await self.session.refresh(row)
        return SceneEngineSettingsSchema.model_validate(row)

    def _validate_scene_type(self, scene_type: str | SceneType | None) -> None:
        if scene_type is None:
            return
        value = scene_type.value if isinstance(scene_type, SceneType) else scene_type
        try:
            SceneType(value)
        except ValueError as exc:
            raise InvalidSceneTypeError(str(value)) from exc

    def _validate_stakes_level(self, level: int | None) -> None:
        if level is not None and not 0 <= level <= 5:
            raise InvalidStakesLevelError()

    async def run_scene_lint(self, project: Project, chapter: Chapter) -> SceneLintResponse:
        settings = await self.settings_repo.ensure_settings(project.id)
        beat_rows = await self.beats.list_for_chapter(chapter.id)
        characters = await self.characters.list_all_for_project(project.id)
        stakes_entries = await self.stakes.list_entries_for_act(
            project.id,
            (await self._act_number(project, chapter.number)),
        )
        genre_pack = merged_genre_pack(project.genre_rule_pack_json or {}, project.genre_profile)

        if settings.llm_auditor_enabled:
            import os

            if os.getenv("STORYFORGE_SCENE_LLM_AUDITOR", "").lower() == "true":
                try:
                    from app.services.continuity.scene_llm_stub import run_scene_llm_auditor

                    llm_issues = await run_scene_llm_auditor(beat_rows, chapter.id)
                except Exception as exc:
                    raise SceneLLMAuditorError(str(exc)) from exc
            else:
                llm_issues = []
        else:
            llm_issues = []

        raw = run_scene_structure_checks(
            beats=beat_rows,
            chapter_number=chapter.number,
            settings=settings,
            characters=characters,
            genre_pack=genre_pack,
            stakes_entries=stakes_entries,
        )
        raw.extend(llm_issues)

        issues = [issue.to_dict() for issue in raw]
        fail_count = sum(1 for i in issues if i["severity"] == ContinuitySeverity.FAIL.value)
        warn_count = sum(1 for i in issues if i["severity"] == ContinuitySeverity.WARN.value)
        pass_count = max(0, len(beat_rows) - fail_count - warn_count)

        if fail_count > 0:
            result = ContinuityResult.FAIL
        elif warn_count > 0:
            result = ContinuityResult.WARN
        else:
            result = ContinuityResult.PASS

        return SceneLintResponse(
            chapter_id=chapter.id,
            result=result,
            issues=[ContinuityIssue.model_validate(i) for i in issues],
            stats={"fail": fail_count, "warn": warn_count, "pass": pass_count},
        )

    async def _act_number(self, project: Project, chapter_number: int) -> int:
        from app.services.continuity.stakes import resolve_act_for_chapter

        settings = await self.stakes.ensure_settings(project.id)
        act_number, _, _ = resolve_act_for_chapter(chapter_number, settings)
        return act_number

    def validate_beat_fields(
        self,
        *,
        completed: bool | None,
        outcome: str | None,
        settings_row,
        require_outcome: bool = True,
    ) -> None:
        if completed and require_outcome and settings_row.require_outcome_on_complete:
            if outcome is not None and not outcome.strip():
                raise SceneMissingOutcomeError()
            if outcome is None:
                raise SceneMissingOutcomeError()

    def apply_beat_defaults(self, beat: SceneBeat, payload_dict: dict) -> None:
        if "scene_type" in payload_dict:
            self._validate_scene_type(payload_dict["scene_type"])
        if "stakes_level" in payload_dict:
            self._validate_stakes_level(payload_dict["stakes_level"])
