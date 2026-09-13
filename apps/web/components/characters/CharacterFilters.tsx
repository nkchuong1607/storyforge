"use client";

import type { CharacterStatus, CharacterTier } from "@/lib/api/types";
import { useLabelHelpers } from "@/lib/labels";
import { useTranslations } from "@/lib/i18n/use-translations";

export interface CharacterFilterValues {
  tier: "" | CharacterTier;
  status: "" | CharacterStatus;
  q: string;
}

interface CharacterFiltersProps {
  values: CharacterFilterValues;
  onChange: (values: CharacterFilterValues) => void;
}

const TIERS: CharacterTier[] = [0, 1, 2, 3];
const STATUSES: CharacterStatus[] = ["established", "provisional", "archived"];

export function CharacterFilters({ values, onChange }: CharacterFiltersProps) {
  const t = useTranslations();
  const labels = useLabelHelpers(t);

  return (
    <div className="mb-4 flex flex-wrap gap-3">
      <label className="flex flex-col gap-1 text-xs font-medium text-slate-500">
        {t("characters.tier")}
        <select
          aria-label={t("characters.filterTier")}
          value={values.tier === "" ? "" : String(values.tier)}
          onChange={(event) =>
            onChange({
              ...values,
              tier: event.target.value === "" ? "" : (Number(event.target.value) as CharacterTier),
            })
          }
          className="rounded-lg border border-slate-300 bg-white px-3 py-2 text-sm text-slate-900"
        >
          <option value="">{t("characters.filterAll")}</option>
          {TIERS.map((tier) => (
            <option key={tier} value={tier}>
              {labels.characterTier(tier)}
            </option>
          ))}
        </select>
      </label>
      <label className="flex flex-col gap-1 text-xs font-medium text-slate-500">
        {t("characters.status")}
        <select
          aria-label={t("characters.filterStatus")}
          value={values.status}
          onChange={(event) =>
            onChange({
              ...values,
              status: event.target.value as CharacterFilterValues["status"],
            })
          }
          className="rounded-lg border border-slate-300 bg-white px-3 py-2 text-sm text-slate-900"
        >
          <option value="">{t("characters.filterActive")}</option>
          {STATUSES.map((status) => (
            <option key={status} value={status}>
              {labels.characterStatus(status)}
            </option>
          ))}
        </select>
      </label>
      <label className="min-w-[220px] flex-1 flex-col gap-1 text-xs font-medium text-slate-500 sm:flex">
        {t("common.search")}
        <input
          aria-label={t("characters.searchLabel")}
          type="search"
          placeholder={t("characters.searchPlaceholder")}
          value={values.q}
          onChange={(event) => onChange({ ...values, q: event.target.value })}
          className="rounded-lg border border-slate-300 bg-white px-3 py-2 text-sm text-slate-900"
        />
      </label>
    </div>
  );
}
