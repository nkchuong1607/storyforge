"use client";

import type { TwistBoardCard } from "@/lib/api/types";
import { useTranslations } from "@/lib/i18n/use-translations";

interface PlantCardProps {
  card: TwistBoardCard;
  onClick?: () => void;
}

export function PlantCard({ card, onClick }: PlantCardProps) {
  const t = useTranslations();

  return (
    <button
      type="button"
      onClick={onClick}
      className="w-full rounded-lg border border-slate-200 bg-white p-3 text-left shadow-sm transition hover:border-emerald-300 hover:shadow"
    >
      <p className="text-[11px] font-medium uppercase tracking-wide text-emerald-700">
        {t("twist.plantMeta", {
          number: card.chapter_number ?? "?",
          salience: card.salience ?? "",
        })}
      </p>
      <p className="mt-1 text-sm text-slate-800">{card.snippet}</p>
      {card.twist_title ? (
        <p className="mt-2 truncate text-xs text-slate-500">
          {t("twist.plantTwistLink", { twistTitle: card.twist_title })}
        </p>
      ) : null}
    </button>
  );
}
