"use client";

import { useState } from "react";
import type { GenreRulePack } from "@/lib/api/types";

interface GenreThresholdsFormProps {
  thresholds: Record<string, unknown>;
  onChange: (thresholds: Record<string, unknown>) => void;
}

export function GenreThresholdsForm({ thresholds, onChange }: GenreThresholdsFormProps) {
  const [open, setOpen] = useState(false);

  const updateNumber = (key: string, value: string) => {
    onChange({ ...thresholds, [key]: Number(value) });
  };

  return (
    <div className="rounded-lg border border-slate-200">
      <button
        type="button"
        onClick={() => setOpen((v) => !v)}
        className="flex w-full items-center justify-between px-4 py-3 text-sm font-medium text-slate-700"
      >
        Thresholds (advanced)
        <span>{open ? "▲" : "▼"}</span>
      </button>
      {open ? (
        <div className="grid gap-3 border-t border-slate-100 px-4 py-3 sm:grid-cols-2">
          <label className="text-sm">
            <span className="mb-1 block text-slate-600">Min plants default</span>
            <input
              type="number"
              min={0}
              value={Number(thresholds.foreshadow_min_plants_default ?? 1)}
              onChange={(e) => updateNumber("foreshadow_min_plants_default", e.target.value)}
              className="w-full rounded-lg border border-slate-200 px-2 py-1"
            />
          </label>
          <label className="text-sm">
            <span className="mb-1 block text-slate-600">Max rank jump / chương</span>
            <input
              type="number"
              min={0}
              value={Number(thresholds.power_max_rank_jump_per_chapter ?? 1)}
              onChange={(e) => updateNumber("power_max_rank_jump_per_chapter", e.target.value)}
              className="w-full rounded-lg border border-slate-200 px-2 py-1"
            />
          </label>
        </div>
      ) : null}
    </div>
  );
}
