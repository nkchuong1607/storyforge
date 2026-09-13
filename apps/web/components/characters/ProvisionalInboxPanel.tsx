"use client";

import type { Character, CharacterProvisional } from "@/lib/api/types";
import { useTranslations } from "@/lib/i18n/use-translations";

interface ProvisionalInboxPanelProps {
  provisionals: CharacterProvisional[];
  characters: Character[];
  onMerge: (provisional: CharacterProvisional) => void;
  onPromoteNew: (provisional: CharacterProvisional) => void;
  onReject: (provisional: CharacterProvisional) => void;
  onClose?: () => void;
}

function suggestedName(
  provisional: CharacterProvisional,
  characters: Character[],
): string | null {
  if (!provisional.matched_character_id) return null;
  return (
    characters.find((c) => c.id === provisional.matched_character_id)?.display_name ?? null
  );
}

export function ProvisionalInboxPanel({
  provisionals,
  characters,
  onMerge,
  onPromoteNew,
  onReject,
  onClose,
}: ProvisionalInboxPanelProps) {
  const t = useTranslations();

  return (
    <aside className="rounded-xl border border-slate-200 bg-white">
      <div className="flex items-center justify-between border-b border-slate-200 px-4 py-3">
        <h2 className="text-sm font-semibold text-slate-900">{t("characters.inbox")}</h2>
        {onClose ? (
          <button
            type="button"
            onClick={onClose}
            aria-label={t("characters.inboxCloseAria")}
            className="text-slate-400 hover:text-slate-600"
          >
            ×
          </button>
        ) : null}
      </div>
      {provisionals.length === 0 ? (
        <p className="px-4 py-6 text-sm text-slate-500">{t("characters.inboxEmptyPending")}</p>
      ) : (
        <ul className="divide-y divide-slate-100">
          {provisionals.map((provisional) => {
            const matchName = suggestedName(provisional, characters);
            return (
              <li key={provisional.id} className="px-4 py-3">
                <div className="flex items-start justify-between gap-3">
                  <div className="min-w-0">
                    <p className="font-medium text-slate-900">{provisional.mention_text}</p>
                    <p className="mt-1 truncate text-xs text-slate-500" title={provisional.snippet}>
                      {provisional.snippet}
                    </p>
                    <p className="mt-1 text-xs text-slate-500">
                      {t("characters.inboxChapter", { number: provisional.chapter_number })}
                    </p>
                    {matchName ? (
                      <p className="mt-1 text-xs text-indigo-600">
                        {t("characters.inboxSuggestion")} {matchName}
                      </p>
                    ) : null}
                  </div>
                  <div className="flex shrink-0 flex-col gap-1">
                    <button
                      type="button"
                      onClick={() => onMerge(provisional)}
                      className="rounded border border-indigo-300 px-2 py-1 text-xs font-medium text-indigo-700 hover:bg-indigo-50"
                    >
                      {t("characters.mergeAction")}
                    </button>
                    <button
                      type="button"
                      onClick={() => onPromoteNew(provisional)}
                      className="rounded border border-emerald-300 px-2 py-1 text-xs font-medium text-emerald-700 hover:bg-emerald-50"
                    >
                      {t("characters.promoteNew")}
                    </button>
                    <button
                      type="button"
                      onClick={() => onReject(provisional)}
                      className="rounded border border-slate-300 px-2 py-1 text-xs font-medium text-slate-600 hover:bg-slate-50"
                    >
                      {t("characters.reject")}
                    </button>
                  </div>
                </div>
              </li>
            );
          })}
        </ul>
      )}
    </aside>
  );
}
