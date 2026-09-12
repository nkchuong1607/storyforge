"use client";

import type { PsycheArcFlags } from "@/lib/api/types";
import { TagListEditor } from "./TagListEditor";

interface ArcFlagsPanelProps {
  arcFlags: PsycheArcFlags;
  onChange: (flags: PsycheArcFlags) => void;
}

export function ArcFlagsPanel({ arcFlags, onChange }: ArcFlagsPanelProps) {
  const beats = arcFlags.expected_arc_beats ?? [];

  return (
    <div className="space-y-4 rounded-lg border border-slate-200 bg-slate-50 p-4">
      <h3 className="text-sm font-semibold text-slate-900">Arc flags</h3>
      <label className="flex items-center gap-2 text-sm text-slate-700">
        <input
          type="checkbox"
          checked={arcFlags.allow_moral_break ?? false}
          onChange={(event) =>
            onChange({ ...arcFlags, allow_moral_break: event.target.checked })
          }
        />
        Cho phép moral break
      </label>
      <TagListEditor
        label="Expected arc beats"
        values={beats}
        onChange={(values) => onChange({ ...arcFlags, expected_arc_beats: values })}
        placeholder="Thêm arc beat"
      />
      <div>
        <label htmlFor="current-arc-beat" className="block text-sm font-medium text-slate-700">
          Current arc beat
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
