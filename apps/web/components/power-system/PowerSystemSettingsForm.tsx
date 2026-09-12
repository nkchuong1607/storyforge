"use client";

import type { PowerSystemSettings, PowerSystemSettingsUpdate } from "@/lib/api/types";
import { antiCreepTip } from "@/lib/power-utils";

interface PowerSystemSettingsFormProps {
  settings: PowerSystemSettings;
  onChange: (patch: PowerSystemSettingsUpdate) => void;
  saving?: boolean;
}

export function PowerSystemSettingsForm({
  settings,
  onChange,
  saving,
}: PowerSystemSettingsFormProps) {
  return (
    <div className="rounded-xl border border-slate-200 bg-white p-4 shadow-sm">
      <h3 className="mb-3 text-sm font-semibold text-slate-900">Cài đặt hệ thống</h3>
      <div className="grid gap-4 sm:grid-cols-2 lg:grid-cols-4">
        <label className="flex items-center gap-2 text-sm">
          <input
            type="checkbox"
            checked={settings.enabled}
            onChange={(e) => onChange({ enabled: e.target.checked })}
            disabled={saving}
          />
          Bật power system
        </label>
        <label className="text-sm">
          <span className="mb-1 block text-slate-600">Priority gap</span>
          <input
            type="number"
            min={1}
            max={10}
            value={settings.priority_gap}
            onChange={(e) => onChange({ priority_gap: Number(e.target.value) })}
            disabled={saving}
            className="w-full rounded-lg border border-slate-200 px-2 py-1"
          />
        </label>
        <label className="text-sm">
          <span className="mb-1 block text-slate-600">Max rank jump / chương</span>
          <input
            type="number"
            min={0}
            max={5}
            value={settings.max_rank_jump_per_chapter}
            onChange={(e) => onChange({ max_rank_jump_per_chapter: Number(e.target.value) })}
            disabled={saving}
            className="w-full rounded-lg border border-slate-200 px-2 py-1"
          />
        </label>
        <label className="flex items-center gap-2 text-sm">
          <input
            type="checkbox"
            checked={settings.require_breakthrough_event}
            onChange={(e) => onChange({ require_breakthrough_event: e.target.checked })}
            disabled={saving}
          />
          Yêu cầu breakthrough
        </label>
      </div>
      <p className="mt-3 rounded-lg bg-violet-50 px-3 py-2 text-xs text-violet-800">
        {antiCreepTip(settings.priority_gap, settings.max_rank_jump_per_chapter)}
      </p>
    </div>
  );
}
