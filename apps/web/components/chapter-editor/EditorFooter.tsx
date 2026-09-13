"use client";

import { formatDate } from "@/lib/labels";
import { useLocale, useTranslations } from "@/lib/i18n/use-translations";

interface EditorFooterProps {
  wordCount: number;
  updatedAt: string;
  saveState: "idle" | "saving" | "saved";
}

export function EditorFooter({ wordCount, updatedAt, saveState }: EditorFooterProps) {
  const t = useTranslations();
  const { locale } = useLocale();
  const saveLabel =
    saveState === "saving" ? t("common.saving") : saveState === "saved" ? t("common.saved") : "";

  return (
    <footer className="flex items-center justify-between border-t border-slate-200 pt-3 text-xs text-slate-500">
      <span>
        {t("editor.wordCount", {
          count: wordCount.toLocaleString(locale === "vi" ? "vi-VN" : "en-US"),
        })}
      </span>
      <span>{t("editor.updatedAt", { date: formatDate(updatedAt, locale) })}</span>
      {saveLabel ? <span className="font-medium text-indigo-600">{saveLabel}</span> : <span />}
    </footer>
  );
}
