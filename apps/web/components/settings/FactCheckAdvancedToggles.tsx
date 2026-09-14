"use client";

import { useTranslations } from "@/lib/i18n/use-translations";

interface FactCheckAdvancedTogglesProps {
  blocksSettle: boolean;
  autoRun: boolean;
  includeResearch: boolean;
  onBlocksSettleChange: (value: boolean) => void;
  onAutoRunChange: (value: boolean) => void;
  onIncludeResearchChange: (value: boolean) => void;
  disabled?: boolean;
}

export function FactCheckAdvancedToggles({
  blocksSettle,
  autoRun,
  includeResearch,
  onBlocksSettleChange,
  onAutoRunChange,
  onIncludeResearchChange,
  disabled,
}: FactCheckAdvancedTogglesProps) {
  const t = useTranslations();

  return (
    <fieldset className="space-y-3" disabled={disabled}>
      <legend className="text-sm font-medium text-sf-text-primary">{t("factCheck.settings.advanced")}</legend>
      <label className="flex cursor-pointer items-start gap-2 text-sm">
        <input
          type="checkbox"
          checked={blocksSettle}
          onChange={(e) => onBlocksSettleChange(e.target.checked)}
          className="mt-0.5"
        />
        <span>
          {t("factCheck.settings.blocks_settle")}
          {blocksSettle ? (
            <span className="mt-1 block text-xs text-amber-700">{t("factCheck.settings.blocks_settle_warn")}</span>
          ) : null}
        </span>
      </label>
      <label className="flex cursor-pointer items-center gap-2 text-sm">
        <input type="checkbox" checked={autoRun} onChange={(e) => onAutoRunChange(e.target.checked)} />
        {t("factCheck.settings.auto_run")}
      </label>
      <label className="flex cursor-pointer items-center gap-2 text-sm">
        <input
          type="checkbox"
          checked={includeResearch}
          onChange={(e) => onIncludeResearchChange(e.target.checked)}
        />
        {t("factCheck.settings.include_research")}
      </label>
    </fieldset>
  );
}
