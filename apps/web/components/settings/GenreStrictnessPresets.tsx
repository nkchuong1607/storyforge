"use client";

import type { GenreRulePack, GenreStrictness } from "@/lib/api/types";
import { STRICTNESS_OPTIONS } from "@/lib/genre-utils";

interface GenreStrictnessPresetsProps {
  pack: GenreRulePack;
  onChange: (strictness: NonNullable<GenreRulePack["strictness"]>) => void;
}

const STRICTNESS_KEYS = [
  { key: "foreshadow" as const, label: "Foreshadow" },
  { key: "power" as const, label: "Power" },
  { key: "psychology" as const, label: "Psychology" },
];

export function GenreStrictnessPresets({ pack, onChange }: GenreStrictnessPresetsProps) {
  const strictness = pack.strictness ?? {};

  const update = (key: keyof NonNullable<GenreRulePack["strictness"]>, value: GenreStrictness) => {
    onChange({ ...strictness, [key]: value });
  };

  return (
    <div>
      <h4 className="mb-2 text-sm font-semibold text-slate-900">Strictness</h4>
      <div className="grid gap-3 sm:grid-cols-3">
        {STRICTNESS_KEYS.map(({ key, label }) => (
          <label key={key} className="text-sm">
            <span className="mb-1 block text-slate-600">{label}</span>
            <select
              value={strictness[key] ?? "standard"}
              onChange={(e) => update(key, e.target.value as GenreStrictness)}
              className="w-full rounded-lg border border-slate-200 px-2 py-1.5"
            >
              {STRICTNESS_OPTIONS.map((opt) => (
                <option key={opt} value={opt}>
                  {opt}
                </option>
              ))}
            </select>
          </label>
        ))}
      </div>
    </div>
  );
}
