"use client";

import type { FactClaimCategory } from "@/lib/api/types";
import { ALL_FACT_CATEGORIES } from "@/lib/fact-check-utils";
import { useTranslations } from "@/lib/i18n/use-translations";

interface FactCheckCategorySelectProps {
  value: FactClaimCategory[];
  onChange: (categories: FactClaimCategory[]) => void;
  disabled?: boolean;
  modeOff?: boolean;
}

export function FactCheckCategorySelect({
  value,
  onChange,
  disabled,
  modeOff,
}: FactCheckCategorySelectProps) {
  const t = useTranslations();
  const toggle = (category: FactClaimCategory) => {
    const base = [...value];
    if (base.includes(category)) {
      onChange(base.filter((c) => c !== category));
    } else {
      onChange([...base, category]);
    }
  };

  return (
    <fieldset className="space-y-2" disabled={disabled || modeOff}>
      <legend className="text-sm font-medium text-sf-text-primary">
        {t("factCheck.settings.categories")}
      </legend>
      <div className="grid gap-2 sm:grid-cols-2">
        {ALL_FACT_CATEGORIES.map((category) => (
          <label key={category} className="flex cursor-pointer items-center gap-2 text-sm">
            <input
              type="checkbox"
              checked={value.includes(category)}
              onChange={() => toggle(category)}
            />
            {t(`factCheck.category.${category}`)}
          </label>
        ))}
      </div>
    </fieldset>
  );
}
