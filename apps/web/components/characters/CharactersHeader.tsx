"use client";

import { useTranslations } from "@/lib/i18n/use-translations";

interface CharactersHeaderProps {
  pendingCount: number;
  showInbox: boolean;
  onToggleInbox: () => void;
  onAdd: () => void;
}

export function CharactersHeader({
  pendingCount,
  showInbox,
  onToggleInbox,
  onAdd,
}: CharactersHeaderProps) {
  const t = useTranslations();

  return (
    <div className="mb-4 flex flex-wrap items-center justify-between gap-3">
      <div>
        <h1 className="text-xl font-bold text-slate-900">{t("characters.title")}</h1>
        <p className="mt-1 text-sm text-slate-600">{t("characters.subtitle")}</p>
      </div>
      <div className="flex flex-wrap gap-2">
        <button
          type="button"
          onClick={onToggleInbox}
          className={`rounded-lg border px-4 py-2 text-sm font-medium ${
            showInbox
              ? "border-indigo-300 bg-indigo-50 text-indigo-700"
              : "border-slate-300 bg-white text-slate-700 hover:bg-slate-50"
          }`}
        >
          {t("characters.inbox")}
          {pendingCount > 0 ? (
            <span className="ml-2 rounded-full bg-indigo-600 px-2 py-0.5 text-xs text-white">
              {pendingCount}
            </span>
          ) : null}
        </button>
        <button
          type="button"
          onClick={onAdd}
          className="rounded-lg bg-indigo-600 px-4 py-2 text-sm font-medium text-white hover:bg-indigo-700"
        >
          + {t("common.add")}
        </button>
      </div>
    </div>
  );
}
