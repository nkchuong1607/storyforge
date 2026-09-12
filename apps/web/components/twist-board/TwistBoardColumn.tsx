import type { TwistBoardColumn as TwistBoardColumnType } from "@/lib/api/types";
import { EmptyState } from "@/components/ui/EmptyState";
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

export function TwistBoardColumn({
  column,
  projectId,
  payoffChapterIds,
  onCardClick,
  onCreateSecret,
}: TwistBoardColumnProps) {
  const columnLabels: Record<string, string> = {
    secrets: "Bí mật",
    plants: "Plants",
    payoffs: "Payoffs",
    revealed: "Đã lộ",
  };

  return (
    <section className="flex min-h-[420px] flex-col rounded-xl border border-slate-200 bg-slate-50/60">
      <header className="border-b border-slate-200 px-4 py-3">
        <h3 className="text-sm font-semibold text-slate-800">
          {columnLabels[column.id] ?? column.label}
        </h3>
        <p className="text-xs text-slate-500">{column.cards.length} thẻ</p>
      </header>
      <div className="flex flex-1 flex-col gap-2 p-3">
        {column.cards.length === 0 && column.id === "secrets" ? (
          <EmptyState
            title="Chưa có secret"
            description="Đăng ký secret đầu tiên để bắt đầu twist board."
            action={
              onCreateSecret ? (
                <button
                  type="button"
                  onClick={onCreateSecret}
                  className="rounded-lg bg-indigo-600 px-4 py-2 text-sm font-medium text-white hover:bg-indigo-700"
                >
                  Đăng ký secret đầu tiên
                </button>
              ) : null
            }
          />
        ) : null}
        {column.cards.length === 0 && column.id === "revealed" ? (
          <p className="py-8 text-center text-xs text-slate-400">Chưa có twist đã reveal</p>
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
