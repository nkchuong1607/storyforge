"use client";

import type { BibleVersionSummary } from "@/lib/api/types";
import { formatDate } from "@/lib/labels";
import { useLocale } from "@/lib/i18n/use-translations";
import { useTranslations } from "@/lib/i18n/use-translations";

interface VersionHistoryPanelProps {
  versions: BibleVersionSummary[];
  loading?: boolean;
}

export function VersionHistoryPanel({ versions, loading }: VersionHistoryPanelProps) {
  const t = useTranslations();
  const { locale } = useLocale();

  return (
    <div className="rounded-xl border border-slate-200 bg-white p-4 shadow-sm">
      <h3 className="text-sm font-semibold text-slate-900">{t("bible.versionHistory.title")}</h3>
      {loading ? (
        <p className="mt-3 text-sm text-slate-500">{t("common.loading")}</p>
      ) : versions.length === 0 ? (
        <p className="mt-3 text-sm text-slate-500">{t("bible.versionHistory.empty")}</p>
      ) : (
        <ul className="mt-3 space-y-2">
          {versions.map((v) => (
            <li
              key={v.version}
              className="rounded-lg border border-slate-100 bg-slate-50 px-3 py-2 text-sm"
            >
              <span className="font-medium text-slate-900">v{v.version}</span>
              <span className="ml-2 text-xs text-slate-500">{formatDate(v.created_at, locale)}</span>
              {v.entry_count !== undefined ? (
                <span className="mt-1 block text-xs text-slate-500">
                  {t("bible.versionHistory.entryCount", { count: v.entry_count })}
                </span>
              ) : null}
            </li>
          ))}
        </ul>
      )}
      <button
        type="button"
        disabled
        className="mt-4 w-full cursor-not-allowed rounded-lg border border-slate-200 bg-slate-50 px-3 py-2 text-sm text-slate-400"
        title={t("bible.versionHistory.settleTitle")}
      >
        {t("bible.versionHistory.settlePhase2")}
      </button>
    </div>
  );
}
