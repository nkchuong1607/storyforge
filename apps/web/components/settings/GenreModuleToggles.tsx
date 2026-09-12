"use client";

import type { GenreRulePack } from "@/lib/api/types";

interface GenreModuleTogglesProps {
  pack: GenreRulePack;
  onChange: (modules: NonNullable<GenreRulePack["modules"]>) => void;
}

const MODULE_KEYS = [
  { key: "power_system" as const, label: "Power System" },
  { key: "foreshadow" as const, label: "Foreshadow / Twist" },
  { key: "psychology" as const, label: "Psychology / OOC" },
  { key: "timeline" as const, label: "Timeline" },
];

export function GenreModuleToggles({ pack, onChange }: GenreModuleTogglesProps) {
  const modules = pack.modules ?? {};

  const toggle = (key: keyof NonNullable<GenreRulePack["modules"]>, enabled: boolean) => {
    onChange({
      ...modules,
      [key]: { enabled },
    });
  };

  return (
    <div>
      <h4 className="mb-2 text-sm font-semibold text-slate-900">Modules</h4>
      <div className="grid gap-2 sm:grid-cols-2">
        {MODULE_KEYS.map(({ key, label }) => (
          <label key={key} className="flex items-center gap-2 rounded-lg border border-slate-200 p-3 text-sm">
            <input
              type="checkbox"
              checked={modules[key]?.enabled ?? false}
              onChange={(e) => toggle(key, e.target.checked)}
            />
            {label}
          </label>
        ))}
      </div>
    </div>
  );
}
