"use client";

import { useTranslations } from "@/lib/i18n/use-translations";

export function FactCheckPanelHeader() {
  const t = useTranslations();
  return (
    <header className="mb-4">
      <h2 className="text-xl font-semibold text-sf-text-primary">{t("factCheck.panel.title")}</h2>
      <p className="mt-1 text-sm text-sf-text-secondary">{t("factCheck.panel.subtitle")}</p>
    </header>
  );
}
