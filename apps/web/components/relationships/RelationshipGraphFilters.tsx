"use client";

import type { RelationType } from "@/lib/api/types";
import { useTranslations } from "@/lib/i18n/use-translations";
import { RELATION_TYPES } from "@/lib/relationship-utils";
import { Button } from "@/components/ui/Button";

interface RelationshipGraphFiltersProps {
  actNumber: number | "";
  minIntensity: number;
  relationTypes: RelationType[];
  onActChange: (act: number | "") => void;
  onMinIntensityChange: (value: number) => void;
  onRelationTypesChange: (types: RelationType[]) => void;
  onApply: () => void;
}

export function RelationshipGraphFilters({
  actNumber,
  minIntensity,
  relationTypes,
  onActChange,
  onMinIntensityChange,
  onRelationTypesChange,
  onApply,
}: RelationshipGraphFiltersProps) {
  const t = useTranslations();

  const toggleType = (type: RelationType) => {
    if (relationTypes.includes(type)) {
      onRelationTypesChange(relationTypes.filter((t) => t !== type));
    } else {
      onRelationTypesChange([...relationTypes, type]);
    }
  };

  return (
    <div className="flex flex-wrap items-end gap-4 rounded-xl border border-slate-200 bg-white p-4">
      <div>
        <label htmlFor="rel-act" className="mb-1 block text-xs font-medium text-slate-600">
          {t("relationships.filters.act")}
        </label>
        <select
          id="rel-act"
          value={actNumber}
          onChange={(e) => onActChange(e.target.value ? Number(e.target.value) : "")}
          className="rounded-lg border border-slate-200 px-2 py-1 text-sm"
        >
          <option value="">{t("relationships.filters.allActs")}</option>
          {[1, 2, 3].map((n) => (
            <option key={n} value={n}>
              {t("stakes.act.label", { n })}
            </option>
          ))}
        </select>
      </div>
      <div>
        <label htmlFor="rel-intensity" className="mb-1 block text-xs font-medium text-slate-600">
          {t("relationships.intensity.label")}
        </label>
        <input
          id="rel-intensity"
          type="range"
          min={-5}
          max={5}
          value={minIntensity}
          onChange={(e) => onMinIntensityChange(Number(e.target.value))}
          className="w-32"
        />
      </div>
      <div className="flex flex-wrap gap-1">
        {RELATION_TYPES.filter((t) => t !== "custom").map((type) => (
          <button
            key={type}
            type="button"
            onClick={() => toggleType(type)}
            className={`rounded-full px-2 py-0.5 text-xs ${
              relationTypes.includes(type)
                ? "bg-indigo-100 text-indigo-800"
                : "bg-slate-100 text-slate-600"
            }`}
          >
            {t(`relationships.types.${type}`)}
          </button>
        ))}
      </div>
      <Button type="button" size="sm" onClick={onApply}>
        {t("relationships.filters.apply")}
      </Button>
    </div>
  );
}
