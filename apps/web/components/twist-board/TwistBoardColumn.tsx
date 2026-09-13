"use client";

import type { TwistBoardColumn as TwistBoardColumnType } from "@/lib/api/types";
import { EmptyState } from "@/components/ui/EmptyState";
import { useTranslations } from "@/lib/i18n/use-translations";
import { PayoffCard } from "./PayoffCard";
import { PlantCard } from "./PlantCard";
import { RevealedCard } from "./RevealedCard";
import { SecretCard } from "./SecretCard";

interface TwistBoardColumnProps {
  column: TwistBoardColumnType;
  projectId: string;
  payoffChapterIds: Record<string, string>;
  onCardClick: (twistId: string) => void;
  onCreateSecret?: () => void;
}

const COLUMN_KEYS: Record<string, string> = {
  secrets: "twist.columns.secrets",
  plants: "twist.columns.plants",
  payoffs: "twist.columns.payoffs",
  revealed: "twist.columns.revealed",
};

export function TwistBoardColumn({
  column,
  projectId,
  payoffChapterIds,
  onCardClick,
  onCreateSecret,
}: TwistBoardColumnProps) {
  const t = useTranslations();
  const columnLabelKey = COLUMN_KEYS[column.id];
  const columnLabel = columnLabelKey ? t(columnLabelKey) : column.label;

  return (
    <section className="flex min-h-[420px] flex-col rounded-xl border border-slate-200 bg-slate-50/60">
      <header className="border-b border-slate-200 px-4 py-3">
        <h3 className="text-sm font-semibold text-slate-800">{columnLabel}</h3>
        <p className="text-xs text-slate-500">{t("twist.cardCount", { count: column.cards.length })}</p>
      </header>
      <div className="flex flex-1 flex-col gap-2 p-3">
        {column.cards.length === 0 && column.id === "secrets" ? (
          <EmptyState
            title={t("twist.secretsEmptyTitle")}
            description={t("twist.secretsEmptyDescription")}
            action={
              onCreateSecret ? (
                <button
                  type="button"
                  onClick={onCreateSecret}
                  className="rounded-lg bg-indigo-600 px-4 py-2 text-sm font-medium text-white hover:bg-indigo-700"
                >
                  {t("twist.secretsEmptyCta")}
                </button>
              ) : null
            }
          />
        ) : null}
        {column.cards.length === 0 && column.id === "revealed" ? (
          <p className="py-8 text-center text-xs text-slate-400">{t("twist.revealedEmpty")}</p>
        ) : null}
        {column.cards.map((card) => {
          const key = card.plant_id ?? card.payoff_id ?? card.twist_id ?? card.title;
          if (card.card_type === "twist" && column.id === "revealed") {
            return <RevealedCard key={key} card={card} />;
          }
          if (card.card_type === "twist") {
            return (
              <SecretCard
                key={key}
                card={card}
                onClick={() => card.twist_id && onCardClick(card.twist_id)}
              />
            );
          }
          if (card.card_type === "plant") {
            return (
              <PlantCard
                key={key}
                card={card}
                onClick={() => card.twist_id && onCardClick(card.twist_id)}
              />
            );
          }
          return (
            <PayoffCard
              key={key}
              card={card}
              projectId={projectId}
              targetChapterId={
                card.twist_id ? payoffChapterIds[card.twist_id] : undefined
              }
              onClick={() => card.twist_id && onCardClick(card.twist_id)}
            />
          );
        })}
      </div>
    </section>
  );
}
