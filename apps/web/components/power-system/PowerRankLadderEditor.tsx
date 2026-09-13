"use client";

import type { PowerRank } from "@/lib/api/types";
import { validateRankMonotonic } from "@/lib/power-utils";
import { useTranslations } from "@/lib/i18n/use-translations";
import { PowerRankRow } from "./PowerRankRow";

interface PowerRankLadderEditorProps {
  ranks: PowerRank[];
  onUpdateRank: (rankId: string, displayName: string, constraints: string) => void;
  onAddRank: () => void;
  onSeedTemplate: () => void;
}

export function PowerRankLadderEditor({
  ranks,
  onUpdateRank,
  onAddRank,
  onSeedTemplate,
}: PowerRankLadderEditorProps) {
  const t = useTranslations();
  const validationError = validateRankMonotonic(ranks, t);
  const sorted = [...ranks].sort((a, b) => a.sort_order - b.sort_order);

  return (
    <div className="rounded-xl border border-slate-200 bg-white p-4 shadow-sm">
      <div className="mb-3 flex items-center justify-between">
        <h3 className="text-sm font-semibold text-slate-900">{t("power.ranks")}</h3>
        <div className="flex gap-2">
          {ranks.length === 0 ? (
            <button
              type="button"
              onClick={onSeedTemplate}
              className="rounded-lg bg-violet-100 px-3 py-1.5 text-xs font-medium text-violet-700"
            >
              {t("power.seedXianxiaTemplate")}
            </button>
          ) : null}
          <button
            type="button"
            onClick={onAddRank}
            className="rounded-lg bg-indigo-600 px-3 py-1.5 text-xs font-medium text-white"
          >
            {t("power.addRankButton")}
          </button>
        </div>
      </div>

      {validationError ? (
        <p className="mb-3 rounded-lg bg-red-50 px-3 py-2 text-xs text-red-700">{validationError}</p>
      ) : null}

      {sorted.length === 0 ? (
        <p className="py-8 text-center text-sm text-slate-500">{t("power.emptyRanksAction")}</p>
      ) : (
        <div className="space-y-2">
          {sorted.map((rank) => (
            <PowerRankRow key={rank.id} rank={rank} onUpdate={onUpdateRank} />
          ))}
        </div>
      )}
    </div>
  );
}
