"use client";

import { useState } from "react";
import type { ProjectRealitySettings, ProjectRealitySettingsUpdate } from "@/lib/api/types";
import { ALL_FACT_CATEGORIES, validateRealitySettings } from "@/lib/fact-check-utils";
import { useTranslations } from "@/lib/i18n/use-translations";
import { Button } from "@/components/ui/Button";
import { FactCheckAdvancedToggles } from "./FactCheckAdvancedToggles";
import { FactCheckCategorySelect } from "./FactCheckCategorySelect";
import { RealityAnchorsModeRadio } from "./RealityAnchorsModeRadio";

interface RealitySettingsSectionProps {
  settings: ProjectRealitySettings;
  saving: boolean;
  onSave: (update: ProjectRealitySettingsUpdate) => Promise<void>;
}

export function RealitySettingsSection({ settings, saving, onSave }: RealitySettingsSectionProps) {
  const t = useTranslations();
  const [draft, setDraft] = useState({
    ...settings,
    enabled_categories:
      settings.enabled_categories.length === 0
        ? [...ALL_FACT_CATEGORIES]
        : settings.enabled_categories,
  });
  const [validationError, setValidationError] = useState<string | null>(null);

  const handleSave = async () => {
    const err = validateRealitySettings(draft.reality_anchors, draft.enabled_categories);
    if (err) {
      setValidationError(t(err));
      return;
    }
    setValidationError(null);
    const categoriesForApi =
      draft.enabled_categories.length === ALL_FACT_CATEGORIES.length
        ? []
        : draft.enabled_categories;
    await onSave({
      reality_anchors: draft.reality_anchors,
      enabled_categories: categoriesForApi,
      fact_check_blocks_settle: draft.fact_check_blocks_settle,
      auto_run_on_save: draft.auto_run_on_save,
      include_research_notes: draft.include_research_notes,
    });
  };

  return (
    <section className="rounded-[var(--sf-radius-lg)] border border-sf-border bg-sf-bg-surface p-6">
      <h2 className="mb-4 text-lg font-semibold text-sf-text-primary">{t("factCheck.settings.title")}</h2>

      {validationError ? (
        <p className="mb-4 text-sm text-sf-danger" role="alert">
          {validationError}
        </p>
      ) : null}

      <div className="space-y-6">
        <RealityAnchorsModeRadio
          value={draft.reality_anchors}
          onChange={(mode) => setDraft((prev) => ({ ...prev, reality_anchors: mode }))}
          disabled={saving}
        />

        <FactCheckCategorySelect
          value={draft.enabled_categories}
          onChange={(categories) => setDraft((prev) => ({ ...prev, enabled_categories: categories }))}
          disabled={saving}
          modeOff={draft.reality_anchors === "off"}
        />

        <FactCheckAdvancedToggles
          blocksSettle={draft.fact_check_blocks_settle}
          autoRun={draft.auto_run_on_save}
          includeResearch={draft.include_research_notes}
          onBlocksSettleChange={(v) => setDraft((prev) => ({ ...prev, fact_check_blocks_settle: v }))}
          onAutoRunChange={(v) => setDraft((prev) => ({ ...prev, auto_run_on_save: v }))}
          onIncludeResearchChange={(v) => setDraft((prev) => ({ ...prev, include_research_notes: v }))}
          disabled={saving || draft.reality_anchors === "off"}
        />
      </div>

      <div className="mt-6">
        <Button type="button" variant="primary" onClick={() => void handleSave()} disabled={saving}>
          {saving ? t("common.saving") : t("common.save")}
        </Button>
      </div>
    </section>
  );
}
