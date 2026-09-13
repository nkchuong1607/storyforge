"use client";

import Link from "next/link";
import type { TwistBoardCard } from "@/lib/api/types";
import { continuityGatePath } from "@/lib/chapter-routes";
import { useTranslations } from "@/lib/i18n/use-translations";

interface PayoffCardProps {
  card: TwistBoardCard;
  projectId: string;
  targetChapterId?: string;
  onClick?: () => void;
}

export function PayoffCard({ card, projectId, targetChapterId, onClick }: PayoffCardProps) {
  const t = useTranslations();
  const fairness = card.fairness?.state ?? "ok";
  const borderClass =
    fairness === "fail"
      ? "border-red-400 bg-red-50/40"
      : fairness === "warn"
        ? "border-amber-300 bg-amber-50/40"
        : "border-slate-200 bg-white";

  return (
    <div className={`rounded-lg border p-3 shadow-sm ${borderClass}`} data-testid="payoff-card">
      <button type="button" onClick={onClick} className="w-full text-left">
        <h4 className="text-sm font-semibold text-slate-900">{card.twist_title}</h4>
        <p className="mt-1 text-xs text-slate-600">
          {t("twist.payoffMeta", {
            chapter: card.target_chapter_number ?? "?",
            minPlants: card.min_plants ?? 0,
            count: card.plant_count ?? 0,
          })}
        </p>
      </button>
      {fairness === "fail" && card.fairness?.issue_codes?.length ? (
        <div className="mt-2 rounded bg-red-100/80 px-2 py-1.5 text-xs text-red-800">
          <p>{card.fairness.issue_codes[0]}</p>
          {targetChapterId ? (
            <Link
              href={continuityGatePath(projectId, targetChapterId)}
              className="mt-1 inline-block font-medium underline"
            >
              {t("twist.openContinuityGate")}
            </Link>
          ) : null}
        </div>
      ) : null}
    </div>
  );
}
