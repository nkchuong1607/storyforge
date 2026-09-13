"use client";

import type { PromptEditProvider } from "@/lib/api/types";
import { useTranslations } from "@/lib/i18n/use-translations";

interface PromptEditPanelHeaderProps {
  provider: PromptEditProvider;
}

export function PromptEditPanelHeader({ provider }: PromptEditPanelHeaderProps) {
  const t = useTranslations();

  return (
    <div className="mb-3 flex items-center justify-between">
      <h3 className="text-sm font-semibold text-slate-900">{t("editor.promptEdit.title")}</h3>
      <span
        className={`rounded-full px-2 py-0.5 text-xs font-medium ${
          provider === "fake" ? "bg-emerald-100 text-emerald-700" : "bg-indigo-100 text-indigo-700"
        }`}
      >
        {provider}
      </span>
    </div>
  );
}
