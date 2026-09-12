"use client";

import type { CharacterStatus, CharacterTier } from "@/lib/api/types";
import { CHARACTER_STATUS_LABELS, CHARACTER_TIER_LABELS } from "@/lib/labels";

export interface CharacterFilterValues {
  tier: "" | CharacterTier;
  status: "" | CharacterStatus;
  q: string;
}

interface CharacterFiltersProps {
  values: CharacterFilterValues;
  onChange: (values: CharacterFilterValues) => void;
}

export function CharacterFilters({ values, onChange }: CharacterFiltersProps) {
  return (
    <div className="mb-4 flex flex-wrap gap-3">
      <label className="flex flex-col gap-1 text-xs font-medium text-slate-500">
        Hạng
        <select
          aria-label="Lọc theo hạng"
          value={values.tier === "" ? "" : String(values.tier)}
          onChange={(event) =>
            onChange({
              ...values,
              tier: event.target.value === "" ? "" : (Number(event.target.value) as CharacterTier),
            })
          }
          className="rounded-lg border border-slate-300 bg-white px-3 py-2 text-sm text-slate-900"
        >
          <option value="">Tất cả</option>
          {(Object.keys(CHARACTER_TIER_LABELS) as unknown as CharacterTier[]).map((tier) => (
            <option key={tier} value={tier}>
              {CHARACTER_TIER_LABELS[tier]}
            </option>
          ))}
        </select>
      </label>
      <label className="flex flex-col gap-1 text-xs font-medium text-slate-500">
        Trạng thái
        <select
          aria-label="Lọc theo trạng thái"
          value={values.status}
          onChange={(event) =>
            onChange({
              ...values,
              status: event.target.value as CharacterFilterValues["status"],
            })
          }
          className="rounded-lg border border-slate-300 bg-white px-3 py-2 text-sm text-slate-900"
        >
          <option value="">Đang hoạt động</option>
          {(Object.keys(CHARACTER_STATUS_LABELS) as CharacterStatus[]).map((status) => (
            <option key={status} value={status}>
              {CHARACTER_STATUS_LABELS[status]}
            </option>
          ))}
        </select>
      </label>
      <label className="min-w-[220px] flex-1 flex-col gap-1 text-xs font-medium text-slate-500 sm:flex">
        Tìm kiếm
        <input
          aria-label="Tìm kiếm nhân vật"
          type="search"
          placeholder="Tìm kiếm nhân vật…"
          value={values.q}
          onChange={(event) => onChange({ ...values, q: event.target.value })}
          className="rounded-lg border border-slate-300 bg-white px-3 py-2 text-sm text-slate-900"
        />
      </label>
    </div>
  );
}
