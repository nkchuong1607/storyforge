"use client";

import Link from "next/link";
import type { TwistBoardCard } from "@/lib/api/types";
import { continuityGatePath } from "@/lib/chapter-routes";
import { useTranslations } from "@/lib/i18n/use-translations";

interface FairnessCheckPanelProps {
  projectId: string;
  payoffCards: TwistBoardCard[];
  payoffChapterIds: Record<string, string>;
}

export function FairnessCheckPanel({
  projectId,
  payoffCards,
  payoffChapterIds,
}: FairnessCheckPanelProps) {
  const t = useTranslations();
  const failing = payoffCards.filter((card) => card.fairness?.state === "fail");

  if (failing.length === 0) {
    return (
      <aside className="rounded-xl border border-emerald-200 bg-emerald-50/60 p-4">
        <h3 className="text-sm font-semibold text-emerald-900">{t("twist.fairness.title")}</h3>
        <p className="mt-1 text-xs text-emerald-800">{t("twist.fairness.allPass")}</p>
      </aside>
    );
  }

  return (
    <aside className="rounded-xl border border-red-200 bg-red-50/60 p-4">
      <h3 className="text-sm font-semibold text-red-900">{t("twist.fairness.title")}</h3>
      <ul className="mt-2 space-y-2">
        {failing.map((card) => (
          <li key={card.payoff_id ?? card.twist_id} className="text-xs text-red-800">
            <p className="font-medium">{card.twist_title}</p>
            <p>{card.fairness?.issue_codes?.join(", ")}</p>
            {card.twist_id && payoffChapterIds[card.twist_id] ? (
              <Link
                href={continuityGatePath(projectId, payoffChapterIds[card.twist_id])}
                className="mt-1 inline-block font-medium underline"
              >
                {t("twist.openContinuityGate")}
              </Link>
            ) : null}
          </li>
        ))}
      </ul>
    </aside>
  );
}
