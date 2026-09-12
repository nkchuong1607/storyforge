import type { TwistBoardCard } from "@/lib/api/types";

interface PlantCardProps {
  card: TwistBoardCard;
  onClick?: () => void;
}

export function PlantCard({ card, onClick }: PlantCardProps) {
  return (
    <button
      type="button"
      onClick={onClick}
      className="w-full rounded-lg border border-slate-200 bg-white p-3 text-left shadow-sm transition hover:border-emerald-300 hover:shadow"
    >
      <p className="text-[11px] font-medium uppercase tracking-wide text-emerald-700">
        Ch.{card.chapter_number} · {card.salience}
      </p>
      <p className="mt-1 text-sm text-slate-800">{card.snippet}</p>
      {card.twist_title ? (
        <p className="mt-2 truncate text-xs text-slate-500">↳ {card.twist_title}</p>
      ) : null}
    </button>
  );
}
