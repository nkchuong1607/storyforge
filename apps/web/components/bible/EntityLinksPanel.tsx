"use client";

import { useTranslations } from "@/lib/i18n/use-translations";

export function EntityLinksPanel() {
  const t = useTranslations();

  return (
    <div className="rounded-xl border border-slate-200 bg-white p-4 shadow-sm">
      <h3 className="text-sm font-semibold text-slate-900">{t("bible.entityLinks.title")}</h3>
      <p className="mt-3 text-sm text-slate-500">{t("bible.entityLinks.empty")}</p>
    </div>
  );
}
