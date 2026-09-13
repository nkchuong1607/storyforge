"use client";

import type { PsycheArcFlags } from "@/lib/api/types";
import { useTranslations } from "@/lib/i18n/use-translations";
import { TagListEditor } from "./TagListEditor";

interface ArcFlagsPanelProps {
  arcFlags: PsycheArcFlags;
  onChange: (flags: PsycheArcFlags) => void;
}

export function ArcFlagsPanel({ arcFlags, onChange }: ArcFlagsPanelProps) {
  const t = useTranslations();
  const beats = arcFlags.expected_arc_beats ?? [];

  return (
    <div className="space-y-4 rounded-lg border border-slate-200 bg-slate-50 p-4">
      <h3 className="text-sm font-semibold text-slate-900">{t("psych.arcFlags.title")}</h3>
      <label className="flex items-center gap-2 text-sm text-slate-700">
        <input
          type="checkbox"
          checked={arcFlags.allow_moral_break ?? false}
          onChange={(event) =>
            onChange({ ...arcFlags, allow_moral_break: event.target.checked })
          }
        />
        {t("psych.arcFlags.allowMoralBreak")}
      </label>
      <TagListEditor
        label={t("psych.arcFlags.expectedBeats")}
        values={beats}
        onChange={(values) => onChange({ ...arcFlags, expected_arc_beats: values })}
        placeholder={t("psych.arcFlags.beatPlaceholder")}
      />
      <div>
        <label htmlFor="current-arc-beat" className="block text-sm font-medium text-slate-700">
          {t("psych.arcFlags.currentBeat")}
        </label>
        <input
          id="current-arc-beat"
          type="text"
          value={arcFlags.current_arc_beat ?? ""}
          onChange={(event) =>
            onChange({ ...arcFlags, current_arc_beat: event.target.value || null })
          }
          className="mt-1 w-full rounded-lg border border-slate-300 px-3 py-2 text-sm"
        />
      </div>
    </div>
  );
}
