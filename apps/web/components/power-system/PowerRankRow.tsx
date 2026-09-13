"use client";

import type { PowerRank } from "@/lib/api/types";
import { useTranslations } from "@/lib/i18n/use-translations";

interface PowerRankRowProps {
  rank: PowerRank;
  onUpdate: (rankId: string, displayName: string, constraints: string) => void;
}

export function PowerRankRow({ rank, onUpdate }: PowerRankRowProps) {
  const t = useTranslations();

  return (
    <div className="flex items-start gap-3 rounded-lg border border-slate-100 bg-slate-50 p-3">
      <span className="cursor-grab text-slate-400" aria-hidden>
        ⋮⋮
      </span>
      <div className="flex-1">
        <div className="flex items-center gap-2">
          <span className="text-xs font-medium text-slate-400">#{rank.sort_order}</span>
          <input
            type="text"
            defaultValue={rank.display_name}
            onBlur={(e) =>
              onUpdate(rank.id, e.target.value, rank.constraints_md ?? "")
            }
            aria-label={t("power.rankNameAria", { name: rank.display_name })}
            className="flex-1 rounded border border-slate-200 px-2 py-1 text-sm font-medium"
          />
        </div>
        {rank.sub_stages.length > 0 ? (
          <p className="mt-1 text-xs text-slate-500">
            {t("power.subStagesLabel")}{" "}
            {rank.sub_stages.map((s) => s.display_name).join(", ")}
          </p>
        ) : null}
        <textarea
          defaultValue={rank.constraints_md ?? ""}
          onBlur={(e) => onUpdate(rank.id, rank.display_name, e.target.value)}
          placeholder={t("power.constraintsPlaceholder")}
          className="mt-2 w-full rounded border border-slate-200 px-2 py-1 text-xs"
          rows={2}
        />
      </div>
    </div>
  );
}
