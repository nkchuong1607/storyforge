"use client";

import type { TwistBoardCard } from "@/lib/api/types";
import { useTranslations } from "@/lib/i18n/use-translations";

interface RevealedCardProps {
  card: TwistBoardCard;
  onClick?: () => void;
}

export function RevealedCard({ card, onClick }: RevealedCardProps) {
  const t = useTranslations();

  return (
    <button
      type="button"
      onClick={onClick}
      className="w-full rounded-lg border border-slate-200 bg-slate-50 p-3 text-left opacity-90"
      disabled
    >
      <h4 className="text-sm font-medium text-slate-700">{card.title}</h4>
      <p className="mt-1 text-xs text-slate-500">
        {t("twist.revealedMeta", { count: card.plant_count ?? 0 })}
      </p>
    </button>
  );
}
