"use client";

import type { SceneBeat, SceneType } from "@/lib/api/types";
import { useTranslations } from "@/lib/i18n/use-translations";
import { SCENE_TYPES } from "@/lib/scene-utils";
import { Textarea } from "@/components/ui/Input";

interface SceneBeatStructureFieldsProps {
  beat: SceneBeat;
  readOnly: boolean;
  characterOptions?: { id: string; name: string }[];
  onChange: (fields: Partial<SceneBeat>) => void;
  onBlur?: () => void;
}

export function SceneBeatStructureFields({
  beat,
  readOnly,
  characterOptions = [],
  onChange,
  onBlur,
}: SceneBeatStructureFieldsProps) {
  const t = useTranslations();

  return (
    <div className="mt-2 space-y-2 border-t border-slate-100 pt-2">
      <Textarea
        label={t("scene.fields.goal")}
        value={beat.goal ?? ""}
        readOnly={readOnly}
        rows={2}
        onChange={(e) => onChange({ goal: e.target.value })}
        onBlur={onBlur}
      />
      <Textarea
        label={t("scene.fields.conflict")}
        value={beat.conflict ?? ""}
        readOnly={readOnly}
        rows={2}
        onChange={(e) => onChange({ conflict: e.target.value })}
        onBlur={onBlur}
      />
      <Textarea
        label={t("scene.fields.outcome")}
        value={beat.outcome ?? ""}
        readOnly={readOnly}
        rows={2}
        onChange={(e) => onChange({ outcome: e.target.value })}
        onBlur={onBlur}
      />
      <div>
        <label className="mb-1 block text-xs font-medium text-slate-600">
          {t("scene.fields.stakes_level")}: {beat.stakes_level ?? 0}
        </label>
        <input
          type="range"
          min={0}
          max={5}
          value={beat.stakes_level ?? 0}
          disabled={readOnly}
          onChange={(e) => onChange({ stakes_level: Number(e.target.value) })}
          onBlur={onBlur}
          className="w-full"
          aria-label={t("scene.fields.stakes_level")}
        />
      </div>
      <div>
        <label htmlFor={`scene-type-${beat.id}`} className="mb-1 block text-xs font-medium text-slate-600">
          {t("scene.fields.scene_type")}
        </label>
        <select
          id={`scene-type-${beat.id}`}
          value={beat.scene_type ?? "scene"}
          disabled={readOnly}
          onChange={(e) => onChange({ scene_type: e.target.value as SceneType })}
          onBlur={onBlur}
          className="w-full rounded-lg border border-slate-200 px-2 py-1 text-sm"
        >
          {SCENE_TYPES.map((type) => (
            <option key={type} value={type}>
              {t(`scene.types.${type}`)}
            </option>
          ))}
        </select>
      </div>
      {characterOptions.length > 0 ? (
        <div>
          <label htmlFor={`pov-${beat.id}`} className="mb-1 block text-xs font-medium text-slate-600">
            POV
          </label>
          <select
            id={`pov-${beat.id}`}
            value={beat.pov_character_id ?? ""}
            disabled={readOnly}
            onChange={(e) =>
              onChange({ pov_character_id: e.target.value || null })
            }
            onBlur={onBlur}
            className="w-full rounded-lg border border-slate-200 px-2 py-1 text-sm"
          >
            <option value="">{t("scene.fields.pov_none")}</option>
            {characterOptions.map((c) => (
              <option key={c.id} value={c.id}>
                {c.name}
              </option>
            ))}
          </select>
        </div>
      ) : null}
    </div>
  );
}
